"""Schémas de données de l'API (Pydantic).

Un schéma décrit précisément la forme d'une réponse : nom, type et signification de chaque champ.
FastAPI s'en sert pour :
  - vérifier que la réponse respecte bien ce format ;
  - générer automatiquement la documentation Swagger (/docs), avec des exemples.
"""
from typing import Literal

from pydantic import BaseModel, Field


class Sante(BaseModel):
    """Réponse de la route /health."""

    statut: str = Field(description="État de l'API", examples=["ok"])


class Prediction(BaseModel):
    """Réponse de la route de prédiction."""

    id_employee: int = Field(description="Identifiant de l'employé", examples=[1273])
    # Literal : seules ces deux valeurs sont possibles
    prediction: Literal["partant", "restant"] = Field(
        description="Prédiction du modèle", examples=["partant"]
    )
    probabilite_depart: float = Field(
        description="Probabilité de départ estimée par le modèle (entre 0 et 1)", examples=[0.98]
    )
    seuil_decision: float = Field(
        description="Seuil au-delà duquel l'employé est considéré comme partant", examples=[0.16]
    )


class Erreur(BaseModel):
    """Réponse renvoyée en cas d'erreur (format standard de FastAPI)."""

    detail: str = Field(description="Message expliquant l'erreur", examples=["Employé 999999 introuvable"])