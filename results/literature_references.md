# Literature References

This comparison layer provides context for the current platform. It does not claim that the current simulation reproduces either reference exactly.

## Reference 1: Yung et al. (2020)

- **Title:** *One-shot detection limits of quantum illumination with discrete signals*
- **Authors:** Man-Hong Yung, Fei Meng, Xiao-Ming Zhang, and Ming-Jing Zhao
- **Year:** 2020
- **Status:** Peer-reviewed journal article, published in *npj Quantum Information*, volume 6, article 75
- **URL:** https://www.nature.com/articles/s41534-020-00303-z
- **Model type:** Discrete-signal quantum-channel discrimination with finite-dimensional environmental noise
- **Detector/measurement method:** The paper analyzes conventional and quantum illumination and derives optimal one-shot discrimination performance, including analytic solutions over parameter regions. It is not the same as this project's computational-basis agreement statistic.
- **Reported evaluation metric:** Minimum detection-error performance / minimum error probability for one-shot channel discrimination.
- **Why it is relevant:** It is a theoretical discrete-signal benchmark for target detection with environmental noise and explicitly studies when entangled resources can or cannot help.
- **Major differences from this project:** The paper uses a channel-discrimination formulation, finite-dimensional environment states, and optimized quantum decision theory. This project uses a two-qubit Bell pair, toy `eta` correlation probability, binary `epsilon` flips, normalized agreement correlation, and empirical Pd/Pfa/ROC/AUC. The project's `eta` is not physical optical reflectivity, and no paper numerical values are copied here because the current comparison does not use the paper's exact parameterization or decision problem.

## Reference 2: Ahmed (2026)

- **Title:** *Quantum Illumination for Stealth Target Detection: A Discrete-Qubit Toy Model on PKTron and IBM Quantum Hardware*
- **Author:** Zuhair Ahmed
- **Year:** 2026
- **Status:** **SSRN preprint; not a peer-reviewed journal result**
- **URL:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7381919
- **Model type:** Discrete-qubit toy-model comparison of an entangled Bell-pair probe and a classically correlated separable probe.
- **Detector/measurement method:** Joint $Z\otimes Z$ correlation measurement, according to the supplied reference description.
- **Reported evaluation metric:** Correlation separation between target-present and target-absent cases.
- **Why it is relevant:** It is close in spirit to this project's educational two-qubit comparison and uses an entangled probe versus a classically correlated probe with a correlation measurement.
- **Major differences from this project:** The parameter definitions, channel/noise assumptions, hardware context, sampling details, and reported conditions are not established as identical to this project. This project additionally includes a classical matched-filter baseline and evaluates empirical ROC/AUC/Pd/Pfa. The supplied Ahmed values are retained only as explicitly reported endpoint values, not converted into this project's AUC or treated as directly comparable numerical performance.

## Reported Ahmed values retained in this repository

The following values are stored as `published_reported_value` in `literature_comparison.csv`, exactly as supplied for this comparison task:

- Entangled probe: correlation separation `0.0100` at zero background noise.
- Entangled probe: correlation separation `0.0025` at high background noise.
- Classically correlated probe: correlation separation `0.1000` at zero background noise.
- Classically correlated probe: correlation separation `0.0500` at high background noise.

No intermediate values are invented. Yung et al. theoretical results are represented qualitatively and without manually copied numerical values.

## Comparability warning

The current platform is a simplified two-qubit/discrete-variable educational simulation. Its normalized correlation separation, AUC, Pd, and Pfa are not automatically equivalent to physical optical reflectivity, thermal optical background, photon number, minimum-error POVMs, or continuous-variable quantum illumination metrics. The simulation and published benchmark plots are therefore kept separate.
