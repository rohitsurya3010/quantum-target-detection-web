"""Classical binary correlation baseline for the fair comparison."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ClassicalSimulationConfig:
    """Settings for one classical binary observation sequence."""

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


def run_classical_trial(
    simulation_config: ClassicalSimulationConfig,
    target_present: bool,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Run a classical binary correlation trial.

    Each sample has a target-correlated return with probability ``eta`` when
    the target is present. Otherwise, including every absent-target sample,
    the return is an independent uniform binary background. The same binary
    flip probability ``epsilon`` is then applied to the return.
    """

    reference = rng.integers(0, 2, size=simulation_config.samples)
    correlated = target_present & (rng.random(simulation_config.samples) < simulation_config.eta)
    target_return = rng.integers(0, 2, size=simulation_config.samples)
    target_return[correlated] = reference[correlated]
    flipped = rng.random(simulation_config.samples) < simulation_config.epsilon
    target_return[flipped] = 1 - target_return[flipped]
    statistic = float(
        np.mean(np.where(reference == target_return, 1.0, -1.0))
    )

    return {
        "statistic": statistic,
        "target_present": target_present,
        "eta": simulation_config.eta,
        "epsilon": simulation_config.epsilon,
    }
