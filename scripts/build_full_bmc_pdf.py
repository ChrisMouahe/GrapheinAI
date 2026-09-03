"""Master ReportLab PDF Builder generating the comprehensive multi-page Business Model Canvas & Financial Strategy in FCFA."""

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
OUTPUT_PDF = ROOT_DIR / "business_model_canvas.pdf"

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
                self.drawString(36, 11 * 72 - 30, "GRAPHEIN AI — BUSINESS MODEL CANVAS & STRATÉGIE FINANCIÈRE")
                self.drawRightString(8.5 * 72 - 36, 11 * 72 - 30, "CONFIDENTIEL (FCFA)")
                self.setStrokeColor(colors.HexColor("#CBD5E1"))
                self.setLineWidth(0.5)
                self.line(36, 11 * 72 - 34, 8.5 * 72 - 36, 11 * 72 - 34)
                self.line(36, 40, 8.5 * 72 - 36, 40)
                self.setFont("Helvetica", 8)
                self.drawString(36, 28, "© 2026 GraphEin AI Inc. — Analyse de Monétisation en Franc CFA (XOF)")
                self.drawRightString(8.5 * 72 - 36, 28, f"Page {self._pageNumber} / {num_pages}")
                self.restoreState()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


def build_bmc():
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

    styles.add(ParagraphStyle("BTitle", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=colors.white, spaceAfter=8))
    styles.add(ParagraphStyle("BSub", fontName="Helvetica", fontSize=11, leading=15, textColor=colors.HexColor("#93C5FD"), spaceAfter=14))
    styles.add(ParagraphStyle("BH1", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=c_secondary, spaceBefore=12, spaceAfter=6, keepWithNext=True))
    styles.add(ParagraphStyle("BH2", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=c_accent, spaceBefore=8, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle("BBody", fontName="Helvetica", fontSize=8.5, leading=12, textColor=c_text, spaceAfter=5))
    styles.add(ParagraphStyle("BBullet", fontName="Helvetica", fontSize=8.5, leading=12, textColor=c_text, leftIndent=12, firstLineIndent=-8, spaceAfter=3))
    styles.add(ParagraphStyle("BTH", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.white, alignment=1))
    styles.add(ParagraphStyle("BTD", fontName="Helvetica", fontSize=7.5, leading=10, textColor=c_text))
    styles.add(ParagraphStyle("BTDBold", fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=c_text))

    story = []

    # Header Card
    h_data = [
        [Paragraph("<b>GRAPHEIN AI — BUSINESS MODEL CANVAS STRATÉGIQUE & MODÈLE FINANCIER</b>", styles["BTitle"])],
        [Paragraph("Modélisation Approfondie de la Monétisation, Canaux Locaux (Mobile Money) & Unit Economics en Franc CFA (XOF)", styles["BSub"])],
        [Paragraph("<b>Auteurs :</b> Direction Stratégique, Business Analyst & VC Advisory | <b>Parité Fixe :</b> 1 EUR = 655,957 FCFA", 
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

    # Matrice BMC Visuelle
    story.append(Paragraph("<b>1. MATRICE SYNTHÉTIQUE BUSINESS MODEL CANVAS</b>", styles["BH1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceAfter=6))

    bmc_matrix = [
        [
            Paragraph("<b>Partenaires Clés</b><br/>• Google GenAI (API Gemini)<br/>• Supabase (PostgreSQL HA)<br/>• Passerelles Mobile Money (Wave, Orange, CinetPay)<br/>• Banques & Bourse BRVM<br/>• Cabinets de Conseil", styles["BTD"]),
            Paragraph("<b>Activités Clés</b><br/>• R&D Vision & Moteur AST<br/>• Zéro Hallucination Math<br/>• Développement API & SDKs<br/>• Support Client & Sécurité", styles["BTD"]),
            Paragraph("<b>Proposition de Valeur</b><br/>• <b>100% de fiabilité mathématique</b> (0 hallucination)<br/>• Extraction en 1 clic vers Excel/PDF<br/>• Workspaces collaboratifs<br/>• Prix en FCFA adaptés", styles["BTDBold"]),
            Paragraph("<b>Relations Clients</b><br/>• Product-Led Growth (Freemium)<br/>• Onboarding B2B Entreprises<br/>• Documentation Swagger & SDKs<br/>• Support réactif WhatsApp/Email", styles["BTD"]),
            Paragraph("<b>Segments Clients</b><br/>• Banques & Sociétés de Bourse<br/>• Filières agro-industrielles<br/>• Cabinets d'audit & conseil<br/>• Directions Finance & BI<br/>• Développeurs Logiciels", styles["BTD"])
        ],
        [
            Paragraph("<b>Ressources Clés</b><br/>• Algorithmes brevetables AST<br/>• Dataset de Ground Truth<br/>• Équipe d'ingénieurs IA<br/>• Marque & Infrastructure", styles["BTD"]),
            Paragraph("<b>Canaux de Distribution</b><br/>• Plateforme SaaS Web directe<br/>• Réseau d'intégrateurs IT<br/>• Salons Fintech (Abidjan)<br/>• Plugins Power BI / Tableau", styles["BTD"]),
            Paragraph("<b>Structure de Coûts (FinOps)</b><br/>• Inférence Gemini (~2 FCFA/req.)<br/>• Serveurs K8s & Supabase HA<br/>• Salaires R&D & Sales B2B<br/>• Marketing & Partenariats", styles["BTD"]),
            Paragraph("<b>Flux de Revenus en FCFA</b><br/>• <b>Pro :</b> 19 000 FCFA / mois<br/>• <b>Team :</b> 65 000 FCFA / mois<br/>• <b>Enterprise :</b> Dès 650 000 FCFA<br/>• <b>API :</b> 35 FCFA / requête", styles["BTDBold"]),
            Paragraph("<b>Unit Economics Cibles</b><br/>• CAC : 118 000 FCFA<br/>• LTV : 950 000 FCFA (LTV/CAC > 8x)<br/>• Marge Brute Infra : > 97%<br/>• Payback : < 5 mois", styles["BTD"])
        ]
    ]
    t_bmc = Table(bmc_matrix, colWidths=[1.5*inch]*5)
    t_bmc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1.5, c_secondary),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#EFF6FF')),
        ('BACKGROUND', (3,1), (3,1), colors.HexColor('#ECFDF5')),
    ]))
    story.append(t_bmc)

    story.append(PageBreak())

    # Analyse Approfondie des Piliers
    story.append(Paragraph("<b>2. ANALYSE APPROFONDIE DES PILIERS COMMERCIAUX EN ZONE UEMOA</b>", styles["BH1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceAfter=6))

    story.append(Paragraph("<b>2.1. Stratégie d'Acquisition & Intégration Mobile Money</b>", styles["BH2"]))
    story.append(Paragraph(
        "En Côte d'Ivoire et en Afrique de l'Ouest, le taux de pénétration des cartes bancaires internationales reste sous les 15%, "
        "tandis que le Mobile Money (Wave, Orange Money, MTN MoMo, Moov Money) dépasse les 80% d'usage actif. "
        "GraphEin AI intègre nativement ces moyens de paiement locaux, réduisant le taux de friction à l'inscription payante de plus de 70% "
        "par rapport aux solutions SaaS étrangères (qui imposent Stripe avec carte bancaire US/EU).",
        styles["BBody"]
    ))

    story.append(Paragraph("<b>2.2. Unit Economics & Rentabilité Client (LTV / CAC)</b>", styles["BH2"]))
    unit_data = [
        [Paragraph("Indicateur Économique", styles["BTH"]), Paragraph("Valeur en Franc CFA", styles["BTH"]), Paragraph("Interprétation & Benchmarks SaaS B2B", styles["BTH"])],
        [Paragraph("Coût d'Acquisition Client (CAC)", styles["BTDBold"]), Paragraph("118 000 FCFA (~180 €)", styles["BTD"]), Paragraph("Campagnes ciblées LinkedIn B2B, salons professionnels et bouche-à-oreille", styles["BTD"])],
        [Paragraph("Valeur Vie Client Moyenne (LTV)", styles["BTDBold"]), Paragraph("950 000 FCFA (~1 450 €)", styles["BTD"]), Paragraph("Calculée sur une durée de rétention moyenne de 28 mois (Churn mensuel < 2.5%)", styles["BTD"])],
        [Paragraph("Ratio LTV / CAC", styles["BTDBold"]), Paragraph("<b>8.05 x</b>", styles["BTDBold"]), Paragraph("Excellence opérationnelle (le standard de l'industrie B2B est supérieur à 3.0x)", styles["BTD"])],
        [Paragraph("Délai de Récupération (Payback)", styles["BTDBold"]), Paragraph("<b>4.2 mois</b>", styles["BTDBold"]), Paragraph("Le client rembourse son coût d'acquisition en moins d'un semestre", styles["BTD"])],
        [Paragraph("Marge Brute d'Infrastructure", styles["BTDBold"]), Paragraph("<b>97.9% à 98.7%</b>", styles["BTDBold"]), Paragraph("Coût de revient serveur et API VLM inférieur à 360 FCFA / user / mois", styles["BTD"])],
    ]
    t_unit = Table(unit_data, colWidths=[2.2*inch, 1.8*inch, 3.5*inch])
    t_unit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_unit)

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>2.3. Projections Financières Triennales Consolidées (FCFA)</b>", styles["BH2"]))
    story.append(Paragraph(
        "• <b>Année 1 :</b> 1 500 utilisateurs actifs $\\rightarrow$ <b>ARR : 60 350 000 FCFA</b> | Coût Infra : 4.3 M FCFA | <b>Marge Nette : 92.8%</b>.<br/>"
        "• <b>Année 2 :</b> 12 000 utilisateurs + 15 Enterprise $\\rightarrow$ <b>ARR : 551 000 000 FCFA</b> | Coût Infra : 35.6 M FCFA | <b>EBITDA : 38%</b>.<br/>"
        "• <b>Année 3 :</b> 65 000 utilisateurs + 60 Enterprise $\\rightarrow$ <b>ARR : 2 755 000 000 FCFA</b> *(2.75 Milliards FCFA)* | <b>EBITDA : 42%</b>.",
        styles["BBody"]
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Full Business Model Canvas PDF in FCFA generated successfully: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_bmc()
