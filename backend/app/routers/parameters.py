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
    FuzzyMembership,
    FuzzyRule,
    PalmNUptakeParam,
    CalculationMethod,
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
    FuzzyMembershipCreate,
    FuzzyMembershipUpdate,
    FuzzyMembershipRead,
    FuzzyRuleCreate,
    FuzzyRuleRead,
    PalmNUptakeParamCreate,
    PalmNUptakeParamUpdate,
    PalmNUptakeParamRead,
    CalculationMethodCreate,
    CalculationMethodRead,
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


# ===================== Fuzzy Membership =====================


@router.get("/fuzzy/membership", response_model=list[FuzzyMembershipRead])
async def list_fuzzy_memberships(db: AsyncSession = Depends(get_db)):
    stmt = select(FuzzyMembership).order_by(
        FuzzyMembership.variable_name, FuzzyMembership.linguistic_value
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/fuzzy/membership", response_model=FuzzyMembershipRead)
async def create_fuzzy_membership(
    data: FuzzyMembershipCreate, db: AsyncSession = Depends(get_db)
):
    obj = FuzzyMembership(**data.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.put("/fuzzy/membership/{item_id}", response_model=FuzzyMembershipRead)
async def update_fuzzy_membership(
    item_id: int, data: FuzzyMembershipUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(FuzzyMembership).where(FuzzyMembership.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Membership non trouvée")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    await db.flush()
    await db.refresh(obj)
    return obj


# ===================== Fuzzy Rules =====================


@router.get("/fuzzy/rules", response_model=list[FuzzyRuleRead])
async def list_fuzzy_rules(db: AsyncSession = Depends(get_db)):
    stmt = select(FuzzyRule).order_by(FuzzyRule.rule_set_name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/fuzzy/rules", response_model=FuzzyRuleRead)
async def create_fuzzy_rule(
    data: FuzzyRuleCreate, db: AsyncSession = Depends(get_db)
):
    obj = FuzzyRule(**data.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.delete("/fuzzy/rules/{item_id}")
async def delete_fuzzy_rule(item_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(FuzzyRule).where(FuzzyRule.id == item_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Règle non trouvée")
    await db.delete(obj)
    return {"message": "Supprimée"}


# ===================== Palm N Uptake =====================


@router.get("/palm-uptake", response_model=list[PalmNUptakeParamRead])
async def list_palm_uptake_params(db: AsyncSession = Depends(get_db)):
    stmt = select(PalmNUptakeParam).order_by(PalmNUptakeParam.age_min)
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
