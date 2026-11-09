"""Tests unitaires du modèle : fidélité au projet 4, cohérence, reproductibilité et performances."""
import pandas as pd
import pytest
from sklearn.metrics import recall_score

from projet5.modele import CHEMIN_DONNEES, calculer_probabilite, charger_modele
from projet5.prediction import SEUIL_DECISION

# Chargés une seule fois pour tout le fichier
MODELE = charger_modele()
DONNEES = pd.read_csv(CHEMIN_DONNEES)


def features_employe(id_employee: int) -> pd.DataFrame:
    """Renvoie les 40 features d'un employé (une ligne), au format attendu par le modèle."""
    employe = DONNEES[DONNEES["id_employee"] == id_employee]
    return employe[MODELE.feature_names_in_]


# parametrize : le même test est lancé pour chaque couple (employé, probabilité attendue)
@pytest.mark.parametrize("id_employee, probabilite_p4", [(1273, 0.98), (959, 0.93), (478, 0.87)])
def test_probabilites_identiques_au_projet_4(id_employee, probabilite_p4):
    # Le modèle exporté doit redonner exactement les valeurs obtenues dans le notebook du projet 4
    probabilite = calculer_probabilite(MODELE, features_employe(id_employee))
    assert round(probabilite, 2) == probabilite_p4


def test_probabilites_toutes_entre_0_et_1():
    # Cas critique : pour les 1 470 employés, une probabilité doit toujours être dans [0, 1]
    probabilites = MODELE.predict_proba(DONNEES[MODELE.feature_names_in_])[:, 1]
    assert probabilites.min() >= 0
    assert probabilites.max() <= 1


def test_prediction_reproductible():
    # Reproductibilité : la même entrée donne toujours exactement le même résultat
    features = features_employe(1273)
    assert calculer_probabilite(MODELE, features) == calculer_probabilite(MODELE, features)


def test_colonne_manquante_leve_une_erreur():
    # Scénario d'erreur : s'il manque une feature, le modèle refuse de prédire
    # (plutôt que de renvoyer un résultat faux sans prévenir)
    features_incompletes = features_employe(1273).drop(columns=["age"])
    with pytest.raises(ValueError):
        calculer_probabilite(MODELE, features_incompletes)


def test_performances_non_degradees():
    # Contrôle de performance (non-régression) : avec le seuil de 0,16, le modèle doit détecter
    # au moins 74 % des départs réels, soit le rappel mesuré sur le jeu de test au projet 4.
    # Sur le dataset complet (qui inclut les données d'entraînement), on obtient environ 0,81.
    probabilites = MODELE.predict_proba(DONNEES[MODELE.feature_names_in_])[:, 1]
    predictions = (probabilites >= SEUIL_DECISION).astype(int)
    rappel = recall_score(DONNEES["a_quitte_l_entreprise"], predictions)
    assert rappel >= 0.74