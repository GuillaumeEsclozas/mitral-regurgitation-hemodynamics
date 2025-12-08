"""Tests for simulation: baseline targets, conservation, MR physics, diastolic."""

import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.model.parameters import Params
from src.simulation.hemodynamics import run_turbo, run_production
from src.simulation.solver import simulate


# --- Healthy baseline ---

def test_baseline_converges():
    assert run_turbo(Params()) is not None

def test_baseline_ef():
    r = run_turbo(Params())
    assert 55 < r["EF"] < 60, f"EF={r['EF']:.1f}"

def test_baseline_edv():
    r = run_turbo(Params())
    assert 120 < r["EDV"] < 135, f"EDV={r['EDV']:.1f}"

def test_baseline_esv():
    r = run_turbo(Params())
    assert 45 < r["ESV"] < 65, f"ESV={r['ESV']:.1f}"

def test_baseline_sbp():
    r = run_turbo(Params())
    assert 110 < r["SBP"] < 125, f"SBP={r['SBP']:.1f}"

def test_baseline_co():
    r = run_turbo(Params())
    assert 4.5 < r["CO"] < 6.0, f"CO={r['CO']:.2f}"

def test_baseline_lvedp():
    r = run_turbo(Params())
    assert 8 < r["LVEDP"] < 14, f"LVEDP={r['LVEDP']:.1f}"

def test_baseline_lap():
    r = run_turbo(Params())
    assert 5 < r["mean_LAP"] < 10, f"LAP={r['mean_LAP']:.1f}"

def test_baseline_pap():
    r = run_turbo(Params())
    assert 12 < r["mean_PAP"] < 20, f"PAP={r['mean_PAP']:.1f}"

def test_baseline_ea():
    r = run_turbo(Params())
    assert r["EA"] is not None and 1.0 < r["EA"] < 2.0, f"E/A={r['EA']}"

def test_baseline_no_regurgitation():
    r = run_turbo(Params())
    assert r["RegVol"] < 0.01


# --- Conservation ---

def test_volume_conservation_healthy():
    sol = simulate(Params(), n_beats=25)
    assert abs(np.sum(sol.y[:, -1]) - 5000.0) < 0.01

def test_volume_conservation_mr():
    sol = simulate(Params(EROA=0.3), n_beats=25)
    assert abs(np.sum(sol.y[:, -1]) - 5000.0) < 0.01

def test_volume_conservation_stiff_mr():
    sol = simulate(Params(EROA=0.5, alpha_lv=30), n_beats=25)
    assert abs(np.sum(sol.y[:, -1]) - 5000.0) < 0.01

def test_sv_conservation():
    for eroa in [0.0, 0.2, 0.4]:
        r = run_turbo(Params(EROA=eroa))
        sv_total = r["EF"] / 100 * r["EDV"]
        diff = abs(sv_total - r["SV_fwd"] - r["RegVol"])
        assert diff < 1.0, f"EROA={eroa}: diff={diff:.3f}"


# --- MR physics ---

def test_ef_paradox_total_rises():
    r0 = run_turbo(Params(EROA=0.0))
    r4 = run_turbo(Params(EROA=0.4))
    assert r4["EF"] > r0["EF"]

def test_ef_paradox_forward_falls():
    r0 = run_turbo(Params(EROA=0.0))
    r4 = run_turbo(Params(EROA=0.4))
    assert r4["EF_fwd"] < r0["EF_fwd"]

def test_volume_overload():
    r0 = run_turbo(Params(EROA=0.0))
    r4 = run_turbo(Params(EROA=0.4))
    assert r4["EDV"] > r0["EDV"]

def test_easier_ejection():
    r0 = run_turbo(Params(EROA=0.0))
    r4 = run_turbo(Params(EROA=0.4))
    assert r4["ESV"] < r0["ESV"]

def test_co_decreases_with_mr():
    r0 = run_turbo(Params(EROA=0.0))
    r4 = run_turbo(Params(EROA=0.4))
    assert r4["CO"] < r0["CO"]

def test_lap_increases_with_mr():
    r0 = run_turbo(Params(EROA=0.0))
    r4 = run_turbo(Params(EROA=0.4))
    assert r4["mean_LAP"] > r0["mean_LAP"]

def test_regvol_positive():
    r = run_turbo(Params(EROA=0.4))
    assert r["RegVol"] > 30

def test_regvol_scales_with_eroa():
    r1 = run_turbo(Params(EROA=0.1))
    r3 = run_turbo(Params(EROA=0.3))
    assert r3["RegVol"] > r1["RegVol"]

def test_disproportionate_mr_lap():
    rp2 = run_turbo(Params(alpha_lv=10, EROA=0.4))
    rp4 = run_turbo(Params(alpha_lv=18, EROA=0.25, R_sys=1.1))
    assert rp4["mean_LAP"] > rp2["mean_LAP"]

def test_disproportionate_mr_lvedp():
    rp2 = run_turbo(Params(alpha_lv=10, EROA=0.4))
    rp4 = run_turbo(Params(alpha_lv=18, EROA=0.25, R_sys=1.1))
    assert rp4["LVEDP"] > rp2["LVEDP"]


# --- Diastolic dysfunction ---

def test_stiffness_raises_lvedp():
    r_n = run_turbo(Params(alpha_lv=10, tau_lv=0.025))
    r_s = run_turbo(Params(alpha_lv=14, tau_lv=0.080))
    assert r_s["LVEDP"] > r_n["LVEDP"]

def test_stiffness_reduces_co():
    r_n = run_turbo(Params(alpha_lv=10, tau_lv=0.025))
    r_s = run_turbo(Params(alpha_lv=14, tau_lv=0.080))
    assert r_s["CO"] < r_n["CO"]

def test_severe_stiffness_high_lvedp():
    r = run_turbo(Params(alpha_lv=35, tau_lv=0.025))
    assert r["LVEDP"] > 20

def test_severe_stiffness_high_lap():
    r = run_turbo(Params(alpha_lv=35, tau_lv=0.025))
    assert r["mean_LAP"] > 14


# --- Turbo vs production agreement ---

def test_turbo_matches_production():
    r_t = run_turbo(Params())
    r_p = run_production(Params())
    assert abs(r_t["EF"] - r_p["EF"]) < 0.2
    assert abs(r_t["SBP"] - r_p["SBP"]) < 0.5
