from numpy import exp, cos, pi


def activation_ventricle(t, T, T_es=0.3, tau=0.025):
    t_v = t % T
    if t_v < T_es:
        return 0.5 * (1.0 - cos(pi * t_v / T_es))
    else:
        return exp(-(t_v - T_es) / tau)


def activation_atrium(t, T, T_as=0.12, onset_frac=0.70):
    t_a = (t % T) - onset_frac * T
    # was missing the wraparound, atria were contracting at wrong time
    if t_a < 0:
        t_a += T
    if t_a < T_as:
        return 0.5 * (1.0 - cos(pi * t_a / T_as))
    else:
        return 0.0


def edpvr(V, V0, alpha, beta, V_ref):
    return alpha * (max(V - V0, 0) / V_ref) ** beta


def chamber_pressure(V, e, E_es, V_d, V0, alpha, beta, V_ref):
    P_active = e * E_es * (V - V_d)
    P_passive = edpvr(V, V0, alpha, beta, V_ref)
    return P_active + (1.0 - e) * P_passive
