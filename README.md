# Assistant Multimodal de Raisonnement sur Graphiques (ChartQA)

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-green.svg)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/pytest-41%20passing-brightgreen.svg)](https://docs.pytest.org/)

Bienvenue dans le dépôt du projet **Assistant Multimodal de Raisonnement sur Graphiques (ChartQA)** - GrapheinAI.

---

## 🚀 Fonctionnalités Implémentées

### Sprint 1 — Fondations & SafeCalculator
- **Architecture POO Domaine (Pydantic v2)** : `ChartImage`, `ExtractedDataPoint`, `ChartExtraction` et hiérarchie d'exceptions métiers.
- **Agent SafeCalculator (AST Uniquement)** : Évaluateur d'expressions arithmétiques basé sur AST sans `eval()` ni `exec()`, avec détection et blocage strict des tentatives d'injections et appels système.
- **Pipeline Data Engineering** : Nettoyage, imputation des nans, coercition des types, statistiques descriptives et génération de visualisations exploratoires.

### Sprint 2 — Classifier ML & Pipeline RAG (FAISS)
- **Feature Engineering Pipeline (`ChartQAFeatureEngineer`)** : Extraction de caractéristiques textuelles (longueur, tokens, chiffres, questions) et détection des mots-clés d'analyse mathématique/comparative (`difference`, `average`, `sum`, `ratio`, etc.). Génération automatique de la cible binaire `SIMPLE` (0) vs. `COMPLEX` (1).
- **Entraînement & Comparaison ML (`ChartQAClassifierTrainer`)** : Comparaison de **XGBoost** et **RandomForest** sur les métriques (Accuracy, Precision, Recall, F1-Score, Confusion Matrix). Sauvegarde automatique du meilleur modèle dans `models/best_classifier.joblib`.
- **ClassifierAgent** : Agent OO permettant la prédiction en temps réel de la complexité des requêtes avec score de confiance.
- **Générateur d'Embeddings (`EmbeddingGenerator`)** : Modèle `sentence-transformers/all-MiniLM-L6-v2` avec cache local et fallback résilient.
- **Index Vectoriel & Pipeline RAG (`FAISSRAGPipeline` & `RetrievalAgent`)** : Indexation FAISS `IndexFlatL2` pour la recherche sémantique Top-k d'exemples de résolution.

---

## 📁 Architecture du Projet

```
GrapheinAI/
├── data/
│   ├── raw/
│   │   └── sample_chartqa.csv       # Dataset exemple ChartQA
│   └── processed/
│       └── plots/                   # Visuels exploratoires générés
├── models/
│   ├── best_classifier.joblib      # Modèle ML entraîné (XGBoost)
│   ├── classifier_metadata.json    # Métadonnées et métriques
│   ├── index.faiss                 # Index vectoriel FAISS
│   └── metadata.pkl                # Base de connaissances RAG
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── chart.py                 # Modèles Pydantic v2
│   │   └── exceptions.py            # Exceptions domaine
│   ├── agents/
│   │   ├── safe_calculator.py       # Agent SafeCalculator (AST)
│   │   ├── classifier_agent.py      # Agent Classifier (XGBoost)
│   │   └── retrieval_agent.py       # Agent RAG (FAISS Top-k)
│   └── utils/
│       ├── data_engineering.py      # Pipeline Data Engineering
│       ├── feature_engineering.py   # Extraction de caractéristiques
│       ├── ml_classifier.py         # Trainer & Evaluateur ML
│       ├── embedding_generator.py   # Générateur MiniLM Embeddings
│       └── rag_pipeline.py          # Indexation & Recherche FAISS
├── app/
│   ├── __init__.py
│   └── main.py                      # Démonstration globale CLI
├── tests/
│   ├── test_models.py
│   ├── test_safe_calculator.py
│   ├── test_data_engineering.py
│   └── test_ml_rag.py               # Tests unitaires ML & RAG
├── pyproject.toml
└── README.md
```

---

## 🛠️ Installation et Prérequis

```bash
# Clone du dépôt
cd ChartQA-Multimodal-Assistant

# Installation des dépendances
python -m pip install -e .
```

---

## 🧪 Exécution des Tests Unitaires (41 tests)

Pour exécuter l'ensemble de la suite de tests unitaires :

```bash
# Lancer tous les tests (Sprint 1 + Sprint 2)
python -m pytest tests/ -v

# Lancer uniquement les tests ML & RAG du Sprint 2
python -m pytest tests/test_ml_rag.py -v
```

---

## 🚀 Démonstration Interactive (CLI)

Pour lancer la démonstration complète réunissant le SafeCalculator, le Classificateur ML et le Retriever RAG FAISS :

```bash
python -m src.app.main
```

---

## 📜 Licences & Auteurs

Développé dans le cadre du projet **Assistant Multimodal de Raisonnement sur Graphiques (ChartQA)** - GrapheinAI.
