"""Deterministic tests for the quantum correlation simulation platform."""

from __future__ import annotations

import numpy as np
import pytest

from src.analysis import ExperimentConfig, run_sweep
from src.channel import ChannelConfig, apply_target_channel
from src.classical import ClassicalSimulationConfig, run_classical_trial
from src.classical_correlated import (
    ClassicallyCorrelatedConfig,
    run_classically_correlated_trial,
)
from src.detection import area_under_roc, detection_metrics, roc_curve
from src.literature import (
    AHMED_REPORTED_CORRELATION_SEPARATION,
    correlation_separation,
)
from src.quantum import (
    QuantumSimulationConfig,
    correlation_from_counts,
    create_bell_pair,
    run_quantum_trial,
    run_quantum_trials,
)


class SequenceRng:
    """Small scripted RNG for deterministic channel-event tests."""

    def __init__(self, values: list[float]) -> None:
        self.values = iter(values)

    def random(self) -> float:
        return next(self.values)


def operation_names(circuit) -> list[str]:
    """Return circuit operation names in execution order."""

    return [instruction.operation.name for instruction in circuit.data]


def test_create_bell_pair_has_expected_gates_and_registers() -> None:
    circuit = create_bell_pair()

    assert circuit.num_qubits == 2
    assert circuit.num_clbits == 2
    assert operation_names(circuit) == ["h", "cx"]


def test_correlation_perfect_agreement() -> None:
    assert correlation_from_counts({"00": 3, "11": 2}) == 1.0


def test_correlation_no_correlation() -> None:
    assert correlation_from_counts({"00": 1, "01": 1, "10": 1, "11": 1}) == 0.0


def test_correlation_perfect_disagreement() -> None:
    assert correlation_from_counts({"01": 2, "10": 3}) == -1.0


def test_target_present_can_remain_correlated_without_noise() -> None:
    circuit = create_bell_pair()
    metadata = apply_target_channel(
        circuit,
        probe_qubit=0,
        config=ChannelConfig(eta=1.0, epsilon=0.0),
        target_present=True,
        rng=SequenceRng([0.0, 0.9]),
    )

    assert metadata == {
        "target_present": True,
        "correlated": True,
        "background": False,
        "flipped": False,
    }
    assert "reset" not in operation_names(circuit)
    assert "x" not in operation_names(circuit)


def test_target_absent_uses_uniform_background_and_noise_event() -> None:
    circuit = create_bell_pair()
    metadata = apply_target_channel(
        circuit,
        probe_qubit=0,
        config=ChannelConfig(eta=1.0, epsilon=0.5),
        target_present=False,
        rng=SequenceRng([0.1, 0.1]),
    )

    assert metadata["target_present"] is False
    assert metadata["correlated"] is False
    assert metadata["background"] is True
    assert metadata["flipped"] is True
    assert operation_names(circuit).count("reset") == 1
    assert operation_names(circuit).count("x") == 2


def test_eta_and_epsilon_are_sampled_for_each_channel_observation() -> None:
    config = ChannelConfig(eta=0.5, epsilon=0.5)
    metadata = []
    scripted_rng = SequenceRng([
        0.1, 0.9,
        0.9, 0.9, 0.1,
        0.1, 0.1,
    ])

    for _ in range(3):
        metadata.append(
            apply_target_channel(
                create_bell_pair(), 0, config, True, scripted_rng
            )
        )

    assert [item["correlated"] for item in metadata] == [True, False, True]
    assert [item["flipped"] for item in metadata] == [False, True, True]


def test_quantum_trial_is_reproducible_with_same_seed() -> None:
    config = ChannelConfig(eta=0.3, epsilon=0.1)
    settings = QuantumSimulationConfig(shots=12)

    first = run_quantum_trial(config, settings, True, np.random.default_rng(1234))
    second = run_quantum_trial(config, settings, True, np.random.default_rng(1234))

    assert first == second
    assert sum(first["counts"].values()) == settings.shots


def test_quantum_trials_batch_backend_submission() -> None:
    class SpySimulator:
        def __init__(self) -> None:
            from qiskit_aer import AerSimulator

            self.backend = AerSimulator()
            self.calls = 0

        def run(self, *args, **kwargs):
            self.calls += 1
            return self.backend.run(*args, **kwargs)

    simulator = SpySimulator()
    results = run_quantum_trials(
        ChannelConfig(eta=0.4, epsilon=0.1),
        QuantumSimulationConfig(shots=4),
        target_present=True,
        trials=3,
        rng=np.random.default_rng(42),
        simulator=simulator,
    )

    assert simulator.calls == 1
    assert len(results) == 3
    assert all(sum(result["counts"].values()) == 4 for result in results)


def test_classical_trial_is_reproducible_with_same_seed() -> None:
    settings = ClassicalSimulationConfig(samples=12, eta=0.3, epsilon=0.1)

    first = run_classical_trial(settings, True, np.random.default_rng(1234))
    second = run_classical_trial(settings, True, np.random.default_rng(1234))

    assert first == second


def test_classically_correlated_eta_controls_correlation() -> None:
    samples = 2000
    fully_correlated = run_classically_correlated_trial(
        ClassicallyCorrelatedConfig(samples=samples, eta=1.0, epsilon=0.0),
        True,
        np.random.default_rng(10),
    )
    independent_background = run_classically_correlated_trial(
        ClassicallyCorrelatedConfig(samples=samples, eta=0.0, epsilon=0.0),
        True,
        np.random.default_rng(10),
    )

    assert fully_correlated["statistic"] == 1.0
    assert abs(independent_background["statistic"]) < 0.1


def test_classically_correlated_epsilon_adds_independent_flips() -> None:
    result = run_classically_correlated_trial(
        ClassicallyCorrelatedConfig(samples=2000, eta=1.0, epsilon=0.5),
        True,
        np.random.default_rng(11),
    )

    assert 850 < result["flipped_observations"] < 1150
    assert abs(result["statistic"]) < 0.1


def test_classically_correlated_target_hypotheses_differ() -> None:
    settings = ClassicallyCorrelatedConfig(samples=2000, eta=1.0, epsilon=0.0)
    present = run_classically_correlated_trial(settings, True, np.random.default_rng(12))
    absent = run_classically_correlated_trial(settings, False, np.random.default_rng(12))

    assert present["statistic"] == 1.0
    assert abs(absent["statistic"]) < 0.1


def test_classically_correlated_trial_is_reproducible() -> None:
    settings = ClassicallyCorrelatedConfig(samples=32, eta=0.3, epsilon=0.1)

    first = run_classically_correlated_trial(settings, True, np.random.default_rng(123))
    second = run_classically_correlated_trial(settings, True, np.random.default_rng(123))

    assert first == second


def test_detection_metrics_calculate_pd_and_pfa() -> None:
    metrics = detection_metrics(
        present_statistics=[-0.2, 0.4, 0.8],
        absent_statistics=[-0.4, 0.1, 0.3],
        threshold=0.3,
    )

    assert metrics == {"threshold": 0.3, "pd": pytest.approx(2 / 3), "pfa": pytest.approx(1 / 3)}


def test_roc_curve_contains_expected_endpoints() -> None:
    pfa, pd, thresholds = roc_curve([0.8, 1.0], [-1.0, 0.0])

    assert pfa[0] == 0.0
    assert pd[0] == 0.0
    assert pfa[-1] == 1.0
    assert pd[-1] == 1.0
    assert np.isinf(thresholds[[0, -1]]).all()


def test_auc_is_one_for_separated_statistics() -> None:
    assert area_under_roc([0.8, 1.0], [-1.0, 0.0]) == pytest.approx(1.0)


def test_quantum_and_classical_use_same_observation_budget() -> None:
    config = ExperimentConfig(
        eta_values=(0.4,),
        epsilon_values=(0.1,),
        trials=2,
        quantum_shots=8,
        classical_samples=8,
        seed=99,
    )
    summary, trials = run_sweep(config)

    assert set(summary["detector"]) == {
        "quantum",
        "classical_correlated",
        "classical_matched_filter",
    }
    for detector in (
        "quantum",
        "classical_correlated",
        "classical_matched_filter",
    ):
        detector_trials = trials[trials["detector"] == detector]
        assert len(detector_trials) == 2 * config.trials * 1
        assert detector_trials.groupby("target_present").size().to_dict() == {
            False: config.trials,
            True: config.trials,
        }

    with pytest.raises(ValueError, match="must be equal"):
        ExperimentConfig(quantum_shots=8, classical_samples=16)


def test_correlation_separation_groups_present_minus_absent() -> None:
    trials = __import__("pandas").DataFrame(
        [
            {"detector": "quantum", "eta": 0.2, "epsilon": 0.1, "target_present": True, "statistic": 0.4},
            {"detector": "quantum", "eta": 0.2, "epsilon": 0.1, "target_present": True, "statistic": 0.6},
            {"detector": "quantum", "eta": 0.2, "epsilon": 0.1, "target_present": False, "statistic": 0.1},
            {"detector": "quantum", "eta": 0.2, "epsilon": 0.1, "target_present": False, "statistic": -0.1},
        ]
    )

    result = correlation_separation(trials)

    assert result.iloc[0]["correlation_separation"] == pytest.approx(0.5)


def test_correlation_separation_is_reproducible_from_same_trial_data() -> None:
    config = ExperimentConfig(
        eta_values=(0.2,),
        epsilon_values=(0.1,),
        trials=2,
        quantum_shots=8,
        classical_samples=8,
        seed=321,
    )
    _, first_trials = run_sweep(config)
    _, second_trials = run_sweep(config)

    first = correlation_separation(first_trials)
    second = correlation_separation(second_trials)
    assert first.equals(second)


def test_ahmed_benchmark_values_are_reference_only() -> None:
    values = {(row["detector"], row["condition"]): row["value"] for row in AHMED_REPORTED_CORRELATION_SEPARATION}

    assert set(row["source"] for row in AHMED_REPORTED_CORRELATION_SEPARATION) == {
        "Ahmed 2026 preprint"
    }
    assert values == {
        ("quantum", "zero background noise"): 0.0100,
        ("quantum", "high background noise"): 0.0025,
        ("classical_correlated", "zero background noise"): 0.1000,
        ("classical_correlated", "high background noise"): 0.0500,
    }


def test_existing_auc_values_are_preserved_by_separation_layer() -> None:
    config = ExperimentConfig(
        eta_values=(0.2,),
        epsilon_values=(0.1,),
        trials=3,
        quantum_shots=8,
        classical_samples=8,
        seed=654,
    )
    summary, trials = run_sweep(config)
    expected = {
        row["detector"]: row["auc"]
        for _, row in summary.iterrows()
    }
    for detector in expected:
        detector_trials = trials[trials["detector"] == detector]
        present = detector_trials.loc[detector_trials["target_present"], "statistic"]
        absent = detector_trials.loc[~detector_trials["target_present"], "statistic"]
        assert area_under_roc(present, absent) == pytest.approx(expected[detector])
