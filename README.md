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

PostgreSQL, piloté depuis Python avec SQLAlchemy. Deux tables :

| Table | Contenu |
|---|---|
| `employes` | Dataset du projet 4 (1 470 employés) : clé technique `id`, identifiant métier `id_employee`, 40 features, réponse réelle `a_quitte_l_entreprise` |
| `predictions` | Une ligne par prédiction : employé concerné (clé étrangère), date, probabilité, prédiction, seuil, version de l'API |

Les noms de colonnes du modèle sont normalisés pour SQL (minuscules, sans accents ni caractères spéciaux),
par exemple `statut_marital_Divorcé(e)` → `statut_marital_divorce_e`. Seuls les noms changent, pas les valeurs.

**Création de la base** :
1. Dans PostgreSQL, créer un utilisateur et une base dédiés :
   ```sql
   CREATE ROLE projet5 WITH LOGIN PASSWORD '<mot_de_passe>';
   CREATE DATABASE projet5 OWNER projet5;
   ```
2. Renseigner `DATABASE_URL` dans le fichier `.env`.
3. Créer les tables et insérer le dataset :
   ```bash
   uv run python scripts/create_db.py
   ```
   ⚠️ Le script recrée les tables à chaque exécution : l'historique des prédictions est effacé.

**Traçabilité** : chaque appel réussi à `/predict` enregistre l'entrée (employé concerné) et les sorties
du modèle (probabilité, prédiction, seuil, version de l'API) dans la table `predictions`. Les requêtes
en erreur (employé inconnu, clé invalide) ne sont pas enregistrées.

**Tests** : les tests utilisent une base SQLite temporaire, créée automatiquement (`tests/conftest.py`).
Ils ne modifient jamais la base PostgreSQL et fonctionnent sans elle, notamment dans la CI.
En production, le test de fumée utilise une base PostgreSQL temporaire fournie par GitHub Actions.

Documentation détaillée du schéma (tables, contraintes, clés) : [`docs/base_de_donnees.md`](docs/base_de_donnees.md).

## Lancement de l'API

Prérequis : PostgreSQL démarré, `.env` renseigné et base créée (voir « Base de données »).
```bash
uv run uvicorn projet5.api:app --reload
```

- API : http://127.0.0.1:8000
- Documentation interactive (Swagger) : http://127.0.0.1:8000/docs
- Vérification de l'état de l'API : http://127.0.0.1:8000/health

## Utilisation

Prédiction pour un employé, à partir de son identifiant :

```bash
curl.exe -H "X-API-Key: <votre_clé>" http://127.0.0.1:8000/predict/1273
```

Réponse :
```json
{
  "id_employee": 1273,
  "prediction": "partant",
  "probabilite_depart": 0.98,
  "seuil_decision": 0.16
}
```

| Code HTTP | Signification |
|---|---|
| 200 | Prédiction effectuée |
| 401 | Clé API absente ou invalide |
| 404 | Identifiant d'employé inconnu |
| 422 | Identifiant invalide (pas un nombre entier) |

## Authentification et sécurité

**Authentification par clé API** : les routes de prédiction exigent l'en-tête HTTP `X-API-Key`.
Sans clé, ou avec une clé invalide, l'API répond `401`. La route `/health` reste publique (supervision).
Dans Swagger (`/docs`), le bouton **Authorize** permet de saisir la clé.

**Gestion des secrets** :
- La clé n'est jamais écrite dans le code : elle est lue dans la variable d'environnement `API_KEY`.
- En local, elle est définie dans le fichier `.env`, exclu du dépôt par le `.gitignore`. Le fichier
  `.env.example` indique les variables à renseigner, sans leurs valeurs.
- En production, elle est stockée dans le secret `API_KEY` de l'environnement GitHub `production`,
  accessible uniquement aux workflows qui déploient depuis `main`.
- Les tests utilisent une clé fictive, définie le temps du test.

Générer une clé :
```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Autres mesures** :
- Comparaison de la clé en temps constant (`secrets.compare_digest`), contre les attaques par mesure du temps de réponse.
- Si la clé n'est pas configurée sur le serveur, l'API refuse toutes les requêtes (`500`) plutôt que de s'ouvrir.
- Branches `main` et `develop` protégées : toute modification passe par une pull request validée par les tests.

## Tests

29 tests Pytest, organisés en deux catégories :

| Dossier | Type | Contenu |
|---|---|---|
| `tests/unitaires/` | Tests unitaires | Règle de décision, modèle (fidélité au projet 4, reproductibilité, performances), normalisation des noms de colonnes, lecture en base |
| `tests/fonctionnels/` | Tests fonctionnels | API de bout en bout : prédiction, authentification, codes d'erreur, enregistrement en base |

Les tests utilisent une base SQLite temporaire (`tests/conftest.py`) : ils ne modifient jamais la base
PostgreSQL et fonctionnent sans elle.

**Lancer les tests** :
```bash
uv run pytest -v
```

**Rapport de couverture** :
```bash
uv run pytest --cov=projet5 --cov-report=term-missing --cov-report=html
```
Le rapport détaillé est généré dans `htmlcov/index.html`. Couverture actuelle : **100 %**
(voir [`docs/rapport_couverture.md`](docs/rapport_couverture.md)).

**Dans la CI** : à chaque exécution, le tableau de couverture s'affiche sur la page du run GitHub Actions,
et les rapports (HTML + résultats JUnit) sont téléchargeables dans l'artefact `rapports-tests`.

### Points faibles identifiés et corrigés

| Point faible | Correction | Test associé |
|---|---|---|
| Modèle du projet 4 jamais sauvegardé | Export avec joblib et vérification des probabilités | `test_probabilites_identiques_au_projet_4` |
| Noms de colonnes incompatibles avec SQL (accents, espaces) | Normalisation automatique, dans les deux sens | `test_noms_sql_tous_differents`, `test_lecture_employe_valeurs_identiques_au_csv` |
| Tests dépendants de la vraie base | Base SQLite temporaire dédiée aux tests | Ensemble des tests fonctionnels |
| API ouverte si la clé n'est pas configurée | Refus de toutes les requêtes (500) | `test_prediction_refusee_si_cle_non_configuree` |
| Feature manquante | Le modèle refuse de prédire plutôt que de renvoyer un résultat faux | `test_colonne_manquante_leve_une_erreur` |
| Connexions à la base de test non refermées (`ResourceWarning`) | Fermeture explicite en fin de session de tests | Ensemble des tests |

### Limites connues
- Le contrôle de performance porte sur le dataset complet, qui inclut les données d'entraînement : il sert
  de garde-fou contre un modèle dégradé, pas de mesure de performance (voir le projet 4 pour celle-ci).
- Les tests tournent sur SQLite. Le comportement avec PostgreSQL est vérifié par le test de fumée du
  déploiement, qui utilise une vraie base PostgreSQL.
- Pas de test de charge : non requis pour ce POC.

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

**Déploiement** (`.github/workflows/cd.yml`) : à chaque fusion sur `main`, le workflow :
1. relance les tests Pytest ;
2. attend une validation manuelle dans l'environnement GitHub `production` ;
3. vérifie que le numéro de version est nouveau ;
4. réalise un **test de fumée** : il démarre l'API et vérifie que `/health` répond, qu'une prédiction
   fonctionne avec la clé de production et qu'une requête sans clé est refusée ;
5. construit le paquet de l'API et publie une release versionnée (tag `vX.Y.Z` créé automatiquement).

**Environnements et secrets** :
| Environnement | Où | Secrets |
|---|---|---|
| Développement | Poste local, branches `feature/*` et `develop` | Fichier `.env` (non versionné) |
| Test | GitHub Actions, à chaque pull request | Aucun secret nécessaire |
| Production | Environnement GitHub `production`, branche `main` uniquement | Secret `API_KEY` (environnement GitHub) |

## Besoins analytiques

La table `predictions` historise chaque utilisation du modèle. Croisée avec la table `employes`,
elle permet d'alimenter un tableau de bord de suivi. Les requêtes correspondantes sont dans
[`scripts/requetes_analyse.sql`](scripts/requetes_analyse.sql).

| Indicateur | Utilité |
|---|---|
| Nombre de prédictions et part de « partant » | Suivre l'usage de l'API et le volume d'alertes transmises aux RH |
| Activité par jour et par version de l'API | Suivre l'adoption et vérifier l'effet de chaque mise en production |
| Employés les plus à risque (dernière prédiction) | Prioriser les entretiens RH, en commençant par les probabilités les plus élevées |
| Prédictions comparées à la réalité connue | Surveiller la qualité du modèle dans le temps et détecter une dérive |
| Risque moyen selon les heures supplémentaires | Suivre l'un des principaux facteurs de départ identifiés au projet 4 |

Exemples de prédictions stockées : [`docs/exemples_predictions.csv`](docs/exemples_predictions.csv).

## Auteur
Antoine Driot