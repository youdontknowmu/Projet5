# API de prédiction du risque de démission – POC Futurisys

Projet 5 de la formation AI Engineer (OpenClassrooms).

## Présentation
Ce projet met à disposition, sous forme d'API locale, le modèle de classification
développé au projet 4 (prédiction du risque de démission des employés de TechNova Partners).
L'API reçoit l'identifiant d'un employé, récupère ses données dans une base PostgreSQL
et renvoie la prédiction « partant » ou « restant », avec la probabilité de départ.

## Architecture

```
Projet5/
├── .github/workflows/   # Pipelines CI/CD (GitHub Actions)
├── data/                # Dataset du projet 4, prêt pour le modèle
├── docs/                # Documentation (schéma de la base de données…)
├── models/              # Modèle entraîné (.joblib)
├── scripts/             # Scripts utilitaires (création et alimentation de la base)
├── src/projet5/         # Code source de l'API
├── tests/               # Tests unitaires et fonctionnels (Pytest)
├── .env.example         # Modèle du fichier de configuration (secrets)
├── pyproject.toml       # Dépendances et configuration du projet (uv)
└── README.md
```

## Prérequis
- Python 3.14
- [uv](https://docs.astral.sh/uv/) (gestionnaire de dépendances)
- PostgreSQL

## Installation
1. Cloner le dépôt :
   ```bash
   git clone https://github.com/youdontknowmu/Projet5.git
   cd Projet5
   ```
2. Installer les dépendances (crée l'environnement virtuel `.venv`) :
   ```bash
   uv sync
   ```
   Sans uv : `pip install -r requirements.txt`
3. Créer le fichier de configuration à partir du modèle, puis renseigner les valeurs :
   ```bash
   cp .env.example .env
   ```

> Le fichier `requirements.txt` est généré depuis `uv.lock`. Après toute modification des dépendances, le régénérer avec :
> `uv export --format requirements-txt --no-hashes --no-emit-project -o requirements.txt`

## Base de données
*À compléter*

## Lancement de l'API

```bash
uv run uvicorn projet5.api:app --reload
```

- API : http://127.0.0.1:8000
- Documentation interactive (Swagger) : http://127.0.0.1:8000/docs
- Vérification de l'état de l'API : http://127.0.0.1:8000/health

## Utilisation
*À compléter*

## Authentification et sécurité
*À compléter*

## Tests
*À compléter*

## CI/CD et gestion des versions

### Organisation des branches (Gitflow léger)
| Branche | Rôle | Règle |
|---|---|---|
| `main` | Production | Ne reçoit que des fusions depuis `develop`, par pull request. Chaque fusion donne lieu à un tag de version. |
| `develop` | Intégration (développement) | Rassemble les fonctionnalités terminées, par pull request. |
| `feature/<nom-court>` | Une fonctionnalité | Créée depuis `develop`, puis fusionnée dans `develop` par pull request. |

Exemples de noms de branches : `feature/api`, `feature/base-de-donnees`, `feature/tests`.

### Convention des messages de commit
Format `type: description` ([Conventional Commits](https://www.conventionalcommits.org/fr/)) :

| Type | Usage |
|---|---|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation (README…) |
| `test` | Ajout ou modification de tests |
| `ci` | Pipeline CI/CD (GitHub Actions) |
| `chore` | Organisation, configuration, dépendances |
| `refactor` | Réorganisation du code sans changement de comportement |

### Versions
Les versions suivent le format `vMAJEUR.MINEUR.CORRECTIF` (ex. `v0.1.0`). Un tag est posé sur `main` à chaque mise en production.

### Pipeline CI/CD

![CI - Tests](https://github.com/youdontknowmu/Projet5/actions/workflows/ci.yml/badge.svg?branch=develop)

**Intégration continue** (`.github/workflows/ci.yml`) : à chaque pull request et à chaque fusion
sur `develop` ou `main`, GitHub Actions installe le projet sur une machine neuve et lance les tests
Pytest avec un rapport de couverture.

**Déploiement** (`.github/workflows/cd.yml`) : à chaque fusion sur `main`, le workflow relance les tests,
puis, après validation manuelle dans l'environnement GitHub `production`, construit le paquet de l'API
et publie une release versionnée (tag `vX.Y.Z` créé automatiquement).

**Environnements et secrets** :
| Environnement | Où | Secrets |
|---|---|---|
| Développement | Poste local, branches `feature/*` et `develop` | Fichier `.env` (non versionné) |
| Test | GitHub Actions, à chaque pull request | Aucun secret nécessaire |
| Production | Environnement GitHub `production`, branche `main` uniquement | Secret `API_KEY` (environnement GitHub) |

## Besoins analytiques
*À compléter*

## Auteur
Antoine Driot