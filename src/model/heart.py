# Just left heart + systemic for now, will add right heart later

from .chambers import activation_ventricle, activation_atrium, chamber_pressure
from .valves import valve_flow


def compute_pressures_4(y, t, p):
    V_lv, V_la, V_sa, V_sv = y
    T = p.T

    e_lv = activation_ventricle(t, T, p.T_es_lv, p.tau_lv)
    e_la = activation_atrium(t, T, p.T_as_la, p.onset_la)

    P_lv = chamber_pressure(V_lv, e_lv, p.E_es_lv, p.V_d_lv,
                             p.V0_lv, p.alpha_lv, p.beta_lv)
    P_la = chamber_pressure(V_la, e_la, p.E_es_la, p.V_d_la,
                             p.V0_la, p.alpha_la, p.beta_la)
    P_sa = (V_sa - p.V0_sa) / p.C_sa
    P_sv = (V_sv - p.V0_sv) / p.C_sv
    return P_lv, P_la, P_sa, P_sv


def rhs(t, y, p):
    P_lv, P_la, P_sa, P_sv = compute_pressures_4(y, t, p)

    Q_mv = valve_flow(P_la, P_lv, p.R_mv)
    Q_av = valve_flow(P_lv, P_sa, p.R_av)
    Q_sys = (P_sa - P_sv) / p.R_sys
    # TODO: need a proper venous return resistance, this is a hack
    Q_return = (P_sv - P_la) / (p.R_sys * 0.05)

    dV_lv = Q_mv - Q_av
    dV_la = Q_return - Q_mv
    dV_sa = Q_av - Q_sys   # was backwards, took me an hour to find this
    dV_sv = Q_sys - Q_return

    return [dV_lv, dV_la, dV_sa, dV_sv]
