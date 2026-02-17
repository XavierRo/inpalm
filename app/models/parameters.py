from sqlalchemy import String, Float, Integer, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FertilizerProperty(Base):
    """Propriétés N des différents fertilisants."""

    __tablename__ = "fertilizer_property"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # Mineral / Organic
    n_content: Mapped[float] = mapped_column(Float, nullable=False)  # % N total
    nh4_fraction: Mapped[float] = mapped_column(Float, nullable=True)  # fraction NH4+
    no3_fraction: Mapped[float] = mapped_column(Float, nullable=True)  # fraction NO3-
    organic_n_fraction: Mapped[float] = mapped_column(Float, nullable=True)
    unit_conversion: Mapped[float] = mapped_column(
        Float, nullable=True, default=1.0
    )  # ex: tFM → kg N/ha
    description: Mapped[str] = mapped_column(Text, nullable=True)


class VolatilizationParam(Base):
    """Paramètres de volatilisation NH3 selon fertilisant et placement."""

    __tablename__ = "volatilization_param"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fertilizer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    placement: Mapped[str] = mapped_column(String(255), nullable=False)
    base_rate: Mapped[float] = mapped_column(Float, nullable=False)  # taux de base
    ph_adjustment: Mapped[float] = mapped_column(
        Float, nullable=True, default=0.0
    )  # ajustement pH
    temperature_adjustment: Mapped[float] = mapped_column(
        Float, nullable=True, default=0.0
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)


class EmissionFactor(Base):
    """Facteurs d'émission pour N2O, NOx, N2."""

    __tablename__ = "emission_factor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flux_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # N2O, NOx, N2
    source: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # synthetic, organic, residues, etc.
    method: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # nom de la méthode
    factor_value: Mapped[float] = mapped_column(Float, nullable=False)
    factor_unit: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class LeachingParam(Base):
    """Paramètres de lessivage NO3 selon texture et pente."""

    __tablename__ = "leaching_param"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    texture: Mapped[str] = mapped_column(String(100), nullable=False)
    slope_min: Mapped[float] = mapped_column(Float, nullable=True)
    slope_max: Mapped[float] = mapped_column(Float, nullable=True)
    terraces: Mapped[str] = mapped_column(String(50), nullable=True)
    base_leaching_fraction: Mapped[float] = mapped_column(Float, nullable=False)
    rainfall_coefficient: Mapped[float] = mapped_column(
        Float, nullable=True, default=1.0
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)


class FuzzyMembership(Base):
    """Fonctions d'appartenance pour la logique floue."""

    __tablename__ = "fuzzy_membership"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    variable_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # ex: Legume_fraction
    linguistic_value: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ex: High
    membership_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="triangular"
    )
    params: Mapped[dict] = mapped_column(
        JSON, nullable=False
    )  # {a, b, c} pour triangulaire
    output_min: Mapped[float] = mapped_column(Float, nullable=True)
    output_max: Mapped[float] = mapped_column(Float, nullable=True)


class FuzzyRule(Base):
    """Règles d'inférence floue."""

    __tablename__ = "fuzzy_rule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_set_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # ex: N_fixation
    conditions: Mapped[dict] = mapped_column(
        JSON, nullable=False
    )  # {"Legume_fraction": "High", ...}
    output_value: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=True, default=1.0)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class PalmNUptakeParam(Base):
    """Paramètres de captation N par les palmiers selon l'âge."""

    __tablename__ = "palm_n_uptake_param"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    age_min: Mapped[int] = mapped_column(Integer, nullable=False)
    age_max: Mapped[int] = mapped_column(Integer, nullable=False)
    n_per_tffb: Mapped[float] = mapped_column(Float, nullable=False)  # kg N / t FFB
    vegetative_n_demand: Mapped[float] = mapped_column(
        Float, nullable=True
    )  # kg N/ha/an pour croissance végétative
    description: Mapped[str] = mapped_column(Text, nullable=True)


class CalculationMethod(Base):
    """Méthodes de calcul disponibles par type de flux."""

    __tablename__ = "calculation_method"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flux_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # volatilization, leaching, n2o, etc.
    method_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    formula_reference: Mapped[str] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
