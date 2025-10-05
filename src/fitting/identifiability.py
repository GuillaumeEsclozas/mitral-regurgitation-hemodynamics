"""Jacobian-based identifiability analysis."""

import numpy as np
from ..model.parameters import Params
from ..simulation.hemodynamics import run_turbo


def compute_jacobian(base_params, delta_frac=0.02):
    """Normalized Jacobian of [EF, EA, SBP] w.r.t. [alpha, E_es, R_sys].

    Returns (J_normalized, condition_number, eigenvalues).
    """
    # condition number < ~10 means the 3 params are distinguishable from these obs
    param_names = ["alpha_lv", "E_es_lv", "R_sys"]
    obs_names = ["EF", "EA", "SBP"]
    J = np.zeros((3, 3))
    for j, pname in enumerate(param_names):
        p_val = base_params[pname]
        delta = p_val * delta_frac
        pp = dict(base_params)
        pp[pname] = p_val + delta
        pm = dict(base_params)
        pm[pname] = p_val - delta
        rp = run_turbo(Params(**pp))
        rm = run_turbo(Params(**pm))
        if rp is None or rm is None:
            continue
        for i, oname in enumerate(obs_names):
            vp = rp[oname] if rp[oname] is not None else 0
            vm = rm[oname] if rm[oname] is not None else 0
            J[i, j] = (vp - vm) / (2 * delta)

    r_base = run_turbo(Params(**base_params))
    obs_vals = [r_base["EF"],
                r_base["EA"] if r_base["EA"] else 1.0,
                r_base["SBP"]]
    par_vals = [base_params[p] for p in param_names]

    J_norm = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            if obs_vals[i] != 0:
                J_norm[i, j] = J[i, j] * par_vals[j] / obs_vals[i]

    eigvals = np.linalg.eigvalsh(J_norm.T @ J_norm)
    cond = (np.max(eigvals) / np.min(eigvals)
            if np.min(eigvals) > 0 else np.inf)
    return J_norm, cond, eigvals
