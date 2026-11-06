"""Règle de décision : transforme la probabilité de départ calculée par le modèle en prédiction lisible."""

# Seuil de décision choisi au projet 4 (section 7.3).
# À partir de 16 % de probabilité de départ, l'employé est considéré comme "partant".
# Ce seuil bas privilégie le rappel : mieux vaut un entretien RH de trop qu'un départ non détecté.
SEUIL_DECISION = 0.16


def interpreter_probabilite(probabilite: float, seuil: float = SEUIL_DECISION) -> str:
    """Renvoie "partant" si la probabilité atteint le seuil, "restant" sinon."""
    # Une probabilité est toujours comprise entre 0 et 1 : sinon, il y a une erreur en amont
    if not 0 <= probabilite <= 1:
        raise ValueError(f"Probabilité invalide : {probabilite} (attendu entre 0 et 1)")

    if probabilite >= seuil:
        return "partant"
    return "restant"