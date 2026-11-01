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

## TP2 — Versionner le code avec Git, les données avec DVC

### Réponses aux questions

#### Q1. Pendant que vous travailliez sur la branche, main contenait-elle la règle 6 ? À quelle commande est-elle apparue sur main ? Pourquoi est-ce utile si le rapport tourne chaque nuit depuis main ?
Non, la branche `main` ne contenait pas la règle 6 pendant le développement sur `feature/country-rule`. Elle n'est apparue sur `main` qu'après la commande `git merge --no-ff feature/country-rule`. C'est une protection essentielle en production : si le pipeline tourne chaque nuit depuis `main`, il est garanti de tourner sur du code stable et validé, sans être perturbé par des développements en cours d'expérimentation.

#### Q2. Dans une vraie équipe, la fusion passerait par une pull request sur GitHub. Qu’apporterait une pull request qu’un git merge local n’apporte pas ?
Une Pull Request (PR) apporte :
1. La revue de code systématique par les pairs (code review).
2. L'exécution automatique des tests sur des runners isolés via la CI (GitHub Actions) avant d'autoriser la fusion.
3. Une traçabilité complète des discussions, approbations et décisions techniques directement liées aux commits.

#### Q3. Recopiez la ligne md5 de `data/raw.dvc`. Qu’identifie-t-elle, et que lui arriverait-il si vous changiez un seul caractère dans un des CSV ?
- Ligne MD5 initiale : `md5: 94e9693bd7aa741446eb54aae611e617.dir`.
- Elle identifie l'empreinte cryptographique globale du contenu du répertoire `data/raw`.
- Si un seul caractère venait à changer dans un des fichiers CSV, l'empreinte MD5 changerait complètement (effet avalanche du hachage cryptographique), et DVC détecterait immédiatement une modification des données.

#### Q4. Les CSV sont toujours sur votre disque, mais Git ne les voit plus. Quel fichier fait que Git les ignore ?
C'est le fichier [`data/.gitignore`](file:///c:/Users/berri/Desktop/dataops/dataops-lab1/data/.gitignore) généré automatiquement par la commande `dvc add data/raw`, qui contient `/raw`.

#### Q5. Les fichiers de `dvc-storage` ne s’appellent pas `orders_day1.csv`. Comment sont-ils nommés, et pourquoi est-ce une bonne idée quand il existe plusieurs versions du même fichier ?
Ils sont stockés et nommés selon leur empreinte de hachage MD5 (ex: `aa/8c0d16...`), selon le principe du *Content-Addressable Storage* (CAS).
C'est une excellente pratique car cela permet à plusieurs versions d'un même fichier de coexister sur le stockage sans aucun risque de collision de noms, tout en assurant une déduplication automatique des fichiers identiques.

#### Q6. `git diff data/raw.dvc` n’a montré que deux lignes modifiées, alors que des données ont été ajoutées. Pourquoi est-ce suffisant pour Git ? Pourquoi faut-il quand même commiter ?
- C'est suffisant pour Git car Git ne suit que le fichier pointeur léger `data/raw.dvc`, qui référence le nouveau hash MD5 des données.
- Il est indispensable de commiter ce fichier pointeur dans Git afin d'associer de façon immuable l'état exact du code source à la version exacte des données dans l'historique Git.

#### Q7. Entre data-v1 et data-v2, le code a-t-il changé ? Écrivez les deux totaux.
Non, le code est resté rigoureusement identique.
- Total avec `data-v1` (30 commandes) : **7 655,90 €**
- Total avec `data-v2` (35 commandes, 5 commandes tardives ajoutées) : **8 835,40 €**

#### Q8. Avec vos mots : qu’a changé `git checkout data-v1 -- data/raw.dvc`, et qu’a changé `dvc checkout` ?
- `git checkout data-v1 -- data/raw.dvc` a restauré dans Git la version du fichier pointeur correspondant au tag `data-v1`.
- `dvc checkout` a lu cette empreinte dans le pointeur et a remplacé sur le disque les fichiers de `data/raw/` par leur version v1 extraite du cache DVC.

#### Q9. Que se passe-t-il si vous oubliez `dvc checkout` ? Pourquoi est-ce dangereux pour un rapport ?
Si l'on omet `dvc checkout`, le pointeur Git pointe vers `data-v1`, mais les données réelles sur disque restent celles de `data-v2`. Le pipeline exécuterait donc les données récentes tout en croyant reproduire le passé, générant un rapport incohérent avec le commit et ruinant l'auditabilité.

#### Q10. Qu’est-ce que `git clone` a donné au collègue, et qu’est-ce que `dvc pull` lui a donné ?
- `git clone` lui a fourni le code source complet, l'arborescence, les tests, les workflows CI et les fichiers pointeurs `.dvc`.
- `dvc pull` a téléchargé depuis le remote (`../dvc-storage`) les fichiers de données brutes volumineux référencés par les pointeurs et les a reconstitués dans `data/raw/`.

#### Q11. Imaginez que vous ayez oublié `dvc push` à l’étape 4. Qu’obtiendrait le collègue avec `dvc pull`, et quel total ?
Sans `dvc push`, le remote `dvc-storage` ne contiendrait pas la version `data-v2`. Le collègue obtiendrait une erreur lors du `dvc pull` signalant des objets manquants sur le remote et ne pourrait pas exécuter le pipeline sur les données v2 (impossible d'obtenir les 8 835,40 €).

### Sortie de `git log --oneline --graph --decorate`
```
* 7e3671c (HEAD -> main) Describe the report as a DVC stage
* 95a8f79 (tag: data-v2) Data v2: late orders for 2026-10-05
* 454c740 Add the DVC remote
* 840c0e0 (tag: data-v1) Track raw data with DVC
*   af9ef9a Merge the country rule
|\  
| * 010fdc6 (feature/country-rule) Reject orders from countries the shop does not sell to
|/  
* caa0628 Finish TP1, add DVC to requirements
* 4cd79aa Add pipeline, data checks and unit tests
* 3c8775a Empty project with requirements
```
