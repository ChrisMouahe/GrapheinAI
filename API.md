# 🔌 Spécification Technique des API REST — GraphEin AI

**Version API** : v5.0.0  
**Format de Données** : JSON / Multipart Form-Data  
**Authentification** : Jetons Bearer JWT (`Authorization: Bearer <token>`)  

---

## 📑 Table des Matières
1. [Endpoints Système & Monitoring (Publics)](#1-endpoints-système--monitoring-publics)
2. [Endpoints Authentification & Identité](#2-endpoints-authentification--identité)
3. [Endpoints Analyse Multimodale & Inférence](#3-endpoints-analyse-multimodale--inférence)
4. [Endpoints Gestion de Session](#4-endpoints-gestion-de-session)
5. [Endpoints Rapports & Collaboration](#5-endpoints-rapports--collaboration)
6. [Gestion des Erreurs & Codes HTTP](#6-gestion-des-erreurs--codes-http)

---

## 1. Endpoints Système & Monitoring (Publics)

### `GET /health` | `GET /api/health`
Vérifie la santé opérationnelle des composants du pipeline.

**Réponse (200 OK)** :
```json
{
  "status": "healthy",
  "uptime_seconds": 1240.45,
  "timestamp": 1784905200.0,
  "components": {
    "opencv_ocr": true,
    "cv_chart_detector": true,
    "validation_agent": true,
    "graph_interpreter": true,
    "safe_calculator_ast": true,
    "xgboost_classifier": true,
    "faiss_rag": true,
    "gemini_vlm": true
  }
}
```

### `GET /status` | `GET /api/status`
Retourne les métriques SRE de performance et d'utilisation mémoire.

**Réponse (200 OK)** :
```json
{
  "status": "operational",
  "uptime_seconds": 1240.45,
  "performance_metrics": {
    "memory_mb": 142.5,
    "cpu_percent": 4.5,
    "cache_hit_ratio": 88.5
  },
  "active_sessions_count": 3
}
```

### `GET /version` | `GET /api/version`
Retourne les métadonnées de version du logiciel.

---

## 2. Endpoints Authentification & Identité

### `POST /api/auth/login`
Authentifie un utilisateur et délivre un jeton JWT.

**Requête Body (JSON)** :
```json
{
  "email": "demo@graphein.ai",
  "password": "password123"
}
```

**Réponse (200 OK)** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "user": {
    "id": "user_123",
    "email": "demo@graphein.ai",
    "name": "Demo User",
    "role": "admin"
  }
}
```

---

## 3. Endpoints Analyse Multimodale & Inférence

### `POST /api/extract`
Extrait les données géométriques, l'OCR et le JSON structuré d'un graphique.

**Requête** : `multipart/form-data` avec champ `file` (Image PNG/JPG).

**Réponse (200 OK)** :
```json
{
  "image_filename": "uploaded_chart.png",
  "chart_structure": {
    "detected_type": "bar",
    "confidence": 0.96
  },
  "extracted_data": {
    "chart_type": "bar",
    "title": "Ventes Mensuelles",
    "data_points": [
      { "label": "Janvier", "value": 68.0, "confidence": 0.98 },
      { "label": "Février", "value": 88.0, "confidence": 0.95 }
    ]
  }
}
```

### `POST /api/analyze`
Exécute le pipeline multimodal complet avec calcul déterministe AST et recommandations.

**Requête Body (Form Data)** :
- `question` (string, requis) : La question posée sur le graphique.
- `target_language` (string, optionnel) : `"fr"` ou `"en"`.
- `hitl_data_json` (string, optionnel) : Surcharges de la grille HITL au format JSON.

**Réponse (200 OK)** :
```json
{
  "final_answer": "234.0",
  "calculation_expression": "68.0 + 88.0 + 78.0",
  "reasoning": "Addition des valeurs pour les trois trimestres",
  "execution_latency": 0.82,
  "recommendations": {
    "executive_summary": "La tendance globale est haussière...",
    "priority_recommendations": [
      { "title": "Optimiser le budget Q2", "priority": "haute" }
    ]
  }
}
```

---

## 4. Endpoints Gestion de Session

### `POST /api/session/new`
Crée une nouvelle session isolée à partir d'une image téléversée.

### `POST /api/session/interpret`
Génère le rapport scientifique narratif complet (GraphInterpreter) pour la session active.

**Réponse (200 OK)** :
```json
{
  "session_id": "sess_89123",
  "interpretation": "# RAPPORT AUTOMATIQUE D'INTERPRÉTATION SCIENTIFIQUE...",
  "status": "INTERPRETED"
}
```

---

## 5. Endpoints Rapports & Collaboration

### `POST /api/report/pdf`
Génère et télécharge le rapport PDF officiel complet.

**Réponse** : Fichier binaire `application/pdf`.

---

## 6. Gestion des Erreurs & Codes HTTP

| Code HTTP | Description | Cause Fréquente |
| :--- | :--- | :--- |
| `200 OK` | Succès | Requête traitée avec succès. |
| `400 Bad Request` | Paramètre invalide | Prompt d'injection détecté ou image trop volumineuse (>10MB). |
| `401 Unauthorized` | Non authentifié | Jeton JWT manquant ou expiré. |
| `403 Forbidden` | Accès refusé | Compte suspendu ou privilèges administrateur manquants. |
| `404 Not Found` | Image non trouvée | Identifiant de session ou image introuvable. |
| `500 Server Error` | Erreur interne | Erreur d'inférence VLM ou de connexion Supabase. |
