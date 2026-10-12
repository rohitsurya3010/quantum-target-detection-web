"""Qiskit/Aer implementation of the simplified two-qubit detector."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Kraus
from qiskit_aer import AerSimulator

from .channel import ChannelConfig


@dataclass(frozen=True)
class QuantumSimulationConfig:
    """Execution settings for independent quantum observations."""

    shots: int = 256

    def __post_init__(self) -> None:
        if self.shots < 1:
            raise ValueError("shots must be a positive integer")


def create_bell_pair() -> QuantumCircuit:
    """Create an unmeasured Bell pair with probe qubit 0 and reference qubit 1."""

    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    return circuit


def correlation_from_counts(counts: dict[str, int]) -> float:
    """Return +1/-1 equality correlation averaged over observations."""

    total_shots = sum(counts.values())
    if total_shots == 0:
        raise ValueError("counts must contain at least one shot")

    equal_count = sum(count for outcome, count in counts.items() if outcome[0] == outcome[-1])
    return (2.0 * equal_count / total_shots) - 1.0


def _target_return_channel(channel_config: ChannelConfig, target_present: bool) -> Kraus:
    """Build the per-observation target/background and flip channel."""

    eta = channel_config.eta if target_present else 0.0
    identity = np.eye(2, dtype=complex)
    operators = [np.sqrt(eta) * identity]
    for source in range(2):
        for destination in range(2):
            operator = np.zeros((2, 2), dtype=complex)
            operator[destination, source] = np.sqrt((1.0 - eta) / 2.0)
            operators.append(operator)

    flip = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    noisy_operators = []
    for operator in operators:
        noisy_operators.append(np.sqrt(1.0 - channel_config.epsilon) * operator)
        noisy_operators.append(np.sqrt(channel_config.epsilon) * flip @ operator)
    return Kraus(noisy_operators)


def _stochastic_observation_circuit(
    channel_config: ChannelConfig,
    target_present: bool,
) -> QuantumCircuit:
    """Create one circuit whose shots are independent channel observations."""

    circuit = create_bell_pair()
    circuit.append(_target_return_channel(channel_config, target_present), [0])
    circuit.measure([0, 1], [0, 1])
    return circuit


def run_quantum_trial(
    channel_config: ChannelConfig,
    simulation_config: QuantumSimulationConfig,
    target_present: bool,
    rng: np.random.Generator,
    simulator: AerSimulator | None = None,
) -> dict[str, Any]:
    """Run one independent-observation trial and return its statistic."""

    return run_quantum_trials(
        channel_config=channel_config,
        simulation_config=simulation_config,
        target_present=target_present,
        trials=1,
        rng=rng,
        simulator=simulator,
    )[0]


def run_quantum_trials(
    channel_config: ChannelConfig,
    simulation_config: QuantumSimulationConfig,
    target_present: bool,
    trials: int,
    rng: np.random.Generator,
    simulator: AerSimulator | None = None,
) -> list[dict[str, Any]]:
    """Run multiple trials in one Aer job using independent observations.

    ``shots`` is the observation budget, not repeated executions of one
    channel realization. Each observation receives a fresh Bell pair and an
    independent target/background and flip-noise sample. Batching changes only
    execution overhead; each circuit still runs with one shot.
    """

    if trials < 1:
        raise ValueError("trials must be a positive integer")

    circuits = [
        _stochastic_observation_circuit(channel_config, target_present)
        for _ in range(trials)
    ]

    backend = simulator or AerSimulator()
    simulator_seed = int(rng.integers(0, 2**32))
    result = backend.run(
        circuits,
        shots=simulation_config.shots,
        seed_simulator=simulator_seed,
    ).result()
    trial_results: list[dict[str, Any]] = []
    for trial_index in range(trials):
        counts: dict[str, int] = {}
        observation_counts = result.get_counts(trial_index)
        for outcome, count in observation_counts.items():
            counts[outcome] = counts.get(outcome, 0) + count
        trial_results.append(
            {
                "statistic": correlation_from_counts(counts),
                "counts": counts,
                "target_present": target_present,
            }
        )
    return trial_results
