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

## TP3 — Du pipeline Python à l’ELT moderne avec DuckDB et dbt

### Réponses aux questions

#### Q1. Pourquoi charger toutes les colonnes en texte, au lieu de laisser DuckDB deviner les types ? Pensez à ce qui arriverait le jour où une quantité vaut deux.
Charger toutes les colonnes en `VARCHAR` (`all_varchar = true`) découple strictement l'ingestion (Load) de la validation/transformation (Transform). Si une colonne de quantité contenait par exemple la valeur textuelle `"deux"`, ou si une date était mal formatée (`2026-13-45`), DuckDB planterait brutalement lors de la détection automatique de type à l'ingestion. En chargeant tout en texte brut, le fichier est toujours ingéré avec succès, préservant ainsi l'intégralité des données brutes pour audit et permettant d'appliquer des conversions contrôlées (`try_cast`, `try_strptime`) en SQL.

#### Q2. Le total naïf en SQL est aussi faux que celui de l’ancien script Python. Qu’est-ce que cela vous apprend sur le langage, et sur ce qui rend un pipeline fiable ?
La fiabilité d'un pipeline de données ne dépend pas du langage de programmation (Python, SQL ou autre). Une même logique dépourvue de contrôles de qualité produira rigoureusement les mêmes erreurs quel que soit le moteur d'exécution. Ce qui rend un pipeline fiable, c'est l'architecture de contrôle : validation de schéma, règles d'intégrité explicites, détection des anomalies, tables de quarantaine et arrêt automatique de la chaîne de publication en cas d'erreur.

#### Q3. Si demain une règle de nettoyage est fausse, quel avantage y a-t-il à avoir gardé le brut dans l’entrepôt ?
En conservant les données brutes immutables dans l'entrepôt (`raw.orders`), il suffit de corriger le modèle SQL et de relancer `dbt run` pour recalculer immédiatement et rétroactivement tous les modèles et rapports en aval. Il n'est pas nécessaire de solliciter à nouveau les systèmes sources ou de re-extraire les fichiers.

#### Q4. En entreprise, profiles.yml contiendrait l’adresse et le mot de passe de Snowflake ou de BigQuery. Que faudrait-il changer dans ce fichier, et où mettre le mot de passe ?
Il ne faut jamais inscrire de secrets en clair dans `profiles.yml` car ce fichier est versionné dans Git. On utilise des variables d'environnement Jinja :
```yaml
password: "{{ env_var('DBT_PASSWORD') }}"
```
Le mot de passe réel est stocké dans les variables d'environnement de la machine ou injecté via les secrets de la plateforme de CI/CD (ex. GitHub Secrets, AWS Secrets Manager, HashiCorp Vault).

#### Q5. La commande 1013 a toujours sa ligne dans stg_orders, avec une date vide. Pourquoi ne pas la supprimer dès le staging ?
Le modèle de staging a pour unique rôle de normaliser la forme (types, casse, trim), sans altérer le fond ni prendre de décisions métier sur le filtrage des lignes. Supprimer des lignes dès le staging masquerait des données et rendrait impossible la construction d'une table de quarantaine ou l'analyse des rejets en aval.

#### Q6. stg_orders est une vue, pas une table. Que se passe-t-il quand vous la lisez, et pourquoi est-ce acceptable pour une couche de staging ?
Lorsqu'on interroge une vue, DuckDB exécute la requête sous-jacente à la volée. C'est parfaitement acceptable (et recommandé) pour une couche de staging car la transformation est légère (simples casts et renommages), évitant ainsi d'occuper de l'espace disque inutilement tout en garantissant des données toujours à jour par rapport à la source brute.

#### Q7. Ouvrez target/compiled/shop/models/intermediate/int_orders_checked.sql. Par quoi dbt a-t-il remplacé `{{ ref('stg_orders') }}` ?
dbt a remplacé le Jinja `{{ ref('stg_orders') }}` par le nom complet et qualifié de la relation dans DuckDB : `"warehouse"."main"."stg_orders"` (ou `stg_orders`).

#### Q8. Dans le TP1, la règle 5 utilisait `df.duplicated("order_id", keep="first")`. Expliquez ce que fait `row_number() over (partition by order_id order by _row_number)`, et pourquoi on a eu besoin de `_row_number`.
- `row_number() over (partition by order_id order by _row_number)` partitionne les données par `order_id` et attribue un numéro séquentiel (1, 2, 3...) trié selon `_row_number`. Les lignes ayant un numéro > 1 sont les doublons ultérieurs.
- En SQL relationnel, les tables représentent des ensembles mathématiques non ordonnés. La colonne technique `_row_number` générée dès l'ingestion est indispensable pour mémoriser l'ordre physique initial des lignes du fichier CSV et déterminer sans ambiguïté quelle commande est arrivée en premier.

#### Q9. Un analyste veut ajouter le chiffre d’affaires par produit. Quel fichier crée-t-il, dans quel dossier, et doit-il toucher à du Python ?
L'analyste crée simplement le fichier [`models/marts/revenue_by_product.sql`](file:///c:/Users/berri/Desktop/dataops/dataops-lab1/models/marts/revenue_by_product.sql) en effectuant une requête SQL agrégeant les ventes depuis `orders_clean`. Il n'a besoin de toucher à **aucune ligne de Python**.

#### Q10. Quand vous avez cassé la règle 5, quel test a échoué ? Quels modèles et quels tests ont été SKIP, et pourquoi est-ce exactement ce que l’on veut pour le rapport du directeur ?
- Le test de données `unique_orders_clean_order_id` a échoué.
- Tous les modèles et tests dépendants en aval (`revenue_by_country`, `unique_revenue_by_country_country`) ont été automatiquement passés en **SKIP**.
- C'est le principe du « cordon Andon » (arrêt de chaîne) : cela empêche formellement de publier un rapport de chiffre d'affaires corrompu au directeur général lorsqu'une anomalie de données est détectée.

#### Q11. Tableau de correspondance Python vs dbt
| Contrôle du TP1 (Python) | Son équivalent dbt |
| :--- | :--- |
| `check_schema` | Schéma déclaré dans `sources.yml`, types stricts dans `stg_orders.sql`, et tests `not_null` |
| Règles 1 à 6 dans `clean_orders` | Expression `CASE WHEN ... END AS reject_reason` dans `int_orders_checked.sql` |
| `check_reject_rate` | Test singulier `data_tests/assert_reject_rate_below_20_percent.sql` |
| `rejected_orders.csv` | Table de quarantaine matérialisée `models/marts/orders_rejected.sql` |
| `PIPELINE STOPPED, rien n’est publié` | Échec de test dans `dbt build`, bloquant l'exécution et mettant les marts en `SKIP` |

#### Q12. Le test unitaire n’a pas eu besoin de load_raw.py ni d’aucun fichier CSV. D’où venaient ses données ? Pourquoi est-ce important pour un test qui tournera dans la CI à la séance 4 ?
Les données de test proviennent directement des lignes déclarées en YAML sous `given.rows` dans [`int_orders_checked.yml`](file:///c:/Users/berri/Desktop/dataops/dataops-lab1/models/intermediate/int_orders_checked.yml). C'est essentiel pour la CI car les tests unitaires doivent s'exécuter de façon instantanée, déterministe et autonome, sans dépendre de fichiers CSV externes ni d'accès à des bases distantes.

#### Q13. Demain, la colonne country arrive vide dans la source. Avec le graphe, citez tous les modèles touchés. Combien de temps vous aurait pris la même réponse sans le graphe, dans un dossier de 200 scripts SQL ?
- Modèles impactés : `raw.orders` → `stg_orders` → `int_orders_checked` → `orders_clean` et `orders_rejected` → `revenue_by_country` et `revenue_by_product`.
- Sans graphe de lignage automatique, il aurait fallu faire des recherches textuelles manuelles (`grep`, parcours des tables) dans les 200 scripts, une opération fastidieuse pouvant prendre plusieurs heures avec un risque élevé d'erreur ou d'omission.

#### Q14. Tableau comparatif Jour 2 et Jour 3
| Cas de figure | Pipeline Python (TP1) | Pipeline dbt (TP3) |
| :--- | :--- | :--- |
| **Jour 2 : quel contrôle arrête la chaîne ?** | `check_reject_rate` (taux de rejet 100% > 20%) | Test singulier `assert_reject_rate_below_20_percent` en FAIL, marts en SKIP |
| **Jour 3 : quel message d’erreur ?** | `DataQualityError: Missing columns: ['unit_price']` | `Binder Error: Table "src" does not have a column named "unit_price"` dans `stg_orders` |
| **Le rapport de la veille est-il conservé ?** | Oui, le fichier `revenue_by_country.csv` est intact | Oui, la table `revenue_by_country` n'est pas modifiée (total préservé à 8 835,40 €) |
| **Code de sortie** | `1` | `1` |

#### Q15. Au jour 2, orders_rejected a aussi été SKIP. Le fichier de quarantaine contient donc encore les rejets du jour 1. Est-ce un problème ? Proposez une façon de garder la quarantaine du jour 2 tout en bloquant le rapport.
Oui, c'est une limite pour l'investigation car les équipes support ne peuvent pas inspecter directement dans la table de quarantaine les motifs précis des rejets du jour 2.
Pour y remédier, on peut :
1. Positionner le test du taux de rejet uniquement en amont de `revenue_by_country` et `orders_clean`, tout en laissant `orders_rejected` se matérialiser.
2. Ou scinder l'exécution : construire systématiquement la table de quarantaine (`dbt run --select orders_rejected`), puis exécuter les tests d'arrêt de chaîne avant la publication du rapport final.

---

### Dernière ligne d'exécution de `dbt build` sur le Jour 1 :
```
Done. PASS=14 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=14
```
*(Et PASS=16 avec le modèle bonus `revenue_by_product`)*
