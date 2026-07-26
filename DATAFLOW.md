# 🔄 Flux de Données & Pipelines — GraphEin AI

Ce document détaille les flux de données bout-en-bout, la modélisation de la base de données et les pipelines d'exécution multimodaux de **GraphEin AI**.

---

## 📑 Table des Matières
1. [Diagramme de Séquence Général](#1-diagramme-de-séquence-général)
2. [Workflow d'Analyse IA & Multimodal](#2-workflow-danalyse-ia--multimodal)
3. [Schéma de la Base de Données (Mermaid ERD)](#3-schéma-de-la-base-de-données-mermaid-erd)
4. [Politiques de Sécurité Supabase (Row Level Security)](#4-politiques-de-sécurité-supabase-row-level-security)

---

## 1. Diagramme de Séquence Général

Le diagramme suivant illustre le cheminement complet d'une requête utilisateur, du téléversement initial du graphique à la réponse finale.

```mermaid
sequenceDiagram
    autonumber
    actor User as Utilisateur
    participant SPA as Client Frontend SPA
    participant API as FastAPI Backend
    participant Guard as PromptInjectionGuard
    participant OCR as OpenCV OCREngine
    participant Gemini as Gemini 1.5 Flash VLM
    participant AST as SafeCalculator AST
    participant DB as Supabase PostgreSQL (RLS)

    User->>SPA: 1. Téléverse l'image d'un graphique
    SPA->>API: POST /api/session/new (Multipart File)
    API->>OCR: 2. Extrait les boîtes OCR & géométrie
    API->>Gemini: 3. Inférence Vision VLM (Extraction JSON)
    Gemini-->>API: 4. Données structurées (ChartExtraction)
    API->>DB: 5. Sauvegarde la session (Status: ANALYZED)
    API-->>SPA: 6. Affiche la grille de données HITL & Bouton VALIDER

    User->>SPA: 7. Clique sur le bouton VALIDER
    SPA->>API: POST /api/session/interpret
    API->>Gemini: 8. Génère le rapport narratif GraphInterpreter
    API-->>SPA: 9. Affiche le rapport et débloque le Chat

    User->>SPA: 10. Saisit une question ("Quel est le total ?")
    SPA->>API: POST /api/analyze (Question)
    API->>Guard: 11. Inspecte la requête anti-injection
    API->>Gemini: 12. Analyse la question & extrait la formule mathématique
    Gemini-->>API: 13. Formule arithmétique ("68.0 + 88.0 + 78.0")
    API->>AST: 14. Évalue la formule de manière déterministe
    AST-->>API: 15. Résultat calculé ("234.0")
    API-->>SPA: 16. Retourne la réponse enrichie avec métriques XAI
```

---

## 2. Workflow d'Analyse IA & Multimodal

```mermaid
flowchart TD
    Start([Image Téléversée]) --> Preprocess[Pré-traitement OpenCV Niveaux de gris / Contours]
    Preprocess --> OCRBoxes[Détection des boîtes englobantes OCR]
    OCRBoxes --> MultiDetect{Planche Multi-Graphiques ?}
    
    MultiDetect -- Oui --> Segment[Segmentation en sous-images par MultiChartDetector]
    MultiDetect -- Non --> SingleImage[Image unique]
    
    Segment --> VLMInference[Inférence Gemini 1.5 Flash Vision]
    SingleImage --> VLMInference
    
    VLMInference --> StructJSON[Structure JSON Pydantic ChartExtraction]
    StructJSON --> HITLDataGrid[Présentation dans la Grille HITL Frontend]
    
    HITLDataGrid --> UserValidate{Utilisateur valide (VALIDER) ?}
    UserValidate -- Non --> HITLEdit[Édition manuelle des valeurs]
    HITLEdit --> HITLDataGrid
    
    UserValidate -- Oui --> Interpret[GraphInterpreter Agent: Génération du Rapport]
    Interpret --> UnlockChat[Déblocage du Chat Utilisateur]
    
    UnlockChat --> UserQuery[Question Utilisateur]
    UserQuery --> GuardCheck{Prompt Conforme ?}
    GuardCheck -- Non --> SecurityAlert[Alerte Sécurité Bloquante]
    GuardCheck -- Oui --> IntentClass[Classification de l'Intention XGBoost/Rules]
    
    IntentClass --> FormulaExtract[Extraction de la Formule par VLM/Rules]
    FormulaExtract --> ASTEval[SafeCalculator AST Engine]
    ASTEval --> FinalOutput[Réponse Finale + Métriques XAI + PDF]
```

---

## 3. Schéma de la Base de Données (Mermaid ERD)

```mermaid
erDiagram
    PROFILES ||--o{ ANALYSES : "possède"
    PROFILES ||--o{ WORKSPACE_MEMBERS : "participe"
    WORKSPACES ||--o{ WORKSPACE_MEMBERS : "contient"
    WORKSPACES ||--o{ ANALYSES : "regroupe"
    ANALYSES ||--o{ COMMENTS : "reçoit"

    PROFILES {
        uuid id PK
        string email
        string prenom
        string nom
        string entreprise
        string secteur_activite
        string fonction
        string niveau_expertise
        string role
        timestamp created_at
    }

    WORKSPACES {
        uuid id PK
        string name
        uuid owner_id FK
        timestamp created_at
    }

    WORKSPACE_MEMBERS {
        uuid workspace_id PK, FK
        uuid user_id PK, FK
        string role
    }

    ANALYSES {
        uuid id PK
        uuid user_id FK
        uuid workspace_id FK
        string session_id
        string file_name
        string chart_type
        jsonb extraction_data
        jsonb interpretation_report
        jsonb recommendations
        float execution_latency
        timestamp created_at
    }

    COMMENTS {
        uuid id PK
        uuid session_id FK
        uuid user_id FK
        string content
        timestamp created_at
    }
```

---

## 4. Politiques de Sécurité Supabase (Row Level Security)

Les requêtes vers la base de données PostgreSQL Supabase sont protégées par les politiques RLS suivantes :

```sql
-- Politiques RLS pour la table 'analyses'
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- 1. Lecture : Un utilisateur ne peut lire que ses propres analyses ou celles des workspaces auxquels il appartient
CREATE POLICY "RLS_Select_User_Analyses" ON public.analyses
    FOR SELECT USING (
        auth.uid() = user_id OR
        workspace_id IN (
            SELECT workspace_id FROM public.workspace_members WHERE user_id = auth.uid()
        )
    );

-- 2. Insertion : Un utilisateur ne peut insérer des analyses que pour lui-même
CREATE POLICY "RLS_Insert_User_Analyses" ON public.analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```
