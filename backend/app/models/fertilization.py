from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FertilizationData(Base):
    __tablename__ = "fertilization_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("field.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[str] = mapped_column(String(20), nullable=False)
    fertilization_type: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    composition: Mapped[str] = mapped_column(String(100), nullable=False)
    placement: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relations
    field: Mapped["Field"] = relationship("Field", back_populates="fertilization_data")
