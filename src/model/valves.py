# simple valve model, open/close based on pressure gradient

def valve_flow(P_up, P_down, R_valve):
    dP = P_up - P_down
    if dP <= 0:
        return 0.0
    return dP / R_valve
