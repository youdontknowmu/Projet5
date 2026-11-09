"""Base de données PostgreSQL : connexion et définition des tables (SQLAlchemy)."""
import os
import re
import unicodedata

from dotenv import load_dotenv
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    func,
)

from projet5.modele import charger_modele

# Lit le fichier .env (en local) : il contient DATABASE_URL
load_dotenv()


def nom_colonne_sql(nom: str) -> str:
    """Transforme un nom de colonne du modèle en nom compatible SQL.

    Exemple : "statut_marital_Divorcé(e)" -> "statut_marital_divorce_e"
    """
    # 1) Supprime les accents : "é" devient "e"
    nom = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
    # 2) Remplace tout ce qui n'est ni lettre ni chiffre (espaces, &, parenthèses...) par "_"
    nom = re.sub(r"[^a-zA-Z0-9]+", "_", nom)
    # 3) Retire les "_" en début et fin, et passe en minuscules
    return nom.strip("_").lower()


# Les 40 features, dans l'ordre attendu par le modèle : la table est construite à partir de cette liste
FEATURES_MODELE = list(charger_modele().feature_names_in_)

# Seule colonne décimale du dataset (toutes les autres sont des nombres entiers)
COLONNES_DECIMALES = {"taux_mobilite"}

# MetaData : le "catalogue" qui regroupe toutes les tables du projet
metadata = MetaData()

# ---------- Table employes : le dataset du projet 4, inséré une seule fois ----------
table_employes = Table(
    "employes",
    metadata,
    # Clé technique, numérotée automatiquement par PostgreSQL (distincte de l'identifiant métier)
    Column("id", Integer, primary_key=True, autoincrement=True),
    # Identifiant métier de l'employé : unique, c'est lui que l'API reçoit
    Column("id_employee", Integer, unique=True, nullable=False),
    # Les 40 features, générées à partir de la liste du modèle (noms normalisés pour SQL)
    *[
        Column(nom_colonne_sql(feature), Float if feature in COLONNES_DECIMALES else Integer, nullable=False)
        for feature in FEATURES_MODELE
    ],
    # Vraie réponse connue au projet 4 (1 = parti), conservée pour les analyses
    Column("a_quitte_l_entreprise", Integer, nullable=False),
)

# ---------- Table predictions : une ligne par appel réussi à l'API ----------
table_predictions = Table(
    "predictions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    # Entrée du modèle : l'employé concerné (lien vers la table employes)
    Column("employe_id", Integer, ForeignKey("employes.id"), nullable=False),
    # Date et heure de la prédiction, remplies automatiquement par PostgreSQL
    Column("date_prediction", DateTime(timezone=True), server_default=func.now(), nullable=False),
    # Sorties du modèle
    Column("probabilite_depart", Float, nullable=False),
    Column("prediction", String(10), nullable=False),
    Column("seuil_decision", Float, nullable=False),
    # Version de l'API (donc du modèle) qui a produit la prédiction
    Column("version_api", String(20), nullable=False),
    # Contrôles : la base refuse toute valeur incohérente
    CheckConstraint("prediction IN ('partant', 'restant')", name="ck_prediction_valeur"),
    CheckConstraint("probabilite_depart BETWEEN 0 AND 1", name="ck_probabilite_entre_0_et_1"),
)


def creer_moteur():
    """Crée la connexion à la base, à partir de DATABASE_URL (fichier .env ou variable d'environnement)."""
    return create_engine(os.environ["DATABASE_URL"])