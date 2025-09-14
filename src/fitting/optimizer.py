# trying L-BFGS-B first, not sure if the cost surface is smooth enough

import numpy as np
from scipy.optimize import minimize
from ..model.parameters import Params
from ..simulation.hemodynamics import run_production


def cost_function(x, target_obs, fixed):
    p = Params(**fixed, alpha_lv=x[0], E_es_lv=x[1], R_sys=x[2])
    r = run_production(p)
    if r is None:
        return 1e6
    cost = 0.0
    for obs in ["EF", "EA", "SBP"]:
        sim = r[obs]
        tgt = target_obs[obs]
        if sim is None or tgt is None:
            cost += 100
        elif tgt != 0:
            cost += ((sim - tgt) / tgt) ** 2
    return cost


def fit_twin(target_obs, fixed, verbose=True):
    bounds = [(5.0, 35.0), (1.5, 4.0), (0.7, 1.5)]
    x0 = [10.0, 2.7, 1.05]
    result = minimize(cost_function, x0, args=(target_obs, fixed),
                      method="L-BFGS-B", bounds=bounds)
    if verbose:
        print(f"  {result.nfev} evals, cost={result.fun:.6f}")
        print(f"  alpha={result.x[0]:.2f}, E_es={result.x[1]:.3f}, "
              f"R_sys={result.x[2]:.3f}")
    return {
        "alpha_lv": result.x[0],
        "E_es_lv": result.x[1],
        "R_sys": result.x[2],
        "cost": result.fun,
        "nfev": result.nfev,
    }
