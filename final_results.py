"""Generate final results artifacts from frozen CSV outputs."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import pandas as pd

from src.detection import area_under_roc, roc_curve
from src.literature import correlation_separation

DETECTORS = ["quantum", "classical_correlated", "classical_matched_filter"]
LABELS = {
    "quantum": "Quantum",
    "classical_correlated": "Classically correlated",
    "classical_matched_filter": "Classical matched filter",
}
COLORS = {
    "quantum": "#1565c0",
    "classical_correlated": "#2e7d32",
    "classical_matched_filter": "#c62828",
}


def load_results(results_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load only the frozen numerical result files."""

    return (
        pd.read_csv(results_dir / "summary.csv"),
        pd.read_csv(results_dir / "trial_statistics.csv"),
        pd.read_csv(results_dir / "literature_comparison.csv"),
        pd.read_csv(results_dir / "model_comparison.csv"),
    )


def build_auc_tables(summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build detector summaries and condition-by-condition AUC comparisons."""

    auc_summary = (
        summary.groupby("detector")["auc"]
        .agg(min_auc="min", max_auc="max", mean_auc="mean", std_auc="std")
        .reset_index()
    )
    pivot = summary.pivot(index=["eta", "epsilon"], columns="detector", values="auc").reset_index()
    pivot.columns.name = None
    pivot = pivot.rename(
        columns={
            "quantum": "quantum_auc",
            "classical_correlated": "classical_correlated_auc",
            "classical_matched_filter": "classical_matched_filter_auc",
        }
    )
    pivot["quantum_minus_classical_correlated"] = (
        pivot["quantum_auc"] - pivot["classical_correlated_auc"]
    )
    pivot["quantum_minus_classical_matched_filter"] = (
        pivot["quantum_auc"] - pivot["classical_matched_filter_auc"]
    )
    return auc_summary, pivot.sort_values(["eta", "epsilon"], ignore_index=True)


def build_correlation_table(trials: pd.DataFrame) -> pd.DataFrame:
    """Rename the existing literature helper output for final reporting."""

    separation = correlation_separation(trials)
    means = (
        trials.groupby(["detector", "eta", "epsilon", "target_present"], as_index=False)["statistic"]
        .mean()
        .pivot_table(
            index=["detector", "eta", "epsilon"],
            columns="target_present",
            values="statistic",
        )
        .reset_index()
        .rename(columns={False: "mean_absent_statistic", True: "mean_present_statistic"})
    )
    result = means.merge(separation, on=["detector", "eta", "epsilon"], validate="one_to_one")
    return result[
        ["detector", "eta", "epsilon", "mean_present_statistic", "mean_absent_statistic", "correlation_separation"]
    ].sort_values(["detector", "eta", "epsilon"], ignore_index=True)


def build_final_results_table(auc_by_condition: pd.DataFrame, correlation: pd.DataFrame) -> pd.DataFrame:
    """Join AUC and separation values into the requested table."""

    separation = correlation.pivot(index=["eta", "epsilon"], columns="detector", values="correlation_separation").reset_index()
    separation.columns.name = None
    separation = separation.rename(
        columns={
            "quantum": "quantum_correlation_separation",
            "classical_correlated": "classical_correlated_correlation_separation",
            "classical_matched_filter": "classical_matched_filter_correlation_separation",
        }
    )
    return auc_by_condition[
        ["eta", "epsilon", "quantum_auc", "classical_correlated_auc", "classical_matched_filter_auc"]
    ].merge(separation, on=["eta", "epsilon"], validate="one_to_one")


def save_auc_plots(summary: pd.DataFrame, output_dir: Path) -> None:
    """Save AUC-versus-eta and AUC-versus-epsilon figures."""

    style = {"linewidth": 2.0, "marker": "o", "markersize": 5}
    figure, axis = plt.subplots(figsize=(8, 5))
    selected = summary[summary["epsilon"] == 0.20]
    for detector in DETECTORS:
        data = selected[selected["detector"] == detector].sort_values("eta")
        axis.plot(data["eta"], data["auc"], color=COLORS[detector], label=LABELS[detector], **style)
    axis.set_xlabel("Eta: target-correlation probability")
    axis.set_ylabel("ROC AUC")
    axis.set_title("AUC versus eta at epsilon=0.20")
    axis.set_ylim(0.0, 1.02)
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "final_auc_vs_eta.png", dpi=200)
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8, 5))
    selected = summary[summary["eta"] == 0.10]
    for detector in DETECTORS:
        data = selected[selected["detector"] == detector].sort_values("epsilon")
        axis.plot(data["epsilon"], data["auc"], color=COLORS[detector], label=LABELS[detector], **style)
    axis.set_xlabel("Epsilon: binary flip probability")
    axis.set_ylabel("ROC AUC")
    axis.set_title("AUC versus epsilon at eta=0.10")
    axis.set_ylim(0.0, 1.02)
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "final_auc_vs_noise.png", dpi=200)
    plt.close(figure)


def save_correlation_plot(correlation: pd.DataFrame, output_dir: Path) -> None:
    """Save correlation separation across all available conditions."""

    figure, axis = plt.subplots(figsize=(9, 6))
    for detector in DETECTORS:
        detector_data = correlation[correlation["detector"] == detector]
        for epsilon, data in detector_data.groupby("epsilon"):
            data = data.sort_values("eta")
            axis.plot(
                data["eta"],
                data["correlation_separation"],
                color=COLORS[detector],
                marker="o",
                linewidth=1.8,
                label=f"{LABELS[detector]}, epsilon={epsilon:g}",
            )
    axis.set_xlabel("Eta: target-correlation probability")
    axis.set_ylabel("Correlation separation")
    axis.set_title("Correlation separation across simulated conditions")
    axis.grid(alpha=0.3)
    axis.legend(fontsize="small", ncol=2)
    figure.tight_layout()
    figure.savefig(output_dir / "final_correlation_separation.png", dpi=200)
    plt.close(figure)


def save_difficult_roc(trials: pd.DataFrame, output_dir: Path) -> None:
    """Save all detector ROC curves at eta=0.10, epsilon=0.20."""

    figure, axis = plt.subplots(figsize=(7, 7))
    condition = trials[(trials["eta"] == 0.10) & (trials["epsilon"] == 0.20)]
    for detector in DETECTORS:
        detector_data = condition[condition["detector"] == detector]
        present = detector_data.loc[detector_data["target_present"], "statistic"]
        absent = detector_data.loc[~detector_data["target_present"], "statistic"]
        pfa, pd, _ = roc_curve(present, absent)
        auc = area_under_roc(present, absent)
        axis.plot(pfa, pd, color=COLORS[detector], linewidth=2.0, label=f"{LABELS[detector]} AUC={auc:.3f}")
    axis.plot([0.0, 1.0], [0.0, 1.0], "k--", alpha=0.6, label="Chance")
    axis.set_xlabel("Probability of False Alarm (Pfa)")
    axis.set_ylabel("Probability of Detection (Pd)")
    axis.set_title("ROC at eta=0.10, epsilon=0.20")
    axis.set_xlim(0.0, 1.0)
    axis.set_ylim(0.0, 1.0)
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_dir / "final_roc_difficult_condition.png", dpi=200)
    plt.close(figure)


def _condition_text(row: pd.Series) -> str:
    eta = row["eta"] if isinstance(row, pd.Series) else row.eta
    epsilon = row["epsilon"] if isinstance(row, pd.Series) else row.epsilon
    return f"eta={eta:.2f}, epsilon={epsilon:.2f}"


def write_findings(
    summary: pd.DataFrame,
    auc_summary: pd.DataFrame,
    auc_by_condition: pd.DataFrame,
    correlation: pd.DataFrame,
    literature: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Write computed findings and paper-ready results prose."""

    highest = summary.loc[summary.groupby("detector")["auc"].idxmax()].sort_values("detector")
    lowest = summary.loc[summary.groupby("detector")["auc"].idxmin()].sort_values("detector")
    common = auc_by_condition.copy()
    common["mean_auc"] = common[[f"{detector}_auc" for detector in DETECTORS]].mean(axis=1)
    difficult = common.loc[common["mean_auc"].idxmin()]
    high_rows = summary[summary["auc"] >= 0.9999]
    weak = summary[summary["eta"] == 0.10].sort_values(["epsilon", "detector"])
    high_noise = summary[summary["epsilon"] == 0.20].sort_values(["eta", "detector"])
    separation_difficult = correlation[(correlation["eta"] == difficult["eta"]) & (correlation["epsilon"] == difficult["epsilon"])]
    quantum_highest = highest[highest["detector"] == "quantum"].iloc[0]

    auc_lines = "\n".join(
        f"- `{row.detector}`: {_condition_text(row)} with AUC={row.auc:.5f}."
        for row in highest.itertuples()
    )
    low_lines = "\n".join(
        f"- `{row.detector}`: {_condition_text(row)} with AUC={row.auc:.5f}."
        for row in lowest.itertuples()
    )
    weak_text = "; ".join(f"{row.detector} AUC={row.auc:.5f}" for row in weak[weak["epsilon"] == 0.20].itertuples())
    high_noise_text = "; ".join(f"eta={row.eta:.2f}: {row.detector} AUC={row.auc:.5f}" for row in high_noise[high_noise["eta"] == 0.10].itertuples())
    separation_text = "; ".join(f"{row.detector} separation={row.correlation_separation:.5f}" for row in separation_difficult.itertuples())
    literature_sources = ", ".join(sorted(literature["source"].drop_duplicates()))

    findings = f"""# Scientific Findings

## 1. Overall observation

This frozen simulation compares three detectors under the same eta/epsilon grid and observation budget. Across the 48 detector-condition rows, performance generally improves as eta increases because target-present and target-absent statistics become more separated. Increasing epsilon generally reduces useful correlation, especially in the weak-target regime, although finite-sample variation produces occasional small non-monotonic changes.

    AUC ranges are:

{auc_summary.to_string(index=False, float_format=lambda value: f"{value:.5f}")}

## 2. Weak-target regime

At eta=0.10, the AUC values at the difficult noise level epsilon=0.20 are: {weak_text}. This is the weakest-target/high-noise corner of the grid and shows that all detectors retain some discrimination, but none should be interpreted as universally superior.

## 3. High-noise regime

At epsilon=0.20, the eta=0.10 condition is the most difficult common condition by mean AUC. As eta increases from 0.10 to 0.60, all three detectors approach perfect separation in the simulated data despite the binary flip noise.

At eta=0.10 and epsilon=0.20: {high_noise_text}.

## 4. Quantum detector behavior

The quantum detector's highest observed AUC is identified below. It performs strongly once eta is at least moderate, while its lowest observed AUC occurs at the weak-target/high-noise corner. Its results are comparable to the classical detectors in some conditions and lower in others. These data do not support a universal quantum advantage claim.

Highest observed quantum condition: {_condition_text(quantum_highest)} with AUC={quantum_highest['auc']:.5f}.

## 5. Classical correlated detector

The classically correlated detector follows the same qualitative trend: higher eta increases separation, and epsilon generally reduces it. Its classically generated correlation provides a useful baseline for distinguishing effects attributable to correlation from effects attributable specifically to entanglement. Under the current uniform binary assumptions, it has the same probability law as the existing matched-filter baseline despite being implemented separately.

## 6. Classical matched filter

The classical matched filter also achieves high AUC at moderate and high eta. Its lowest observed condition is reported below. It is a binary baseline in this implementation, not a continuous-amplitude physical matched filter.

## 7. Most difficult simulated condition

The lowest mean AUC across all three detectors occurs at {_condition_text(difficult)} with mean AUC={difficult['mean_auc']:.5f}. At this condition, the correlation separations are: {separation_text}.

## 8. Highest observed performance

Per-detector highest observed conditions are:

{auc_lines}

Per-detector lowest observed conditions are:

{low_lines}

AUC = 1.0 indicates perfect separation in that simulated condition, not universal quantum advantage.

## 9. Literature comparison

Our AUC and correlation-separation values are simulation results computed from the current project's trial data. The Ahmed 2026 values are explicitly labeled published reported values from an SSRN preprint, not peer-reviewed journal results. Yung et al. provides a theoretical discrete-signal quantum-illumination/channel-discrimination reference. The numerical values are not directly equivalent because channel definitions, noise representations, measurement rules, physical parameters, and metrics differ.

The literature sources represented in the comparison layer are: {literature_sources}. The published benchmark is intentionally kept separate from our simulation plots.

## 10. Main scientific interpretation

This simulation demonstrates how a shared binary target-correlation parameter and binary noise probability affect empirical detection discrimination for an entangled detector and two classical baselines. It demonstrates condition-dependent statistical behavior under a defined educational model. It does not determine which technology is universally better, establish physical radar performance, or prove experimental quantum advantage.
"""
    (output_dir / "scientific_findings.md").write_text(findings, encoding="utf-8")

    quantum_mean = auc_summary.loc[auc_summary["detector"] == "quantum", "mean_auc"].iloc[0]
    classical_correlated_mean = auc_summary.loc[auc_summary["detector"] == "classical_correlated", "mean_auc"].iloc[0]
    matched_mean = auc_summary.loc[auc_summary["detector"] == "classical_matched_filter", "mean_auc"].iloc[0]
    paper = f"""## Results

### Detection performance

The frozen experiment evaluated quantum, classically correlated, and classical matched-filter detectors over eta values 0.10, 0.20, 0.40, and 0.60 and epsilon values 0.00, 0.05, 0.10, and 0.20. The mean AUC values across the 16 conditions were {quantum_mean:.5f} for the quantum detector, {classical_correlated_mean:.5f} for the classically correlated detector, and {matched_mean:.5f} for the classical matched filter. Across all conditions, the AUC ranges were {auc_summary.loc[auc_summary.detector == 'quantum', 'min_auc'].iloc[0]:.5f}-{auc_summary.loc[auc_summary.detector == 'quantum', 'max_auc'].iloc[0]:.5f}, {auc_summary.loc[auc_summary.detector == 'classical_correlated', 'min_auc'].iloc[0]:.5f}-{auc_summary.loc[auc_summary.detector == 'classical_correlated', 'max_auc'].iloc[0]:.5f}, and {auc_summary.loc[auc_summary.detector == 'classical_matched_filter', 'min_auc'].iloc[0]:.5f}-{auc_summary.loc[auc_summary.detector == 'classical_matched_filter', 'max_auc'].iloc[0]:.5f}, respectively.

### Effect of target correlation

Increasing eta generally improved separation between target-present and target-absent trials. For example, at epsilon=0.00, the quantum AUC increased from {auc_by_condition.query('eta == 0.1 and epsilon == 0.0').quantum_auc.iloc[0]:.5f} at eta=0.10 to {auc_by_condition.query('eta == 0.6 and epsilon == 0.0').quantum_auc.iloc[0]:.5f} at eta=0.60. The corresponding classically correlated and matched-filter values changed from {auc_by_condition.query('eta == 0.1 and epsilon == 0.0').classical_correlated_auc.iloc[0]:.5f} to {auc_by_condition.query('eta == 0.6 and epsilon == 0.0').classical_correlated_auc.iloc[0]:.5f}, and from {auc_by_condition.query('eta == 0.1 and epsilon == 0.0').classical_matched_filter_auc.iloc[0]:.5f} to {auc_by_condition.query('eta == 0.6 and epsilon == 0.0').classical_matched_filter_auc.iloc[0]:.5f}. This behavior is consistent with eta increasing target-present correlation under the defined toy model.

### Effect of noise

At eta=0.10, increasing epsilon from 0.00 to 0.20 reduced AUC for all three detectors: quantum from {auc_by_condition.query('eta == 0.1 and epsilon == 0.0').quantum_auc.iloc[0]:.5f} to {auc_by_condition.query('eta == 0.1 and epsilon == 0.2').quantum_auc.iloc[0]:.5f}, classically correlated from {auc_by_condition.query('eta == 0.1 and epsilon == 0.0').classical_correlated_auc.iloc[0]:.5f} to {auc_by_condition.query('eta == 0.1 and epsilon == 0.2').classical_correlated_auc.iloc[0]:.5f}, and matched filter from {auc_by_condition.query('eta == 0.1 and epsilon == 0.0').classical_matched_filter_auc.iloc[0]:.5f} to {auc_by_condition.query('eta == 0.1 and epsilon == 0.2').classical_matched_filter_auc.iloc[0]:.5f}. At higher eta, the larger target-present separation keeps AUC close to one even at epsilon=0.20.

### Comparison with classical detectors

The quantum detector was not uniformly highest. At eta=0.10 and epsilon=0.20, its AUC was {auc_by_condition.query('eta == 0.1 and epsilon == 0.2').quantum_auc.iloc[0]:.5f}, compared with {auc_by_condition.query('eta == 0.1 and epsilon == 0.2').classical_correlated_auc.iloc[0]:.5f} and {auc_by_condition.query('eta == 0.1 and epsilon == 0.2').classical_matched_filter_auc.iloc[0]:.5f}. At eta=0.40 and epsilon=0.00, all three reached or effectively reached AUC=1.0. These are condition-specific results; AUC=1.0 indicates perfect separation in that simulated condition, not universal quantum advantage.

The condition-by-condition differences were generally small once eta reached 0.20 or higher, and several conditions produced identical or nearly identical AUC values. At eta=0.10, the detectors separated more visibly: the quantum detector was highest at epsilon=0.05 and epsilon=0.10, while the matched filter was highest at epsilon=0.00 and epsilon=0.20. This variation reinforces that detector ordering depends on the defined target and noise condition rather than establishing a universal ranking.

### Comparison with prior work

The current AUC and correlation-separation values are simulation outputs from this project. Ahmed 2026 provides explicitly reported correlation-separation values in an SSRN preprint, while Yung et al. provides a theoretical discrete-signal channel-discrimination benchmark. Their metrics and physical conditions are not automatically equivalent to the present toy eta/epsilon model, so no direct numerical ranking is inferred.

### Limitations

The model is a simplified two-qubit educational simulation. Eta is a toy target-correlation parameter rather than optical reflectivity, and epsilon is a binary flip probability rather than a complete thermal optical-noise model. The detectors use equal observation counts, but the physical resource models and measurement tasks are not those of a full optical quantum-illumination receiver. The results therefore demonstrate condition-dependent behavior of the defined simulation rather than a universal technology comparison.

The reported AUC values summarize empirical threshold discrimination over the generated trial statistics, whereas correlation separation summarizes the difference between two mean statistics. Neither metric is a substitute for the minimum-error channel-discrimination quantities reported in theoretical work. Likewise, the Ahmed preprint values are retained as reference-only reported quantities because their conditions and normalization are not demonstrated to match this platform. The figures and tables should therefore be read as a reproducible analysis of this frozen model, with the literature serving as context rather than as a directly matched benchmark.
"""
    (output_dir / "paper_results_section.md").write_text(paper, encoding="utf-8")


def main() -> None:
    """Generate final tables, figures, and scientific text."""

    results_dir = PROJECT_ROOT / "results"
    summary, trials, literature, _ = load_results(results_dir)
    auc_summary, auc_by_condition = build_auc_tables(summary)
    correlation = build_correlation_table(trials)
    final_table = build_final_results_table(auc_by_condition, correlation)
    auc_summary.to_csv(results_dir / "final_auc_summary.csv", index=False)
    auc_by_condition.to_csv(results_dir / "detector_auc_comparison.csv", index=False)
    correlation.to_csv(results_dir / "final_correlation_summary.csv", index=False)
    final_table.to_csv(results_dir / "final_results_table.csv", index=False)
    save_auc_plots(summary, results_dir)
    save_correlation_plot(correlation, results_dir)
    save_difficult_roc(trials, results_dir)
    write_findings(summary, auc_summary, auc_by_condition, correlation, literature, results_dir)
    print(f"Generated final results in {results_dir.resolve()}")


if __name__ == "__main__":
    main()
