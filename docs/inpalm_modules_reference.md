# IN-Palm — Référence des modules de calcul
> Source : Pardon et al. (2019), *IN-Palm: An agri-environmental indicator to assess nitrogen losses in oil palm plantations*. Technical Report, CIRAD.

---

## Vue d'ensemble

IN-Palm calcule les pertes d'azote (N) pour **1 hectare de palmeraie**, sur un cycle de 1 à 30 ans, avec une granularité **mensuelle**. Il comporte **17 modules** regroupés en 5 étapes de calcul :

| Étape | Thème | Modules |
|-------|-------|---------|
| ① | Volatilisation NH₃ depuis les fertilisants | 1.1, 1.2 |
| ② | Calculs préliminaires : couverture sol et bilan hydrique | 2.1, 2.2, 2.3, 2.4 |
| ③ | Dénitrification depuis fertilisants + pertes par ruissellement | 3.1, 3.2, 3.3, 3.4 |
| ④ | Calculs préliminaires : azote minéral du sol | 4.1, 4.2, 4.3 |
| ⑤ | Dénitrification basale + lessivage depuis N minéral du sol | 5.1, 5.2, 5.3, 5.4 |

**Types de modèles utilisés :**
- **Fuzzy decision tree** (arbre de décision flou, Sugeno 1985) : 11 modules
- **Mass budget** (bilan de masse) : 3 modules
- **Regression model** (modèle de régression) : 3 modules

---

## Moteur de logique floue (commun à tous les modules fuzzy)

Toutes les fonctions d'appartenance utilisent **2 classes cosinus** (van der Werf & Zimmer, 1998) :

```
Membership_Favourable  = 0.5 × [1 + cos(input_value × π + π)]
Membership_Unfavourable = 0.5 × [1 + cos(input_value × π)]
```

Les valeurs d'entrée sont normalisées entre 0 et 1 avant application. Les variables nominales sont converties via des tables de correspondance (voir chaque module).

**Calcul de la valeur de vérité d'une règle i (MIN operator, Sugeno) :**
```
Truth_value_i = min(Membership_degree_j)  pour j = 1 à n facteurs de la règle
```

**Calcul de la sortie (moyenne pondérée, Sugeno) :**
```
Output = Σ(Truth_value_i × Conclusion_i) / Σ(Truth_value_i)
```

---

## Étape ① — Volatilisation NH₃ depuis les fertilisants

### Module 1.1 — R-NH₃-Mineral
**Type :** Fuzzy decision tree  
**Granularité :** Mensuelle  
**Périmètre :** Volatilisation NH₃ depuis les engrais minéraux

#### Variables d'entrée

| Variable | Unité | Plage / Classes | Nature |
|----------|-------|-----------------|--------|
| Mineral fertilizer rate | kg N ha⁻¹ mois⁻¹ | ≥ 0 | Continue |
| Mineral fertilizer type | — | Urea (0) / Ammonium sulfate (1) / Ammonium chloride (1) / Ammonium nitrate (1) / Sodium nitrate (1) | Nominale |
| Mineral fertilizer placement | — | In the circle, buried (1) / In the circle, not buried (0) / In the circle + windrow (0) / Evenly distributed (0) | Nominale |
| Number of rainy days | jours mois⁻¹ | 0–31 | Continue |
| Age of palms | années | 1–30 | Continue |
| Soil texture | — | Fine (1) / Medium (0.5) / Coarse (0) | Nominale |

#### Paramètres de l'arbre flou

| Facteur | Limite Unfav. | Limite Fav. |
|---------|--------------|-------------|
| Mineral fertilizer type | 0 (Urea) | 1 (Autres) |
| Mineral fertilizer placement | 0 (Non enterré) | 1 (Enterré) |
| Rain frequency | 7.5 j mois⁻¹ | 30 j mois⁻¹ |
| Age of palms | 4 ans | 10 ans |
| Soil texture | 0 (Grossière) | 1 (Fine) |

#### Structure de l'arbre (7 règles)

| Règle | Fertilizer type | Placement | Rain freq. | Palm age | Soil texture | Facteur émission (% N appliqué) |
|-------|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | F | | | | | Very_low — **2** |
| 2 | U | F | | | | Very_low — **2** |
| 3 | U | U | F | | | Low — **13** |
| 4 | U | U | U | F | F | Low — **13** |
| 5 | U | U | U | F | U | Medium — **24** |
| 6 | U | U | U | U | F | High — **34** |
| 7 | U | U | U | U | U | Very_high — **45** |

**Sortie :** Facteur d'émission mensuel NH₃ → **2 à 45 % du N appliqué**  
**Références :** Bouchet (2003), Chan & Chew (1984), Synasami et al. (1982)

---

### Module 1.2 — R-NH₃-Organic
**Type :** Regression model (Bouwman et al., 2002a)  
**Granularité :** Annuelle (divisée par 12 pour calculs mensuels)  
**Périmètre :** Volatilisation NH₃ depuis les engrais organiques

#### Équation

```
Annual_volatilisation = Organic_N_fertilizer_rate × exp(Σ correction_factor_i)
```

#### Variables d'entrée / paramètres fixes pour palmier

| Variable | Valeur IN-Palm | Unité |
|----------|---------------|-------|
| Organic N fertilizer rate | Variable terrain | kg N ha⁻¹ an⁻¹ |
| Organic fertilizer type | Animal manure (fixé) | — |
| Crop type | Upland crop (fixé) | — |
| Application mode | Broadcast (fixé) | — |
| Soil pH | ≤ 5.5 (fixé) | — |
| Soil CEC | ≤ 16 cmol kg⁻¹ (fixé) | — |
| Climate | Tropical (fixé) | — |

**Sortie :** N perdu par volatilisation NH₃ → **kg N ha⁻¹ an⁻¹**  
**Référence :** Bouwman et al. (2002a)

---

## Étape ② — Calculs préliminaires : couverture sol et bilan hydrique

### Module 2.1 — Litter Budget
**Type :** Mass budget  
**Granularité :** Annuelle  
**Périmètre :** Estimation de la quantité de litière (t MS ha⁻¹)

#### Équation

```
Litter(n+1) = Litter(n) + Inputs(n+1) − Decomposition(n+1)
```
avec `n+1` = âge des palmiers, toutes variables en t MS ha⁻¹.

#### Décomposition (modèle de Moradi et al., 2014)

```
Decomposition = Litter × (1 − exp(−k))
```

#### Valeurs de k par type de résidu

| Résidu | k | Méthode | C/N |
|--------|---|---------|-----|
| Trunk | 0.14 | (b) déduit C/N | 82 |
| Leaflets | 0.26 | (a) Moradi | 18 |
| Rachis | 0.12 | (a) Moradi | 107 |
| Spears | 0.26 | (c) hypothèse | — |
| Cabbage | 0.26 | (c) hypothèse | — |
| Frond bases | 0.12 | (c) hypothèse | — |
| Inflorescences | 0.20 | (c) hypothèse | — |
| Fronds | 0.15 | (a) Moradi | 41 |
| Roots | 0.11 | (b) déduit C/N | 117 |
| Compost | 0.21 | (b) déduit C/N | 30 |
| EFB (Empty Fruit Bunches) | 0.20 | (a) Moradi | 52 |

Relation k / C/N : `k = −0.074 × ln(C/N) + 0.4651` (R² = 0.79)

**Sortie :** Quantité annuelle de litière → **t MS ha⁻¹**

---

### Module 2.2 — Fraction of Soil Covered
**Type :** Fuzzy decision tree (18 règles, 6 facteurs)  
**Granularité :** Annuelle

#### Paramètres de l'arbre flou

| Facteur | Limite Unfav. | Limite Fav. | Note |
|---------|--------------|-------------|------|
| Understorey biomass | 0 t MS ha⁻¹ | 12.4 t MS ha⁻¹ | Nominale convertie : No=0, Low=3.1, Med=6.2, High=9.3, VHigh=12.4 |
| Fronds litter* | 0 t MS ha⁻¹ | 9 t MS ha⁻¹ | Variable intermédiaire (Module 2.1) |
| Fronds placement | 0 (Exporté/Heaps) | 1 (Spread anti-érosion) | Windrows=0.5 |
| Organic fertilizer litter* | 0 t MS ha⁻¹ | 25 t MS ha⁻¹ | Variable intermédiaire (Module 2.1) |
| Organic fertilizer placement | 0 (Circle/Path) | 1 (Spread) | Harvesting path=0.5 |
| Previous palms litter* | 20 t MS ha⁻¹ | 88 t MS ha⁻¹ | Variable intermédiaire (Module 2.1) |

**Sortie :** Fraction de sol couverte → **0 à 1**

---

### Module 2.3 — Water Runoff
**Type :** Fuzzy decision tree (5 règles, 4 facteurs)  
**Granularité :** Mensuelle

#### Paramètres de l'arbre flou

| Facteur | Limite Unfav. | Limite Fav. |
|---------|--------------|-------------|
| Rain intensity (= rainfall / rainy days) | 20 mm | 0 mm |
| Fraction of soil covered* | 0 | 1 |
| Slope | 25 % | 0 % |
| Terraces | 0 (Absence) | 1 (Présence) |

#### Structure de l'arbre (5 règles)

| Règle | Rain intensity | Soil cover | Slope | Terraces | Coefficient ruissellement (% pluie) |
|-------|:-:|:-:|:-:|:-:|:-:|
| 1 | F | | | | Very_low — **1** |
| 2 | U | F | | | Low — **10** |
| 3 | U | U | F | | High — **15** |
| 4 | U | U | U | F | High — **15** |
| 5 | U | U | U | U | Very_high — **20** |

**Sortie :** Coefficient de ruissellement mensuel → **1 à 20 % de la pluie**  
**Référence :** Sionita et al. (2014)

---

### Module 2.4 — Soil Water Budget
**Type :** Mass budget (adapté de Corley & Tinker, 2003)  
**Granularité :** Mensuelle

#### Équation

```
W(m+1) = W(m) + Rain(m+1) − Intercepted_water(m+1) − Water_runoff(m+1) − Evapotranspiration(m+1) − Drainage(m+1)
```
avec W = eau disponible pour les plantes (mm), m = mois.

#### Paramètres fixes

| Paramètre | Valeur |
|-----------|--------|
| Eau interceptée par la canopée | 0 % (an 1) → 11 % (≥ 10 ans), augmentation linéaire |
| ETP potentielle | 140 mm mois⁻¹ |
| Profondeur sol racinaire | 1.5 m |
| Capacité en eau disponible | Déduite de la texture (pédotransfert, Moody & Cong, 2008) |
| Capacité à saturation | Déduite de la texture |

**Logique :**
- `Evapotranspiration = min(ETP, W après Rain − Interception − Runoff)`
- `Drainage = max(0, W − Capacité en eau disponible)` après déduction ETP

**Sorties :** Eau disponible mensuelle (mm) + Drainage mensuel (mm)

---

## Étape ③ — Dénitrification depuis fertilisants et ruissellement

### Module 3.1 — R-N₂O-Mineral
**Type :** Fuzzy decision tree (32 règles, 5 facteurs)  
**Granularité :** Mensuelle  
**Périmètre :** Émissions N₂O depuis engrais minéraux

#### Paramètres de l'arbre flou

| Facteur | Limite Unfav. | Limite Fav. | Note |
|---------|--------------|-------------|------|
| Soil moisture* | 100 % (cap. + sat.) | 0 % | Variable intermédiaire (Module 2.4) |
| Soil texture | 0 (Fine) | 1 (Medium) | Coarse=0.5 |
| Soil organic C | 3 % | 1 % | |
| Litter amount* | 130 t MS ha⁻¹ | 10 t MS ha⁻¹ | Variable intermédiaire (Module 2.1) |
| Mineral fertilizer rate | 250 kg N ha⁻¹ mois⁻¹ | 0 | |

> Note texture N₂O : Fine=0, Medium=1, Coarse=0.5 (différent du module NH₃ !)

#### Structure de l'arbre (32 règles, extrait représentatif)

La sortie varie de Very_low (0.01 %) à Very_high (10.6 %) du N appliqué. Les règles combinent les 5 facteurs (F/U) avec toutes les combinaisons binaires, pondérées par la logique floue.

**Sortie :** Facteur d'émission mensuel N₂O → **0.01 à 10.6 % du N appliqué** (max 13.0 % selon table A.3)  
**Références :** Banabas (2007), Ishizuka et al. (2005), Stehfest & Bouwman (2006)

---

### Module 3.2 — R-N₂-Mineral
**Type :** Fuzzy decision tree (2 règles, 1 facteur)  
**Granularité :** Mensuelle  
**Périmètre :** Émissions N₂ depuis engrais minéraux

#### Paramètres de l'arbre flou

| Facteur | Limite Unfav. | Limite Fav. |
|---------|--------------|-------------|
| Soil saturation* (% capacité à saturation) | 100 % | 0 % |

#### Structure de l'arbre

| Règle | Soil saturation | Ratio N₂/N₂O |
|-------|:-:|:-:|
| 1 | F | Low — **1.92** |
| 2 | U | High — **9.96** |

**Calcul final :** `N₂_Mineral = N₂O_Mineral × (N₂/N₂O ratio)`  
**Référence :** Vinther (2005)

---

### Module 3.3 — R-NOx-Mineral/Organic
**Type :** Regression model (Bouwman et al., 2002b)  
**Granularité :** Annuelle (÷ 12 pour calculs mensuels)  
**Périmètre :** Émissions NOx depuis engrais minéraux et organiques

#### Équation

```
Annual_NOx_emission = exp(−1.527 + Σ correction_factor_i)
```

**Variables d'entrée :** Taux N engrais minéral (kg N ha⁻¹ mois⁻¹), taux N engrais organique (kg N ha⁻¹ an⁻¹), types d'engrais, texture sol, teneur en C organique.

> Note : Le modèle estime ensemble émissions fertilisant + émissions basales. Les émissions basales sont **soustraites** pour n'isoler que les émissions induites par les fertilisants.

**Sortie :** Pertes N par NOx → **kg N ha⁻¹ an⁻¹** (directement)  
**Référence :** Bouwman et al. (2002b)

---

### Module 3.4 — R-Runoff-Erosion
**Type :** Fuzzy decision tree (9 règles, 5 facteurs)  
**Granularité :** Mensuelle  
**Périmètre :** Pertes N par ruissellement-érosion (engrais minéraux + dépôts atmosphériques)

#### Paramètres de l'arbre flou

| Facteur | Limite Unfav. | Limite Fav. | Note |
|---------|--------------|-------------|------|
| Rain intensity | 20 mm | 0 mm | = Rainfall / rainy days |
| Soil texture | 0 (Grossière) | 1 (Fine) | Coarse=0, Medium=0.5, Fine=1 |
| Fraction of soil covered* | 0 | 1 | Variable intermédiaire (Module 2.2) |
| Slope | 25 % | 0 % | |
| Terraces | 0 (Absence) | 1 (Présence) | |

#### Structure de l'arbre (9 règles)

| Règle | Rain | Texture | Cover | Slope | Terraces | Facteur (% N appliqué) |
|-------|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | F | | | | | Very_low — **1** |
| 2 | U | F | F | | | Very_low — **1** |
| 3 | U | F | U | F | | Very_low — **1** |
| 4 | U | F | U | U | F | Medium_high — **10** |
| 5 | U | F | U | U | U | High — **15** |
| 6 | U | U | F | | | Low — **2.5** |
| 7 | U | U | U | F | | Low — **2.5** |
| 8 | U | U | U | U | F | High — **15** |
| 9 | U | U | U | U | U | Very_high — **20** |

**Sortie :** Facteur d'émission mensuel → **1 à 20 % de (N engrais minéral + N dépôt atmosphérique)**  
**Références :** Kee & Chew (1996), Maena et al. (1979), Sionita et al. (2014)

---

## Étape ④ — Calculs préliminaires : azote minéral du sol

### Module 4.1 — Palm N Uptake
**Type :** Fuzzy decision tree (2 facteurs, table par âge)  
**Granularité :** Annuelle  
**Périmètre :** Absorption N par les palmiers

#### Paramètres par âge (limites favorable/défavorable pour le rendement)

| Âge | Limite Unfav. (t FFB ha⁻¹ an⁻¹) | Limite Fav. (t FFB ha⁻¹ an⁻¹) | Uptake Low (kg N ha⁻¹ an⁻¹) | Uptake High (kg N ha⁻¹ an⁻¹) |
|-----|:-:|:-:|:-:|:-:|
| 0 | 0 | 0 | 0 | 0 |
| 1–2 | 0 | 0 | 2–10 | 2–10 |
| 3 | 0 | 5 | 22 | 53 |
| 4 | 5 | 15 | 81 | 140 |
| 5 | 10 | 25 | 167 | 225 |
| 6–7 | 15 | 35 | 187–203 | 282–297 |
| 8–20 | 15 | 40 | 205–214 | 287–321 |
| > 20 | 15 | 40 | 189–199 | 287–308 |

*Calibré sur 58 500 simulations APSIM-Oil Palm (Papua New Guinea)*

**Sortie :** Absorption N annuelle par les palmiers → **2.2 à 321 kg N ha⁻¹ an⁻¹**  
**Référence :** Pardon et al. (2017)

---

### Module 4.2 — Understorey N Uptake/Fixation
**Type :** Fuzzy decision tree (2 règles, 1 facteur principal + contexte biomasse/légumineuses)  
**Granularité :** Mensuelle  
**Périmètre :** Fixation N atmosphérique et absorption N sol par le sous-étage

#### Paramètres de l'arbre flou

| Facteur | Limite Unfav. | Limite Fav. |
|---------|--------------|-------------|
| Soil mineral N available* (kg N ha⁻¹ an⁻¹) | 60 | 0 |

#### Structure de l'arbre

| Règle | Soil mineral N | % N fixé atmosphere |
|-------|:-:|:-:|
| 1 | F (faible N dispo → légumineuse fixe) | High — **90 %** |
| 2 | U (fort N dispo → absorption sol) | No_fixation — **0 %** |

**Calcul final :**
```
N_fixed = Understorey_biomass_N_need × fixation_rate
N_uptake_from_soil = Understorey_biomass_N_need × (1 − fixation_rate)
```

**Sorties :** Taux de fixation mensuel (0–90 %) + N fixé (kg N ha⁻¹ an⁻¹) + N prélevé sol (kg N ha⁻¹ an⁻¹)  
**Références :** Agamuthu & Broughton (1985), Pipai (2014)

---

### Module 4.3 — Soil Mineral N Budget
**Type :** Mass budget  
**Granularité :** Mensuelle  
**Périmètre :** Bilan azote minéral dans le sol

#### Équation

```
Soil_mineral_N(m+1) = Soil_mineral_N(m)
  + Fertilizer_N_net_release(m+1)
  + Atmospheric_deposition_N_net_release(m+1)
  + Litter_N_net_release(m+1)
  − Palm_N_uptake(m+1)
  − Understorey_N_uptake(m+1)
  − N_losses(m+1)
  + Net_soil_organic_N_mineralization(m+1)
```

#### Paramètres

| Paramètre | Valeur | Référence |
|-----------|--------|-----------|
| N minéral sol initial (équilibre) | 45 à 55.2 kg N ha⁻¹ m⁻¹ (selon texture) | Allen et al. (2015) |
| N organique sol initial (équilibre) | 14.4 à 26 t N ha⁻¹ m⁻¹ (selon texture) | Allen et al. (2015) |

#### Teneur en N des résidus de palmier

| Résidu | N (% MS) |
|--------|----------|
| Trunk | 0.56 |
| Leaflets | 2.18 |
| Rachis | 0.45 |
| Spears | 2.14 |
| Cabbage | 3.12 |
| Frond bases | 0.23 |
| Inflorescences | 1.94 |
| Roots | 0.32 |

> Quand N minéral sol < équilibre → minéralisation nette estimée pour ramener au niveau d'équilibre.

**Sorties :** N minéral disponible mensuel (kg N ha⁻¹) pour : palmiers / sous-étage / pertes / fin de mois

---

## Étape ⑤ — Dénitrification basale et lessivage depuis N minéral du sol

### Module 5.1 — R-N₂O-Baseline
**Type :** Fuzzy decision tree (16 règles, 4 facteurs)  
**Granularité :** Mensuelle  
**Périmètre :** Émissions N₂O basales depuis N minéral du sol

> Structure identique à Module 3.1 (R-N₂O-Mineral) **mais sans le facteur "Mineral fertilizer rate"**.

#### Paramètres de l'arbre flou

| Facteur | Limite Unfav. | Limite Fav. |
|---------|--------------|-------------|
| Soil moisture* | 100 % | 0 % |
| Soil texture | 0 (Fine) | 1 (Medium) |
| Soil organic C | 3 % | 1 % |
| Litter amount* | 130 t MS ha⁻¹ | 10 t MS ha⁻¹ |

**Sortie :** Facteur d'émission mensuel N₂O baseline → **0.1 à 1.1 % du N minéral du sol disponible**  
(plage complète : 0.1 à 2.5 % selon table A.2)

---

### Module 5.2 — R-N₂-Baseline
**Type :** Fuzzy decision tree (même arbre que Module 3.2)  
**Calcul :** `N₂_Baseline = N₂O_Baseline × (N₂/N₂O ratio du Module 3.2)`

---

### Module 5.3 — R-NOx-Baseline
**Type :** Regression model (Bouwman et al., 2002a)  
**Calcul :** Même modèle que Module 3.3 **mais avec taux engrais = 0** (émissions basales uniquement).

---

### Module 5.4 — R-Leaching
**Type :** Fuzzy decision tree (2 règles, 1 facteur)  
**Granularité :** Mensuelle  
**Périmètre :** Lessivage NO₃⁻ depuis N minéral du sol

#### Paramètres de l'arbre flou

| Facteur | Limite Unfav. | Limite Fav. |
|---------|--------------|-------------|
| Water above field capacity* (% capacité à saturation) | 50 % | 0 % |

#### Structure de l'arbre

| Règle | Drainage | Facteur lessivage (% N minéral sol) |
|-------|:-:|:-:|
| 1 | F | No — **0** |
| 2 | U | High — **20** |

**Sortie :** Facteur d'émission mensuel → **0 à 20 % du N minéral du sol disponible**  
**Références :** Ah Tung et al. (2009), Chang & Abas (1986), Foong et al. (1983), Foong (1993), Omoti et al. (1983)

---

## Récapitulatif des dépendances entre modules (ordre de calcul)

```
Données terrain + paramètres fixes
        │
        ▼
[2.1] Litter Budget ─────────────────────────────────────────────────────────────┐
        │                                                                         │
        ▼                                                                         │
[2.2] Fraction of Soil Covered ←── (litter fronds, organic fert, prev palms)    │
        │                                                                         │
        ▼                                                                         │
[2.3] Water Runoff ←── (rain intensity, soil cover, slope, terraces)             │
        │                                                                         │
        ▼                                                                         │
[2.4] Soil Water Budget ←── (rain, runoff)                                       │
  → soil_moisture, drainage, soil_saturation                                     │
        │                                                                         │
        ├─────────────────────────────────────────────────────────────────────── ▼
        │
[1.1] R-NH₃-Mineral     ←── (fertilizer type, placement, rain freq, age, texture)
[1.2] R-NH₃-Organic     ←── (organic N rate, fixed params)
[3.1] R-N₂O-Mineral     ←── (soil moisture, texture, orgC, litter, mineral N rate)
[3.2] R-N₂-Mineral      ←── (soil saturation) → N₂/N₂O ratio
[3.3] R-NOx-Mineral/Org ←── (mineral+organic rates, types, texture, orgC)
[3.4] R-Runoff-Erosion  ←── (rain intensity, texture, soil cover, slope, terraces)
        │
        ▼
[4.1] Palm N Uptake     ←── (age, yield)
[4.2] Understorey N Fixation ←── (soil mineral N available)
[4.3] Soil Mineral N Budget  ←── (tous les flux ci-dessus)
  → soil_mineral_N_available (pour palmiers, sous-étage, pertes)
        │
        ▼
[5.1] R-N₂O-Baseline   ←── (soil moisture, texture, orgC, litter)
[5.2] R-N₂-Baseline    ←── (N₂O baseline × ratio Module 3.2)
[5.3] R-NOx-Baseline   ←── (Bouwman, taux fertilisant = 0)
[5.4] R-Leaching        ←── (drainage % saturation)
```

---

## Scores INDIGO®

Conversion des pertes (kg N ha⁻¹ an⁻¹) en scores 0–10 :

```
si perte < 2R  : Score = −3 × perte/R + 10
si 2R < perte < 6R : Score = −perte/R + 6
si perte > 6R  : Score = 0
```

Avec R = valeur de référence = 50 % des pertes avec pratiques standard (Pardon et al., 2016a).

#### Valeurs de référence R par âge (kg N ha⁻¹)

| Voie de perte | Âge 0 | 1 | 2 | 3–5 | 6–20 | 21–25+ |
|---------------|:--:|:--:|:--:|:--:|:--:|:--:|
| NH₃ | 0 | 7 | 9 | 4–5 | 5 | 5 |
| N₂O | 0 | 2.4 | 2.8 | 2.6–2.7 | 1.9–2.2 | 1.9–2.0 |
| NOx | 0 | 0.7 | 0.9 | 0.7–0.8 | 0.8 | 0.8 |
| Runoff-Erosion | 0 | 0.3 | 0.6 | 0.9–3.8 | 5.0–6.0 | 6.0 |
| Leaching | 0 | 56 | 45 | 30–38 | 13–20 | 14–20 |

---

## Variables d'entrée terrain (21 variables)

| Type | Variable | Unité | Plage |
|------|----------|-------|-------|
| Crop | Age of palms | années | 0–30 |
| Crop | Expected yield (after 3 years) | t FFB ha⁻¹ an⁻¹ | 0–40 |
| Soil/Land | Soil initial mineral N | kg N ha⁻¹ | ≥ 0 |
| Soil/Land | Soil initial water content | mm | ≥ 0 |
| Soil/Land | Soil organic C | % | 0–10 |
| Soil/Land | Slope | % | 0–30 |
| Soil/Land | Terraces | — | Yes / No |
| Soil/Land | Soil texture | — | 12 classes FAO → Fine/Medium/Coarse |
| Weather | Number of rainy days | jours mois⁻¹ | 0–31 |
| Weather | Monthly rainfall | mm | ≥ 0 |
| Weather | Atmospheric N deposition | kg N ha⁻¹ an⁻¹ | ≥ 0 |
| Fertilizer | Rate/Date mineral fertilizer | kg ha⁻¹ | ≥ 0 |
| Fertilizer | Type mineral fertilizer | — | Urea / NH₄SO₄ / NH₄Cl / NH₄NO₃ / NaNO₃ |
| Fertilizer | Placement mineral fertilizer | — | Circle buried / Circle not buried / Circle+windrow / Evenly |
| Fertilizer | Rate/Date organic fertilizer | t FM ha⁻¹ | — |
| Fertilizer | Type organic fertilizer | — | Compost / EFB |
| Fertilizer | Placement organic fertilizer | — | Circle / Harvesting path / Spread |
| Understorey | Fronds | — | Exported / In heaps / In windrows |
| Understorey | Understorey biomass | — | No / Low / Medium / High / Very high |
| Understorey | Legume fraction | — | No / Low / Medium / High / Very high |
| Understorey | Previous palm residues | — | Yes / No |

---

*Référence complète : Pardon, L. et al. (2019). IN-Palm: An agri-environmental indicator to assess nitrogen losses in oil palm plantations. Technical Report, CIRAD/SMART Research Institute.*