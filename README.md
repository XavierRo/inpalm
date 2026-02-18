# 🌴 NBalance — Bilan Azoté du Palmier à Huile

Outil de diagnostic et d'aide à la décision pour le calcul du **bilan azoté** sur le cycle complet d'une plantation de palmier à huile.

## Présentation

NBalance modélise l'ensemble des **flux d'azote** (entrées et sorties) sur le cycle de vie d'une plantation, à partir de données terrain importées en CSV. L'application permet de :

- **Importer** des données de terrain (caractéristiques parcelle, pluviométrie, fertilisation, données annuelles)
- **Configurer** les paramètres de calcul (facteurs d'émission, coefficients de lessivage, logique floue, méthodes de calcul)
- **Simuler** le bilan azoté avec différents scénarios (jeux météo, coefficients modifiés)
- **Visualiser** les résultats (graphiques annuels, répartition des flux, bilan sur le cycle complet)

### Flux d'azote modélisés

**Entrées (+)** : azote initial du sol, fixation biologique (légumineuses), résidus, fertilisants synthétiques et organiques, dépôt atmosphérique.

**Sorties (−)** : volatilisation NH₃, lessivage NO₃⁻, captation par les palmiers, émissions N₂O / NOx / N₂, ruissellement.

## Stack technique

| Composant | Technologie |
|-----------|------------|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) |
| Frontend | React 18 · Vite · Tailwind CSS · Recharts |
| Base de données | PostgreSQL 16 |
| CI/CD | GitLab CI · Docker |

## Structure du projet

```
nbalance/
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d'entrée FastAPI
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Connexion BDD async
│   │   ├── models/              # Modèles SQLAlchemy
│   │   ├── schemas/             # Schémas Pydantic
│   │   ├── routers/             # Endpoints API
│   │   │   ├── import_data.py   # Upload CSV
│   │   │   ├── fields.py       # CRUD parcelles
│   │   │   ├── parameters.py   # CRUD paramètres
│   │   │   └── simulations.py  # Gestion simulations
│   │   ├── services/
│   │   │   ├── csv_parser.py    # Import CSV
│   │   │   ├── fuzzy_engine.py  # Logique floue
│   │   │   └── n_balance/       # Moteur de calcul
│   │   │       ├── engine.py    # Orchestrateur
│   │   │       ├── inputs.py    # Calcul entrées N
│   │   │       └── outputs.py   # Calcul sorties N
│   │   └── utils/
│   ├── alembic/                 # Migrations BDD
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # Composants réutilisables
│   │   ├── pages/               # Pages de l'application
│   │   └── services/api.js      # Client API
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .gitlab-ci.yml
└── README.md
```

## Développement local

### Prérequis

- Python 3.12+
- Node.js 20+
- PostgreSQL 16 (ou Docker pour la BDD uniquement)

### 1. Base de données

```bash
# Option A : Docker (recommandé)
docker compose up -d db

# Option B : PostgreSQL local
createdb nbalance
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

pip install -r requirements.txt

# Migrations
alembic upgrade head

# Lancer
uvicorn app.main:app --reload --port 8000
```

L'API est accessible sur http://localhost:8000/docs (Swagger).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

L'application est accessible sur http://localhost:5173.
Le proxy Vite redirige les appels `/api/*` vers le backend.

## Utilisation

### Workflow type

1. **Importer les données** via la page Import (glisser-déposer les CSV)
2. **Vérifier la parcelle** importée dans la page Parcelles
3. **Configurer les paramètres** (fertilisants, facteurs d'émission, logique floue...)
4. **Lancer une simulation** en choisissant la parcelle et le jeu de données météo
5. **Consulter les résultats** : bilan annuel, graphiques, répartition des flux

### Format des fichiers CSV

| Fichier | Contenu | Granularité |
|---------|---------|-------------|
| `Field_characteristics.csv` | Propriétés sol, pente, texture, précédent cultural | Par parcelle |
| `Year_Field_data.csv` | Rendement, biomasse, légumineuses, dépôt atm. | Par année |
| `Rainfall_data.csv` | Pluviométrie et fréquence de pluie | Par mois |
| `Fertilization_data.csv` | Apports minéraux et organiques | Par événement |

### API

Documentation Swagger interactive : http://localhost:8000/docs

Principaux endpoints :

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/import/field` | Import caractéristiques parcelle |
| POST | `/api/import/year-field` | Import données annuelles |
| POST | `/api/import/rainfall?dataset_name=...` | Import pluviométrie |
| POST | `/api/import/fertilization` | Import fertilisation |
| GET | `/api/fields/` | Liste des parcelles |
| GET/PUT | `/api/parameters/*` | Gestion des paramètres |
| POST | `/api/simulations/` | Lancer une simulation |
| GET | `/api/simulations/{id}/results` | Résultats d'une simulation |

## Docker

### Build et lancement complet

```bash
docker compose up -d --build
```

Services :
- **db** : PostgreSQL → port 5432
- **api** : Backend FastAPI → port 8000
- **front** : Frontend React (Nginx) → port 80

### Build des images seules

```bash
docker compose build api
docker compose build front
```

## Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | URL PostgreSQL async | `postgresql+asyncpg://nbalance:nbalance_dev@localhost:5432/nbalance` |
| `DATABASE_URL_SYNC` | URL PostgreSQL sync (Alembic) | `postgresql://nbalance:nbalance_dev@localhost:5432/nbalance` |

## Licence

Projet de recherche — CIRAD / Agroécologie.
