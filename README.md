# Assistant Multimodal de Raisonnement sur Graphiques (ChartQA)

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-green.svg)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](https://docs.pytest.org/)

Bienvenue dans le dépôt du projet **Assistant Multimodal de Raisonnement sur Graphiques (ChartQA)**. Ce projet implémente un agent intelligent capable d'analyser, d'extraire et de raisonner sur des données visuelles et tabulaires issues de graphiques (ChartQA benchmark).

---

## 🚀 Fonctionnalités du Sprint 1

### 1. Architecture Domaine (Orientée Objet & Pydantic v2)
- `ChartImage` : Gestion des métadonnées d'images de graphiques et validation des chemins de fichiers.
- `ExtractedDataPoint` : Structure d'un point de donnée extrait avec libellé, valeur et niveau de confiance ($[0.0, 1.0]$).
- `ChartExtraction` : Structure globale des données extraites (type de graphique, axes, titres, points de données).
- **Exceptions Métier** : Claires et hiérarchisées (`ChartQAError`, `SafeCalculatorError`, `ForbiddenASTNodeError`, `DataEngineeringError`).

### 2. Evaluateur Arithmétique Sécurisé (`SafeCalculator`)
- Évaluation basée **exclusivement** sur l'analyseur syntaxique AST (`ast.parse`).
- **Strictement Interdit** : `eval()`, `exec()`, `import`, appels de fonctions (`Call`), accès aux attributs (`Attribute`), variables (`Name`), et tout nœud AST non autorisé.
- **Autorisé** : Opérateurs arithmétiques `+`, `-`, `*`, `/`, `//`, `%`, `**`, parenthèses, et constantes numériques (nombres entiers et flottants, négatifs/positifs).
- **Couverture de tests** : >90% (100% des lignes couvertes par pytest).

### 3. Pipeline Data Engineering (`ChartQADataEngineer`)
- Chargement robuste des datasets ChartQA CSV.
- Nettoyage des valeurs manquantes (imputation médiane / mode / suppression).
- Conversion contrôlée des types de données.
- Statistiques descriptives complètes.
- Génération automatique de graphiques exploratoires sauvegardés dans `data/processed/plots/`.

---

## 📁 Architecture du Projet

```
GrapheinAI/
├── data/
│   ├── raw/
│   │   └── sample_chartqa.csv       # Dataset de démonstration ChartQA
│   └── processed/
│       └── plots/                   # Visualisations exploratoires générées
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chart.py                 # Modèles Pydantic v2 (ChartImage, ChartExtraction, etc.)
│   │   └── exceptions.py            # Exceptions métier personnalisées
│   ├── agents/
│   │   ├── __init__.py
│   │   └── safe_calculator.py       # Agent SafeCalculator basés sur AST uniquement
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_engineering.py      # Module d'ingénierie et nettoyage de données
│   └── app/
│       ├── __init__.py
│       └── main.py                  # Script d'exécution et démonstration CLI
├── tests/
│   ├── __init__.py
│   ├── test_models.py               # Tests des modèles et de validation Pydantic
│   ├── test_safe_calculator.py      # Tests d'évaluation et de sécurité (injections)
│   └── test_data_engineering.py     # Tests du pipeline data engineering
├── pyproject.toml                   # Configuration du projet, pytest, ruff, black
├── README.md                        # Documentation d'utilisation
└── .gitignore                       # Fichiers à ignorer par Git
```

---

## 🛠️ Installation et Prérequis

### Prérequis
- **Python 3.12+**

### Installation

1. Cloner le dépôt et se positionner dans le répertoire :
```bash
git clone https://github.com/GrapheinAI/ChartQA-Multimodal-Assistant.git
cd ChartQA-Multimodal-Assistant
```

2. Installer les dépendances du projet :
```bash
python -m pip install -e .
```
*(Ou utiliser `pip install pydantic pandas matplotlib seaborn pytest`)*

---

## 🧪 Exécution des Tests

Lancer la suite complète de 30 tests unitaires avec `pytest` :

```bash
python -m pytest tests/ -v
```

Structure des tests :
- **`tests/test_safe_calculator.py`** : Validation des opérations mathématiques, parenthèses, nombres négatifs, et blocage d'injections arbitraires (`eval`, `exec`, `import os`, `__class__`, etc.).
- **`tests/test_models.py`** : Validation des schémas Pydantic v2 et levée d'exceptions.
- **`tests/test_data_engineering.py`** : Validation du chargement, du nettoyage, des statistiques et de la génération des visuels.

---

## 🚀 Exécution de la Démonstration CLI

Pour exécuter la démonstration complète des fonctionnalités du Sprint 1 :

```bash
python -m src.app.main
```

Ce script va :
1. Instancier et valider les modèles de graphiques et points de données.
2. Évaluer plusieurs expressions arithmétiques complexes et tenter une injection sécurisée.
3. Charger le dataset `data/raw/sample_chartqa.csv`, nettoyer les nans, convertir les types et générer les graphiques d'analyse dans `data/processed/plots/`.

---

## 📜 Licences & Auteurs

Développé dans le cadre du projet **Assistant Multimodal de Raisonnement sur Graphiques (ChartQA)** - GrapheinAI.
