# NBalance — Document de contexte projet

## 1. Contexte et objectifs

### Domaine
Agroécologie — Palmier à huile

### Objectif principal
Développer un **outil de diagnostic et d'aide à la décision** permettant de calculer le **bilan azoté** (N) avec l'ensemble des flux sur le cycle complet d'une plantation de palmier à huile.

### Utilisateurs cibles
Chercheurs en agroécologie (pas de gestion multi-utilisateurs dans la v1).

### Fonctionnalités clés
- Import de données terrain via fichiers CSV
- Gestion des paramètres de calcul et de simulation en base de données
- Calcul du bilan azoté annuel et sur le cycle complet
- Visualisation des résultats (graphiques, tableaux)
- Simulation de scénarios (modification de coefficients, jeux météo alternatifs)

---

## 2. Modélisation du bilan azoté

### Principe
**Bilan = Σ Entrées − Σ Sorties** (en kg N/ha/an)

### Entrées d'azote (+)

| Code | Flux | Source de données |
|------|------|-------------------|
| E1 | Azote minéral initial dans le sol | Caractéristiques parcelle (C organique, texture, pH, CEC) |
| E2 | Fixation biologique (légumineuses) | Données annuelles (Legume_fraction, Understorey_biomass) → logique floue |
| E3 | Azote des résidus | Précédent cultural (Previous_palm) + palmes élaguées (Pruned_frond) |
| E4 | Fertilisants synthétiques | Événements de fertilisation (type Mineral) |
| E5 | Fertilisants organiques | Événements de fertilisation (type Organic) |
| E6 | Dépôt atmosphérique | Données annuelles (Atmospheric_deposition) |

### Sorties d'azote (−)

| Code | Flux | Facteurs d'influence |
|------|------|----------------------|
| S1 | Volatilisation NH₃ | Type de fertilisant, placement, conditions climatiques |
| S2 | Lessivage NO₃⁻ | Pluviométrie, texture du sol, pente, terrasses |
| S3 | Captation par les palmiers | Rendement (tFFB/ha/an), âge de la plantation |
| S4 | Émissions N₂O (nitrification / dénitrification) | Méthode de calcul spécifique |
| S5 | Émissions NOx (nitrification / dénitrification) | Méthode de calcul spécifique |
| S6 | Émissions N₂ (dénitrification) | Méthode de calcul spécifique |
| S7 | Ruissellement | Pente, pluviométrie, terrasses, couverture du sol |

### Approches de calcul
- **Logique floue** pour la conversion des variables qualitatives (Legume_fraction, Understorey_biomass) en valeurs numériques
- **Méthodes de calcul configurables** par flux (possibilité de choisir entre différentes méthodes pour chaque simulation)
- **Variables intermédiaires** calculées et stockées pour la traçabilité

---

## 3. Données d'entrée

### Fichiers CSV importés

| Fichier | Contenu | Granularité | Clé de jointure |
|---------|---------|-------------|-----------------|
| Field_characteristics | Propriétés sol (texture, C organique, pH, CEC), pente, terrasses, précédent cultural | Par parcelle | Field_name + Localisation |
| Year_Field_data | Rendement, biomasse sous-étage, fraction légumineuses, gestion des palmes, dépôt atmosphérique | Par année × parcelle | Field_name + Localisation + Year |
| Rainfall_data | Pluviométrie (mm) et fréquence de pluie | Par mois × parcelle | Field_name + Localisation + Year + Month |
| Fertilization_data | Type (Mineral/Organic), quantité, composition, placement | Par événement (mois × parcelle) | Field_name + Localisation + Year + Month |

### Données de paramétrage (en base PostgreSQL)
- Propriétés N des fertilisants (teneur N, fractions NH₄⁺/NO₃⁻, conversion d'unités)
- Taux de volatilisation selon fertilisant × placement
- Facteurs d'émission N₂O, NOx, N₂ selon source et méthode
- Coefficients de lessivage selon texture × pente × terrasses
- Fonctions d'appartenance et règles d'inférence floue
- Paramètres de captation N par les palmiers selon l'âge
- Méthodes de calcul disponibles par type de flux

---

## 4. Options de simulation

- **Choix du jeu de données météo** : possibilité d'importer plusieurs fichiers Rainfall_data avec des noms de dataset différents et de sélectionner celui à utiliser pour chaque simulation
- **Choix des méthodes de calcul** : pour chaque flux, sélection de la méthode de calcul à appliquer
- **Modification de coefficients (scénarios what-if)** : possibilité de modifier ponctuellement des paramètres sans altérer les valeurs par défaut
- **Période de simulation** : cycle complet de la plantation

### Résultats produits
- **Bilan annuel** : détail de chaque flux d'entrée et de sortie, bilan net, variables intermédiaires
- **Bilan sur le cycle complet** : agrégation de tous les flux sur l'ensemble des années
- **Visualisations** : barres empilées entrées/sorties par année, camemberts de répartition, tableau détaillé, évolution temporelle

---

## 5. Architecture technique

### Stack

| Composant | Technologie | Rôle |
|-----------|------------|------|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) | API REST, moteur de calcul |
| Frontend | React 18 · Vite · Tailwind CSS · Recharts | Interface utilisateur |
| Base de données | PostgreSQL 16 | Données importées + paramétrage + résultats |
| CI/CD | GitLab CI · Docker | Build et déploiement |

### Structure du projet (monorepo)

```
nbalance/
├── backend/
│   ├── app/
│   │   ├── main.py                # Point d'entrée FastAPI
│   │   ├── config.py              # Configuration (Pydantic Settings)
│   │   ├── database.py            # Connexion BDD async
│   │   ├── models/                # Modèles SQLAlchemy (ORM)
│   │   ├── schemas/               # Schémas Pydantic (validation)
│   │   ├── routers/               # Endpoints API (import, fields, parameters, simulations)
│   │   ├── services/
│   │   │   ├── csv_parser.py      # Parsing et import des CSV
│   │   │   ├── fuzzy_engine.py    # Moteur de logique floue
│   │   │   └── n_balance/         # Moteur de calcul du bilan
│   │   │       ├── engine.py      # Orchestrateur (boucle annuelle)
│   │   │       ├── inputs.py      # Calcul des 6 flux d'entrée
│   │   │       └── outputs.py     # Calcul des 7 flux de sortie
│   │   └── utils/                 # Conversions d'unités
│   ├── alembic/                   # Migrations de schéma BDD
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/            # Layout, FileDropzone, PageHeader
│   │   ├── pages/                 # Dashboard, Import, Fields, Parameters, Simulations, Results
│   │   └── services/api.js        # Client Axios centralisé
│   ├── nginx.conf                 # Config Nginx (proxy API + SPA)
│   ├── package.json
│   └── Dockerfile
├── scripts/                       # Scripts de build et déploiement
│   ├── build-api.sh
│   ├── build-front.sh
│   ├── deploy-db.sh
│   ├── deploy-api.sh
│   ├── deploy-front.sh
│   ├── deploy-all.sh
│   └── cleanup.sh
├── docker-compose.yml
├── .gitlab-ci.yml
├── .env.example
└── README.md
```

### Infrastructure de déploiement
- **GitLab Runner Shell** installé sur le serveur de développement
- Images Docker construites et stockées localement sur le serveur
- Déploiement via scripts shell indépendants par conteneur
- 3 conteneurs : `nbalance-db` (PostgreSQL), `nbalance-api` (FastAPI), `nbalance-front` (Nginx + React)

### Pipeline CI/CD
1. **test** : compilation Python + build frontend (sur changements respectifs)
2. **build** : construction des images Docker (branches `main` et `develop`)
3. **deploy** : déploiement automatique sur `develop`, manuel sinon

---

## 6. Points à compléter

- [ ] Détail des formules de calcul pour chaque flux (E1→E6, S1→S7)
- [ ] Définition complète des fonctions d'appartenance floue et des règles d'inférence
- [ ] Liste exhaustive des méthodes de calcul disponibles par flux (avec références bibliographiques)
- [ ] Variables intermédiaires à stocker pour chaque calcul
- [ ] Valeurs par défaut des paramètres (facteurs d'émission, coefficients, etc.)
- [ ] Règles de validation des données CSV à l'import
- [ ] Exports de résultats (CSV, PDF, graphiques)
- [ ] Conteneur dédié à la gestion du schéma BDD (Alembic)

---

## 7. Équipe

| Rôle | Responsabilité |
|------|----------------|
| Chercheuse (Cécile) | Expertise métier, définition des formules et paramètres, validation des résultats |
| Développeur | Conception, développement backend/frontend, infrastructure |

---

*Document de référence — mis à jour au fil de l'avancement du projet.*	