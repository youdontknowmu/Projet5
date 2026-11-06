"""Tests fonctionnels de l'API : on l'appelle comme le ferait un utilisateur."""
from fastapi.testclient import TestClient

from projet5.api import app

# TestClient simule des appels à l'API sans démarrer de vrai serveur
client = TestClient(app)


def test_health_repond_ok():
    reponse = client.get("/health")

    assert reponse.status_code == 200            # 200 = "OK" en langage HTTP
    assert reponse.json() == {"statut": "ok"}


def test_route_inconnue_renvoie_404():
    # Scénario d'erreur : une adresse qui n'existe pas doit renvoyer 404 ("introuvable")
    reponse = client.get("/route-qui-n-existe-pas")

    assert reponse.status_code == 404