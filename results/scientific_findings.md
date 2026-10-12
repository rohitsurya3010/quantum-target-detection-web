# Scientific Findings

## 1. Overall observation

This frozen simulation compares three detectors under the same eta/epsilon grid and observation budget. Across the 48 detector-condition rows, performance generally improves as eta increases because target-present and target-absent statistics become more separated. Increasing epsilon generally reduces useful correlation, especially in the weak-target regime, although finite-sample variation produces occasional small non-monotonic changes.

    AUC ranges are:

                detector  min_auc  max_auc  mean_auc  std_auc
    classical_correlated  0.73830  1.00000   0.94603  0.08098
classical_matched_filter  0.77870  1.00000   0.94933  0.07368
                 quantum  0.69395  1.00000   0.94822  0.08559

## 2. Weak-target regime

At eta=0.10, the AUC values at the difficult noise level epsilon=0.20 are: classical_correlated AUC=0.73830; classical_matched_filter AUC=0.77870; quantum AUC=0.69395. This is the weakest-target/high-noise corner of the grid and shows that all detectors retain some discrimination, but none should be interpreted as universally superior.

## 3. High-noise regime

At epsilon=0.20, the eta=0.10 condition is the most difficult common condition by mean AUC. As eta increases from 0.10 to 0.60, all three detectors approach perfect separation in the simulated data despite the binary flip noise.

At eta=0.10 and epsilon=0.20: eta=0.10: classical_correlated AUC=0.73830; eta=0.10: classical_matched_filter AUC=0.77870; eta=0.10: quantum AUC=0.69395.

## 4. Quantum detector behavior

The quantum detector's highest observed AUC is identified below. It performs strongly once eta is at least moderate, while its lowest observed AUC occurs at the weak-target/high-noise corner. Its results are comparable to the classical detectors in some conditions and lower in others. These data do not support a universal quantum advantage claim.

Highest observed quantum condition: eta=0.40, epsilon=0.00 with AUC=1.00000.

## 5. Classical correlated detector

The classically correlated detector follows the same qualitative trend: higher eta increases separation, and epsilon generally reduces it. Its classically generated correlation provides a useful baseline for distinguishing effects attributable to correlation from effects attributable specifically to entanglement. Under the current uniform binary assumptions, it has the same probability law as the existing matched-filter baseline despite being implemented separately.

## 6. Classical matched filter

The classical matched filter also achieves high AUC at moderate and high eta. Its lowest observed condition is reported below. It is a binary baseline in this implementation, not a continuous-amplitude physical matched filter.

## 7. Most difficult simulated condition

The lowest mean AUC across all three detectors occurs at eta=0.10, epsilon=0.20 with mean AUC=0.73698. At this condition, the correlation separations are: classical_correlated separation=0.05437; classical_matched_filter separation=0.06422; quantum separation=0.05000.

## 8. Highest observed performance

Per-detector highest observed conditions are:

- `classical_correlated`: eta=0.40, epsilon=0.00 with AUC=1.00000.
- `classical_matched_filter`: eta=0.40, epsilon=0.00 with AUC=1.00000.
- `quantum`: eta=0.40, epsilon=0.00 with AUC=1.00000.

Per-detector lowest observed conditions are:

- `classical_correlated`: eta=0.10, epsilon=0.20 with AUC=0.73830.
- `classical_matched_filter`: eta=0.10, epsilon=0.20 with AUC=0.77870.
- `quantum`: eta=0.10, epsilon=0.20 with AUC=0.69395.

AUC = 1.0 indicates perfect separation in that simulated condition, not universal quantum advantage.

## 9. Literature comparison

Our AUC and correlation-separation values are simulation results computed from the current project's trial data. The Ahmed 2026 values are explicitly labeled published reported values from an SSRN preprint, not peer-reviewed journal results. Yung et al. provides a theoretical discrete-signal quantum-illumination/channel-discrimination reference. The numerical values are not directly equivalent because channel definitions, noise representations, measurement rules, physical parameters, and metrics differ.

The literature sources represented in the comparison layer are: Ahmed 2026 preprint, Yung et al. 2020, our_simulation. The published benchmark is intentionally kept separate from our simulation plots.

## 10. Main scientific interpretation

This simulation demonstrates how a shared binary target-correlation parameter and binary noise probability affect empirical detection discrimination for an entangled detector and two classical baselines. It demonstrates condition-dependent statistical behavior under a defined educational model. It does not determine which technology is universally better, establish physical radar performance, or prove experimental quantum advantage.
