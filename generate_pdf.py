import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(40, 842 - 32, "Rapport DataOps — Du Script Fragile à l'ELT Moderne (TP1, TP2, TP3)")
            self.drawRightString(595 - 40, 842 - 32, "Octobre 2026")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(40, 842 - 36, 595 - 40, 842 - 36)
        
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 36, 595 - 40, 36)
        self.drawString(40, 24, "DataOps Engineering — Pipeline & ELT Qualifié")
        self.drawRightString(595 - 40, 24, f"Page {self._pageNumber} / {page_count}")
        self.restoreState()

def build_pdf(filename="Rapport_DataOps_TP1_TP2_TP3.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_accent = colors.HexColor("#2563EB")     # Blue 600
    c_accent_dark = colors.HexColor("#1D4ED8")# Blue 700
    c_success = colors.HexColor("#059669")    # Emerald 600
    c_warning = colors.HexColor("#D97706")    # Amber 600
    c_border = colors.HexColor("#E2E8F0")     # Slate 200
    c_bg_light = colors.HexColor("#F8FAFC")   # Slate 50
    c_code_bg = colors.HexColor("#1E293B")    # Slate 800

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_accent_dark,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    question_style = ParagraphStyle(
        'Question_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#F1F5F9"),
        spaceBefore=3,
        spaceAfter=5
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1E293B")
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#0F172A")
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )

    story = []

    # ==========================
    # EN-TÊTE / COUVERTURE
    # ==========================
    story.append(Paragraph("Rapport DataOps d'Ingénierie des Données", title_style))
    story.append(Paragraph("Du Script Fragile à l'ELT Moderne avec DuckDB, dbt, Git et DVC — TP 1, TP 2 & TP 3", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_accent, spaceBefore=0, spaceAfter=12))

    # Bloc Métadonnées & Statut
    meta_data = [
        [
            Paragraph("<b>Auteurs :</b> Équipe DataOps", body_style),
            Paragraph("<b>Environnement :</b> Python 3.13.17 | DuckDB 2.0 | dbt 1.12", body_style),
            Paragraph("<b>Statut global :</b> <font color='#059669'><b>100% VALIDÉ</b></font>", body_style)
        ],
        [
            Paragraph("<b>Date :</b> Novembre 2026", body_style),
            Paragraph("<b>Dépôt :</b> dataops-lab1 (Git + DVC)", body_style),
            Paragraph("<b>Certification :</b> 16/16 tests dbt | 6/6 tests pytest", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[170, 205, 140])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # ==========================
    # RÉSUMÉ EXÉCUTIF
    # ==========================
    story.append(Paragraph("1. Synthèse Exécutive et Tableau Récapitulatif", h1_style))
    story.append(Paragraph(
        "Ce projet documente la transformation progressive et industrielle d'un processus de traitement de données pour une boutique en ligne. "
        "Parti d'un script Python naïf présentant des failles critiques (erreurs silencieuses, surestimation de +66.8% du CA), le projet a évolué vers "
        "un pipeline modulaire testé (TP1), versionné au niveau code et données avec Git et DVC (TP2), puis intégralement réarchitecturé selon le paradigme "
        "ELT moderne avec un entrepôt analytique DuckDB et dbt (TP3).",
        body_style
    ))

    summary_rows = [
        [Paragraph("Travail Pratique", table_header), Paragraph("Objectif DataOps", table_header), Paragraph("Outils Clés", table_header), Paragraph("Indicateur / Résultat", table_header)],
        [
            Paragraph("<b>TP 1</b> — Script fragile vers pipeline testé", table_cell_bold),
            Paragraph("Structuration en fonctions, contrôles de schéma, arrêt de chaîne, quarantaine.", table_cell),
            Paragraph("Python, Pandas, Pytest", table_cell),
            Paragraph("<font color='#059669'><b>TOTAL: 7 655,90 €</b></font><br/>5 tests unitaires passés<br/>J2/J3 refusés (arrêt net)", table_cell)
        ],
        [
            Paragraph("<b>TP 2</b> — Versionner code (Git) & données (DVC)", table_cell_bold),
            Paragraph("Branches de fonctionnalités, Content-Addressable Storage, tags de données, reproductibilité.", table_cell),
            Paragraph("Git, DVC, Remote Storage", table_cell),
            Paragraph("<font color='#059669'><b>TOTAL: 8 835,40 €</b></font><br/>Tags data-v1 & data-v2<br/>Clone collègue validé", table_cell)
        ],
        [
            Paragraph("<b>TP 3</b> — Pipeline ELT moderne (DuckDB + dbt)", table_cell_bold),
            Paragraph("Chargement brut tel quel, transformation SQL en couches, tests singuliers, tests unitaires dbt.", table_cell),
            Paragraph("DuckDB, dbt Core, Jinja, SQL", table_cell),
            Paragraph("<font color='#059669'><b>PASS=14 (PASS=16)</b></font><br/>Total exact: <b>8 835,40 €</b><br/>Lignage automatique généré", table_cell)
        ]
    ]
    summary_table = Table(summary_rows, colWidths=[120, 155, 110, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # ==========================
    # TP 1 : PIPELINE TESTÉ
    # ==========================
    story.append(Paragraph("2. TP 1 — D'un Script Fragile à un Pipeline Testé", h1_style))
    story.append(Paragraph(
        "<b>Problématique initiale :</b> Le script naïf (<code>naive_report.py</code>) calcule <code>quantity * unit_price</code> sans aucun contrôle. "
        "Il affichait un chiffre d'affaires erroné de <b>12 771,10 €</b> au lieu des <b>7 655,90 €</b> réels (surestimation de +66.8%) en raison d'anomalies non détectées.",
        body_style
    ))

    story.append(Paragraph("<b>Tableau des anomalies interceptées dans <code>orders_day1.csv</code> :</b>", body_style))
    anomalies_data = [
        [Paragraph("Dimension de Qualité", table_header), Paragraph("Order ID", table_header), Paragraph("Description du Problème", table_header), Paragraph("Action / Règle appliquée", table_header)],
        [Paragraph("<b>Complétude</b>", table_cell), Paragraph("1008", table_cell), Paragraph("customer_id absent (valeur vide)", table_cell), Paragraph("Rejeté : <code>missing_customer_id</code>", table_cell)],
        [Paragraph("<b>Unicité</b>", table_cell), Paragraph("1010", table_cell), Paragraph("Commande dupliquée à l'identique", table_cell), Paragraph("Rejeté : <code>duplicate_order_id</code>", table_cell)],
        [Paragraph("<b>Validité</b>", table_cell), Paragraph("1004", table_cell), Paragraph("Quantité négative (quantity = -2)", table_cell), Paragraph("Rejeté : <code>invalid_quantity</code>", table_cell)],
        [Paragraph("<b>Validité</b>", table_cell), Paragraph("1013", table_cell), Paragraph("Date impossible (2026-13-45)", table_cell), Paragraph("Rejeté : <code>invalid_date</code>", table_cell)],
        [Paragraph("<b>Exactitude / Plausibilité</b>", table_cell), Paragraph("1019", table_cell), Paragraph("Clavier à 4 500 € au lieu de 45 €", table_cell), Paragraph("Rejeté : <code>invalid_unit_price</code>", table_cell)],
        [Paragraph("<b>Cohérence</b>", table_cell), Paragraph("1006, 1016, 1023", table_cell), Paragraph("Casse et espaces (' tunisia', 'MOROCCO')", table_cell), Paragraph("Nettoyé : <code>.str.strip().str.title()</code>", table_cell)]
    ]
    anomalies_table = Table(anomalies_data, colWidths=[110, 55, 190, 160])
    anomalies_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(anomalies_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Réponses aux Questions Clés du TP1 :</b>", h2_style))
    story.append(Paragraph("<b>Q1 (requirements.txt) :</b> Figer les dépendances et versions minimales assure la reproductibilité stricte sur toute machine et dans la CI via <code>pip install -r requirements.txt</code>.", body_style))
    story.append(Paragraph("<b>Q4 (Évaluation du total sans contrôle) :</b> Impossible de savoir si le chiffre naïf est trop haut ou trop bas car les erreurs se compensent partiellement (les quantités négatives tirent vers le bas, les doublons et prix aberrants tirent vers le haut).", body_style))
    story.append(Paragraph("<b>Q8 (Fichier de quarantaine) :</b> Enregistrer les lignes rejetées dans <code>rejected_orders.csv</code> garantit l'observabilité et l'auditabilité : les équipes métier peuvent investiguer et retraiter les commandes légitimes sans perte d'information.", body_style))
    story.append(Paragraph("<b>Q13 (Danger J2 vs J3) :</b> Le Jour 2 est infiniment plus dangereux car l'ancien script tourne sans erreur et publie silencieusement un total colossalement faux (270 200 € au lieu de 2 702 €). Le Jour 3 plante bruyamment (KeyError), ce qui alerte immédiatement.", body_style))
    story.append(Paragraph("<b>Q14 (Code de sortie 1) :</b> Utilisé par les orchestrateurs (Airflow, Dagster) et la CI (GitHub Actions) pour bloquer l'exécution en aval et alerter l'équipe en cas d'anomalie.", body_style))

    story.append(PageBreak())

    # ==========================
    # TP 2 : GIT & DVC
    # ==========================
    story.append(Paragraph("3. TP 2 — Versionner le Code avec Git et les Données avec DVC", h1_style))
    story.append(Paragraph(
        "<b>Objectif :</b> Les pipelines de données dépendent de deux composants qui évoluent indépendamment : le code et les données. "
        "Les données volumineuses ne doivent pas être commitées dans Git (gonflement du dépôt). DVC permet de versionner les données dans un stockage "
        "externe tout en conservant un pointeur léger (<code>.dvc</code>) tracé par Git.",
        body_style
    ))

    story.append(Paragraph("<b>Architecture et Cycle de Vie Mis en Œuvre :</b>", h2_style))
    story.append(Paragraph(
        "1. <b>Branche de fonctionnalité :</b> Création de <code>feature/country-rule</code> pour la Règle 6 (rejet des pays hors périmètre avec <code>unknown_country</code>), "
        "couplée à un test pytest (6/6 passés), puis fusion explicite <code>git merge --no-ff</code> sur <code>main</code>.<br/>"
        "2. <b>Initialisation DVC :</b> Suppression des CSV de l'index Git (<code>git rm --cached</code>) et suivi par DVC (<code>dvc add data/raw</code>). "
        "Génération de <code>data/raw.dvc</code> (empreinte MD5) et tag <code>data-v1</code>.<br/>"
        "3. <b>Remote de stockage :</b> Configuration de <code>../dvc-storage</code> et synchronisation via <code>dvc push</code> (Content-Addressable Storage).<br/>"
        "4. <b>Nouvelle version de données :</b> Intégration de 5 commandes tardives (35 commandes au total). Mise à jour de l'empreinte MD5, création du tag <code>data-v2</code>. "
        "Le pipeline produit le nouveau chiffre d'affaires exact : <b>8 835,40 €</b>.<br/>"
        "5. <b>Time-Travel vérifié :</b> Restauration de l'état passé via <code>git checkout data-v1 -- data/raw.dvc</code> et <code>dvc checkout</code> (retour à 31 lignes et 7 655,90 €), puis retour immédiat à <code>HEAD</code>.<br/>"
        "6. <b>Reproduction par un tiers :</b> Clone simulé dans <code>../teammate</code> : <code>git clone</code> + <code>dvc pull</code> reproduit exactement les <b>8 835,40 €</b>.",
        body_style
    ))

    # Tableau Questions TP2
    story.append(Paragraph("<b>Réponses aux Questions Clés du TP2 :</b>", h2_style))
    story.append(Paragraph("<b>Q1 (Isolation des branches) :</b> Pendant le travail sur la branche, <code>main</code> reste totalement stable. Si un batch tourne la nuit depuis <code>main</code>, il ne risque jamais d'exécuter un code en cours de test.", body_style))
    story.append(Paragraph("<b>Q3 & Q5 (Empreinte MD5 et nommage CAS) :</b> Les fichiers dans <code>dvc-storage</code> sont nommés par leur hash MD5. Ce nommage par contenu évite les collisions, déduplique automatiquement les fichiers identiques et permet à plusieurs versions de coexister.", body_style))
    story.append(Paragraph("<b>Q9 (Oubli de dvc checkout) :</b> Si l'on change de version dans Git sans exécuter <code>dvc checkout</code>, les fichiers physiques sur disque ne correspondent plus au pointeur. Le pipeline s'exécute sur des données désynchronisées, produisant un rapport faux tout en prétendant correspondre à l'ancien commit.", body_style))
    story.append(Paragraph("<b>Q10 (Rôles respectifs de Git et DVC) :</b> <code>git clone</code> transfère le code, l'historique et les pointeurs légers ; <code>dvc pull</code> télécharge les volumineux fichiers de données depuis le stockage distribué.", body_style))

    # Git Log Graph Box
    log_text = """* 7e3671c Describe the report as a DVC stage
* 95a8f79 (tag: data-v2) Data v2: late orders for 2026-10-05
* 454c740 Add the DVC remote
* 840c0e0 (tag: data-v1) Track raw data with DVC
*   af9ef9a Merge the country rule
|\\  
| * 010fdc6 (feature/country-rule) Reject orders from countries the shop does not sell to
|/  
* caa0628 Finish TP1, add DVC to requirements
* 4cd79aa Add pipeline, data checks and unit tests
* 3c8775a Empty project with requirements"""
    log_table = Table([[Paragraph(f"<font face='Courier' size=7 color='#E2E8F0'>{log_text.replace(chr(10), '<br/>')}</font>", code_style)]], colWidths=[515])
    log_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
        ('BOX', (0,0), (-1,-1), 1, c_primary),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Graphe Git des branches, fusions et tags DVC :</b>", body_style))
    story.append(log_table)

    story.append(PageBreak())

    # ==========================
    # TP 3 : ELT DUCKDB & DBT
    # ==========================
    story.append(Paragraph("4. TP 3 — Du Pipeline Python à l'ELT Moderne avec DuckDB et dbt", h1_style))
    story.append(Paragraph(
        "<b>Transition ETL vers ELT :</b> Dans l'ETL (TP1), la transformation s'exécutait en mémoire Python avant écriture. "
        "Dans l'ELT moderne (TP3), le fichier brut est chargé tel quel dans l'entrepôt analytique (DuckDB), et l'ensemble des transformations "
        "est orchestré en SQL en couches modulaires via dbt (Data Build Tool).",
        body_style
    ))

    story.append(Paragraph("<b>Architecture en Couches dbt Implémentée :</b>", h2_style))
    layers_data = [
        [Paragraph("Couche", table_header), Paragraph("Modèle SQL", table_header), Paragraph("Matérialisation", table_header), Paragraph("Rôle & Spécificités DataOps", table_header)],
        [
            Paragraph("<b>Source</b>", table_cell_bold),
            Paragraph("<code>raw.orders</code>", table_cell),
            Paragraph("Table brute", table_cell),
            Paragraph("Chargé par <code>load_raw.py</code> avec <code>all_varchar=true</code>. Colonnes techniques <code>_row_number</code>, <code>_source_file</code>, <code>_loaded_at</code>.", table_cell)
        ],
        [
            Paragraph("<b>Staging</b>", table_cell_bold),
            Paragraph("<code>stg_orders</code>", table_cell),
            Paragraph("View", table_cell),
            Paragraph("Typage strict (<code>try_cast</code>, <code>try_strptime</code>, <code>decimal(10,2)</code>). Nettoyage de casse/espaces des pays. <b>Aucune ligne supprimée</b>.", table_cell)
        ],
        [
            Paragraph("<b>Intermediate</b>", table_cell_bold),
            Paragraph("<code>int_orders_checked</code>", table_cell),
            Paragraph("View", table_cell),
            Paragraph("Application séquentielle des <b>6 règles de qualité</b> via <code>CASE WHEN ... END AS reject_reason</code>.", table_cell)
        ],
        [
            Paragraph("<b>Marts</b>", table_cell_bold),
            Paragraph("<code>orders_clean</code><br/><code>orders_rejected</code><br/><code>revenue_by_country</code>", table_cell),
            Paragraph("Tables", table_cell),
            Paragraph("• <code>orders_clean</code> : commandes saines (reject_reason IS NULL).<br/>• <code>orders_rejected</code> : table de quarantaine.<br/>• <code>revenue_by_country</code> : rapport direction (<b>8 835,40 €</b>).", table_cell)
        ],
        [
            Paragraph("<b>Bonus Marts</b>", table_cell_bold),
            Paragraph("<code>revenue_by_product</code>", table_cell),
            Paragraph("Table", table_cell),
            Paragraph("Nouvel indicateur analyste ajouté sans écrire une seule ligne de Python.", table_cell)
        ]
    ]
    layers_table = Table(layers_data, colWidths=[75, 110, 80, 250])
    layers_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent_dark),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(layers_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Batterie de Tests dbt (Tests de Données & Tests Unitaires) :</b>", h2_style))
    story.append(Paragraph(
        "• <b>Tests génériques (marts.yml) :</b> <code>unique</code> et <code>not_null</code> sur <code>order_id</code>, <code>not_null</code> sur <code>customer_id</code>, <code>accepted_values</code> sur <code>country</code>.<br/>"
        "• <b>Tests singuliers (SQL métier) :</b> <code>assert_quantity_positive.sql</code> (quantités > 0) et <code>assert_reject_rate_below_20_percent.sql</code> (arrêt si taux rejet > 20%).<br/>"
        "• <b>Tests unitaires dbt (int_orders_checked.yml) :</b> Vérification de la logique SQL sur des données synthétiques injectées en YAML (rejet de pays non autorisés et déduplication).<br/>"
        "• <b>Résultat d'exécution :</b> <code>Done. PASS=14 WARN=0 ERROR=0 SKIP=0</code> (et <code>PASS=16</code> avec le modèle analyste).",
        body_style
    ))

    # Tableau Comparatif Jours 2 et 3
    story.append(Paragraph("<b>Validation de la Résistance aux Mauvaises Données (Jours 2 et 3) :</b>", h2_style))
    j23_data = [
        [Paragraph("Scénario", table_header), Paragraph("Comportement Pipeline Python (TP1)", table_header), Paragraph("Comportement Pipeline dbt (TP3)", table_header)],
        [
            Paragraph("<b>Jour 2 :</b> Prix aberrants en centimes (multipliés par 100)", table_cell_bold),
            Paragraph("<code>check_reject_rate</code> lève <code>DataQualityError</code> (100% rejet). Arrêt net (exit code 1).", table_cell),
            Paragraph("Test singulier <code>assert_reject_rate_below_20_percent</code> en <b>FAIL</b>. Tous les marts passent en <b>SKIP</b> (exit code 1). Rapport J1 préservé.", table_cell)
        ],
        [
            Paragraph("<b>Jour 3 :</b> Renommage de colonne source ('price')", table_cell_bold),
            Paragraph("<code>check_schema</code> lève <code>DataQualityError: Missing columns: ['unit_price']</code>. Arrêt net.", table_cell),
            Paragraph("Échec immédiat de compilation/liaison DuckDB dans <code>stg_orders</code> (Binder Error). 13 étapes suivantes en <b>SKIP</b> (exit code 1).", table_cell)
        ],
        [
            Paragraph("<b>Retour Jour 1 :</b> Données saines", table_cell_bold),
            Paragraph("Succès complet, total = 8 835,40 €.", table_cell),
            Paragraph("<b>PASS=14</b> (100% vert), total exact = <b>8 835,40 €</b>.", table_cell)
        ]
    ]
    j23_table = Table(j23_data, colWidths=[135, 190, 190])
    j23_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(j23_table)

    story.append(PageBreak())

    # ==========================
    # SYNTHÈSE DES PRATIQUES
    # ==========================
    story.append(Paragraph("5. Synthèse des Bonnes Pratiques DataOps Validées", h1_style))
    
    practices_data = [
        [Paragraph("Pilier DataOps", table_header), Paragraph("Principe Théorique", table_header), Paragraph("Mise en Pratique dans le Projet", table_header)],
        [
            Paragraph("<b>Analytics is Code</b>", table_cell_bold),
            Paragraph("Toute logique de données doit être versionnée, revue et testable comme du logiciel.", table_cell),
            Paragraph("Transformations en fichiers SQL versionnés dans Git, dépendances déclarées dans <code>dbt_project.yml</code>.", table_cell)
        ],
        [
            Paragraph("<b>Data as Code</b>", table_cell_bold),
            Paragraph("Séparer le stockage des données volumineuses du code source tout en garantissant leur traçabilité.", table_cell),
            Paragraph("Données gérées par DVC (Content-Addressable Storage), pointeurs légers <code>.dvc</code> suivis dans Git.", table_cell)
        ],
        [
            Paragraph("<b>Tests de Code vs Tests de Données</b>", table_cell_bold),
            Paragraph("Distinguer la validité de la logique algorithmique de la conformité des données entrantes.", table_cell),
            Paragraph("• Tests de code : Pytest & tests unitaires dbt (données mockées statiques).<br/>• Tests de données : contrôles de schéma, tests singuliers dbt (données réelles de production).", table_cell)
        ],
        [
            Paragraph("<b>Arrêter la Chaîne (Andon Cord)</b>", table_cell_bold),
            Paragraph("Ne jamais publier de rapport sur des données corrompues ou incomplètes.", table_cell),
            Paragraph("Échec bloquant de <code>dbt build</code> mettant les tables aval en <code>SKIP</code> et préservant le rapport de la veille.", table_cell)
        ],
        [
            Paragraph("<b>Observabilité & Lignage</b>", table_cell_bold),
            Paragraph("Comprendre immédiatement l'impact d'une modification et tracer les rejets.", table_cell),
            Paragraph("Graphe de dépendance DAG généré avec <code>dbt docs</code> et table de quarantaine matérialisée <code>orders_rejected</code>.", table_cell)
        ],
        [
            Paragraph("<b>Intégration Continue (CI)</b>", table_cell_bold),
            Paragraph("Exécution automatique des tests à chaque push ou Pull Request.", table_cell),
            Paragraph("Workflow GitHub Actions configuré dans <code>.github/workflows/ci.yml</code>.", table_cell)
        ]
    ]
    practices_table = Table(practices_data, colWidths=[120, 165, 230])
    practices_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(practices_table)
    story.append(Spacer(1, 14))

    # Bloc Conclusion & Signature
    story.append(Paragraph("<b>Conclusion :</b>", h2_style))
    story.append(Paragraph(
        "Ce cycle de trois TP démontre avec rigueur comment transformer un script artisanal en une plateforme d'ingénierie de données robuste, "
        "collaborative et pérenne. L'équipe dispose désormais d'un pipeline ELT moderne, d'un entrepôt analytique autonome, d'une couverture "
        "complète de tests de qualité, et d'un couplage parfait entre l'historique du code et celui des données.",
        body_style
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<i>Document généré automatiquement dans le cadre du projet dataops-lab1 — Tous droits réservés.</i>", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated: {filename}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "Rapport_DataOps_TP1_TP2_TP3.pdf"
    build_pdf(out_file)
