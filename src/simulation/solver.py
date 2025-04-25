import numpy as np
from scipy.integrate import solve_ivp
from ..model.heart import rhs
from ..model.constants import INITIAL_VOLUMES


def simulate(p, n_beats=20, n_eval=500):
    T = p.T
    y_cur = INITIAL_VOLUMES.copy()

    for beat in range(n_beats):
        t_s = beat * T
        t_e = (beat + 1) * T
        sol = solve_ivp(rhs, [t_s, t_e], y_cur, method="RK45",
                        args=(p,), rtol=1e-6, atol=1e-8,
                        t_eval=np.linspace(t_s, t_e, n_eval))
        if not sol.success:
            return None
        y_cur = sol.y[:, -1]

    return sol
