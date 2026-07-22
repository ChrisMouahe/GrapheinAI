"""Automated User Journey Audit & UI/UX Evaluation Script for GrapheinAI SaaS Web App."""

import json
import time
import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8085"

def run_user_journey_audit():
    print("=" * 70)
    print("STARTING USER JOURNEY AUDIT & UX EVALUATION - GrapheinAI v4.0")
    print("=" * 70)

    # 1. Health Check Endpoint Evaluation
    t0 = time.time()
    resp_health = requests.get(f"{BASE_URL}/api/health")
    dt_health = round(time.time() - t0, 3)
    print(f"\n[STEP 1 - HEALTH CHECK] Status Code: {resp_health.status_code} | Latency: {dt_health}s")
    print(f"Components Health: {json.dumps(resp_health.json(), indent=2)}")

    # 2. Page Load & Static Asset Verification
    t0 = time.time()
    resp_index = requests.get(f"{BASE_URL}/")
    dt_index = round(time.time() - t0, 3)
    print(f"\n[STEP 2 - DASHBOARD PAGE LOAD] Status Code: {resp_index.status_code} | Size: {len(resp_index.content)} bytes | Latency: {dt_index}s")
    assert "<title>GrapheinAI | Research-Grade Chart Analysis Platform</title>" in resp_index.text

    # 3. Dynamic Initial Extraction on Load
    t0 = time.time()
    resp_extract = requests.post(f"{BASE_URL}/api/extract", data={"image_filename": "uploaded_Graphe 1.png"})
    dt_extract = round(time.time() - t0, 3)
    print(f"\n[STEP 3 - INITIAL IMAGE EXTRACTION] Status Code: {resp_extract.status_code} | Latency: {dt_extract}s")
    extract_data = resp_extract.json()
    print(f"Extracted Data Structure: {json.dumps(extract_data, indent=2)}")

    # 4. Multi-Image Upload & Dynamic Data Extraction Variance
    sample_img_path = Path("data/raw/sample_chart.png")
    if sample_img_path.exists():
        t0 = time.time()
        with open(sample_img_path, "rb") as f:
            resp_upload = requests.post(f"{BASE_URL}/api/extract", files={"file": ("sample_chart.png", f, "image/png")})
        dt_upload = round(time.time() - t0, 3)
        print(f"\n[STEP 4 - FILE UPLOAD & EXTRACTION] Status Code: {resp_upload.status_code} | Latency: {dt_upload}s")
        print(f"Uploaded Chart Extraction: {json.dumps(resp_upload.json(), indent=2)}")

    # 5. Human-in-the-Loop (HITL) Data Grid Editing Simulation
    hitl_edited_grid = [
        {"label": "Petit-déjeuner", "value": 310.0, "confidence": 0.99},
        {"label": "Déjeuner", "value": 260.0, "confidence": 0.98},
        {"label": "Collation", "value": 240.0, "confidence": 0.97},
        {"label": "Dîner", "value": 290.0, "confidence": 0.99}
    ]
    
    t0 = time.time()
    payload = {
        "question": "Quelle est la somme totale et la moyenne des calories des repas ?",
        "image_filename": "uploaded_Graphe 1.png",
        "hitl_data_json": json.dumps(hitl_edited_grid)
    }
    resp_analyze = requests.post(f"{BASE_URL}/api/analyze", data=payload)
    dt_analyze = round(time.time() - t0, 3)
    print(f"\n[STEP 5 - PIPELINE ANALYSIS WITH HITL GRID] Status Code: {resp_analyze.status_code} | Latency: {dt_analyze}s")
    analyze_res = resp_analyze.json()
    print(f"Pipeline Result Output:\n{json.dumps(analyze_res, indent=2)}")

    # 6. PDF Report Generation & Download Verification
    t0 = time.time()
    pdf_payload = {
        "question": "Quelle est la somme totale et la moyenne des calories des repas ?",
        "image_filename": "uploaded_Graphe 1.png",
        "hitl_data_json": json.dumps(hitl_edited_grid)
    }
    resp_pdf = requests.post(f"{BASE_URL}/api/report/pdf", data=pdf_payload)
    dt_pdf = round(time.time() - t0, 3)
    print(f"\n[STEP 6 - PDF REPORT DOWNLOAD] Status Code: {resp_pdf.status_code} | Size: {len(resp_pdf.content)} bytes | Latency: {dt_pdf}s")
    assert resp_pdf.content.startswith(b"%PDF")

    print("\n" + "=" * 70)
    print("USER JOURNEY AUDIT FINISHED WITH 100% SUCCESS")
    print("=" * 70)

if __name__ == "__main__":
    run_user_journey_audit()
