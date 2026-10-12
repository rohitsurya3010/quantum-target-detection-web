"""Literature-comparison analysis for the frozen detector model."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DETECTOR_LABELS = {
    "quantum": "Quantum",
    "classical_correlated": "Classically correlated",
    "classical_matched_filter": "Classical matched filter",
}

# Values are transcribed only from the user-supplied Ahmed preprint summary.
AHMED_REPORTED_CORRELATION_SEPARATION = (
    {
        "source": "Ahmed 2026 preprint",
        "detector": "quantum",
        "metric": "correlation_separation",
        "condition": "zero background noise",
        "value": 0.0100,
        "notes": "Published reported value; entangled probe.",
    },
    {
        "source": "Ahmed 2026 preprint",
        "detector": "quantum",
        "metric": "correlation_separation",
        "condition": "high background noise",
        "value": 0.0025,
        "notes": "Published reported value; entangled probe.",
    },
    {
        "source": "Ahmed 2026 preprint",
        "detector": "classical_correlated",
        "metric": "correlation_separation",
        "condition": "zero background noise",
        "value": 0.1000,
        "notes": "Published reported value; classically correlated probe.",
    },
    {
        "source": "Ahmed 2026 preprint",
        "detector": "classical_correlated",
        "metric": "correlation_separation",
        "condition": "high background noise",
        "value": 0.0500,
        "notes": "Published reported value; classically correlated probe.",
    },
)


def correlation_separation(trials: pd.DataFrame) -> pd.DataFrame:
    """Calculate mean target-present minus target-absent statistic by condition."""

    required_columns = {"detector", "eta", "epsilon", "target_present", "statistic"}
    missing_columns = required_columns.difference(trials.columns)
    if missing_columns:
        raise ValueError(f"trial data is missing columns: {sorted(missing_columns)}")

    grouped = (
        trials.groupby(
            ["detector", "eta", "epsilon", "target_present"],
            as_index=False,
        )["statistic"]
        .mean()
        .rename(columns={"statistic": "mean_statistic"})
    )
    present = grouped[grouped["target_present"]].drop(columns="target_present")
    absent = grouped[~grouped["target_present"]].drop(columns="target_present")
    separation = present.merge(
        absent,
        on=["detector", "eta", "epsilon"],
        suffixes=("_present", "_absent"),
        validate="one_to_one",
    )
    separation["correlation_separation"] = (
        separation["mean_statistic_present"]
        - separation["mean_statistic_absent"]
    )
    return separation[
        ["detector", "eta", "epsilon", "correlation_separation"]
    ].sort_values(["detector", "epsilon", "eta"], ignore_index=True)


def model_comparison() -> pd.DataFrame:
    """Return qualitative comparison metadata for the three current models."""

    rows = [
        {
            "Model": "Quantum detector",
            "Metric": "Normalized agreement correlation; AUC; Pd/Pfa",
            "Noise representation": "Per-shot binary X-flip probability epsilon via Kraus channel",
            "Target representation": "Bell-pair probe/reference correlation controlled by toy eta",
            "Measurement": "Computational-basis probe/reference agreement",
            "Observation budget": "256 Aer shots per trial by default",
            "AUC available": "Yes",
            "Pd/Pfa available": "Yes",
            "Correlation separation available": "Yes",
            "Physical fidelity": "Simplified two-qubit educational model",
            "Main limitation": "Not optical quantum illumination; eta is not physical reflectivity",
        },
        {
            "Model": "Classical correlated detector",
            "Metric": "Normalized agreement correlation; AUC; Pd/Pfa",
            "Noise representation": "Independent binary flip probability epsilon",
            "Target representation": "Classical binary probe/reference correlation controlled by eta",
            "Measurement": "Classical probe/reference agreement",
            "Observation budget": "256 binary samples per trial by default",
            "AUC available": "Yes",
            "Pd/Pfa available": "Yes",
            "Correlation separation available": "Yes",
            "Physical fidelity": "Simplified discrete-variable baseline",
            "Main limitation": "Same probability law as current matched-filter baseline under uniform bits",
        },
        {
            "Model": "Classical matched filter",
            "Metric": "Normalized agreement correlation; AUC; Pd/Pfa",
            "Noise representation": "Independent binary flip probability epsilon",
            "Target representation": "Binary reference/return agreement controlled by eta",
            "Measurement": "Classical reference/return agreement",
            "Observation budget": "256 binary samples per trial by default",
            "AUC available": "Yes",
            "Pd/Pfa available": "Yes",
            "Correlation separation available": "Yes",
            "Physical fidelity": "Simplified discrete-variable baseline",
            "Main limitation": "Not a continuous-amplitude physical matched filter in current code",
        },
    ]
    return pd.DataFrame(rows)


def build_comparison_table(
    separation: pd.DataFrame,
) -> pd.DataFrame:
    """Combine our simulation separation values with published reference rows."""

    ours = separation.assign(
        source="our_simulation",
        metric="correlation_separation",
        condition=lambda frame: frame.apply(
            lambda row: f"eta={row['eta']:g}, epsilon={row['epsilon']:g}", axis=1
        ),
        value=separation["correlation_separation"],
        notes="Computed from current trial_statistics.csv; not a published value.",
    )[["source", "detector", "metric", "condition", "value", "notes"]]
    published = pd.DataFrame(AHMED_REPORTED_CORRELATION_SEPARATION)
    theory = pd.DataFrame(
        [
            {
                "source": "Yung et al. 2020",
                "detector": "quantum_illumination",
                "metric": "minimum_detection_error",
                "condition": "one-shot discrete-signal channel discrimination",
                "value": None,
                "notes": "Theoretical result; no numerical value copied into this table.",
            },
            {
                "source": "Yung et al. 2020",
                "detector": "conventional_illumination",
                "metric": "minimum_detection_error",
                "condition": "one-shot discrete-signal channel discrimination",
                "value": None,
                "notes": "Theoretical result; no numerical value copied into this table.",
            },
        ]
    )
    return pd.concat([ours, published, theory], ignore_index=True)


def save_literature_artifacts(
    trials: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """Write comparison CSV files and separate simulation/reference plots."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    separation = correlation_separation(trials)
    comparison = build_comparison_table(separation)
    comparison.to_csv(output_path / "literature_comparison.csv", index=False)
    model_comparison().to_csv(output_path / "model_comparison.csv", index=False)

    figure, axis = plt.subplots(figsize=(9, 6))
    for detector, detector_data in separation.groupby("detector"):
        for epsilon, curve in detector_data.groupby("epsilon"):
            curve = curve.sort_values("eta")
            axis.plot(
                curve["eta"],
                curve["correlation_separation"],
                marker="o",
                label=f"{DETECTOR_LABELS[detector]}, epsilon={epsilon:g}",
            )
    axis.set_xlabel("Eta: toy target-correlation probability")
    axis.set_ylabel("Correlation separation")
    axis.set_title("Our simulation: correlation separation")
    axis.grid(alpha=0.3)
    axis.legend(fontsize="small")
    figure.tight_layout()
    figure.savefig(output_path / "correlation_separation_ours.png", dpi=150)
    plt.close(figure)

    published = pd.DataFrame(AHMED_REPORTED_CORRELATION_SEPARATION)
    figure, axis = plt.subplots(figsize=(8, 5))
    for detector, detector_data in published.groupby("detector"):
        axis.plot(
            detector_data["condition"],
            detector_data["value"],
            marker="o",
            label=DETECTOR_LABELS[detector],
        )
    axis.set_xlabel("Ahmed 2026 preprint condition")
    axis.set_ylabel("Reported correlation separation")
    axis.set_title("Ahmed 2026 preprint - published reported values")
    axis.grid(alpha=0.3)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path / "published_correlation_benchmark.png", dpi=150)
    plt.close(figure)
