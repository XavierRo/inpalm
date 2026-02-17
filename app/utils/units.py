"""Utilitaires de conversion d'unités."""


def kg_to_t(kg: float) -> float:
    """Convertit des kilogrammes en tonnes."""
    return kg / 1000.0


def t_to_kg(t: float) -> float:
    """Convertit des tonnes en kilogrammes."""
    return t * 1000.0


def tfm_to_kg(tfm: float, dry_matter_fraction: float = 0.25) -> float:
    """Convertit des tonnes de matière fraîche en kg de matière sèche."""
    return tfm * 1000.0 * dry_matter_fraction


def n2o_n_to_n2o(n_kg: float) -> float:
    """Convertit kg N-N₂O en kg N₂O (ratio moléculaire 44/28)."""
    return n_kg * (44.0 / 28.0)


def nox_n_to_no2(n_kg: float) -> float:
    """Convertit kg N-NOx en kg NO₂ (ratio moléculaire 46/14)."""
    return n_kg * (46.0 / 14.0)


def mm_to_m3_per_ha(mm: float) -> float:
    """Convertit des mm de pluie en m³/ha."""
    return mm * 10.0  # 1 mm = 1 L/m² = 10 m³/ha
