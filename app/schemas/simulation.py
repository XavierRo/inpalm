from datetime import datetime
from pydantic import BaseModel


# --- Simulation ---
class SimulationOverrideCreate(BaseModel):
    param_table: str
    param_id: int
    param_field: str
    override_value: float


class SimulationOptionCreate(BaseModel):
    flux_type: str
    method_id: int


class SimulationCreate(BaseModel):
    name: str
    field_id: int
    rainfall_dataset: str = "default"
    description: str | None = None
    options: list[SimulationOptionCreate] = []
    overrides: list[SimulationOverrideCreate] = []


class SimulationRead(BaseModel):
    id: str
    name: str
    field_id: int
    rainfall_dataset: str
    description: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SimulationListRead(BaseModel):
    id: str
    name: str
    field_id: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Results ---
class YearlyResultRead(BaseModel):
    year: int
    palm_age: int
    # Entrées
    n_initial_soil: float
    n_fixation: float
    n_residues: float
    n_synthetic_fertilizer: float
    n_organic_fertilizer: float
    n_atmospheric_deposition: float
    total_inputs: float
    # Sorties
    n_volatilization: float
    n_leaching: float
    n_palm_uptake: float
    n_n2o_emission: float
    n_nox_emission: float
    n_n2_emission: float
    n_runoff: float
    total_outputs: float
    # Bilan
    balance: float
    intermediate_results: dict | None = None

    model_config = {"from_attributes": True}


class CycleResultRead(BaseModel):
    total_n_inputs: float
    total_n_outputs: float
    total_balance: float
    summary: dict | None = None

    model_config = {"from_attributes": True}


class SimulationResultsRead(BaseModel):
    simulation: SimulationRead
    yearly_results: list[YearlyResultRead]
    cycle_result: CycleResultRead | None = None
