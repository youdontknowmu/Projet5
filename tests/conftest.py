"""Configuration commune à tous les tests (fichier lu automatiquement par Pytest, avant les tests).

Les tests n'utilisent PAS la vraie base PostgreSQL : ils travaillent sur une base SQLite
temporaire (un simple fichier), créée et remplie ici. Avantages :
  - ta vraie base n'est jamais modifiée par les tests ;
  - les tests fonctionnent aussi dans la CI de GitHub, où il n'y a pas de PostgreSQL.
"""
import os
import tempfile
from pathlib import Path

# IMPORTANT : à faire AVANT d'importer le code du projet, qui lit DATABASE_URL au démarrage.
# (load_dotenv ne remplace pas une variable déjà définie : le .env est donc ignoré pendant les tests)
DOSSIER_TEMPORAIRE = Path(tempfile.mkdtemp())
os.environ["DATABASE_URL"] = f"sqlite:///{DOSSIER_TEMPORAIRE / 'tests.db'}"

import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from projet5.base_de_donnees import creer_moteur, metadata, nom_colonne_sql  # noqa: E402
from projet5.modele import CHEMIN_DONNEES  # noqa: E402


# scope="session" : exécuté UNE seule fois pour toute la session de tests
@pytest.fixture(scope="session", autouse=True)
def base_de_test():
    """Crée les tables dans la base SQLite de test et y insère le dataset."""
    moteur = creer_moteur()
    metadata.create_all(moteur)
    donnees = pd.read_csv(CHEMIN_DONNEES).rename(columns=nom_colonne_sql)
    donnees.to_sql("employes", moteur, if_exists="append", index=False)
    yield

    # Fin des tests : on ferme proprement TOUTES les connexions ouvertes vers la base de test
    # (celle créée ici et celle de l'API), sinon Python signale des "ResourceWarning"
    from projet5.api import moteur as moteur_api

    moteur_api.dispose()
    moteur.dispose()