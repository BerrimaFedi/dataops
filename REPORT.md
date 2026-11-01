# Rapport DataOps — Compte-Rendu des Travaux Pratiques

Étudiants : Equipe DataOps (TP1, TP2, TP3)

---

## TP1 — D’un script fragile à un pipeline testé

### Réponses aux questions

#### Q1. Pourquoi écrit-on les bibliothèques dans requirements.txt au lieu de taper simplement `pip install pandas` ?
Écrire les dépendances dans `requirements.txt` permet de garantir la reproductibilité stricte de l'environnement d'exécution. Cela permet à n'importe quel collaborateur ou serveur d'intégration continue (CI) de réinstaller exactement les mêmes bibliothèques et versions minimales requises via `pip install -r requirements.txt`.

#### Q2. La boutique vend dans cinq pays. Combien de lignes le rapport affiche-t-il ? Pourquoi ?
Le rapport naïf affiche 8 lignes au lieu des 5 pays attendus. Cela provient de variations de casse (`MOROCCO`, `Morocco`, `tunisia`, `Tunisia`) et de la présence d'espaces avant le nom (` Tunisia`). Sans nettoyage préalable, l'opération `groupby("country")` traite chacune de ces variantes comme une catégorie distincte.

#### Q3. Problèmes de qualité identifiés dans `orders_day1.csv`
| Dimension de qualité | Order ID | Problème constaté |
| :--- | :--- | :--- |
| **Complétude** | 1008 | Le `customer_id` est vide (manquant). |
| **Unicité** | 1010 | La commande 1010 apparaît en double avec les mêmes données. |
| **Validité** | 1004 | Quantité négative (`quantity = -2`). |
| **Validité** | 1013 | Date invalide (`2026-13-45`). |
| **Validité / Exactitude**| 1019 | Prix unitaire invraisemblable (`unit_price = 4500.0` pour un clavier). |
| **Cohérence** | 1006, 1016, 1023 | Incohérences de saisie du pays (`tunisia`, `MOROCCO`, ` Tunisia`). |

#### Q4. Le total est-il trop haut ou trop bas ? Pouvez-vous le savoir sans le recalculer à la main ?
Il est impossible de le déterminer sans recalcul : le fichier contient à la fois des anomalies tirant le chiffre d'affaires vers le bas (quantité négative : `-39.80 €`) et des anomalies tirant le chiffre très fortement vers le haut (doublon : `+449.00 €`, et prix unitaire aberrant : `+4500.00 €`). Ces erreurs se compensent partiellement de manière imprévisible.

#### Q5. Qu’a-t-on gagné en découpant le script en fonctions ? Donnez deux avantages.
1. **Séparation des responsabilités (SoC) et maintenabilité** : Chaque étape (extraire, vérifier, nettoyer, calculer, charger) a une fonction dédiée et indépendante, ce qui facilite la lecture et l'évolution du pipeline.
2. **Testabilité unitaire** : Chaque fonction peut être isolée et testée individuellement avec pytest sur de petits jeux de données factices, sans avoir besoin d'exécuter l'ensemble du pipeline.

#### Q6. L’ancien script disait 12771.10. Quel est le bon total ? De combien l’ancien script se trompait-il, en pourcentage ?
- Le bon total après nettoyage est de **7 655,40 €** (ou **7 655,90 €** avec les 5 règles du TP1).
- Écart : `12 771,10 - 7 655,90 = +5 115,20 €`.
- L'ancien script surestimait le chiffre d'affaires de `5 115,20 / 7 655,90 ≈ +66,8 %`.

#### Q7. Quelle commande, à elle seule, a causé l’essentiel de l’erreur ? Quelle règle l’a attrapée ?
La commande **1019** (un clavier facturé 4 500 € au lieu d'une valeur normale ~45 €), représentant à elle seule 4 500 € de chiffre d'affaires erroné. Elle a été interceptée par la **Règle 4** (`invalid_unit_price`).

#### Q8. Pourquoi enregistre-t-on les lignes rejetées dans un fichier au lieu de simplement les supprimer ?
Pour assurer l'observabilité et l'auditabilité : les lignes rejetées doivent pouvoir être analysées par les équipes métier ou techniques pour identifier la cause racine des bugs (problème d'UI, bogue d'export) et permettre un retraitement ultérieur des commandes légitimes sans perte de données.

#### Q9. Que s’est-il passé quand vous avez cassé la règle 3 ? Quel test a échoué ?
En autorisant `quantity > -5` au lieu de `quantity > 0`, le test unitaire `test_negative_quantity_is_rejected` a échoué immédiatement car la commande à quantité négative n'a pas été rejetée.

#### Q10. En une phrase chacun : que vérifie un test unitaire, et que vérifie un contrôle de données ?
- **Test unitaire (test de code)** : Il vérifie que la logique algorithmique du code fonctionne comme prévu sur des cas tests statiques synthétiques.
- **Contrôle de données (test de données)** : Il vérifie en production que le flux de données entrant respecte le schéma attendu et les critères de qualité métier.

#### Q11. Tableau comparatif : Ancien script vs Pipeline de données
| Cas de test | Ancien script (naïf) | Notre pipeline testé |
| :--- | :--- | :--- |
| **Jour 2 : message d’erreur ?** | Aucun message, exécution silencieuse | `PIPELINE STOPPED: Reject rate 100% is above the limit of 20% (6 of 6 rows)` |
| **Jour 2 : total affiché** | `270 200.0` (aberrant, prix en centimes) | Aucun (rien n'est publié, rapport J1 préservé) |
| **Jour 3 : message d’erreur ?** | `KeyError: 'unit_price'` (crash non géré) | `PIPELINE STOPPED: Missing columns: ['unit_price']` (arrêt contrôlé) |

#### Q12. Qu’est-ce qui a changé dans le système source au jour 2 ? Au jour 3 ?
- **Jour 2** : Le système source a envoyé les prix en centimes plutôt qu'en euros (valeurs multipliées par 100), violant la règle de plausibilité des prix.
- **Jour 3** : Le schéma a été modifié en amont sans préavis : la colonne `unit_price` a été renommée en `price`.

#### Q13. Sans pipeline, quel jour est le plus dangereux pour l’entreprise, le jour 2 ou le jour 3 ? Pourquoi ?
Le **jour 2** est beaucoup plus dangereux. Le script naïf ne plante pas et publie un chiffre d'affaires erroné de 270 200 € au lieu de 2 702 €. Les décideurs risquent d'agir sur des données fausses sans le savoir (erreur silencieuse). Au jour 3, le script plante brutalement (`KeyError`), ce qui alerte immédiatement sur un problème.

#### Q14. Le code de sortie vaut 1 quand le pipeline s’arrête. Qui ou quoi peut utiliser ce nombre ?
Le code de retour (`exit code = 1`) est utilisé par les orchestrateurs de données (Airflow, Dagster, Prefect), les planificateurs (cron), et les outils d'intégration continue (GitHub Actions) pour stopper la chaîne de traitement, bloquer les publications aval et déclencher des alertes immédiates (monitoring).

---
