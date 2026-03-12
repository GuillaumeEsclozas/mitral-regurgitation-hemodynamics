"""Digital twin parameter estimation via differential evolution."""

import numpy as np
from scipy.optimize import differential_evolution
import time
from ..model.parameters import Params
from ..simulation.hemodynamics import run_turbo

PARAM_BOUNDS = {
    "alpha_lv": (5.0, 35.0),
    "E_es_lv": (1.5, 4.0),
    "R_sys": (0.7, 1.5),
}
OBS_WEIGHTS = {"EF": 1.0, "EA": 2.0, "SBP": 1.0}


def cost_function(x, target_obs, fixed):
    """Weighted sum of squared relative errors."""
    p = Params(**fixed, alpha_lv=x[0], E_es_lv=x[1], R_sys=x[2])
    r = run_turbo(p)
    if r is None:
        return 1e6
    cost = 0.0
    for obs, w in OBS_WEIGHTS.items():
        sim = r[obs]; tgt = target_obs[obs]
        if sim is None or tgt is None:
            cost += 100
        elif tgt != 0:
            cost += w * ((sim - tgt) / tgt) ** 2
    return cost


def fit_digital_twin(target_obs, fixed, seed=42, verbose=True):
    """Fit 3 parameters from noninvasive observables."""
    bounds = [PARAM_BOUNDS["alpha_lv"],
              PARAM_BOUNDS["E_es_lv"],
              PARAM_BOUNDS["R_sys"]]
    start = time.perf_counter()
    result = differential_evolution(
        cost_function, bounds, args=(target_obs, fixed),
        strategy="best1bin", maxiter=25, popsize=5,
        tol=1e-4, mutation=(0.5, 1.0), recombination=0.7,
        seed=seed, polish=True, init="sobol",
    )
    elapsed = time.perf_counter() - start
    a, e, r_sys = result.x
    predictions = run_turbo(Params(**fixed, alpha_lv=a,
                                    E_es_lv=e, R_sys=r_sys))
    if verbose:
        print(f"  {result.nfev} evals, {elapsed:.0f}s, "
              f"cost={result.fun:.6f}")
        print(f"  alpha={a:.2f}, E_es={e:.3f}, R_sys={r_sys:.3f}")
    return {
        "alpha_lv": a, "E_es_lv": e, "R_sys": r_sys,
        "cost": result.fun, "nfev": result.nfev,
        "time": elapsed, "predictions": predictions,
    }
