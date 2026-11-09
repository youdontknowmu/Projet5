"""Crée les tables dans PostgreSQL, puis insère le dataset des employés.

Lancement : uv run python scripts/create_db.py

ATTENTION : le script repart de zéro. Il supprime les tables existantes (et donc l'historique
des prédictions) avant de les recréer. Il peut ainsi être relancé autant de fois que nécessaire.
"""
import pandas as pd
from sqlalchemy import func, select

from projet5.base_de_donnees import creer_moteur, metadata, nom_colonne_sql, table_employes
from projet5.modele import CHEMIN_DONNEES

moteur = creer_moteur()

# 1) Suppression puis création des tables (dans le bon ordre, grâce au catalogue "metadata")
metadata.drop_all(moteur)
metadata.create_all(moteur)
print("Tables créées :", ", ".join(metadata.tables))

# 2) Lecture du CSV et normalisation des NOMS de colonnes (les valeurs ne sont pas modifiées)
donnees = pd.read_csv(CHEMIN_DONNEES).rename(columns=nom_colonne_sql)

# 3) Insertion des employés dans la table existante (if_exists="append" : on garde notre structure)
donnees.to_sql("employes", moteur, if_exists="append", index=False)

# 4) Vérification : on recompte les lignes directement dans la base
with moteur.connect() as connexion:
    nombre = connexion.execute(select(func.count()).select_from(table_employes)).scalar()
print(f"Employés insérés : {nombre} (attendu : 1470)")