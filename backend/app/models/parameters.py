"""
Modèles SQLAlchemy — Paramètres du simulateur NBalance.

Organisation :
  - Paramètres généraux (fertilisants, facteurs d'émission, lessivage, uptake)
  - Paramètres fuzzy IN-Palm (modules, facteurs, règles, conversions nominales)
  - Méthodes de calcul disponibles par flux

Concernant les tables fuzzy, la philosophie retenue est :
  - La STRUCTURE des modules (quels facteurs, quelles règles, dans quel ordre)
    est définie dans le code Python de chaque module → immuable, c'est la science.
  - Les VALEURS (limites F/U, conclusions des règles, conversions nominales)
    sont stockées en base → paramétrables via l'interface, traçables, versionnables.

Ce découpage permet à Cécile de recalibrer l'indicateur sans toucher au code,
tout en garantissant que la logique de calcul reste sous contrôle.

Référence : Pardon et al. (2019), IN-Palm Technical Report, §2 et §3.
"""

from sqlalchemy import String, Float, Integer, Boolean, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# ---------------------------------------------------------------------------
# Paramètres généraux (inchangés, conservés de l'existant)
# ---------------------------------------------------------------------------

class FertilizerProperty(Base):
    """Propriétés N des différents fertilisants."""

    __tablename__ = "fertilizer_property"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # Mineral / Organic
    n_content: Mapped[float] = mapped_column(Float, nullable=False)  # % N total
    nh4_fraction: Mapped[float] = mapped_column(Float, nullable=True)
    no3_fraction: Mapped[float] = mapped_column(Float, nullable=True)
    organic_n_fraction: Mapped[float] = mapped_column(Float, nullable=True)
    unit_conversion: Mapped[float] = mapped_column(Float, nullable=True, default=1.0)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class VolatilizationParam(Base):
    """Paramètres de volatilisation NH3 selon fertilisant et placement."""

    __tablename__ = "volatilization_param"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fertilizer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    placement: Mapped[str] = mapped_column(String(255), nullable=False)
    base_rate: Mapped[float] = mapped_column(Float, nullable=False)
    ph_adjustment: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    temperature_adjustment: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class EmissionFactor(Base):
    """Facteurs d'émission pour N2O, NOx, N2."""

    __tablename__ = "emission_factor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flux_type: Mapped[str] = mapped_column(String(20), nullable=False)   # N2O, NOx, N2
    source: Mapped[str] = mapped_column(String(100), nullable=False)     # synthetic, organic...
    method: Mapped[str] = mapped_column(String(100), nullable=False)
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
    rainfall_coefficient: Mapped[float] = mapped_column(Float, nullable=True, default=1.0)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class PalmNUptakeParam(Base):
    """
    Paramètres d'absorption N par les palmiers selon l'âge.

    Calibré sur 58 500 simulations APSIM-Oil Palm (Pardon et al., 2017).
    Les limites fav/unfav correspondent aux classes de rendement (tFFB/ha/an)
    et les valeurs low/high à l'absorption N associée (kg N/ha/an).

    Rapport §3, Module 4.1 — Palm N Uptake, Table p.34.
    """

    __tablename__ = "palm_n_uptake_param"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    palm_age: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    # Limites de rendement (facteur Yield dans l'arbre fuzzy)
    yield_unfav_limit: Mapped[float] = mapped_column(Float, nullable=False)  # t FFB/ha/an
    yield_fav_limit: Mapped[float] = mapped_column(Float, nullable=False)

    # Absorption N correspondante (conclusions de l'arbre fuzzy)
    n_uptake_low: Mapped[float] = mapped_column(Float, nullable=False)   # kg N/ha/an
    n_uptake_high: Mapped[float] = mapped_column(Float, nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=True)


class CalculationMethod(Base):
    """Méthodes de calcul disponibles par type de flux."""

    __tablename__ = "calculation_method"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flux_type: Mapped[str] = mapped_column(String(50), nullable=False)
    method_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    formula_reference: Mapped[str] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


# ---------------------------------------------------------------------------
# Paramètres fuzzy IN-Palm
# ---------------------------------------------------------------------------

class FuzzyModule(Base):
    """
    Registre des modules à arbre de décision flou d'IN-Palm.

    Chaque entrée correspond à un module du rapport (§3).
    Ce n'est pas une table de calcul : elle sert de référence et de clé
    étrangère pour les tables FuzzyFactor, FuzzyRule et FuzzyNominalConversion.

    Le champ `module_code` est la clé métier utilisée dans le code Python
    pour charger les paramètres d'un module donné (ex: "water_runoff").

    11 modules fuzzy dans IN-Palm :
      step1  : nh3_mineral
      step2  : soil_cover, water_runoff
      step3  : n2o_mineral, n2_mineral, runoff_erosion
      step4  : palm_uptake, understorey_fixation
      step5  : n2o_baseline, n2_baseline, leaching
    """

    __tablename__ = "fuzzy_module"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module_code: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True
    )  # clé métier, ex: "water_runoff"
    module_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )  # ex: "Module 2.3 — Water Runoff"
    step: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # étape de calcul IN-Palm : 1 à 5
    report_section: Mapped[str] = mapped_column(
        String(20), nullable=True
    )  # ex: "§3, Module 2.3"
    output_unit: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # ex: "% of rainfall", "kg N/ha/month"
    output_min: Mapped[float] = mapped_column(Float, nullable=True)
    output_max: Mapped[float] = mapped_column(Float, nullable=True)
    reference: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class FuzzyFactor(Base):
    """
    Facteurs (variables d'entrée) d'un module fuzzy IN-Palm.

    Chaque facteur définit les deux limites de ses classes Favourable/Unfavourable.
    Ces limites sont les valeurs paramétrables : elles correspondent aux lignes
    "Unfavorable limit" et "Favorable limit" des tableaux du rapport (§3).

    Les variables nominales (texture, type engrais...) ont leurs valeurs numériques
    définies dans FuzzyNominalConversion — ici, unfav_limit et fav_limit sont les
    bornes de l'espace normalisé [0, 1] après conversion (généralement 0 et 1).

    Le champ `factor_order` définit l'ordre de lecture dans les règles de l'arbre,
    ce qui correspond à l'ordre des colonnes dans les tableaux du rapport.
    """

    __tablename__ = "fuzzy_factor"
    __table_args__ = (
        UniqueConstraint("module_code", "factor_name", name="uq_fuzzy_factor"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module_code: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # FK logique vers fuzzy_module.module_code
    factor_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # clé Python, ex: "rain_intensity"
    label: Mapped[str] = mapped_column(
        String(150), nullable=True
    )  # libellé affichage, ex: "Rain intensity"
    unit: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # ex: "mm", "%", "years"
    unfav_limit: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # ← PARAMÉTRABLE : limite classe Unfavourable
    fav_limit: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # ← PARAMÉTRABLE : limite classe Favourable
    factor_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )  # ordre dans l'arbre (gauche → droite dans les tableaux)
    is_intermediate: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )  # True si calculé par un autre module (marqué * dans le rapport)
    reference: Mapped[str] = mapped_column(Text, nullable=True)


class FuzzyRule(Base):
    """
    Règles de l'arbre de décision flou d'un module IN-Palm.

    Chaque règle encode les conditions F/U pour chaque facteur impliqué,
    et la valeur de conclusion (facteur d'émission ou coefficient de sortie).

    Structure du champ `conditions` (JSON) :
      {"rain_intensity": "U", "soil_cover": "F", "slope": "U"}
    Les facteurs absents d'une règle ne sont pas listés (règle partielle).

    Le champ `conclusion` est la valeur PARAMÉTRABLE : c'est elle qui
    définit l'amplitude de la sortie du module (ex: 10.0 pour "Low",
    20.0 pour "Very_high" dans Water Runoff).

    Le champ `conclusion_label` est un libellé qualitatif non calculatoire
    (ex: "Very_low", "High") qui correspond aux labels du rapport.

    Rapport §3 : les conclusions sont les valeurs dans la colonne
    "Emission factor" de chaque tableau de module.
    """

    __tablename__ = "fuzzy_rule"
    __table_args__ = (
        UniqueConstraint("module_code", "rule_number", name="uq_fuzzy_rule"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module_code: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # FK logique vers fuzzy_module.module_code
    rule_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # numéro de règle dans l'arbre (1-indexé, ordre du rapport)
    conditions: Mapped[dict] = mapped_column(
        JSON, nullable=False
    )  # {"factor_name": "F"|"U", ...} — STRUCTURE immuable
    conclusion: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # ← PARAMÉTRABLE : valeur de sortie de la règle
    conclusion_label: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # ex: "Very_low", "High" — libellé qualitatif
    reference: Mapped[str] = mapped_column(Text, nullable=True)


class FuzzyNominalConversion(Base):
    """
    Tables de conversion des variables nominales en valeurs numériques.

    Dans IN-Palm, certains facteurs prennent des valeurs nominales
    (ex: type d'engrais, texture du sol, placement) qui doivent être
    converties en numérique [0, 1] avant d'entrer dans le moteur fuzzy.

    Ces tables correspondent aux "Table 3.x — Conversion of nominal input
    variables into numerical values" du rapport (§3).

    La valeur `numeric_value` est PARAMÉTRABLE : elle définit la position
    d'une modalité sur l'axe F/U. Par exemple, pour la texture dans
    le module NH3-Mineral : Fine=1.0, Medium=0.5, Coarse=0.0.

    Attention : pour un même facteur (ex: "soil_texture"), les valeurs
    numériques peuvent différer selon le module (ex: dans N2O-Mineral,
    Fine=0.0, Medium=1.0, Coarse=0.5 — ordre inversé). D'où la clé
    composite (module_code, factor_name, nominal_value).
    """

    __tablename__ = "fuzzy_nominal_conversion"
    __table_args__ = (
        UniqueConstraint(
            "module_code", "factor_name", "nominal_value",
            name="uq_fuzzy_nominal"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module_code: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    factor_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # ex: "soil_texture", "mineral_fertilizer_type"
    nominal_value: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # ex: "Fine", "Urea", "Presence"
    numeric_value: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # ← PARAMÉTRABLE : valeur numérique [0, 1]
    reference: Mapped[str] = mapped_column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Tables supprimées / remplacées
# ---------------------------------------------------------------------------
# Les anciennes tables FuzzyMembership (membership triangulaire/trapézoïdale)
# et l'ancienne FuzzyRule (avec rule_set_name + conditions textuelles) sont
# remplacées par FuzzyModule + FuzzyFactor + FuzzyRule + FuzzyNominalConversion.
#
# Migration Alembic nécessaire :
#   - DROP TABLE fuzzy_membership
#   - DROP TABLE fuzzy_rule  (ancienne version)
#   - CREATE TABLE fuzzy_module
#   - CREATE TABLE fuzzy_factor
#   - CREATE TABLE fuzzy_rule  (nouvelle version)
#   - CREATE TABLE fuzzy_nominal_conversion
