"""Beat-by-beat ODE solver with convergence checking."""

import numpy as np
from scipy.integrate import solve_ivp
from ..model.heart import rhs
from ..model.constants import CONVERGENCE_TOL, INITIAL_VOLUMES


def simulate(p, n_beats=30, n_eval=1000,
             rtol=1e-6, atol=1e-8, max_step=0.005):
    """Run model to steady state. Returns solution for last beat."""
    T = p.T
    y_cur = INITIAL_VOLUMES.copy()
    sv_prev = None
    for beat in range(n_beats):
        t_s = beat * T; t_e = (beat + 1) * T
        sol = solve_ivp(rhs, [t_s, t_e], y_cur, method="RK45",
                        args=(p,), rtol=rtol, atol=atol,
                        max_step=max_step,
                        t_eval=np.linspace(t_s, t_e, n_eval))
        if not sol.success:
            return None
        y_cur = sol.y[:, -1]
        sv = np.max(sol.y[0]) - np.min(sol.y[0])
        if sv_prev is not None and sv_prev > 0:
            if abs(sv - sv_prev) / sv_prev < CONVERGENCE_TOL:
                return sol
        sv_prev = sv
    return sol


def simulate_turbo(p):
    """Fast simulation for parameter estimation."""
    T = p.T
    y_cur = INITIAL_VOLUMES.copy()
    sv_prev = None
    for beat in range(20):
        t_s = beat * T; t_e = (beat + 1) * T
        sol = solve_ivp(rhs, [t_s, t_e], y_cur, method="RK45",
                        args=(p,), rtol=1e-4, atol=1e-6, max_step=0.01)
        if not sol.success:
            return None
        y_cur = sol.y[:, -1]
        sv = np.max(sol.y[0]) - np.min(sol.y[0])
        if sv_prev is not None and sv_prev > 0:
            if abs(sv - sv_prev) / sv_prev < CONVERGENCE_TOL:
                return solve_ivp(rhs, [t_s, t_e], sol.y[:, 0],
                                 method="RK45", args=(p,),
                                 rtol=1e-4, atol=1e-6, max_step=0.005,
                                 t_eval=np.linspace(t_s, t_e, 400))
        sv_prev = sv
    return solve_ivp(rhs, [beat * T, (beat + 1) * T], y_cur,
                     method="RK45", args=(p,),
                     rtol=1e-4, atol=1e-6, max_step=0.005,
                     t_eval=np.linspace(beat * T, (beat + 1) * T, 400))
