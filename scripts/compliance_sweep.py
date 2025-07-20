"""Sweep EROA x stiffness to find disproportionate MR."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.model.parameters import Params
from src.simulation.hemodynamics import run_production


EROA_VALUES = [0, 0.1, 0.2, 0.3, 0.4]
ALPHA_VALUES = [10, 20, 30]


def main():
    for alpha in ALPHA_VALUES:
        print(f"\nalpha_lv = {alpha}")
        print(f"{'EROA':>6s}  {'EF':>6s}  {'EF_fwd':>6s}  {'CO':>6s}  "
              f"{'LAP':>6s}  {'LVEDP':>6s}")
        print("-" * 50)
        for eroa in EROA_VALUES:
            p = Params(EROA=eroa, alpha_lv=alpha)
            r = run_production(p)
            if r is None:
                print(f"{eroa:6.2f}  FAILED")
                continue
            print(f"{eroa:6.2f}  {r['EF']:6.1f}  {r['EF_fwd']:6.1f}  "
                  f"{r['CO']:6.2f}  {r['mean_LAP']:6.1f}  {r['LVEDP']:6.1f}")


if __name__ == "__main__":
    main()
