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


# --- Fuzzy Module (lecture seule — registre des 11 modules IN-Palm) ---
class FuzzyModuleRead(BaseModel):
    id: int
    module_code: str
    module_name: str
    step: int
    report_section: str | None = None
    output_unit: str | None = None
    output_min: float | None = None
    output_max: float | None = None
    reference: str | None = None
    description: str | None = None

    model_config = {"from_attributes": True}


# --- Fuzzy Factor (limites F/U paramétrables) ---
class FuzzyFactorRead(BaseModel):
    id: int
    module_code: str
    factor_name: str
    label: str | None = None
    unit: str | None = None
    unfav_limit: float
    fav_limit: float
    factor_order: int
    is_intermediate: bool
    reference: str | None = None

    model_config = {"from_attributes": True}


class FuzzyFactorUpdate(BaseModel):
    unfav_limit: float | None = None
    fav_limit: float | None = None


# --- Fuzzy Rule (conclusion paramétrable, conditions immuables) ---
class FuzzyRuleRead(BaseModel):
    id: int
    module_code: str
    rule_number: int
    conditions: dict
    conclusion: float
    conclusion_label: str | None = None
    reference: str | None = None

    model_config = {"from_attributes": True}


class FuzzyRuleUpdate(BaseModel):
    conclusion: float


# --- Fuzzy Nominal Conversion (valeur numérique paramétrable) ---
class FuzzyNominalConversionRead(BaseModel):
    id: int
    module_code: str
    factor_name: str
    nominal_value: str
    numeric_value: float
    reference: str | None = None

    model_config = {"from_attributes": True}


class FuzzyNominalConversionUpdate(BaseModel):
    numeric_value: float


# --- Palm N Uptake (schéma IN-Palm, Pardon 2019 §3 Module 4.1) ---
class PalmNUptakeParamBase(BaseModel):
    palm_age: int
    yield_unfav_limit: float
    yield_fav_limit: float
    n_uptake_low: float
    n_uptake_high: float
    description: str | None = None


class PalmNUptakeParamCreate(PalmNUptakeParamBase):
    pass


class PalmNUptakeParamUpdate(BaseModel):
    yield_unfav_limit: float | None = None
    yield_fav_limit: float | None = None
    n_uptake_low: float | None = None
    n_uptake_high: float | None = None
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
