"""Hemodynamic index extraction from simulation solutions."""

import numpy as np
from ..model.heart import compute_pressures, compute_flows
from ..model.chambers import edpvr
from ..model.constants import VALVE_OPEN_THRESHOLD


def compute_waveforms(sol, p):
    """Compute all pressures and flows from an ODE solution."""
    t = sol.t; n = len(t)
    P_lv = np.zeros(n); P_la = np.zeros(n); P_rv = np.zeros(n)
    P_ra = np.zeros(n); P_sa = np.zeros(n); P_pa = np.zeros(n)
    Q_mv = np.zeros(n); Q_av = np.zeros(n); Q_mr = np.zeros(n)
    for i, ti in enumerate(t):
        pressures = compute_pressures(sol.y[:, i], ti, p)
        P_lv[i], P_la[i], P_rv[i], P_ra[i], P_sa[i], _, P_pa[i], _ = pressures
        flows = compute_flows(pressures, p)
        Q_mv[i], Q_av[i] = flows[0], flows[1]
        Q_mr[i] = flows[8]
    return {
        "t": t, "V_lv": sol.y[0], "V_la": sol.y[1],
        "V_rv": sol.y[2], "V_ra": sol.y[3],
        "P_lv": P_lv, "P_la": P_la, "P_rv": P_rv, "P_ra": P_ra,
        "P_sa": P_sa, "P_pa": P_pa,
        "Q_mv": Q_mv, "Q_av": Q_av, "Q_mr": Q_mr,
    }


def extract_ea(Q_mv, t, onset_frac=0.70):
    """Activation-based E/A extraction."""
    T_beat = t[-1] - t[0]
    onset_time = onset_frac * T_beat
    t_in_beat = t - t[0]
    diastole_start = None
    for i in range(len(Q_mv)):
        if Q_mv[i] > VALVE_OPEN_THRESHOLD:
            diastole_start = i
            break
    if diastole_start is None:
        return None, 0, 0, "no_diastole"
    onset_idx = None
    for i in range(len(t_in_beat)):
        if t_in_beat[i] >= onset_time:
            onset_idx = i
            break
    if onset_idx is None or onset_idx <= diastole_start:
        return None, 0, 0, "bad_timing"
    E_peak = np.max(Q_mv[diastole_start:onset_idx])
    A_peak = np.max(Q_mv[onset_idx:])
    if E_peak < VALVE_OPEN_THRESHOLD and A_peak < VALVE_OPEN_THRESHOLD:
        return None, E_peak, A_peak, "no_filling"
    if A_peak < 10:
        return None, E_peak, A_peak, "fused_E_dominant"
    if E_peak < VALVE_OPEN_THRESHOLD:
        return None, E_peak, A_peak, "fused_A_dominant"
    ratio = E_peak / A_peak
    pattern = ("restrictive" if ratio > 2.0
               else "normal" if ratio > 0.8
               else "impaired_relaxation")
    return ratio, E_peak, A_peak, pattern


def extract_indices(sol, p):
    """Extract all hemodynamic indices from a simulation solution."""
    w = compute_waveforms(sol, p)
    t = w["t"]
    V_lv = w["V_lv"]; V_la = w["V_la"]
    V_rv = w["V_rv"]; V_ra = w["V_ra"]
    P_lv = w["P_lv"]; P_la = w["P_la"]
    P_sa = w["P_sa"]; P_pa = w["P_pa"]; P_ra = w["P_ra"]
    Q_mv = w["Q_mv"]; Q_av = w["Q_av"]; Q_mr = w["Q_mr"]

    EDV = np.max(V_lv); ESV = np.min(V_lv); SV_total = EDV - ESV
    dt = np.diff(t)
    SV_fwd = np.sum(np.maximum(0.5 * (Q_av[:-1] + Q_av[1:]), 0) * dt)
    RegVol = np.sum(np.maximum(0.5 * (Q_mr[:-1] + Q_mr[1:]), 0) * dt)
    LVEDP = edpvr(EDV, p.V0_lv, p.alpha_lv, p.beta, p.V_ref_lv)
    SBP = np.max(P_sa); DBP = np.min(P_sa)
    mean_LAP = np.mean(P_la); mean_PAP = np.mean(P_pa)
    mean_RAP = np.mean(P_ra)

    mv_open_idx = len(P_la) - 1
    for i in range(50, len(P_la)):
        if P_la[i] > P_lv[i]:
            mv_open_idx = i
            break
    v_wave = np.max(P_la[:mv_open_idx])

    ea, E_pk, A_pk, pattern = extract_ea(Q_mv, t, p.onset_la)
    EF = SV_total / EDV * 100
    EF_fwd = SV_fwd / EDV * 100
    CO = SV_fwd * p.HR / 1000
    reg_frac = RegVol / SV_total * 100 if SV_total > 0 else 0

    return {
        "EDV": EDV, "ESV": ESV, "SV_total": SV_total,
        "SV_fwd": SV_fwd, "RegVol": RegVol, "reg_frac": reg_frac,
        "EF": EF, "EF_fwd": EF_fwd, "CO": CO, "LVEDP": LVEDP,
        "SBP": SBP, "DBP": DBP, "MAP": np.mean(P_sa),
        "mean_LAP": mean_LAP, "PCWP": mean_LAP,
        "mean_PAP": mean_PAP, "mean_RAP": mean_RAP,
        "v_wave": v_wave,
        "v_wave_ratio": v_wave / mean_LAP if mean_LAP > 0 else 0,
        "EA": ea, "E_pk": E_pk, "A_pk": A_pk, "ea_pattern": pattern,
        "LA_min": np.min(V_la), "LA_max": np.max(V_la),
        "RA_min": np.min(V_ra), "RA_max": np.max(V_ra),
        "RV_EDV": np.max(V_rv), "RV_ESV": np.min(V_rv),
        "V_total": np.sum(sol.y[:, -1]),
        "waveforms": w,
    }


def run_production(p):
    """Full production run with all indices."""
    from .solver import simulate
    sol = simulate(p)
    return extract_indices(sol, p) if sol else None


def run_turbo(p):
    """Fast run for parameter estimation."""
    from .solver import simulate_turbo
    sol = simulate_turbo(p)
    if sol is None:
        return None
    try:
        r = extract_indices(sol, p)
        if r["EDV"] < 30 or r["EDV"] > 300 or r["ESV"] < 5:
            return None
        if r["SBP"] < 40 or r["SBP"] > 250:
            return None
        if r["CO"] < 1.0 or r["CO"] > 12.0:
            return None
        return r
    except (ValueError, RuntimeError):
        return None
