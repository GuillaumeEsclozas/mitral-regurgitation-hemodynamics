import numpy as np
from scipy.integrate import solve_ivp
from ..model.heart import rhs


def simulate(p, n_beats=20, n_eval=500):
    T = p.T
    y0 = [120.0, 60.0, 900.0, 3200.0]
    y_cur = np.array(y0)

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
