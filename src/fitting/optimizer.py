# L-BFGS-B kept converging to local minima, DE is slower but actually works

import numpy as np
from scipy.optimize import differential_evolution
import time
from ..model.parameters import Params
from ..simulation.hemodynamics import run_turbo


# EA carries more info about stiffness than EF or SBP
OBS_WEIGHTS = {"EF": 1.0, "EA": 2.0, "SBP": 1.0}


def cost_function(x, target_obs, fixed):
    """Weighted sum of squared relative errors."""
    p = Params(**fixed, alpha_lv=x[0], E_es_lv=x[1], R_sys=x[2])
    r = run_turbo(p)
    if r is None:
        return 1e6
    cost = 0.0
    for obs, w in OBS_WEIGHTS.items():
        sim = r[obs]
        tgt = target_obs[obs]
        if sim is None or tgt is None:
            cost += 100
        elif tgt != 0:
            cost += w * ((sim - tgt) / tgt) ** 2
    return cost


def fit_digital_twin(target_obs, fixed, seed=42, verbose=True):
    """Fit 3 parameters from noninvasive observables."""
    bounds = [(5.0, 35.0), (1.5, 4.0), (0.7, 1.5)]
    start = time.perf_counter()
    result = differential_evolution(
        cost_function, bounds, args=(target_obs, fixed),
        strategy="best1bin", maxiter=25, popsize=5,
        tol=1e-4, mutation=(0.5, 1.0), recombination=0.7,
        seed=seed, polish=True, init="sobol",
    )
    elapsed = time.perf_counter() - start
    a, e, r_sys = result.x
    if verbose:
        print(f"  {result.nfev} evals, {elapsed:.0f}s, "
              f"cost={result.fun:.6f}")
        print(f"  alpha={a:.2f}, E_es={e:.3f}, R_sys={r_sys:.3f}")
    return {
        "alpha_lv": a, "E_es_lv": e, "R_sys": r_sys,
        "cost": result.fun, "nfev": result.nfev,
        "time": elapsed,
    }


# NOTE: tried computing confidence intervals via inverse Hessian at the
# optimum. Doesn't work because the cost surface is essentially flat at
# ~1e-6 near the minimum (inverse crime). The noise robustness test is
# more honest anyway. See commit message.
