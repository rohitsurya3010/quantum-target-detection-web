"""Classically correlated binary detector for the three-detector comparison."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ClassicallyCorrelatedConfig:
    """Settings for independent classical probe/reference observations."""

    samples: int = 256
    eta: float = 0.2
    epsilon: float = 0.05

    def __post_init__(self) -> None:
        if self.samples < 2:
            raise ValueError("samples must be at least 2")
        if not 0.0 <= self.eta <= 1.0:
            raise ValueError("eta must be between 0 and 1")
        if not 0.0 <= self.epsilon <= 0.5:
            raise ValueError("epsilon must be between 0 and 0.5")


def run_classically_correlated_trial(
    simulation_config: ClassicallyCorrelatedConfig,
    target_present: bool,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Run one classical A/B correlation trial.

    A is the classical probe and B is the retained reference. Under the
    target-present hypothesis, B equals A with probability ``eta`` and is an
    independent uniform bit otherwise. Under the absent hypothesis, A and B
    are independent uniform bits. Binary flip noise is applied independently
    to A with probability ``epsilon`` before the agreement statistic is formed.
    """

    probe = rng.integers(0, 2, size=simulation_config.samples)
    reference = rng.integers(0, 2, size=simulation_config.samples)
    correlated = target_present & (
        rng.random(simulation_config.samples) < simulation_config.eta
    )
    reference[correlated] = probe[correlated]

    flipped = rng.random(simulation_config.samples) < simulation_config.epsilon
    probe[flipped] = 1 - probe[flipped]
    statistic = float(np.mean(np.where(probe == reference, 1.0, -1.0)))

    return {
        "statistic": statistic,
        "target_present": target_present,
        "eta": simulation_config.eta,
        "epsilon": simulation_config.epsilon,
        "correlated_observations": int(np.sum(correlated)),
        "flipped_observations": int(np.sum(flipped)),
    }
