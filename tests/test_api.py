"""Tests fonctionnels de l'API : on l'appelle comme le ferait un utilisateur."""
import pytest
from fastapi.testclient import TestClient

from projet5.api import app

# TestClient simule des appels à l'API sans démarrer de vrai serveur
client = TestClient(app)

# Clé utilisée uniquement pendant les tests (ce n'est PAS la vraie clé)
CLE_TEST = "cle-de-test"
ENTETES_VALIDES = {"X-API-Key": CLE_TEST}


# Fixture : code exécuté automatiquement avant CHAQUE test du fichier (autouse=True).
# monkeypatch.setenv définit la variable API_KEY le temps du test, puis la remet comme avant.
@pytest.fixture(autouse=True)
def cle_api_de_test(monkeypatch):
    monkeypatch.setenv("API_KEY", CLE_TEST)


# ---------- Route /health (publique) ----------

def test_health_repond_ok_sans_cle():
    # /health reste accessible sans clé : c'est la convention pour la supervision
    reponse = client.get("/health")

    assert reponse.status_code == 200            # 200 = "OK" en langage HTTP
    assert reponse.json() == {"statut": "ok"}


def test_route_inconnue_renvoie_404():
    # Scénario d'erreur : une adresse qui n'existe pas doit renvoyer 404 ("introuvable")
    reponse = client.get("/route-qui-n-existe-pas")

    assert reponse.status_code == 404


# ---------- Route /predict/{id_employee} : prédiction ----------

def test_prediction_employe_a_risque():
    # Employé 1273 : probabilité de 0,98 au projet 4, donc "partant"
    reponse = client.get("/predict/1273", headers=ENTETES_VALIDES)

    assert reponse.status_code == 200
    resultat = reponse.json()
    assert resultat["id_employee"] == 1273
    assert resultat["prediction"] == "partant"
    assert round(resultat["probabilite_depart"], 2) == 0.98


def test_prediction_employe_inconnu_renvoie_404():
    # Scénario d'erreur : identifiant absent des données
    reponse = client.get("/predict/999999", headers=ENTETES_VALIDES)

    assert reponse.status_code == 404
    assert reponse.json()["detail"] == "Employé 999999 introuvable"


def test_prediction_identifiant_non_entier_renvoie_422():
    # Scénario d'erreur : "abc" n'est pas un nombre entier, FastAPI refuse la requête tout seul
    reponse = client.get("/predict/abc", headers=ENTETES_VALIDES)

    assert reponse.status_code == 422            # 422 = données de la requête invalides


# ---------- Route /predict/{id_employee} : authentification ----------

def test_prediction_sans_cle_renvoie_401():
    # Scénario d'erreur : aucune clé envoyée
    reponse = client.get("/predict/1273")

    assert reponse.status_code == 401            # 401 = non autorisé
    assert reponse.json()["detail"] == "Clé API absente ou invalide"


def test_prediction_mauvaise_cle_renvoie_401():
    # Scénario d'erreur : une clé est envoyée, mais ce n'est pas la bonne
    reponse = client.get("/predict/1273", headers={"X-API-Key": "mauvaise-cle"})

    assert reponse.status_code == 401


def test_prediction_refusee_si_cle_non_configuree(monkeypatch):
    # Scénario d'erreur côté serveur : API_KEY n'est pas définie.
    # L'API doit tout refuser plutôt que de s'ouvrir à tout le monde.
    monkeypatch.delenv("API_KEY")
    reponse = client.get("/predict/1273", headers=ENTETES_VALIDES)

    assert reponse.status_code == 500