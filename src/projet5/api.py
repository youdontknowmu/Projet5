"""API de prédiction du risque de démission (POC Futurisys)."""
from importlib.metadata import version

from fastapi import Depends, FastAPI, HTTPException

from projet5.modele import calculer_probabilite, charger_donnees, charger_modele
from projet5.prediction import SEUIL_DECISION, interpreter_probabilite
from projet5.schemas import Prediction, Sante
from projet5.securite import verifier_cle_api

# Création de l'application.
# Le titre, la description et la version s'affichent dans la documentation Swagger (/docs).
# version("projet5") lit le numéro de version dans pyproject.toml : il n'est écrit qu'à un seul endroit.
app = FastAPI(
    title="API Futurisys - Risque de démission",
    description="Prédit si un employé risque de quitter l'entreprise, à partir du modèle entraîné au projet 4.",
    version=version("projet5"),
)

# Chargés UNE seule fois, au démarrage de l'API (et non à chaque requête : ce serait beaucoup plus lent)
modele = charger_modele()
donnees = charger_donnees()


# @app.get("/health") : quand quelqu'un appelle l'adresse /health (méthode GET),
# FastAPI exécute la fonction juste en dessous et renvoie son résultat en JSON.
# response_model : le schéma de la réponse (vérification + documentation Swagger).
@app.get("/health", response_model=Sante, tags=["Supervision"])
def verifier_sante() -> Sante:
    """Indique que l'API est démarrée et répond."""
    return Sante(statut="ok")


# {id_employee} : partie variable de l'adresse. Exemple : /predict/1273
# Le type "int" dans la fonction fait vérifier par FastAPI que c'est bien un nombre entier
# (sinon il répond automatiquement une erreur 422).
# dependencies : avant d'exécuter la fonction, FastAPI appelle verifier_cle_api.
# Si la clé est absente ou fausse, la requête s'arrête là (erreur 401).
@app.get(
    "/predict/{id_employee}",
    response_model=Prediction,
    tags=["Prédiction"],
    dependencies=[Depends(verifier_cle_api)],
)
def predire(id_employee: int) -> Prediction:
    """Prédit si l'employé risque de quitter l'entreprise."""
    try:
        probabilite = calculer_probabilite(modele, donnees, id_employee)
    except KeyError:
        # Identifiant absent des données : erreur 404 "introuvable" avec un message clair
        raise HTTPException(status_code=404, detail=f"Employé {id_employee} introuvable")

    return Prediction(
        id_employee=id_employee,
        prediction=interpreter_probabilite(probabilite),
        probabilite_depart=round(probabilite, 4),
        seuil_decision=SEUIL_DECISION,
    )