class Params:
    """LV + LA + systemic circulation parameters."""
    def __init__(self, **kwargs):
        # LV
        self.E_es_lv = 2.7
        self.V_d_lv = 10.0
        self.V0_lv = 10.0
        self.alpha_lv = 0.05     # exponential EDPVR coeff
        self.beta_lv = 0.03      # exponential EDPVR coeff
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

        # systemic
        self.C_sa = 1.5
        self.V0_sa = 750.0
        self.C_sv = 60.0
        self.V0_sv = 2920.0
        self.R_sys = 1.05
        self.R_mv = 0.005
        self.R_av = 0.005

        self.HR = 75.0

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def T(self):
        return 60.0 / self.HR
