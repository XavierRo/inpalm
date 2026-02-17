from pydantic import BaseModel


# --- Fertilizer Properties ---
class FertilizerPropertyBase(BaseModel):
    name: str
    type: str
    n_content: float
    nh4_fraction: float | None = None
    no3_fraction: float | None = None
    organic_n_fraction: float | None = None
    unit_conversion: float | None = 1.0
    description: str | None = None


class FertilizerPropertyCreate(FertilizerPropertyBase):
    pass


class FertilizerPropertyUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    n_content: float | None = None
    nh4_fraction: float | None = None
    no3_fraction: float | None = None
    organic_n_fraction: float | None = None
    unit_conversion: float | None = None
    description: str | None = None


class FertilizerPropertyRead(FertilizerPropertyBase):
    id: int

    model_config = {"from_attributes": True}


# --- Emission Factors ---
class EmissionFactorBase(BaseModel):
    flux_type: str
    source: str
    method: str
    factor_value: float
    factor_unit: str | None = None
    description: str | None = None


class EmissionFactorCreate(EmissionFactorBase):
    pass


class EmissionFactorUpdate(BaseModel):
    flux_type: str | None = None
    source: str | None = None
    method: str | None = None
    factor_value: float | None = None
    factor_unit: str | None = None
    description: str | None = None


class EmissionFactorRead(EmissionFactorBase):
    id: int

    model_config = {"from_attributes": True}


# --- Volatilization Params ---
class VolatilizationParamBase(BaseModel):
    fertilizer_name: str
    placement: str
    base_rate: float
    ph_adjustment: float | None = 0.0
    temperature_adjustment: float | None = 0.0
    description: str | None = None


class VolatilizationParamCreate(VolatilizationParamBase):
    pass


class VolatilizationParamUpdate(BaseModel):
    fertilizer_name: str | None = None
    placement: str | None = None
    base_rate: float | None = None
    ph_adjustment: float | None = None
    temperature_adjustment: float | None = None
    description: str | None = None


class VolatilizationParamRead(VolatilizationParamBase):
    id: int

    model_config = {"from_attributes": True}


# --- Leaching Params ---
class LeachingParamBase(BaseModel):
    texture: str
    slope_min: float | None = None
    slope_max: float | None = None
    terraces: str | None = None
    base_leaching_fraction: float
    rainfall_coefficient: float | None = 1.0
    description: str | None = None


class LeachingParamCreate(LeachingParamBase):
    pass


class LeachingParamUpdate(BaseModel):
    texture: str | None = None
    slope_min: float | None = None
    slope_max: float | None = None
    terraces: str | None = None
    base_leaching_fraction: float | None = None
    rainfall_coefficient: float | None = None
    description: str | None = None


class LeachingParamRead(LeachingParamBase):
    id: int

    model_config = {"from_attributes": True}


# --- Fuzzy Membership ---
class FuzzyMembershipBase(BaseModel):
    variable_name: str
    linguistic_value: str
    membership_type: str = "triangular"
    params: dict
    output_min: float | None = None
    output_max: float | None = None


class FuzzyMembershipCreate(FuzzyMembershipBase):
    pass


class FuzzyMembershipUpdate(BaseModel):
    variable_name: str | None = None
    linguistic_value: str | None = None
    membership_type: str | None = None
    params: dict | None = None
    output_min: float | None = None
    output_max: float | None = None


class FuzzyMembershipRead(FuzzyMembershipBase):
    id: int

    model_config = {"from_attributes": True}


# --- Fuzzy Rules ---
class FuzzyRuleBase(BaseModel):
    rule_set_name: str
    conditions: dict
    output_value: float
    weight: float = 1.0
    description: str | None = None


class FuzzyRuleCreate(FuzzyRuleBase):
    pass


class FuzzyRuleRead(FuzzyRuleBase):
    id: int

    model_config = {"from_attributes": True}


# --- Palm N Uptake ---
class PalmNUptakeParamBase(BaseModel):
    age_min: int
    age_max: int
    n_per_tffb: float
    vegetative_n_demand: float | None = None
    description: str | None = None


class PalmNUptakeParamCreate(PalmNUptakeParamBase):
    pass


class PalmNUptakeParamUpdate(BaseModel):
    age_min: int | None = None
    age_max: int | None = None
    n_per_tffb: float | None = None
    vegetative_n_demand: float | None = None
    description: str | None = None


class PalmNUptakeParamRead(PalmNUptakeParamBase):
    id: int

    model_config = {"from_attributes": True}


# --- Calculation Methods ---
class CalculationMethodBase(BaseModel):
    flux_type: str
    method_name: str
    description: str | None = None
    formula_reference: str | None = None
    is_default: bool = False


class CalculationMethodCreate(CalculationMethodBase):
    pass


class CalculationMethodRead(CalculationMethodBase):
    id: int

    model_config = {"from_attributes": True}
