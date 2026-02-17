import uuid
from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Simulation(Base):
    """Configuration d'une simulation de bilan azoté."""

    __tablename__ = "simulation"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey("field.id"), nullable=False)
    rainfall_dataset: Mapped[str] = mapped_column(
        String(255), nullable=False, default="default"
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, running, completed, error
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relations
    field: Mapped["Field"] = relationship("Field", back_populates="simulations")
    options: Mapped[list["SimulationOption"]] = relationship(
        "SimulationOption", back_populates="simulation", cascade="all, delete-orphan"
    )
    overrides: Mapped[list["SimulationOverride"]] = relationship(
        "SimulationOverride", back_populates="simulation", cascade="all, delete-orphan"
    )
    results_yearly: Mapped[list["SimulationResultYearly"]] = relationship(
        "SimulationResultYearly",
        back_populates="simulation",
        cascade="all, delete-orphan",
    )
    result_cycle: Mapped["SimulationResultCycle"] = relationship(
        "SimulationResultCycle",
        back_populates="simulation",
        cascade="all, delete-orphan",
        uselist=False,
    )


class SimulationOption(Base):
    """Méthode de calcul choisie pour chaque flux dans une simulation."""

    __tablename__ = "simulation_option"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[str] = mapped_column(
        ForeignKey("simulation.id"), nullable=False
    )
    flux_type: Mapped[str] = mapped_column(String(50), nullable=False)
    method_id: Mapped[int] = mapped_column(
        ForeignKey("calculation_method.id"), nullable=False
    )

    # Relations
    simulation: Mapped["Simulation"] = relationship(
        "Simulation", back_populates="options"
    )
    method: Mapped["CalculationMethod"] = relationship("CalculationMethod")


class SimulationOverride(Base):
    """Coefficients modifiés pour un scénario (what-if)."""

    __tablename__ = "simulation_override"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[str] = mapped_column(
        ForeignKey("simulation.id"), nullable=False
    )
    param_table: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # table d'origine
    param_id: Mapped[int] = mapped_column(Integer, nullable=False)
    param_field: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # champ modifié
    original_value: Mapped[float] = mapped_column(Float, nullable=True)
    override_value: Mapped[float] = mapped_column(Float, nullable=False)

    # Relations
    simulation: Mapped["Simulation"] = relationship(
        "Simulation", back_populates="overrides"
    )
