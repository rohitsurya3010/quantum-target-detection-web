# Final Model Comparison

| Feature | Quantum | Classical Correlated | Classical Matched Filter |
|---|---|---|---|
| Entanglement | Yes | No | No |
| Classical correlation | Not the defining resource | Yes | No |
| Probe/reference | Yes | Yes | Reference signal |
| Target/noise experiment | Yes | Yes | Yes |
| Same observation budget | Yes | Yes | Yes |
| ROC/AUC | Yes | Yes | Yes |
| Pd/Pfa | Yes | Yes | Yes |

## Row explanations

- **Entanglement:** The quantum detector prepares a Bell pair. The two classical detectors use ordinary binary variables and do not use entanglement.
- **Classical correlation:** The classically correlated detector explicitly creates a correlated binary probe/reference pair. The quantum detector's defining resource is the entangled state, while the matched filter uses a reference signal rather than this explicit correlated-pair construction.
- **Probe/reference:** The quantum detector has a quantum probe and retained reference qubit. The classically correlated detector has classical probe `A` and reference `B`. The matched filter has a classical reference signal and return.
- **Target/noise experiment:** Each detector is evaluated with the same target-present and target-absent hypotheses over the frozen eta/epsilon conditions.
- **Same observation budget:** Each detector uses the same number of observations per trial in the frozen experiment.
- **ROC/AUC:** Each detector produces trial statistics that are evaluated with the same ROC and AUC implementation.
- **Pd/Pfa:** Each detector uses the same threshold-based probability of detection and probability of false alarm definitions.

This table describes the project's simplified educational comparison. It does not imply equal physical hardware cost or a universal quantum advantage.
