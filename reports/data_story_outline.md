# Data Story — Détection de Fraude Bancaire
## Structure de la présentation (15 slides max)
### Projet DDDM — Juin 2026

---

### SLIDE 1 — Titre
**"Comment l'IA peut sauver des millions : détecter la fraude bancaire avant qu'il soit trop tard"**
- Sous-titre : Projet Data-Driven Decision Making
- Visuel : Illustration d'un bouclier sur fond de transactions

---

### SLIDE 2 — Le problème (accroche)
**"1 700 fraudes par jour. 765 000 MAD perdus. Chaque jour."**
- Chiffres clés du contexte
- Visualisation : timeline d'une transaction frauduleuse
- Citation client fictive : "J'ai découvert la fraude 3 jours après"

---

### SLIDE 3 — Pourquoi c'est difficile
**Le défi du déséquilibre : 1 fraude pour 588 transactions légitimes**
- Visualisation du déséquilibre des classes
- Le dilemme : détecter sans bloquer les bons clients
- Coût d'un faux positif vs coût d'une fraude non détectée

---

### SLIDE 4 — Notre approche
**Pipeline Data-Driven en 6 phases**
- Schéma visuel du pipeline complet
- De la donnée brute à la décision opérationnelle
- Timeline du projet

---

### SLIDE 5 — Les données
**100 000 transactions + profils clients = une vision complète**
- Cartographie des sources (transactions + CRM)
- Résultats de l'audit qualité
- Exemples de features clés

---

### SLIDE 6 — Ce que les données révèlent (EDA)
**3 signaux forts de fraude**
- 🌙 Les fraudes frappent la nuit (0h–5h) : taux ×8
- 🌍 Certains pays concentrent le risque (CN, NG, RO)
- 💰 Les montants frauduleux sont 3× plus élevés
- Visualisations : boxplots, cartes, heatmaps

---

### SLIDE 7 — La modélisation
**Trois modèles en compétition**
- Tableau comparatif (Logistique, Random Forest, XGBoost)
- Graphique : courbes ROC des 3 modèles
- Conclusion : XGBoost domine sur tous les indicateurs

---

### SLIDE 8 — Le modèle gagnant : XGBoost
**AUC-ROC : 0.963 | Recall : 85.4% | F1 : 0.805**
- Matrice de confusion annotée
- Ce que ça signifie en langage métier :
  "Sur 100 fraudes réelles, nous en détectons 85"

---

### SLIDE 9 — Pourquoi le modèle décide ainsi (SHAP)
**"Ouvrir la boîte noire"**
- Graphique SHAP global : top 10 features
- Exemple concret : explication d'une transaction frauduleuse
- Insight : le montant, l'heure et le pays sont les 3 signaux les plus puissants

---

### SLIDE 10 — Le dashboard opérationnel
**5 vues, 3 profils, une seule vérité**
- Screenshots du dashboard Streamlit
- Vue Direction : KPIs & ROI
- Vue Opérations : alertes temps réel
- Vue Prédiction : scoring manuel

---

### SLIDE 11 — Nos 3 recommandations
**Actionnables. Quantifiées. Prioritisées.**
1. Déployer XGBoost en production → -40% de pertes
2. Challenge 3D Secure nocturne hors-pays → coût zéro
3. Alertes SMS pour clients à historique fraude → prévention

---

### SLIDE 12 — Le plan A/B Test
**Valider avant de déployer massivement**
- Schéma du design expérimental (A vs B)
- Métriques primaires et guardrails
- Calendrier 4 semaines
- Règle de décision statistique

---

### SLIDE 13 — L'impact financier
**+229 000 MAD évités. Chaque jour.**
- Graphique comparatif Baseline vs Modèle
- Projection ROI sur 12 mois : ×8 à ×12
- Break-even : semaine 3 après déploiement

---

### SLIDE 14 — Prochaines étapes
**La route vers la production**
- S+1 : Lancement A/B Test
- S+5 : Analyse résultats A/B
- S+6 : Déploiement API REST (FastAPI)
- S+8 : Monitoring Data Drift (Evidently AI)
- S+12 : Révision du modèle (réentraînement)

---

### SLIDE 15 — Conclusion
**"De la donnée à la décision : 229 000 MAD économisés par jour"**
- Récapitulatif des KPIs atteints
- Message clé : la donnée + l'IA = avantage concurrentiel durable
- Questions & discussion

---

*Présentation de 10 minutes pour jury non-technique*
*Projet DDDM — Juin 2026*
