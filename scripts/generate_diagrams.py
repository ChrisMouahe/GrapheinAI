"""Script to generate architecture_target.drawio and architecture_target.png for GraphEin AI."""

import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent

def generate_drawio():
    drawio_content = """<mxfile host="app.diagrams.net" modified="2026-08-31T20:00:00.000Z" agent="GraphEin AI Audit Team" version="24.0.0" type="device">
  <diagram id="graphein-arch-target" name="GraphEin AI Production Cloud Architecture">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- Edge / Ingress Layer -->
        <mxCell id="zone_edge" value="Zone Edge &amp; Protection (Cloudflare / Global CDN)" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F3F4F6;strokeColor=#D1D5DB;fontStyle=1;fontSize=14;fontColor=#111827;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="1520" height="130" as="geometry" />
        </mxCell>
        <mxCell id="cf_dns" value="Cloudflare DNS &amp; DDoS&#xa;WAF Layer 7 &amp; SSL/TLS Termination" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F97316;strokeColor=#EA580C;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_edge">
          <mxGeometry x="30" y="40" width="260" height="60" as="geometry" />
        </mxCell>
        <mxCell id="cf_cdn" value="Global Static Asset CDN&#xa;HTML / JS / CSS / Favicons" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F97316;strokeColor=#EA580C;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_edge">
          <mxGeometry x="340" y="40" width="240" height="60" as="geometry" />
        </mxCell>
        <mxCell id="cf_cache" value="Edge Caching &amp; Rate Limiting&#xa;100 req/min per IP Policy" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F97316;strokeColor=#EA580C;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_edge">
          <mxGeometry x="630" y="40" width="260" height="60" as="geometry" />
        </mxCell>
        <mxCell id="ingress_gateway" value="Ingress Traefik / Nginx Controller&#xa;mTLS &amp; JWT Verification Gateway" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0284C7;strokeColor=#0369A1;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_edge">
          <mxGeometry x="940" y="40" width="280" height="60" as="geometry" />
        </mxCell>
        <mxCell id="prompt_sec" value="OWASP Prompt Injection Guard&#xa;Magic Bytes &amp; Regex Sanitizer" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DC2626;strokeColor=#B91C1C;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_edge">
          <mxGeometry x="1270" y="40" width="220" height="60" as="geometry" />
        </mxCell>

        <!-- Kubernetes Cluster Core -->
        <mxCell id="zone_k8s" value="Kubernetes Cluster Core (Production EKS / GKE / Hetzner k3s Multi-AZ)" style="swimlane;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#93C5FD;fontStyle=1;fontSize=14;fontColor=#1E3A8A;" vertex="1" parent="1">
          <mxGeometry x="40" y="200" width="1520" height="480" as="geometry" />
        </mxCell>

        <!-- API Pods -->
        <mxCell id="api_service" value="FastAPI REST Backend (HPA Autoscaling: 2-20 Pods)&#xa;Uvicorn ASGI • Pydantic V2 • Async Handlers&#xa;Auth Middleware • Admin Services • Workspace Engine" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2563EB;strokeColor=#1D4ED8;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_k8s">
          <mxGeometry x="40" y="50" width="460" height="90" as="geometry" />
        </mxCell>

        <!-- Redis Cluster -->
        <mxCell id="redis_cluster" value="Redis Cluster v7 (HA Master/Replica + Sentinel)&#xa;• Task Queue Broker (Celery / RQ)&#xa;• SHA-256 Extraction Cache (TTL 7d)&#xa;• User Session &amp; Rate-Limit Store" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DC2626;strokeColor=#991B1B;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_k8s">
          <mxGeometry x="560" y="50" width="400" height="90" as="geometry" />
        </mxCell>

        <!-- Celery Workers -->
        <mxCell id="workers_pool" value="Asynchronous Pipeline Workers (Celery Autoscale)&#xa;Image Processing • OCR Contours • Statistical Engine&#xa;AST Evaluator • ReportLab PDF Generation" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0D9488;strokeColor=#0F766E;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_k8s">
          <mxGeometry x="1020" y="50" width="460" height="90" as="geometry" />
        </mxCell>

        <!-- Pipeline Agent Core Sub-System -->
        <mxCell id="zone_pipeline" value="Multimodal AI Orchestration Sub-System (PipelineAgent)" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontStyle=1;fontSize=12;fontColor=#334155;" vertex="1" parent="zone_k8s">
          <mxGeometry x="40" y="180" width="1440" height="270" as="geometry" />
        </mxCell>
        <mxCell id="ocr_cv" value="1. Vision Preprocessor&#xa;OpenCV Bounding Boxes&#xa;Grayscale &amp; Adaptive Thresh" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#475569;strokeColor=#334155;fontColor=#FFFFFF;" vertex="1" parent="zone_pipeline">
          <mxGeometry x="30" y="40" width="200" height="70" as="geometry" />
        </mxCell>
        <mxCell id="chart_intel" value="2. ChartIntelligenceEngine&#xa;Color Segmentation&#xa;Axis &amp; Legend Mapper" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#475569;strokeColor=#334155;fontColor=#FFFFFF;" vertex="1" parent="zone_pipeline">
          <mxGeometry x="260" y="40" width="200" height="70" as="geometry" />
        </mxCell>
        <mxCell id="vlm_router" value="3. Gemini VLM Reasoning&#xa;Gemini Flash 1.5 / 2.5&#xa;Single-Pass JSON Extraction" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#4338CA;strokeColor=#3730A3;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_pipeline">
          <mxGeometry x="490" y="40" width="220" height="70" as="geometry" />
        </mxCell>
        <mxCell id="ast_engine" value="4. SafeCalculator AST Engine&#xa;Deterministic Python AST&#xa;Zero Math Hallucination" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#15803D;strokeColor=#166534;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_pipeline">
          <mxGeometry x="740" y="40" width="210" height="70" as="geometry" />
        </mxCell>
        <mxCell id="faiss_rag" value="5. FAISS Vector Search&#xa;all-MiniLM-L6-v2 Embeddings&#xa;Domain Few-Shot Context" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#7C3AED;strokeColor=#6D28D9;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_pipeline">
          <mxGeometry x="980" y="40" width="200" height="70" as="geometry" />
        </mxCell>
        <mxCell id="xai_recs" value="6. XAI &amp; Recommender&#xa;Explainability Tracing&#xa;Industry Actionable Insights" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#D97706;strokeColor=#B45309;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_pipeline">
          <mxGeometry x="1210" y="40" width="200" height="70" as="geometry" />
        </mxCell>

        <mxCell id="multi_chart" value="Multi-Chart Splitter &amp; Fusion Engine (multi_chart_pipeline.py + multi_chart_fusion.py)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#64748B;strokeColor=#475569;fontColor=#FFFFFF;" vertex="1" parent="zone_pipeline">
          <mxGeometry x="30" y="150" width="430" height="50" as="geometry" />
        </mxCell>
        <mxCell id="hitl_grid" value="Human-in-the-Loop Validation Grid (Ag-Grid / Data Reconciler)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#64748B;strokeColor=#475569;fontColor=#FFFFFF;" vertex="1" parent="zone_pipeline">
          <mxGeometry x="500" y="150" width="450" height="50" as="geometry" />
        </mxCell>
        <mxCell id="pdf_exporter" value="Vectorial PDF &amp; XLSX Generators (ReportLab + OpenPyXL Engine)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#64748B;strokeColor=#475569;fontColor=#FFFFFF;" vertex="1" parent="zone_pipeline">
          <mxGeometry x="980" y="150" width="430" height="50" as="geometry" />
        </mxCell>

        <!-- Data & External Services Layer -->
        <mxCell id="zone_storage" value="Data Persistence, Security &amp; External SaaS Integrations" style="swimlane;whiteSpace=wrap;html=1;fillColor=#FEF2F2;strokeColor=#FECACA;fontStyle=1;fontSize=14;fontColor=#991B1B;" vertex="1" parent="1">
          <mxGeometry x="40" y="710" width="1520" height="340" as="geometry" />
        </mxCell>

        <mxCell id="supabase_db" value="Supabase PostgreSQL HA Cluster&#xa;• Row Level Security (RLS) Isolation&#xa;• Users, Sessions, Workspaces, Comments&#xa;• Point-in-Time Recovery (PITR)" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#059669;strokeColor=#047857;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_storage">
          <mxGeometry x="50" y="50" width="300" height="110" as="geometry" />
        </mxCell>

        <mxCell id="s3_storage" value="S3 Compatible Object Storage&#xa;(Cloudflare R2 / AWS S3 / Wasabi)&#xa;• Original High-Res Charts&#xa;• Cached Processed Cropped Tiles&#xa;• Generated PDF &amp; XLSX Reports" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#D97706;strokeColor=#B45309;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_storage">
          <mxGeometry x="400" y="50" width="300" height="110" as="geometry" />
        </mxCell>

        <mxCell id="google_genai" value="Google Gemini API (Flash 1.5/2.5)&#xa;• Multimodal Visual Question Answering&#xa;• Token Quota Management&#xa;• Rate-limit Retry with Backoff" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#4338CA;strokeColor=#3730A3;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_storage">
          <mxGeometry x="750" y="50" width="280" height="110" as="geometry" />
        </mxCell>

        <mxCell id="resend_mail" value="Resend Email Service&#xa;• Magic Link &amp; Password Resets&#xa;• Workspace Member Invites&#xa;• Quota &amp; Security Alerts" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1F2937;strokeColor=#111827;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_storage">
          <mxGeometry x="1080" y="50" width="200" height="110" as="geometry" />
        </mxCell>

        <mxCell id="sentry_obs" value="SRE &amp; Observability Stack&#xa;• Sentry Error Tracking&#xa;• Prometheus + Grafana Metrics&#xa;• Loguru Structured Log Aggregator" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#831843;strokeColor=#701A75;fontColor=#FFFFFF;fontStyle=1;" vertex="1" parent="zone_storage">
          <mxGeometry x="1310" y="50" width="180" height="110" as="geometry" />
        </mxCell>

        <mxCell id="faiss_disk" value="Persistent FAISS Index Volume (EFS / Ceph NVMe SSD)&#xa;• Vector Search Embedding Base &amp; Domain Ontology" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#6D28D9;strokeColor=#5B21B6;fontColor=#FFFFFF;" vertex="1" parent="zone_storage">
          <mxGeometry x="50" y="200" width="650" height="90" as="geometry" />
        </mxCell>

        <mxCell id="backup_vault" value="Cold Backup Vault &amp; Audit Trail (Daily Automated Snapshots, Retention 90 Days)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#374151;strokeColor=#1F2937;fontColor=#FFFFFF;" vertex="1" parent="zone_storage">
          <mxGeometry x="750" y="200" width="740" height="90" as="geometry" />
        </mxCell>

        <!-- Connections -->
        <mxCell id="flow_1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0284C7;strokeWidth=2;" edge="1" parent="1" source="ingress_gateway" target="api_service">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="flow_2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DC2626;strokeWidth=2;" edge="1" parent="1" source="api_service" target="redis_cluster">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="flow_3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0D9488;strokeWidth=2;" edge="1" parent="1" source="redis_cluster" target="workers_pool">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="flow_4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;" edge="1" parent="1" source="api_service" target="supabase_db">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="flow_5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#4338CA;strokeWidth=2;" edge="1" parent="1" source="workers_pool" target="google_genai">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="flow_6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;" edge="1" parent="1" source="workers_pool" target="s3_storage">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    out_file = ROOT_DIR / "architecture_target.drawio"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(drawio_content)
    print(f"✅ Generated {out_file}")

def generate_png():
    plt.figure(figsize=(18, 11), dpi=300)
    ax = plt.gca()
    ax.set_facecolor('#0F172A')
    
    # Title
    plt.text(9, 10.5, "GraphEin AI — Enterprise Target Cloud Architecture (Production)", 
             fontsize=20, fontweight='bold', color='#38BDF8', ha='center', va='center')
    plt.text(9, 10.1, "High-Availability, Multi-Tenant, Zero-Hallucination Multimodal Architecture", 
             fontsize=12, color='#94A3B8', ha='center', va='center')
    
    def draw_box(x, y, w, h, title, subtitle, bg_color, border_color, text_color='#FFFFFF', title_color='#38BDF8'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15", 
                                      facecolor=bg_color, edgecolor=border_color, linewidth=2)
        ax.add_patch(rect)
        plt.text(x + w/2, y + h*0.65, title, fontsize=11, fontweight='bold', color=title_color, ha='center', va='center')
        plt.text(x + w/2, y + h*0.35, subtitle, fontsize=8.5, color=text_color, ha='center', va='center')

    def draw_group(x, y, w, h, group_title, bg='#1E293B', border='#334155'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.2", 
                                      facecolor=bg, edgecolor=border, linewidth=1.5, alpha=0.85)
        ax.add_patch(rect)
        plt.text(x + 0.3, y + h - 0.25, group_title, fontsize=12, fontweight='bold', color='#F8FAFC', ha='left', va='center')

    # Layer 1: Edge & Ingress
    draw_group(0.5, 8.2, 17, 1.5, "1. EDGE & PROTECTION LAYER (Cloudflare / WAF / CDN)")
    draw_box(0.8, 8.4, 3.6, 0.9, "Cloudflare DNS & WAF", "DDoS L7 + SSL/TLS + Bot Guard", "#1E293B", "#F97316")
    draw_box(4.8, 8.4, 3.6, 0.9, "Global CDN Caching", "Static SPA + HTML/CSS/JS Assets", "#1E293B", "#F97316")
    draw_box(8.8, 8.4, 3.6, 0.9, "Traefik Ingress Gateway", "mTLS + JWT Validation + Routing", "#1E293B", "#0284C7")
    draw_box(12.8, 8.4, 4.3, 0.9, "Prompt Injection Guard", "OWASP Security + Magic Bytes Check", "#1E293B", "#DC2626")

    # Layer 2: Compute & Orchestration
    draw_group(0.5, 4.4, 17, 3.5, "2. COMPUTE CLUSTER (Kubernetes EKS/GKE / Hetzner k3s Multi-AZ)")
    draw_box(0.8, 6.7, 4.8, 0.9, "FastAPI REST Core (ASGI)", "HPA Autoscale (2-20 Pods) • Pydantic V2", "#1E3A8A", "#3B82F6")
    draw_box(6.1, 6.7, 5.0, 0.9, "Redis 7 HA Cluster", "Celery Queue Broker • SHA256 Cache • RateLimit", "#991B1B", "#EF4444")
    draw_box(11.6, 6.7, 5.5, 0.9, "Celery Async Workers", "Image Preproc • AST Math • PDF/XLSX Gen", "#065F46", "#10B981")

    # Inner Pipeline Orchestration Box
    draw_group(0.8, 4.6, 16.4, 1.8, "Multimodal Pipeline Sub-Agents (PipelineAgent)", bg="#0F172A", border="#475569")
    draw_box(1.0, 4.8, 2.4, 1.2, "OpenCV Preproc", "Adaptive Thresh\nOCR Bounding Boxes", "#334155", "#64748B", text_color="#E2E8F0")
    draw_box(3.7, 4.8, 2.4, 1.2, "ChartIntelligence", "Color & Axis Mapping\nLegend Reconciliation", "#334155", "#64748B", text_color="#E2E8F0")
    draw_box(6.4, 4.8, 2.6, 1.2, "Gemini VLM Vision", "Flash 1.5/2.5 Engine\nSingle-Pass Extraction", "#312E81", "#6366F1", title_color="#A5B4FC")
    draw_box(9.3, 4.8, 2.4, 1.2, "SafeCalculator AST", "Deterministic Math\n0% Hallucination", "#14532D", "#22C55E", title_color="#86EFAC")
    draw_box(12.0, 4.8, 2.4, 1.2, "FAISS RAG Engine", "all-MiniLM-L6-v2\nSub-ms Vector Search", "#581C87", "#A855F7", title_color="#D8B4FE")
    draw_box(14.7, 4.8, 2.3, 1.2, "XAI & Recommender", "Explainability Score\nActionable Business", "#78350F", "#F59E0B", title_color="#FDE68A")

    # Layer 3: Persistence & Third-Party
    draw_group(0.5, 0.6, 17, 3.5, "3. PERSISTENCE, OBSERVABILITY & EXTERNAL PROVIDERS")
    draw_box(0.8, 2.7, 3.8, 1.1, "Supabase PostgreSQL HA", "Row-Level Security (RLS)\nSessions, Workspaces, Users", "#064E3B", "#10B981")
    draw_box(5.0, 2.7, 3.8, 1.1, "Cloudflare R2 / S3 Storage", "High-Res Charts, Tiles\nGenerated PDF / Excel Reports", "#78350F", "#F59E0B")
    draw_box(9.2, 2.7, 3.8, 1.1, "Google Gemini 2.5 API", "Multimodal VLM Reasoning\nQuota & Retry Backoff", "#312E81", "#6366F1")
    draw_box(13.4, 2.7, 3.7, 1.1, "Resend & Sentry Stack", "Transactional Emails\nSRE Logs & Prometheus", "#500724", "#EC4899")

    draw_box(0.8, 0.9, 7.5, 1.4, "Persistent FAISS Volume (NVMe)", "Sub-millisecond Vector DB Index\nDomain-Specific Rules & Benchmark Embeddings", "#3B0764", "#9333EA")
    draw_box(8.7, 0.9, 8.4, 1.4, "Automated Backup & Disaster Recovery", "Daily Point-in-Time Recovery (PITR)\nCross-Region Encrypted Vault (90 Days Retention)", "#1E293B", "#475569")

    # Connective arrows
    ax.annotate("", xy=(2.5, 8.4), xytext=(2.5, 7.6), arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=2))
    ax.annotate("", xy=(8.5, 6.7), xytext=(8.5, 6.0), arrowprops=dict(arrowstyle="->", color="#EF4444", lw=2))
    ax.annotate("", xy=(14.2, 6.7), xytext=(14.2, 3.8), arrowprops=dict(arrowstyle="->", color="#10B981", lw=2))
    ax.annotate("", xy=(2.7, 4.4), xytext=(2.7, 3.8), arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=2))

    ax.set_xlim(0, 18)
    ax.set_ylim(0, 11)
    plt.axis('off')
    plt.tight_layout()
    
    out_file = ROOT_DIR / "architecture_target.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight', facecolor='#0F172A')
    plt.close()
    print(f"✅ Generated {out_file}")

if __name__ == "__main__":
    generate_drawio()
    generate_png()
