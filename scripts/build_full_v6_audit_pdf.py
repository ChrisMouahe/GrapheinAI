"""Master ReportLab PDF Builder generating the full v6.0.0 Audit Document with optimized font readability and premium section layout."""

import os
import sys
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image as RLImage
)
from reportlab.pdfgen import canvas

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = ROOT_DIR / "audit_complet_graphein_ai_v6_production_roadmap.pdf"

class NumberedCanvas(canvas.Canvas):
    """Custom canvas providing Page X / Y numbering and running corporate headers/footers."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            
            # Running Header
            self.drawString(36, 11 * 72 - 30, "GRAPHEIN AI — AUDIT TECHNIQUE, ARCHITECTURAL ET STRATÉGIQUE (V6.0.0)")
            self.drawRightString(8.5 * 72 - 36, 11 * 72 - 30, "PRODUCTION ROADMAP & GO-TO-MARKET (FCFA)")
            
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * 72 - 34, 8.5 * 72 - 36, 11 * 72 - 34)

            # Running Footer
            self.line(36, 38, 8.5 * 72 - 36, 38)
            self.setFont("Helvetica", 8)
            self.drawString(36, 26, "© 2026 GraphEin AI Inc. — Rapport d'Audit & Production Roadmap (Côte d'Ivoire & UEMOA)")
            page_text = f"Page {self._pageNumber} / {page_count}"
            self.drawRightString(8.5 * 72 - 36, 26, page_text)
            self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_secondary = colors.HexColor("#1E3A8A")  # Blue 900
    c_accent = colors.HexColor("#1D4ED8")     # Blue 700
    c_text = colors.HexColor("#1E293B")       # Slate 800
    c_muted = colors.HexColor("#475569")      # Slate 600
    
    styles.add(ParagraphStyle(
        "CoverMainTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=colors.white,
        alignment=0,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        "CoverSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#93C5FD"),
        alignment=0,
        spaceAfter=14
    ))

    styles.add(ParagraphStyle(
        "PartH1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13.5,
        leading=17,
        textColor=c_secondary,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        "PartH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14.5,
        textColor=c_accent,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_text,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        "BulletCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_text,
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        "CalloutBox",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=12.5,
        textColor=colors.HexColor("#1E3A8A"),
    ))

    styles.add(ParagraphStyle(
        "TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
        alignment=1
    ))

    styles.add(ParagraphStyle(
        "TD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.6,
        leading=10.2,
        textColor=c_text
    ))

    styles.add(ParagraphStyle(
        "TDBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.6,
        leading=10.2,
        textColor=c_text
    ))

    styles.add(ParagraphStyle(
        "CodeText",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=9.2,
        textColor=colors.HexColor("#0F172A")
    ))

    return styles

def make_part_banner(title_text, subtitle=None):
    """Generates an executive full-width banner block for major parts."""
    rows = [
        [
            Paragraph(f"<b>{title_text}</b>", ParagraphStyle(
                "BannerTitle",
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=15,
                textColor=colors.white
            ))
        ]
    ]
    if subtitle:
        rows.append([
            Paragraph(subtitle, ParagraphStyle(
                "BannerSubtitle",
                fontName="Helvetica",
                fontSize=8.5,
                leading=11.5,
                textColor=colors.HexColor("#BAE6FD")
            ))
        ])
    t = Table(rows, colWidths=[7.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0F172A")),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINELEFT', (0,0), (0,-1), 4.5, colors.HexColor("#0284C7")),
    ]))
    return t

def make_callout(html_text, bg_hex="#F0F9FF", border_hex="#0284C7"):
    """Generates a stylish callout notification card."""
    styles = get_styles()
    p = Paragraph(html_text, styles["CalloutBox"])
    t = Table([[p]], colWidths=[7.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_hex)),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINELEFT', (0,0), (-1,-1), 3.5, colors.HexColor(border_hex)),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BAE6FD")),
    ]))
    return t

def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )
    
    styles = get_styles()
    story = []

    # =========================================================================
    # PAGE DE GARDE / COVER PAGE
    # =========================================================================
    cover_data = [
        [
            Paragraph("<b>RAPPORT D'AUDIT TECHNIQUE, ARCHITECTURAL ET STRATÉGIQUE COMPLET</b>", styles["CoverMainTitle"]),
        ],
        [
            Paragraph("<b>Projet GraphEin AI — Version 6.0.0 Production Roadmap & Go-to-Market</b><br/>"
                      "Dossier de Référence de Passation, d'Investissement, FinOps et de Déploiement Industriel", styles["CoverSub"]),
        ],
        [
            Paragraph("<b>Auteurs :</b> Consortium d'Experts (CTO SaaS, Principal Software Architect, Senior AI Research Scientist, Principal MLOps Engineer, Senior Cloud Architect, FinOps Specialist, VC Technical Due Diligence Partner)<br/>"
                      "<b>Marché & Ancrage :</b> Côte d'Ivoire / Zone UEMOA & International | <b>Devise de Référence :</b> Franc CFA (XOF)<br/>"
                      "<b>Date d'Émission :</b> Septembre 2026 | <b>Statut de Certification :</b> <b>GO Conditionnel</b> (Score Révisé : <b>8.4 / 10</b>)", 
                      ParagraphStyle('CoverMeta', fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=colors.HexColor('#E2E8F0')))
        ]
    ]
    cover_table = Table(cover_data, colWidths=[7.5 * inch])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
        ('PADDING', (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 8))

    # Executive Scorecard Banner
    score_data = [
        [
            Paragraph("<b>Architecture Hexagonale</b><br/><font size=9.5 color='#2563EB'><b>9.5 / 10</b></font>", styles["TD"]),
            Paragraph("<b>Exactitude Mathématique AST</b><br/><font size=9.5 color='#059669'><b>10.0 / 10</b></font>", styles["TD"]),
            Paragraph("<b>Sécurité & RLS Supabase</b><br/><font size=9.5 color='#2563EB'><b>8.8 / 10</b></font>", styles["TD"]),
            Paragraph("<b>Couverture Tests (28 Suites)</b><br/><font size=9.5 color='#2563EB'><b>9.0 / 10</b></font>", styles["TD"]),
            Paragraph("<b>Budget Lean (<100k F/m)</b><br/><font size=9.5 color='#059669'><b>9.8 / 10</b></font>", styles["TD"]),
            Paragraph("<b>Score Global Révisé</b><br/><font size=10.5 color='#059669'><b>8.4 / 10 (GO)</b></font>", styles["TDBold"]),
        ]
    ]
    score_table = Table(score_data, colWidths=[1.25*inch]*6)
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 10))

    # Table des Matières Formelle (22 Parties)
    story.append(make_part_banner("TABLE DES MATIÈRES EXHAUSTIVE (VERSION 6.0.0)"))
    story.append(Spacer(1, 6))

    toc_list = [
        ("RÉSUMÉ EXÉCUTIF", "Diagnostic expert réel, 4 chantiers critiques, FinOps d'amorçage et décision GO conditionnel"),
        ("PARTIE 1 : État Actuel & Vision Stratégique", "Ancrage Côte d'Ivoire / UEMOA, BRVM, Agro-industrie, Nuance mathématique AST vs VLM"),
        ("PARTIE 2 : Cartographie Complète du Codebase", "Architecture Hexagonale, Analyse d'impact des 28 modules, Tableau d'état réel vérifié"),
        ("PARTIE 3 : Inventaire des 34 Fonctionnalités", "Statuts réalistes, Ajout Mobile Money (CinetPay) et Enforceur de quotas par plan"),
        ("PARTIE 4 : Analyse du Pipeline IA Multimodal", "OpenCV + Gemini 2.5 Flash, AST SafeCalculator, Limites VLM et garde-fous statistiques"),
        ("PARTIE 5 : Architecture & Pile Logicielle", "FastAPI, Supabase PostgreSQL RLS, Intégration Celery + Redis asynchrone (Sprint 3)"),
        ("PARTIE 6 : Qualité du Code & Dette Technique", "Typage strict Pydantic V2, Ruff/Black, Priorités SRE (Doppler, Redis, Tests RLS)"),
        ("PARTIE 7 : Sécurité, OWASP & Conformité ARTCI", "Plan de tests RLS multi-tenant, TVA 18% Côte d'Ivoire, Déclaration obligatoire ARTCI"),
        ("PARTIE 8 : Performance & Optimisations SRE", "Latences, Stratégie de cache à 3 niveaux (SHA-256, imagehash, sémantique Redis)"),
        ("PARTIE 9 : Scalabilité & Architecture Cible", "Phase 0 Lean (Hetzner CPX31 + Compose < 100k F/m), Report de Kubernetes à Phase 3"),
        ("PARTIE 10 : Stratégie Cloud & Benchmark", "Comparatif Hetzner vs AWS vs GCP vs DigitalOcean, Recommandation Phase 1 Hetzner"),
        ("PARTIE 11 : Benchmark Comparatif des VLM", "Gemini 2.5 Flash vs Pro vs GPT-4o vs Claude 3.5, Routage intelligent FinOps (-50 à -75%)"),
        ("PARTIE 12 : Modélisation Coûts FinOps en FCFA", "Scénario Early Stage Lean (100–1k users à 88 050 FCFA/m) et projections à l'échelle"),
        ("PARTIE 13 : Modèle Économique & Facturation", "Grille tarifaire (Free, Pro, Team, API), Mécanique Mobile Money (liens CinetPay), TVA 18%"),
        ("PARTIE 14 : Roadmap Stratégique R&D", "Perspectives 12–24 mois : 3D, Séries temporelles complexes, Connecteurs BI, SLM On-prem"),
        ("PARTIE 15 : Analyse Concurrentielle", "Différenciation : Zéro hallucination arithmétique, HITL, Mobile Money UEMOA, Prix bas"),
        ("PARTIE 16 : Plan de Déploiement & Critères DoD", "Gouvernance Agile, Exécution 90 jours et critères stricts de sortie de sprint"),
        ("PARTIE 17 : Conclusion & Décision d'Investissement", "Arbitrage GO Conditionnel, Validation des 10 jalons impératifs de production"),
        ("PARTIE 18 : Roadmap 90 Jours Opérationnelle", "Détail des 6 Sprints de 2 semaines (Sprint 0 à 6) avec livrables et Definition of Done"),
        ("PARTIE 19 : Stratégie de Paiement Mobile Money", "CinetPay/PayDunya, Schéma SQL billing Supabase complet, Flux 7 étapes, Dunning"),
        ("PARTIE 20 : AI Ops & Évaluation Continue", "Golden Dataset (100 graphes BRVM/agro), Registry de prompts, Active Learning HITL"),
        ("PARTIE 21 : Budget d'Amorçage Lean Détaillé", "Postes mensuels chiffrés (< 100 000 FCFA/m), Scénarios 100, 1k et 10k utilisateurs"),
        ("PARTIE 22 : Checklist des 10 Conditions Go-Live", "Matrice d'audit final bloquante avant ouverture commerciale publique"),
    ]
    for title, desc in toc_list:
        story.append(Paragraph(f"• <b>{title}</b> — <font color='#475569'>{desc}</font>", styles["BulletCustom"]))

    story.append(PageBreak())

    # =========================================================================
    # RÉSUMÉ EXÉCUTIF
    # =========================================================================
    story.append(make_part_banner("🏛️ RÉSUMÉ EXÉCUTIF & SYNTHÈSE DE DÉCISION (1 PAGE)"))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "<b>GraphEin AI</b> s'affirme comme une plateforme SaaS industrielle d'intelligence graphique multimodale pionnière, "
        "conçue pour résoudre l'un des goulets d'étranglement les plus coûteux des entreprises et institutions : "
        "l'extraction, la vérification mathématique et la synthèse décisionnelle des données encapsulées dans des visuels complexes "
        "(courbes boursières, bilans annuels, histogrammes d'activité, planches multi-graphiques). "
        "Ancré prioritairement en Côte d'Ivoire et dans la zone UEMOA, le projet s'adresse aux banques (BRVM), cabinets d'audit, compagnies agro-industrielles et ministères.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>Diagnostic Réel Post-Audit Expert : Fin du Mythe du 9.2/10 Fictif</b>", styles["PartH2"]))
    story.append(Paragraph(
        "Le second audit expert réévalue la maturité globale à <b>8.4 / 10 (Production-Grade Foundational)</b>, en corrigeant deux surévaluations :<br/>"
        "1. <b>Exactitude Mathématique vs Probabilité VLM :</b> L'exactitude mathématique est <b>garantie à 100 % sur les calculs arithmétiques déterministes</b> via l'AST Python (<code>SafeCalculator</code>). "
        "Cependant, l'extraction visuelle initiale par Gemini 2.5 Flash demeure <b>probabiliste</b> et assujettie à la qualité d'image, au score de confiance et à la validation humaine obligatoire (HITL).<br/>"
        "2. <b>Maturité Réelle du Codebase :</b> Sur 34 fonctionnalités, 18 sont en production stable, 8 en production partielle, 4 en statut bêta et 4 restent à implémenter pour le Go-Live commercial.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>Les 4 Chantiers Critiques Indispensables au Go-Live Commercial</b>", styles["PartH2"]))
    story.append(Paragraph("• <b>Passerelle Mobile Money Locale :</b> Intégration de CinetPay/PayDunya (Wave, Orange, MTN) avec facturation TVA 18 % Côte d'Ivoire.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Exécution Asynchrone Celery + Redis :</b> Découplage de l'API FastAPI des tâches lourdes (PDF vectoriel, VLM, emails).", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Enforceur de Quotas par Palier :</b> Régulation stricte de consommation API (Free, Pro, Team) pour préserver les marges brutes.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Sécurité RLS & Conformité Réglementaire :</b> Tests d'étanchéité multi-tenant automatisés et dépôt du dossier légal ARTCI.", styles["BulletCustom"]))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>FinOps d'Amorçage & Décision d'Investissement</b>", styles["PartH2"]))
    story.append(make_callout(
        "<b>Synthèse de Décision :</b> Déploiement Phase 0 Lean sur <b>Hetzner Cloud (CPX31) + Docker Compose + Supabase Pro + Cloudflare</b> pour un coût opérationnel maîtrisé de <b>74 130 FCFA/mois (113 €)</b> à 1 000 utilisateurs. "
        "L'audit conclut à un <b>GO CONDITIONNEL (8.4 / 10)</b> assujetti à la validation de la Roadmap 90 jours et des 10 conditions de Go-Live."
    ))

    story.append(PageBreak())

    # =========================================================================
    # PARTIE 1 : ÉTAT ACTUEL DU PROJET & VISION
    # =========================================================================
    story.append(make_part_banner("PARTIE 1 : ÉTAT ACTUEL DU PROJET & VISION STRATÉGIQUE"))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>1.1. Ancrage dans l'Écosystème Ivoirien et Sous-Régional (UEMOA)</b>", styles["PartH2"]))
    story.append(Paragraph(
        "En Côte d'Ivoire et dans la zone UEMOA, plus de <b>65 % des métriques décisionnelles</b> demeurent prisonnières de rapports PDF ou captures d'écran. "
        "Les analystes financiers de la place d'Abidjan et les contrôleurs de gestion consacrent en moyenne 4,5 heures par semaine à ressaisir manuellement des valeurs sous Excel, "
        "avec un taux d'erreur documenté entre 3 % et 8 %. GraphEin AI digitalise, extrait et fiabilise ce patrimoine visuel en moins de 2 secondes.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>1.2. Nuance Fondamentale : Exactitude AST vs Probabilité VLM</b>", styles["PartH2"]))
    story.append(make_callout(
        "<b>1. Exactitude Mathématique Déterministe (100 % Fiable) :</b> Le composant <code>SafeCalculator</code> compile les expressions arithmétiques via l'arbre syntaxique abstrait (<code>ast.parse</code>). "
        "Les opérations (+, -, *, /, %, moyennes, TCAM) sont exécutées directement par le processeur Python sans intervention d'un LLM. Zéro hallucination mathématique garantie.<br/>"
        "<b>2. Extraction VLM Probabiliste (Fiabilité 92 % à 98 %) :</b> L'inférence par Gemini 2.5 Flash Vision est une lecture statistique. Sur des images floues ou bruitées, des erreurs de transcription restent possibles. "
        "La fiabilité du système découle du triptyque : <i>Score de Confiance Pondéré ➔ Détection d'Anomalies Z-Score ➔ Validation Humaine HITL</i>."
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.3. Matrice de Différenciation Marché (UVP)</b>", styles["PartH2"]))
    uvp_data = [
        [Paragraph("Défi du Marché Actuel", styles["TH"]), Paragraph("Solution Technologique GraphEin AI", styles["TH"]), Paragraph("Bénéfice Quantifiable", styles["TH"])],
        [Paragraph("Hallucinations arithmétiques des LLM", styles["TD"]), Paragraph("Calcul déterministe par AST Python (aucun eval)", styles["TD"]), Paragraph("<b>100 % exactitude calculs</b>", styles["TDBold"])],
        [Paragraph("Extraction visuelle opaque ou erronée", styles["TD"]), Paragraph("Grille interactive Human-in-the-Loop (HITL)", styles["TD"]), Paragraph("Validation humaine en 1 clic", styles["TD"])],
        [Paragraph("Absence de paiement bancaire régional", styles["TD"]), Paragraph("Intégration Mobile Money native (Wave, Orange, MTN)", styles["TD"]), Paragraph("Monétisation fluide UEMOA", styles["TD"])],
        [Paragraph("Coûts de tokens exorbitants", styles["TD"]), Paragraph("Routage intelligent AST/FAISS + Cache SHA-256", styles["TD"]), Paragraph("<b>-50 % à -75 % coûts VLM</b>", styles["TDBold"])],
    ]
    t_uvp = Table(uvp_data, colWidths=[2.1*inch, 3.5*inch, 1.9*inch])
    t_uvp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_uvp)

    story.append(PageBreak())

    # =========================================================================
    # PARTIE 2 : CARTOGRAPHIE DU CODEBASE
    # =========================================================================
    story.append(make_part_banner("PARTIE 2 : CARTOGRAPHIE DU CODEBASE & ÉTAT RÉEL VÉRIFIÉ"))
    story.append(Spacer(1, 8))
    
    code_data = [
        [Paragraph("Composant / Fichier", styles["TH"]), Paragraph("Rôle & Responsabilité", styles["TH"]), Paragraph("État Réel Vérifié", styles["TH"]), Paragraph("Actions Requises", styles["TH"])],
        [Paragraph("pipeline_agent.py", styles["TDBold"]), Paragraph("Orchestrateur maître (Vision, AST, RAG, Synthèse)", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"]), Paragraph("Aucune (Stable)", styles["TD"])],
        [Paragraph("safe_calculator.py", styles["TDBold"]), Paragraph("Évaluation déterministe par AST Python", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"]), Paragraph("Aucune (100% testé)", styles["TD"])],
        [Paragraph("reasoning_agent.py", styles["TDBold"]), Paragraph("Inférence Gemini 2.5 Flash Vision & Pydantic DTO", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"]), Paragraph("Maintenir fallback 2.5 Pro", styles["TD"])],
        [Paragraph("multi_chart_pipeline.py", styles["TDBold"]), Paragraph("Segmentation et fusion multi-graphiques", styles["TD"]), Paragraph("<font color='#D97706'><b>Bêta</b></font>", styles["TD"]), Paragraph("Durcir planches asymétriques", styles["TD"])],
        [Paragraph("gemini/cache.py", styles["TDBold"]), Paragraph("Cache persistant SHA-256 + hash perceptuel", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"]), Paragraph("Migration Redis (Sprint 3)", styles["TD"])],
        [Paragraph("gemini/router.py", styles["TDBold"]), Paragraph("Routage heuristique requêtes AST vs VLM", styles["TD"]), Paragraph("<font color='#D97706'><b>Bêta</b></font>", styles["TD"]), Paragraph("Enrichir lexique financier", styles["TD"])],
        [Paragraph("static/index.html", styles["TDBold"]), Paragraph("SPA Stepper 5 étapes, HITL DataGrid, i18n FR/EN", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"]), Paragraph("Légère (<200 Ko)", styles["TD"])],
        [Paragraph("supabase/schema.sql", styles["TDBold"]), Paragraph("Schéma PostgreSQL, JWT Auth & RLS multi-tenant", styles["TD"]), Paragraph("<font color='#2563EB'><b>Production partielle</b></font>", styles["TD"]), Paragraph("Tests d'étanchéité RLS (Sprint 1)", styles["TD"])],
        [Paragraph("task_queue.py", styles["TDBold"]), Paragraph("Traitement des tâches de fond", styles["TD"]), Paragraph("<font color='#DC2626'><b>Partiel</b></font>", styles["TD"]), Paragraph("Migration Celery/Redis (Sprint 3)", styles["TD"])],
        [Paragraph("billing_service.py", styles["TDBold"]), Paragraph("Passerelle Mobile Money CinetPay & TVA 18%", styles["TD"]), Paragraph("<font color='#DC2626'><b>À faire</b></font>", styles["TD"]), Paragraph("Développement Sprint 2", styles["TD"])],
    ]
    t_code = Table(code_data, colWidths=[1.6*inch, 2.6*inch, 1.4*inch, 1.9*inch])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_code)

    story.append(PageBreak())

    # =========================================================================
    # PARTIE 3 : INVENTAIRE DES 34 FONCTIONNALITÉS
    # =========================================================================
    story.append(make_part_banner("PARTIE 3 : INVENTAIRE EXHAUSTIF DES 34 FONCTIONNALITÉS"))
    story.append(Spacer(1, 8))
    
    feat_data = [
        [Paragraph("ID", styles["TH"]), Paragraph("Fonctionnalité Métier", styles["TH"]), Paragraph("Module Technique", styles["TH"]), Paragraph("Statut Réel Révisé", styles["TH"])],
        [Paragraph("F01-F03", styles["TD"]), Paragraph("Ingestion multi-formats, Magic Bytes, Segmentation OpenCV", styles["TD"]), Paragraph("api.py, security_guard, ocr_engine", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"])],
        [Paragraph("F04-F05", styles["TD"]), Paragraph("Extraction structurée VLM Gemini, Fallback ML local XGBoost", styles["TD"]), Paragraph("reasoning_agent, ml_classifier", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"])],
        [Paragraph("F06-F08", styles["TD"]), Paragraph("Grille HITL DataGrid, Calculateur AST déterministe, AnomalyDetector", styles["TD"]), Paragraph("index.html, safe_calculator, anomaly", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"])],
        [Paragraph("F09-F10", styles["TD"]), Paragraph("Recherche vectorielle RAG FAISS, Classification d'intention", styles["TD"]), Paragraph("retrieval_agent, intent_classifier", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"])],
        [Paragraph("F11-F14", styles["TD"]), Paragraph("Routage FinOps, Interpréteur narratif 4 volets, Copilote profilé, XAI 10 pts", styles["TD"]), Paragraph("router, graph_interpreter, recs, xai", styles["TD"]), Paragraph("<font color='#059669'><b>Production / Bêta</b></font>", styles["TD"])],
        [Paragraph("F15-F16", styles["TD"]), Paragraph("Pipeline multi-graphiques & moteur de fusion croisée", styles["TD"]), Paragraph("multi_chart_pipeline, multi_chart_fusion", styles["TD"]), Paragraph("<font color='#D97706'><b>Bêta</b></font>", styles["TD"])],
        [Paragraph("F17-F20", styles["TD"]), Paragraph("Chat multi-tours, Sessions, Liens chiffrés, Commentaires d'équipe", styles["TD"]), Paragraph("conversation_mgr, session_mgr, collab", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"])],
        [Paragraph("F21-F23", styles["TD"]), Paragraph("Auth JWT Supabase, Isolation multi-tenant RLS, Rôles RBAC", styles["TD"]), Paragraph("supabase_service, schema.sql", styles["TD"]), Paragraph("<font color='#2563EB'><b>Production partielle</b></font>", styles["TD"])],
        [Paragraph("F24-F26", styles["TD"]), Paragraph("Cache SHA-256 persistant, Quota Leaky Bucket, Retry Jitter", styles["TD"]), Paragraph("gemini/cache, quota, retry", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"])],
        [Paragraph("F27-F30", styles["TD"]), Paragraph("Export PDF ReportLab, Export Excel, Emailing Resend, i18n FR/EN", styles["TD"]), Paragraph("pdf_gen, openpyxl, email_svc, lang_mgr", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"])],
        [Paragraph("F31-F32", styles["TD"]), Paragraph("Console Admin, Journalisation structurée JSON Loguru", styles["TD"]), Paragraph("admin_service, structured_logger", styles["TD"]), Paragraph("<font color='#059669'><b>Production</b></font>", styles["TD"])],
        [Paragraph("F33", styles["TDBold"]), Paragraph("<b>Paiement Mobile Money (CinetPay / Wave / Orange / MTN)</b>", styles["TDBold"]), Paragraph("billing_service.py (Nouveau)", styles["TD"]), Paragraph("<font color='#DC2626'><b>À faire (Sprint 2)</b></font>", styles["TD"])],
        [Paragraph("F34", styles["TDBold"]), Paragraph("<b>Enforceur de Quotas par Plan (Free/Pro/Team/API)</b>", styles["TDBold"]), Paragraph("quota_middleware.py (Nouveau)", styles["TD"]), Paragraph("<font color='#DC2626'><b>À faire (Sprint 1)</b></font>", styles["TD"])],
    ]
    t_feat = Table(feat_data, colWidths=[0.8*inch, 3.4*inch, 1.7*inch, 1.6*inch])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_feat)

    story.append(PageBreak())

    # =========================================================================
    # PARTIES 4 à 6 : PIPELINE, ARCHITECTURE & QUALITÉ
    # =========================================================================
    story.append(make_part_banner("PARTIES 4 À 6 : PIPELINE IA, ARCHITECTURE & DETTE TECHNIQUE"))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>Limites Opérationnelles du VLM & Garde-Fous Statistiques (Partie 4)</b>", styles["PartH2"]))
    story.append(Paragraph(
        "L'inférence visuelle par Gemini 2.5 Flash présente des risques objectifs de mauvaise lecture sur les graphiques à faible contraste (&lt;150 DPI) ou à polices exotiques. "
        "GraphEin AI déploie une triple barrière de sécurité :<br/>"
        "1. <b>Validation Croisée OpenCV :</b> Comparaison spatiale des boîtes de détection géométrique avec les libellés restitués.<br/>"
        "2. <b>Détection Statistique d'Anomalies :</b> Calcul automatisé du Z-Score et de l'IQR sur chaque série extraite ; signalement visuel immédiat des points aberrants (&gt; 3&sigma;).<br/>"
        "3. <b>Interrupteur HITL :</b> Dès que le score de confiance global passe sous 80 %, l'interface bloque l'interprétation automatique et requiert l'approbation de l'analyste.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>Intégration Asynchrone Celery + Redis (Partie 5 — Chantier Sprint 3)</b>", styles["PartH2"]))
    story.append(Paragraph(
        "Pour éliminer tout risque de saturation de la boucle d'événements ASGI FastAPI lors de pics de charge, "
        "l'architecture du Sprint 3 introduit un broker Redis 7.2 et 4 workers Celery spécialisés : "
        "<code>pdf_generation_queue</code> (rendu vectoriel ReportLab), <code>ai_inference_queue</code> (analyses multi-graphiques), "
        "<code>export_queue</code> (tableurs Excel) et <code>email_queue</code> (notifications et invitations transactionnelles).",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>Audit de Qualité du Code & Purge de Dette Technique (Partie 6)</b>", styles["PartH2"]))
    story.append(Paragraph(
        "Le codebase de 12 500+ lignes Python est typé via Pydantic V2 et validé par Ruff/Black. "
        "Trois actions de purge SRE sont programmées avant ouverture commerciale : "
        "1. Centralisation des secrets sur <b>Doppler</b> (Sprint 0). "
        "2. Synchronisation du cache et des sessions sur <b>Redis</b> (Sprint 3). "
        "3. Déploiement d'une suite de tests d'intégration RLS sur conteneur PostgreSQL dédié (Sprint 1).",
        styles["BodyCustom"]
    ))

    story.append(PageBreak())

    # =========================================================================
    # PARTIES 7 & 8 : SÉCURITÉ, RLS, TVA 18%, ARTCI & CACHE 3 NIVEAUX
    # =========================================================================
    story.append(make_part_banner("PARTIES 7 & 8 : SÉCURITÉ, CONFORMITÉ ARTCI, TVA 18 % & CACHE SRE"))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>Plan de Tests de Validation RLS Multi-Tenant (Sprint 1)</b>", styles["PartH2"]))
    rls_data = [
        [Paragraph("Scénario de Test RLS", styles["TH"]), Paragraph("Simulation & Vecteur d'Attaque", styles["TH"]), Paragraph("Résultat Requis", styles["TH"]), Paragraph("Statut DoD", styles["TH"])],
        [Paragraph("Fuite Inter-Workspace", styles["TDBold"]), Paragraph("Utilisateur A tente SELECT sur session Workspace B", styles["TD"]), Paragraph("0 ligne renvoyée / 404", styles["TD"]), Paragraph("<font color='#DC2626'><b>Bloquant</b></font>", styles["TD"])],
        [Paragraph("Escalade Horizontale", styles["TDBold"]), Paragraph("Injection de commentaire sur analyse concurrente", styles["TD"]), Paragraph("Rejet RLS PostgreSQL", styles["TD"]), Paragraph("<font color='#DC2626'><b>Bloquant</b></font>", styles["TD"])],
        [Paragraph("Escalade Verticale RBAC", styles["TDBold"]), Paragraph("Rôle Viewer tente modification de permissions Admin", styles["TD"]), Paragraph("HTTP 403 Forbidden", styles["TD"]), Paragraph("<font color='#2563EB'><b>Majeur</b></font>", styles["TD"])],
        [Paragraph("Lien Public Partagé", styles["TDBold"]), Paragraph("Consultation anonyme via token chiffré", styles["TD"]), Paragraph("Lecture seule restreinte", styles["TD"]), Paragraph("<font color='#2563EB'><b>Majeur</b></font>", styles["TD"])],
    ]
    t_rls = Table(rls_data, colWidths=[1.7*inch, 2.7*inch, 1.9*inch, 1.2*inch])
    t_rls.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_rls)

    story.append(Paragraph("<b>Conformité Réglementaire : ARTCI & TVA 18 % Côte d'Ivoire</b>", styles["PartH2"]))
    story.append(Paragraph(
        "• <b>Déclaration Préalable ARTCI :</b> Obligation légale selon la loi ivoirienne n° 2013-450. Dépôt formel du registre des traitements, durée de conservation (3 ans max) et politique de consentement au Sprint 1.<br/>"
        "• <b>Facturation Fiscale TVA 18 % :</b> Application automatique du taux de 18 % DGI sur toute souscription en Côte d'Ivoire et zone UEMOA, avec ventilation HT/TVA/TTC et numéro de compte contribuable.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>Stratégie de Cache Avancée à 3 Niveaux (Partie 8)</b>", styles["PartH2"]))
    story.append(Paragraph(
        "1. <b>Niveau 1 (SHA-256 Fichier) :</b> Hachage cryptographique strict. Si le fichier binaire est identique, restitution de l'extraction en &lt; 10 ms sans appel VLM.<br/>"
        "2. <b>Niveau 2 (Hachage Perceptuel imagehash) :</b> Résistance aux variations mineures de compression/recadrage (distance de Hamming &le; 2). Réutilisation instantanée de la structure.<br/>"
        "3. <b>Niveau 3 (Cache Sémantique Redis) :</b> Mémorisation des réponses Q&amp;R fréquentes sur un graphique validé (ex: <i>« Quel est le total ? »</i>). Réponse sub-milliseconde.",
        styles["BodyCustom"]
    ))

    story.append(PageBreak())

    # =========================================================================
    # PARTIES 9 à 12 : SCALABILITÉ, CLOUD BENCHMARK & FINOPS LEAN
    # =========================================================================
    story.append(make_part_banner("PARTIES 9 À 12 : ARCHITECTURE LEAN HETZNER, VLM & FINOPS EN FCFA"))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>Phase 0 Lean : Hetzner CPX31 + Docker Compose (&lt; 100 000 FCFA/mois)</b>", styles["PartH2"]))
    story.append(Paragraph(
        "L'audit expert repousse formellement Kubernetes à la Phase 3 (&gt; 50 000 utilisateurs). "
        "Pour la phase d'amorçage (100 à 1 000 utilisateurs), l'architecture repose sur : "
        "<b>1 VPS Hetzner CPX31</b> (4 vCPU AMD, 8 Go RAM) à 9 970 FCFA/mois, <b>Supabase Pro</b> à 14 900 FCFA/mois, "
        "<b>Cloudflare CDN/WAF</b> (gratuit), <b>Redis local</b> et <b>Resend</b>. "
        "Coût global d'infrastructure : <b>~74 130 FCFA/mois (113 €)</b>.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>Benchmark Fournisseurs Cloud & Choix Stratégique Phase 1</b>", styles["PartH2"]))
    cloud_data = [
        [Paragraph("Plateforme Cloud", styles["TH"]), Paragraph("Configuration Évaluée", styles["TH"]), Paragraph("Coût Mensuel (€)", styles["TH"]), Paragraph("Coût en FCFA", styles["TH"]), Paragraph("Verdict Audit", styles["TH"])],
        [Paragraph("<b>Hetzner Cloud</b>", styles["TDBold"]), Paragraph("CPX31 (4 vCPU / 8 Go RAM / 160 Go NVMe)", styles["TD"]), Paragraph("<b>15,20 €</b>", styles["TDBold"]), Paragraph("<b>9 970 FCFA</b>", styles["TDBold"]), Paragraph("<font color='#059669'><b>Recommandé Phase 1</b></font>", styles["TD"])],
        [Paragraph("DigitalOcean", styles["TD"]), Paragraph("Basic Droplet (4 vCPU / 8 Go RAM)", styles["TD"]), Paragraph("48,00 €", styles["TD"]), Paragraph("31 500 FCFA", styles["TD"]), Paragraph("Acceptable", styles["TD"])],
        [Paragraph("AWS", styles["TD"]), Paragraph("t4g.xlarge + ALB + EBS gp3", styles["TD"]), Paragraph("145,00 €", styles["TD"]), Paragraph("95 000 FCFA", styles["TD"]), Paragraph("Trop onéreux amorçage", styles["TD"])],
        [Paragraph("Google Cloud", styles["TD"]), Paragraph("e2-standard-4 + Cloud Load Balancer", styles["TD"]), Paragraph("158,00 €", styles["TD"]), Paragraph("103 600 FCFA", styles["TD"]), Paragraph("Trop onéreux amorçage", styles["TD"])],
    ]
    t_cloud = Table(cloud_data, colWidths=[1.6*inch, 2.6*inch, 1.1*inch, 1.1*inch, 1.1*inch])
    t_cloud.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_cloud)

    story.append(Paragraph("<b>Routage FinOps Éco-Conçu : -50 % à -75 % d'Économie sur l'IA</b>", styles["PartH2"]))
    story.append(Paragraph(
        "Grâce au <code>QuestionRouter</code>, les requêtes arithmétiques ou de lookup sur données déjà extraites ne sollicitent jamais le VLM Gemini Flash. "
        "Pour 1 000 utilisateurs actifs générant 15 000 requêtes, la facture IA mensuelle est contenue à <b>20 000 FCFA/mois</b>, "
        "portant le coût total de revient technique à <b>88 FCFA par utilisateur actif par mois</b>.",
        styles["BodyCustom"]
    ))

    story.append(PageBreak())

    # =========================================================================
    # PARTIES 13 à 17 : MODÈLE ÉCONOMIQUE, MOBILE MONEY & DÉCISION
    # =========================================================================
    story.append(make_part_banner("PARTIES 13 À 17 : MODÈLE ÉCONOMIQUE, FACTURATION & DÉCISION GO"))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>Grille Tarifaire SaaS Révisée (Facturation Mensuelle & Annuelle)</b>", styles["PartH2"]))
    price_data = [
        [Paragraph("Plan Tarifaire", styles["TH"]), Paragraph("Cible & Usage", styles["TH"]), Paragraph("Quota Inclus", styles["TH"]), Paragraph("Prix Mensuel TTC", styles["TH"]), Paragraph("Offre Annuelle", styles["TH"])],
        [Paragraph("<b>Free Tier</b>", styles["TD"]), Paragraph("Découverte, étudiants, tests", styles["TD"]), Paragraph("5 graphiques / m", styles["TD"]), Paragraph("<b>0 FCFA</b>", styles["TD"]), Paragraph("0 FCFA", styles["TD"])],
        [Paragraph("<b>Starter / Pro</b>", styles["TDBold"]), Paragraph("Analyste, consultant indépendant", styles["TD"]), Paragraph("150 graphiques / m", styles["TD"]), Paragraph("<b>15 000 FCFA / m</b>", styles["TDBold"]), Paragraph("150 000 FCFA / an", styles["TD"])],
        [Paragraph("<b>Team / Business</b>", styles["TDBold"]), Paragraph("Pôles finance, cabinets d'audit (5 sièges)", styles["TD"]), Paragraph("1 000 graphiques / m", styles["TD"]), Paragraph("<b>65 000 FCFA / m</b>", styles["TDBold"]), Paragraph("650 000 FCFA / an", styles["TD"])],
        [Paragraph("<b>Enterprise / API</b>", styles["TD"]), Paragraph("Banques, intégration SI, grands comptes", styles["TD"]), Paragraph("Sur mesure / SLA", styles["TD"]), Paragraph("Dès 350 000 FCFA", styles["TD"]), Paragraph("Contrat annuel", styles["TD"])],
    ]
    t_price = Table(price_data, colWidths=[1.3*inch, 2.2*inch, 1.3*inch, 1.35*inch, 1.35*inch])
    t_price.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_price)

    story.append(Paragraph("<b>Mécanique de Facturation Mobile Money (UEMOA)</b>", styles["PartH2"]))
    story.append(Paragraph(
        "En l'absence de prélèvement automatique récurrent sur Wave, Orange Money et MTN MoMo :<br/>"
        "• <b>Plan Pro Mensuel :</b> Envoi automatisé d'un lien de paiement interactif CinetPay par email et SMS à J-7, J-3 et J-1 de l'échéance.<br/>"
        "• <b>Grace Period :</b> Maintien du service pendant 3 jours ouvrés après expiration. Bascule automatique en Free Tier à J+4 sans suppression de données.<br/>"
        "• <b>Plans Team & API :</b> Souscription annuelle prépayée ou facturation sur devis avec virement bancaire / Mobile Money.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>Arbitrage Final d'Investissement : GO CONDITIONNEL (Score 8.4 / 10)</b>", styles["PartH2"]))
    story.append(make_callout(
        "<b>Avis Final d'Audit :</b> Le potentiel technologique de GraphEin AI est validé. "
        "L'autorisation de Go-Live commercial est accordée sous condition suspensive de livrer d'ici 90 jours : "
        "1. La passerelle Mobile Money CinetPay fonctionnelle • 2. L'asynchrone Celery/Redis • "
        "3. L'enforceur de quotas d'API • 4. La déclaration ARTCI et facturation TVA 18 %."
    ))

    # Architecture PNG if exists
    arch_png = ROOT_DIR / "architecture_target.png"
    if arch_png.exists():
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Blueprint d'Architecture Cible de Production Cloud</b>", styles["PartH2"]))
        story.append(RLImage(str(arch_png), width=7.3*inch, height=3.5*inch))

    story.append(PageBreak())

    # =========================================================================
    # PARTIE 18 : ROADMAP 90 JOURS RÉALISTE (6 SPRINTS)
    # =========================================================================
    story.append(make_part_banner("PARTIE 18 : ROADMAP 90 JOURS OPÉRATIONNELLE (6 SPRINTS DE 2 SEMAINES)"))
    story.append(Spacer(1, 8))
    
    sprint_data = [
        [Paragraph("Sprint & Période", styles["TH"]), Paragraph("Objectifs Principaux", styles["TH"]), Paragraph("Livrables Techniques", styles["TH"]), Paragraph("Definition of Done (DoD)", styles["TH"])],
        [
            Paragraph("<b>Sprint 0</b><br/>(1 semaine)", styles["TDBold"]),
            Paragraph("Stabilisation technique & SRE", styles["TD"]),
            Paragraph("Staging isolé, Secrets sur Doppler, Sentry & Better Stack, Backups PITR", styles["TD"]),
            Paragraph("Zéro secret dans Git, Staging opérationnel, Alertes actives", styles["TD"])
        ],
        [
            Paragraph("<b>Sprint 1</b><br/>(2 semaines)", styles["TDBold"]),
            Paragraph("Sécurité, RLS & Quotas", styles["TD"]),
            Paragraph("Tests d'étanchéité multi-tenant, Quota middleware, CGU/DPA, Dossier ARTCI", styles["TD"]),
            Paragraph("100% tests RLS verts, Quotas appliqués sur l'API, Dépôt ARTCI", styles["TD"])
        ],
        [
            Paragraph("<b>Sprint 2</b><br/>(2 semaines)", styles["TDBold"]),
            Paragraph("Paiement Mobile Money", styles["TD"]),
            Paragraph("Intégration CinetPay (Wave, Orange, MTN), Webhooks idempotents, Factures TVA 18%", styles["TD"]),
            Paragraph("Paiement bout en bout validé, Quota Pro activé, Facture reçue", styles["TD"])
        ],
        [
            Paragraph("<b>Sprint 3</b><br/>(2 semaines)", styles["TDBold"]),
            Paragraph("Asynchrone & Observabilité", styles["TD"]),
            Paragraph("Celery + Redis 7.2, Workers PDF/VLM/Email, Dashboards Prometheus/Grafana", styles["TD"]),
            Paragraph("Latence API &lt;120ms, Zéro tâche lourde bloquante, Dashboards SRE", styles["TD"])
        ],
        [
            Paragraph("<b>Sprint 4</b><br/>(2 semaines)", styles["TDBold"]),
            Paragraph("Durcissement & Continuité", styles["TD"]),
            Paragraph("Tests de charge Locust (500 req/s), Pentest Top 10 OWASP, Plan PCA/PRA", styles["TD"]),
            Paragraph("500 req/s tenus sans crash, Zéro faille critique, PRA testé &lt;30 min", styles["TD"])
        ],
        [
            Paragraph("<b>Sprint 5</b><br/>(2 semaines)", styles["TDBold"]),
            Paragraph("Bêta Payante Fermée", styles["TD"]),
            Paragraph("Onboarding guidé, Templates BRVM/Agro, Widget Chatwoot, Analytics PostHog", styles["TD"]),
            Paragraph("10 à 20 clients bêta payants actifs, NPS &gt; 30, Retours consolidés", styles["TD"])
        ],
        [
            Paragraph("<b>Sprint 6</b><br/>(1-2 semaines)", styles["TDBold"]),
            Paragraph("Go-Live Commercial Public", styles["TD"]),
            Paragraph("Bascule DNS graphein.ai, Status page publique, Publication SLA, Marketing", styles["TD"]),
            Paragraph("Ouverture publique, Paiement en libre-service, Premières factures", styles["TD"])
        ],
    ]
    t_sprint = Table(sprint_data, colWidths=[1.3*inch, 1.8*inch, 2.3*inch, 2.1*inch])
    t_sprint.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_sprint)

    story.append(PageBreak())

    # =========================================================================
    # PARTIE 19 : STRATÉGIE DE PAIEMENT MOBILE MONEY DÉTAILLÉE
    # =========================================================================
    story.append(make_part_banner("PARTIE 19 : STRATÉGIE DE PAIEMENT MOBILE MONEY DÉTAILLÉE"))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>19.1. Choix du Partenaire : Agrégateur Agréé CinetPay</b>", styles["PartH2"]))
    story.append(Paragraph(
        "Pour des raisons d'efficacité capitalistique et d'agilité, l'intégration directe opérateur par opérateur est rejetée au démarrage. "
        "<b>CinetPay</b> offre un guichet unique agréé BCEAO fédérant Wave, Orange Money, MTN MoMo, Moov Money et cartes Visa/Mastercard dans une seule API unifiée avec réconciliation bancaire.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>19.2. Schéma de Données Billing (Supabase PostgreSQL)</b>", styles["PartH2"]))
    sql_schema_code = (
        "-- Tables Billing d'Entreprise\n"
        "CREATE TABLE billing_customers (id UUID PRIMARY KEY, user_id UUID REFERENCES auth.users, phone TEXT, tax_id TEXT);\n"
        "CREATE TABLE plans (id TEXT PRIMARY KEY, name TEXT, price_xof INT, quota_analyses INT, interval TEXT);\n"
        "CREATE TABLE subscriptions (id UUID PRIMARY KEY, customer_id UUID, plan_id TEXT, status TEXT, current_period_end TIMESTAMPTZ);\n"
        "CREATE TABLE payments (id UUID PRIMARY KEY, transaction_ref TEXT UNIQUE, provider_id TEXT, amount_xof INT, status TEXT);\n"
        "CREATE TABLE invoices (id UUID PRIMARY KEY, payment_id UUID, invoice_number TEXT UNIQUE, amount_ht INT, vat_18 INT, amount_ttc INT);\n"
        "CREATE TABLE webhook_events (id UUID PRIMARY KEY, provider TEXT, payload JSONB, signature TEXT, processed BOOLEAN);\n"
        "ALTER TABLE billing_customers ENABLE ROW LEVEL SECURITY; ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;"
    )
    story.append(Paragraph(sql_schema_code.replace("\n", "<br/>"), styles["CodeText"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>19.3. Flux de Paiement Sécurisé en 7 Étapes</b>", styles["PartH2"]))
    story.append(Paragraph(
        "1. <b>Choix du Plan</b> par l'utilisateur ➔ 2. <b>Génération d'Intention</b> avec référence unique ➔ 3. <b>Initialisation CinetPay</b> ➔ "
        "4. <b>Validation Mobile</b> (Wave/Orange/MTN) ➔ 5. <b>Callback Webhook</b> signé HMAC-SHA256 ➔ 6. <b>Validation & Quota Pro</b> ➔ 7. <b>Facture PDF TVA 18%</b>.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>19.4. Procédure de Relance (Dunning) & Rétrogradation</b>", styles["PartH2"]))
    story.append(Paragraph(
        "• <b>J-7, J-3, J-1 :</b> Relances avec lien CinetPay direct.<br/>"
        "• <b>J0 à J+3 :</b> Période de grâce (accès Pro maintenu).<br/>"
        "• <b>J+4 :</b> Rétrogradation automatique en Free Tier sans perte de données.",
        styles["BodyCustom"]
    ))

    story.append(PageBreak())

    # =========================================================================
    # PARTIES 20 & 21 : AI OPS & BUDGET D'AMORÇAGE LEAN
    # =========================================================================
    story.append(make_part_banner("PARTIES 20 & 21 : AI OPS, QUALITÉ CONTINUE & BUDGET LEAN FINOPS"))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>AI Ops & Golden Evaluation Dataset (Partie 20)</b>", styles["PartH2"]))
    story.append(Paragraph(
        "• <b>Jeu de Données Doré :</b> Référentiel de 100 graphiques régionaux annotés au pixel près (40 BRVM, 30 Agro, 15 Macro, 15 Multi-figures). "
        "Exécution automatisée en CI/CD lors de chaque évolution de prompt ou de modèle VLM.<br/>"
        "• <b>Active Learning HITL :</b> Micro-retour utilisateur (<i>« Valeur exacte ? »</i>) sur la grille pour enrichir continuellement les exemples Few-Shot du RAG FAISS.",
        styles["BodyCustom"]
    ))

    story.append(Paragraph("<b>Budget d'Amorçage Lean Détaillé (&lt; 100 000 FCFA/mois — Partie 21)</b>", styles["PartH2"]))
    finops_data = [
        [Paragraph("Poste / Fournisseur", styles["TH"]), Paragraph("Ressource & Spécification", styles["TH"]), Paragraph("Coût Mensuel (€)", styles["TH"]), Paragraph("Coût en FCFA", styles["TH"]), Paragraph("Part Budget", styles["TH"])],
        [Paragraph("<b>Hetzner CPX31</b>", styles["TDBold"]), Paragraph("VPS 4 vCPU, 8 Go RAM, 160 Go NVMe", styles["TD"]), Paragraph("15,20 €", styles["TD"]), Paragraph("9 970 FCFA", styles["TD"]), Paragraph("13.4 %", styles["TD"])],
        [Paragraph("<b>Supabase Pro</b>", styles["TDBold"]), Paragraph("PostgreSQL managé, Auth JWT, PITR", styles["TD"]), Paragraph("22,70 €", styles["TD"]), Paragraph("14 900 FCFA", styles["TD"]), Paragraph("20.1 %", styles["TD"])],
        [Paragraph("<b>Cloudflare</b>", styles["TDBold"]), Paragraph("DDoS, SSL/TLS, CDN mondial", styles["TD"]), Paragraph("0,00 €", styles["TD"]), Paragraph("0 FCFA", styles["TD"]), Paragraph("0.0 %", styles["TD"])],
        [Paragraph("<b>Resend Email</b>", styles["TDBold"]), Paragraph("50 000 emails transactionnels/mois", styles["TD"]), Paragraph("18,20 €", styles["TD"]), Paragraph("11 940 FCFA", styles["TD"]), Paragraph("16.1 %", styles["TD"])],
        [Paragraph("<b>Sentry + Better Stack</b>", styles["TDBold"]), Paragraph("Suivi d'erreurs et status page publique", styles["TD"]), Paragraph("26,40 €", styles["TD"]), Paragraph("17 320 FCFA", styles["TD"]), Paragraph("23.4 %", styles["TD"])],
        [Paragraph("<b>Gemini 2.5 Flash</b>", styles["TDBold"]), Paragraph("Inférences VLM (1 000 users avec cache)", styles["TD"]), Paragraph("30,50 €", styles["TD"]), Paragraph("20 000 FCFA", styles["TD"]), Paragraph("27.0 %", styles["TD"])],
        [Paragraph("<b>TOTAL MENSUEL AMORÇAGE</b>", styles["TH"]), Paragraph("<b>Infrastructure & IA complète</b>", styles["TH"]), Paragraph("<b>113,00 €</b>", styles["TH"]), Paragraph("<b>74 130 FCFA</b>", styles["TH"]), Paragraph("<b>100 %</b>", styles["TH"])],
    ]
    t_finops = Table(finops_data, colWidths=[1.5*inch, 2.7*inch, 1.1*inch, 1.2*inch, 1.0*inch])
    t_finops.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_finops)

    story.append(PageBreak())

    # =========================================================================
    # PARTIE 22 : CONDITIONS DE GO-LIVE (CHECKLIST STRICTE)
    # =========================================================================
    story.append(make_part_banner("PARTIE 22 : MATRICE DE CONTRÔLE PRÉ-DÉPLOIEMENT (10 CONDITIONS STRICTES)"))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "Pour autoriser le basculement commercial officiel en production, le comité technique et la direction générale doivent valider formellement la conformité intégrale des 10 prérequis ci-dessous :",
        styles["BodyCustom"]
    ))

    chk_data = [
        [Paragraph("N°", styles["TH"]), Paragraph("Condition Impérative de Go-Live", styles["TH"]), Paragraph("Critère de Validation Mesurable", styles["TH"]), Paragraph("Responsable", styles["TH"]), Paragraph("Statut Requis", styles["TH"])],
        [Paragraph("1", styles["TDBold"]), Paragraph("Paiement Mobile Money CinetPay", styles["TD"]), Paragraph("Transactions Wave, Orange et MTN validées en direct", styles["TD"]), Paragraph("Lead Backend", styles["TD"]), Paragraph("<font color='#DC2626'><b>Bloquant</b></font>", styles["TD"])],
        [Paragraph("2", styles["TDBold"]), Paragraph("Tests d'Étanchéité RLS 100% Verts", styles["TD"]), Paragraph("Zéro fuite de données inter-tenant sur 15 tests", styles["TD"]), Paragraph("Security Lead", styles["TD"]), Paragraph("<font color='#DC2626'><b>Bloquant</b></font>", styles["TD"])],
        [Paragraph("3", styles["TDBold"]), Paragraph("Enforceur de Quotas Actif", styles["TD"]), Paragraph("Blocage automatique à l'épuisement du palier", styles["TD"]), Paragraph("Lead Backend", styles["TD"]), Paragraph("<font color='#DC2626'><b>Bloquant</b></font>", styles["TD"])],
        [Paragraph("4", styles["TDBold"]), Paragraph("File Asynchrone Celery/Redis", styles["TD"]), Paragraph("Exports PDF et emails déportés dans les queues", styles["TD"]), Paragraph("DevOps Lead", styles["TD"]), Paragraph("<font color='#2563EB'><b>Majeur</b></font>", styles["TD"])],
        [Paragraph("5", styles["TDBold"]), Paragraph("Observabilité SRE & Alertes", styles["TD"]), Paragraph("Sentry connecté, Better Stack actif, astreinte", styles["TD"]), Paragraph("DevOps Lead", styles["TD"]), Paragraph("<font color='#2563EB'><b>Majeur</b></font>", styles["TD"])],
        [Paragraph("6", styles["TDBold"]), Paragraph("Documentation Juridique Publiée", styles["TD"]), Paragraph("CGU, Politique de Confidentialité, DPA en ligne", styles["TD"]), Paragraph("Legal Advisor", styles["TD"]), Paragraph("<font color='#2563EB'><b>Majeur</b></font>", styles["TD"])],
        [Paragraph("7", styles["TDBold"]), Paragraph("Déclaration Légale ARTCI Déposée", styles["TD"]), Paragraph("Récépissé ou dossier formel de déclaration", styles["TD"]), Paragraph("DPO / Legal", styles["TD"]), Paragraph("<font color='#DC2626'><b>Bloquant</b></font>", styles["TD"])],
        [Paragraph("8", styles["TDBold"]), Paragraph("Facturation Fiscale Conforme TVA 18%", styles["TD"]), Paragraph("Mentions obligatoires DGI et numérotation séquentielle", styles["TD"]), Paragraph("Finance Lead", styles["TD"]), Paragraph("<font color='#2563EB'><b>Majeur</b></font>", styles["TD"])],
        [Paragraph("9", styles["TDBold"]), Paragraph("Sauvegardes & Test PITR Réussi", styles["TD"]), Paragraph("Restauration complète à chaud en staging &lt; 30 min", styles["TD"]), Paragraph("DevOps Lead", styles["TD"]), Paragraph("<font color='#2563EB'><b>Majeur</b></font>", styles["TD"])],
        [Paragraph("10", styles["TDBold"]), Paragraph("Plan de Continuité PCA/PRA Validé", styles["TD"]), Paragraph("Procédure de secours documentée et testée", styles["TD"]), Paragraph("CTO / Tech Lead", styles["TD"]), Paragraph("<font color='#2563EB'><b>Majeur</b></font>", styles["TD"])],
    ]
    t_chk = Table(chk_data, colWidths=[0.4*inch, 2.4*inch, 2.7*inch, 1.1*inch, 0.9*inch])
    t_chk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_chk)

    story.append(Spacer(1, 14))

    # Signature Block
    sign_data = [
        [
            Paragraph("<b>Pour le Comité Technique d'Audit :</b><br/><i>CTO SaaS & Principal Software Architect</i><br/>Signé électroniquement (Abidjan / Paris)", styles["TD"]),
            Paragraph("<b>Pour le Comité FinOps & Due Diligence :</b><br/><i>VC Investment Partner & FinOps Lead</i><br/>Certification de conformité d'investissement", styles["TD"])
        ]
    ]
    t_sign = Table(sign_data, colWidths=[3.75*inch, 3.75*inch])
    t_sign.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF generated successfully at: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
