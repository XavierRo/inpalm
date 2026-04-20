"""Endpoints CRUD pour les tables de paramétrage."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.parameters import (
    FertilizerProperty,
    VolatilizationParam,
    EmissionFactor,
    LeachingParam,
    PalmNUptakeParam,
    CalculationMethod,
    FuzzyModule,
    FuzzyFactor,
    FuzzyRule,
    FuzzyNominalConversion,
)
from app.schemas.parameters import (
    FertilizerPropertyCreate,
    FertilizerPropertyUpdate,
    FertilizerPropertyRead,
    EmissionFactorCreate,
    EmissionFactorUpdate,
    EmissionFactorRead,
    VolatilizationParamCreate,
    VolatilizationParamUpdate,
    VolatilizationParamRead,
    LeachingParamCreate,
    LeachingParamUpdate,
    LeachingParamRead,
    PalmNUptakeParamCreate,
    PalmNUptakeParamUpdate,
    PalmNUptakeParamRead,
    CalculationMethodCreate,
    CalculationMethodRead,
    FuzzyModuleRead,
    FuzzyFactorRead,
    FuzzyFactorUpdate,
    FuzzyRuleRead,
    FuzzyRuleUpdate,
    FuzzyNominalConversionRead,
    FuzzyNominalConversionUpdate,
)

router = APIRouter(prefix="/api/parameters", tags=["Parameters"])


# ===================== Fertilizer Properties =====================


@router.get("/fertilizers", response_model=list[FertilizerPropertyRead])
async def list_fertilizers(db: AsyncSession = Depends(get_db)):
    stmt = select(FertilizerProperty).order_by(FertilizerProperty.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/fertilizers", response_model=FertilizerPropertyRead)
async def create_fertilizer(
    data: FertilizerPropertyCreate, db: AsyncSession = Depends(get_db)
):
    obj = FertilizerProperty(**data.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.put("/fertilizers/{item_id}", response_model=FertilizerPropertyRead)
async def update_fertilizer(
    item_id: int, data: FertilizerPropertyUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(FertilizerProperty).where(FertilizerProperty.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Fertilisant non trouvé")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.delete("/fertilizers/{item_id}")
async def delete_fertilizer(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(FertilizerProperty).where(FertilizerProperty.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Fertilisant non trouvé")
    await db.delete(obj)
    return {"message": "Supprimé"}


# ===================== Emission Factors =====================


@router.get("/emission-factors", response_model=list[EmissionFactorRead])
async def list_emission_factors(db: AsyncSession = Depends(get_db)):
    stmt = select(EmissionFactor).order_by(
        EmissionFactor.flux_type, EmissionFactor.source
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/emission-factors", response_model=EmissionFactorRead)
async def create_emission_factor(
    data: EmissionFactorCreate, db: AsyncSession = Depends(get_db)
):
    obj = EmissionFactor(**data.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.put("/emission-factors/{item_id}", response_model=EmissionFactorRead)
async def update_emission_factor(
    item_id: int, data: EmissionFactorUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(EmissionFactor).where(EmissionFactor.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Facteur d'émission non trouvé")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.flush()
    await db.refresh(obj)
    return obj


# ===================== Volatilization Params =====================


@router.get("/volatilization", response_model=list[VolatilizationParamRead])
async def list_volatilization_params(db: AsyncSession = Depends(get_db)):
    stmt = select(VolatilizationParam)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/volatilization", response_model=VolatilizationParamRead)
async def create_volatilization_param(
    data: VolatilizationParamCreate, db: AsyncSession = Depends(get_db)
):
    obj = VolatilizationParam(**data.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.put("/volatilization/{item_id}", response_model=VolatilizationParamRead)
async def update_volatilization_param(
    item_id: int, data: VolatilizationParamUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(VolatilizationParam).where(VolatilizationParam.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.flush()
    await db.refresh(obj)
    return obj


# ===================== Leaching Params =====================


@router.get("/leaching", response_model=list[LeachingParamRead])
async def list_leaching_params(db: AsyncSession = Depends(get_db)):
    stmt = select(LeachingParam)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/leaching", response_model=LeachingParamRead)
async def create_leaching_param(
    data: LeachingParamCreate, db: AsyncSession = Depends(get_db)
):
    obj = LeachingParam(**data.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.put("/leaching/{item_id}", response_model=LeachingParamRead)
async def update_leaching_param(
    item_id: int, data: LeachingParamUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(LeachingParam).where(LeachingParam.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.flush()
    await db.refresh(obj)
    return obj


# ===================== Fuzzy Modules (lecture seule) =====================


@router.get("/fuzzy/modules", response_model=list[FuzzyModuleRead])
async def list_fuzzy_modules(db: AsyncSession = Depends(get_db)):
    stmt = select(FuzzyModule).order_by(FuzzyModule.step, FuzzyModule.module_code)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/fuzzy/modules/{module_code}", response_model=FuzzyModuleRead)
async def get_fuzzy_module(module_code: str, db: AsyncSession = Depends(get_db)):
    stmt = select(FuzzyModule).where(FuzzyModule.module_code == module_code)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Module fuzzy non trouvé")
    return obj


# ===================== Fuzzy Factors (limites F/U paramétrables) =====================


@router.get("/fuzzy/factors", response_model=list[FuzzyFactorRead])
async def list_fuzzy_factors(
    module_code: str | None = None, db: AsyncSession = Depends(get_db)
):
    stmt = select(FuzzyFactor).order_by(FuzzyFactor.module_code, FuzzyFactor.factor_order)
    if module_code:
        stmt = stmt.where(FuzzyFactor.module_code == module_code)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/fuzzy/factors/{item_id}", response_model=FuzzyFactorRead)
async def update_fuzzy_factor(
    item_id: int, data: FuzzyFactorUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(FuzzyFactor).where(FuzzyFactor.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Facteur fuzzy non trouvé")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.flush()
    await db.refresh(obj)
    return obj


# ===================== Fuzzy Rules (conclusion paramétrable) =====================


@router.get("/fuzzy/rules", response_model=list[FuzzyRuleRead])
async def list_fuzzy_rules(
    module_code: str | None = None, db: AsyncSession = Depends(get_db)
):
    stmt = select(FuzzyRule).order_by(FuzzyRule.module_code, FuzzyRule.rule_number)
    if module_code:
        stmt = stmt.where(FuzzyRule.module_code == module_code)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/fuzzy/rules/{item_id}", response_model=FuzzyRuleRead)
async def update_fuzzy_rule(
    item_id: int, data: FuzzyRuleUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(FuzzyRule).where(FuzzyRule.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Règle fuzzy non trouvée")
    obj.conclusion = data.conclusion
    await db.flush()
    await db.refresh(obj)
    return obj


# ===================== Fuzzy Nominal Conversions (valeur numérique paramétrable) =====================


@router.get("/fuzzy/nominal-conversions", response_model=list[FuzzyNominalConversionRead])
async def list_fuzzy_nominal_conversions(
    module_code: str | None = None, db: AsyncSession = Depends(get_db)
):
    stmt = select(FuzzyNominalConversion).order_by(
        FuzzyNominalConversion.module_code,
        FuzzyNominalConversion.factor_name,
        FuzzyNominalConversion.nominal_value,
    )
    if module_code:
        stmt = stmt.where(FuzzyNominalConversion.module_code == module_code)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/fuzzy/nominal-conversions/{item_id}", response_model=FuzzyNominalConversionRead)
async def update_fuzzy_nominal_conversion(
    item_id: int, data: FuzzyNominalConversionUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(FuzzyNominalConversion).where(FuzzyNominalConversion.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Conversion nominale non trouvée")
    obj.numeric_value = data.numeric_value
    await db.flush()
    await db.refresh(obj)
    return obj


# ===================== Palm N Uptake =====================


@router.get("/palm-uptake", response_model=list[PalmNUptakeParamRead])
async def list_palm_uptake_params(db: AsyncSession = Depends(get_db)):
    stmt = select(PalmNUptakeParam).order_by(PalmNUptakeParam.palm_age)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/palm-uptake", response_model=PalmNUptakeParamRead)
async def create_palm_uptake_param(
    data: PalmNUptakeParamCreate, db: AsyncSession = Depends(get_db)
):
    obj = PalmNUptakeParam(**data.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.put("/palm-uptake/{item_id}", response_model=PalmNUptakeParamRead)
async def update_palm_uptake_param(
    item_id: int, data: PalmNUptakeParamUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(PalmNUptakeParam).where(PalmNUptakeParam.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.flush()
    await db.refresh(obj)
    return obj


# ===================== Calculation Methods =====================


@router.get("/methods", response_model=list[CalculationMethodRead])
async def list_methods(db: AsyncSession = Depends(get_db)):
    stmt = select(CalculationMethod).order_by(
        CalculationMethod.flux_type, CalculationMethod.method_name
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/methods", response_model=CalculationMethodRead)
async def create_method(
    data: CalculationMethodCreate, db: AsyncSession = Depends(get_db)
):
    obj = CalculationMethod(**data.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj
