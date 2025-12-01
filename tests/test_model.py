"""Tests for model physics: chambers, valves, and parameters."""

import numpy as np
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.model.parameters import Params
from src.model.chambers import (sigmoid, activation_ventricle,
                                activation_atrium, edpvr, chamber_pressure)
from src.model.valves import valve_flow, mr_flow
from src.model.constants import MR_ORIFICE_CONSTANT


T = Params().T


# --- Activation ventricle ---

def test_vent_activation_zero_at_start():
    assert abs(activation_ventricle(0, T)) < 1e-10

def test_vent_activation_one_at_T_es():
    assert abs(activation_ventricle(0.3, T) - 1.0) < 1e-10

def test_vent_activation_decays():
    assert activation_ventricle(0.4, T) < 0.02

def test_vent_activation_periodic():
    assert abs(activation_ventricle(0.1, T) - activation_ventricle(0.1 + T, T)) < 1e-10

def test_vent_activation_c0_continuous():
    assert abs(activation_ventricle(0.3 - 1e-10, T) - activation_ventricle(0.3 + 1e-10, T)) < 1e-6

def test_vent_activation_scalar_returns_float():
    assert isinstance(activation_ventricle(0.15, T), float)

def test_vent_activation_array_returns_ndarray():
    result = activation_ventricle(np.linspace(0, T, 10), T)
    assert isinstance(result, np.ndarray)
    assert result.shape == (10,)


# --- Activation atrium ---

def test_atrium_zero_before_onset():
    assert abs(activation_atrium(0, T)) < 1e-10

def test_atrium_peaks_at_one():
    assert abs(activation_atrium(0.70 * T + 0.12 - 1e-6, T) - 1.0) < 0.01

def test_atrium_zero_after_contraction():
    assert abs(activation_atrium(0.70 * T + 0.15, T)) < 1e-10

def test_atrium_periodic():
    assert abs(activation_atrium(0.6, T) - activation_atrium(0.6 + T, T)) < 1e-10


# --- EDPVR ---

def test_edpvr_zero_at_v0():
    assert abs(edpvr(10, 10, 10, 2.5, 110)) < 1e-10

def test_edpvr_zero_below_v0():
    assert abs(edpvr(5, 10, 10, 2.5, 110)) < 1e-10

def test_edpvr_positive_above_v0():
    assert edpvr(120, 10, 10, 2.5, 110) > 0

def test_edpvr_about_10_at_v120():
    assert abs(edpvr(120, 10, 10, 2.5, 110) - 10.0) < 1.0

def test_edpvr_monotonic_in_alpha():
    assert edpvr(120, 10, 20, 2.5, 110) > edpvr(120, 10, 10, 2.5, 110)

def test_edpvr_linear_in_alpha():
    ratio = edpvr(120, 10, 20, 2.5, 110) / edpvr(120, 10, 10, 2.5, 110)
    assert abs(ratio - 2.0) < 0.01


# --- Chamber pressure ---

def test_pressure_at_e0_equals_edpvr():
    P = chamber_pressure(120, 0, 2.7, 10, 10, 10, 2.5, 110)
    P_passive = edpvr(120, 10, 10, 2.5, 110)
    assert abs(P - P_passive) < 1e-10

def test_pressure_at_e1_equals_espvr():
    P = chamber_pressure(60, 1, 2.7, 10, 10, 10, 2.5, 110)
    assert abs(P - 2.7 * 50) < 1e-10


# --- Sigmoid ---

def test_sigmoid_half_at_zero():
    assert abs(sigmoid(0) - 0.5) < 1e-10

def test_sigmoid_one_at_positive():
    assert abs(sigmoid(10) - 1.0) < 1e-10

def test_sigmoid_zero_at_negative():
    assert abs(sigmoid(-10)) < 1e-10


# --- Valve flow ---

def test_valve_opens_on_positive_dp():
    assert valve_flow(100, 80, 0.005) > 3900

def test_valve_closes_on_negative_dp():
    assert abs(valve_flow(80, 100, 0.005)) < 0.01

def test_valve_flow_equals_dp_over_r():
    assert abs(valve_flow(100, 80, 0.005) - 4000) < 10


# --- MR flow ---

def test_mr_flow_sanity_check():
    assert abs(mr_flow(180, 80, 0.3) - 0.3 * 50.16 * 10) < 1.0

def test_mr_flow_zero_at_eroa_zero():
    assert abs(mr_flow(180, 80, 0.0)) < 1e-10

def test_mr_flow_zero_at_negative_dp():
    assert abs(mr_flow(70, 80, 0.3)) < 0.01

def test_mr_constant_derivation():
    const = 1e-4 * np.sqrt(2 * 133.322 / 1060) * 1e6
    assert abs(const - 50.16) < 0.01


# --- Params dataclass ---

def test_params_T():
    assert abs(Params().T - 0.8) < 1e-10
