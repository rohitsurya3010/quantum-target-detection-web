"""Generate literature-comparison artifacts from current experiment results."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from src.literature import save_literature_artifacts


def main() -> None:
    """Generate comparison tables and separate plots from results files."""

    results_dir = PROJECT_ROOT / "results"
    trials = pd.read_csv(results_dir / "trial_statistics.csv")
    save_literature_artifacts(trials, results_dir)
    print(f"Saved literature artifacts to {results_dir.resolve()}")


if __name__ == "__main__":
    main()
