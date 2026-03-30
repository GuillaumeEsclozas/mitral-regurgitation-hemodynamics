# Mitral Regurgitation Hemodynamics

[![CI](https://github.com/YOUR_USERNAME/mitral-regurgitation-hemodynamics/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/mitral-regurgitation-hemodynamics/actions/workflows/ci.yml)

Closed-loop 0D cardiovascular model connecting EROA measurements to patient-specific filling pressure predictions. Estimates LVEDP and PCWP from noninvasive echo inputs with ±2.5 mmHg accuracy under realistic measurement noise, compared to ±6 mmHg for E/e' ratio.

![Overview](figures/readme_hero_figure.png)

## Approach

8-compartment lumped-parameter ODE system (4 chambers, 4 vascular beds) with time-varying elastance and power-law EDPVR. Valves use sigmoid gating, MR is an orifice flow scaled by EROA. Solved beat-by-beat with scipy RK45 until steady state. A digital twin layer fits three hidden parameters (LV stiffness, contractility, vascular resistance) to three noninvasive observables (EF, E/A ratio, SBP) using differential evolution, then predicts invasive hemodynamics that normally require catheterization.

All parameters use a frozen dataclass. Single ODE right-hand side used everywhere via `args=`. 73 tests passing.

![Circuit](figures/readme_circuit_diagram.png)

## Results

### Healthy baseline

All 13 hemodynamic targets within range. Volume conservation exact (5000.000000 mL). Left-right balance within 0.02 mL.

### EF paradox

| EROA (cm²) | Total EF | Forward EF | CO (L/min) | Mean LAP |
|:---:|:---:|:---:|:---:|:---:|
| 0.00 | 57.5% | 57.5% | 5.40 | 7.4 |
| 0.20 | 67.7% | 46.4% | 4.84 | 11.0 |
| 0.40 | 75.4% | 39.3% | 4.38 | 14.1 |

Total EF rises with MR severity. Forward EF drops. A 75% EF looks hyperdynamic but forward output is critically compromised.

### Disproportionate MR

| | Patient A (EROA=0.4, normal LV) | Patient B (EROA=0.25, stiff LV) |
|:---|:---:|:---:|
| Forward EF | 39.3% | 43.4% |
| LVEDP | 17.8 mmHg | **21.5 mmHg** |
| Mean LAP | 14.1 mmHg | **16.1 mmHg** |
| PCWP | 14.1 mmHg | **16.1 mmHg** |

Lower EROA, higher filling pressures. Diastolic dysfunction amplifies moderate MR.

### Digital twin accuracy under noise

EF ±3%, E/A ±15% relative, SBP ±5 mmHg. 80 fits, 100% convergence.

| Index | Worst-case error | Clinical alternative |
|:---|:---:|:---:|
| LVEDP | ±3.0 mmHg | Catheter only |
| LAP / PCWP | ±2.5 mmHg | E/e': ±6 mmHg |
| CO | ±0.57 L/min | Thermodilution |
| PAP | ±1.8 mmHg | Catheter only |

Identifiability confirmed (Jacobian condition number 5 to 7). Robust to ±40% EROA measurement error (LAP shift: ±0.4 mmHg). Robust to 20% model mismatch in fixed parameters (LAP shift: 0.04 mmHg).

![Heatmap](figures/readme_heatmap.png)

### Diastolic dysfunction grading

The model reproduces Grades I through III from two parameters (stiffness alpha and relaxation tau). E/A drops below 1 with impaired relaxation, normalizes pseudonormally at moderate stiffness, then rises above 2 in restrictive filling.

![DD Spectrum](figures/readme_dd_spectrum.png)

## Installation
```bash
git clone https://github.com/YOUR_USERNAME/mitral-regurgitation-hemodynamics.git
cd mitral-regurgitation-hemodynamics
pip install -e ".[dev]"
```

Requires Python 3.10+, numpy, scipy, matplotlib.

## Usage
```python
from src.model.parameters import Params
from src.simulation.hemodynamics import run_production

# Healthy baseline
r = run_production(Params())
print(f"EF = {r['EF']:.1f}%, CO = {r['CO']:.2f} L/min")

# Digital twin: fit from echo, predict catheter values
from src.fitting.optimizer import fit_digital_twin

fit = fit_digital_twin({"EF": 68.9, "EA": 2.57, "SBP": 94}, fixed={"EROA": 0.25})
print(f"Predicted PCWP = {fit['predictions']['PCWP']:.1f} mmHg")
```

## What worked (and what didn't)

**Helped:** Power-law EDPVR (exponential blows up at MR volumes, 162,000 mmHg at V=180), simple sigmoid valve (composite model was broken without inertance), RK45 over Radau (2.5x faster after sigmoid smoothing removed stiffness), per-chamber V_ref for atria, activation-based E/A extraction for fused waves.

**Didn't help:** Jacobian sparsity (overhead exceeds savings at 8x8), Hessian-based confidence intervals (cost surface flat at machine precision due to inverse crime), exponential EDPVR (tested 5 approaches, all failed except power law).

## Limitations

Synthetic validation only. The digital twin fits its own forward model, so perfect noiseless recovery is expected. The noise test is more honest but still not clinical validation against catheterization data. Fixed HR, no baroreflex, 0D only, 3 free parameters out of ~30. Chronic MR (steady state). This is a portfolio project, not a clinical tool.

## References

Holmes & Lumens (2018). Clinical applications of patient-specific models: the case for a simple approach. J Cardiovasc Transl Res 11:71-79.

Niederer, Lumens & Trayanova (2019). Computational models in cardiology. Nat Rev Cardiol 16:100-111.

Grayburn et al. (2019). Proportionate and disproportionate functional MR. JACC Cardiovasc Imaging.

Van Osta et al. (2020). Parameter subset reduction for patient-specific modelling. Phil Trans R Soc A 378:20190347.

Klotz et al. (2006). Single-beat estimation of end-diastolic pressure-volume relationship. Am J Physiol Heart Circ Physiol.

Korakianitis & Shi (2006). A concentrated parameter model for the human cardiovascular system. J Biomech 39(11):1964-82.

## License

MIT
