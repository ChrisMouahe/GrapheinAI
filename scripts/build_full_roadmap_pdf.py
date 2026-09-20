"""Master ReportLab PDF Builder generating the full multi-page Strategic Roadmap in FCFA."""

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PDF = ROOT_DIR / "roadmap_production.pdf"

class NumberedCanvas(canvas.Canvas):
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
            if self._pageNumber > 1:
                self.saveState()
                self.setFont("Helvetica-Bold", 8)
                self.setFillColor(colors.HexColor("#64748B"))
                self.drawString(36, 11 * 72 - 30, "LUMICHART AI — FEUILLE DE ROUTE STRATÉGIQUE & ROADMAP R&D")
                self.drawRightString(8.5 * 72 - 36, 11 * 72 - 30, "CONFIDENTIEL (FCFA)")
                self.setStrokeColor(colors.HexColor("#CBD5E1"))
                self.setLineWidth(0.5)
                self.line(36, 11 * 72 - 34, 8.5 * 72 - 36, 11 * 72 - 34)
                self.line(36, 40, 8.5 * 72 - 36, 40)
                self.setFont("Helvetica", 8)
                self.drawString(36, 28, "© 2026 LumiChart Inc. — Roadmap Stratégique de Production (Côte d'Ivoire / International)")
                self.drawRightString(8.5 * 72 - 36, 28, f"Page {self._pageNumber} / {num_pages}")
                self.restoreState()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


def build_roadmap():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )
    styles = getSampleStyleSheet()
    c_primary = colors.HexColor("#0F172A")
    c_secondary = colors.HexColor("#1E3A8A")
    c_accent = colors.HexColor("#2563EB")
    c_text = colors.HexColor("#1E293B")

    styles.add(ParagraphStyle("RTitle", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=colors.white, spaceAfter=8))
    styles.add(ParagraphStyle("RSub", fontName="Helvetica", fontSize=11, leading=15, textColor=colors.HexColor("#93C5FD"), spaceAfter=14))
    styles.add(ParagraphStyle("RH1", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=c_secondary, spaceBefore=12, spaceAfter=6, keepWithNext=True))
    styles.add(ParagraphStyle("RH2", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=c_accent, spaceBefore=8, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle("RBody", fontName="Helvetica", fontSize=8.5, leading=12, textColor=c_text, spaceAfter=5))
    styles.add(ParagraphStyle("RBullet", fontName="Helvetica", fontSize=8.5, leading=12, textColor=c_text, leftIndent=12, firstLineIndent=-8, spaceAfter=3))
    styles.add(ParagraphStyle("RTH", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.white, alignment=1))
    styles.add(ParagraphStyle("RTD", fontName="Helvetica", fontSize=7.5, leading=10, textColor=c_text))
    styles.add(ParagraphStyle("RTDBold", fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=c_text))

    story = []

    # Header Card
    h_data = [
        [Paragraph("<b>LUMICHART AI — FEUILLE DE ROUTE STRATÉGIQUE & PLAN DE DÉPLOIEMENT R&D</b>", styles["RTitle"])],
        [Paragraph("Plan d'Ingénierie, de Sécurité et d'Expansion Commerciale (1 mois à 24 mois) • Contexte Ivoirien & International", styles["RSub"])],
        [Paragraph("<b>Auteurs :</b> Direction Technique (CTO, Principal Architect, Senior MLOps) | <b>Devise de Référence :</b> Franc CFA (XOF)", 
                   ParagraphStyle('HMeta', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#E2E8F0')))]
    ]
    t_h = Table(h_data, colWidths=[7.5*inch])
    t_h.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_primary),
        ('PADDING', (0,0), (-1,-1), 18),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_h)
    story.append(Spacer(1, 10))

    # Phase 1
    story.append(Paragraph("<b>PHASE 1 : MOIS 1 À MOIS 3 — FONDATIONS DE PRODUCTION & PAIEMENTS LOCAUX</b>", styles["RH1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceAfter=6))
    story.append(Paragraph("<b>Objectif :</b> Sécuriser l'infrastructure critique, déporter les calculs lourds et ouvrir les canaux d'acquisition B2B en Côte d'Ivoire.", styles["RBody"]))

    p1_data = [
        [Paragraph("Chantier / Livrable", styles["RTH"]), Paragraph("Description Technique Détaillée", styles["RTH"]), Paragraph("Impact Métier", styles["RTH"]), Paragraph("Échéance", styles["RTH"])],
        [Paragraph("Paiements Mobile Money", styles["RTDBold"]), Paragraph("Intégration des APIs Wave, Orange Money et MTN MoMo via passerelle unifiée (CinetPay/Stripe)", styles["RTD"]), Paragraph("Conversion immédiate des utilisateurs B2B et pros en Côte d'Ivoire et zone UEMOA", styles["RTD"]), Paragraph("Mois 1", styles["RTD"])],
        [Paragraph("Workers Asynchrones Celery", styles["RTDBold"]), Paragraph("Migration du traitement d'image OpenCV, calculs AST et génération PDF vers file Redis Celery", styles["RTD"]), Paragraph("API REST 100% disponible, suppression des risques de blocage I/O", styles["RTD"]), Paragraph("Mois 1.5", styles["RTD"])],
        [Paragraph("Gestionnaire de Secrets", styles["RTDBold"]), Paragraph("Déploiement de Doppler / HashiCorp Vault pour la rotation automatique des clés d'API", styles["RTD"]), Paragraph("Élimination des risques de fuite d'identifiants de production", styles["RTD"]), Paragraph("Mois 2", styles["RTD"])],
        [Paragraph("SDKs Développeurs V1", styles["RTDBold"]), Paragraph("Publication des bibliothèques clientes officielles Python (`graphein-ai`) et TypeScript", styles["RTD"]), Paragraph("Intégration fluide dans les systèmes d'information des banques et startups", styles["RTD"]), Paragraph("Mois 3", styles["RTD"])],
    ]
    t_p1 = Table(p1_data, colWidths=[1.6*inch, 2.7*inch, 2.3*inch, 0.9*inch])
    t_p1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_p1)

    story.append(Spacer(1, 8))
    # Phase 2
    story.append(Paragraph("<b>PHASE 2 : MOIS 3 À MOIS 6 — SÉCURITÉ GRAND COMPTE & INTÉGRATIONS BI</b>", styles["RH1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceAfter=6))
    story.append(Paragraph("<b>Objectif :</b> Répondre aux exigences des banques, assurances et institutions publiques avec SSO et certifications.", styles["RBody"]))

    p2_data = [
        [Paragraph("Chantier / Livrable", styles["RTH"]), Paragraph("Description Technique Détaillée", styles["RTH"]), Paragraph("Impact Métier", styles["RTH"]), Paragraph("Échéance", styles["RTH"])],
        [Paragraph("SSO d'Entreprise SAML 2.0", styles["RTDBold"]), Paragraph("Connexion centralisée Okta, Azure Active Directory / Microsoft Entra ID et Google Workspace", styles["RTD"]), Paragraph("Adoption fluide par les DSI des grands comptes sans gestion de mot de passe", styles["RTD"]), Paragraph("Mois 4", styles["RTD"])],
        [Paragraph("Conformité ARTCI & SOC2", styles["RTDBold"]), Paragraph("Audit de conformité avec l'autorité ivoirienne (ARTCI) et préparation SOC2 Type 1", styles["RTD"]), Paragraph("Éligibilité aux appels d'offres bancaires et institutionnels régionaux", styles["RTD"]), Paragraph("Mois 5", styles["RTD"])],
        [Paragraph("Connecteurs Power BI & Tableau", styles["RTDBold"]), Paragraph("Plugin d'export direct et de synchronisation dynamique vers les dashboards de Business Intelligence", styles["RTD"]), Paragraph("Intégration directe dans les flux de travail existants des analystes", styles["RTD"]), Paragraph("Mois 6", styles["RTD"])],
        [Paragraph("Ingestion Multi-Pages PDF", styles["RTDBold"]), Paragraph("Analyse automatique de rapports complets de 50+ pages avec détection de 20+ graphiques", styles["RTD"]), Paragraph("Gain de temps massif sur le dépouillement de bilans financiers complets", styles["RTD"]), Paragraph("Mois 6", styles["RTD"])],
    ]
    t_p2 = Table(p2_data, colWidths=[1.6*inch, 2.7*inch, 2.3*inch, 0.9*inch])
    t_p2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_p2)

    story.append(PageBreak())

    # Phase 3 & 4
    story.append(Paragraph("<b>PHASE 3 : MOIS 6 À MOIS 12 — INFÉRENCE SOUVERAINE ON-PREMISE</b>", styles["RH1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceAfter=6))
    story.append(Paragraph("<b>Objectif :</b> Déployer l'IA dans les environnements fermés (Défense, Banques Centrales, Ministères) sans dépendance cloud.", styles["RBody"]))

    p3_data = [
        [Paragraph("Chantier / Livrable", styles["RTH"]), Paragraph("Description Technique Détaillée", styles["RTH"]), Paragraph("Impact Métier", styles["RTH"]), Paragraph("Échéance", styles["RTH"])],
        [Paragraph("Moteur On-Premise Mistral", styles["RTDBold"]), Paragraph("Conteneurisation de Mistral Pixtral 12B sur serveur GPU local (NVIDIA L4 / A10G) avec vLLM", styles["RTD"]), Paragraph("Confinement total des données pour secret bancaire et défense nationale", styles["RTD"]), Paragraph("Mois 9", styles["RTD"])],
        [Paragraph("Chiffrement BYOK (Clé Client)", styles["RTDBold"]), Paragraph("Gestion des clés de chiffrement de bout en bout directement par le client", styles["RTD"]), Paragraph("Garantie absolue de confidentialité sur les données sensibles", styles["RTD"]), Paragraph("Mois 10", styles["RTD"])],
        [Paragraph("Marketplace Partenaires", styles["RTDBold"]), Paragraph("Portail pour intégrateurs certifiés et cabinets d'audit déployant LumiChart", styles["RTD"]), Paragraph("Effet de levier commercial et expansion indirecte en zone CEDEAO", styles["RTD"]), Paragraph("Mois 12", styles["RTD"])],
    ]
    t_p3 = Table(p3_data, colWidths=[1.6*inch, 2.7*inch, 2.3*inch, 0.9*inch])
    t_p3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_p3)

    story.append(Spacer(1, 8))
    # Phase 4
    story.append(Paragraph("<b>PHASE 4 : MOIS 12 À MOIS 24 — LEADERSHIP MONDIAL & VLM PROPRIÉTAIRE</b>", styles["RH1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceAfter=6))
    story.append(Paragraph("<b>Objectif :</b> Créer un actif technologique propriétaire de rupture et conquérir les marchés anglophones et mondiaux.", styles["RBody"]))

    p4_data = [
        [Paragraph("Chantier / Livrable", styles["RTH"]), Paragraph("Description Technique Détaillée", styles["RTH"]), Paragraph("Impact Métier", styles["RTH"]), Paragraph("Échéance", styles["RTH"])],
        [Paragraph("Fine-Tuning VLM GraphEin-V1", styles["RTDBold"]), Paragraph("Entraînement d'un modèle de fondation spécialisé sur 10 millions de paires graphiques annotées", styles["RTD"]), Paragraph("Moat technologique inattaquable et réduction de 90% des coûts d'API tiers", styles["RTD"]), Paragraph("Mois 18", styles["RTD"])],
        [Paragraph("Simulation Prédictive What-If", styles["RTDBold"]), Paragraph("Moteur interactif modifiant directement les courbes pour générer des prévisions instantanées", styles["RTD"]), Paragraph("Transformation de l'outil d'analyse rétrospective en copilote prédictif", styles["RTD"]), Paragraph("Mois 20", styles["RTD"])],
        [Paragraph("Expansion Internationale", styles["RTDBold"]), Paragraph("Déploiement commercial au Nigeria, Ghana, Kenya, France et Amérique du Nord", styles["RTD"]), Paragraph("Atteinte de 2.75 Milliards FCFA d'ARR en fin d'Année 3", styles["RTD"]), Paragraph("Mois 24", styles["RTD"])],
    ]
    t_p4 = Table(p4_data, colWidths=[1.6*inch, 2.7*inch, 2.3*inch, 0.9*inch])
    t_p4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_p4)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Full Roadmap PDF in FCFA generated successfully: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_roadmap()
