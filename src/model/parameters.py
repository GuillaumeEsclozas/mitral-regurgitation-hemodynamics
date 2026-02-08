"""Model parameters as a frozen dataclass with validation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Params:
    """Cardiovascular model parameters. Immutable after creation."""
    E_es_lv: float = 2.7
    V_d_lv: float = 10.0
    V0_lv: float = 10.0
    alpha_lv: float = 10.0
    V_ref_lv: float = 110.0
    T_es_lv: float = 0.3
    tau_lv: float = 0.025
    E_es_rv: float = 0.7
    V_d_rv: float = 10.0
    V0_rv: float = 10.0
    alpha_rv: float = 10.0
    V_ref_rv: float = 110.0
    T_es_rv: float = 0.3
    tau_rv: float = 0.025
    E_es_la: float = 0.65
    V_d_la: float = 4.0
    V0_la: float = 4.0
    alpha_la: float = 3.0
    V_ref_la: float = 40.0
    T_as_la: float = 0.12
    onset_la: float = 0.70
    E_es_ra: float = 0.39
    V_d_ra: float = 4.0
    V0_ra: float = 4.0
    alpha_ra: float = 3.0
    V_ref_ra: float = 40.0
    T_as_ra: float = 0.12
    onset_ra: float = 0.70
    C_sa: float = 1.5
    V0_sa: float = 750.0
    C_sv: float = 60.0
    V0_sv: float = 2920.0
    C_pa: float = 4.0
    V0_pa: float = 120.0
    C_pv: float = 8.0
    V0_pv: float = 250.0
    R_sys: float = 1.05
    R_pul: float = 0.08
    R_mv: float = 0.005
    R_av: float = 0.005
    R_tc: float = 0.005
    R_pv_valve: float = 0.005
    R_pv_la: float = 0.01
    R_sv_ra: float = 0.01
    HR: float = 75.0
    EROA: float = 0.0
    k_valve: float = 300.0
    beta: float = 2.5

    @property
    def T(self) -> float:
        return 60.0 / self.HR

    def __post_init__(self):
        if self.EROA < 0:
            raise ValueError(f"EROA must be >= 0, got {self.EROA}")
        if self.E_es_lv <= 0:
            raise ValueError(f"E_es_lv must be > 0, got {self.E_es_lv}")
        if self.R_sys <= 0:
            raise ValueError(f"R_sys must be > 0, got {self.R_sys}")
        if self.alpha_lv <= 0:
            raise ValueError(f"alpha_lv must be > 0, got {self.alpha_lv}")
        if self.HR <= 0:
            raise ValueError(f"HR must be > 0, got {self.HR}")

    def replace(self, **kwargs) -> "Params":
        d = {f.name: getattr(self, f.name)
             for f in self.__dataclass_fields__.values()}
        d.update(kwargs)
        return Params(**d)
