# Discussion

## 1. Effect of Target Correlation

The model's `eta` parameter controls the probability that a target-present observation retains correlation between the probe and reference. It is a target-correlation parameter for this discrete simulation, not a physical optical reflectivity.

Increasing `eta` generally improves detection for all three detectors because it increases the expected separation between target-present and target-absent statistics. At zero noise, the quantum AUC increased from `0.87700` at `eta=0.10` to `1.00000` at `eta=0.60`. The classically correlated detector increased from `0.88050` to `1.00000`, and the classical matched filter increased from `0.90590` to `1.00000`. This trend reflects the defined probability model rather than a statement about optical target behavior.

## 2. Effect of Noise

The `epsilon` parameter represents the probability of an independent binary flip. Increasing it generally reduces useful agreement correlation and makes target-present statistics less distinguishable from target-absent background.

The difficult common condition is `eta=0.10, epsilon=0.20`: the target-correlation probability is weak while the binary flip probability is relatively high. The resulting AUC values are `0.69395` for quantum, `0.73830` for classically correlated, and `0.77870` for the matched filter. At higher `eta`, the stronger target correlation provides enough separation that AUC approaches or reaches `1.00000` even with `epsilon=0.20`.

## 3. Quantum Detector Performance

The quantum detector has an AUC range of `0.69395` to `1.00000`. Its highest observed condition is `eta=0.40, epsilon=0.00`, where all three detectors reach `1.00000`. Its lowest observed condition is the weak-target/high-noise condition described above.

The quantum detector does not consistently outperform the classical detectors. At `eta=0.10, epsilon=0.20`, its AUC of `0.69395` is below the classically correlated value of `0.73830` and the matched-filter value of `0.77870`. At other weak-target conditions, it is comparable to or higher than one or both classical baselines. These are condition-specific simulation results, not evidence of universal quantum advantage.

## 4. Classical Correlation

The classically correlated detector uses classical binary probe and reference variables with the same model parameter `eta` and binary noise parameter `epsilon`. Its AUC ranges from `0.73830` to `1.00000`.

Including this detector is scientifically important because it tests whether the observed detection behavior can be reproduced using classical correlation without entanglement. Under the current uniform binary assumptions, it has the same probability law as the existing matched-filter baseline, although it is implemented as a separate classical probe/reference model. Its results show that strong detection in this simplified setting is not by itself evidence that entanglement is responsible.

## 5. Classical Matched Filter

The classical matched filter has an AUC range of `0.77870` to `1.00000`. It provides a classical detection baseline using binary reference/return agreement under the same observation budget and parameter grid. It produces the highest AUC at the difficult common condition, `0.77870`, while all detectors become nearly indistinguishable at moderate or high `eta`.

This implementation is a simplified binary baseline rather than a continuous-amplitude physical matched filter. Its performance should therefore be interpreted within the project's defined model.

## 6. Interpretation of AUC = 1

AUC = `1.0` means perfect separation between the sampled target-present and target-absent statistics in that particular simulated condition. It does not prove:

- universal quantum advantage;
- physical quantum advantage;
- superiority in real radar; or
- superiority under all noise conditions.

The shared `eta=0.40, epsilon=0.00` condition reaching AUC `1.00000` for all three detectors is a useful illustration of condition-specific perfect separation, not a technology ranking.

## 7. Comparison With Prior Work

Yung et al. (2020) is peer-reviewed theoretical work in *npj Quantum Information* on one-shot discrete-signal quantum illumination formulated as a quantum-channel discrimination problem. Its minimum-error framework, finite-dimensional environmental states, and optimized decision measurements differ from this project's binary channel, agreement statistic, and empirical ROC/AUC analysis.

Ahmed (2026) is an SSRN preprint, not a peer-reviewed journal result. It is relevant because it compares entangled and classically correlated discrete-qubit probes using a correlation measurement. However, its parameter definitions, noise conditions, measurement details, and reported metric are not established as identical to this platform. This project does not reproduce either paper exactly.

## 8. Why the Result Is Still Useful

The absence of universal quantum advantage is scientifically useful because it prevents an entanglement-based interpretation from being assumed without controlled comparison. The platform provides a reproducible benchmark with fixed seeds, equal observation budgets, three detector baselines, parameter sweeps, and common ROC/AUC/Pd/Pfa evaluation. It also demonstrates the educational value of translating a quantum-correlation idea into a directly comparable classical experiment.

The resulting framework can support future work by making it clear which performance changes arise from target correlation, binary noise, finite sampling, or detector structure. It also provides a transparent starting point for more physically motivated models.

## 9. Limitations

The model has important limitations:

- It is a simplified two-qubit model.
- It uses a binary target and binary noise model.
- `eta` is not physical optical reflectivity.
- `epsilon` is not a full optical thermal-noise model.
- It contains no photon-number model.
- It contains no continuous-variable optical field.
- It contains no physical transmitter or receiver.
- Its measurement model is simplified computational-basis agreement.
- It is a simulation rather than a hardware experiment.

Equal observation counts do not imply equal physical resource cost, and the reported results should not be extrapolated to real radar systems.

## 10. Future Work

Meaningful extensions, not implemented here, include:

1. Continuous-variable quantum illumination.
2. A bosonic-loss channel.
3. A thermal background model.
4. Photon-number statistics.
5. Physically motivated reflectivity.
6. An optimal quantum receiver or POVM.
7. Helstrom and Chernoff error bounds.
8. IBM/Qiskit hardware experiments.
9. Hardware noise characterization.
10. Larger Monte Carlo trial counts.
