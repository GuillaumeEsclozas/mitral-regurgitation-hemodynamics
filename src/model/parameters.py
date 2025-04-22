class Params:
    """Cardiovascular model parameters, all four chambers + vasculature."""
    def __init__(self, **kwargs):
        # LV
        self.E_es_lv = 2.7
        self.V_d_lv = 10.0
        self.V0_lv = 10.0
        self.alpha_lv = 0.05
        self.beta_lv = 0.03
        self.T_es_lv = 0.3
        self.tau_lv = 0.025

        # LA
        self.E_es_la = 0.65
        self.V_d_la = 4.0
        self.V0_la = 4.0
        self.alpha_la = 0.03
        self.beta_la = 0.03
        self.T_as_la = 0.12
        self.onset_la = 0.70

        # RV
        self.E_es_rv = 0.7
        self.V_d_rv = 10.0
        self.V0_rv = 10.0
        self.alpha_rv = 0.05
        self.beta_rv = 0.03
        self.T_es_rv = 0.3
        self.tau_rv = 0.025

        # RA
        self.E_es_ra = 0.39
        self.V_d_ra = 4.0
        self.V0_ra = 4.0
        self.alpha_ra = 0.03
        self.beta_ra = 0.03
        self.T_as_ra = 0.12
        self.onset_ra = 0.70

        # systemic
        self.C_sa = 1.5
        self.V0_sa = 750.0
        self.C_sv = 60.0
        self.V0_sv = 2920.0
        self.R_sys = 1.05

        # pulmonary
        self.C_pa = 4.0
        self.V0_pa = 120.0
        self.C_pv = 8.0
        self.V0_pv = 250.0
        self.R_pul = 0.08

        # valves
        self.R_mv = 0.005
        self.R_av = 0.005
        self.R_tc = 0.005
        self.R_pv_valve = 0.005
        self.R_pv_la = 0.01
        self.R_sv_ra = 0.01

        self.HR = 75.0

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def T(self):
        return 60.0 / self.HR
