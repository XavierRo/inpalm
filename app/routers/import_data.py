"""Endpoints d'import de fichiers CSV."""

from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.csv_parser import (
    import_field_characteristics,
    import_year_field_data,
    import_rainfall_data,
    import_fertilization_data,
)

router = APIRouter(prefix="/api/import", tags=["Import"])


@router.post("/field")
async def upload_field_characteristics(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Importe un fichier Field_characteristics CSV."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un CSV.")
    content = await file.read()
    result = await import_field_characteristics(db, content)
    return {"message": "Import réussi", **result}


@router.post("/year-field")
async def upload_year_field_data(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Importe un fichier Year_Field_data CSV."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un CSV.")
    content = await file.read()
    result = await import_year_field_data(db, content)
    return {"message": "Import réussi", **result}


@router.post("/rainfall")
async def upload_rainfall_data(
    file: UploadFile = File(...),
    dataset_name: str = Query(default="default", description="Nom du jeu de données météo"),
    db: AsyncSession = Depends(get_db),
):
    """Importe un fichier Rainfall_data CSV avec un nom de dataset."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un CSV.")
    content = await file.read()
    result = await import_rainfall_data(db, content, dataset_name)
    return {"message": "Import réussi", **result}


@router.post("/fertilization")
async def upload_fertilization_data(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Importe un fichier Fertilization_data CSV."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un CSV.")
    content = await file.read()
    result = await import_fertilization_data(db, content)
    return {"message": "Import réussi", **result}
