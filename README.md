# Détection de Fraude Bancaire — Projet DDDM
## Description
Ce projet applique le pipeline complet de **Data-Driven Decision Making** à la détection de transactions frauduleuses en temps réel pour une banque.
**Problème métier :** Une banque traite des millions de transactions par jour. Parmi elles, une infime partie sont frauduleuses. L'objectif est de construire un modèle capable de détecter ces transactions suspectes avant que le dommage soit fait.
---
## Architecture du projet
```
fraud_detection/
├── data/                        # Données brutes et traitées
│   ├── generate_data.py         # Script de génération du dataset synthétique
│   └── data_dictionary.md       # Dictionnaire des données
├── notebooks/
│   └── fraud_detection_full.ipynb   # Notebook principal (toutes les phases)
├── dashboard/
│   └── app.py                   # Dashboard interactif Streamlit
├── models/                      # Modèles sauvegardés
├── reports/
│   ├── ab_test_plan.md          # Plan A/B Test (2 pages)
│   └── data_story_outline.md   # Structure de la Data Story (15 slides)
├── requirements.txt
└── README.md
```
---
## Installation
```bash
# 1. Cloner le dépôt
git clone https://github.com/Ruined-King/PROJET-DDD.git
cd fraud_detection
# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
# 3. Installer les dépendances
pip install -r requirements.txt
# 4. Télécharger le dataset (voir section Dataset)
# 5. Lancer le notebook
jupyter notebook notebooks/fraud_detection_full.ipynb
# 6. Lancer le dashboard
streamlit run dashboard/app.py
```
---
## Phases du Projet
| Phase | Description |
|-------|-------------|
| 1 | Définition du Problème & KPIs |
| 2 | Collecte & Audit des Données |
| 3 | Exploration & Analyse Statistique (EDA) |
| 4 | Modélisation Prédictive & Interprétabilité |
| 5 | Visualisation & Dashboard |
| 6 | Décision, A/B Testing & Mesure d'Impact |
---
## Dataset
- **Source :** Kaggle — [Credit Card Fraud Detection (ULB)](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- **Volume :** 284 807 transactions réelles
- **Déséquilibre des classes :** 0.172% de fraudes

> ⚠️ Le fichier `creditcard.csv` (144 MB) dépasse la limite GitHub/GitLab.  
> Téléchargez-le manuellement depuis Kaggle et placez-le dans le dossier `data/` avant d'exécuter le projet.

---
## Équipe
| Nom | Prénom |
|-----|--------|
| BENAYAD | Nizar |
| EL KAOUNI | Abdessamad |
| BOURHIM | Issam |

Projet réalisé dans le cadre du module **Data-Driven Decision Making**  
Date limite : **07 Juin 2026**