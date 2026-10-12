# Executive Summary

This project studies whether correlations between a transmitted probe and a retained reference can help detect a weak target hidden in noise. It uses a simplified two-qubit, discrete-variable educational simulation rather than a full physical optical radar or quantum-illumination system.

Three detectors were compared under the same target-correlation parameter, binary noise parameter, observation budget, and evaluation procedure: an entangled Bell-pair detector, a classically correlated binary detector, and a classical matched-filter detector. Experiments swept `eta`, which controls target-present correlation in this model, and `epsilon`, which controls binary flip noise. Performance was evaluated using ROC curves, AUC, probability of detection, and probability of false alarm.

The main finding is that performance depends strongly on the simulated condition. At the weak-target/high-noise condition `eta=0.10, epsilon=0.20`, AUC was `0.69395` for quantum, `0.73830` for classically correlated, and `0.77870` for the matched filter. At `eta=0.40, epsilon=0.00`, all three reached AUC `1.00000`, meaning perfect separation in that particular simulation condition.

The results do not demonstrate universal quantum advantage. Their contribution is methodological: they provide a reproducible comparison with classical controls and make the effects of target correlation and noise visible. Future work should use physically motivated optical channels, thermal backgrounds, photon-number models, and hardware experiments.
