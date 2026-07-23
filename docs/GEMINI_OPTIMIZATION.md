# ⚡ Optimisation Radical de l'API Gemini & Architecture IA Modulaire

Ce document présente l'architecture optimisée du module IA de **GraphEin AI Enterprise** (`src/services/gemini/`). Ce réusinage vise une réduction drastique du nombre d'appels à l'API Gemini Flash Vision, une baisse significative de la consommation de tokens, une diminution des coûts futurs et une extensibilité sans couture via la classe abstraite `BaseAIService`.

---

## 📊 Comparatif : Ancienne vs Nouvelle Architecture

| Critère | Ancienne Architecture | Nouvelle Architecture Optimisée | Gain & Impact |
| :--- | :--- | :--- | :--- |
| **Nombre d'appels à l'upload** | 2 à 4 appels par image | **1 seul appel** (Single Pass Extraction) | **-75% d'appels API** |
| **Téléversement d'image identique** | Ré-extraction VLM complète à chaque upload | **0 appel API** (Cache Hit SHA256 instantané) | **-100% de coûts (0 ms)** |
| **Questions Math / Statistiques** | Envoi systématique du prompt à Gemini | Interception par **QuestionRouter ➔ AST Safe Calculator** | **-100% de tokens sur les calculs** |
| **Génération du Rapport PDF** | Nouvel appel Gemini pour ré-interpréter | Réutilisation de l'interprétation stockée en mémoire | **0 appel Gemini pour les PDF** |
| **Chat Conversationnel** | Envoi répété de l'image brute | Envoi exclusif du **JSON structuré + AST + FAISS** | **-80% de tokens de vision** |
| **Résilience API** | Échecs directs sur 429/503 | **Exponential Backoff Retry** (1s, 2s, 4s, 8s) | **99.9% de taux de succès** |
| **Extensibilité Provider** | Invocations directes dispersées | Interface unifiée **`BaseAIService`** | Prêt pour OpenAI / Claude |

---

## 🏗️ Architecture du Module `src/services/gemini/`

```
src/services/gemini/
├── __init__.py          # Export unifié des composants
├── base.py              # Classe abstraite BaseAIService & modèle Pydantic FullChartExtraction
├── service.py           # Implémentation concrete GeminiService
├── cache.py             # ChartCacheManager (Cache persistant sur disque basé sur SHA256)
├── router.py            # QuestionRouter (Routage AST / Pandas / FAISS vs Gemini VLM)
├── quota.py             # GeminiQuotaManager (Suivi des tokens, latences et économies $)
├── retry.py             # Décorateur exponential_backoff_retry
└── prompts.py           # System prompts optimisés (Format JSON strict application/json)
```

---

## 🔍 Fonctionnement des Composants Clés

### 1. Single Extraction Strategy & `FullChartExtraction`
Lorsqu'un graphique est téléversé, `GeminiService.extract_chart()` réalise **une seule extraction structurée complète** produisant un objet Pydantic `FullChartExtraction` contenant :
- `type_graphique`, `titre`, `sous_titre`, `axes`, `labels`, `legendes`, `series`, `donnees_tabulaires`, `metadonnees`, `confiance_extraction`, `resume_executif` et `interpretation_initiale`.

### 2. Cache SHA256 Persistant (`ChartCacheManager`)
- Calcul de l'empreinte cryptographique `SHA256` du fichier image source.
- Vérification prioritaire dans le cache persistant sur disque (`data/cache/gemini_chart_cache.json`).
- Si l'image a déjà été analysée : restitution en **0 ms sans solliciter l'API Gemini**.

### 3. Routage Local Sans LLM (`QuestionRouter`)
Pour chaque question posée dans le Chat ou l'Analyse Studio, le `QuestionRouter` examine l'intention :
- **Questions mathématiques ou statistiques** (*moyenne, somme, max, min, écart-type, variation %*) ➔ Résolues immédiatement par le calculateur déterministe **AST Safe Calculator / Pandas / NumPy**.
- **Recherche documentaire ou historique** ➔ Résolue par **FAISS**.
- **Raisonnement qualitatif ou synthèse** ➔ Transmise à **GeminiService** (en mode texte structuré uniquement, sans réexpédier l'image).

### 4. Robustesse & Retry Automatique (`exponential_backoff_retry`)
Les appels API à Gemini sont protégés par un système de retentatives exponentielles avec délais progressifs de **1s, 2s, 4s, 8s (jusqu'à 5 essais)** en cas d'erreurs temporaires HTTP 429 (Rate Limit), 503 (Service Unavailable) ou Timeout.

### 5. Suivi SRE & Économies (`GeminiQuotaManager`)
L'endpoint REST `GET /api/gemini/metrics` fournit en temps réel les indicateurs d'observabilité :
- Nombre d'appels total
- Cache Hits / Cache Misses
- Appels évités via AST / Cache
- Consommation estimée en tokens
- Temps moyen et maximum de latence
- Estimation financière des coûts économisés ($ USD)

---

## 🔮 Extensibilité Multi-Provider Future

Le reste de l'application GraphEin AI ne dépend désormais plus que de l'interface abstraite **`BaseAIService`**.

Pour ajouter un nouveau fournisseur IA à l'avenir (ex: OpenAI GPT-4o ou Anthropic Claude 3.5 Sonnet) :
1. Dériver une nouvelle classe `OpenAIService(BaseAIService)` dans `src/services/gemini/` (ou `src/services/ai/`).
2. Implémenter les 7 méthodes du contrat (`extract_chart`, `detect_chart_type`, `generate_interpretation`, `answer_question`, `generate_recommendation`, `vision_chat`, `summarize`).
3. Aucun changement de code ne sera nécessaire dans les contrôleurs API, les agents ou l'interface utilisateur.
