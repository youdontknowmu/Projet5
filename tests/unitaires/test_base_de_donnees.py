"""Tests unitaires du module base_de_donnees : noms de colonnes et lecture des employés."""
import pandas as pd

from projet5.base_de_donnees import FEATURES_MODELE, creer_moteur, lire_employe, nom_colonne_sql
from projet5.modele import CHEMIN_DONNEES

def test_nom_deja_propre_inchange():
    assert nom_colonne_sql("revenu_mensuel") == "revenu_mensuel"


def test_accents_et_parentheses_supprimes():
    assert nom_colonne_sql("statut_marital_Divorcé(e)") == "statut_marital_divorce_e"


def test_espaces_et_esperluette_remplaces():
    assert nom_colonne_sql("domaine_etude_Infra & Cloud") == "domaine_etude_infra_cloud"


def test_noms_sql_tous_differents():
    # Cas critique : deux features ne doivent jamais donner le même nom de colonne en base
    noms_sql = [nom_colonne_sql(feature) for feature in FEATURES_MODELE]
    assert len(set(noms_sql)) == len(FEATURES_MODELE) 


# ---------- Lecture d'un employé en base (base SQLite de test, voir tests/conftest.py) ----------

def test_lecture_employe_inconnu_renvoie_none():
    with creer_moteur().connect() as connexion:
        assert lire_employe(connexion, 999999) is None


def test_lecture_employe_redonne_les_noms_du_modele():
    # Les features lues en base doivent reprendre les noms d'origine, dans l'ordre du modèle
    with creer_moteur().connect() as connexion:
        employe_id, features = lire_employe(connexion, 1273)

    assert list(features.columns) == FEATURES_MODELE
    assert len(features) == 1


def test_lecture_employe_valeurs_identiques_au_csv():
    # Les valeurs stockées en base doivent être exactement celles du dataset d'origine
    donnees = pd.read_csv(CHEMIN_DONNEES)
    attendu = donnees[donnees["id_employee"] == 1273][FEATURES_MODELE].reset_index(drop=True)

    with creer_moteur().connect() as connexion:
        _, features = lire_employe(connexion, 1273)

    pd.testing.assert_frame_equal(features, attendu, check_dtype=False) 