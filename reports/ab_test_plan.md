# Plan A/B Test — Déploiement du Modèle de Détection de Fraude
## Projet DDDM — Détection de Fraude Bancaire

---

## 1. Contexte & Objectif

Le modèle XGBoost de détection de fraude a été développé et validé en laboratoire (AUC-ROC = 0.963, Recall = 85%). Avant un déploiement complet en production, un test A/B contrôlé est nécessaire pour mesurer son impact réel par rapport au système actuel basé sur des règles métier.

**Objectif du test :** Valider que le modèle XGBoost réduit significativement le taux de fraude non détectée, sans dégrader l'expérience client (taux de faux positifs).

---

## 2. Hypothèses statistiques

| | Description |
|---|---|
| **H₀ (nulle)** | Le modèle XGBoost ne réduit pas le taux de fraude non détectée par rapport au système de règles actuel (Δ Recall = 0) |
| **H₁ (alternative)** | Le modèle XGBoost réduit le taux de fraude non détectée d'au moins **30 points de pourcentage** (Δ Recall ≥ 30 pts) |
| **Seuil α** | 0.05 (risque d'erreur de type I) |
| **Puissance (1-β)** | 0.80 (risque d'erreur de type II = 20%) |
| **Test statistique** | Test Z à deux proportions (taux de fraude détecté) |

---

## 3. Design expérimental

### 3.1 Groupes

| Groupe | Système | Population |
|---|---|---|
| **Contrôle (A)** | Système de règles métier actuel (score_expert) | 50 000 transactions |
| **Test (B)** | Modèle XGBoost (seuil de décision = 0.40) | 50 000 transactions |

### 3.2 Assignation

- Assignation **aléatoire** par `client_id % 2` (parité)
- Stratification par tranche de montant et par pays pour garantir la représentativité
- Aucun client ne sera dans les deux groupes simultanément

### 3.3 Durée

- **Durée totale : 4 semaines**
- Semaine 1–2 : phase de rodage (monitoring intensif, possibilité d'arrêt d'urgence)
- Semaine 3–4 : phase de mesure principale
- Analyse intermédiaire à J+14 (sequential testing avec correction de Bonferroni)

---

## 4. Métriques de suivi

### 4.1 Métriques primaires (décisionnelles)

| Métrique | Description | Cible groupe B vs A |
|---|---|---|
| **Recall fraude** | % de fraudes détectées | +30 pts minimum |
| **Faux Positifs Rate (FPR)** | % de transactions légitimes bloquées | Pas de dégradation (≤ +0.1 pt) |

### 4.2 Métriques secondaires (surveillance)

| Métrique | Description |
|---|---|
| Montant fraude évité (MAD) | Gain financier direct |
| Taux de contestation client | Nombre de réclamations pour blocage injustifié |
| Temps de traitement (ms) | Latence du modèle vs règles |
| NPS opérationnel | Satisfaction des équipes fraude |

### 4.3 Métriques guardrail (arrêt d'urgence)

Si l'une de ces conditions est atteinte, le test est **arrêté immédiatement** :

- FPR groupe B > 1.5% (dégradation forte de l'expérience client)
- Recall groupe B < 40% (performance inférieure au baseline)
- Plus de 5 incidents clients majeurs liés à des blocages injustifiés

---

## 5. Calcul de la taille d'échantillon

```
Paramètres :
- p₁ (Recall baseline)   = 0.55  (système règles)
- p₂ (Recall modèle)     = 0.85  (XGBoost cible)
- α = 0.05 (bilatéral → z_α/2 = 1.96)
- β = 0.20 (puissance 80% → z_β = 0.84)

Formule :
n = 2 × (z_α/2 + z_β)² × p̄(1-p̄) / (p₁-p₂)²
p̄ = (p₁+p₂)/2 = 0.70

n ≈ 2 × (1.96+0.84)² × 0.70×0.30 / (0.30)²
n ≈ 2 × 7.84 × 0.21 / 0.09
n ≈ 366 fraudes par groupe

Avec un taux de fraude de ~0.17%, il faut :
366 / 0.0017 ≈ 215 000 transactions par groupe

Par sécurité, on vise 50 000 transactions/groupe sur 4 semaines
(volume journalier moyen : ~12 500 txn/groupe/jour)
```

---

## 6. Analyse statistique prévue

1. **Test Z à deux proportions** sur le Recall après 4 semaines
2. **Intervalle de confiance à 95%** sur la différence de Recall
3. **Analyse de sensibilité** : impact du seuil de décision (0.30 / 0.40 / 0.50)
4. **Analyse par sous-groupes** : pays, canal, tranche de montant
5. **Bootstrap** (1 000 itérations) pour robustesse des estimateurs

**Règle de décision :**
- Si p-value < 0.05 ET Δ Recall ≥ 30 pts ET FPR_B ≤ FPR_A + 0.1% → **Déploiement total du modèle XGBoost**
- Sinon → Analyse approfondie, ajustement du seuil, ou retour au baseline

---

## 7. Calendrier

| Semaine | Action |
|---|---|
| S0 | Préparation technique, mise en place du split A/B, brief équipe |
| S1–S2 | Phase de rodage + monitoring quotidien |
| S3–S4 | Phase de mesure principale |
| S4+3 jours | Analyse statistique finale |
| S4+1 semaine | Présentation des résultats + décision de déploiement |

---

*Document rédigé dans le cadre du projet DDDM — Juin 2026*
