import plotly.express as px
import pandas as pd 
import streamlit as st

def afficher_analyse(performances, nom_athlete):
    st.header(f"📊 Analyse de {nom_athlete}")

    if performances.empty:
        st.warning("Aucune performance enregistrée pour cet athlète.")
        return
    #---- STATISTIQUES DESCRIPTIVES ----
    st.markdown("### 📈 Statistiques générales")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Distance moy. (km)",
            round(performances["distance_km"].mean(), 2))
        st.metric("Vitesse max . (km/h)",
            performances["vitesse_max_kmh"].max())

    with col2:
        st.metric("cardio max moy. (bpm)",
            round(performances["cardio_max_bpm"].mean(), 1))
        st.metric("Recupération moy. (min)",
            round(performances["temps_recuperation"].mean(), 1))

    with col3:
        st.metric("Accélération moy. (m/s^2)",
            round(performances["acceleration"].mean(), 2))
        st.metric("Contraction moy. (1-10)",
            round(performances["contraction_muscle"].mean(), 1))

    #---- GRAPHIQUES DISTANCES ----
    st.markdown("### 🏃 Evolution de la distance parcourue")
    fig1 = px.line(
        performances,
        x="date",
        y="distance_km",
        title="Distance parcourue par session",
        markers=True
    )
    st.plotly_chart(fig1)

    #---- GRAPHIQUES CARDIO ----
    st.markdown("### ❤️ Evolution du cardio")
    fig2 = px.line(
        performances,
        x="date",
        y=["cardio_max_bpm", "cardio_repos_bpm"],
        title="Fréquence cardiaque max et repos par session",
        markers=True
    )
    st.plotly_chart(fig2)

    #---- GRAPHIQUES CONTRACTION MUSCULAIRE ----
    st.markdown("### 💪 Evolution de la contraction musculaire")
    fig3 = px.bar(
        performances,
        x="date",
        y="contraction_muscle",
        title="Niveau de contraction musculaire",
        color="contraction_muscle",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig3)

    #--- GRAPHIQUES DOULEUR ----
    st.markdown("### 😖 Douleur signalée")
    douleur = performances[performances["douleur"] == "Oui"]
    if douleur.empty:
        st.success("Aucune douleur signalée !")
    else:
        st.error(f"{len(douleur)} session(s) avec douleur signalée")
        st.dataframe(douleur[["date", "zone_douleur"]])

