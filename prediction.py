import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import streamlit as st

def faire_prediction(performances):
    if len(performances) < 1:
        st.warning("⚠️ Pas assez de données pour faire une prédiction fiable.")
        return

        # ---- PREPARATION DES DONNEES ---
    df = performances.copy()

        # créer la cible : l'Athlete progresse t'il?
    df["progression"] = df["distance_km"].diff().fillna(0) 
    df["progression"] = (df["progression"] > 0).astype(int)

        #créer le risque de blessure
    df["risque_blessure"] = (
        (df["contraction_muscle" ] >= 8) |
        (df["cardio_max_bpm"] >= 190) |
        (df["temps_recuperation"] >= 30) |
        (df["douleur"] == "Oui")
    ).astype(int)

        #---- SELECTION DES FEATURES ET CIBLE(variable d'entrée) ---
    features = [
        "distance_km", "vitesse_max_kmh", "acceleration",
        "cardio_max_bpm", "cardio_repos_bpm",
        "temps_recuperation", "contraction_muscle",
            
    ]
    X = df[features].fillna(0)

        #---- PREDICTION DE LA PROGRESSION ---
    st.markdown("### 🚀 peut-il progresser à la prochaine session ?")
    derniere = X.iloc[-1]
    moyenne = X.mean()

    score_progression = 0
    if derniere["distance_km"] >= moyenne["distance_km"]:
        score_progression += 1
    if derniere["vitesse_max_kmh"] >= moyenne["vitesse_max_kmh"]:
        score_progression += 1
    if derniere["acceleration"] >= moyenne["acceleration"]:
        score_progression += 1

    pourcentage = (score_progression / 3) * 100

    if pourcentage >= 70:
        st.success(f"✅ Probabilité de progression élevée , l'athlète peut encore progresser ({pourcentage:.0f}%)")
    elif pourcentage >= 40:
        st.warning(f"⚠️ Probabilité de progression modérée, attention à ne pas trop forcer ({pourcentage:.0f}%)")
    else:
        st.error(f"❌ Probabilité de progression faible, risque de stagnation ou de blessure ({pourcentage:.0f}%)")

        #---- JAUGE VISUELLE ---
    st.progress(int(pourcentage))

        #---- PREDICTION DU RISQUE DE BLESSURE ---
    st.markdown("⚠️ **Risque de blessure**")

    risque = 0
    if derniere["contraction_muscle"] >= 8:
        risque += 1
    if derniere["cardio_max_bpm"] >= 190:
        risque += 1
    if derniere["temps_recuperation"] >= 30:
        risque += 1
    if df["douleur"].iloc[-1] == "Oui":
        risque += 1
    if risque == 0:
        st.success("✅ Risque de blessure faible")
    elif risque <= 2:
        st.warning("⚠️ Risque de blessure modéré, surveiller les signes de fatigue")
    else:
        st.error("❌ Risque de blessure élevé, envisager une récupération ou un suivi médical")

        #---- RECOMMANDATIONS PERSONNALISEES ---
    st.markdown("💡 **Recommandations**")
    if pourcentage >= 70 and risque <= 1:
        st.info("L'athlète est en bonne forme, continuer sur cette lancée !")
    elif pourcentage >= 40 and risque <= 2: 
        st.info("L'athlète progresse mais attention à ne pas trop forcer, privilégier la récupération active.")
    elif pourcentage < 40 and risque > 2:
        st.info("L'athlète montre des signes de fatigue, envisager une pause ou un suivi médical.")


    