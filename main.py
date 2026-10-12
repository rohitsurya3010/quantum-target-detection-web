"""Command-line entry point for the quantum target detection experiments."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import ExperimentConfig, run_sweep, save_results


def _parse_float_list(value: str) -> tuple[float, ...]:
    """Parse a comma-separated list of floating-point values."""

    try:
        values = tuple(float(item.strip()) for item in value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected comma-separated numbers") from error
    if not values:
        raise argparse.ArgumentTypeError("at least one value is required")
    return values


def build_parser() -> argparse.ArgumentParser:
    """Build the experiment CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eta-values", type=_parse_float_list, default=(0.1, 0.2, 0.4, 0.6))
    parser.add_argument("--epsilon-values", type=_parse_float_list, default=(0.0, 0.05, 0.1, 0.2))
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--quantum-shots", type=int, default=256)
    parser.add_argument("--classical-samples", type=int, default=256)
    parser.add_argument("--seed", type=int, default=20260912)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    return parser


def main() -> None:
    """Run the configured sweep and save its results."""

    arguments = build_parser().parse_args()
    config = ExperimentConfig(
        eta_values=arguments.eta_values,
        epsilon_values=arguments.epsilon_values,
        trials=arguments.trials,
        quantum_shots=arguments.quantum_shots,
        classical_samples=arguments.classical_samples,
        seed=arguments.seed,
    )
    summary, trials = run_sweep(config)
    save_results(summary, trials, arguments.output_dir)
    print(summary.to_string(index=False))
    print(f"\nSaved results to {arguments.output_dir.resolve()}")


if __name__ == "__main__":
    main()
