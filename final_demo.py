"""Final professor-facing demonstration for the frozen simulation results."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import pandas as pd

from src.detection import area_under_roc, roc_curve

RESULTS_DIR = PROJECT_ROOT / "results"
DETECTORS = ["quantum", "classical_correlated", "classical_matched_filter"]
LABELS = {
    "quantum": "Quantum",
    "classical_correlated": "Classical Correlated",
    "classical_matched_filter": "Classical Matched Filter",
}
COLORS = {
    "quantum": "#1565c0",
    "classical_correlated": "#2e7d32",
    "classical_matched_filter": "#c62828",
}


def load_results() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the existing frozen summary and trial-level result files."""

    return (
        pd.read_csv(RESULTS_DIR / "summary.csv"),
        pd.read_csv(RESULTS_DIR / "trial_statistics.csv"),
    )


def condition_row(summary: pd.DataFrame, eta: float, epsilon: float) -> pd.DataFrame:
    """Return one requested eta/epsilon condition in detector order."""

    condition = summary[
        (summary["eta"] == eta) & (summary["epsilon"] == epsilon)
    ].copy()
    return condition.set_index("detector").loc[DETECTORS].reset_index()


def create_comparison_csv(summary: pd.DataFrame) -> None:
    """Write the complete existing experiment in presentation-friendly form."""

    comparison = summary.pivot(
        index=["eta", "epsilon"], columns="detector", values="auc"
    ).reset_index()
    comparison.columns.name = None
    comparison = comparison.rename(
        columns={
            "quantum": "quantum_auc",
            "classical_correlated": "classical_correlated_auc",
            "classical_matched_filter": "classical_matched_filter_auc",
        }
    )
    comparison["condition"] = comparison.apply(
        lambda row: f"eta={row['eta']:.2f}, epsilon={row['epsilon']:.2f}", axis=1
    )
    comparison = comparison[
        [
            "condition",
            "eta",
            "epsilon",
            "quantum_auc",
            "classical_correlated_auc",
            "classical_matched_filter_auc",
        ]
    ].sort_values(["eta", "epsilon"], ignore_index=True)
    comparison.to_csv(RESULTS_DIR / "final_demo_comparison.csv", index=False)


def save_line_plot(
    data: pd.DataFrame,
    x_column: str,
    title: str,
    xlabel: str,
    filename: str,
) -> None:
    """Save a clean three-detector line chart."""

    figure, axis = plt.subplots(figsize=(8, 5))
    for detector in DETECTORS:
        detector_data = data[data["detector"] == detector].sort_values(x_column)
        axis.plot(
            detector_data[x_column],
            detector_data["auc"],
            marker="o",
            linewidth=2.2,
            color=COLORS[detector],
            label=LABELS[detector],
        )
    axis.set_xlabel(xlabel)
    axis.set_ylabel("AUC")
    axis.set_title(title)
    axis.set_ylim(0.0, 1.02)
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(RESULTS_DIR / filename, dpi=200)
    plt.close(figure)


def create_roc_plot(trials: pd.DataFrame) -> None:
    """Save all detector ROC curves at the difficult common condition."""

    condition = trials[
        (trials["eta"] == 0.10) & (trials["epsilon"] == 0.20)
    ]
    figure, axis = plt.subplots(figsize=(7, 7))
    for detector in DETECTORS:
        detector_data = condition[condition["detector"] == detector]
        present = detector_data.loc[detector_data["target_present"], "statistic"]
        absent = detector_data.loc[~detector_data["target_present"], "statistic"]
        pfa, pd, _ = roc_curve(present, absent)
        auc = area_under_roc(present, absent)
        axis.plot(
            pfa,
            pd,
            linewidth=2.2,
            color=COLORS[detector],
            label=f"{LABELS[detector]} AUC={auc:.5f}",
        )
    axis.plot([0.0, 1.0], [0.0, 1.0], "k--", alpha=0.6, label="Chance")
    axis.set_xlabel("Probability of False Alarm (Pfa)")
    axis.set_ylabel("Probability of Detection (Pd)")
    axis.set_title("ROC at eta=0.10, epsilon=0.20")
    axis.set_xlim(0.0, 1.0)
    axis.set_ylim(0.0, 1.0)
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(RESULTS_DIR / "presentation_roc.png", dpi=200)
    plt.close(figure)


def create_overall_plot(summary: pd.DataFrame) -> None:
    """Save a compact mean-AUC and observed-range comparison."""

    grouped = summary.groupby("detector")["auc"]
    means = grouped.mean().reindex(DETECTORS)
    minima = grouped.min().reindex(DETECTORS)
    maxima = grouped.max().reindex(DETECTORS)

    figure, axis = plt.subplots(figsize=(8, 5))
    positions = range(len(DETECTORS))
    axis.errorbar(
        positions,
        means,
        yerr=[means - minima, maxima - means],
        fmt="o",
        capsize=7,
        markersize=8,
        linewidth=2,
        color="#263238",
    )
    axis.set_xticks(list(positions), [LABELS[detector] for detector in DETECTORS])
    axis.set_ylabel("AUC")
    axis.set_title("Overall detector comparison across all conditions")
    axis.set_ylim(0.0, 1.02)
    axis.grid(axis="y", alpha=0.3)
    figure.tight_layout()
    figure.savefig(RESULTS_DIR / "presentation_overall.png", dpi=200)
    plt.close(figure)


def print_summary(summary: pd.DataFrame) -> None:
    """Print the professor-facing terminal summary."""

    difficult = condition_row(summary, 0.10, 0.20)
    highest = condition_row(summary, 0.40, 0.00)
    ranges = summary.groupby("detector")["auc"].agg(["min", "max"])

    print("=" * 60)
    print("QUANTUM TARGET DETECTION - FINAL RESULTS")
    print("=" * 60)
    print()
    print("MODEL COMPARISON")
    print()
    print("1. Quantum Entangled Detector")
    print("2. Classically Correlated Detector")
    print("3. Classical Matched-Filter Detector")
    print()
    print("-" * 60)
    print("DIFFICULT CONDITION")
    print("-" * 60)
    print()
    print("eta     = 0.10")
    print("epsilon = 0.20")
    print()
    print(f"Quantum AUC                  : {difficult.loc[difficult.detector == 'quantum', 'auc'].iloc[0]:.5f}")
    print(f"Classical Correlated AUC     : {difficult.loc[difficult.detector == 'classical_correlated', 'auc'].iloc[0]:.5f}")
    print(f"Classical Matched Filter AUC : {difficult.loc[difficult.detector == 'classical_matched_filter', 'auc'].iloc[0]:.5f}")
    print()
    print("-" * 60)
    print("HIGHEST OBSERVED CONDITION")
    print("-" * 60)
    print()
    print("eta     = 0.40")
    print("epsilon = 0.00")
    print()
    print(f"Quantum AUC                  : {highest.loc[highest.detector == 'quantum', 'auc'].iloc[0]:.5f}")
    print(f"Classical Correlated AUC     : {highest.loc[highest.detector == 'classical_correlated', 'auc'].iloc[0]:.5f}")
    print(f"Classical Matched Filter AUC : {highest.loc[highest.detector == 'classical_matched_filter', 'auc'].iloc[0]:.5f}")
    print()
    print("-" * 60)
    print("OVERALL AUC RANGE")
    print("-" * 60)
    print()
    for detector in DETECTORS:
        print(f"{LABELS[detector]:<25}: {ranges.loc[detector, 'min']:.5f} - {ranges.loc[detector, 'max']:.5f}")
    print()
    print("-" * 60)
    print("SCIENTIFIC INTERPRETATION")
    print("-" * 60)
    print()
    print("The simulation does not demonstrate universal quantum advantage.")
    print()
    print("Performance depends on target correlation and noise conditions.")
    print()
    print("=" * 60)


def main() -> None:
    """Generate and display the final demonstration artifacts."""

    summary, trials = load_results()
    create_comparison_csv(summary)
    save_line_plot(
        summary[summary["eta"] == 0.10],
        "epsilon",
        "Weak-target performance at eta=0.10",
        "Epsilon: binary flip probability",
        "presentation_weak_target.png",
    )
    save_line_plot(
        summary[summary["epsilon"] == 0.20],
        "eta",
        "Target-correlation performance at epsilon=0.20",
        "Eta: target-correlation probability",
        "presentation_target_strength.png",
    )
    create_roc_plot(trials)
    create_overall_plot(summary)
    print_summary(summary)
    print()
    print("FINAL DEMO READY")
    print("Tests: run python -m pytest -q")
    print("Scientific model modified: NO")
    print("Detector algorithms modified: NO")


if __name__ == "__main__":
    main()
