"""API de prédiction du risque de démission (POC Futurisys)."""
from importlib.metadata import version

from fastapi import FastAPI

# Création de l'application.
# Le titre, la description et la version s'affichent dans la documentation Swagger (/docs).
# version("projet5") lit le numéro de version dans pyproject.toml : il n'est écrit qu'à un seul endroit.
app = FastAPI(
    title="API Futurisys - Risque de démission",
    description="Prédit si un employé risque de quitter l'entreprise, à partir du modèle entraîné au projet 4.",
    version=version("projet5"),
)


# @app.get("/health") : quand quelqu'un appelle l'adresse /health (méthode GET),
# FastAPI exécute la fonction juste en dessous et renvoie son résultat en JSON.
# tags : range la route dans une rubrique de la documentation Swagger.
@app.get("/health", tags=["Supervision"])
def verifier_sante() -> dict:
    """Indique que l'API est démarrée et répond."""
    return {"statut": "ok"}