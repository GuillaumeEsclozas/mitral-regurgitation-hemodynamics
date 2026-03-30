# Mitral Regurgitation Hemodynamics

0D closed-loop cardiovascular model for studying how mitral regurgitation interacts with ventricular and atrial compliance at the system level.

## What this does

- 8-compartment lumped-parameter ODE model (4 chambers, 4 vascular beds)
- EROA x compliance sweep: 30 simulations across 10 EROA values and 3 stiffness profiles
- Digital twin layer: estimates 3 patient-specific parameters (LV stiffness, contractility, afterload) from noninvasive observables (EF, E/A ratio, SBP)
- Predicts invasive hemodynamics (LVEDP, LAP/PCWP, CO, PAP) with 2-3x better accuracy than E/e'

## Quick start
```
pip install -e ".[dev]"
pytest tests/ -v
```

## Context

Built to bridge experimental EROA measurements (PISA method, Physics for Medicine Paris) with computational cardiovascular modeling (CircAdapt paradigm, Maastricht/CARIM). Full README with figures and results coming soon.
