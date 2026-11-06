"""Vérifie que le modèle et le dataset exportés depuis le projet 4 sont cohérents.

Lancement : uv run python scripts/verifier_export.py
"""
import joblib
import pandas as pd

# 1) Chargement des deux fichiers exportés
modele = joblib.load("models/modele_xgb.joblib")
donnees = pd.read_csv("data/employes.csv")
print("Dataset :", donnees.shape)   # attendu : (1470, 42)

# 2) On garde uniquement les 40 colonnes que le modèle attend, dans le même ordre qu'à l'entraînement
features = donnees[modele.feature_names_in_]

# 3) Probabilité de départ pour chaque employé (colonne 1 = classe "parti")
donnees["probabilite_depart"] = modele.predict_proba(features)[:, 1]

# 4) Comparaison avec les valeurs du projet 4 (attendu : 0.98, 0.93, 0.87)
controle = donnees[donnees["id_employee"].isin([1273, 959, 478])]
print(controle[["id_employee", "probabilite_depart"]].round(2))