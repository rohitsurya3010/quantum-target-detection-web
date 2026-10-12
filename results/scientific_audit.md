# Final Scientific Audit of the Literature-Comparison Layer

Date: 2026-09-23

## Overall Status

**PASS WITH LIMITATIONS**

The literature-comparison layer is scientifically defensible as a clearly separated contextual comparison for this simplified educational model. It does not claim that the current simulation reproduces either cited reference, and it does not treat AUC as equivalent to correlation separation.

No detector algorithm, scientific parameter, random seed, observation budget, AUC/Pd/Pfa implementation, or simulation model was modified during this audit.

## Audit Results

### 1. All 48 `our_simulation` rows come from current trial data: PASS

`results/literature_comparison.csv` contains 48 rows with `source=our_simulation`: 3 detectors across 4 eta values and 4 epsilon values.

The audit independently recomputed, from `results/trial_statistics.csv`:

$$
\Delta C = \operatorname{mean}(C \mid \text{target present}) -
\operatorname{mean}(C \mid \text{target absent}).
$$

All 48 CSV values matched the independent recomputation within numerical tolerance below $10^{-12}$. The source notes also identify them as computed from current `trial_statistics.csv` rather than published values.

### 2. Correlation-separation formula: PASS

`src/literature.py:correlation_separation` groups by detector, eta, epsilon, and `target_present`, computes the mean statistic for each hypothesis, and subtracts absent from present:

```text
mean_statistic_present - mean_statistic_absent
```

This exactly implements the required definition.

### 3. Same separation definition for all three detectors: PASS

The same grouping and subtraction code is applied without detector-specific formulas to:

- `quantum`
- `classical_correlated`
- `classical_matched_filter`

No detector receives a special separation calculation.

### 4. Ahmed values are published/reference values, not simulation values: PASS

The four Ahmed rows use:

```text
source = Ahmed 2026 preprint
notes  = Published reported value; ...
```

They are stored as constants in `src/literature.py`, not generated from trial data. Their values are exactly:

- Quantum, zero background noise: `0.0100`
- Quantum, high background noise: `0.0025`
- Classically correlated, zero background noise: `0.1000`
- Classically correlated, high background noise: `0.0500`

### 5. No invented Ahmed intermediate values: PASS

Only the four supplied endpoint/condition rows exist. No interpolated or inferred Ahmed values were found.

### 6. Yung et al. rows contain no fabricated numerical values: PASS

The two Yung rows are labeled `Yung et al. 2020`, use metric `minimum_detection_error`, and have blank numeric `value` fields. Their notes identify them as theoretical results with no numerical value copied into the table.

### 7. AUC is not treated as correlation separation: PASS

AUC remains in `results/summary.csv` and is computed by the existing ROC/AUC implementation. Correlation separation is a distinct metric in `literature_comparison.csv` with metric name `correlation_separation`.

No conversion, ranking substitution, or numerical equivalence between AUC and correlation separation is performed.

### 8. Simulation and published conditions are separated: PASS

Our rows use `source=our_simulation` and conditions such as:

```text
eta=0.4, epsilon=0.1
```

Ahmed rows use textual paper conditions such as `zero background noise` and `high background noise`. Yung rows use `one-shot discrete-signal channel discrimination`.

The plots are separate:

- `correlation_separation_ours.png` contains only our simulation.
- `published_correlation_benchmark.png` contains only the explicitly reported Ahmed values.

### 9. README simplified-model statement: PASS

The README explicitly describes the platform as a simplified two-qubit educational model and states that it is not a complete physical optical quantum-illumination receiver.

### 10. README prohibited-claim audit: PASS

The README does not claim:

- Universal quantum advantage.
- Quantum superiority.
- Exact reproduction of either paper.
- Physical equivalence of `eta` to optical reflectivity.
- Physical equivalence of `epsilon` to thermal optical noise.

It explicitly warns that these equivalences do not hold automatically.

### 11. CSV integrity: PASS

Checks performed:

- No missing values in the simulation rows or required comparison fields.
- No duplicate rows in `summary.csv`, `trial_statistics.csv`, or simulation comparison rows.
- Detector names are restricted to `quantum`, `classical_correlated`, and `classical_matched_filter` for current simulation data.
- Source labels are `our_simulation`, `Ahmed 2026 preprint`, and `Yung et al. 2020` as intended.
- Metric names are `correlation_separation` for separation rows and `minimum_detection_error` for qualitative Yung theory rows.
- All current AUC values remain within `[0, 1]`.

The current generated files contain:

- `summary.csv`: 48 rows.
- `trial_statistics.csv`: 9,600 rows.
- `literature_comparison.csv`: 54 rows: 48 simulation, 4 Ahmed reference, and 2 Yung theoretical rows.
- `model_comparison.csv`: 3 detector rows.

### 12. Plot integrity: PASS

The generated plots were audited through their actual Matplotlib axes and legend labels.

`correlation_separation_ours.png`:

- x-axis: `Eta: toy target-correlation probability`
- y-axis: `Correlation separation`
- title: `Our simulation: correlation separation`
- legends include Quantum, Classically correlated, and Classical matched filter for each epsilon value.

`published_correlation_benchmark.png`:

- x-axis: `Ahmed 2026 preprint condition`
- y-axis: `Reported correlation separation`
- title: `Ahmed 2026 preprint - published reported values`
- legends include Quantum and Classically correlated.

Correlation separation is dimensionless; no misleading physical unit is displayed. The published plot contains only the four explicit Ahmed values and does not overlay incomparable simulation values.

A first local legend assertion assumed a particular Matplotlib ordering and failed because the published legend order was `Classically correlated`, then `Quantum`. An order-independent verification confirmed both required entries; this was a check-script assumption, not a plotting defect.

### 13. Reproducibility: PASS

The default experiment was run twice with the fixed project seed. SHA-256 hashes of the numerical CSV outputs matched.

The literature-generation command was also run twice against the same trial data. SHA-256 hashes of the numerical CSV outputs matched.

Commands verified:

```text
python experiments/main.py
python experiments/literature_comparison.py
```

### 14. Required test run: PASS

```text
22 passed
0 failed
```

## Discrepancies Found

No genuine scientific or implementation bug was found.

The only observed issue was an initial audit script that expected a specific legend order. Matplotlib produced the same correct legend entries in a different order. The plot implementation was not changed.

## Scientific Defensibility

The literature comparison is scientifically defensible when interpreted as contextual comparison rather than direct benchmarking. The current simulation and cited works differ in channel definitions, noise models, measurement/decision rules, parameter meanings, and metrics.

Yung et al. (2020) is a peer-reviewed theoretical discrete-signal quantum-channel discrimination reference. Its minimum-error formulation is not the current platform's normalized correlation plus empirical ROC/AUC procedure.

Ahmed (2026) is explicitly labeled an SSRN preprint, not a peer-reviewed journal result. Its four supplied correlation-separation values are retained as published reported values only. They are not converted to AUC, not used to generate intermediate points, and not directly overlaid with our simulation.

## Incomparable Numbers

The following comparisons are not numerically interchangeable without explicitly matched conditions and definitions:

- Our AUC versus published correlation separation.
- Our toy `eta` versus optical reflectivity.
- Our binary `epsilon` versus thermal optical background.
- Our empirical Pd/Pfa versus Yung et al.'s minimum-error channel-discrimination formulation.
- Our normalized agreement statistic versus any paper-specific correlation normalization unless proven identical.

The separate tables and plots correctly preserve these distinctions.

## Final Results Readiness

The project is ready for final results/discussion writing provided that the discussion:

1. Calls the platform a simplified educational model.
2. Keeps simulation and published values in separate comparisons.
3. Labels Ahmed as an SSRN preprint.
4. Does not claim quantum advantage from AUC or correlation-separation values.
5. Explains that the current conditions and metrics are not physically equivalent to the cited papers.

## Final Execution Summary

- Tests passed: `22`
- Tests failed: `0`
- Final default experiment runtime: approximately `15.801 seconds`
- Audit status: **PASS WITH LIMITATIONS**
- Files changed during this audit: `results/scientific_audit.md` only
- Scientific model modified: **No**
