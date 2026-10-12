"""Configurable binary target channel for the educational quantum detector."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit import QuantumCircuit


@dataclass(frozen=True)
class ChannelConfig:
    """Parameters for target correlation and binary return noise.

    ``eta`` is the probability that a target-present probe remains correlated
    with the retained reference. Otherwise it is replaced by an independent
    uniformly random binary return. ``epsilon`` is the probability of a
    measurement-relevant binary flip applied after the target channel.
    """

    eta: float = 0.2
    epsilon: float = 0.05

    def __post_init__(self) -> None:
        if not 0.0 <= self.eta <= 1.0:
            raise ValueError("eta must be between 0 and 1")
        if not 0.0 <= self.epsilon <= 0.5:
            raise ValueError("epsilon must be between 0 and 0.5")


def apply_target_channel(
    circuit: QuantumCircuit,
    probe_qubit: int,
    config: ChannelConfig,
    target_present: bool,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Apply one sampled target-return channel to ``probe_qubit``.

    The circuit begins with an entangled probe/reference pair. For a present
    target, the probe remains correlated with probability ``eta``; otherwise
    it is replaced by an independent uniform binary return. For an absent
    target, it is always replaced by independent uniform background. A sampled
    X flip then applies the common binary noise probability ``epsilon``.
    Metadata makes the sampled event inspectable.
    """

    correlated = bool(target_present and rng.random() < config.eta)
    if not correlated:
        circuit.reset(probe_qubit)
        if rng.random() < 0.5:
            circuit.x(probe_qubit)

    flipped = bool(rng.random() < config.epsilon)
    if flipped:
        circuit.x(probe_qubit)

    return {
        "target_present": target_present,
        "correlated": correlated,
        "background": not correlated,
        "flipped": flipped,
    }
