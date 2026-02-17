"""Endpoints CRUD pour les parcelles."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.field import Field
from app.schemas.field import FieldRead, FieldDetailRead

router = APIRouter(prefix="/api/fields", tags=["Fields"])


@router.get("/", response_model=list[FieldRead])
async def list_fields(db: AsyncSession = Depends(get_db)):
    """Liste toutes les parcelles."""
    stmt = select(Field).order_by(Field.field_name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{field_id}", response_model=FieldDetailRead)
async def get_field(field_id: int, db: AsyncSession = Depends(get_db)):
    """Détail d'une parcelle avec toutes ses données associées."""
    stmt = (
        select(Field)
        .where(Field.id == field_id)
        .options(
            selectinload(Field.year_field_data),
            selectinload(Field.rainfall_data),
            selectinload(Field.fertilization_data),
        )
    )
    result = await db.execute(stmt)
    field = result.scalar_one_or_none()

    if not field:
        raise HTTPException(status_code=404, detail="Parcelle non trouvée")

    return field


@router.delete("/{field_id}")
async def delete_field(field_id: int, db: AsyncSession = Depends(get_db)):
    """Supprime une parcelle et toutes ses données associées."""
    stmt = select(Field).where(Field.id == field_id)
    result = await db.execute(stmt)
    field = result.scalar_one_or_none()

    if not field:
        raise HTTPException(status_code=404, detail="Parcelle non trouvée")

    await db.delete(field)
    return {"message": f"Parcelle {field.field_name} supprimée"}
