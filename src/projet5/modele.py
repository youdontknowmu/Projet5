"""Chargement du modèle et des données, puis calcul de la probabilité de départ."""
from pathlib import Path

import joblib
import pandas as pd

# Dossier racine du projet : ce fichier est dans src/projet5/, on remonte donc de 3 niveaux
RACINE = Path(__file__).resolve().parents[2]
CHEMIN_MODELE = RACINE / "models" / "modele_xgb.joblib"
CHEMIN_DONNEES = RACINE / "data" / "employes.csv"


def charger_modele():
    """Charge le modèle XGBoost entraîné au projet 4."""
    return joblib.load(CHEMIN_MODELE)


def charger_donnees() -> pd.DataFrame:
    """Charge le dataset des employés, indexé par id_employee pour retrouver un employé rapidement.

    Provisoire : à l'étape 4, ces données seront lues dans PostgreSQL.
    """
    return pd.read_csv(CHEMIN_DONNEES).set_index("id_employee")


def calculer_probabilite(modele, donnees: pd.DataFrame, id_employee: int) -> float:
    """Renvoie la probabilité de départ de l'employé demandé.

    Lève une KeyError si l'identifiant n'existe pas dans les données.
    """
    # .loc[[id]] (double crochet) : renvoie un tableau d'UNE ligne, le format attendu par le modèle
    employe = donnees.loc[[id_employee]]

    # On garde les 40 colonnes du modèle, dans l'ordre exact de l'entraînement
    features = employe[modele.feature_names_in_]

    # predict_proba renvoie [proba "resté", proba "parti"] : on garde la 2e colonne
    return float(modele.predict_proba(features)[0, 1])