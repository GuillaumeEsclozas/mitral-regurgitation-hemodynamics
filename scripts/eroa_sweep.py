"""Quick sweep over EROA values to see what happens."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.model.parameters import Params
from src.simulation.hemodynamics import run_production


EROA_VALUES = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]


def main():
    print(f"{'EROA':>6s}  {'EF':>6s}  {'CO':>6s}  {'LAP':>6s}  {'LVEDP':>6s}")
    print("-" * 40)
    for eroa in EROA_VALUES:
        p = Params(EROA=eroa)
        r = run_production(p)
        if r is None:
            print(f"{eroa:6.2f}  FAILED")
            continue
        print(f"{eroa:6.2f}  {r['EF']:6.1f}  {r['CO']:6.2f}  "
              f"{r['mean_LAP']:6.1f}  {r['LVEDP']:6.1f}")

    # import matplotlib.pyplot as plt
    # fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    # ... maybe later


if __name__ == "__main__":
    main()
