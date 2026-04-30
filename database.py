import sqlite3
import os
os.makedirs("data", exist_ok=True)
DB_PATH = "data/athletes.db"

def creer_base_de_donnees():
    connexion = sqlite3.connect(DB_PATH)
    curseur = connexion.cursor()

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS athletes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            age INTEGER NOT NULL,
            sport TEXT,
            poste TEXT
        )
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS performances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            athlete_id INTEGER,
            date TEXT,
            distance_km REAL,
            vitesse_max_kmh REAL,
            acceleration REAL,
            cardio_max_bpm INTEGER,
            cardio_repos_bpm INTEGER,
            temps_recuperation REAL,
            contraction_muscle INTEGER,
            douleur TEXT,
            zone_douleur TEXT,
            FOREIGN KEY (athlete_id) REFERENCES athletes(id)
        )
    """)

    connexion.commit()
    connexion.close()
    print("Base de données prete !")

if __name__ == "__main__":
    creer_base_de_donnees()

