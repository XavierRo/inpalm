"""Calcul des flux d'entrée d'azote (E1 → E6)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field import Field
from app.models.year_field import YearFieldData
from app.models.fertilization import FertilizationData
from app.models.parameters import FertilizerProperty


async def calc_n_initial_soil(
    db: AsyncSession, field: Field, year: int, palm_age: int
) -> tuple[float, dict]:
    """
    E1 — Azote minéral initial dans le sol.
    Calculé uniquement la première année (année de plantation).
    """
    intermediates = {}

    if palm_age > 0:
        return 0.0, intermediates

    # TODO: Formule à définir avec Cécile
    # Probablement basé sur : organic_carbon, texture, pH, CEC
    # Exemple placeholder :
    n_initial = 0.0
    if field.organic_carbon:
        # Placeholder : relation simplifiée C organique → N minéral
        n_initial = field.organic_carbon * 10.0  # à remplacer

    intermediates["organic_carbon"] = field.organic_carbon
    intermediates["method"] = "placeholder"

    return n_initial, intermediates


async def calc_n_fixation(
    db: AsyncSession, field: Field, year_data: YearFieldData, palm_age: int
) -> tuple[float, dict]:
    """
    E2 — Azote fixé par les légumineuses.
    Utilise la logique floue sur Legume_fraction et Understorey_biomass.
    """
    intermediates = {}

    # TODO: implémenter step4_understorey_fixation (fuzzy)
    n_fixation = 0.0

    intermediates["legume_fraction"] = year_data.legume_fraction
    intermediates["understorey_biomass"] = year_data.understorey_biomass
    intermediates["method"] = "placeholder"

    return n_fixation, intermediates


async def calc_n_residues(
    db: AsyncSession,
    field: Field,
    year_data: YearFieldData,
    palm_age: int,
) -> tuple[float, dict]:
    """
    E3 — Azote des résidus.
    Inclut : résidus de la plantation précédente (année 0)
             + palmes élaguées (chaque année).
    """
    intermediates = {}
    n_residues = 0.0

    # Résidus de la plantation précédente (première année uniquement)
    if palm_age == 0 and field.previous_palm:
        # TODO: Table de correspondance previous_palm → kg N/ha
        # Placeholder
        previous_palm_n = {
            "Shredded left on soil": 50.0,
            "Burned": 5.0,
            "Removed": 0.0,
        }
        n_residues += previous_palm_n.get(field.previous_palm, 0.0)
        intermediates["previous_palm"] = field.previous_palm
        intermediates["previous_palm_n"] = previous_palm_n.get(
            field.previous_palm, 0.0
        )

    # Palmes élaguées
    if year_data.pruned_frond:
        # TODO: Formule à définir — dépend du nombre de palmes, teneur N
        # Placeholder
        pruned_frond_n = 10.0  # kg N/ha/an à remplacer
        n_residues += pruned_frond_n
        intermediates["pruned_frond"] = year_data.pruned_frond
        intermediates["pruned_frond_n"] = pruned_frond_n

    return n_residues, intermediates


async def calc_n_synthetic_fertilizer(
    db: AsyncSession, field: Field, year: int
) -> tuple[float, dict]:
    """
    E4 — Azote des fertilisants synthétiques.
    Somme des apports minéraux sur l'année, convertis en kg N/ha.
    """
    intermediates = {"details": []}

    stmt = select(FertilizationData).where(
        FertilizationData.field_id == field.id,
        FertilizationData.year == year,
        FertilizationData.fertilization_type == "Mineral",
    )
    result = await db.execute(stmt)
    fertilizations = result.scalars().all()

    total_n = 0.0
    for fert in fertilizations:
        # Récupérer les propriétés du fertilisant
        stmt_prop = select(FertilizerProperty).where(
            FertilizerProperty.name == fert.composition
        )
        result_prop = await db.execute(stmt_prop)
        prop = result_prop.scalar_one_or_none()

        if prop:
            # quantity est en kg/ha (pour minéral)
            n_amount = fert.quantity * (prop.n_content / 100.0)
        else:
            # Fallback : urée par défaut (46% N)
            n_amount = fert.quantity * 0.46

        total_n += n_amount
        intermediates["details"].append(
            {
                "month": fert.month,
                "composition": fert.composition,
                "quantity": fert.quantity,
                "unit": fert.unit,
                "n_content_pct": prop.n_content if prop else 46.0,
                "n_amount_kg": n_amount,
                "placement": fert.placement,
            }
        )

    return total_n, intermediates


async def calc_n_organic_fertilizer(
    db: AsyncSession, field: Field, year: int
) -> tuple[float, dict]:
    """
    E5 — Azote des fertilisants organiques.
    Somme des apports organiques sur l'année, convertis en kg N/ha.
    """
    intermediates = {"details": []}

    stmt = select(FertilizationData).where(
        FertilizationData.field_id == field.id,
        FertilizationData.year == year,
        FertilizationData.fertilization_type == "Organic",
    )
    result = await db.execute(stmt)
    fertilizations = result.scalars().all()

    total_n = 0.0
    for fert in fertilizations:
        stmt_prop = select(FertilizerProperty).where(
            FertilizerProperty.name == fert.composition
        )
        result_prop = await db.execute(stmt_prop)
        prop = result_prop.scalar_one_or_none()

        if prop:
            # quantity en tFM/ha → convertir via unit_conversion
            n_amount = fert.quantity * prop.unit_conversion * (prop.n_content / 100.0)
        else:
            # Fallback : compost ~1.5% N, 1 tFM ≈ 1000 kg
            n_amount = fert.quantity * 1000.0 * 0.015

        total_n += n_amount
        intermediates["details"].append(
            {
                "month": fert.month,
                "composition": fert.composition,
                "quantity": fert.quantity,
                "unit": fert.unit,
                "n_amount_kg": n_amount,
            }
        )

    return total_n, intermediates


async def calc_n_atmospheric_deposition(
    year_data: YearFieldData,
) -> tuple[float, dict]:
    """
    E6 — Dépôt atmosphérique d'azote.
    Valeur directement fournie dans les données.
    """
    n_depo = year_data.atmospheric_deposition or 0.0
    return n_depo, {"atmospheric_deposition": n_depo}
