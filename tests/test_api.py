"""Tests fonctionnels de l'API : on l'appelle comme le ferait un utilisateur."""
from fastapi.testclient import TestClient

from projet5.api import app

# TestClient simule des appels à l'API sans démarrer de vrai serveur
client = TestClient(app)


# ---------- Route /health ----------

def test_health_repond_ok():
    reponse = client.get("/health")

    assert reponse.status_code == 200            # 200 = "OK" en langage HTTP
    assert reponse.json() == {"statut": "ok"}


def test_route_inconnue_renvoie_404():
    # Scénario d'erreur : une adresse qui n'existe pas doit renvoyer 404 ("introuvable")
    reponse = client.get("/route-qui-n-existe-pas")

    assert reponse.status_code == 404


# ---------- Route /predict/{id_employee} ----------

def test_prediction_employe_a_risque():
    # Employé 1273 : probabilité de 0,98 au projet 4, donc "partant"
    reponse = client.get("/predict/1273")

    assert reponse.status_code == 200
    resultat = reponse.json()
    assert resultat["id_employee"] == 1273
    assert resultat["prediction"] == "partant"
    assert round(resultat["probabilite_depart"], 2) == 0.98


def test_prediction_employe_inconnu_renvoie_404():
    # Scénario d'erreur : identifiant absent des données
    reponse = client.get("/predict/999999")

    assert reponse.status_code == 404
    assert reponse.json()["detail"] == "Employé 999999 introuvable"


def test_prediction_identifiant_non_entier_renvoie_422():
    # Scénario d'erreur : "abc" n'est pas un nombre entier, FastAPI refuse la requête tout seul
    reponse = client.get("/predict/abc")

    assert reponse.status_code == 422            # 422 = données de la requête invalides