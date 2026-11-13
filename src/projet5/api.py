"""API de prédiction du risque de démission (POC Futurisys)."""
from importlib.metadata import version

from fastapi import Depends, FastAPI, HTTPException

from projet5.base_de_donnees import creer_moteur, enregistrer_prediction, lire_employe
from projet5.modele import calculer_probabilite, charger_modele
from projet5.prediction import SEUIL_DECISION, interpreter_probabilite
from projet5.schemas import Erreur, Prediction, Sante
from projet5.securite import verifier_cle_api

# Numéro de version lu dans pyproject.toml : il n'est écrit qu'à un seul endroit
VERSION_API = version("projet5")

# Création de l'application.
# Le titre, la description et la version s'affichent dans la documentation Swagger (/docs).
# La description accepte le format Markdown : elle s'affiche en haut de la page Swagger.
DESCRIPTION = """
Prédit si un employé risque de quitter l'entreprise, à partir du modèle entraîné au projet 4.

**Authentification** : les routes de prédiction exigent une clé API dans l'en-tête `X-API-Key`
(bouton **Authorize** ci-dessous).

**Traçabilité** : chaque prédiction réussie est enregistrée dans la base PostgreSQL (table `predictions`).
"""

app = FastAPI(
    title="API Futurisys - Risque de démission",
    description=DESCRIPTION,
    version=VERSION_API,
)

# Créés UNE seule fois, au démarrage de l'API (et non à chaque requête : ce serait beaucoup plus lent)
modele = charger_modele()
moteur = creer_moteur()


def obtenir_connexion():
    """Ouvre une connexion à la base pour la durée d'une requête.

    moteur.begin() ouvre une transaction : si la requête se termine bien, les écritures sont
    validées (commit) ; en cas d'erreur, elles sont toutes annulées (rollback).
    """
    with moteur.begin() as connexion:
        yield connexion


# @app.get("/health") : quand quelqu'un appelle l'adresse /health (méthode GET),
# FastAPI exécute la fonction juste en dessous et renvoie son résultat en JSON.
# response_model : le schéma de la réponse (vérification + documentation Swagger).
@app.get("/health", response_model=Sante, tags=["Supervision"], summary="Vérifier que l'API répond")
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
    summary="Prédire le risque de départ d'un employé",
    # Erreurs possibles, affichées dans Swagger avec leur format et un exemple
    # (l'erreur 422 de validation est documentée automatiquement par FastAPI)
    responses={
        401: {"model": Erreur, "description": "Clé API absente ou invalide"},
        404: {"model": Erreur, "description": "Aucun employé avec cet identifiant"},
        500: {"model": Erreur, "description": "Clé API non configurée sur le serveur"},
    },
)
def predire(id_employee: int, connexion=Depends(obtenir_connexion)) -> Prediction:
    """Prédit si l'employé risque de quitter l'entreprise, et enregistre la prédiction en base."""
    # 1) Lecture de l'employé dans PostgreSQL
    employe = lire_employe(connexion, id_employee)
    if employe is None:
        # Identifiant absent de la base : erreur 404 "introuvable" avec un message clair
        raise HTTPException(status_code=404, detail=f"Employé {id_employee} introuvable")
    employe_id, features = employe

    # 2) Calcul par le modèle
    probabilite = round(calculer_probabilite(modele, features), 4)
    prediction = interpreter_probabilite(probabilite)

    # 3) Enregistrement de l'entrée et des sorties dans la table predictions
    enregistrer_prediction(connexion, employe_id, probabilite, prediction, SEUIL_DECISION, VERSION_API)

    return Prediction(
        id_employee=id_employee,
        prediction=prediction,
        probabilite_depart=probabilite,
        seuil_decision=SEUIL_DECISION,
    )