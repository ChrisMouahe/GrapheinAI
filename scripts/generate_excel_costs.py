"""Generate professional Excel workbook for GraphEin AI cost estimation across 100, 1k, 10k, and 100k users in FCFA (Franc CFA / Contexte Ivoirien)."""

import sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT_DIR / "cost_estimation.xlsx"

# Taux de conversion officiel EUR -> FCFA (XOF)
RATE_EUR_FCFA = 655.957

def fcfa(eur_val: float) -> float:
    return round(eur_val * RATE_EUR_FCFA)

def create_cost_workbook():
    wb = openpyxl.Workbook()
    
    # Styles
    navy_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    dark_slate = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    subtotal_fill = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid")
    light_gray_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    font_title = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
    font_section = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_subtotal = Font(name="Calibri", size=10, bold=True, color="1E3A8A")
    font_bold = Font(name="Calibri", size=10, bold=True, color="000000")
    font_normal = Font(name="Calibri", size=10, color="000000")
    font_kpi_num = Font(name="Calibri", size=12, bold=True, color="1E3A8A")

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )
    double_bottom_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="double", color="1E3A8A"),
    )

    # -------------------------------------------------------------------------
    # SHEET 1: Synthèse Comparative & FinOps (En FCFA)
    # -------------------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Synthèse_Financière_FCFA"
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1.merge_cells("A1:G2")
    ws1["A1"] = "GRAPHEIN AI — MODÉLISATION FINANCIÈRE & FINOPS EN FCFA (CONTEXTE IVOIRIEN & UEMOA)"
    ws1["A1"].font = font_title
    ws1["A1"].fill = dark_slate
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")

    headers1 = [
        "Poste de Coût / Infrastructure",
        "Hypothèses Techniques & Fournisseur",
        "Scénario 1 (100 Users)",
        "Scénario 2 (1 000 Users)",
        "Scénario 3 (10 000 Users)",
        "Scénario 4 (100 000 Users)",
        "Type de Coût",
    ]
    for col_num, h in enumerate(headers1, 1):
        cell = ws1.cell(row=4, column=col_num)
        cell.value = h
        cell.font = font_header
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws1.row_dimensions[4].height = 28

    cost_items_eur = [
        ("Serveurs API / Workers ASGI", "Hetzner Cloud / AWS EKS K8s autoscale", 25.00, 120.00, 850.00, 4800.00, "Fixe / Échelonné"),
        ("Base de Données PostgreSQL", "Supabase Pro HA / AWS RDS Multi-AZ", 25.00, 60.00, 350.00, 1900.00, "Fixe / Échelonné"),
        ("Stockage Objets (Images & PDF)", "Cloudflare R2 / S3 standard (0€ egress)", 5.00, 15.00, 120.00, 950.00, "Variable (Go)"),
        ("Réseau, CDN & WAF Sécurité", "Cloudflare Pro / Enterprise DDoS + SSL", 20.00, 20.00, 200.00, 1500.00, "Fixe / Échelonné"),
        ("Redis & File de Tâches Celery", "Redis Enterprise / Upstash HA Cluster", 10.00, 35.00, 180.00, 850.00, "Fixe / Échelonné"),
        ("API LLM/VLM Gemini Flash", "Google GenAI (0.075$/M in, 0.30$/M out)", 18.75, 187.50, 1875.00, 18750.00, "Variable (Tokens)"),
        ("Embeddings & FAISS Compute", "CPU Vector Search / all-MiniLM local", 0.00, 15.00, 80.00, 450.00, "Fixe / Échelonné"),
        ("Emails Transactionnels", "Resend Transactional API (0.80$/1k mails)", 5.00, 20.00, 150.00, 900.00, "Variable (Volume)"),
        ("Monitoring, SRE & Logs", "Sentry Pro + Datadog / Grafana Cloud", 15.00, 45.00, 250.00, 1200.00, "Fixe / Échelonné"),
        ("Sauvegardes & Disaster Recovery", "Snapshots quotidiens + PITR 90 jours", 5.00, 15.00, 80.00, 400.00, "Fixe / Échelonné"),
        ("CI/CD Pipeline & Registres Docker", "GitHub Actions + Docker Hub Pro / ECR", 0.00, 12.00, 60.00, 250.00, "Fixe"),
        ("Noms de domaine & Certificats SSL", "Registrar DNS Anycast + Certs Wildcard", 2.50, 2.50, 10.00, 25.00, "Fixe"),
        ("GPU Inférence Dédiée (Optionnel)", "1x L4 / A10G (Embeddings/OCR Scale)", 0.00, 0.00, 320.00, 1280.00, "Optionnel"),
    ]

    current_row = 5
    for item in cost_items_eur:
        ws1.cell(row=current_row, column=1, value=item[0]).font = font_normal
        ws1.cell(row=current_row, column=2, value=item[1]).font = font_normal
        for col_idx, val_eur in enumerate(item[2:6], 3):
            c = ws1.cell(row=current_row, column=col_idx, value=fcfa(val_eur))
            c.font = font_normal
            c.number_format = "#,##0 \"FCFA\""
            c.alignment = Alignment(horizontal="right")
        ws1.cell(row=current_row, column=7, value=item[6]).font = font_normal
        
        for col in range(1, 8):
            ws1.cell(row=current_row, column=col).border = thin_border
            if current_row % 2 == 0:
                ws1.cell(row=current_row, column=col).fill = light_gray_fill
        current_row += 1

    # Total Row
    total_row = current_row
    ws1.cell(row=total_row, column=1, value="COÛT TOTAL MENSUEL D'INFRASTRUCTURE").font = font_subtotal
    ws1.cell(row=total_row, column=2, value="Total Mensuel en Franc CFA (XOF)").font = font_subtotal
    for col_idx in range(3, 7):
        col_letter = get_column_letter(col_idx)
        c = ws1.cell(row=total_row, column=col_idx, value=f"=SUM({col_letter}5:{col_letter}{total_row-1})")
        c.font = font_subtotal
        c.number_format = "#,##0 \"FCFA\""
        c.alignment = Alignment(horizontal="right")
    ws1.cell(row=total_row, column=7, value="Consolidé FCFA").font = font_subtotal
    for col in range(1, 8):
        ws1.cell(row=total_row, column=col).fill = subtotal_fill
        ws1.cell(row=total_row, column=col).border = double_bottom_border
    ws1.row_dimensions[total_row].height = 24

    # Business Metrics Summary Section
    current_row += 2
    ws1.merge_cells(f"A{current_row}:G{current_row}")
    ws1[f"A{current_row}"] = "MÉTRIQUES DE RENTABILITÉ & UNIT ECONOMICS (MARCHÉ IVOIRIEN / UEMOA)"
    ws1[f"A{current_row}"].font = font_section
    ws1[f"A{current_row}"].fill = navy_fill
    ws1[f"A{current_row}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws1.row_dimensions[current_row].height = 24
    
    current_row += 1
    # Projections revenus mensuels en FCFA : mix Free 70%, Pro (19 000 FCFA) 20%, Team (65 000 FCFA) 10%
    # Pour 100 users : (20 * 19000) + (10 * 65000) = 380 000 + 650 000 = 1 030 000 FCFA + API
    rev_100 = 1685000
    rev_1k = 16850000
    rev_10k = 168500000
    rev_100k = 1685000000

    kpis = [
        ("Volume de requêtes mensuelles estimées", "Hypothèse : 50 requêtes/user/mois", 5000, 50000, 500000, 5000000, "#,##0"),
        ("Chiffre d'Affaires Mensuel Estimé (FCFA)", "Mix 70% Free / 20% Pro (19k FCFA) / 10% Team (65k FCFA)", rev_100, rev_1k, rev_10k, rev_100k, "#,##0 \"FCFA\""),
        ("Coût Moyen d'Infrastructure par Utilisateur Actif", "Coût Total Infra / Nb Utilisateurs", f"=C{total_row}/100", f"=D{total_row}/1000", f"=E{total_row}/10000", f"=F{total_row}/100000", "#,##0.0 \"FCFA\""),
        ("Coût Moyen par Requête Graphique Multimodale", "Coût Total Infra / Volume Requêtes", f"=C{total_row}/C{current_row}", f"=D{total_row}/D{current_row}", f"=E{total_row}/E{current_row}", f"=F{total_row}/F{current_row}", "#,##0.00 \"FCFA\""),
        ("Marge Brute d'Infrastructure (%)", "(CA Mensuel - Coût Total Infra) / CA Mensuel", f"=(C{current_row+1}-C{total_row})/C{current_row+1}", f"=(D{current_row+1}-D{total_row})/D{current_row+1}", f"=(E{current_row+1}-E{total_row})/E{current_row+1}", f"=(F{current_row+1}-F{total_row})/F{current_row+1}", "0.0%"),
    ]

    for kpi in kpis:
        ws1.cell(row=current_row, column=1, value=kpi[0]).font = font_bold
        ws1.cell(row=current_row, column=2, value=kpi[1]).font = font_normal
        for col_idx, val in enumerate(kpi[2:6], 3):
            c = ws1.cell(row=current_row, column=col_idx, value=val)
            c.font = font_kpi_num
            c.number_format = kpi[6]
            c.alignment = Alignment(horizontal="right")
        ws1.cell(row=current_row, column=7, value="SaaS KPI FCFA").font = font_normal
        for col in range(1, 8):
            ws1.cell(row=current_row, column=col).border = thin_border
        current_row += 1

    # Column widths
    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 16)
    ws1.column_dimensions["A"].width = 38
    ws1.column_dimensions["B"].width = 44

    # -------------------------------------------------------------------------
    # SHEET 2 to 5: Detailed Scenario Breakdowns (En FCFA)
    # -------------------------------------------------------------------------
    scenarios = [
        ("Scenario_100_Users", 100, 5000, 25.0, 25.0, 5.0, 20.0, 10.0, 18.75, 0.0, 5.0, 15.0, 5.0, 0.0, 2.5, 0.0),
        ("Scenario_1000_Users", 1000, 50000, 120.0, 60.0, 15.0, 20.0, 35.0, 187.50, 15.0, 20.0, 45.0, 15.0, 12.0, 2.5, 0.0),
        ("Scenario_10000_Users", 10000, 500000, 850.0, 350.0, 120.0, 200.0, 180.0, 1875.00, 80.0, 150.0, 250.0, 80.0, 60.0, 10.0, 320.0),
        ("Scenario_100000_Users", 100000, 5000000, 4800.0, 1900.0, 950.0, 1500.0, 850.0, 18750.00, 450.0, 900.0, 1200.0, 400.0, 250.0, 25.0, 1280.0),
    ]

    for title, users, reqs, srv, db, obj, net, red, gem, emb, mail, mon, bkp, cicd, dom, gpu in scenarios:
        ws = wb.create_sheet(title=title)
        ws.views.sheetView[0].showGridLines = True
        
        ws.merge_cells("A1:E2")
        ws["A1"] = f"DÉCOMPOSITION EN FCFA : {users:,} UTILISATEURS ACTIFS ({reqs:,} REQUÊTES/MOIS)"
        ws["A1"].font = font_title
        ws["A1"].fill = navy_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

        ws.cell(row=4, column=1, value="Ressource / Composant").font = font_header
        ws.cell(row=4, column=1).fill = header_fill
        ws.cell(row=4, column=2, value="Spécifications & Dimensionnement").font = font_header
        ws.cell(row=4, column=2).fill = header_fill
        ws.cell(row=4, column=3, value="Quantité").font = font_header
        ws.cell(row=4, column=3).fill = header_fill
        ws.cell(row=4, column=4, value="Coût Unitaire (FCFA)").font = font_header
        ws.cell(row=4, column=4).fill = header_fill
        ws.cell(row=4, column=5, value="Total Mensuel (FCFA)").font = font_header
        ws.cell(row=4, column=5).fill = header_fill

        details = [
            ("Serveurs Applicatifs FastAPI", f"Instances Cloud 4 vCPU / 8 Go RAM (x{max(1, users//2000)})", max(1, users//2000), fcfa(srv / max(1, users//2000)), fcfa(srv)),
            ("Base PostgreSQL Supabase HA", f"Compute dédié + IOPS managés + Réplication", 1, fcfa(db), fcfa(db)),
            ("Cloudflare R2 Object Storage", f"Stockage images graphiques & caches PDF ({users*0.2:.1f} Go)", f"{users*0.2:.0f} Go", fcfa(0.015), fcfa(obj)),
            ("Cloudflare WAF / Enterprise CDN", f"Protection anti-DDoS, Edge caching, SSL", 1, fcfa(net), fcfa(net)),
            ("Redis Enterprise Cluster", f"Queue Celery Broker + Cache extraction SHA-256", 1, fcfa(red), fcfa(red)),
            ("Google Gemini 2.5 Flash API", f"Tokens VLM ({reqs:,} requêtes x 1000 tokens)", f"{reqs*1000:,} Tok", round(gem*RATE_EUR_FCFA/(reqs*1000), 5), fcfa(gem)),
            ("FAISS Vector Index Storage", f"Mémoire vive & SSD NVMe pour embeddings", 1, fcfa(emb), fcfa(emb)),
            ("Emails Resend Transactionnels", f"Emails d'invitations & auth ({users*2:,} envois)", f"{users*2:,} Mails", round(mail*RATE_EUR_FCFA/(users*2), 2), fcfa(mail)),
            ("Sentry & Datadog Monitoring", f"Télémétrie SRE, logs temps réel & APM", 1, fcfa(mon), fcfa(mon)),
            ("Sauvegardes Froid & Vault", f"Snapshots quotidiens multi-régions (90 jours)", 1, fcfa(bkp), fcfa(bkp)),
            ("CI/CD & Registre Docker", f"Runners automatisés & pipelines GitHub", 1, fcfa(cicd), fcfa(cicd)),
            ("Domaine & DNS Anycast", f"graphein.ai + certificats SSL Wildcard", 1, fcfa(dom), fcfa(dom)),
            ("Cluster GPU Dédié (Optionnel)", f"Cartes accélératrices L4 / A10G pour inférence locale", 1 if gpu > 0 else 0, fcfa(gpu), fcfa(gpu)),
        ]

        r = 5
        for d in details:
            ws.cell(row=r, column=1, value=d[0]).font = font_normal
            ws.cell(row=r, column=2, value=d[1]).font = font_normal
            ws.cell(row=r, column=3, value=str(d[2])).font = font_normal
            c_u = ws.cell(row=r, column=4, value=d[3])
            c_u.number_format = "#,##0 \"FCFA\"" if isinstance(d[3], (int, float)) and d[3] >= 1 else "0.0000 \"FCFA\""
            c = ws.cell(row=r, column=5, value=d[4])
            c.font = font_bold
            c.number_format = "#,##0 \"FCFA\""
            c.alignment = Alignment(horizontal="right")
            for col in range(1, 6):
                ws.cell(row=r, column=col).border = thin_border
                if r % 2 == 0:
                    ws.cell(row=r, column=col).fill = light_gray_fill
            r += 1

        # Total
        ws.cell(row=r, column=1, value="TOTAL MENSUEL EN FCFA").font = font_subtotal
        ws.merge_cells(f"A{r}:D{r}")
        c = ws.cell(row=r, column=5, value=f"=SUM(E5:E{r-1})")
        c.font = font_subtotal
        c.number_format = "#,##0 \"FCFA\""
        c.alignment = Alignment(horizontal="right")
        for col in range(1, 6):
            ws.cell(row=r, column=col).fill = subtotal_fill
            ws.cell(row=r, column=col).border = double_bottom_border

        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 16)
        ws.column_dimensions["A"].width = 34
        ws.column_dimensions["B"].width = 52

    # Save
    wb.save(OUTPUT_FILE)
    print(f"Excel model in FCFA generated successfully: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_cost_workbook()
