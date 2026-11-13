# API de prédiction du risque de démission – POC Futurisys

![CI - Tests](https://github.com/youdontknowmu/Projet5/actions/workflows/ci.yml/badge.svg?branch=develop)
![Python](https://img.shields.io/badge/python-3.14-blue)
![Couverture](https://img.shields.io/badge/couverture-100%25-brightgreen)

Projet 5 de la formation AI Engineer (OpenClassrooms).

## Sommaire
1. [Présentation](#présentation)
2. [Architecture](#architecture)
3. [Choix techniques](#choix-techniques)
4. [Prérequis](#prérequis)
5. [Installation](#installation)
6. [Base de données](#base-de-données)
7. [Lancement de l'API](#lancement-de-lapi)
8. [Utilisation](#utilisation)
9. [Modèle de machine learning](#modèle-de-machine-learning)
10. [Authentification et sécurité](#authentification-et-sécurité)
11. [Tests](#tests)
12. [CI/CD et gestion des versions](#cicd-et-gestion-des-versions)
13. [Déploiement](#déploiement)
14. [Besoins analytiques](#besoins-analytiques)
15. [Pistes d'amélioration](#pistes-damélioration)

## Présentation
Ce projet met à disposition, sous forme d'API locale, le modèle de classification
développé au projet 4 (prédiction du risque de démission des employés de TechNova Partners).
L'API reçoit l'identifiant d'un employé, récupère ses données dans une base PostgreSQL
et renvoie la prédiction « partant » ou « restant », avec la probabilité de départ.

**Cas d'usage** : aider les équipes RH à **prioriser les entretiens préventifs**. Plus la probabilité
de départ est élevée, plus l'entretien est urgent. Le modèle ne prend aucune décision : il signale,
et la décision reste humaine.

## Architecture

```
Client (RH, Swagger)
        │  GET /predict/1273 + en-tête X-API-Key
        ▼
┌─────────────────────── API FastAPI (uvicorn) ────────────────────────┐
│ 1. securite.py         vérifie la clé API          (sinon 401)       │
│ 2. base_de_donnees.py  lit l'employé               (sinon 404)       │◄── PostgreSQL : table employes
│ 3. modele.py           calcule la probabilité (XGBoost)              │
│ 4. prediction.py       applique le seuil de 0,16                     │
│ 5. base_de_donnees.py  enregistre la prédiction                      │──► PostgreSQL : table predictions
└──────────────────────────────────────────────────────────────────────┘
        │
        ▼
Réponse JSON : prédiction + probabilité
```

```
Projet5/
├── .github/workflows/   # Pipelines CI/CD (GitHub Actions)
├── data/                # Dataset du projet 4, prêt pour le modèle
├── docs/                # Documentation (schéma de la base, exemples, rapport de couverture)
├── models/              # Modèle entraîné (.joblib)
├── scripts/             # Scripts utilitaires (création de la base, export, requêtes d'analyse)
├── src/projet5/         # Code source de l'API
│   ├── api.py             # Routes FastAPI
│   ├── base_de_donnees.py # Tables, connexion, lecture et enregistrement en base
│   ├── modele.py          # Chargement du modèle et calcul de la probabilité
│   ├── prediction.py      # Règle de décision (seuil)
│   ├── schemas.py         # Schémas des réponses (Pydantic)
│   └── securite.py        # Vérification de la clé API
├── tests/               # Tests unitaires et fonctionnels (Pytest)
├── .env.example         # Modèle du fichier de configuration (secrets)
├── pyproject.toml       # Dépendances et configuration du projet (uv)
└── README.md
```

## Choix techniques

| Besoin | Choix | Justification |
|---|---|---|
| API | **FastAPI** + uvicorn | Documentation Swagger générée automatiquement, validation des entrées et des sorties avec Pydantic |
| Dépendances | **uv** (`pyproject.toml` + `uv.lock`) | Installation rapide et versions figées : le même environnement partout (poste, CI, déploiement). `requirements.txt` exporté pour pip |
| Modèle | **XGBoost** du projet 4, sauvegardé avec **joblib** | Modèle retenu au projet 4 ; versions de `xgboost` et `scikit-learn` figées pour que le fichier se recharge à l'identique |
| Base de données | **PostgreSQL** + **SQLAlchemy** | Base relationnelle robuste (contraintes, clés étrangères, index) ; SQLAlchemy permet d'écrire les tables en Python et de changer de base (PostgreSQL en production, SQLite en test) |
| Authentification | **Clé API** dans un en-tête HTTP | Réponse proportionnée pour un POC : l'API ne répond qu'aux détenteurs de la clé |
| Tests | **Pytest** + pytest-cov, base **SQLite temporaire** | Tests rapides, reproductibles, sans risque pour la vraie base et exécutables dans la CI |
| Gestion de versions | **Gitflow léger** (`main`, `develop`, `feature/*`) | Rien n'arrive en production sans pull request ni tests verts ; plus simple que le Gitflow complet pour un développeur seul |
| CI/CD | **GitHub Actions** | Intégré au dépôt, gratuit, environnements et secrets natifs |
| Déploiement | Release GitHub après validation manuelle | Hébergement cloud non requis (Hugging Face devenu payant) ; le pipeline reproduit toutes les étapes d'un vrai déploiement (voir [Déploiement](#déploiement)) |

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

### Cycle de vie des données

| Étape | Données | Où | Comment |
|---|---|---|---|
| 1. Source | Dataset du projet 4, déjà nettoyé et encodé | `data/employes.csv` | Export depuis le notebook du projet 4 |
| 2. Chargement | 1 470 employés | Table `employes` | `scripts/create_db.py` (noms de colonnes normalisés, valeurs inchangées) |
| 3. Lecture | Les 40 features d'un employé | Table `employes` | À chaque appel de `/predict`, par l'identifiant `id_employee` (colonne indexée) |
| 4. Journalisation | Entrée (employé) et sorties du modèle | Table `predictions` | Une ligne par prédiction réussie, dans la même transaction que la lecture |
| 5. Analyse | Indicateurs de suivi | Requêtes SQL | `scripts/requetes_analyse.sql`, export d'exemples avec `scripts/exporter_exemples.py` |
| 6. Conservation | Historique des prédictions | Table `predictions` | Conservé tant que la base n'est pas réinitialisée ; une durée de conservation serait à définir en production (RGPD) |

**Traçabilité** : chaque appel réussi à `/predict` enregistre l'entrée (employé concerné) et les sorties
du modèle (probabilité, prédiction, seuil, version de l'API) dans la table `predictions`. Les requêtes
en erreur (employé inconnu, clé invalide) ne sont pas enregistrées. La table `predictions` ne contient
que la clé technique de l'employé, jamais son identifiant métier.

**Volume** : la table `predictions` grossit à chaque appel ; ses colonnes de recherche (`employe_id`,
`date_prediction`) sont indexées.

Documentation détaillée du schéma (tables, contraintes, clés, index) : [`docs/base_de_donnees.md`](docs/base_de_donnees.md).

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
| 200 | Prédiction effectuée (et enregistrée en base) |
| 401 | Clé API absente ou invalide |
| 404 | Identifiant d'employé inconnu |
| 422 | Identifiant invalide (pas un nombre entier) |
| 500 | Clé API non configurée sur le serveur |

Toutes ces réponses, avec leur format et un exemple, sont décrites dans la documentation Swagger (`/docs`).

## Modèle de machine learning

| Élément | Valeur |
|---|---|
| Type | Classification binaire : XGBoost (`XGBClassifier`), entraîné au projet 4 |
| Hyperparamètres | `learning_rate=0.05`, `max_depth=1`, `min_child_weight=5`, `n_estimators=600`, `subsample=0.8`, `random_state=42` |
| Entrées | 40 features : données RH, évaluations et sondage, déjà nettoyées et encodées au projet 4 |
| Sortie | Probabilité de départ, transformée en `partant` / `restant` |
| Fichier | `models/modele_xgb.joblib` (`xgboost` 3.4.1, `scikit-learn` 1.9.1) |

**Seuil de décision : 0,16.** Il a été choisi au projet 4 pour privilégier le **rappel** : rater un départ
coûte plus cher qu'un entretien RH de trop. À partir de 16 % de probabilité, l'employé est signalé.

**Performances mesurées au projet 4** (jeu de test, seuil de 0,16) :

| Indicateur | Valeur | Lecture |
|---|---|---|
| Rappel | 0,74 | 3 départs sur 4 sont détectés |
| Précision | 0,37 | Un peu plus d'une alerte sur 3 correspond à un vrai départ |
| F2 | 0,62 | Score qui donne plus de poids au rappel |
| Les 10 employés les plus à risque | 80 % de vrais partants | Intérêt de commencer les entretiens par les probabilités les plus élevées |

**Limites** : le modèle a été entraîné sur un historique de 1 470 employés ; une partie de ces employés a servi
à l'entraînement, ce qui rend leurs prédictions optimistes. La vraie performance est celle mesurée sur le jeu
de test du projet 4.

**Protocole de mise à jour du modèle** :
1. **Quand** : surveillance régulière (par exemple trimestrielle) avec la requête « prédictions comparées à la
   réalité » de `scripts/requetes_analyse.sql` ; réentraînement si le rappel se dégrade, si de nouvelles données
   du SIRH sont disponibles ou si l'organisation change (nouveaux postes, nouvelles politiques RH).
2. **Comment** : réentraîner dans le notebook, exporter le nouveau modèle avec joblib dans `models/`, mettre à
   jour les valeurs attendues des tests du modèle (`tests/unitaires/test_modele.py`).
3. **Livrer** : branche `feature/`, pull request (les tests de non-régression doivent passer), nouvelle version
   (`uv version --bump minor`), puis mise en production par le pipeline. Chaque prédiction enregistre la
   `version_api` : on sait quel modèle a produit chaque résultat.

## Authentification et sécurité

**Authentification par clé API** : les routes de prédiction exigent l'en-tête HTTP `X-API-Key`.
Sans clé, ou avec une clé invalide, l'API répond `401`. La route `/health` reste publique (supervision).
Dans Swagger (`/docs`), le bouton **Authorize** permet de saisir la clé.

**Gestion des accès** : la clé est partagée par les utilisateurs autorisés (équipe RH). C'est suffisant
pour un POC, mais cela ne permet pas de savoir qui a fait quel appel (voir [Pistes d'amélioration](#pistes-damélioration)).

**Gestion des secrets** :
- La clé n'est jamais écrite dans le code : elle est lue dans la variable d'environnement `API_KEY`.
- En local, elle est définie dans le fichier `.env`, exclu du dépôt par le `.gitignore`. Le fichier
  `.env.example` indique les variables à renseigner, sans leurs valeurs.
- En production, elle est stockée dans le secret `API_KEY` de l'environnement GitHub `production`,
  accessible uniquement aux workflows qui déploient depuis `main`. Le mot de passe de la base de test
  du déploiement est lui aussi un secret (`DB_PASSWORD`).
- Les tests utilisent une clé fictive, définie le temps du test.

Générer une clé :
```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Mots de passe et hachage** : l'API ne gère aucun compte utilisateur et ne stocke donc aucun mot de passe.
Le seul mot de passe est celui de la base de données, conservé dans le `.env` ou dans les secrets GitHub.
Avec des comptes individuels (voir [Pistes d'amélioration](#pistes-damélioration)), les mots de passe devraient être
stockés **hachés** avec un algorithme dédié (bcrypt ou Argon2), jamais en clair.

**Autres mesures** :
- Comparaison de la clé en temps constant (`secrets.compare_digest`), contre les attaques par mesure du temps de réponse.
- Si la clé n'est pas configurée sur le serveur, l'API refuse toutes les requêtes (`500`) plutôt que de s'ouvrir.
- Utilisateur PostgreSQL dédié (`projet5`), sans droits d'administration : principe du moindre privilège.
- Minimisation des données : l'API ne renvoie que la prédiction, jamais les données personnelles de l'employé.
- Branches `main` et `develop` protégées : toute modification passe par une pull request validée par les tests.

## Tests

42 tests Pytest, organisés en deux catégories :

| Dossier | Type | Contenu |
|---|---|---|
| `tests/unitaires/` | Tests unitaires | Règle de décision, modèle (fidélité au projet 4, reproductibilité, performances), normalisation des noms de colonnes, lecture en base, intégrité de la base (typage, contraintes, index, insertion, suppression) |
| `tests/fonctionnels/` | Tests fonctionnels | API de bout en bout : prédiction, authentification, codes d'erreur, enregistrement en base, documentation Swagger |

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
| SQLite (tests) n'applique pas les clés étrangères, contrairement à PostgreSQL | Activation explicite (`PRAGMA foreign_keys=ON`) dans `tests/conftest.py` | `test_prediction_pour_employe_inexistant_refusee`, `test_suppression_employe_avec_predictions_refusee` |
| Clé étrangère de `predictions` non indexée (PostgreSQL ne le fait pas automatiquement) | Index sur `employe_id` et `date_prediction` | `test_index_de_la_table_predictions` |

### Limites connues
- Le contrôle de performance porte sur le dataset complet, qui inclut les données d'entraînement : il sert
  de garde-fou contre un modèle dégradé, pas de mesure de performance (voir le projet 4 pour celle-ci).
- Les tests tournent sur SQLite. Le comportement avec PostgreSQL est vérifié par le test de fumée du
  déploiement, qui utilise une vraie base PostgreSQL.
- Pas de test de charge : non requis pour ce POC.
- Les tests s'exécutent sur un jeu de données fixe (reproductibilité). En production, avec une table alimentée
  régulièrement par le SIRH, il faudrait ajouter des contrôles de qualité à chaque chargement
  (volumétrie cohérente avec la source, doublons, valeurs manquantes, plages de valeurs).

## CI/CD et gestion des versions

### Organisation des branches (Gitflow léger)
| Branche | Rôle | Règle |
|---|---|---|
| `main` | Production | Ne reçoit que des fusions depuis `develop`, par pull request. Chaque fusion donne lieu à un tag de version. |
| `develop` | Intégration (développement), branche par défaut | Rassemble les fonctionnalités terminées, par pull request. |
| `feature/<nom-court>` | Une fonctionnalité | Créée depuis `develop`, puis fusionnée dans `develop` par pull request. |

Exemples de noms de branches : `feature/api`, `feature/base-de-donnees`, `feature/tests`.

`main` et `develop` sont protégées par une règle GitHub (ruleset) : push direct interdit, pull request
obligatoire, tests `Tests Pytest` obligatoirement verts avant fusion, suppression et réécriture de
l'historique interdites.

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
| `style` | Mise en forme du code, sans changement de comportement |

### Versions
Les versions suivent le format `vMAJEUR.MINEUR.CORRECTIF` (ex. `v1.0.0`). Le numéro est défini dans
`pyproject.toml` (`uv version --bump minor`) ; le tag correspondant est créé automatiquement sur `main`
à chaque mise en production.

| Version | Contenu |
|---|---|
| `v0.1.0` | Structure du dépôt, conventions, dépendances |
| `v0.2.0` | CI/CD : tests automatiques, déploiement avec validation |
| `v0.3.0` | API de prédiction protégée par clé, test de fumée |
| `v0.4.0` | Base PostgreSQL, traçabilité des prédictions |
| `v1.0.0` | Tests d'intégrité, index, documentation complète |

### Pipeline CI/CD

**Intégration continue** (`.github/workflows/ci.yml`) : à chaque pull request et à chaque fusion
sur `develop` ou `main`, GitHub Actions installe le projet sur une machine neuve et lance les tests
Pytest avec un rapport de couverture.

**Déploiement** (`.github/workflows/cd.yml`) : à chaque fusion sur `main`, le workflow :
1. relance les tests Pytest ;
2. attend une validation manuelle dans l'environnement GitHub `production` ;
3. vérifie que le numéro de version est nouveau ;
4. démarre une base PostgreSQL temporaire et y crée les tables avec `create_db.py` ;
5. réalise un **test de fumée** : il démarre l'API et vérifie que `/health` répond, qu'une prédiction
   fonctionne avec la clé de production et qu'une requête sans clé est refusée ;
6. construit le paquet de l'API et publie une release versionnée (tag `vX.Y.Z` créé automatiquement).

**Environnements et secrets** :
| Environnement | Où | Secrets |
|---|---|---|
| Développement | Poste local, branches `feature/*` et `develop` | Fichier `.env` (non versionné) |
| Test | GitHub Actions, à chaque pull request | Aucun secret nécessaire (clé fictive, base SQLite temporaire) |
| Production | Environnement GitHub `production`, branche `main` uniquement, validation manuelle | Secrets `API_KEY` et `DB_PASSWORD` (environnement GitHub) |

## Déploiement

### Déploiement actuel (local)
Depuis septembre 2026, le déploiement cloud n'est plus requis pour ce projet (Hugging Face Spaces est devenu
payant). L'API est donc déployée localement. Chaque mise en production publie une **release GitHub**
validée par le pipeline : déployer une version revient à installer cette version précise.

```bash
git clone https://github.com/youdontknowmu/Projet5.git
cd Projet5
git checkout v1.0.0                       # la version publiée à déployer
uv sync --frozen                          # dépendances exactes du uv.lock
cp .env.example .env                      # puis renseigner API_KEY et DATABASE_URL
uv run python scripts/create_db.py        # première installation uniquement
uv run uvicorn projet5.api:app --host 0.0.0.0 --port 8000
```

La release contient aussi le paquet Python de l'API (`.whl`). Il n'embarque que le code : le modèle et les
données sont fournis par le dépôt, d'où l'installation à partir du tag.

### Cible de déploiement finale (cloud)
Dans un contexte de production réel, le même pipeline déploierait l'API chez un hébergeur cloud.
Seules les dernières étapes changent :

| Étape du pipeline | Aujourd'hui (POC) | Cible cloud |
|---|---|---|
| Tests, validation manuelle, contrôle de version | Identique | Identique |
| Empaquetage | Paquet Python + release GitHub | **Image Docker** contenant l'API, le modèle et les dépendances, publiée sur un registre (GitHub Container Registry) |
| Base de données | PostgreSQL local | **PostgreSQL managé** (sauvegardes et mises à jour gérées par l'hébergeur) |
| Mise en service | Installation à partir du tag | Le pipeline met à jour le service (par exemple Azure Container Apps, Google Cloud Run ou Render) avec la nouvelle image |
| Secrets | `.env` et secrets GitHub | Gestionnaire de secrets de l'hébergeur |
| Test de fumée | Sur une API temporaire dans GitHub Actions | Sur l'URL réelle, juste après la mise en service |
| Retour arrière | Réinstaller le tag précédent | Redéployer l'image de la version précédente |

L'API serait alors exposée en **HTTPS** uniquement. Pour un usage strictement interne (données RH),
un hébergement sur les serveurs de l'entreprise, derrière un reverse proxy, serait une alternative.

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

## Pistes d'amélioration

| Domaine | Amélioration |
|---|---|
| Accès | **Une clé par utilisateur** (ou des comptes avec jetons JWT et mots de passe hachés), pour savoir qui a interrogé l'API et tracer chaque appel |
| Traçabilité | Enregistrer l'utilisateur appelant dans la table `predictions` (piste d'audit) |
| Confidentialité | Passer l'identifiant dans le corps d'une requête `POST` plutôt que dans l'URL, pour qu'il n'apparaisse pas dans les journaux et l'historique du navigateur |
| RGPD | Durée de conservation et purge des prédictions, analyse d'impact (profilage de salariés), information des employés |
| Fonctionnalités | Route « employés les plus à risque » pour les RH ; prédiction sur un lot d'employés |
| Déploiement | Image Docker et déploiement cloud (voir [Cible de déploiement finale](#cible-de-déploiement-finale-cloud)) |
| Supervision | Suivi automatique de la dérive du modèle, alertes, journaux centralisés |
| Données | Contrôles de qualité à chaque chargement depuis le SIRH |

## Auteur
Antoine Driot