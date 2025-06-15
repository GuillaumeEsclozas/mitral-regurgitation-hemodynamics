"""Valve and orifice flow models."""

import numpy as np
from .chambers import sigmoid
from .constants import MR_ORIFICE_CONSTANT


def valve_flow(P_up, P_down, R_valve, k=300.0):
    """Sigmoid-gated valve flow."""
    dP = P_up - P_down
    return sigmoid(dP, k) * dP / R_valve


def mr_flow(P_lv, P_la, EROA, k=300.0):
    """Mitral regurgitation orifice flow, sigmoid-smoothed."""
    dP = P_lv - P_la
    return sigmoid(dP, k) * EROA * MR_ORIFICE_CONSTANT * np.sqrt(max(dP, 0.0))
