# Final Demonstration Guide

## STEP 1: Open the project folder

Open the `quantum-target-detection` folder in VS Code.

## STEP 2: Activate the virtual environment

Open a PowerShell terminal in VS Code and run:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution for the current terminal, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

## STEP 3: Run

```text
python experiments/final_demo.py
```

The terminal prints the difficult condition, highest observed condition, overall AUC ranges, and the scientific interpretation.

## STEP 4: Open the results folder

In VS Code, open the `results` folder after the script completes.

## STEP 5: Show `presentation_weak_target.png`

Explain:

> This graph shows how increasing noise affects the three detectors under a weak target condition.

The target-correlation parameter is fixed at `eta=0.10`, while `epsilon` increases along the x-axis.

## STEP 6: Show `presentation_target_strength.png`

Explain:

> This graph shows how increasing target correlation changes detection performance under high noise.

The binary noise parameter is fixed at `epsilon=0.20`, while `eta` increases along the x-axis.

## STEP 7: Show `presentation_roc.png`

Explain:

> This ROC comparison shows detection performance under the most difficult common condition.

This figure uses `eta=0.10` and `epsilon=0.20` and includes all three detectors plus the chance line.

## STEP 8: Open `final_demo_comparison.csv`

Explain that the complete numerical results are available and were generated from the frozen experiment outputs.

## What I should tell my professor

### Problem

The project studies whether a weak target can be detected when the return is noisy, and whether correlation with a retained reference helps.

### Quantum approach

The quantum detector prepares a Bell pair using an H gate and a CNOT gate. One qubit is treated as the probe and the other as the retained reference. The simulation measures whether the two results agree.

### Three detector models

I compared the entangled Bell-pair detector with a classically correlated binary detector and a classical matched-filter detector. The classically correlated detector is important because it tests whether similar behavior can arise from classical correlation without entanglement.

### Fair comparison

All three detectors use the same eta and epsilon parameter grid, the same observation budget, separate target-present and target-absent trials, and the same Pd, Pfa, ROC, and AUC evaluation procedure.

### Experiments

The experiment sweeps the target-correlation parameter eta from `0.10` to `0.60` and the binary noise parameter epsilon from `0.00` to `0.20`. The results are reproducible using fixed random seeds.

### Results

The most difficult common condition is `eta=0.10, epsilon=0.20`. The AUC values there are `0.69395` for quantum, `0.73830` for classically correlated, and `0.77870` for the matched filter. At `eta=0.40, epsilon=0.00`, all three detectors reach AUC `1.00000`.

I did not assume quantum advantage. I experimentally compared the three detectors under controlled conditions.

### Conclusion

The results show condition-dependent detection behavior, not a universal ranking. Increasing target correlation generally improves detection, while binary noise generally makes detection more difficult. This is a simplified educational two-qubit simulation, not a complete physical optical quantum-illumination experiment.
