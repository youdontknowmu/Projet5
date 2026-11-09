"""Exporte un échantillon de prédictions enregistrées en base, au format CSV.

Lancement : uv run python scripts/exporter_exemples.py
Résultat  : docs/exemples_predictions.csv (entrées et sorties du modèle, telles que stockées en base)
"""
import pandas as pd
from sqlalchemy import text

from projet5.base_de_donnees import creer_moteur
from projet5.modele import RACINE

CHEMIN_EXPORT = RACINE / "docs" / "exemples_predictions.csv"

# Jointure predictions + employes : pour chaque prédiction, on affiche l'identifiant métier
# de l'employé (l'entrée), quelques-unes de ses features, puis les sorties du modèle.
REQUETE = text("""
    SELECT p.id                    AS id_prediction,
           p.date_prediction,
           e.id_employee,
           e.age,
           e.revenu_mensuel,
           e.heures_supplementaires,
           e.annees_dans_l_entreprise,
           p.probabilite_depart,
           p.prediction,
           p.seuil_decision,
           p.version_api
    FROM predictions p
    JOIN employes e ON e.id = p.employe_id
    ORDER BY p.id
    LIMIT 20
""")

with creer_moteur().connect() as connexion:
    exemples = pd.read_sql(REQUETE, connexion)

exemples.to_csv(CHEMIN_EXPORT, index=False)
print(f"{len(exemples)} prédictions exportées dans {CHEMIN_EXPORT.relative_to(RACINE)}")
print(exemples.head())