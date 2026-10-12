# Quantum Correlation Simulation Platform

This project is a simplified educational simulation of quantum illumination and correlation detection. It compares three detectors under matched target and noise conditions:

1. A quantum entangled Bell-pair detector.
2. A classically correlated binary detector.
3. A classical binary matched-filter detector.

It is not a complete physical quantum-illumination receiver and does not assume quantum advantage. The experiments report all three methods objectively; depending on the sampled condition, any detector can perform better, similarly, or worse.

## Project layout

- `src/channel.py`: configurable binary target-correlation and flip-noise model.
- `src/quantum.py`: Bell-pair preparation, Qiskit Aer execution, and quantum correlation statistic.
- `src/classical_correlated.py`: classical A/B probe/reference correlation detector.
- `src/classical.py`: seeded classical binary matched-filter baseline.
- `src/literature.py`: trial-level correlation-separation analysis and literature artifact generation.
- `src/detection.py`: Pd, Pfa, ROC, and AUC calculations.
- `src/analysis.py`: reproducible sweeps, Pandas tables, and Matplotlib plots.
- `experiments/main.py`: command-line experiment runner.
- `experiments/literature_comparison.py`: generates literature comparison tables and separate plots from existing results.
- `results/`: generated CSV files and figures.

## Setup

Create or activate a Python environment, then install dependencies:

```text
python -m pip install -r requirements.txt
```

The required stack is Qiskit, Qiskit Aer, NumPy, SciPy, Pandas, and Matplotlib.

## Run

Run the default sweep:

```text
python experiments/main.py
```

Run a smaller reproducible sweep while exploring parameters:

```text
python experiments/main.py --eta-values 0.1,0.3,0.6 --epsilon-values 0.0,0.1,0.2 --trials 100 --seed 20260912
```

Useful options include `--quantum-shots`, `--classical-samples`, and `--output-dir`.

## Outputs

The runner writes these files to the selected output directory:

- `summary.csv`: one row per detector, eta, and epsilon condition, including ROC AUC and zero-threshold Pd/Pfa.
- `trial_statistics.csv`: raw trial-level detector statistics.
- `auc_comparison.png`: AUC versus eta for each epsilon level and detector.
- `roc_best_condition.png`: ROC curve for the best observed detector/condition in the sweep.

The shared seed controls NumPy sampling for reproducible classical sequences and channel events. Aer measurement sampling is configured through the trial shot count. Quantum shots and classical samples are set to the same value and each contributes one binary agreement observation.

## Model notes

A Bell pair is prepared with H and CNOT gates. Qubit A is the probe and qubit B is the retained reference. `eta` is the probability that a target-present observation remains correlated with the reference. With probability `1 - eta`, and for every absent-target observation, the probe is replaced by an independent uniformly random binary return. `epsilon` is the common probability of an X bit flip applied after the target/background process.

The classically correlated detector uses two classical binary variables: A is the probe and B is the retained reference. When the target is present, B equals A with probability `eta`; otherwise B is independent uniform background. When the target is absent, A and B are independent uniform bits. Epsilon flips the probe independently before the normalized agreement statistic is calculated.

The existing classical detector uses its own binary matched-filter construction under the same observation budget and eta/epsilon settings. All three detectors use the same normalized agreement statistic where applicable, and all three are evaluated with the same Pd, Pfa, ROC, and AUC functions. The models are simplified educational baselines under defined simulation assumptions, not a physical quantum-illumination receiver and not evidence of quantum advantage.

## Literature Comparison

This platform is a simplified two-qubit educational model. Its `eta`, `epsilon`, normalized agreement statistic, observation budget, and empirical AUC/Pd/Pfa metrics are defined by this repository and are not automatically equivalent to physical optical reflectivity, thermal optical background, photon number, minimum-error POVMs, or continuous-variable quantum illumination.

Yung et al. (2020), *One-shot detection limits of quantum illumination with discrete signals*, is a peer-reviewed *npj Quantum Information* theoretical benchmark. It formulates discrete-signal quantum illumination as a finite-dimensional quantum-channel discrimination problem and studies minimum detection-error performance. It is relevant context, but this project does not reproduce its channel, optimized measurement, or error formulation exactly.

Ahmed (2026), *Quantum Illumination for Stealth Target Detection: A Discrete-Qubit Toy Model on PKTron and IBM Quantum Hardware*, is an SSRN **preprint**, not a peer-reviewed journal result. It is close in spirit because it compares an entangled Bell-pair probe with a classically correlated separable probe using a joint correlation measurement. Its reported correlation-separation values are retained separately and are not treated as equivalent to this project's AUC.

Generate the comparison artifacts from the current trial-level results without rerunning or changing the detector experiment:

```text
python experiments/literature_comparison.py
```

Generated files include:

- `results/literature_references.md`: reference metadata and comparability warnings.
- `results/literature_comparison.csv`: our correlation-separation values plus explicitly reported Ahmed values and qualitative Yung theoretical rows.
- `results/model_comparison.csv`: model, noise, measurement, budget, and fidelity comparison table.
- `results/correlation_separation_ours.png`: our three detectors by eta/epsilon.
- `results/published_correlation_benchmark.png`: only the explicitly reported Ahmed endpoint values.

Our simulation values and published values are plotted separately because the conditions, channel definitions, measurement procedures, and metric normalizations are not demonstrably identical. No direct numerical superiority or quantum advantage claim follows from these comparisons.


## Streamlit Frontend

This repository includes `app.py`, an interactive Streamlit frontend connected to the existing Qiskit and classical detector implementation.

### Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

### Deploy

Deploy from this GitHub repository using Streamlit Community Cloud. Select branch `main` and set the main file path to `app.py`. Keep the `src/`, `results/` and `requirements.txt` files in the repository.

The app loads the saved `results/summary.csv` on startup. Use the sidebar controls and click **Run Simulation** to execute the actual `ExperimentConfig` / `run_sweep()` backend. Newly generated results remain in the session and can be downloaded; they do not overwrite the saved project results.
