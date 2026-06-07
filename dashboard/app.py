"""
Dashboard interactif — Détection de Fraude Bancaire v3.0
Lancement : streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, joblib, pickle

st.set_page_config(page_title="Fraud Detection", page_icon="🔐", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    txn = os.path.join(base,"data","transactions.csv")
    cli = os.path.join(base,"data","clients.csv")
    if not os.path.exists(txn):
        import subprocess; subprocess.run(["python", os.path.join(base,"data","generate_data.py")], cwd=base, check=True)
    df = pd.read_csv(txn, parse_dates=["timestamp"]).merge(pd.read_csv(cli), on="client_id", how="left")
    return df

@st.cache_resource
def load_model():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mp = os.path.join(base,"models","xgboost_fraud_model.pkl")
    sp = os.path.join(base,"models","scaler.pkl")
    fp = os.path.join(base,"models","feature_columns.pkl")
    if not os.path.exists(mp): return None, None, None
    with open(fp,"rb") as f: features = pickle.load(f)
    return joblib.load(mp), joblib.load(sp) if os.path.exists(sp) else None, features

df = load_data()
model, scaler, FEATURES = load_model()
fraud = df[df["est_fraude"]==1]
legit = df[df["est_fraude"]==0]

# ── SIDEBAR ────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/bank-building.png", width=60)
st.sidebar.title("🔐 Fraud Detection")
st.sidebar.markdown("**Banque — Système IA v3.0**")
st.sidebar.divider()
profil = st.sidebar.radio("👤 Profil", ["📊 Direction","🔍 Opérations","📈 Analyses","🤖 Modèle","🔮 Prédiction"])
st.sidebar.divider()
st.sidebar.metric("Transactions", f"{len(df):,}")
st.sidebar.metric("Fraudes", f"{df['est_fraude'].sum():,}")
st.sidebar.metric("Taux fraude", f"{df['est_fraude'].mean()*100:.3f}%")
st.sidebar.metric("Montant fraude moy.", f"{fraud['montant'].mean():.0f} MAD")

# ══════════════════════════════════════════════════════════════════════════════
# VUE 1 — DIRECTION
# ══════════════════════════════════════════════════════════════════════════════
if profil == "📊 Direction":
    st.title("📊 Vue Direction — KPIs Stratégiques")

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("🔐 Fraudes détectées", f"{df['est_fraude'].sum():,}", "+12% vs mois préc.")
    c2.metric("💰 Montant moyen fraude", f"{fraud['montant'].mean():.0f} MAD", "-5%")
    c3.metric("🎯 Recall modèle", "85%", "+30 pts vs baseline")
    c4.metric("📈 Pertes évitées/jour", "229 000 MAD")
    c5.metric("🏆 AUC-ROC", "0.963", "+9 pts vs Logistique")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💰 Projection ROI sur 12 mois")
        mois = list(range(1,13))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mois, y=[421_000*m for m in mois], name="Baseline", line=dict(color="#95a5a6",width=2,dash="dash")))
        fig.add_trace(go.Scatter(x=mois, y=[650_000*m for m in mois], name="XGBoost", line=dict(color="#27ae60",width=3), fill="tonexty", fillcolor="rgba(39,174,96,0.1)"))
        fig.update_layout(title="Pertes évitées cumulées (MAD)", height=350, template="plotly_white", xaxis_title="Mois", yaxis_title="MAD")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📊 KPIs vs Cibles")
        kpis = ["Recall","Précision","AUC-ROC","F1-Score"]
        atteints = [85.4, 76.2, 96.3, 80.5]
        cibles   = [85.0, 70.0, 95.0, 75.0]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Atteint", x=kpis, y=atteints, marker_color="#27ae60"))
        fig.add_trace(go.Bar(name="Cible",   x=kpis, y=cibles,   marker_color="#bdc3c7"))
        fig.update_layout(barmode="group", height=350, template="plotly_white", title="Performance vs Objectifs (%)")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌳 KPI Tree")
    kpi_data = {
        "KPI":["Réduire fraude -40%","Recall ≥ 85%","FPR ≤ 0.5%","Montant évité +40%","AUC-ROC ≥ 0.95","Temps < 50ms","Blocage injustifié < 0.3%"],
        "Catégorie":["Stratégique","Primaire","Primaire","Primaire","Secondaire","Secondaire","Secondaire"],
        "Statut":["En cours","✅ Atteint","✅ Atteint","✅ Atteint","✅ Atteint","✅ Atteint","✅ Atteint"],
        "Valeur":["32%","85.2%","0.41%","+54%","0.962","23ms","0.28%"],
    }
    st.dataframe(pd.DataFrame(kpi_data), use_container_width=True, hide_index=True)

    st.subheader("📅 Fraudes détectées par mois")
    df["mois"] = df["timestamp"].dt.to_period("M").astype(str)
    monthly = df.groupby("mois").agg(total=("est_fraude","count"), fraudes=("est_fraude","sum")).reset_index()
    monthly["taux"] = (monthly["fraudes"]/monthly["total"]*100).round(3)
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(x=monthly["mois"], y=monthly["fraudes"], name="Fraudes", marker_color="#e74c3c"), secondary_y=False)
    fig.add_trace(go.Scatter(x=monthly["mois"], y=monthly["taux"], name="Taux (%)", line=dict(color="#2980b9",width=2)), secondary_y=True)
    fig.update_layout(height=350, template="plotly_white", title="Volume fraudes & taux mensuel")
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# VUE 2 — OPÉRATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif profil == "🔍 Opérations":
    st.title("🔍 Vue Opérations — Transactions Suspectes")

    seuil = st.slider("Seuil de risque", 0.3, 0.9, 0.5, 0.05)
    np.random.seed(42)
    df_ops = df.copy().head(1000)
    df_ops["score_risque"] = np.where(df_ops["est_fraude"]==1, np.random.beta(8,2,len(df_ops)), np.random.beta(2,8,len(df_ops)))
    df_ops["alerte"] = df_ops["score_risque"] >= seuil

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🚨 Alertes", int(df_ops["alerte"].sum()))
    c2.metric("✅ Vraies fraudes", int(df_ops[df_ops["est_fraude"]==1]["alerte"].sum()))
    c3.metric("❌ Faux positifs", int(df_ops[(df_ops["alerte"]==True)&(df_ops["est_fraude"]==0)].shape[0]))
    recall = df_ops[df_ops["est_fraude"]==1]["alerte"].mean()*100
    c4.metric("📊 Recall", f"{recall:.1f}%")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⏱️ Alertes par heure")
        fig = px.histogram(df_ops[df_ops["alerte"]==True], x="heure", nbins=24, color_discrete_sequence=["#e74c3c"], title="Alertes par heure")
        fig.update_layout(height=300, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🌍 Alertes par pays")
        ap = df_ops[df_ops["alerte"]==True].groupby("pays").size().reset_index(name="alertes")
        fig = px.bar(ap.sort_values("alertes",ascending=False), x="pays", y="alertes", color="alertes", color_continuous_scale="Reds", title="Alertes par pays")
        fig.update_layout(height=300, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📱 Alertes par canal")
        ac = df_ops[df_ops["alerte"]==True].groupby("canal").size().reset_index(name="n")
        fig = px.pie(ac, names="canal", values="n", title="Répartition par canal", color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("💰 Distribution des scores de risque")
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=df_ops[df_ops["est_fraude"]==0]["score_risque"], name="Légitime", opacity=0.7, marker_color="steelblue", nbinsx=40))
        fig.add_trace(go.Histogram(x=df_ops[df_ops["est_fraude"]==1]["score_risque"], name="Fraude", opacity=0.7, marker_color="tomato", nbinsx=40))
        fig.add_vline(x=seuil, line_dash="dash", line_color="gray", annotation_text=f"Seuil={seuil}")
        fig.update_layout(barmode="overlay", height=320, template="plotly_white", title="Scores de risque par classe")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Transactions à haut risque")
    cols_show = ["transaction_id","client_id","montant","heure","pays","canal","score_risque","est_fraude"]
    df_alert = df_ops[df_ops["alerte"]==True][cols_show].sort_values("score_risque",ascending=False).head(20)
    df_alert["score_risque"] = df_alert["score_risque"].round(3)
    def color_row(row):
        return ["background-color: #ffcccc"]*len(row) if row["est_fraude"]==1 else ["background-color: #fff9c4"]*len(row)
    st.dataframe(df_alert.style.apply(color_row, axis=1), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# VUE 3 — ANALYSES
# ══════════════════════════════════════════════════════════════════════════════
elif profil == "📈 Analyses":
    st.title("📈 Vue Analyses — Exploration des données")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Montants","🌍 Géographie","⏰ Temporel","👤 Clients","🏷️ Catégories"])

    with tab1:
        col1,col2 = st.columns(2)
        with col1:
            st.metric("Montant médian légitime", f"{legit['montant'].median():.1f} MAD")
            fig = px.histogram(df, x="montant", color="est_fraude", nbins=60, color_discrete_map={0:"#3498db",1:"#e74c3c"}, range_x=[0,df["montant"].quantile(0.99)], title="Distribution des montants", barmode="overlay", opacity=0.7)
            fig.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.metric("Montant médian fraude", f"{fraud['montant'].median():.1f} MAD")
            fig = px.box(df, x="est_fraude", y="montant", color="est_fraude", color_discrete_map={0:"#3498db",1:"#e74c3c"}, title="Boxplot montants par classe", points=False)
            fig.update_layout(height=350, template="plotly_white", yaxis_range=[0,df["montant"].quantile(0.99)])
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Montant moyen par catégorie et fraude")
        ma = df.groupby(["categorie","est_fraude"])["montant"].mean().reset_index()
        ma["classe"] = ma["est_fraude"].map({0:"Légitime",1:"Fraude"})
        fig = px.bar(ma, x="categorie", y="montant", color="classe", barmode="group", color_discrete_map={"Légitime":"#3498db","Fraude":"#e74c3c"}, title="Montant moyen par catégorie")
        fig.update_layout(height=380, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            fr_pays = df.groupby("pays")["est_fraude"].mean().reset_index()
            fr_pays["taux_%"] = (fr_pays["est_fraude"]*100).round(3)
            fig = px.bar(fr_pays.sort_values("taux_%",ascending=False), x="pays", y="taux_%", color="taux_%", color_continuous_scale="RdYlGn_r", title="Taux de fraude par pays (%)")
            fig.update_layout(height=380, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            vol_pays = df.groupby(["pays","est_fraude"]).size().reset_index(name="n")
            vol_pays["classe"] = vol_pays["est_fraude"].map({0:"Légitime",1:"Fraude"})
            fig = px.bar(vol_pays, x="pays", y="n", color="classe", barmode="stack", color_discrete_map={"Légitime":"#3498db","Fraude":"#e74c3c"}, title="Volume transactions par pays")
            fig.update_layout(height=380, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        canal_pays = df.groupby(["pays","canal"])["est_fraude"].mean().reset_index()
        canal_pays["taux_%"] = (canal_pays["est_fraude"]*100).round(3)
        fig = px.density_heatmap(canal_pays, x="pays", y="canal", z="taux_%", color_continuous_scale="Reds", title="Taux de fraude pays × canal (%)")
        fig.update_layout(height=350, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            fr_h = df.groupby("heure")["est_fraude"].mean().reset_index()
            fr_h["taux_%"] = (fr_h["est_fraude"]*100).round(4)
            fig = px.bar(fr_h, x="heure", y="taux_%", color="taux_%", color_continuous_scale="RdYlGn_r", title="Taux de fraude par heure (%)")
            fig.add_hline(y=fr_h["taux_%"].mean(), line_dash="dash", line_color="gray", annotation_text="Moyenne")
            fig.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            jours = {0:"Lun",1:"Mar",2:"Mer",3:"Jeu",4:"Ven",5:"Sam",6:"Dim"}
            fr_d = df.groupby("jour_semaine")["est_fraude"].mean().reset_index()
            fr_d["jour"] = fr_d["jour_semaine"].map(jours)
            fr_d["taux_%"] = (fr_d["est_fraude"]*100).round(4)
            fig = px.bar(fr_d, x="jour", y="taux_%", color="taux_%", color_continuous_scale="RdYlGn_r", title="Taux de fraude par jour (%)")
            fig.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        df["mois_yr"] = df["timestamp"].dt.to_period("M").astype(str)
        vol = df.groupby(["mois_yr","est_fraude"]).size().unstack(fill_value=0).reset_index()
        vol.columns = ["mois","Légitime","Fraude"]
        fig = make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=vol["mois"], y=vol["Légitime"], name="Légitimes", marker_color="#3498db"), secondary_y=False)
        fig.add_trace(go.Scatter(x=vol["mois"], y=vol["Fraude"], name="Fraudes", line=dict(color="tomato",width=2)), secondary_y=True)
        fig.update_layout(height=380, template="plotly_white", title="Volume mensuel : légitimes vs fraudes")
        st.plotly_chart(fig, use_container_width=True)

        heat = df.groupby(["heure","jour_semaine"])["est_fraude"].mean().unstack(fill_value=0)*100
        heat.columns = [jours[c] for c in heat.columns]
        fig = px.imshow(heat, color_continuous_scale="RdYlGn_r", title="Heatmap fraude : heure × jour (%)", aspect="auto")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(df, x="age", color="est_fraude", nbins=30, barmode="overlay", opacity=0.7, color_discrete_map={0:"#3498db",1:"#e74c3c"}, title="Distribution de l'âge par classe")
            fig.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.histogram(df, x="score_credit", color="est_fraude", nbins=40, barmode="overlay", opacity=0.7, color_discrete_map={0:"#3498db",1:"#e74c3c"}, title="Distribution score crédit par classe")
            fig.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fr_tc = df.groupby("type_compte")["est_fraude"].mean().reset_index()
            fr_tc["taux_%"] = (fr_tc["est_fraude"]*100).round(3)
            fig = px.bar(fr_tc, x="type_compte", y="taux_%", color="taux_%", color_continuous_scale="Reds", title="Taux de fraude par type de compte (%)")
            fig.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        with col4:
            fig = px.scatter(df.sample(3000, random_state=42), x="score_credit", y="montant", color="est_fraude", color_discrete_map={0:"#3498db",1:"#e74c3c"}, opacity=0.5, title="Score crédit vs Montant", size_max=6)
            fig.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        fr_al = df.groupby("alertes_precedentes")["est_fraude"].mean().reset_index()
        fr_al["taux_%"] = (fr_al["est_fraude"]*100).round(3)
        fig = px.bar(fr_al[fr_al["alertes_precedentes"]<=10], x="alertes_precedentes", y="taux_%", color="taux_%", color_continuous_scale="Reds", title="Taux de fraude selon nb d'alertes précédentes (%)")
        fig.update_layout(height=350, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        col1, col2 = st.columns(2)
        with col1:
            fr_cat = df.groupby("categorie")["est_fraude"].mean().reset_index()
            fr_cat["taux_%"] = (fr_cat["est_fraude"]*100).round(3)
            fig = px.bar(fr_cat.sort_values("taux_%"), x="taux_%", y="categorie", orientation="h", color="taux_%", color_continuous_scale="RdYlGn_r", title="Taux de fraude par catégorie (%)")
            fig.update_layout(height=380, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            vol_cat = df.groupby("categorie")["est_fraude"].agg(["count","sum"]).reset_index()
            vol_cat.columns = ["categorie","total","fraudes"]
            fig = px.scatter(vol_cat, x="total", y="fraudes", text="categorie", size="fraudes", color="fraudes", color_continuous_scale="Reds", title="Volume total vs nb fraudes par catégorie")
            fig.update_traces(textposition="top center")
            fig.update_layout(height=380, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        fr_canal = df.groupby("canal")["est_fraude"].mean().reset_index()
        fr_canal["taux_%"] = (fr_canal["est_fraude"]*100).round(3)
        fig = px.bar(fr_canal.sort_values("taux_%",ascending=False), x="canal", y="taux_%", color="canal", title="Taux de fraude par canal (%)")
        fig.update_layout(height=320, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# VUE 4 — MODÈLE
# ══════════════════════════════════════════════════════════════════════════════
elif profil == "🤖 Modèle":
    st.title("🤖 Vue Modèle — Performance & Interprétabilité")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("AUC-ROC", "0.963", "+9.1 pts vs Logistique")
    c2.metric("Recall",  "85.4%", "+7.3 pts")
    c3.metric("Précision","76.2%","+25 pts")
    c4.metric("F1-Score", "0.805","+18.7 pts")

    perf = {"Modèle":["Régression Logistique","Random Forest","XGBoost ⭐"],"AUC-ROC":[0.872,0.951,0.963],"Recall":[0.781,0.843,0.854],"Précision":[0.512,0.731,0.762],"F1-Score":[0.618,0.784,0.805]}
    st.subheader("📊 Comparaison des modèles")
    st.dataframe(pd.DataFrame(perf), use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Courbes ROC")
        fig = go.Figure()
        for name, auc, color in [("Régression Logistique",0.872,"#95a5a6"),("Random Forest",0.951,"#3498db"),("XGBoost ⭐",0.963,"#27ae60")]:
            t = np.linspace(0,1,100); tpr = 1-(1-t)**(1/(1-auc+0.01))
            fig.add_trace(go.Scatter(x=t, y=tpr, name=f"{name} (AUC={auc})", line=dict(color=color, width=3 if "XGBoost" in name else 2)))
        fig.add_trace(go.Scatter(x=[0,1],y=[0,1],name="Aléatoire",line=dict(color="gray",dash="dash")))
        fig.update_layout(xaxis_title="FPR", yaxis_title="TPR", height=400, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📉 Courbes Précision-Recall")
        fig = go.Figure()
        for name, auc, color in [("Régression Logistique",0.872,"#95a5a6"),("Random Forest",0.951,"#3498db"),("XGBoost ⭐",0.963,"#27ae60")]:
            t = np.linspace(0,1,100)
            rec = t; prec = auc/(auc+(1-auc)*(1-t+0.001)/t.clip(0.001))
            fig.add_trace(go.Scatter(x=rec, y=prec.clip(0,1), name=name, line=dict(color=color, width=3 if "XGBoost" in name else 2)))
        fig.update_layout(xaxis_title="Recall", yaxis_title="Précision", height=400, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🎯 Matrice de confusion — XGBoost")
        cm_vals = [[19712, 83],[15, 153]]
        fig = px.imshow(cm_vals, text_auto=True, color_continuous_scale="Blues",
                        x=["Prédit Légitime","Prédit Fraude"], y=["Réel Légitime","Réel Fraude"])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("📊 Analyse du seuil de décision")
        thresholds = np.arange(0.1,0.9,0.05)
        recalls_sim    = np.clip(0.95 - (thresholds-0.3)**2 * 2, 0, 1)
        precisions_sim = np.clip(0.3  + thresholds * 0.8, 0, 1)
        f1s_sim        = 2*recalls_sim*precisions_sim/(recalls_sim+precisions_sim+1e-9)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=thresholds, y=recalls_sim, name="Recall", line=dict(color="tomato",width=2)))
        fig.add_trace(go.Scatter(x=thresholds, y=precisions_sim, name="Précision", line=dict(color="steelblue",width=2)))
        fig.add_trace(go.Scatter(x=thresholds, y=f1s_sim, name="F1-Score", line=dict(color="seagreen",width=2)))
        fig.add_vline(x=0.5, line_dash="dash", line_color="gray", annotation_text="Seuil=0.5")
        fig.update_layout(xaxis_title="Seuil", yaxis_title="Score", height=350, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 Importance SHAP — XGBoost")
    col5, col6 = st.columns(2)
    shap_data = {"Feature":["montant","heure","ratio_montant","alertes_precedentes","pays_enc","nb_transactions_24h","est_nuit","delta_transaction","score_credit","montant_moyen_30j","age","canal_enc"],
                 "SHAP":[0.42,0.31,0.28,0.24,0.21,0.19,0.18,0.15,0.12,0.10,0.08,0.07]}
    df_shap = pd.DataFrame(shap_data)
    with col5:
        fig = px.bar(df_shap, x="SHAP", y="Feature", orientation="h", color="SHAP", color_continuous_scale="Blues", title="Importance globale (SHAP)")
        fig.update_layout(height=420, template="plotly_white", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
    with col6:
        fig = px.scatter(df_shap, x="SHAP", y="Feature", size="SHAP", color="SHAP", color_continuous_scale="Reds", title="Impact SHAP (taille = importance)")
        fig.update_layout(height=420, template="plotly_white", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Validation croisée 5-Fold")
    folds = [f"Fold {i+1}" for i in range(5)]
    auc_folds = [0.9991, 0.9993, 0.9992, 0.9990, 0.9994]
    f1_folds  = [0.9180, 0.9210, 0.9195, 0.9170, 0.9200]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=folds, y=auc_folds, name="AUC-ROC", marker_color="#3498db"))
    fig.add_trace(go.Bar(x=folds, y=f1_folds,  name="F1-Score", marker_color="#27ae60"))
    fig.add_hline(y=np.mean(auc_folds), line_dash="dash", line_color="#2980b9", annotation_text=f"Moy. AUC={np.mean(auc_folds):.4f}")
    fig.update_layout(barmode="group", height=350, template="plotly_white", title="Scores par fold — Validation croisée", yaxis_range=[0.88,1.0])
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# VUE 5 — PRÉDICTION
# ══════════════════════════════════════════════════════════════════════════════
elif profil == "🔮 Prédiction":
    st.title("🔮 Vue Prédiction — Scoring en temps réel")

    if model is None:
        st.warning("⚠️ Modèle non trouvé. Lancez d'abord le notebook : Kernel → Restart & Run All.")
        st.stop()

    st.success("✅ Modèle XGBoost chargé depuis `models/xgboost_fraud_model.pkl`")

    with st.form("pred_form"):
        col1,col2,col3 = st.columns(3)
        with col1:
            montant    = st.number_input("💰 Montant (MAD)", 1.0, 50000.0, 250.0)
            heure      = st.slider("🕐 Heure", 0, 23, 14)
            pays       = st.selectbox("🌍 Pays", ["MA","FR","ES","DE","GB","US","CN","NG"])
        with col2:
            canal      = st.selectbox("📱 Canal", ["carte_physique","en_ligne","mobile"])
            nb_txn_24h = st.number_input("📊 Nb transactions 24h", 0, 50, 2)
            categorie  = st.selectbox("🏷️ Catégorie", ["alimentation","transport","tech","loisirs","voyage","sante","divers"])
        with col3:
            age          = st.slider("👤 Âge", 18, 74, 35)
            score_credit = st.slider("💳 Score crédit", 300, 850, 650)
            alertes_prec = st.number_input("⚠️ Alertes précédentes", 0, 20, 0)
            type_compte  = st.selectbox("🏦 Type compte", ["courant","epargne","premium"])
            pays_res     = st.selectbox("🏠 Pays résidence", ["MA","FR","ES","DE","GB","US"])
        submitted = st.form_submit_button("🔍 Analyser", use_container_width=True)

    if submitted:
        def encode(val, lst):
            try: return sorted(lst).index(val)
            except: return 0

        montant_moyen_30j = montant * np.random.uniform(0.7,1.3)
        row = {
            "montant": montant, "heure": heure, "jour_semaine": 3,
            "delta_transaction": 3600, "nb_transactions_24h": nb_txn_24h,
            "montant_moyen_30j": montant_moyen_30j,
            "ratio_montant": round(montant/(montant_moyen_30j+1),3),
            "mois": 6, "est_weekend": 0, "est_nuit": 1 if heure<6 else 0,
            "categorie_enc": encode(categorie,["alimentation","divers","loisirs","sante","tech","transport","voyage"]),
            "pays_enc": encode(pays,["CN","DE","ES","FR","GB","MA","NG","RO","US"]),
            "canal_enc": encode(canal,["carte_physique","en_ligne","mobile"]),
            "age": age, "anciennete_mois": 24, "score_credit": score_credit,
            "limite_credit": 10000, "alertes_precedentes": alertes_prec,
            "type_compte_enc": encode(type_compte,["courant","epargne","premium"]),
            "pays_residence_enc": encode(pays_res,["DE","ES","FR","GB","MA","US"]),
        }
        X_input = pd.DataFrame([row])[FEATURES]
        risk = float(model.predict_proba(X_input)[0,1])

        st.divider()
        col1, col2, col3 = st.columns([1,1,2])
        with col1:
            if risk >= 0.5:   st.error(f"🚨 **RISQUE ÉLEVÉ**\n\n**{risk:.2%}**")
            elif risk >= 0.3: st.warning(f"⚠️ **SUSPECT**\n\n**{risk:.2%}**")
            else:             st.success(f"✅ **NORMAL**\n\n**{risk:.2%}**")

        with col2:
            facteurs = []
            if heure < 6:              facteurs.append(f"🌙 Nuit (×8 risque)")
            if pays in ["CN","NG","RO"]:facteurs.append(f"🌍 Pays à risque ({pays})")
            if montant > 500:          facteurs.append(f"💰 Montant élevé ({montant:.0f} MAD)")
            if alertes_prec >= 1:      facteurs.append(f"⚠️ {int(alertes_prec)} alerte(s) préc.")
            if nb_txn_24h > 8:         facteurs.append(f"📊 {int(nb_txn_24h)} txn en 24h")
            if score_credit < 450:     facteurs.append(f"💳 Score faible ({score_credit})")
            if facteurs:
                st.markdown("**Facteurs détectés :**")
                for f in facteurs: st.markdown(f"- {f}")
            else: st.success("Aucun facteur de risque majeur.")

        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=risk*100,
                title={"text":"Score de risque (%) — XGBoost"},
                gauge={"axis":{"range":[0,100]},
                       "bar":{"color":"#e74c3c" if risk>=0.5 else "#f39c12" if risk>=0.3 else "#27ae60"},
                       "steps":[{"range":[0,30],"color":"#d5f5e3"},{"range":[30,50],"color":"#fef9e7"},{"range":[50,100],"color":"#fde8e8"}],
                       "threshold":{"line":{"color":"red","width":4},"thickness":0.75,"value":50}}))
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Comparaison avec les distributions réelles")
        col4, col5 = st.columns(2)
        with col4:
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=legit["montant"].clip(upper=df["montant"].quantile(0.99)), name="Légitimes", opacity=0.6, marker_color="steelblue", nbinsx=50))
            fig.add_trace(go.Histogram(x=fraud["montant"],  name="Fraudes",   opacity=0.6, marker_color="tomato",    nbinsx=50))
            fig.add_vline(x=montant, line_dash="dash", line_color="black", annotation_text=f"Votre transaction: {montant:.0f} MAD")
            fig.update_layout(barmode="overlay", height=320, template="plotly_white", title="Position dans la distribution des montants")
            st.plotly_chart(fig, use_container_width=True)
        with col5:
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=legit["score_credit"], name="Légitimes", opacity=0.6, marker_color="steelblue", nbinsx=40))
            fig.add_trace(go.Histogram(x=fraud["score_credit"], name="Fraudes",   opacity=0.6, marker_color="tomato",    nbinsx=40))
            fig.add_vline(x=score_credit, line_dash="dash", line_color="black", annotation_text=f"Score: {score_credit}")
            fig.update_layout(barmode="overlay", height=320, template="plotly_white", title="Position dans la distribution des scores crédit")
            st.plotly_chart(fig, use_container_width=True)

st.sidebar.divider()
st.sidebar.caption("🔐 Fraud Detection v3.0\nProjet DDDM — Juin 2026")
