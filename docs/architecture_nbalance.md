# NBalance — Architecture du projet

## Outil de diagnostic et d'aide à la décision pour le bilan azoté du palmier à huile

---

## 1. Vue d'ensemble

### Stack technique
- **Backend** : Python + FastAPI
- **Frontend** : React
- **Base de données** : PostgreSQL
- **Pas de gestion utilisateur** (v1)

### Principe
L'application calcule le **bilan azoté** (Σ Entrées - Σ Sorties) sur le cycle complet d'une plantation de palmier à huile, avec une granularité **annuelle** et un récapitulatif sur l'ensemble du cycle.

---

## 2. Flux d'azote modélisés

### Entrées (+)
| # | Flux | Source de données |
|---|------|-------------------|
| E1 | Azote minéral initial dans le sol | Field_characteristics (Organic_Carbon, texture, pH, CEC) |
| E2 | Fixation biologique (légumineuses) | Year_Field_data (Legume_fraction → logique floue) |
| E3 | Azote des résidus (précédent + palmes) | Field_characteristics (Previous_palm) + Year_Field_data (Pruned_frond) |
| E4 | Fertilisants synthétiques | Fertilization_data (type=Mineral) |
| E5 | Fertilisants organiques | Fertilization_data (type=Organic) |
| E6 | Dépôt atmosphérique | Year_Field_data (Atmospheric_deposition) |

### Sorties (-)
| # | Flux | Facteurs d'influence |
|---|------|---------------------|
| S1 | Volatilisation NH₃ | Type fertilisant, placement, conditions climatiques |
| S2 | Lessivage NO₃⁻ | Pluviométrie, texture sol, pente, terrasses |
| S3 | Captation par les palmiers | Rendement (Yield tFFB/ha/an), âge plantation |
| S4 | Émissions N₂O (nitrification/dénitrification) | Méthode de calcul spécifique |
| S5 | Émissions NOx (nitrification/dénitrification) | Méthode de calcul spécifique |
| S6 | Émissions N₂ (dénitrification) | Méthode de calcul spécifique |
| S7 | Ruissellement | Pente, pluviométrie, terrasses, couverture sol |

---

## 3. Schéma de base de données

### 3.1 Données importées (CSV → tables miroir)

```
┌─────────────────────────────┐
│         field                │  ← Field_characteristics
├─────────────────────────────┤
│ id (PK, serial)             │
│ field_name (varchar)        │
│ localisation (varchar)      │
│ year_planting (int)         │
│ end_field (int)             │
│ slope (float)               │
│ texture (varchar)           │
│ organic_carbon (float)      │
│ initial_soil_water (float)  │
│ ph (float)                  │
│ cec (float)                 │
│ previous_palm (varchar)     │
│ terraces (varchar)          │
│ created_at (timestamp)      │
└─────────────────────────────┘

┌──────────────────────────────┐
│      year_field_data          │  ← Year_Field_data
├──────────────────────────────┤
│ id (PK, serial)              │
│ field_id (FK → field)        │
│ year (int)                   │
│ yield_tffb_ha (float)        │
│ understorey_biomass (varchar)│
│ legume_fraction (varchar)    │
│ pruned_frond (varchar)       │
│ atmospheric_deposition (float)│
└──────────────────────────────┘

┌──────────────────────────────┐
│      rainfall_data            │  ← Rainfall_data
├──────────────────────────────┤
│ id (PK, serial)              │
│ field_id (FK → field)        │
│ year (int)                   │
│ month (varchar)              │
│ rainfall_mm (float)          │
│ rain_frequency (int)         │
│ dataset_name (varchar)       │  ← pour gérer plusieurs jeux météo
└──────────────────────────────┘

┌──────────────────────────────┐
│      fertilization_data       │  ← Fertilization_data
├──────────────────────────────┤
│ id (PK, serial)              │
│ field_id (FK → field)        │
│ year (int)                   │
│ month (varchar)              │
│ fertilization_type (varchar) │
│ quantity (float)             │
│ unit (varchar)               │
│ composition (varchar)        │
│ placement (varchar)          │
└──────────────────────────────┘
```

### 3.2 Tables de paramétrage (en base, éditables)

```
┌──────────────────────────────────┐
│     fertilizer_properties         │  Propriétés des fertilisants
├──────────────────────────────────┤
│ id (PK)                          │
│ name (varchar) — ex: Urea        │
│ type (varchar) — Mineral/Organic │
│ n_content (float) — % N          │
│ nh4_fraction (float)             │
│ no3_fraction (float)             │
│ organic_n_fraction (float)       │
│ unit_conversion (float)          │  ← pour convertir tFM → kg N/ha etc.
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     volatilization_params         │  Paramètres de volatilisation
├──────────────────────────────────┤
│ id (PK)                          │
│ fertilizer_type (varchar)        │
│ placement (varchar)              │
│ base_rate (float)                │  ← taux de volatilisation de base
│ ... (autres coefficients)        │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     emission_factors              │  Facteurs d'émission N₂O, NOx, N₂
├──────────────────────────────────┤
│ id (PK)                          │
│ flux_type (varchar)              │  ← N2O, NOx, N2
│ source (varchar)                 │  ← synthetic, organic, residues...
│ method (varchar)                 │  ← nom de la méthode de calcul
│ factor_value (float)             │
│ description (text)               │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     leaching_params               │  Paramètres de lessivage
├──────────────────────────────────┤
│ id (PK)                          │
│ texture (varchar)                │
│ slope_class (varchar)            │
│ base_leaching_fraction (float)   │
│ ... (autres coefficients)        │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     fuzzy_membership              │  Logique floue
├──────────────────────────────────┤
│ id (PK)                          │
│ variable_name (varchar)          │  ← ex: Legume_fraction
│ linguistic_value (varchar)       │  ← ex: High, Medium, Low
│ membership_type (varchar)        │  ← triangular, trapezoidal...
│ params (jsonb)                   │  ← {a: 0, b: 0.3, c: 0.6} etc.
│ output_min (float)               │
│ output_max (float)               │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     fuzzy_rules                   │  Règles d'inférence floue
├──────────────────────────────────┤
│ id (PK)                          │
│ rule_set_name (varchar)          │  ← ex: N_fixation
│ conditions (jsonb)               │  ← {"Legume_fraction": "High", ...}
│ output_value (float)             │  ← kg N/ha/an résultant
│ weight (float)                   │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     palm_n_uptake_params          │  Captation N par les palmiers
├──────────────────────────────────┤
│ id (PK)                          │
│ age_min (int)                    │
│ age_max (int)                    │
│ n_per_tffb (float)              │  ← kg N par tonne FFB
│ vegetative_n_demand (float)      │  ← demande N végétative (tronc, feuilles)
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     calculation_methods           │  Méthodes de calcul disponibles
├──────────────────────────────────┤
│ id (PK)                          │
│ flux_type (varchar)              │  ← ex: volatilization, leaching, N2O
│ method_name (varchar)            │  ← ex: "IPCC_2019", "Custom_tropical"
│ description (text)               │
│ formula_reference (text)         │  ← référence biblio
│ is_default (boolean)             │
└──────────────────────────────────┘
```

### 3.3 Tables de simulation et résultats

```
┌──────────────────────────────────┐
│     simulation                    │  Configuration d'une simulation
├──────────────────────────────────┤
│ id (PK, uuid)                    │
│ name (varchar)                   │
│ field_id (FK → field)            │
│ rainfall_dataset (varchar)       │  ← choix du jeu météo
│ created_at (timestamp)           │
│ description (text)               │
│ status (varchar)                 │  ← pending, running, completed, error
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     simulation_options            │  Options/méthodes choisies
├──────────────────────────────────┤
│ id (PK)                          │
│ simulation_id (FK → simulation)  │
│ flux_type (varchar)              │
│ method_id (FK → calculation_methods) │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     simulation_overrides          │  Coefficients modifiés (scénarios)
├──────────────────────────────────┤
│ id (PK)                          │
│ simulation_id (FK → simulation)  │
│ param_table (varchar)            │  ← table d'origine du paramètre
│ param_id (int)                   │  ← id du paramètre modifié
│ param_field (varchar)            │  ← nom du champ modifié
│ original_value (float)           │
│ override_value (float)           │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     simulation_results_yearly     │  Résultats annuels
├──────────────────────────────────┤
│ id (PK)                          │
│ simulation_id (FK → simulation)  │
│ year (int)                       │
│ palm_age (int)                   │
│ — Entrées —                      │
│ n_initial_soil (float)           │  ← E1 (année 1 uniquement)
│ n_fixation (float)               │  ← E2
│ n_residues (float)               │  ← E3
│ n_synthetic_fertilizer (float)   │  ← E4
│ n_organic_fertilizer (float)     │  ← E5
│ n_atmospheric_deposition (float) │  ← E6
│ total_inputs (float)             │
│ — Sorties —                      │
│ n_volatilization (float)         │  ← S1
│ n_leaching (float)               │  ← S2
│ n_palm_uptake (float)            │  ← S3
│ n_n2o_emission (float)           │  ← S4
│ n_nox_emission (float)           │  ← S5
│ n_n2_emission (float)            │  ← S6
│ n_runoff (float)                 │  ← S7
│ total_outputs (float)            │
│ — Bilan —                        │
│ balance (float)                  │  ← total_inputs - total_outputs
│ — Variables intermédiaires —     │
│ intermediate_results (jsonb)     │  ← stockage flexible
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     simulation_results_cycle      │  Résultat sur le cycle complet
├──────────────────────────────────┤
│ id (PK)                          │
│ simulation_id (FK → simulation)  │
│ total_n_inputs (float)           │
│ total_n_outputs (float)          │
│ total_balance (float)            │
│ summary (jsonb)                  │  ← détail par flux sur tout le cycle
└──────────────────────────────────┘
```

---

## 4. Architecture API (FastAPI)

### 4.1 Structure du projet

```
nbalance/
├── alembic/                    # Migrations DB
├── app/
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── config.py               # Configuration (DB, etc.)
│   ├── database.py             # Session SQLAlchemy / connexion
│   ├── models/                 # Modèles SQLAlchemy (ORM)
│   │   ├── field.py
│   │   ├── rainfall.py
│   │   ├── fertilization.py
│   │   ├── year_field.py
│   │   ├── parameters.py       # Tous les paramètres
│   │   ├── simulation.py
│   │   └── results.py
│   ├── schemas/                # Schémas Pydantic (validation)
│   │   ├── field.py
│   │   ├── rainfall.py
│   │   ├── fertilization.py
│   │   ├── simulation.py
│   │   └── results.py
│   ├── routers/                # Endpoints API
│   │   ├── import_data.py      # Upload CSV
│   │   ├── fields.py           # CRUD parcelles
│   │   ├── parameters.py       # CRUD paramètres
│   │   ├── simulations.py      # Lancer / gérer simulations
│   │   └── results.py          # Consulter résultats
│   ├── services/               # Logique métier
│   │   ├── csv_parser.py       # Parsing et validation CSV
│   │   ├── fuzzy_engine.py     # Moteur logique floue
│   │   └── n_balance/          # Calculs du bilan
│   │       ├── engine.py       # Orchestrateur du calcul
│   │       ├── inputs.py       # Calcul des entrées N
│   │       ├── outputs.py      # Calcul des sorties N
│   │       ├── volatilization.py
│   │       ├── leaching.py
│   │       ├── emissions.py    # N2O, NOx, N2
│   │       ├── palm_uptake.py
│   │       ├── runoff.py
│   │       └── residues.py
│   └── utils/
│       └── units.py            # Conversions d'unités
├── tests/
├── requirements.txt
└── docker-compose.yml          # PostgreSQL + API
```

### 4.2 Endpoints principaux

```
POST   /api/import/field                  # Upload Field_characteristics CSV
POST   /api/import/rainfall               # Upload Rainfall CSV (+ dataset_name)
POST   /api/import/fertilization          # Upload Fertilization CSV
POST   /api/import/year-field             # Upload Year_Field_data CSV

GET    /api/fields                        # Liste des parcelles
GET    /api/fields/{id}                   # Détail parcelle + données associées

GET    /api/parameters/fertilizers        # Liste propriétés fertilisants
PUT    /api/parameters/fertilizers/{id}   # Modifier un fertilisant
GET    /api/parameters/emission-factors   # Facteurs d'émission
PUT    /api/parameters/emission-factors/{id}
GET    /api/parameters/fuzzy              # Règles logique floue
PUT    /api/parameters/fuzzy/{id}
GET    /api/parameters/methods            # Méthodes de calcul disponibles
# ... idem pour tous les paramètres

POST   /api/simulations                   # Créer et lancer une simulation
GET    /api/simulations                   # Liste des simulations
GET    /api/simulations/{id}              # Détail + statut
GET    /api/simulations/{id}/results      # Résultats annuels + cycle
POST   /api/simulations/{id}/compare      # Comparer avec une autre simulation

DELETE /api/simulations/{id}              # Supprimer
```

### 4.3 Workflow type d'une simulation

```
1. Import CSV ──→ Données en base
                      │
2. Vérifier/éditer paramètres (optionnel)
                      │
3. POST /api/simulations
   {
     "name": "Sangara baseline",
     "field_id": 1,
     "rainfall_dataset": "observed_2008_2015",
     "method_choices": {
       "volatilization": "method_placement_adjusted",
       "leaching": "method_texture_slope",
       "n2o": "ipcc_2019_tropical",
       "nox": "default",
       "n2": "default",
       "runoff": "slope_rainfall"
     },
     "overrides": []    ← ou liste de coefficients modifiés
   }
                      │
4. Moteur de calcul (engine.py)
   Pour chaque année du cycle :
     a. Calcul des entrées N (E1→E6)
     b. Calcul des variables intermédiaires
     c. Calcul des sorties N (S1→S7)
     d. Bilan annuel
                      │
5. Agrégation cycle complet
                      │
6. Résultats stockés en base ──→ API results ──→ Frontend
```

---

## 5. Frontend React (grandes lignes)

### Pages principales

| Page | Description |
|------|-------------|
| **Dashboard** | Vue d'ensemble des parcelles et simulations |
| **Import données** | Upload CSV avec prévisualisation et validation |
| **Fiche parcelle** | Détail d'une parcelle avec ses données (graphiques pluvio, fertilisation...) |
| **Paramètres** | Édition des tables de paramétrage (fertilisants, facteurs, logique floue) |
| **Nouvelle simulation** | Choix parcelle, jeu météo, méthodes de calcul, overrides |
| **Résultats** | Tableau annuel + graphiques (barres empilées entrées/sorties, évolution du bilan, Sankey des flux) |
| **Comparaison** | Mise en parallèle de 2+ simulations (scénarios) |

---

## 6. Points à compléter ensemble

- [ ] Détail des formules de calcul pour chaque flux
- [ ] Définition complète des fonctions d'appartenance floue
- [ ] Liste exhaustive des méthodes de calcul par flux
- [ ] Variables intermédiaires à stocker
- [ ] Paramètres manquants identifiés par la chercheuse
- [ ] Règles de validation des données CSV
- [ ] Exports de résultats (CSV, PDF, graphiques)