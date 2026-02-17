"""Endpoints pour la gestion et l'exécution des simulations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.simulation import Simulation, SimulationOption, SimulationOverride
from app.models.results import SimulationResultYearly, SimulationResultCycle
from app.schemas.simulation import (
    SimulationCreate,
    SimulationRead,
    SimulationListRead,
    SimulationResultsRead,
    YearlyResultRead,
    CycleResultRead,
)
from app.services.n_balance.engine import run_simulation

router = APIRouter(prefix="/api/simulations", tags=["Simulations"])


@router.get("/", response_model=list[SimulationListRead])
async def list_simulations(db: AsyncSession = Depends(get_db)):
    """Liste toutes les simulations."""
    stmt = select(Simulation).order_by(Simulation.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=SimulationRead)
async def create_simulation(
    data: SimulationCreate, db: AsyncSession = Depends(get_db)
):
    """Crée et lance une nouvelle simulation."""
    # Créer la simulation
    simulation = Simulation(
        name=data.name,
        field_id=data.field_id,
        rainfall_dataset=data.rainfall_dataset,
        description=data.description,
    )
    db.add(simulation)
    await db.flush()

    # Ajouter les options de méthode
    for opt in data.options:
        option = SimulationOption(
            simulation_id=simulation.id,
            flux_type=opt.flux_type,
            method_id=opt.method_id,
        )
        db.add(option)

    # Ajouter les overrides
    for ovr in data.overrides:
        override = SimulationOverride(
            simulation_id=simulation.id,
            param_table=ovr.param_table,
            param_id=ovr.param_id,
            param_field=ovr.param_field,
            override_value=ovr.override_value,
        )
        db.add(override)

    await db.flush()

    # Lancer le calcul
    await run_simulation(db, simulation)

    await db.refresh(simulation)
    return simulation


@router.get("/{simulation_id}", response_model=SimulationRead)
async def get_simulation(simulation_id: str, db: AsyncSession = Depends(get_db)):
    """Détail d'une simulation."""
    stmt = select(Simulation).where(Simulation.id == simulation_id)
    result = await db.execute(stmt)
    simulation = result.scalar_one_or_none()

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation non trouvée")

    return simulation


@router.get("/{simulation_id}/results", response_model=SimulationResultsRead)
async def get_simulation_results(
    simulation_id: str, db: AsyncSession = Depends(get_db)
):
    """Résultats complets d'une simulation (annuels + cycle)."""
    # Simulation
    stmt = select(Simulation).where(Simulation.id == simulation_id)
    result = await db.execute(stmt)
    simulation = result.scalar_one_or_none()

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation non trouvée")

    if simulation.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"La simulation n'est pas terminée (statut: {simulation.status})",
        )

    # Résultats annuels
    stmt = (
        select(SimulationResultYearly)
        .where(SimulationResultYearly.simulation_id == simulation_id)
        .order_by(SimulationResultYearly.year)
    )
    result = await db.execute(stmt)
    yearly = result.scalars().all()

    # Résultat cycle
    stmt = select(SimulationResultCycle).where(
        SimulationResultCycle.simulation_id == simulation_id
    )
    result = await db.execute(stmt)
    cycle = result.scalar_one_or_none()

    return SimulationResultsRead(
        simulation=SimulationRead.model_validate(simulation),
        yearly_results=[YearlyResultRead.model_validate(y) for y in yearly],
        cycle_result=CycleResultRead.model_validate(cycle) if cycle else None,
    )


@router.delete("/{simulation_id}")
async def delete_simulation(simulation_id: str, db: AsyncSession = Depends(get_db)):
    """Supprime une simulation et ses résultats."""
    stmt = select(Simulation).where(Simulation.id == simulation_id)
    result = await db.execute(stmt)
    simulation = result.scalar_one_or_none()

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation non trouvée")

    await db.delete(simulation)
    return {"message": f"Simulation '{simulation.name}' supprimée"}
