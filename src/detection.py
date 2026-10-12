"""Detection metrics shared by quantum and classical experiments."""

from __future__ import annotations

from typing import Iterable

import numpy as np
from scipy.integrate import trapezoid


def detection_metrics(
    present_statistics: Iterable[float],
    absent_statistics: Iterable[float],
    threshold: float,
) -> dict[str, float]:
    """Calculate Pd and Pfa for a higher-statistic-means-target detector."""

    present = np.asarray(list(present_statistics), dtype=float)
    absent = np.asarray(list(absent_statistics), dtype=float)
    if present.size == 0 or absent.size == 0:
        raise ValueError("present and absent statistics must both be non-empty")

    return {
        "threshold": float(threshold),
        "pd": float(np.mean(present >= threshold)),
        "pfa": float(np.mean(absent >= threshold)),
    }


def roc_curve(
    present_statistics: Iterable[float],
    absent_statistics: Iterable[float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return false-alarm rates, detection rates, and thresholds."""

    present = np.asarray(list(present_statistics), dtype=float)
    absent = np.asarray(list(absent_statistics), dtype=float)
    if present.size == 0 or absent.size == 0:
        raise ValueError("present and absent statistics must both be non-empty")

    all_statistics = np.concatenate((present, absent))
    thresholds = np.r_[np.inf, np.unique(all_statistics)[::-1], -np.inf]
    pd_values = np.array([np.mean(present >= threshold) for threshold in thresholds])
    pfa_values = np.array([np.mean(absent >= threshold) for threshold in thresholds])
    order = np.argsort(pfa_values)
    return pfa_values[order], pd_values[order], thresholds[order]


def area_under_roc(
    present_statistics: Iterable[float],
    absent_statistics: Iterable[float],
) -> float:
    """Calculate ROC AUC using the trapezoidal rule."""

    pfa_values, pd_values, _ = roc_curve(present_statistics, absent_statistics)
    return float(trapezoid(pd_values, pfa_values))
