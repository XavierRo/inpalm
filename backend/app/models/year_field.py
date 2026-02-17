from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class YearFieldData(Base):
    __tablename__ = "year_field_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("field.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    yield_tffb_ha: Mapped[float] = mapped_column(Float, nullable=True)
    understorey_biomass: Mapped[str] = mapped_column(String(50), nullable=True)
    legume_fraction: Mapped[str] = mapped_column(String(50), nullable=True)
    pruned_frond: Mapped[str] = mapped_column(String(100), nullable=True)
    atmospheric_deposition: Mapped[float] = mapped_column(Float, nullable=True)

    # Relations
    field: Mapped["Field"] = relationship("Field", back_populates="year_field_data")
