"""Chargement du modèle et calcul de la probabilité de départ."""
from pathlib import Path

import joblib
import pandas as pd

# Dossier racine du projet : ce fichier est dans src/projet5/, on remonte donc de 3 niveaux
RACINE = Path(__file__).resolve().parents[2]
CHEMIN_MODELE = RACINE / "models" / "modele_xgb.joblib"
# Dataset d'origine : utilisé uniquement par scripts/create_db.py pour remplir la base
CHEMIN_DONNEES = RACINE / "data" / "employes.csv"


def charger_modele():
    """Charge le modèle XGBoost entraîné au projet 4."""
    return joblib.load(CHEMIN_MODELE)


def calculer_probabilite(modele, features: pd.DataFrame) -> float:
    """Renvoie la probabilité de départ d'un employé, à partir de ses 40 features (une ligne)."""
    # predict_proba renvoie [proba "resté", proba "parti"] : on garde la 2e colonne
    return float(modele.predict_proba(features)[0, 1])