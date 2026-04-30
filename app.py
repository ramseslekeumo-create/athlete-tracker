from prediction import faire_prediction
from analyse import afficher_analyse
import streamlit as st
import sqlite3
import pandas as pd
from database import creer_base_de_donnees

#Initialisation de la base de données
creer_base_de_donnees()

#configuration de la page
st.set_page_config(
    page_title="Athlete Tracker",
    page_icon="⚽",
    layout="wide"
)

#Titre principal
st.title("⚽ Athlete Tracker")
st.markdown("---")

#menu de navigation
menu = st.sidebar.selectbox("Navigation", [
    "Accueil",
    "Ajouter un athlète",
    "saisir une performance",
    "voir les données",
    "Analyse",
    "Prédiction"
])

#--- PAGE D'ACCUEIL ---
if menu == "Accueil":
    st.header("Bienvenue sur Athlete Tracker 🥇")
    st.markdown("*suivi intelligent des performances sportives*")
    st.markdown("---")

#--- chiffre clés en temps réel
    connexion = sqlite3.connect("data/athletes.db")
    total_athletes = pd.read_sql(
        "SELECT COUNT(*) as total FROM athletes",connexion
    )
    total_sessions = pd.read_sql(
    "SELECT COUNT(*) as total FROM performances",connexion
    )
    alertes = pd.read_sql(
        "SELECT COUNT(*) as total FROM performances WHERE douleur = 'Oui'",
        connexion
    )
    connexion.close()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👤 Athlètes",total_athletes["total"][0])
    with col2:
        st.metric("📝 sessions",total_sessions["total"][0])
    with col3:
        st.metric("⚠️ Alertes blessures", alertes["total"][0])
    st.markdown("---")
    st.info("""
    ### Comment utiliser l'application ?
    1. 📝 **Ajouter un athlète**      (Cree le profil)
    2. 📝 **Saisir une performance**  (Entrer les stats )
    3. 📈 **Analyse**                 (Voir la progression)
    4. 🎯 **Prédiction**              (Evaluer les limites)
    """)


#--- PAGE AJOUTER UN ATHLETE ---
elif menu == "Ajouter un athlète":
    st.header("Ajouter un athlète")

    nom    = st.text_input("Nom")
    prenom = st.text_input("prenom")
    age    = st.number_input("Age", min_value=10, max_value=60)
    sport  = st.selectbox("Sport",[
        "Football", "Basketball", "Athlétisme", 
        "Natation", "Rugby", "Tennis"
    ])
    poste  = st.text_input("poste / spécialité")
    if st.button("Enregistrer l'athlète"):
        connexion = sqlite3.connect("data/athletes.db")
        curseur = connexion.cursor()
        curseur.execute("""
            INSERT INTO athletes(nom, prenom, age, sport, poste)
            VALUES (?, ?, ?, ?, ?)
        """, (nom, prenom, age, sport, poste))
        connexion.commit()
        connexion.close()
        st.success(f"✅ Athlète {prenom} {nom} enregistré !")

#--- PAGE SAISIR UNE PERFORMANCE ---
elif menu == "saisir une performance":
    st.header("saisir une performance")

    # charger la liste des athlètes
    connexion = sqlite3.connect("data/athletes.db")
    athletes = pd.read_sql("SELECT * FROM athletes", connexion)
    connexion.close()

    if athletes.empty:
        st.warning("⚠️ Aucun athlète enregistrer. Ajouter-en un d'abord.")
    else:
        noms = athletes["nom"] + " " + athletes["prenom"]
        choix = st.selectbox("sélectionner un athlète", noms)
        athlete_id = athletes[
            (athletes["nom"] + " " + athletes["prenom"]) == choix
        ]["id"].values[0]

        st.markdown("### 📅 Date")
        date = st.date_input("Date de la session")

        st.markdown("### 🏃 Données physiques")
        distance    = st.number_input("Distance parcourue(km)",0.0, 80.0)
        vitesse     = st.number_input("vitesse maximal(km/h)", 0.0, 50.0)
        acceleration = st.number_input("Accéleration(m/s^2)", 0.0, 20.0)

        st.markdown("### ❤️ Données cardio")
        cardio_max   = st.number_input("Frequence cardiaque max (bpm)", 0, 250)
        cardio_repos = st.number_input("Frequance cardiaque repos (bpm)" , 0, 150)
        recuperation = st.number_input("Temps de récuperation (min)", 0.0, 60.0)

        st.markdown("### 💪 Données musculaires")
        contraction = st.slider("Contraction musculaire post-effort(1-10)", 1, 10)
        douleur     = st.radio("Douleur signalée ?", ["Non", "Oui"])
        zone        = ""
        if douleur == "Oui":
            zone = st.text_input("zone douleureuse (ex: cuisse gauche)")

        if st.button("Enregistrer la performance"):
            connexion = sqlite3.connect("data/athletes.db")
            curseur = connexion.cursor()
            curseur.execute("""
                INSERT INTO performances (
                    athlete_id, date, distance_km, vitesse_max_kmh,
                    acceleration, cardio_max_bpm, cardio_repos_bpm,
                    temps_recuperation, contraction_muscle,
                    douleur, zone_douleur
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    athlete_id, str(date), distance, vitesse, 
                    acceleration, cardio_max, cardio_repos,
                    recuperation, contraction, douleur, zone
            ))
            connexion.commit()
            connexion.close()
            st.success("✅ Performance enregistrée !")

# --- PAGE VOIR LES DONNEES ---
elif menu == "voir les données":
    st.header("👤 Profils des athlètes")

    connexion = sqlite3.connect("data/athletes.db")
    athletes = pd.read_sql("SELECT * FROM athletes", connexion)
    perfs = pd.read_sql("SELECT * FROM performances", connexion)
    connexion.close()

    if athletes.empty:
        st.warning("⚠️ Aucun athlète enregistré. Ajouter-en un d'abord.")
    else:
        for _, athlete in athletes.iterrows():
            perfs_athlete = perfs[perfs["athlete_id"] == athlete["id"]]
            nb_sessions = len(perfs_athlete)

            if nb_sessions == 0:
                risque = "Aucune donnée"
                couleur = "⚪"
            else:
                nb_douleurs = len(perfs_athlete[perfs_athlete["douleur"] == "Oui"])
                cardio_max  = perfs_athlete["cardio_max_bpm"].max()
                contraction  = perfs_athlete["contraction_muscle"].max()

                if nb_douleurs > 0 or cardio_max >= 190 or contraction >= 8:
                    risque = "⚠️ Risque de blessure"
                    couleur = "🔴"
                elif cardio_max >= 170 or contraction >= 6:
                    risque = "⚠️ Risque modéré"
                    couleur = "🟠"
                else:
                    risque = "✅ Risque faible"
                    couleur = "🟢"
            # afficher le profil
            with st.expander(
                f"👤 {athlete['prenom']} {athlete['nom']} -"
                f"⚽ {athlete['sport']} - {couleur} Risque {risque}"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Nom complet :** {athlete['prenom']} {athlete['nom']}")
                    st.markdown(f"**Age :** {athlete['age']} ans")
                    st.markdown(f"**Sport :** {athlete['sport']}")
                    st.markdown(f"**Poste :** {athlete['poste']}")
                with col2:
                    st.markdown(f"**Sessions enregistrées :** {nb_sessions}")
                    if nb_sessions > 0:
                        st.markdown(f"**Distance moy. :** {round(perfs_athlete['distance_km'].mean(), 2)} km")
                        st.markdown(f"**Vitesse max :** {perfs_athlete['vitesse_max_kmh'].max()} km/h")
                        st.markdown(f"**Risque blessure :**{couleur} {risque}")
        st.markdown("---")
        st.subheader("📊 Toute les performances ")
        st.dataframe(perfs)

elif menu == "Analyse":
    st.header("📊 Analyse des performances")
    connexion = sqlite3.connect("data/athletes.db")
    athletes = pd.read_sql("SELECT * FROM athletes", connexion)
    connexion.close()

    if athletes.empty:
        st.warning("⚠️ Aucun athlète enregistré. Ajouter-en un d'abord.")
    else:
        noms = athletes["nom"] + " " + athletes["prenom"]
        choix = st.selectbox("sélectionner un athlète", noms)
        athlete_id = athletes[
            (athletes["nom"] + " " + athletes["prenom"]) == choix
        ]["id"].values[0]

        connexion = sqlite3.connect("data/athletes.db")
        perfs = pd.read_sql(
            "SELECT * FROM performances WHERE athlete_id = ?",
            connexion,
            params=(athlete_id,)
        )
        connexion.close()

        afficher_analyse(perfs, choix)

elif menu == "Prédiction":
    st.header("🎯 Prédiction des performances")

    connexion = sqlite3.connect("data/athletes.db")
    athletes  = pd.read_sql("SELECT * FROM athletes", connexion)
    connexion.close()

    if athletes.empty:
        st.warning("⚠️ Aucun athlète enregistré. Ajouter-en un d'abord.")
    else:
        noms = athletes["nom"] + " " + athletes["prenom"]
        choix = st.selectbox("sélectionner un athlète", noms)
        athlete_id = athletes[
            (athletes["nom"] + " " + athletes["prenom"]) == choix
        ]["id"].values[0]

        connexion = sqlite3.connect("data/athletes.db")
        perfs = pd.read_sql(
            "SELECT * FROM performances WHERE athlete_id = ?",
            connexion,
            params=(athlete_id,)
        )
        connexion.close()

        faire_prediction(perfs)