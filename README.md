# Mitral Regurgitation Hemodynamics

Closed-loop cardiovascular model (0D, 8 compartments) that simulates 
mitral regurgitation hemodynamics beat by beat. Includes a digital twin 
layer that fits patient-specific parameters from noninvasive echo data.

## Quick start

```bash
git clone https://github.com/GuillaumeEsclozas/mitral-regurgitation-hemodynamics.git
cd mitral-regurgitation-hemodynamics
pip install -e ".[dev]"
```

## Usage

```python
from src.model.parameters import Params
from src.simulation.hemodynamics import run_production

r = run_production(Params())
print(f"EF = {r['EF']:.1f}%, CO = {r['CO']:.2f} L/min")
```

Requires Python 3.10+.
