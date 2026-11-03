# API de prédiction du risque de démission – POC Futurisys

Projet 5 de la formation AI Engineer (OpenClassrooms).

## Présentation
Ce projet met à disposition, sous forme d'API locale, le modèle de classification
développé au projet 4 (prédiction du risque de démission des employés de TechNova Partners).
L'API reçoit l'identifiant d'un employé, récupère ses données dans une base PostgreSQL
et renvoie la prédiction « partant » ou « restant », avec la probabilité de départ.

## Architecture
*À compléter*

## Prérequis
*À compléter*

## Installation
*À compléter*

## Base de données
*À compléter*

## Lancement de l'API
*À compléter*

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
*À compléter*

## Besoins analytiques
*À compléter*

## Auteur
Antoine Driot