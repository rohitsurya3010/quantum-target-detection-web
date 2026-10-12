## Results

### Detection performance

The frozen experiment evaluated quantum, classically correlated, and classical matched-filter detectors over eta values 0.10, 0.20, 0.40, and 0.60 and epsilon values 0.00, 0.05, 0.10, and 0.20. The mean AUC values across the 16 conditions were 0.94822 for the quantum detector, 0.94603 for the classically correlated detector, and 0.94933 for the classical matched filter. Across all conditions, the AUC ranges were 0.69395-1.00000, 0.73830-1.00000, and 0.77870-1.00000, respectively.

### Effect of target correlation

Increasing eta generally improved separation between target-present and target-absent trials. For example, at epsilon=0.00, the quantum AUC increased from 0.87700 at eta=0.10 to 1.00000 at eta=0.60. The corresponding classically correlated and matched-filter values changed from 0.88050 to 1.00000, and from 0.90590 to 1.00000. This behavior is consistent with eta increasing target-present correlation under the defined toy model.

### Effect of noise

At eta=0.10, increasing epsilon from 0.00 to 0.20 reduced AUC for all three detectors: quantum from 0.87700 to 0.69395, classically correlated from 0.88050 to 0.73830, and matched filter from 0.90590 to 0.77870. At higher eta, the larger target-present separation keeps AUC close to one even at epsilon=0.20.

### Comparison with classical detectors

The quantum detector was not uniformly highest. At eta=0.10 and epsilon=0.20, its AUC was 0.69395, compared with 0.73830 and 0.77870. At eta=0.40 and epsilon=0.00, all three reached or effectively reached AUC=1.0. These are condition-specific results; AUC=1.0 indicates perfect separation in that simulated condition, not universal quantum advantage.

The condition-by-condition differences were generally small once eta reached 0.20 or higher, and several conditions produced identical or nearly identical AUC values. At eta=0.10, the detectors separated more visibly: the quantum detector was highest at epsilon=0.05 and epsilon=0.10, while the matched filter was highest at epsilon=0.00 and epsilon=0.20. This variation reinforces that detector ordering depends on the defined target and noise condition rather than establishing a universal ranking.

### Comparison with prior work

The current AUC and correlation-separation values are simulation outputs from this project. Ahmed 2026 provides explicitly reported correlation-separation values in an SSRN preprint, while Yung et al. provides a theoretical discrete-signal channel-discrimination benchmark. Their metrics and physical conditions are not automatically equivalent to the present toy eta/epsilon model, so no direct numerical ranking is inferred.

### Limitations

The model is a simplified two-qubit educational simulation. Eta is a toy target-correlation parameter rather than optical reflectivity, and epsilon is a binary flip probability rather than a complete thermal optical-noise model. The detectors use equal observation counts, but the physical resource models and measurement tasks are not those of a full optical quantum-illumination receiver. The results therefore demonstrate condition-dependent behavior of the defined simulation rather than a universal technology comparison.

The reported AUC values summarize empirical threshold discrimination over the generated trial statistics, whereas correlation separation summarizes the difference between two mean statistics. Neither metric is a substitute for the minimum-error channel-discrimination quantities reported in theoretical work. Likewise, the Ahmed preprint values are retained as reference-only reported quantities because their conditions and normalization are not demonstrated to match this platform. The figures and tables should therefore be read as a reproducible analysis of this frozen model, with the literature serving as context rather than as a directly matched benchmark.
