# 📖 Dictionnaire des Données — Détection de Fraude Bancaire

## Source 1 : `transactions.csv`

| Nom du champ | Type | Description | Valeurs possibles | Source |
|---|---|---|---|---|
| `transaction_id` | string | Identifiant unique de la transaction | TXN0000001 … | Système bancaire |
| `client_id` | integer | Identifiant du client | 1 – 15000 | CRM |
| `montant` | float | Montant de la transaction en MAD | 0.01 – ∞ | Système bancaire |
| `heure` | integer | Heure locale de la transaction | 0 – 23 | Système bancaire |
| `jour_semaine` | integer | Jour de la semaine | 0 (lundi) – 6 (dimanche) | Système bancaire |
| `categorie` | string | Catégorie du marchand | alimentation, transport, loisirs, sante, tech, voyage, divers | MCC (Merchant Category Code) |
| `pays` | string | Pays d'émission de la transaction | MA, FR, ES, DE, GB, US, CN, NG, RO | Réseau de paiement |
| `canal` | string | Canal utilisé pour la transaction | carte_physique, en_ligne, mobile | Système bancaire |
| `timestamp` | datetime | Date et heure complète de la transaction | 2024-01-01 … 2024-06-30 | Système bancaire |
| `delta_transaction` | integer | Temps (en secondes) depuis la dernière transaction du client | 0 – ∞ | Calculé |
| `nb_transactions_24h` | integer | Nombre de transactions du client dans les dernières 24h | 0 – ∞ | Calculé |
| `montant_moyen_30j` | float | Montant moyen des transactions du client sur 30 jours | 0.01 – ∞ | Calculé |
| `est_fraude` | integer | Label cible : 1 si fraude, 0 sinon | 0, 1 | Équipe fraude (labels manuels) |

---

## Source 2 : `clients.csv`

| Nom du champ | Type | Description | Valeurs possibles | Source |
|---|---|---|---|---|
| `client_id` | integer | Identifiant unique du client (clé de jointure) | 1 – 15000 | CRM |
| `age` | integer | Âge du client en années | 18 – 74 | KYC |
| `anciennete_mois` | integer | Ancienneté du client en mois | 1 – 240 | CRM |
| `score_credit` | integer | Score de crédit interne | 300 – 850 | Scoring interne |
| `type_compte` | string | Type de compte bancaire | standard, premium, pro | CRM |
| `pays_residence` | string | Pays de résidence déclaré | MA, FR, ES, DE, GB | KYC |
| `limite_credit` | integer | Limite de crédit accordée en MAD | 5000, 10000, 20000, 50000 | Crédit |
| `alertes_precedentes` | integer | Nombre d'alertes fraude historiques sur le compte | 0 – ∞ | Équipe fraude |

---

## Notes sur la qualité des données

- **Complétude :** Les deux tables ne contiennent pas de valeurs manquantes par construction. Dans un contexte réel, des valeurs nulles seraient attendues sur `pays`, `categorie` et `score_credit`.
- **Fraîcheur :** Les transactions couvrent la période janvier–juin 2024.
- **Granularité :** Une ligne = une transaction.
- **Biais potentiel :** Le label `est_fraude` est basé sur des signalements manuels — risque de sous-déclaration des fraudes non détectées.
- **Déséquilibre des classes :** ~0.17% de fraudes. Des techniques SMOTE ou class_weight seront nécessaires.
