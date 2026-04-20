# CLAUDE.md — NBalance

Guide de contexte pour Claude Code. À lire en priorité avant toute intervention sur ce projet.

---

## Projet

**NBalance** — Outil de diagnostic et d'aide à la décision pour le bilan azoté du palmier à huile.  
Utilisateurs cibles : chercheurs en agroécologie (pas de multi-utilisateurs en v1).  
Équipe : Cécile Bessou (chercheuse, expertise métier) + Xavier (développeur).

Le modèle de calcul est basé sur **IN-Palm** (Pardon et al., 2019).  
Référence complète : `docs/inpalm_modules_reference.md`  
Rapport source : `docs/Pardon_2019_INPalm_Technical_report_1.pdf`

---

## Stack

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) |
| Frontend | React 18 · Vite · Tailwind CSS · Recharts |
| Base de données | PostgreSQL 16 |
| CI/CD | GitLab CI · Docker (runner shell sur serveur dev) |

---

## Structure du repo

```
nbalance/
├── CLAUDE.md                          ← ce fichier
├── docs/
│   ├── inpalm_modules_reference.md    ← référence complète des 17 modules
│   └── Pardon_2019_INPalm_Technical_report_1.pdf
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── field.py
│   │   │   ├── rainfall.py
│   │   │   ├── fertilization.py
│   │   │   ├── year_field.py
│   │   │   ├── parameters.py          ← modèles SQLAlchemy paramètres + fuzzy
│   │   │   ├── simulation.py
│   │   │   └── results.py
│   │   ├── schemas/
│   │   ├── routers/
│   │   │   ├── import_data.py
│   │   │   ├── fields.py
│   │   │   ├── parameters.py
│   │   │   ├── simulations.py
│   │   │   └── results.py
│   │   └── services/
│   │       ├── csv_parser.py
│   │       ├── fuzzy_engine.py        ← moteur logique floue
│   │       └── n_balance/
│   │           ├── engine.py          ← orchestrateur (boucle mensuelle)
│   │           ├── step1_nh3_mineral.py
│   │           ├── step1_nh3_organic.py
│   │           ├── step2_litter_budget.py
│   │           ├── step2_soil_cover.py
│   │           ├── step2_water_runoff.py
│   │           ├── step2_water_budget.py
│   │           ├── step3_n2o_mineral.py
│   │           ├── step3_n2_mineral.py
│   │           ├── step3_nox.py
│   │           ├── step3_runoff_erosion.py
│   │           ├── step4_palm_uptake.py
│   │           ├── step4_understorey_fixation.py
│   │           ├── step4_soil_mineral_n_budget.py
│   │           ├── step5_n2o_baseline.py
│   │           ├── step5_n2_baseline.py
│   │           ├── step5_nox_baseline.py
│   │           └── step5_leaching.py
│   ├── alembic/
│   │   └── seeds/
│   │       └── seed_fuzzy_inpalm.sql  ← données initiales fuzzy IN-Palm
│   └── requirements.txt
└── frontend/
    └── src/
        ├── components/
        └── pages/
```

---

## Principe de calcul IN-Palm

NBalance implémente les **17 modules IN-Palm** en granularité **mensuelle**.  
Les résultats sont agrégés annuellement pour la visualisation.

### Les 5 étapes de calcul (ordre d'exécution obligatoire)

```
① Volatilisation NH₃ depuis fertilisants
   └─ step1_nh3_mineral.py   (fuzzy, 7 règles)
   └─ step1_nh3_organic.py   (régression Bouwman 2002a)

② Calculs préliminaires sol et eau  ← DOIT tourner avant ③④⑤
   └─ step2_litter_budget.py        (bilan de masse)
   └─ step2_soil_cover.py           (fuzzy, 18 règles) ← dépend litter_budget
   └─ step2_water_runoff.py         (fuzzy, 5 règles)  ← dépend soil_cover
   └─ step2_water_budget.py         (bilan de masse)   ← dépend water_runoff
      → produit : soil_moisture, drainage, soil_saturation

③ Dénitrification depuis fertilisants + ruissellement
   └─ step3_n2o_mineral.py          (fuzzy, 32 règles) ← dépend soil_moisture
   └─ step3_n2_mineral.py           (fuzzy, 2 règles)  ← dépend soil_saturation + n2o_mineral
   └─ step3_nox.py                  (régression Bouwman 2002b)
   └─ step3_runoff_erosion.py       (fuzzy, 9 règles)  ← dépend soil_cover

④ Azote minéral du sol
   └─ step4_palm_uptake.py          (fuzzy, table par âge)
   └─ step4_understorey_fixation.py (fuzzy, 2 règles)  ← dépend soil_mineral_n
   └─ step4_soil_mineral_n_budget.py (bilan de masse)  ← dépend tous les flux ①②③

⑤ Dénitrification basale + lessivage depuis N minéral sol
   └─ step5_n2o_baseline.py         (fuzzy, 16 règles) ← même structure que 3.1 sans fertilisant
   └─ step5_n2_baseline.py          (fuzzy, 2 règles)  ← même arbre que step3_n2_mineral
   └─ step5_nox_baseline.py         (régression Bouwman 2002a, taux=0)
   └─ step5_leaching.py             (fuzzy, 2 règles)  ← dépend drainage
```

---

## Moteur fuzzy — Architecture

### Principe (Pardon et al. 2019, §2)

Tous les modules fuzzy utilisent **les mêmes deux fonctions cosinus** (van der Werf & Zimmer 1998) :
```
Membership_Favourable   = 0.5 × [1 + cos(x × π + π)]
Membership_Unfavourable = 0.5 × [1 + cos(x × π)]
```
Inférence Sugeno (1985) :
- Vérité d'une règle = MIN des degrés d'appartenance de ses facteurs
- Sortie = moyenne pondérée des conclusions par leurs vérités

### Fichiers clés

**`fuzzy_engine.py`** — moteur de calcul pur + chargeur depuis la base :
- `FuzzyFactor`, `FuzzyRule` : dataclasses de calcul (pas d'I/O)
- `FuzzyParamsLoader` : charge et met en cache facteurs/règles/conversions nominales depuis la base
- `fuzzy_decision_tree(input_values, factors, rules)` : exécute un arbre complet
- `convert_nominal(nominal_value, factor_name, nominal_conversions, module_code)` : conversion nominale → numérique

**`parameters.py`** (models) — 4 tables fuzzy :
- `FuzzyModule` : registre des 11 modules fuzzy (métadonnées)
- `FuzzyFactor` : limites F/U par facteur et par module (**valeurs paramétrables**)
- `FuzzyRule` : conditions (JSON, immuable) + conclusion (**valeur paramétrable**)
- `FuzzyNominalConversion` : tables de conversion nominale→numérique (**valeur paramétrable**)

**`seed_fuzzy_inpalm.sql`** : toutes les valeurs initiales des 11 modules, tirées du rapport Pardon 2019.

### Ce qui est paramétrable vs immuable

| Élément | Où | Modifiable |
|---------|-----|-----------|
| Limites F/U des facteurs | `fuzzy_factor.unfav_limit / fav_limit` | ✅ Via UI |
| Conclusions des règles | `fuzzy_rule.conclusion` | ✅ Via UI |
| Conversions nominales | `fuzzy_nominal_conversion.numeric_value` | ✅ Via UI |
| Structure des règles (conditions F/U) | `fuzzy_rule.conditions` JSON | ❌ Immuable |
| Enchaînement des modules | code Python | ❌ Immuable |
| Fonctions cosinus | `fuzzy_engine.py` | ❌ Immuable |

---

## Conventions de code

### Pattern général de chaque module

```python
async def run_<module_name>(
    loader: FuzzyParamsLoader,   # injecté depuis engine.py, pas recréé
    field: Field,
    month_data: dict,            # données du mois courant
    intermediates: dict,         # variables intermédiaires des étapes précédentes
) -> tuple[float, dict]:
    """
    Retourne (valeur_calculée, dict_intermediaires).
    Le dict intermédiaire est stocké en base dans intermediate_results (JSONB).
    """
```

- **Granularité mensuelle** partout — les modules annuels (NH3-Organic, NOx) divisent par 12
- **`FuzzyParamsLoader`** est instancié **une seule fois** dans `engine.py` par simulation, puis passé à chaque module — ne pas le réinstancier dans chaque module
- **Toujours retourner `(valeur, intermediates)`** — les intermédiaires permettent la traçabilité et le débogage
- Les **variables nominales** sont converties via `convert_nominal()` + `loader.get_nominal_conversions(module_code)` avant d'entrer dans `fuzzy_decision_tree()`
- Les **variables intermédiaires** entre modules (soil_moisture, drainage, soil_cover, litter_amount...) transitent via le dict `monthly_state` dans `engine.py`

### Nommage

- Fichiers modules : `step{N}_{nom_court}.py` (ex: `step2_water_runoff.py`)
- Fonctions principales : `run_<nom_court>()` (ex: `run_water_runoff()`)
- `module_code` dans la base : snake_case court (ex: `water_runoff`, `nh3_mineral`)

---

## État d'avancement

### ✅ Fait

- Architecture générale (FastAPI, SQLAlchemy async, Docker, GitLab CI)
- Modèles SQLAlchemy : `field`, `rainfall`, `fertilization`, `year_field`, `simulation`, `results`
- Modèles SQLAlchemy fuzzy : `FuzzyModule`, `FuzzyFactor`, `FuzzyRule`, `FuzzyNominalConversion` (dans `parameters.py`)
- `fuzzy_engine.py` : moteur cosinus Sugeno + `FuzzyParamsLoader` + `convert_nominal()`
- `seed_fuzzy_inpalm.sql` : toutes les valeurs des 11 modules fuzzy (facteurs, règles, conversions)
- Routers CRUD : `fields`, `parameters`, `simulations`, `results`, `import_data`
- `engine.py` : orchestrateur (à adapter pour boucle mensuelle et `monthly_state`)
- Référence documentaire : `docs/inpalm_modules_reference.md`

### 🔄 Migration Alembic à faire

DROP des anciennes tables `fuzzy_membership` et `fuzzy_rule` (ancienne version).  
CREATE des 4 nouvelles tables fuzzy.  
Puis exécuter `seed_fuzzy_inpalm.sql`.

### ⏳ À implémenter (dans l'ordre)

1. **`engine.py`** — adapter la boucle annuelle→mensuelle, introduire `monthly_state`
2. **Étape ②** : `step2_litter_budget.py` → `step2_soil_cover.py` → `step2_water_runoff.py` → `step2_water_budget.py`
3. **Étape ①** : `step1_nh3_mineral.py` → `step1_nh3_organic.py`
4. **Étape ③** : `step3_n2o_mineral.py` → `step3_n2_mineral.py` → `step3_nox.py` → `step3_runoff_erosion.py`
5. **Étape ④** : `step4_palm_uptake.py` → `step4_understorey_fixation.py` → `step4_soil_mineral_n_budget.py`
6. **Étape ⑤** : `step5_n2o_baseline.py` → `step5_n2_baseline.py` → `step5_nox_baseline.py` → `step5_leaching.py`
7. **Frontend** : pages Paramètres (édition tables fuzzy), Résultats (graphiques mensuels/annuels)

---

## Points de décision déjà tranchés

| Décision | Choix retenu |
|----------|-------------|
| Granularité de calcul | **Mensuelle** — agrégation annuelle pour visu uniquement |
| Fonctions d'appartenance | **Cosinus IN-Palm** (Sugeno 1985) — pas triangulaire/trapézoïdale |
| Valeurs des paramètres fuzzy | **En base** (paramétrables via UI) |
| Structure des règles fuzzy | **Dans le code** (immuable, c'est la science) |
| `FuzzyParamsLoader` | **Une instance par simulation**, passée aux modules |
| Modules partagés (N2-Baseline = N2-Mineral) | **Code partagé**, module_code différent en base |
| `palm_n_uptake_param` | Table par âge avec `yield_unfav/fav_limit` + `n_uptake_low/high` |

---

## Références

- **Pardon et al. (2019)** — IN-Palm Technical Report → `docs/`
- **Sugeno (1985)** — Fuzzy inference method
- **van der Werf & Zimmer (1998)** — Cosine membership functions
- **Bouwman et al. (2002a)** — Régression NH3 volatilisation organique
- **Bouwman et al. (2002b)** — Régression NOx emissions