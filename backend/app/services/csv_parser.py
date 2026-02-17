"""Service de parsing et d'import des fichiers CSV."""

import io
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field import Field
from app.models.year_field import YearFieldData
from app.models.rainfall import RainfallData
from app.models.fertilization import FertilizationData


async def _get_or_create_field(
    db: AsyncSession, field_name: str, localisation: str, extra_data: dict | None = None
) -> Field:
    """Récupère une parcelle existante ou en crée une nouvelle."""
    stmt = select(Field).where(
        Field.field_name == field_name,
        Field.localisation == localisation,
    )
    result = await db.execute(stmt)
    field = result.scalar_one_or_none()

    if field is None:
        field = Field(
            field_name=field_name,
            localisation=localisation,
            year_planting=extra_data.get("year_planting", 0) if extra_data else 0,
            end_field=extra_data.get("end_field", 0) if extra_data else 0,
        )
        db.add(field)
        await db.flush()

    return field


async def import_field_characteristics(
    db: AsyncSession, file_content: bytes
) -> dict[str, Any]:
    """Importe un fichier Field_characteristics CSV."""
    df = pd.read_csv(io.BytesIO(file_content), encoding="utf-8-sig")

    imported = 0
    for _, row in df.iterrows():
        # Vérifier si la parcelle existe déjà
        stmt = select(Field).where(
            Field.field_name == row["Field_name"],
            Field.localisation == row["Localisation"],
        )
        result = await db.execute(stmt)
        field = result.scalar_one_or_none()

        if field:
            # Mise à jour
            field.year_planting = int(row["Year_planting"])
            field.end_field = int(row["End_field"])
            field.slope = float(row["Slope"]) if pd.notna(row.get("Slope")) else None
            field.texture = row.get("Texture")
            field.organic_carbon = (
                float(row["Organic_Carbon"])
                if pd.notna(row.get("Organic_Carbon"))
                else None
            )
            field.initial_soil_water = (
                float(row["Initial_soil_water"])
                if pd.notna(row.get("Initial_soil_water"))
                else None
            )
            field.ph = float(row["PH"]) if pd.notna(row.get("PH")) else None
            field.cec = float(row["CEC"]) if pd.notna(row.get("CEC")) else None
            field.previous_palm = row.get("Previous_palm")
            field.terraces = row.get("Terraces")
        else:
            field = Field(
                field_name=row["Field_name"],
                localisation=row["Localisation"],
                year_planting=int(row["Year_planting"]),
                end_field=int(row["End_field"]),
                slope=float(row["Slope"]) if pd.notna(row.get("Slope")) else None,
                texture=row.get("Texture"),
                organic_carbon=(
                    float(row["Organic_Carbon"])
                    if pd.notna(row.get("Organic_Carbon"))
                    else None
                ),
                initial_soil_water=(
                    float(row["Initial_soil_water"])
                    if pd.notna(row.get("Initial_soil_water"))
                    else None
                ),
                ph=float(row["PH"]) if pd.notna(row.get("PH")) else None,
                cec=float(row["CEC"]) if pd.notna(row.get("CEC")) else None,
                previous_palm=row.get("Previous_palm"),
                terraces=row.get("Terraces"),
            )
            db.add(field)

        imported += 1

    await db.flush()
    return {"imported": imported, "type": "field_characteristics"}


async def import_year_field_data(
    db: AsyncSession, file_content: bytes
) -> dict[str, Any]:
    """Importe un fichier Year_Field_data CSV."""
    df = pd.read_csv(io.BytesIO(file_content), encoding="utf-8-sig")

    imported = 0
    for _, row in df.iterrows():
        field = await _get_or_create_field(
            db, row["Field_name"], row["Localisation"]
        )

        # Vérifier si l'entrée existe déjà
        stmt = select(YearFieldData).where(
            YearFieldData.field_id == field.id,
            YearFieldData.year == int(row["Year"]),
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.yield_tffb_ha = (
                float(row["Yield (tFFB/ha/year)"])
                if pd.notna(row.get("Yield (tFFB/ha/year)"))
                else None
            )
            existing.understorey_biomass = row.get("Understorey_biomass")
            existing.legume_fraction = row.get("Legume_fraction")
            existing.pruned_frond = row.get("Pruned_frond")
            existing.atmospheric_deposition = (
                float(row["Atmospheric_deposition"])
                if pd.notna(row.get("Atmospheric_deposition"))
                else None
            )
        else:
            entry = YearFieldData(
                field_id=field.id,
                year=int(row["Year"]),
                yield_tffb_ha=(
                    float(row["Yield (tFFB/ha/year)"])
                    if pd.notna(row.get("Yield (tFFB/ha/year)"))
                    else None
                ),
                understorey_biomass=row.get("Understorey_biomass"),
                legume_fraction=row.get("Legume_fraction"),
                pruned_frond=row.get("Pruned_frond"),
                atmospheric_deposition=(
                    float(row["Atmospheric_deposition"])
                    if pd.notna(row.get("Atmospheric_deposition"))
                    else None
                ),
            )
            db.add(entry)

        imported += 1

    await db.flush()
    return {"imported": imported, "type": "year_field_data"}


async def import_rainfall_data(
    db: AsyncSession, file_content: bytes, dataset_name: str = "default"
) -> dict[str, Any]:
    """Importe un fichier Rainfall_data CSV."""
    df = pd.read_csv(io.BytesIO(file_content), encoding="utf-8-sig")

    imported = 0
    for _, row in df.iterrows():
        field = await _get_or_create_field(
            db, row["Field_name"], row["Localisation"]
        )

        # Vérifier si l'entrée existe déjà pour ce dataset
        stmt = select(RainfallData).where(
            RainfallData.field_id == field.id,
            RainfallData.year == int(row["Year"]),
            RainfallData.month == row["Month"],
            RainfallData.dataset_name == dataset_name,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.rainfall_mm = float(row["Rainfall(mm)"])
            existing.rain_frequency = (
                int(row["Rain frequency"])
                if pd.notna(row.get("Rain frequency"))
                else None
            )
        else:
            entry = RainfallData(
                field_id=field.id,
                year=int(row["Year"]),
                month=row["Month"],
                rainfall_mm=float(row["Rainfall(mm)"]),
                rain_frequency=(
                    int(row["Rain frequency"])
                    if pd.notna(row.get("Rain frequency"))
                    else None
                ),
                dataset_name=dataset_name,
            )
            db.add(entry)

        imported += 1

    await db.flush()
    return {"imported": imported, "type": "rainfall_data", "dataset_name": dataset_name}


async def import_fertilization_data(
    db: AsyncSession, file_content: bytes
) -> dict[str, Any]:
    """Importe un fichier Fertilization_data CSV."""
    df = pd.read_csv(io.BytesIO(file_content), encoding="utf-8-sig")

    imported = 0
    for _, row in df.iterrows():
        field = await _get_or_create_field(
            db, row["Field_name"], row["Localisation"]
        )

        entry = FertilizationData(
            field_id=field.id,
            year=int(row["Year"]),
            month=row["Month"],
            fertilization_type=row["Fertilization_type"],
            quantity=float(row["Quantity"]),
            unit=row["Unit (per ha)"],
            composition=row["Composition"],
            placement=row.get("Placement"),
        )
        db.add(entry)
        imported += 1

    await db.flush()
    return {"imported": imported, "type": "fertilization_data"}
