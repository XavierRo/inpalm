from datetime import datetime
from pydantic import BaseModel


class FieldBase(BaseModel):
    field_name: str
    localisation: str
    year_planting: int
    end_field: int
    slope: float | None = None
    texture: str | None = None
    organic_carbon: float | None = None
    initial_soil_water: float | None = None
    ph: float | None = None
    cec: float | None = None
    previous_palm: str | None = None
    terraces: str | None = None


class FieldCreate(FieldBase):
    pass


class FieldRead(FieldBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class YearFieldDataRead(BaseModel):
    id: int
    field_id: int
    year: int
    yield_tffb_ha: float | None = None
    understorey_biomass: str | None = None
    legume_fraction: str | None = None
    pruned_frond: str | None = None
    atmospheric_deposition: float | None = None

    model_config = {"from_attributes": True}


class RainfallDataRead(BaseModel):
    id: int
    field_id: int
    year: int
    month: str
    rainfall_mm: float
    rain_frequency: int | None = None
    dataset_name: str

    model_config = {"from_attributes": True}


class FertilizationDataRead(BaseModel):
    id: int
    field_id: int
    year: int
    month: str
    fertilization_type: str
    quantity: float
    unit: str
    composition: str
    placement: str | None = None

    model_config = {"from_attributes": True}


class FieldDetailRead(FieldRead):
    """Parcelle avec toutes ses données associées."""

    year_field_data: list[YearFieldDataRead] = []
    rainfall_data: list[RainfallDataRead] = []
    fertilization_data: list[FertilizationDataRead] = []

    model_config = {"from_attributes": True}
