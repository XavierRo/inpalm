"""Moteur de logique floue pour la conversion des variables qualitatives."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parameters import FuzzyMembership, FuzzyRule


def _triangular_membership(x: float, a: float, b: float, c: float) -> float:
    """Fonction d'appartenance triangulaire."""
    if x <= a or x >= c:
        return 0.0
    elif x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    else:
        return (c - x) / (c - b) if c != b else 1.0


def _trapezoidal_membership(
    x: float, a: float, b: float, c: float, d: float
) -> float:
    """Fonction d'appartenance trapézoïdale."""
    if x <= a or x >= d:
        return 0.0
    elif x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    elif x <= c:
        return 1.0
    else:
        return (d - x) / (d - c) if d != c else 1.0


def compute_membership(value: float, membership_type: str, params: dict) -> float:
    """Calcule le degré d'appartenance d'une valeur à un ensemble flou."""
    if membership_type == "triangular":
        return _triangular_membership(value, params["a"], params["b"], params["c"])
    elif membership_type == "trapezoidal":
        return _trapezoidal_membership(
            value, params["a"], params["b"], params["c"], params["d"]
        )
    else:
        raise ValueError(f"Type de membership inconnu: {membership_type}")


async def fuzzy_inference(
    db: AsyncSession,
    rule_set_name: str,
    input_values: dict[str, str],
) -> float:
    """
    Effectue une inférence floue pour un jeu de règles donné.

    Args:
        db: Session base de données
        rule_set_name: Nom du jeu de règles (ex: "N_fixation")
        input_values: Variables d'entrée qualitatives
                      ex: {"Legume_fraction": "High", "Understorey_biomass": "Low"}

    Returns:
        Valeur numérique résultante (défuzzifiée)
    """
    # Récupérer les règles
    stmt = select(FuzzyRule).where(FuzzyRule.rule_set_name == rule_set_name)
    result = await db.execute(stmt)
    rules = result.scalars().all()

    if not rules:
        # TODO: Valeur par défaut à définir avec Cécile
        return 0.0

    # Évaluer chaque règle
    weighted_sum = 0.0
    weight_total = 0.0

    for rule in rules:
        # Vérifier si toutes les conditions correspondent
        match = True
        for var_name, expected_value in rule.conditions.items():
            if input_values.get(var_name) != expected_value:
                match = False
                break

        if match:
            weighted_sum += rule.output_value * rule.weight
            weight_total += rule.weight

    if weight_total == 0.0:
        return 0.0

    return weighted_sum / weight_total
