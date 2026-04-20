"""Calcul des flux de sortie d'azote (S1 → S7)."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field import Field
from app.models.year_field import YearFieldData
from app.models.rainfall import RainfallData
from app.models.fertilization import FertilizationData
from app.models.parameters import (
    VolatilizationParam,
    EmissionFactor,
    LeachingParam,
    PalmNUptakeParam,
)


async def calc_n_volatilization(
    db: AsyncSession,
    field: Field,
    year: int,
    n_synthetic: float,
    n_organic: float,
    method: str = "default",
) -> tuple[float, dict]:
    """
    S1 — Volatilisation NH₃.
    Dépend du type de fertilisant, du placement, et des conditions.
    """
    intermediates = {"method": method, "details": []}

    # Récupérer les événements de fertilisation de l'année
    stmt = select(FertilizationData).where(
        FertilizationData.field_id == field.id,
        FertilizationData.year == year,
    )
    result = await db.execute(stmt)
    fertilizations = result.scalars().all()

    total_volatilized = 0.0

    for fert in fertilizations:
        # Chercher le taux de volatilisation correspondant
        stmt_vol = select(VolatilizationParam).where(
            VolatilizationParam.fertilizer_name == fert.composition,
            VolatilizationParam.placement == fert.placement,
        )
        result_vol = await db.execute(stmt_vol)
        vol_param = result_vol.scalar_one_or_none()

        if vol_param:
            rate = vol_param.base_rate
            # TODO: Ajustements pH, température à implémenter
        else:
            # Fallback : taux par défaut
            rate = 0.10 if fert.fertilization_type == "Mineral" else 0.05

        # TODO: Calculer la quantité N de cet apport (réutiliser inputs)
        # Placeholder simplifié
        if fert.fertilization_type == "Mineral":
            n_applied = fert.quantity * 0.46  # Urée
        else:
            n_applied = fert.quantity * 1000.0 * 0.015  # Compost

        n_vol = n_applied * rate
        total_volatilized += n_vol

        intermediates["details"].append(
            {
                "month": fert.month,
                "composition": fert.composition,
                "placement": fert.placement,
                "rate": rate,
                "n_applied": n_applied,
                "n_volatilized": n_vol,
            }
        )

    return total_volatilized, intermediates


async def calc_n_leaching(
    db: AsyncSession,
    field: Field,
    year: int,
    total_n_inputs: float,
    rainfall_dataset: str = "default",
    method: str = "default",
) -> tuple[float, dict]:
    """
    S2 — Lessivage NO₃⁻.
    Dépend de la pluviométrie, texture du sol, pente, terrasses.
    """
    intermediates = {"method": method}

    # Pluviométrie annuelle
    stmt = select(func.sum(RainfallData.rainfall_mm)).where(
        RainfallData.field_id == field.id,
        RainfallData.year == year,
        RainfallData.dataset_name == rainfall_dataset,
    )
    result = await db.execute(stmt)
    annual_rainfall = result.scalar() or 0.0
    intermediates["annual_rainfall_mm"] = annual_rainfall

    # Récupérer les paramètres de lessivage
    stmt_leach = select(LeachingParam).where(
        LeachingParam.texture == field.texture,
    )
    result_leach = await db.execute(stmt_leach)
    leach_param = result_leach.scalar_one_or_none()

    if leach_param:
        base_fraction = leach_param.base_leaching_fraction
        rainfall_coeff = leach_param.rainfall_coefficient or 1.0
    else:
        # Fallback
        base_fraction = 0.30  # 30% IPCC default
        rainfall_coeff = 1.0

    # TODO: Formule complète à définir avec Cécile
    # Placeholder : fraction simple × ajustement pluviométrie
    rainfall_factor = min(annual_rainfall / 2000.0, 2.0)  # normalisation
    n_leached = total_n_inputs * base_fraction * rainfall_factor * rainfall_coeff

    intermediates["base_fraction"] = base_fraction
    intermediates["rainfall_factor"] = rainfall_factor
    intermediates["n_leached"] = n_leached

    return n_leached, intermediates


async def calc_n_palm_uptake(
    db: AsyncSession,
    field: Field,
    year_data: YearFieldData,
    palm_age: int,
    method: str = "default",
) -> tuple[float, dict]:
    """
    S3 — Captation N par les palmiers.
    Dépend du rendement (tFFB/ha) et de l'âge de la plantation.
    """
    intermediates = {"method": method}

    # Récupérer les paramètres pour cet âge (palm_age exact)
    stmt = select(PalmNUptakeParam).where(PalmNUptakeParam.palm_age == palm_age)
    result = await db.execute(stmt)
    uptake_param = result.scalar_one_or_none()

    yield_tffb = year_data.yield_tffb_ha or 0.0

    if uptake_param:
        # TODO: calcul fuzzy réel (step4_palm_uptake) — placeholder linéaire
        mid_uptake = (uptake_param.n_uptake_low + uptake_param.n_uptake_high) / 2.0
        n_uptake = mid_uptake
    else:
        # Fallback : valeur typique palmier à huile
        n_uptake = 80.0  # kg N/ha/an

    intermediates["yield_tffb_ha"] = yield_tffb
    intermediates["palm_age"] = palm_age
    intermediates["n_uptake"] = n_uptake

    return n_uptake, intermediates


async def calc_n_n2o_emission(
    db: AsyncSession,
    field: Field,
    year: int,
    n_synthetic: float,
    n_organic: float,
    n_residues: float,
    method: str = "default",
) -> tuple[float, dict]:
    """
    S4 — Émissions N₂O par nitrification et dénitrification.
    """
    intermediates = {"method": method}

    # Récupérer le facteur d'émission
    stmt = select(EmissionFactor).where(
        EmissionFactor.flux_type == "N2O",
        EmissionFactor.method == method,
    )
    result = await db.execute(stmt)
    factors = result.scalars().all()

    # TODO: Méthode de calcul spécifique à définir
    # Placeholder : facteur IPCC Tier 1 simplifié
    n_n2o = 0.0

    # Facteur par source
    factor_map = {f.source: f.factor_value for f in factors}

    ef_synthetic = factor_map.get("synthetic", 0.01)  # 1% IPCC default
    ef_organic = factor_map.get("organic", 0.01)
    ef_residues = factor_map.get("residues", 0.01)

    n_n2o = (
        n_synthetic * ef_synthetic
        + n_organic * ef_organic
        + n_residues * ef_residues
    )

    intermediates["ef_synthetic"] = ef_synthetic
    intermediates["ef_organic"] = ef_organic
    intermediates["ef_residues"] = ef_residues
    intermediates["n_n2o"] = n_n2o

    return n_n2o, intermediates


async def calc_n_nox_emission(
    db: AsyncSession,
    field: Field,
    n_synthetic: float,
    n_organic: float,
    method: str = "default",
) -> tuple[float, dict]:
    """
    S5 — Émissions NOx par nitrification et dénitrification.
    """
    intermediates = {"method": method}

    # TODO: Formule spécifique à définir
    # Placeholder
    ef_nox = 0.001  # à remplacer
    n_nox = (n_synthetic + n_organic) * ef_nox

    intermediates["ef_nox"] = ef_nox
    intermediates["n_nox"] = n_nox

    return n_nox, intermediates


async def calc_n_n2_emission(
    db: AsyncSession,
    field: Field,
    n_synthetic: float,
    n_organic: float,
    method: str = "default",
) -> tuple[float, dict]:
    """
    S6 — Émissions N₂ par dénitrification.
    """
    intermediates = {"method": method}

    # TODO: Formule spécifique à définir
    # Placeholder
    ef_n2 = 0.005  # à remplacer
    n_n2 = (n_synthetic + n_organic) * ef_n2

    intermediates["ef_n2"] = ef_n2
    intermediates["n_n2"] = n_n2

    return n_n2, intermediates


async def calc_n_runoff(
    db: AsyncSession,
    field: Field,
    year: int,
    total_n_inputs: float,
    year_data: YearFieldData,
    rainfall_dataset: str = "default",
    method: str = "default",
) -> tuple[float, dict]:
    """
    S7 — Azote perdu par ruissellement.
    Dépend de la pente, pluviométrie, terrasses, couverture du sol.
    """
    intermediates = {"method": method}

    # Pluviométrie annuelle
    from sqlalchemy import func as sqlfunc

    stmt = select(sqlfunc.sum(RainfallData.rainfall_mm)).where(
        RainfallData.field_id == field.id,
        RainfallData.year == year,
        RainfallData.dataset_name == rainfall_dataset,
    )
    result = await db.execute(stmt)
    annual_rainfall = result.scalar() or 0.0

    # TODO: Formule spécifique à définir
    # Placeholder basé sur pente et pluviométrie
    slope = field.slope or 0.0
    has_terraces = field.terraces == "Yes"

    # Facteur pente
    slope_factor = slope / 100.0  # simplification

    # Facteur terrasses
    terrace_factor = 0.3 if has_terraces else 1.0

    # Facteur pluviométrie
    rainfall_factor = min(annual_rainfall / 2000.0, 2.0)

    n_runoff = total_n_inputs * 0.05 * slope_factor * terrace_factor * rainfall_factor

    intermediates["slope"] = slope
    intermediates["has_terraces"] = has_terraces
    intermediates["annual_rainfall_mm"] = annual_rainfall
    intermediates["slope_factor"] = slope_factor
    intermediates["terrace_factor"] = terrace_factor
    intermediates["rainfall_factor"] = rainfall_factor
    intermediates["n_runoff"] = n_runoff

    return n_runoff, intermediates
