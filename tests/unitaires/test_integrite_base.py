"""Tests d'intégrité de la base : contenu, typage, contraintes, insertion et suppression.

Chaque test travaille dans une transaction annulée à la fin (rollback) :
la base de test retrouve toujours son état initial, quel que soit le résultat du test.
"""
import pandas as pd
import pytest
from sqlalchemy import Float, Integer, delete, func, insert, inspect, select
from sqlalchemy.exc import IntegrityError

from projet5.api import moteur
from projet5.base_de_donnees import COLONNES_DECIMALES, FEATURES_MODELE, nom_colonne_sql, table_employes, table_predictions
from projet5.modele import CHEMIN_DONNEES


@pytest.fixture
def connexion():
    """Connexion dans une transaction, annulée après le test (la base n'est jamais modifiée)."""
    with moteur.connect() as connexion:
        transaction = connexion.begin()
        yield connexion
        transaction.rollback()


def cle_technique(connexion, id_employee: int) -> int:
    """Renvoie la clé technique (employes.id) d'un employé à partir de son identifiant métier."""
    return connexion.execute(
        select(table_employes.c.id).where(table_employes.c.id_employee == id_employee)
    ).scalar()


def prediction_valide(employe_id: int, **modifications) -> dict:
    """Une prédiction correcte, dont on peut modifier un champ pour la rendre invalide."""
    valeurs = {
        "employe_id": employe_id,
        "probabilite_depart": 0.5,
        "prediction": "partant",
        "seuil_decision": 0.16,
        "version_api": "test",
    }
    valeurs.update(modifications)
    return valeurs


# ---------- Contenu et typage ----------

def test_chargement_complet_et_sans_doublon(connexion):
    # Le chargement n'a rien perdu ni dupliqué : autant de lignes en base que dans le fichier source,
    # et chaque employé n'apparaît qu'une fois (aucun nombre écrit en dur : fonctionne quelle que soit la taille)
    nombre_source = len(pd.read_csv(CHEMIN_DONNEES))
    nombre = connexion.execute(select(func.count()).select_from(table_employes)).scalar()
    distincts = connexion.execute(select(func.count(func.distinct(table_employes.c.id_employee)))).scalar()
    assert nombre == nombre_source
    assert distincts == nombre


def test_aucune_valeur_manquante(connexion):
    # Présence : aucune case vide dans la table des employés
    employes = pd.read_sql(select(table_employes), connexion)
    assert employes.isna().sum().sum() == 0


def test_types_des_colonnes(connexion):
    # Typage : on lit les types directement dans la base (et non dans notre code Python)
    types_en_base = {colonne["name"]: colonne["type"] for colonne in inspect(connexion).get_columns("employes")}

    for feature in FEATURES_MODELE:
        type_attendu = Float if feature in COLONNES_DECIMALES else Integer
        assert isinstance(types_en_base[nom_colonne_sql(feature)], type_attendu), feature


def test_index_de_la_table_predictions(connexion):
    # Volume : la table predictions grossit à chaque appel, ses colonnes de recherche doivent être indexées
    colonnes_indexees = {
        colonne
        for index in inspect(connexion).get_indexes("predictions")
        for colonne in index["column_names"]
    }
    assert {"employe_id", "date_prediction"} <= colonnes_indexees

    
# ---------- Contraintes : la base refuse les données invalides ----------

def test_prediction_hors_valeurs_autorisees_refusee(connexion):
    employe_id = cle_technique(connexion, 1273)
    with pytest.raises(IntegrityError):
        connexion.execute(insert(table_predictions).values(prediction_valide(employe_id, prediction="peut-être")))


def test_probabilite_superieure_a_1_refusee(connexion):
    employe_id = cle_technique(connexion, 1273)
    with pytest.raises(IntegrityError):
        connexion.execute(insert(table_predictions).values(prediction_valide(employe_id, probabilite_depart=1.5)))


def test_probabilite_absente_refusee(connexion):
    # NOT NULL : une prédiction sans probabilité est refusée
    employe_id = cle_technique(connexion, 1273)
    with pytest.raises(IntegrityError):
        connexion.execute(insert(table_predictions).values(prediction_valide(employe_id, probabilite_depart=None)))


def test_employe_en_double_refuse(connexion):
    # UNIQUE : on recopie l'employé 1273 sans sa clé technique, le même id_employee doit être refusé
    employe = connexion.execute(
        select(table_employes).where(table_employes.c.id_employee == 1273)
    ).mappings().first()
    copie = {colonne: valeur for colonne, valeur in employe.items() if colonne != "id"}
    with pytest.raises(IntegrityError):
        connexion.execute(insert(table_employes).values(copie))


def test_prediction_pour_employe_inexistant_refusee(connexion):
    # Clé étrangère : une prédiction doit toujours être rattachée à un employé existant
    with pytest.raises(IntegrityError):
        connexion.execute(insert(table_predictions).values(prediction_valide(employe_id=999999)))


# ---------- Insertion et suppression ----------

def test_insertion_puis_suppression_d_une_prediction(connexion):
    employe_id = cle_technique(connexion, 1273)
    compter = select(func.count()).select_from(table_predictions)
    avant = connexion.execute(compter).scalar()

    # Insertion : une ligne de plus, avec sa date remplie automatiquement
    nouvelle_id = connexion.execute(
        insert(table_predictions).values(prediction_valide(employe_id)).returning(table_predictions.c.id)
    ).scalar()
    assert connexion.execute(compter).scalar() == avant + 1
    date = connexion.execute(
        select(table_predictions.c.date_prediction).where(table_predictions.c.id == nouvelle_id)
    ).scalar()
    assert date is not None

    # Suppression : on revient au nombre de départ
    connexion.execute(delete(table_predictions).where(table_predictions.c.id == nouvelle_id))
    assert connexion.execute(compter).scalar() == avant


def test_suppression_employe_avec_predictions_refusee(connexion):
    # Clé étrangère : impossible de supprimer un employé qui a un historique de prédictions
    employe_id = cle_technique(connexion, 1273)
    connexion.execute(insert(table_predictions).values(prediction_valide(employe_id)))
    with pytest.raises(IntegrityError):
        connexion.execute(delete(table_employes).where(table_employes.c.id == employe_id))