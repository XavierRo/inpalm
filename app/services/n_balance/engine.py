"""Orchestrateur du calcul de bilan azoté sur le cycle complet."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field import Field
from app.models.year_field import YearFieldData
from app.models.simulation import Simulation, SimulationOption
from app.models.results import SimulationResultYearly, SimulationResultCycle
from app.models.parameters import CalculationMethod
from app.services.n_balance.inputs import (
    calc_n_initial_soil,
    calc_n_fixation,
    calc_n_residues,
    calc_n_synthetic_fertilizer,
    calc_n_organic_fertilizer,
    calc_n_atmospheric_deposition,
)
from app.services.n_balance.outputs import (
    calc_n_volatilization,
    calc_n_leaching,
    calc_n_palm_uptake,
    calc_n_n2o_emission,
    calc_n_nox_emission,
    calc_n_n2_emission,
    calc_n_runoff,
)


async def _get_method_for_flux(
    db: AsyncSession, simulation: Simulation, flux_type: str
) -> str:
    """Récupère la méthode de calcul choisie pour un flux donné."""
    stmt = (
        select(CalculationMethod.method_name)
        .join(SimulationOption, SimulationOption.method_id == CalculationMethod.id)
        .where(
            SimulationOption.simulation_id == simulation.id,
            SimulationOption.flux_type == flux_type,
        )
    )
    result = await db.execute(stmt)
    method = result.scalar_one_or_none()
    return method or "default"


async def run_simulation(db: AsyncSession, simulation: Simulation) -> None:
    """
    Exécute le calcul du bilan azoté pour une simulation donnée.

    Parcourt chaque année du cycle de la plantation et calcule
    tous les flux d'entrée et de sortie.
    """
    # Mettre à jour le statut
    simulation.status = "running"
    await db.flush()

    try:
        # Récupérer la parcelle
        stmt = select(Field).where(Field.id == simulation.field_id)
        result = await db.execute(stmt)
        field = result.scalar_one()

        # Récupérer les données annuelles
        stmt = (
            select(YearFieldData)
            .where(YearFieldData.field_id == field.id)
            .order_by(YearFieldData.year)
        )
        result = await db.execute(stmt)
        yearly_data = result.scalars().all()

        if not yearly_data:
            simulation.status = "error"
            await db.flush()
            return

        # Récupérer les méthodes de calcul choisies
        methods = {
            "volatilization": await _get_method_for_flux(
                db, simulation, "volatilization"
            ),
            "leaching": await _get_method_for_flux(db, simulation, "leaching"),
            "n2o": await _get_method_for_flux(db, simulation, "n2o"),
            "nox": await _get_method_for_flux(db, simulation, "nox"),
            "n2": await _get_method_for_flux(db, simulation, "n2"),
            "runoff": await _get_method_for_flux(db, simulation, "runoff"),
            "palm_uptake": await _get_method_for_flux(db, simulation, "palm_uptake"),
        }

        # Accumulateurs pour le cycle complet
        cycle_inputs = {
            "n_initial_soil": 0.0,
            "n_fixation": 0.0,
            "n_residues": 0.0,
            "n_synthetic_fertilizer": 0.0,
            "n_organic_fertilizer": 0.0,
            "n_atmospheric_deposition": 0.0,
        }
        cycle_outputs = {
            "n_volatilization": 0.0,
            "n_leaching": 0.0,
            "n_palm_uptake": 0.0,
            "n_n2o_emission": 0.0,
            "n_nox_emission": 0.0,
            "n_n2_emission": 0.0,
            "n_runoff": 0.0,
        }

        yearly_results = []

        for year_data in yearly_data:
            year = year_data.year
            palm_age = year - field.year_planting
            intermediates = {}

            # ===== ENTRÉES =====
            n_initial, inter = await calc_n_initial_soil(db, field, year, palm_age)
            intermediates["n_initial_soil"] = inter

            n_fixation, inter = await calc_n_fixation(db, field, year_data, palm_age)
            intermediates["n_fixation"] = inter

            n_residues, inter = await calc_n_residues(db, field, year_data, palm_age)
            intermediates["n_residues"] = inter

            n_synthetic, inter = await calc_n_synthetic_fertilizer(db, field, year)
            intermediates["n_synthetic_fertilizer"] = inter

            n_organic, inter = await calc_n_organic_fertilizer(db, field, year)
            intermediates["n_organic_fertilizer"] = inter

            n_atm_depo, inter = await calc_n_atmospheric_deposition(year_data)
            intermediates["n_atmospheric_deposition"] = inter

            total_inputs = (
                n_initial
                + n_fixation
                + n_residues
                + n_synthetic
                + n_organic
                + n_atm_depo
            )

            # ===== SORTIES =====
            n_vol, inter = await calc_n_volatilization(
                db, field, year, n_synthetic, n_organic, methods["volatilization"]
            )
            intermediates["n_volatilization"] = inter

            n_leach, inter = await calc_n_leaching(
                db,
                field,
                year,
                total_inputs,
                simulation.rainfall_dataset,
                methods["leaching"],
            )
            intermediates["n_leaching"] = inter

            n_uptake, inter = await calc_n_palm_uptake(
                db, field, year_data, palm_age, methods["palm_uptake"]
            )
            intermediates["n_palm_uptake"] = inter

            n_n2o, inter = await calc_n_n2o_emission(
                db,
                field,
                year,
                n_synthetic,
                n_organic,
                n_residues,
                methods["n2o"],
            )
            intermediates["n_n2o_emission"] = inter

            n_nox, inter = await calc_n_nox_emission(
                db, field, n_synthetic, n_organic, methods["nox"]
            )
            intermediates["n_nox_emission"] = inter

            n_n2, inter = await calc_n_n2_emission(
                db, field, n_synthetic, n_organic, methods["n2"]
            )
            intermediates["n_n2_emission"] = inter

            n_runoff, inter = await calc_n_runoff(
                db,
                field,
                year,
                total_inputs,
                year_data,
                simulation.rainfall_dataset,
                methods["runoff"],
            )
            intermediates["n_runoff"] = inter

            total_outputs = (
                n_vol + n_leach + n_uptake + n_n2o + n_nox + n_n2 + n_runoff
            )
            balance = total_inputs - total_outputs

            # Créer le résultat annuel
            yearly_result = SimulationResultYearly(
                simulation_id=simulation.id,
                year=year,
                palm_age=palm_age,
                # Entrées
                n_initial_soil=round(n_initial, 4),
                n_fixation=round(n_fixation, 4),
                n_residues=round(n_residues, 4),
                n_synthetic_fertilizer=round(n_synthetic, 4),
                n_organic_fertilizer=round(n_organic, 4),
                n_atmospheric_deposition=round(n_atm_depo, 4),
                total_inputs=round(total_inputs, 4),
                # Sorties
                n_volatilization=round(n_vol, 4),
                n_leaching=round(n_leach, 4),
                n_palm_uptake=round(n_uptake, 4),
                n_n2o_emission=round(n_n2o, 4),
                n_nox_emission=round(n_nox, 4),
                n_n2_emission=round(n_n2, 4),
                n_runoff=round(n_runoff, 4),
                total_outputs=round(total_outputs, 4),
                # Bilan
                balance=round(balance, 4),
                intermediate_results=intermediates,
            )
            db.add(yearly_result)
            yearly_results.append(yearly_result)

            # Accumuler pour le cycle
            cycle_inputs["n_initial_soil"] += n_initial
            cycle_inputs["n_fixation"] += n_fixation
            cycle_inputs["n_residues"] += n_residues
            cycle_inputs["n_synthetic_fertilizer"] += n_synthetic
            cycle_inputs["n_organic_fertilizer"] += n_organic
            cycle_inputs["n_atmospheric_deposition"] += n_atm_depo

            cycle_outputs["n_volatilization"] += n_vol
            cycle_outputs["n_leaching"] += n_leach
            cycle_outputs["n_palm_uptake"] += n_uptake
            cycle_outputs["n_n2o_emission"] += n_n2o
            cycle_outputs["n_nox_emission"] += n_nox
            cycle_outputs["n_n2_emission"] += n_n2
            cycle_outputs["n_runoff"] += n_runoff

        # Résultat cycle complet
        total_cycle_inputs = sum(cycle_inputs.values())
        total_cycle_outputs = sum(cycle_outputs.values())
        total_cycle_balance = total_cycle_inputs - total_cycle_outputs

        cycle_result = SimulationResultCycle(
            simulation_id=simulation.id,
            total_n_inputs=round(total_cycle_inputs, 4),
            total_n_outputs=round(total_cycle_outputs, 4),
            total_balance=round(total_cycle_balance, 4),
            summary={
                "inputs": {k: round(v, 4) for k, v in cycle_inputs.items()},
                "outputs": {k: round(v, 4) for k, v in cycle_outputs.items()},
                "years_count": len(yearly_data),
                "methods": methods,
            },
        )
        db.add(cycle_result)

        simulation.status = "completed"
        await db.flush()

    except Exception as e:
        simulation.status = "error"
        await db.flush()
        raise e
