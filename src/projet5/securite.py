"""Sécurité de l'API : vérification de la clé API envoyée dans l'en-tête X-API-Key."""
import os
import secrets

from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

# Lit le fichier .env (en local) et place ses valeurs dans les variables d'environnement.
# En production (GitHub Actions), il n'y a pas de .env : la clé vient du secret GitHub API_KEY.
load_dotenv()

# Décrit OÙ l'API attend la clé : dans l'en-tête HTTP "X-API-Key".
# Grâce à cet objet, Swagger affiche un bouton "Authorize" pour saisir la clé.
# auto_error=False : on gère nous-mêmes l'erreur, pour renvoyer un message clair.
schema_cle_api = APIKeyHeader(name="X-API-Key", auto_error=False)


def verifier_cle_api(cle_recue: str | None = Security(schema_cle_api)) -> None:
    """Laisse passer la requête si la clé reçue est la bonne, sinon répond 401."""
    # La clé attendue est lue au moment de la requête, jamais écrite dans le code
    cle_attendue = os.getenv("API_KEY")

    # Oubli de configuration côté serveur : on refuse tout plutôt que d'ouvrir l'API
    if not cle_attendue:
        raise HTTPException(status_code=500, detail="Clé API non configurée sur le serveur")

    # compare_digest compare les deux textes en un temps constant :
    # un attaquant ne peut pas deviner la clé caractère par caractère en mesurant le temps de réponse
    if cle_recue is None or not secrets.compare_digest(cle_recue, cle_attendue):
        raise HTTPException(status_code=401, detail="Clé API absente ou invalide")