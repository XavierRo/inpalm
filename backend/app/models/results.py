from sqlalchemy import String, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SimulationResultYearly(Base):
    """Résultats annuels du bilan azoté."""

    __tablename__ = "simulation_result_yearly"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[str] = mapped_column(
        ForeignKey("simulation.id"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    palm_age: Mapped[int] = mapped_column(Integer, nullable=False)

    # === Entrées N (kg N/ha/an) ===
    n_initial_soil: Mapped[float] = mapped_column(Float, default=0.0)
    n_fixation: Mapped[float] = mapped_column(Float, default=0.0)
    n_residues: Mapped[float] = mapped_column(Float, default=0.0)
    n_synthetic_fertilizer: Mapped[float] = mapped_column(Float, default=0.0)
    n_organic_fertilizer: Mapped[float] = mapped_column(Float, default=0.0)
    n_atmospheric_deposition: Mapped[float] = mapped_column(Float, default=0.0)
    total_inputs: Mapped[float] = mapped_column(Float, default=0.0)

    # === Sorties N (kg N/ha/an) ===
    n_volatilization: Mapped[float] = mapped_column(Float, default=0.0)
    n_leaching: Mapped[float] = mapped_column(Float, default=0.0)
    n_palm_uptake: Mapped[float] = mapped_column(Float, default=0.0)
    n_n2o_emission: Mapped[float] = mapped_column(Float, default=0.0)
    n_nox_emission: Mapped[float] = mapped_column(Float, default=0.0)
    n_n2_emission: Mapped[float] = mapped_column(Float, default=0.0)
    n_runoff: Mapped[float] = mapped_column(Float, default=0.0)
    total_outputs: Mapped[float] = mapped_column(Float, default=0.0)

    # === Bilan ===
    balance: Mapped[float] = mapped_column(Float, default=0.0)

    # === Variables intermédiaires (flexible) ===
    intermediate_results: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Relations
    simulation: Mapped["Simulation"] = relationship(
        "Simulation", back_populates="results_yearly"
    )


class SimulationResultCycle(Base):
    """Résultat agrégé sur le cycle complet de la plantation."""

    __tablename__ = "simulation_result_cycle"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    simulation_id: Mapped[str] = mapped_column(
        ForeignKey("simulation.id"), nullable=False, unique=True
    )

    total_n_inputs: Mapped[float] = mapped_column(Float, default=0.0)
    total_n_outputs: Mapped[float] = mapped_column(Float, default=0.0)
    total_balance: Mapped[float] = mapped_column(Float, default=0.0)

    # Détail par flux sur tout le cycle
    summary: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Relations
    simulation: Mapped["Simulation"] = relationship(
        "Simulation", back_populates="result_cycle"
    )
