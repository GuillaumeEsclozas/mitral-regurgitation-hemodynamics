"""Tests for digital twin fitting and identifiability."""

import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.model.parameters import Params
from src.simulation.hemodynamics import run_turbo
from src.fitting.identifiability import compute_jacobian
from src.fitting.optimizer import fit_digital_twin


# --- Identifiability ---

def test_condition_number_healthy():
    base = dict(alpha_lv=10, E_es_lv=2.7, R_sys=1.05, EROA=0.0)
    _, cond, _ = compute_jacobian(base)
    assert cond < 100, f"cond={cond:.1f}"

def test_alpha_dominates_ea():
    base = dict(alpha_lv=10, E_es_lv=2.7, R_sys=1.05, EROA=0.0)
    J, _, _ = compute_jacobian(base)
    assert abs(J[1, 0]) > abs(J[1, 1]) and abs(J[1, 0]) > abs(J[1, 2])

def test_rsys_dominates_sbp():
    base = dict(alpha_lv=10, E_es_lv=2.7, R_sys=1.05, EROA=0.0)
    J, _, _ = compute_jacobian(base)
    assert abs(J[2, 2]) > abs(J[2, 0]) and abs(J[2, 2]) > abs(J[2, 1])


# --- Parameter recovery (one patient, keeps test fast) ---

def test_parameter_recovery_healthy():
    # these tolerances might be too tight for CI
    obs = run_turbo(Params())
    target = {"EF": obs["EF"], "EA": obs["EA"], "SBP": obs["SBP"]}
    fit = fit_digital_twin(target, {"EROA": 0.0}, verbose=False)
    assert abs(fit["alpha_lv"] - 10) / 10 < 0.01
    assert abs(fit["E_es_lv"] - 2.7) / 2.7 < 0.01
    assert abs(fit["R_sys"] - 1.05) / 1.05 < 0.01

def test_prediction_accuracy_healthy():
    obs = run_turbo(Params())
    target = {"EF": obs["EF"], "EA": obs["EA"], "SBP": obs["SBP"]}
    fit = fit_digital_twin(target, {"EROA": 0.0}, verbose=False)
    pred = fit["predictions"]
    assert abs(pred["LVEDP"] - obs["LVEDP"]) < 1.0
    assert abs(pred["mean_LAP"] - obs["mean_LAP"]) < 1.0
