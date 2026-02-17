from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RainfallData(Base):
    __tablename__ = "rainfall_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("field.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[str] = mapped_column(String(20), nullable=False)
    rainfall_mm: Mapped[float] = mapped_column(Float, nullable=False)
    rain_frequency: Mapped[int] = mapped_column(Integer, nullable=True)
    dataset_name: Mapped[str] = mapped_column(
        String(255), nullable=False, default="default"
    )

    # Relations
    field: Mapped["Field"] = relationship("Field", back_populates="rainfall_data")
