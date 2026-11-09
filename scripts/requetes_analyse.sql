-- ============================================================
-- Requêtes d'analyse de l'activité de l'API (PostgreSQL)
-- À exécuter dans DBeaver (connexion projet5) ou avec psql :
--   psql -h localhost -U projet5 -d projet5 -f scripts/requetes_analyse.sql
-- ============================================================


-- 1) Activité globale : nombre de prédictions et répartition partant / restant
SELECT prediction,
       COUNT(*)                                            AS nombre,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS pourcentage
FROM predictions
GROUP BY prediction
ORDER BY nombre DESC;


-- 2) Activité par jour et par version de l'API (suivi de l'usage et des mises en production)
SELECT DATE(date_prediction) AS jour,
       version_api,
       COUNT(*)              AS nombre_predictions
FROM predictions
GROUP BY jour, version_api
ORDER BY jour, version_api;


-- 3) Employés les plus à risque : dernière prédiction connue pour chaque employé
--    (DISTINCT ON : spécifique à PostgreSQL, garde une seule ligne par employé, la plus récente)
SELECT *
FROM (
    SELECT DISTINCT ON (e.id_employee)
           e.id_employee,
           p.probabilite_depart,
           p.prediction,
           p.date_prediction
    FROM predictions p
    JOIN employes e ON e.id = p.employe_id
    ORDER BY e.id_employee, p.date_prediction DESC
) AS dernieres_predictions
ORDER BY probabilite_depart DESC
LIMIT 10;


-- 4) Prédictions comparées à la réalité connue (dataset historique du projet 4)
--    Permet de suivre la qualité du modèle sur les employés déjà interrogés
SELECT p.prediction,
       CASE e.a_quitte_l_entreprise WHEN 1 THEN 'parti' ELSE 'resté' END AS realite,
       COUNT(*) AS nombre
FROM predictions p
JOIN employes e ON e.id = p.employe_id
GROUP BY p.prediction, realite
ORDER BY p.prediction, realite;


-- 5) Risque moyen selon les heures supplémentaires (premier facteur de départ identifié au projet 4)
SELECT CASE e.heures_supplementaires WHEN 1 THEN 'avec heures sup.' ELSE 'sans heures sup.' END AS heures_sup,
       COUNT(*)                                AS nombre_predictions,
       ROUND(AVG(p.probabilite_depart)::numeric, 3) AS probabilite_moyenne
FROM predictions p
JOIN employes e ON e.id = p.employe_id
GROUP BY heures_sup
ORDER BY probabilite_moyenne DESC;