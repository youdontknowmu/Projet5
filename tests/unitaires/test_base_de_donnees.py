"""Tests unitaires de la normalisation des noms de colonnes pour SQL."""
from projet5.base_de_donnees import FEATURES_MODELE, nom_colonne_sql


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