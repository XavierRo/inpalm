from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Field(Base):
    __tablename__ = "field"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    localisation: Mapped[str] = mapped_column(String(255), nullable=False)
    year_planting: Mapped[int] = mapped_column(Integer, nullable=False)
    end_field: Mapped[int] = mapped_column(Integer, nullable=False)
    slope: Mapped[float] = mapped_column(Float, nullable=True)
    texture: Mapped[str] = mapped_column(String(100), nullable=True)
    organic_carbon: Mapped[float] = mapped_column(Float, nullable=True)
    initial_soil_water: Mapped[float] = mapped_column(Float, nullable=True)
    ph: Mapped[float] = mapped_column(Float, nullable=True)
    cec: Mapped[float] = mapped_column(Float, nullable=True)
    previous_palm: Mapped[str] = mapped_column(String(255), nullable=True)
    terraces: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relations
    year_field_data: Mapped[list["YearFieldData"]] = relationship(
        "YearFieldData", back_populates="field", cascade="all, delete-orphan"
    )
    rainfall_data: Mapped[list["RainfallData"]] = relationship(
        "RainfallData", back_populates="field", cascade="all, delete-orphan"
    )
    fertilization_data: Mapped[list["FertilizationData"]] = relationship(
        "FertilizationData", back_populates="field", cascade="all, delete-orphan"
    )
    simulations: Mapped[list["Simulation"]] = relationship(
        "Simulation", back_populates="field", cascade="all, delete-orphan"
    )
