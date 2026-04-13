"""
Moteur de logique floue IN-Palm — version paramétrée depuis la base.

Architecture :
  - Le calcul pur (cosinus, MIN, moyenne pondérée) reste dans ce module,
    identique à la version précédente.
  - Les valeurs (limites F/U, conclusions des règles, conversions nominales)
    sont chargées depuis la base via FuzzyParamsLoader.
  - Un cache par module_code évite des requêtes répétées à chaque calcul mensuel.

Usage dans un module de calcul :
    loader = FuzzyParamsLoader(db)
    factors, rules = await loader.get(module_code)
    nominal = await loader.get_nominal_conversions(module_code)

    # Convertir les valeurs nominales si nécessaire
    input_values = {
        'rain_intensity': rainfall_mm / rainy_days,
        'soil_cover':     soil_cover_fraction,
        'slope':          field.slope,
        'terraces':       nominal['terraces'][field.terraces],  # "Absence" → 0.0
    }
    result = fuzzy_decision_tree(input_values, factors, rules)
    runoff_coefficient = result['output']  # % de pluie ruisselée

Référence : Pardon et al. (2019), IN-Palm Technical Report, §2 et §3.
"""

import math
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parameters import (
    FuzzyFactor as FuzzyFactorModel,
    FuzzyRule as FuzzyRuleModel,
    FuzzyNominalConversion,
)


# ---------------------------------------------------------------------------
# Structures de données (inchangées — le moteur de calcul ne voit pas la base)
# ---------------------------------------------------------------------------

@dataclass
class FuzzyFactor:
    """
    Facteur (variable d'entrée) d'un arbre de décision flou.

    Valeurs chargées depuis la table fuzzy_factor :
      - unfav_limit : valeur numérique → classe Unfavourable
      - fav_limit   : valeur numérique → classe Favourable

    Rapport §3 : colonnes "Unfavorable limit" / "Favorable limit".
    """
    name: str
    unfav_limit: float
    fav_limit: float


@dataclass
class FuzzyRule:
    """
    Règle d'un arbre de décision flou.

    Valeurs chargées depuis la table fuzzy_rule :
      - conditions  : {nom_facteur: 'F'|'U'} — structure immuable
      - conclusion  : valeur de sortie si la règle est vraie — paramétrable

    Rapport §3 : colonnes "Structure of the tree" + "Emission factor".
    """
    conditions: dict[str, str]
    conclusion: float


# ---------------------------------------------------------------------------
# Chargeur de paramètres depuis la base (avec cache par session)
# ---------------------------------------------------------------------------

class FuzzyParamsLoader:
    """
    Charge et met en cache les paramètres fuzzy depuis la base de données.

    Le cache est local à l'instance (donc à la session de calcul d'une
    simulation). Il évite de requêter la base à chaque module et à
    chaque mois du cycle de 30 ans.

    Utilisation : instancier une fois par simulation dans engine.py,
    puis passer l'instance à chaque module de calcul.
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self._factors_cache: dict[str, list[FuzzyFactor]] = {}
        self._rules_cache: dict[str, list[FuzzyRule]] = {}
        self._nominal_cache: dict[str, dict[str, dict[str, float]]] = {}

    async def get_factors(self, module_code: str) -> list[FuzzyFactor]:
        """
        Retourne les facteurs d'un module, triés par factor_order.

        Le tri garantit la cohérence avec l'ordre des colonnes dans les
        tableaux du rapport (ex: rain_intensity en premier pour water_runoff).
        """
        if module_code not in self._factors_cache:
            stmt = (
                select(FuzzyFactorModel)
                .where(FuzzyFactorModel.module_code == module_code)
                .order_by(FuzzyFactorModel.factor_order)
            )
            result = await self._db.execute(stmt)
            rows = result.scalars().all()

            if not rows:
                raise ValueError(
                    f"Aucun facteur trouvé pour le module fuzzy '{module_code}'. "
                    f"Vérifier que le seed SQL a bien été exécuté."
                )

            self._factors_cache[module_code] = [
                FuzzyFactor(
                    name=row.factor_name,
                    unfav_limit=row.unfav_limit,
                    fav_limit=row.fav_limit,
                )
                for row in rows
            ]

        return self._factors_cache[module_code]

    async def get_rules(self, module_code: str) -> list[FuzzyRule]:
        """
        Retourne les règles d'un module, triées par rule_number.

        L'ordre correspond à la numérotation des règles dans les tableaux
        du rapport (1-indexé, de haut en bas).
        """
        if module_code not in self._rules_cache:
            stmt = (
                select(FuzzyRuleModel)
                .where(FuzzyRuleModel.module_code == module_code)
                .order_by(FuzzyRuleModel.rule_number)
            )
            result = await self._db.execute(stmt)
            rows = result.scalars().all()

            if not rows:
                raise ValueError(
                    f"Aucune règle trouvée pour le module fuzzy '{module_code}'. "
                    f"Vérifier que le seed SQL a bien été exécuté."
                )

            self._rules_cache[module_code] = [
                FuzzyRule(
                    conditions=row.conditions,
                    conclusion=row.conclusion,
                )
                for row in rows
            ]

        return self._rules_cache[module_code]

    async def get_nominal_conversions(
        self, module_code: str
    ) -> dict[str, dict[str, float]]:
        """
        Retourne les tables de conversion nominale → numérique pour un module.

        Retourne un dict à deux niveaux :
          {nom_facteur: {valeur_nominale: valeur_numérique}}

        Exemple pour water_runoff :
          {'terraces': {'Presence': 1.0, 'Absence': 0.0}}

        Les modules sans variables nominales retournent un dict vide.

        Rapport §3 : Tables 3.1 à 3.6 "Conversion of nominal input variables".
        """
        if module_code not in self._nominal_cache:
            stmt = select(FuzzyNominalConversion).where(
                FuzzyNominalConversion.module_code == module_code
            )
            result = await self._db.execute(stmt)
            rows = result.scalars().all()

            conversions: dict[str, dict[str, float]] = {}
            for row in rows:
                if row.factor_name not in conversions:
                    conversions[row.factor_name] = {}
                conversions[row.factor_name][row.nominal_value] = row.numeric_value

            self._nominal_cache[module_code] = conversions

        return self._nominal_cache[module_code]

    async def load_module(
        self, module_code: str
    ) -> tuple[list[FuzzyFactor], list[FuzzyRule], dict[str, dict[str, float]]]:
        """
        Charge en une seule fois facteurs, règles et conversions nominales.

        Raccourci pratique pour les modules qui ont besoin des trois.
        Retourne (factors, rules, nominal_conversions).
        """
        factors = await self.get_factors(module_code)
        rules = await self.get_rules(module_code)
        nominal = await self.get_nominal_conversions(module_code)
        return factors, rules, nominal


# ---------------------------------------------------------------------------
# Moteur de calcul pur — identique à la version précédente, sans I/O
# ---------------------------------------------------------------------------

def _normalise(value: float, unfav_limit: float, fav_limit: float) -> float:
    """
    Normalise une valeur brute entre 0 et 1.

    §2.3 (étape 1) : normalisation linéaire entre les limites F/U,
    avec clamp aux bornes [0, 1].
    """
    if fav_limit == unfav_limit:
        return 0.5
    normalised = (value - unfav_limit) / (fav_limit - unfav_limit)
    return max(0.0, min(1.0, normalised))


def membership_favourable(normalised_value: float) -> float:
    """
    Degré d'appartenance Favourable — Équation (1) du rapport.

    Membership_Favourable = 0.5 × [1 + cos(x × π + π)]
    Pour x=0 → 0.0, x=0.5 → 0.5, x=1 → 1.0
    """
    return 0.5 * (1.0 + math.cos(normalised_value * math.pi + math.pi))


def membership_unfavourable(normalised_value: float) -> float:
    """
    Degré d'appartenance Unfavourable — Équation (2) du rapport.

    Membership_Unfavourable = 0.5 × [1 + cos(x × π)]
    Pour x=0 → 1.0, x=0.5 → 0.5, x=1 → 0.0
    """
    return 0.5 * (1.0 + math.cos(normalised_value * math.pi))


def compute_memberships(
    value: float, factor: FuzzyFactor
) -> tuple[float, float]:
    """Retourne (degree_F, degree_U) pour une valeur et un facteur."""
    normalised = _normalise(value, factor.unfav_limit, factor.fav_limit)
    return membership_favourable(normalised), membership_unfavourable(normalised)


def compute_truth_value(
    rule: FuzzyRule,
    memberships: dict[str, tuple[float, float]],
) -> float:
    """
    Valeur de vérité d'une règle — opérateur MIN (Sugeno, Équation 3).

    Truth_value_i = min(Membership_degree_j) pour j dans les facteurs de la règle.
    """
    degrees = []
    for factor_name, expected_class in rule.conditions.items():
        if factor_name not in memberships:
            continue
        degree_f, degree_u = memberships[factor_name]
        degrees.append(degree_f if expected_class == 'F' else degree_u)

    return min(degrees) if degrees else 0.0


def aggregate_conclusions(
    rules: list[FuzzyRule],
    memberships: dict[str, tuple[float, float]],
) -> float:
    """
    Agrégation des conclusions — moyenne pondérée (Sugeno, Équation 4).

    Output = Σ(Truth_value_i × Conclusion_i) / Σ(Truth_value_i)
    """
    weighted_sum = 0.0
    truth_sum = 0.0

    for rule in rules:
        truth = compute_truth_value(rule, memberships)
        weighted_sum += truth * rule.conclusion
        truth_sum += truth

    return weighted_sum / truth_sum if truth_sum > 0.0 else 0.0


def fuzzy_decision_tree(
    input_values: dict[str, float],
    factors: list[FuzzyFactor],
    rules: list[FuzzyRule],
) -> dict:
    """
    Exécute un arbre de décision flou IN-Palm complet.

    Les facteurs et règles sont fournis par FuzzyParamsLoader — ils viennent
    de la base, pas du code. Le moteur de calcul ne change pas.

    Args:
        input_values : {nom_facteur: valeur_numérique}
                       Les variables nominales doivent être converties
                       au préalable via get_nominal_conversions().
        factors      : liste des FuzzyFactor (depuis la base)
        rules        : liste des FuzzyRule (depuis la base)

    Returns:
        dict avec :
          'output'       : valeur finale du module
          'memberships'  : degrés d'appartenance par facteur (traçabilité)
          'truth_values' : valeur de vérité par règle (traçabilité)
    """
    factor_map = {f.name: f for f in factors}
    memberships: dict[str, tuple[float, float]] = {
        name: compute_memberships(value, factor_map[name])
        for name, value in input_values.items()
        if name in factor_map
    }

    truth_values = [compute_truth_value(rule, memberships) for rule in rules]
    output = aggregate_conclusions(rules, memberships)

    return {
        'output': output,
        'memberships': {
            name: {'F': round(mf, 4), 'U': round(mu, 4)}
            for name, (mf, mu) in memberships.items()
        },
        'truth_values': [round(t, 4) for t in truth_values],
    }


# ---------------------------------------------------------------------------
# Fonction utilitaire pour la conversion nominale (helper pour les modules)
# ---------------------------------------------------------------------------

def convert_nominal(
    nominal_value: str,
    factor_name: str,
    nominal_conversions: dict[str, dict[str, float]],
    module_code: str = "",
) -> float:
    """
    Convertit une valeur nominale en numérique via la table de conversion.

    Lève une ValueError explicite si la valeur n'est pas trouvée,
    pour faciliter le débogage lors de l'import de nouvelles données terrain.

    Exemple :
        convert_nominal("Absence", "terraces", nominal, "water_runoff") → 0.0
        convert_nominal("Urea", "mineral_fertilizer_type", nominal, "nh3_mineral") → 0.0
    """
    if factor_name not in nominal_conversions:
        raise ValueError(
            f"Facteur nominal '{factor_name}' non trouvé pour le module '{module_code}'. "
            f"Facteurs disponibles : {list(nominal_conversions.keys())}"
        )

    conversions = nominal_conversions[factor_name]
    if nominal_value not in conversions:
        raise ValueError(
            f"Valeur nominale '{nominal_value}' non trouvée pour le facteur "
            f"'{factor_name}' (module '{module_code}'). "
            f"Valeurs connues : {list(conversions.keys())}"
        )

    return conversions[nominal_value]
