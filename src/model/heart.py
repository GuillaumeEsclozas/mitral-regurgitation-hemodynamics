# full 8-compartment closed loop

from .chambers import activation_ventricle, activation_atrium, chamber_pressure
from .valves import valve_flow


def compute_pressures(y, t, p):
    V_lv, V_la, V_rv, V_ra, V_sa, V_sv, V_pa, V_pv = y
    T = p.T
    b = p.beta

    e_lv = activation_ventricle(t, T, p.T_es_lv, p.tau_lv)
    e_rv = activation_ventricle(t, T, p.T_es_rv, p.tau_rv)
    e_la = activation_atrium(t, T, p.T_as_la, p.onset_la)
    e_ra = activation_atrium(t, T, p.T_as_ra, p.onset_ra)

    P_lv = chamber_pressure(V_lv, e_lv, p.E_es_lv, p.V_d_lv,
                             p.V0_lv, p.alpha_lv, b, p.V_ref_lv)
    P_rv = chamber_pressure(V_rv, e_rv, p.E_es_rv, p.V_d_rv,
                             p.V0_rv, p.alpha_rv, b, p.V_ref_rv)
    P_la = chamber_pressure(V_la, e_la, p.E_es_la, p.V_d_la,
                             p.V0_la, p.alpha_la, b, p.V_ref_la)
    P_ra = chamber_pressure(V_ra, e_ra, p.E_es_ra, p.V_d_ra,
                             p.V0_ra, p.alpha_ra, b, p.V_ref_ra)
    P_sa = (V_sa - p.V0_sa) / p.C_sa
    P_sv = (V_sv - p.V0_sv) / p.C_sv
    P_pa = (V_pa - p.V0_pa) / p.C_pa
    P_pv = (V_pv - p.V0_pv) / p.C_pv
    return P_lv, P_la, P_rv, P_ra, P_sa, P_sv, P_pa, P_pv


def compute_flows(pressures, p):
    P_lv, P_la, P_rv, P_ra, P_sa, P_sv, P_pa, P_pv = pressures
    Q_mv = valve_flow(P_la, P_lv, p.R_mv)
    Q_av = valve_flow(P_lv, P_sa, p.R_av)
    Q_tc = valve_flow(P_ra, P_rv, p.R_tc)
    Q_pv_v = valve_flow(P_rv, P_pa, p.R_pv_valve)
    Q_sys = (P_sa - P_sv) / p.R_sys
    Q_pul = (P_pa - P_pv) / p.R_pul
    Q_pv_la = (P_pv - P_la) / p.R_pv_la
    Q_sv_ra = (P_sv - P_ra) / p.R_sv_ra
    return Q_mv, Q_av, Q_tc, Q_pv_v, Q_sys, Q_pul, Q_pv_la, Q_sv_ra


def rhs(t, y, p):
    pressures = compute_pressures(y, t, p)
    Q_mv, Q_av, Q_tc, Q_pv_v, Q_sys, Q_pul, Q_pv_la, Q_sv_ra = \
        compute_flows(pressures, p)
    return [
        Q_mv - Q_av,
        Q_pv_la - Q_mv,
        Q_tc - Q_pv_v,
        Q_sv_ra - Q_tc,
        Q_av - Q_sys,
        Q_sys - Q_sv_ra,
        Q_pv_v - Q_pul,
        Q_pul - Q_pv_la,
    ]
