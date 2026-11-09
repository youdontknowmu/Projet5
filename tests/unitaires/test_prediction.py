"""Tests unitaires de la règle de décision."""
import pytest

from projet5.prediction import SEUIL_DECISION, interpreter_probabilite


# Pytest exécute toute fonction dont le nom commence par "test_".
# "assert" vérifie qu'une condition est vraie : sinon, le test échoue.

def test_probabilite_elevee_donne_partant():
    assert interpreter_probabilite(0.80) == "partant"


def test_probabilite_faible_donne_restant():
    assert interpreter_probabilite(0.05) == "restant"


def test_probabilite_egale_au_seuil_donne_partant():
    # Cas limite : pile sur le seuil, l'employé doit être signalé
    assert interpreter_probabilite(SEUIL_DECISION) == "partant"


# Scénario d'erreur : une probabilité hors de [0, 1] doit être refusée.
# parametrize lance le même test une fois par valeur de la liste (ici 2 fois).
@pytest.mark.parametrize("valeur", [-0.1, 1.5])
def test_probabilite_invalide_leve_une_erreur(valeur):
    # pytest.raises : le test réussit SI la fonction lève bien une ValueError
    with pytest.raises(ValueError):
        interpreter_probabilite(valeur)