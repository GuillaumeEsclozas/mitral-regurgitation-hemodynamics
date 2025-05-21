"""Hemodynamic index extraction from simulation solutions."""

import numpy as np
from ..model.heart import compute_pressures, compute_flows
from ..model.chambers import edpvr


def compute_waveforms(sol, p):
    t = sol.t
    n = len(t)
    P_lv = np.zeros(n)
    P_la = np.zeros(n)
    P_rv = np.zeros(n)
    P_ra = np.zeros(n)
    P_sa = np.zeros(n)
    P_pa = np.zeros(n)
    Q_mv = np.zeros(n)
    Q_av = np.zeros(n)
    Q_mr = np.zeros(n)

    for i, ti in enumerate(t):
        pressures = compute_pressures(sol.y[:, i], ti, p)
        P_lv[i], P_la[i], P_rv[i], P_ra[i], P_sa[i], _, P_pa[i], _ = pressures
        flows = compute_flows(pressures, p)
        Q_mv[i] = flows[0]
        Q_av[i] = flows[1]
        Q_mr[i] = flows[8]

    return {
        "t": t, "V_lv": sol.y[0], "V_la": sol.y[1],
        "V_rv": sol.y[2], "V_ra": sol.y[3],
        "P_lv": P_lv, "P_la": P_la, "P_rv": P_rv, "P_ra": P_ra,
        "P_sa": P_sa, "P_pa": P_pa,
        "Q_mv": Q_mv, "Q_av": Q_av, "Q_mr": Q_mr,
    }


def extract_indices(sol, p):
    w = compute_waveforms(sol, p)
    t = w["t"]
    V_lv = w["V_lv"]
    P_lv = w["P_lv"]
    P_la = w["P_la"]
    P_sa = w["P_sa"]
    Q_mv = w["Q_mv"]

    EDV = np.max(V_lv)
    ESV = np.min(V_lv)
    SV = EDV - ESV
    EF = SV / EDV * 100
    LVEDP = edpvr(EDV, p.V0_lv, p.alpha_lv, p.beta, p.V_ref_lv)
    SBP = np.max(P_sa)
    DBP = np.min(P_sa)
    mean_LAP = np.mean(P_la)

    dt = np.diff(t)
    CO = np.sum(np.maximum(0.5 * (w["Q_av"][:-1] + w["Q_av"][1:]), 0) * dt) * p.HR / 1000

    return {
        "EDV": EDV, "ESV": ESV, "SV": SV, "EF": EF,
        "LVEDP": LVEDP, "SBP": SBP, "DBP": DBP,
        "mean_LAP": mean_LAP, "CO": CO,
    }


def run_production(p):
    from .solver import simulate
    sol = simulate(p)
    return extract_indices(sol, p) if sol else None
