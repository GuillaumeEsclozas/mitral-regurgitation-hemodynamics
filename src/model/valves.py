# simple valve model, open/close based on pressure gradient
import numpy as np


def valve_flow(P_up, P_down, R_valve):
    dP = P_up - P_down
    if dP <= 0:
        return 0.0
    return dP / R_valve


def mr_flow(P_lv, P_la, EROA):
    """MR orifice flow, Gorlin-based."""
    dP = P_lv - P_la
    if dP <= 0:
        return 0.0
    # 50.16 = conversion factor, see Gorlin formula
    return EROA * 50.16 * np.sqrt(dP)
