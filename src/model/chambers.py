"""Cardiac chamber physics: activation functions and PV relationships."""

import numpy as np
from .constants import SIGMOID_CLIP


def sigmoid(x: float, k: float = 300.0) -> float:
    """Smooth Heaviside approximation."""
    return 1.0 / (1.0 + np.exp(-np.clip(k * x, -SIGMOID_CLIP, SIGMOID_CLIP)))


def activation_ventricle(t: float, T: float,
                         T_es: float = 0.3, tau: float = 0.025) -> float:
    """Half-sine contraction + exponential relaxation tail."""
    t_v = np.mod(t, T)
    contraction = 0.5 * (1.0 - np.cos(np.pi * t_v / T_es))
    relaxation = np.exp(-(t_v - T_es) / tau)
    result = np.where(t_v < T_es, contraction, relaxation)
    return float(result) if np.ndim(result) == 0 else result


def activation_atrium(t: float, T: float,
                      T_as: float = 0.12, onset_frac: float = 0.70) -> float:
    """Phase-shifted half-sine in late diastole."""
    t_a = np.mod(t, T) - onset_frac * T
    t_a = np.where(t_a < 0, t_a + T, t_a)
    contraction = 0.5 * (1.0 - np.cos(np.pi * t_a / T_as))
    result = np.where(t_a < T_as, contraction, 0.0)
    return float(result) if np.ndim(result) == 0 else result


def edpvr(V: float, V0: float, alpha: float,
          beta: float, V_ref: float) -> float:
    """Power law end-diastolic pressure-volume relationship."""
    return alpha * (np.maximum(V - V0, 0.0) / V_ref) ** beta


def chamber_pressure(V: float, e: float, E_es: float, V_d: float,
                     V0: float, alpha: float, beta: float,
                     V_ref: float) -> float:
    """Time-varying elastance: blend active ESPVR with passive EDPVR."""
    return e * E_es * (V - V_d) + (1.0 - e) * edpvr(V, V0, alpha, beta, V_ref)
