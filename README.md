# Assistant Multimodal de Raisonnement sur Graphiques (ChartQA)

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-green.svg)](https://docs.pydantic.dev/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.59-red.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/pytest-57%20passing-brightgreen.svg)](https://docs.pytest.org/)

Bienvenue dans le dépôt du projet **Assistant Multimodal de Raisonnement sur Graphiques (ChartQA)** - GrapheinAI.

---

## 🚀 Fonctionnalités Implémentées

### Sprint 1 — Fondations & SafeCalculator
- **Architecture POO Domaine (Pydantic v2)** : `ChartImage`, `ExtractedDataPoint`, `ChartExtraction` et hiérarchie d'exceptions métiers.
- **Agent SafeCalculator (AST Uniquement)** : Évaluateur d'expressions arithmétiques basé sur AST sans `eval()` ni `exec()`, avec détection et blocage des injections et appels système.
- **Pipeline Data Engineering** : Nettoyage, imputation des nans, coercition des types, statistiques descriptives et génération de visualisations exploratoires.

### Sprint 2 — Classifier ML & Pipeline RAG (FAISS)
- **Feature Engineering Pipeline (`ChartQAFeatureEngineer`)** : Extraction de caractéristiques textuelles et détection des mots-clés d'analyse mathématique/comparative (`difference`, `average`, `sum`, `ratio`, etc.). Génération automatique de la cible binaire `SIMPLE` (0) vs. `COMPLEX` (1).
- **Entraînement & Comparaison ML (`ChartQAClassifierTrainer`)** : Comparaison de **XGBoost** et **RandomForest**. Sauvegarde automatique du meilleur modèle dans `models/best_classifier.joblib`.
- **ClassifierAgent** : Agent OO permettant la prédiction en temps réel de la complexité avec score de confiance.
- **Générateur d'Embeddings (`EmbeddingGenerator`)** : Modèle `sentence-transformers/all-MiniLM-L6-v2` avec cache local et fallback résilient.
- **Index Vectoriel & Pipeline RAG (`FAISSRAGPipeline` & `RetrievalAgent`)** : Indexation FAISS `IndexFlatL2` pour la recherche sémantique Top-k d'exemples.

### Sprint 3 — Agent VLM & Orchestration Globale
- **Agent VLM Gemini Flash Vision (`ReasoningAgent`)** : Prompting structuré avec règles anti-hallucinations, exemples few-shot RAG et format JSON strict validé par Pydantic v2 (`ReasoningOutput`).
- **Orchestrateur Master (`PipelineAgent`)** : Chaînage complet `ChartImage -> ClassifierAgent -> RetrievalAgent -> ReasoningAgent -> SafeCalculator -> PipelineResult`.

### Sprint 4 — Interface Streamlit & Validation Humaine (HITL)
- **Interface Web Moderne Streamlit (`src/app/streamlit_app.py`)** : Dashboard responsive, badges de métadonnées ML, prévisualisation d'images et sélecteur de suggestions.
- **Validation & Upload Sécurisé** : Téléversement `st.file_uploader()` (PNG, JPG, JPEG) avec contrôle des résolutions et limites de taille (<10 MB).
- **Human-in-the-Loop (HITL) Data Editor (`st.data_editor`)** : Éditeur interactif permettant la modification, l'ajout et la suppression des points de données extraits. Les modifications humaines priment sur l'extraction brute pour le calcul final.
- **Protection Anti-Prompt-Injection (`PromptInjectionGuard`)** : Module de sécurité NLP analysant et bloquant les tentatives d'injection de prompt ou d'attaque par jailbreak.
- **Historique de Session (`st.session_state`)** : Conserve l'historique complet des requêtes exécutées dans la session.

---

## 📁 Architecture du Projet

```
GrapheinAI/
├── data/
│   ├── raw/
│   │   ├── sample_chartqa.csv
│   │   └── sample_chart.png
│   └── processed/
│       └── plots/
│           ├── chart_type_distribution.png
│           └── streamlit_ui_preview.png
├── models/
│   ├── best_classifier.joblib
│   ├── classifier_metadata.json
│   ├── index.faiss
│   └── metadata.pkl
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── chart.py
│   │   └── exceptions.py            # Exceptions métiers (y compris PromptInjectionDetectedError)
│   ├── agents/
│   │   ├── classifier_agent.py
│   │   ├── pipeline_agent.py        # Orchestrateur Master
│   │   ├── reasoning_agent.py       # Gemini Flash Vision VLM
│   │   ├── retrieval_agent.py       # Retriever RAG FAISS
│   │   └── safe_calculator.py       # SafeCalculator AST
│   ├── utils/
│   │   ├── data_engineering.py
│   │   ├── embedding_generator.py
│   │   ├── feature_engineering.py
│   │   ├── ml_classifier.py
│   │   ├── rag_pipeline.py
│   │   └── security_guard.py        # Gardien Anti-Prompt-Injection NLP
│   └── app/
│       ├── __init__.py
│       ├── main.py                  # Démo CLI
│       └── streamlit_app.py         # Application Web Streamlit + HITL
├── tests/
│   ├── test_data_engineering.py
│   ├── test_ml_rag.py
│   ├── test_models.py
│   ├── test_safe_calculator.py
│   ├── test_vlm_orchestration.py
│   └── test_streamlit_ui.py         # Tests Streamlit UI, HITL & Sécurité
├── pyproject.toml
└── README.md
```

---

## 🛠️ Installation et Lancement

### Installation
```bash
python -m pip install -e .
```

### Lancer l'Application Web Streamlit
```bash
python -m streamlit run src/app/streamlit_app.py
```

### Lancer la Démonstration CLI
```bash
python -m src.app.main
```

---

## 🧪 Suite de Tests Unitaires (57 tests)

```bash
# Lancer tous les tests unitaires
python -m pytest tests/ -v

# Lancer spécifiquement les tests Streamlit UI & Sécurité (Sprint 4)
python -m pytest tests/test_streamlit_ui.py -v
```

---

## 📜 Licences & Auteurs

Développé dans le cadre du projet **Assistant Multimodal de Raisonnement sur Graphiques (ChartQA)** - GrapheinAI.
