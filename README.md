# DataOps — De l'ETL Artisanal à l'ELT Industriel

Ce dépôt contient l'ensemble des travaux pratiques (TP 1, TP 2 et TP 3) du module d'ingénierie des données et DataOps.

---

## 📌 Architecture du Projet

```text
dataops-lab1/
├── pipeline/                   # Modules du pipeline Python (TP1 & TP2)
│   ├── extract.py              # Ingestion des fichiers CSV
│   ├── validate.py             # Validation de schéma & taux de rejet
│   ├── transform.py            # Règles de nettoyage (1 à 6) & métriques
│   └── load.py                 # Sauvegarde des résultats
├── data/
│   ├── raw.dvc                 # Pointeur DVC vers les données brutes
│   └── .gitignore              # Exclusion des données brutes de Git
├── models/                     # Modèles dbt (TP3)
│   ├── sources.yml             # Déclaration de la table brute DuckDB
│   ├── staging/stg_orders.sql  # Typage strict & normalisation
│   ├── intermediate/           # int_orders_checked.sql (les 6 règles en SQL)
│   └── marts/                  # orders_clean, orders_rejected, revenue_by_country
├── data_tests/                 # Tests singuliers dbt (quantité, taux de rejet)
├── tests/                      # Tests unitaires pytest (TP1 & TP2)
├── run_pipeline.py             # Script d'exécution du pipeline Python
├── load_raw.py                 # Extract + Load brut vers DuckDB
├── query.py                    # Utilitaire d'interrogation SQL
├── dbt_project.yml             # Configuration du projet dbt
├── profiles.yml                # Configuration de l'entrepôt DuckDB
├── REPORT.md                   # Compte-rendu complet avec réponses Q1 à Q15
└── Rapport_DataOps_TP1_TP2_TP3.pdf # Rapport de synthèse PDF (5 pages)
```

---

## 🚀 Guide d'Exécution Rapide

### 1. Activer l'environnement
```cmd
.venv\Scripts\activate.bat
```

### 2. Lancer les tests unitaires Python (TP1 / TP2)
```cmd
python -m pytest
```

### 3. Exécuter le pipeline Python
```cmd
python run_pipeline.py data/raw/orders_day1.csv
```

### 4. Construire et tester le pipeline ELT dbt (TP3)
```cmd
dbt build
```

### 5. Consulter les rapports dans DuckDB
```cmd
python query.py "select * from revenue_by_country"
```

---

## 📄 Documentation & Rapports
* Compte-rendu exhaustif : [`REPORT.md`](REPORT.md)
* Rapport PDF officiel : [`Rapport_DataOps_TP1_TP2_TP3.pdf`](Rapport_DataOps_TP1_TP2_TP3.pdf)
