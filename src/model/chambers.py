"""Cardiac chamber physics: activation functions and PV relationships."""

import numpy as np
from .constants import SIGMOID_CLIP


def sigmoid(x, k=300.0):
    """Smooth Heaviside approximation."""
    return 1.0 / (1.0 + np.exp(-np.clip(k * x, -SIGMOID_CLIP, SIGMOID_CLIP)))


def activation_ventricle(t, T, T_es=0.3, tau=0.025):
    """Half-sine contraction + exponential relaxation tail."""
    t_v = np.mod(t, T)
    contraction = 0.5 * (1.0 - np.cos(np.pi * t_v / T_es))
    relaxation = np.exp(-(t_v - T_es) / tau)
    result = np.where(t_v < T_es, contraction, relaxation)
    return float(result) if np.ndim(result) == 0 else result


def activation_atrium(t, T, T_as=0.12, onset_frac=0.70):
    """Phase-shifted half-sine in late diastole."""
    t_a = np.mod(t, T) - onset_frac * T
    t_a = np.where(t_a < 0, t_a + T, t_a)
    contraction = 0.5 * (1.0 - np.cos(np.pi * t_a / T_as))
    result = np.where(t_a < T_as, contraction, 0.0)
    return float(result) if np.ndim(result) == 0 else result


def edpvr(V, V0, alpha, beta, V_ref):
    """Power law end-diastolic pressure-volume relationship."""
    return alpha * (np.maximum(V - V0, 0.0) / V_ref) ** beta


def chamber_pressure(V, e, E_es, V_d, V0, alpha, beta, V_ref):
    """Time-varying elastance: blend active ESPVR with passive EDPVR."""
    return e * E_es * (V - V_d) + (1.0 - e) * edpvr(V, V0, alpha, beta, V_ref)
