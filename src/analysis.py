"""Experiment orchestration, result tables, and plots."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .channel import ChannelConfig
from .classical import ClassicalSimulationConfig, run_classical_trial
from .classical_correlated import (
    ClassicallyCorrelatedConfig,
    run_classically_correlated_trial,
)
from .detection import area_under_roc, detection_metrics, roc_curve
from .quantum import QuantumSimulationConfig, run_quantum_trials
from qiskit_aer import AerSimulator


@dataclass(frozen=True)
class ExperimentConfig:
    """Parameters for a reproducible fair binary detector comparison sweep."""

    eta_values: tuple[float, ...] = (0.1, 0.2, 0.4, 0.6)
    epsilon_values: tuple[float, ...] = (0.0, 0.05, 0.1, 0.2)
    trials: int = 100
    quantum_shots: int = 256
    classical_samples: int = 256
    seed: int = 20260912

    def __post_init__(self) -> None:
        if self.trials < 2:
            raise ValueError("trials must be at least 2")
        if self.quantum_shots != self.classical_samples:
            raise ValueError("quantum_shots and classical_samples must be equal")
        if any(not 0.0 <= value <= 1.0 for value in self.eta_values):
            raise ValueError("eta values must be between 0 and 1")
        if any(not 0.0 <= value <= 0.5 for value in self.epsilon_values):
            raise ValueError("epsilon values must be between 0 and 0.5")


def _run_detector_pair(
    eta: float,
    epsilon: float,
    config: ExperimentConfig,
    rng: np.random.Generator,
    simulator: AerSimulator,
) -> tuple[dict[str, list[float]], dict[str, float]]:
    """Collect present/absent statistics and summary metrics for one condition."""

    quantum_present: list[float] = []
    quantum_absent: list[float] = []
    classical_present: list[float] = []
    classical_absent: list[float] = []
    classically_correlated_present: list[float] = []
    classically_correlated_absent: list[float] = []

    channel = ChannelConfig(
        eta=eta,
        epsilon=epsilon,
    )
    quantum_settings = QuantumSimulationConfig(shots=config.quantum_shots)
    classical_settings = ClassicalSimulationConfig(
        samples=config.classical_samples,
        eta=eta,
        epsilon=epsilon,
    )
    classically_correlated_settings = ClassicallyCorrelatedConfig(
        samples=config.classical_samples,
        eta=eta,
        epsilon=epsilon,
    )

    quantum_present.extend(
        result["statistic"]
        for result in run_quantum_trials(
            channel, quantum_settings, True, config.trials, rng, simulator
        )
    )
    quantum_absent.extend(
        result["statistic"]
        for result in run_quantum_trials(
            channel, quantum_settings, False, config.trials, rng, simulator
        )
    )
    for _ in range(config.trials):
        classical_present.append(
            run_classical_trial(classical_settings, True, rng)["statistic"]
        )
        classical_absent.append(
            run_classical_trial(classical_settings, False, rng)["statistic"]
        )
        classically_correlated_present.append(
            run_classically_correlated_trial(
                classically_correlated_settings, True, rng
            )["statistic"]
        )
        classically_correlated_absent.append(
            run_classically_correlated_trial(
                classically_correlated_settings, False, rng
            )["statistic"]
        )

    statistics = {
        "quantum_present": quantum_present,
        "quantum_absent": quantum_absent,
        "classical_present": classical_present,
        "classical_absent": classical_absent,
        "classical_correlated_present": classically_correlated_present,
        "classical_correlated_absent": classically_correlated_absent,
    }
    summary: dict[str, float] = {}
    for detector in (
        "quantum",
        "classical_correlated",
        "classical_matched_filter",
    ):
        statistic_key = "classical" if detector == "classical_matched_filter" else detector
        present = statistics[f"{statistic_key}_present"]
        absent = statistics[f"{statistic_key}_absent"]
        summary[f"{detector}_auc"] = area_under_roc(present, absent)
        summary[f"{detector}_pd_at_zero"] = detection_metrics(present, absent, 0.0)["pd"]
        summary[f"{detector}_pfa_at_zero"] = detection_metrics(present, absent, 0.0)["pfa"]
    return statistics, summary


def run_sweep(config: ExperimentConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run all conditions and return summary rows plus trial-level statistics."""

    rng = np.random.default_rng(config.seed)
    simulator = AerSimulator()
    summary_rows: list[dict[str, float | str]] = []
    trial_rows: list[dict[str, float | str | int]] = []

    for eta in config.eta_values:
        for epsilon in config.epsilon_values:
            statistics, summary = _run_detector_pair(
                eta, epsilon, config, rng, simulator
            )
            summary_rows.extend(
                {
                    "detector": detector,
                    "eta": eta,
                    "epsilon": epsilon,
                    "auc": summary[f"{detector}_auc"],
                    "pd_at_zero": summary[f"{detector}_pd_at_zero"],
                    "pfa_at_zero": summary[f"{detector}_pfa_at_zero"],
                }
                for detector in (
                    "quantum",
                    "classical_correlated",
                    "classical_matched_filter",
                )
            )
            for detector in (
                "quantum",
                "classical_correlated",
                "classical_matched_filter",
            ):
                statistic_key = "classical" if detector == "classical_matched_filter" else detector
                for target_present, values in (
                    (True, statistics[f"{statistic_key}_present"]),
                    (False, statistics[f"{statistic_key}_absent"]),
                ):
                    trial_rows.extend(
                        {
                            "detector": detector,
                            "eta": eta,
                            "epsilon": epsilon,
                            "target_present": target_present,
                            "trial": index,
                            "statistic": value,
                        }
                        for index, value in enumerate(values)
                    )

    return pd.DataFrame(summary_rows), pd.DataFrame(trial_rows)


def save_results(
    summary: pd.DataFrame,
    trials: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """Save numerical CSV files and summary visualizations."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path / "summary.csv", index=False)
    trials.to_csv(output_path / "trial_statistics.csv", index=False)

    figure, axis = plt.subplots(figsize=(8, 5))
    for detector, detector_data in summary.groupby("detector"):
        for epsilon, curve_data in detector_data.groupby("epsilon"):
            curve_data = curve_data.sort_values("eta")
            axis.plot(
                curve_data["eta"],
                curve_data["auc"],
                marker="o",
                label=f"{detector}, epsilon={epsilon:g}",
            )
    axis.set_xlabel("Eta: target-correlation probability")
    axis.set_ylabel("ROC AUC")
    axis.set_ylim(0.0, 1.0)
    axis.set_title("Three-detector AUC comparison")
    axis.grid(alpha=0.3)
    axis.legend(fontsize="small")
    figure.tight_layout()
    figure.savefig(output_path / "auc_comparison.png", dpi=150)
    plt.close(figure)

    best_condition = summary.iloc[summary["auc"].argmax()]
    selected_eta = best_condition["eta"]
    selected_epsilon = best_condition["epsilon"]
    detector_labels = {
        "quantum": "Quantum",
        "classical_correlated": "Classically correlated",
        "classical_matched_filter": "Classical matched filter",
    }
    figure, axis = plt.subplots(figsize=(6, 6))
    for detector, label in detector_labels.items():
        condition_trials = trials[
            (trials["detector"] == detector)
            & (trials["eta"] == selected_eta)
            & (trials["epsilon"] == selected_epsilon)
        ]
        present = condition_trials.loc[condition_trials["target_present"], "statistic"]
        absent = condition_trials.loc[~condition_trials["target_present"], "statistic"]
        pfa_values, pd_values, _ = roc_curve(present, absent)
        auc = area_under_roc(present, absent)
        axis.plot(pfa_values, pd_values, label=f"{label} AUC={auc:.3f}")
    axis.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Chance")
    axis.set_xlabel("Probability of False Alarm (Pfa)")
    axis.set_ylabel("Probability of Detection (Pd)")
    axis.set_title(f"ROC at eta={selected_eta:.1f}, epsilon={selected_epsilon:.1f}")
    axis.set_xlim(0.0, 1.0)
    axis.set_ylim(0.0, 1.0)
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path / "roc_best_condition.png", dpi=150)
    plt.close(figure)
