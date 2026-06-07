"""
Script de génération du dataset synthétique de transactions bancaires.
Produit deux fichiers CSV (2 sources de données) à combiner.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

np.random.seed(42)

N_TRANSACTIONS = 100_000
FRAUD_RATE = 0.0017  # ~0.17% de fraudes, réaliste

print("🔄 Génération des données en cours...")

# ─────────────────────────────────────────────
# SOURCE 1 : Transactions bancaires
# ─────────────────────────────────────────────

n_fraud = int(N_TRANSACTIONS * FRAUD_RATE)
n_legit = N_TRANSACTIONS - n_fraud

# Transactions légitimes
legit = pd.DataFrame({
    "transaction_id": [f"TXN{i:07d}" for i in range(n_legit)],
    "client_id":      np.random.randint(1, 15_000, n_legit),
    "montant":        np.abs(np.random.exponential(scale=80, size=n_legit)).round(2),
    "heure":          np.random.randint(6, 23, n_legit),
    "jour_semaine":   np.random.randint(0, 7, n_legit),
    "categorie":      np.random.choice(
        ["alimentation", "transport", "loisirs", "sante", "tech", "voyage", "divers"],
        n_legit, p=[0.30, 0.20, 0.15, 0.10, 0.10, 0.08, 0.07]
    ),
    "pays":           np.random.choice(
        ["MA", "FR", "ES", "DE", "GB", "US"],
        n_legit, p=[0.55, 0.20, 0.10, 0.05, 0.05, 0.05]
    ),
    "canal":          np.random.choice(["carte_physique", "en_ligne", "mobile"], n_legit, p=[0.50, 0.30, 0.20]),
    "est_fraude":     0,
})

# Transactions frauduleuses (comportement différent)
fraud = pd.DataFrame({
    "transaction_id": [f"TXN{i:07d}" for i in range(n_legit, N_TRANSACTIONS)],
    "client_id":      np.random.randint(1, 15_000, n_fraud),
    "montant":        np.abs(np.random.exponential(scale=400, size=n_fraud)).round(2),  # montants plus élevés
    "heure":          np.random.choice(list(range(0, 6)) + list(range(22, 24)), n_fraud),  # nuit
    "jour_semaine":   np.random.randint(0, 7, n_fraud),
    "categorie":      np.random.choice(
        ["tech", "voyage", "divers", "loisirs", "alimentation", "transport", "sante"],
        n_fraud, p=[0.35, 0.25, 0.15, 0.10, 0.07, 0.05, 0.03]
    ),
    "pays":           np.random.choice(
        ["US", "CN", "NG", "RO", "MA", "FR", "ES"],
        n_fraud, p=[0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]
    ),
    "canal":          np.random.choice(["en_ligne", "carte_physique", "mobile"], n_fraud, p=[0.70, 0.15, 0.15]),
    "est_fraude":     1,
})

transactions = pd.concat([legit, fraud], ignore_index=True)

# Ajouter timestamps aléatoires sur 6 mois
start_date = datetime(2024, 1, 1)
transactions["timestamp"] = [
    start_date + timedelta(seconds=int(s))
    for s in np.random.randint(0, 180 * 24 * 3600, N_TRANSACTIONS)
]
transactions["timestamp"] = pd.to_datetime(transactions["timestamp"])

# Features dérivées réalistes
transactions["delta_transaction"] = np.random.exponential(scale=3600, size=N_TRANSACTIONS).astype(int)  # secondes depuis dernière txn
transactions["nb_transactions_24h"] = np.random.poisson(lam=3, size=N_TRANSACTIONS)
transactions["montant_moyen_30j"] = (transactions["montant"] * np.random.uniform(0.5, 2.0, N_TRANSACTIONS)).round(2)

# Mélanger
transactions = transactions.sample(frac=1, random_state=42).reset_index(drop=True)

# ─────────────────────────────────────────────
# SOURCE 2 : Profils clients
# ─────────────────────────────────────────────

client_ids = transactions["client_id"].unique()
n_clients = len(client_ids)

clients = pd.DataFrame({
    "client_id":          client_ids,
    "age":                np.random.randint(18, 75, n_clients),
    "anciennete_mois":    np.random.randint(1, 240, n_clients),
    "score_credit":       np.random.randint(300, 850, n_clients),
    "type_compte":        np.random.choice(["standard", "premium", "pro"], n_clients, p=[0.60, 0.30, 0.10]),
    "pays_residence":     np.random.choice(["MA", "FR", "ES", "DE", "GB"], n_clients, p=[0.55, 0.20, 0.12, 0.08, 0.05]),
    "limite_credit":      np.random.choice([5000, 10000, 20000, 50000], n_clients, p=[0.40, 0.35, 0.20, 0.05]),
    "alertes_precedentes": np.random.poisson(lam=0.3, size=n_clients),
})

# ─────────────────────────────────────────────
# Sauvegarde
# ─────────────────────────────────────────────
os.makedirs(os.path.dirname(__file__), exist_ok=True)

transactions.to_csv("data/transactions.csv", index=False)
clients.to_csv("data/clients.csv", index=False)

print(f"✅ transactions.csv : {len(transactions):,} lignes")
print(f"✅ clients.csv      : {len(clients):,} lignes")
print(f"   → Fraudes : {transactions['est_fraude'].sum():,} ({transactions['est_fraude'].mean()*100:.2f}%)")
print("Données générées avec succès !")
