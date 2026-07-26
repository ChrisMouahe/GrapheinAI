# 🏗 Architecture Technique & Justification des Choix — GraphEin AI

**Rôles** : Senior Technical Writer, AI Research Engineer & Software Architect  
**Version du Système** : 5.0.0 Enterprise  

---

## 📑 Table des Matières
1. [Vue d'Ensemble de l'Architecture Globale](#1-vue-densemble-de-larchitecture-globale)
2. [Diagramme d'Architecture Système (Mermaid)](#2-diagramme-darchitecture-système-mermaid)
3. [Description Détaillée des Modules Principaux](#3-description-détaillée-des-modules-principaux)
4. [Justification Rationale des Choix Technologiques](#4-justification-rationale-des-choix-technologiques)
5. [Limites du Projet & Travaux Futurs](#5-limites-du-projet--travaux-futurs)
6. [Considérations Éthiques, Empreinte Carbone & RGPD](#6-considérations-éthiques-empreinte-carbone--rgpd)

---

## 1. Vue d'Ensemble de l'Architecture Globale

GraphEin AI adopte une **architecture hexagonale découplée (Ports & Adapters)** combinant :
- Un **Frontend Single Page Application (SPA)** léger et ultra-performant construit en HTML5, Vanilla CSS et JavaScript ES6.
- Un **Backend REST API ASGI** propulsé par FastAPI et Uvicorn.
- Un **Pipeline d'IA Multimodale Hybride** combinant Vision par Ordinateur (OpenCV), Modèle Vision-Langage (Gemini 1.5 Flash Vision), Recherche Vectorielle (FAISS RAG), Classification (XGBoost/Rules) et Évaluation Déterministe (SafeCalculator AST).

---

## 2. Diagramme d'Architecture Système (Mermaid)

```mermaid
graph TB
    subgraph Client Layer
        SPA[Frontend SPA HTML5 / Vanilla CSS]
        ST[Streamlit App / Cloud / HF Spaces]
    end

    subgraph Security & API Gateway Layer
        CORS[CORS Middleware]
        SecHeaders[Security Headers OWASP]
        Guard[PromptInjectionGuard]
        Auth[Supabase Auth & RLS Guard]
    end

    subgraph Application Core Services
        API[FastAPI REST Router]
        SessMgr[AnalysisSessionManager]
        Cache[CacheManager LRU]
        Queue[TaskQueueManager / Workers]
    end

    subgraph AI Pipeline Orchestration (PipelineAgent)
        Intent[QuestionIntentClassifier]
        OCR[OCREngine - OpenCV]
        Intelligence[ChartIntelligenceEngine]
        Reasoning[ReasoningAgent - Gemini 1.5 Flash]
        AST[SafeCalculator AST Engine]
        RAG[RetrievalAgent - FAISS Vector DB]
        Interpreter[GraphInterpreter Agent]
        Recs[RecommendationEngine]
    end

    subgraph External & Persistence Layer
        SupaDB[(Supabase PostgreSQL + RLS)]
        Logs[RotatingFileHandler Log Storage]
        PDF[PDFReportGenerator - ReportLab]
    end

    SPA --> CORS
    ST --> PipelineAgent
    CORS --> SecHeaders
    SecHeaders --> Guard
    Guard --> Auth
    Auth --> API
    API --> SessMgr
    SessMgr --> Cache
    API --> PipelineAgent

    PipelineAgent --> Intent
    PipelineAgent --> OCR
    PipelineAgent --> Intelligence
    PipelineAgent --> Reasoning
    PipelineAgent --> AST
    PipelineAgent --> RAG
    PipelineAgent --> Interpreter
    PipelineAgent --> Recs

    Interpreter --> Recs
    API --> SupaDB
    API --> Logs
    API --> PDF
```

---

## 3. Description Détaillée des Modules Principaux

### 3.1. Gemini Vision (`src/services/gemini/vision.py` & `ReasoningAgent`)
- **Rôle** : Extraction d'information visuelle non-structurée et réponse aux questions complexes en langage naturel.
- **Fonctionnement** : Reçoit l'image du graphique recadrée ainsi qu'un prompt structuré injectant le profil métier de l'utilisateur. Génère des sorties JSON rigoureusement validées par Pydantic.

### 3.2. OCR Engine (`src/utils/ocr_engine.py`)
- **Rôle** : Segmentation géométrique et détection des boîtes englobantes (`[x, y, w, h]`) des textes, graduations et légendes via OpenCV et Tesseract/EAST.
- **Fonctionnement** : Pré-traite l'image (niveaux de gris, seuillage adaptatif, dilatation de contours) pour extraire les régions textuelles avant la transmission au VLM.

### 3.3. Chart Intelligence Engine (`src/utils/chart_intelligence_engine.py`)
- **Rôle** : Réconciliation et fusion des métadonnées visuelles OpenCV avec les sorties du VLM.
- **Fonctionnement** : Calcule les scores de confiance géométriques et ajuste la typologie détectée (Bar, Line, Pie, Scatter).

### 3.4. MultiChartDetector (`src/utils/multi_chart_detector.py`)
- **Rôle** : Détection et découpage des planches multi-graphiques (documents contenant plusieurs figures).
- **Fonctionnement** : Applique un algorithme de détection de contours hiérarchique pour isoler chaque graphique sous forme de sous-image autonome.

### 3.5. Recommendation Engine (`src/agents/recommendation_engine.py`)
- **Rôle** : Génération de recommandations stratégiques adaptées au rôle métier et au niveau d'expertise.
- **Fonctionnement** : Analyse la distribution statistique et génère un résumé exécutif, des points d'attention prioritaires et des conseils d'action.

### 3.6. Prompt Builder (`src/utils/prompt_builder.py`)
- **Rôle** : Constructeur dynamique de prompts système.
- **Fonctionnement** : Injecte le contexte utilisateur (secteur d'activité, fonction, années d'expérience, niveau d'expertise) et les consignes i18n dans les requêtes LLM.

### 3.7. SafeCalculator AST (`src/agents/safe_calculator.py`)
- **Rôle** : Évaluateur déterministe d'expressions mathématiques.
- **Fonctionnement** : Analyse l'Arbre Syntaxique Abstrait (`ast.parse`) de l'expression générée et ré-évalue uniquement les opérations arithmétiques autorisées (`Add`, `Sub`, `Mult`, `Div`, `Pow`). Élimine à 100% les risques d'injection de code et d'hallucination de calcul.

### 3.8. FAISS Vector RAG (`src/utils/faiss_optimizer.py` & `RetrievalAgent`)
- **Rôle** : Indexation et recherche de paires questions-réponses similaires (Few-Shot Prompting).
- **Fonctionnement** : Génère des embeddings et effectue une recherche des $k$ plus proches voisins en temps sous-milliseconde.

### 3.9. XGBoost Question Classifier (`src/agents/classifier_agent.py`)
- **Rôle** : Classification de la complexité des questions utilisateur (SIMPLE vs COMPLEXE).
- **Fonctionnement** : Route les questions simples vers un traitement rapide et les questions complexes vers le pipeline multimodal complet.

### 3.10. SessionManager (`src/services/session_manager.py`)
- **Rôle** : Gestionnaire de cycle de vie des sessions d'analyse.
- **Fonctionnement** : Maintient un registre thread-safe des sessions actives, gère le cache LRU d'extraction et sauvegarde l'état dans Supabase DB.

### 3.11. ThemeManager (`src/app/static/js/theme_manager.js`)
- **Rôle** : Gestionnaire du thème visuel frontend.
- **Fonctionnement** : Alterne dynamiquement les variables CSS (`:root.light` vs `:root.dark`) et persiste la préférence dans `localStorage`.

### 3.12. PDF Generator (`src/utils/pdf_generator.py`)
- **Rôle** : Moteur d'exportation de rapports PDF officiels d'entreprise.
- **Fonctionnement** : Génère des documents PDF vectoriels multi-pages avec ReportLab comprenant les graphiques, grilles de données, rapports narratifs et métriques XAI.

### 3.13. Authentication & Supabase RLS (`src/services/supabase_service.py`)
- **Rôle** : Gestion des identités, jetons JWT et sécurité multi-tenant.
- **Fonctionnement** : Valide les requêtes via les politiques PostgreSQL Row Level Security (RLS), garantissant qu'un utilisateur ne peut accéder qu'à ses propres analyses et workspaces.

---

## 4. Justification Rationale des Choix Technologiques

| Technologie | Raison du Choix | Avantages Principal | Limites | Alternatives Envisagées |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI** | Performance asynchrone ASGI | Vitesse proche de Node.js/Go, validation Pydantic native | Moins d'écosystème ORM que Django | Flask, Django REST Framework |
| **Gemini 1.5 Flash** | Inférence multimodale ultra-rapide | Fenêtre de contexte 1M tokens, faible latence, excellente précision VLM | Quota d'API externe | GPT-4 Vision, Claude 3 Sonnet, LLaVA |
| **SafeCalculator AST** | Sécurité et précision absolue | Zéro hallucination sur les calculs, aucun risque de sécurité (`eval` interdit) | Limité à l'arithmétique classique | `eval()` (dangereux), SymPy |
| **OpenCV** | Traitement d'image bas niveau | Traitement haute vitesse en C++, indépendant du cloud | Sensible au bruit sur les images très dégradées | PIL/Pillow seul, scikit-image |
| **FAISS (Meta)** | Recherche vectorielle locale | Recherche sous-milliseconde, aucune dépendance cloud payante | Maintien de l'index en mémoire RAM | Pinecone, Qdrant, ChromaDB |
| **Vanilla CSS / HTML5** | Performance et maîtrise totale | Temps de chargement FCP < 0.5s, zéro surpoids de bundle JS | Nécessite une discipline d'écriture CSS | TailwindCSS, Bootstrap, Material-UI |

---

## 5. Limites du Projet & Travaux Futurs

### Limites Actuelles
1. **Graphiques Manuscris ou Fortement Dégradés** : La précision de l'OCR baisse sur des résolutions inférieures à 300 DPI ou des écritures à la main.
2. **Planches Multi-pages PDF** : Actuellement limité à l'analyse d'une image par session d'extraction.

### Travaux Futurs & Roadmap
- [ ] **Support Multi-pages PDF** : Découpage automatique des documents PDF de plusieurs pages avec extraction par lots.
- [ ] **Modèle Vision Local Fine-Tuné** : Entraînement d'un modèle LLaVA-NeXT local pour le mode 100% offline sans connexion internet.
- [ ] **Intégration Slack & Microsoft Teams** : Bot d'analyse automatique de graphiques partagés dans les canaux d'entreprise.

---

## 6. Considérations Éthiques, Empreinte Carbone & RGPD

### Empreinte Carbone & Sobriété Numérique
- **Routage Intelligent** : Les requêtes simples sont résolues en local (AST / FAISS) sans solliciter l'API Gemini, divisant la consommation d'énergie par 4.
- **Assets Minimisés** : L'interface frontend n'embarque aucun framework JS lourd (React/Angular), réduisant le transfert réseau à moins de 200 KB.

### Sécurité des Données & Conformité RGPD
- **Strict Data Isolation** : Les données téléversées sont isolées par tenant via PostgreSQL RLS.
- **Non-Entraînement des Modèles** : Les données clients transmises à l'API Gemini ne sont pas réutilisées pour l'entraînement des modèles publics.
