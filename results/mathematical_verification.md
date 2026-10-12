# Mathematical Verification Report

Date: 2026-09-22

## Final Status

**PASS WITH LIMITATIONS**

The current implementation is mathematically consistent with its stated simplified binary model. No detector algorithms, parameters, seeds, observation budgets, or metric definitions were changed during this audit.

This is a simplified two-qubit/discrete-variable educational simulation inspired by quantum illumination and correlation detection. It is not a full physical optical quantum-illumination model. The results do not establish real radar performance, physical optical reflectivity, universal quantum advantage, or experimental quantum advantage.

## 1. Quantum State Preparation

`src/quantum.py:create_bell_pair` creates a two-qubit circuit and applies:

1. `H` to qubit 0.
2. `CNOT` with control qubit 0 and target qubit 1.

Starting from $|00\rangle$:

$$
|00\rangle \xrightarrow{H_0}
\frac{|00\rangle + |10\rangle}{\sqrt{2}}
\xrightarrow{CNOT_{0\rightarrow1}}
\frac{|00\rangle + |11\rangle}{\sqrt{2}}.
$$

Therefore the prepared state is $|\Phi^+\rangle$.

The project consistently treats:

- Qubit 0 as probe $A$.
- Qubit 1 as retained reference $B$.

The computational-basis measurement records both qubits. The correlation implementation compares the two measured bits, so Qiskit’s classical-register display order does not affect the equality statistic.

## 2. Target and Channel Model

The active experiment uses `_target_return_channel` in `src/quantum.py`. `src/channel.py` contains the explicit sampled reference implementation used by tests and documents the same model.

The parameter `eta` is a toy target-correlation probability:

- For target present, the probe/reference correlation is preserved with probability `eta`.
- With probability `1 - eta`, the probe is replaced by an independent uniformly random binary return.
- For target absent, `eta` is forced to zero, so the returned probe is independent uniform background.

`eta` is **not** a physical optical reflectivity.

The Kraus construction implements the mixture

$$
\mathcal{E}_{\eta}(\rho) =
\eta\rho + (1-\eta)\frac{I}{2},
$$

for target present, and the same expression with $\eta=0$ for target absent. Only qubit 0 is passed through this channel. The reference qubit 1 is retained and is not acted on by the target channel.

## 3. Noise Model

`epsilon` is the probability of an independent binary flip. The active quantum channel composes the target/background map with an $X$ flip:

$$
\mathcal{N}_{\epsilon}(\rho) =
(1-\epsilon)\rho + \epsilon X\rho X.
$$

The Kraus construction applies this independently to every Aer shot. The explicit `src/channel.py` implementation has the same documented semantics when used directly: it samples a binary flip independently for each channel application and applies `X` when selected.

Thus, for the measured agreement correlation, an $X$ flip changes the sign of the Bell-state correlation. The reference is not flipped.

## 4. Target-Present Model

For target present, the expected agreement correlation is:

$$
E[C\mid H_1] = \eta(1-2\epsilon).
$$

Reason:

- The correlated branch contributes $+1$ before noise.
- The independent-background branch contributes expected correlation $0$.
- A binary flip changes $+1$ to $-1$, producing factor $(1-\epsilon)-\epsilon=1-2\epsilon$.

Increasing `eta` therefore generally increases useful target-present correlation. Increasing `epsilon` generally reduces it for $0\le\epsilon\le0.5$.

This is an expected-value statement; finite trials and finite observation budgets can produce non-monotonic individual AUC values.

## 5. Target-Absent Model

For target absent, the active quantum channel uses $\eta=0$ and maps the probe to maximally mixed independent background:

$$
\rho_A \mapsto \frac{I}{2}.
$$

The retained reference is independent of this background probe. The classically correlated detector generates independent uniform probe/reference bits under the absent hypothesis. The existing binary classical detector also generates an independent uniform background return under the absent hypothesis.

For independent uniform binary variables:

$$
P(\text{same})=\frac12,
\qquad
P(\text{different})=\frac12,
$$

so:

$$
E[C\mid H_0]=0.
$$

Finite-sample statistics fluctuate around zero.

## 6. Correlation Statistic

`src/quantum.py:correlation_from_counts` computes:

$$
C = 2\frac{N_{same}}{N_{total}}-1,
$$

where:

$$
N_{same}=N_{00}+N_{11},
\qquad
N_{different}=N_{01}+N_{10}.
$$

Therefore:

$$
C = \frac{N_{same}-N_{different}}{N_{total}}.
$$

The same normalized agreement statistic is used by both classical detector implementations through `np.mean(+1 for agreement, -1 for disagreement)`.

Controlled tests confirm:

- Perfect agreement: $C=+1$.
- Balanced independent outcomes: $C=0$.
- Perfect disagreement: $C=-1$.

## 7. Pd and Pfa

`src/detection.py:detection_metrics` uses a higher-statistic-means-target rule at threshold $\tau$:

$$
P_d(\tau)=P(C\ge\tau\mid H_1),
$$

$$
P_{fa}(\tau)=P(C\ge\tau\mid H_0).
$$

Empirically, these are the fractions of target-present and target-absent trial statistics meeting the threshold.

In `src/analysis.py`, `pd_at_zero` and `pfa_at_zero` are specifically:

$$
P_d(0),\qquad P_{fa}(0).
$$

They are measurements at threshold zero, not overall detector performance and not substitutes for the full ROC or AUC.

## 8. ROC Definition

`src/detection.py:roc_curve` constructs thresholds from the combined observed present and absent statistics, with additional $+\infty$ and $-\infty$ endpoints. For every threshold it calculates empirical $P_{fa}$ and $P_d$, then returns:

- x-axis: Pfa.
- y-axis: Pd.
- thresholds: the actual statistic thresholds used.

The diagonal from $(0,0)$ to $(1,1)$ in the plots represents chance-level random discrimination.

The corrected `roc_best_condition.png` plots all three detectors at the selected eta/epsilon condition using their own trial-level statistics.

## 9. AUC Definition

`area_under_roc` calls `roc_curve` and integrates Pd with respect to Pfa using SciPy’s trapezoidal integration.

Interpretation:

- AUC approximately $0.5$: random discrimination.
- AUC approaching $1$: strong separation.
- AUC equal to $1$: perfect separation for that simulated condition.

The current default result table has all AUC values within `[0,1]`:

| Detector | Minimum AUC | Maximum AUC |
|---|---:|---:|
| quantum | 0.69395 | 1.00000 |
| classical_correlated | 0.73830 | 1.00000 |
| classical_matched_filter | 0.77870 | 1.00000 |

AUC equal to one is not quantum advantage.

## 10. Observation-Budget Fairness

The default configuration sets:

- `quantum_shots = 256`.
- `classical_samples = 256`.

`ExperimentConfig` rejects unequal values. Each quantum Aer shot is one fresh Bell-pair measurement observation under the stochastic channel. Each classical sample is one binary probe/reference or reference/return observation. Each trial therefore aggregates the same number of binary observations for all three detectors.

The quantum detector uses additional Bell-pair preparation and two-qubit resources. Equal observation counts do not imply equal physical hardware cost; they define the statistical observation budget used by this educational comparison.

The current result files contain 48 summary rows: 3 detectors across 4 eta values and 4 epsilon values. They contain 9,600 trial-level rows: 3 detectors, 16 conditions, 2 hypotheses, and 100 trials per hypothesis.

## 11. Statistical Sanity Checks

Fixed-seed controlled checks used 20 trials of 512 observations per trial. The derived target-present expectation was compared with observed means.

| eta | epsilon | Expected $E[C\mid H_1]$ | Quantum present mean | Quantum absent mean | Classically correlated present mean | Matched-filter present mean |
|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 0.0 | 0.00 | -0.0055 | 0.0023 | -0.0219 | -0.0018 |
| 0.2 | 0.0 | 0.20 | 0.1994 | -0.0088 | 0.1791 | 0.1977 |
| 0.6 | 0.0 | 0.60 | 0.6002 | -0.0217 | 0.5965 | 0.5895 |
| 0.6 | 0.2 | 0.36 | 0.3633 | 0.0113 | 0.3564 | 0.3385 |

The corresponding absent means for the classical detectors were approximately `0.0182` and `0.0002` in the first three conditions, and `0.0129` and `-0.0031` at `eta=0.6`, `epsilon=0.2`. These are consistent with zero within finite-sample variation.

The checks support:

- `eta=0`: target-present and target-absent means are both near zero.
- Increasing `eta`: target-present correlation generally increases.
- Increasing `epsilon`: useful target-present correlation decreases from the expected value, subject to sampling variation.
- Target absent: correlation remains near zero.

## 12. Three-Detector Fairness Audit

All three detectors use:

- The same eta grid.
- The same epsilon grid.
- The same observation budget.
- Separate target-present and target-absent trial populations.
- The same threshold convention for Pd and Pfa.
- The same ROC and AUC functions.

No detector receives an intentional parameter adjustment.

A structural limitation is that `classically_correlated` and `classical_matched_filter` have the same probability law in this simplified uniform binary model. In the classically correlated implementation, the probe is generated first and the reference is made equal with probability eta. In the existing classical implementation, the reference is generated first and the return is made equal with probability eta. With uniform binary variables and symmetric agreement noise, these are label-swapped formulations with the same expected statistic $\eta(1-2\epsilon)$ and the same absent distribution. They remain separate baselines for implementation comparison, but they should not be interpreted as fundamentally different information models here.

Another implementation limitation is that the active optimized quantum experiment uses the Kraus channel in `src/quantum.py`; the explicit sampled function in `src/channel.py` is retained for direct channel tests and documentation. The two paths encode the same intended eta/epsilon binary model, but duplicated representations should be kept synchronized in future changes.

## 13. Verification and Test Results

The existing test suite completed successfully:

```text
18 passed
```

The default experiment completed successfully in approximately `15.686` seconds. No production changes were made during this verification task.

## 14. Limitations

This model is educational and discrete-variable only. It does not model:

- Optical modes or photon numbers.
- Thermal background fields.
- Physical propagation loss or calibrated reflectivity.
- A complete quantum-illumination receiver.
- Hardware imperfections beyond the defined binary channel.
- Equal physical energy, time, or hardware-cost budgets.

The three-detector results therefore describe this defined simulation, not real radar performance or a universal quantum advantage claim.

## Final Assessment

**PASS WITH LIMITATIONS.** The implementation matches its documented simplified probability model, the statistics and metrics are mathematically consistent, the absent-background expectation is zero, and the observation budgets are matched. The limitations above should remain explicit when interpreting the generated CSV files and plots.
