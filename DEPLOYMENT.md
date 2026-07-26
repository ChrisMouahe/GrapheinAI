# 🚀 Guide de Déploiement Production — GraphEin AI

Ce document constitue le guide officiel de déploiement pour la plateforme SaaS **GraphEin AI**.
Il permet à n'importe quel développeur ou ingénieur DevOps d'installer et de déployer le projet en **moins de 10 minutes**.

---

## 📑 Table des Matières
1. [Configuration Requise & Prérequis](#1-configuration-requise--prérequis)
2. [Variables d'Environnement](#2-variables-denvironnement)
3. [Installation Locale Rapide (< 5 min)](#3-installation-locale-rapide--5-min)
4. [Déploiement avec Docker & Docker Compose](#4-déploiement-avec-docker--docker-compose)
5. [Déploiement sur Streamlit Community Cloud](#5-déploiement-sur-streamlit-community-cloud)
6. [Déploiement sur Hugging Face Spaces](#6-déploiement-sur-hugging-face-spaces)
7. [Supervision & Health Checks](#7-supervision--health-checks)
8. [Rotation des Logs & Sauvegardes](#8-rotation-des-logs--sauvegardes)
9. [Directives de Sécurité Production](#9-directives-de-sécurité-production)

---

## 1. Configuration Requise & Prérequis
- **Python** : `3.12+`
- **Docker** & **Docker Compose** *(optionnel mais recommandé)*
- **Git**

---

## 2. Variables d'Environnement

Le projet utilise exclusivement des variables d'environnement (aucune clé n'est codée en dur).  
Créez un fichier `.env` à la racine du projet en vous basant sur la structure suivante :

```env
# Clé d'API Gemini Flash Vision (Obligatoire)
GEMINI_API_KEY=your_gemini_api_key_here

# Base de Données Supabase & Authentification RLS (Optionnel, Mode Mock Automatique si absent)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key

# Serveur SMTP de Notification & Collaboration (Optionnel, Fallback dev actif)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@domain.com
SMTP_PASSWORD=your_app_password
```

---

## 3. Installation Locale Rapide (< 5 min)

```bash
# 1. Cloner le dépôt
git clone https://github.com/your-org/GrapheinAI.git
cd GrapheinAI

# 2. Créer l'environnement virtuel Python
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le serveur backend FastAPI
python -m uvicorn src.app.api:app --host 127.0.0.1 --port 8088

# 5. Lancer l'application Streamlit (Terminal séparé)
streamlit run src/app/streamlit_app.py
```

- **Application Web SPA / REST API** : `http://127.0.0.1:8088`
- **Interface Streamlit** : `http://127.0.0.1:8501`
- **Documentation API OpenAPI Swagger** : `http://127.0.0.1:8088/docs`

---

## 4. Déploiement avec Docker & Docker Compose

GraphEin AI inclut une image Docker multi-stage optimisée avec utilisateur non-root et bibliothèques OpenCV pré-installées.

### Lancement avec Docker Compose (Recommandé)
```bash
docker-compose up -d --build
```

### Lancement avec Docker simple
```bash
# Construire l'image Docker
docker build -t graphein-ai:latest .

# Exécuter le conteneur
docker run -d \
  -p 8088:8088 \
  --env-file .env \
  --name graphein-app \
  graphein-ai:latest
```

---

## 5. Déploiement sur Streamlit Community Cloud

1. Pushez le dépôt sur GitHub.
2. Rendez-vous sur [share.streamlit.io](https://share.streamlit.io).
3. Connectez votre dépôt GitHub.
4. Renseignez les paramètres de déploiement :
   - **Main file path** : `app.py`
   - **Python version** : `3.12`
5. Dans **Advanced Settings -> Secrets**, collez vos variables d'environnement (`GEMINI_API_KEY`, etc.).
6. Cliquez sur **Deploy**.

---

## 6. Déploiement sur Hugging Face Spaces

1. Créez un nouveau **Space** sur Hugging Face ([huggingface.co/new-space](https://huggingface.co/new-space)).
2. Choisissez le SDK **Streamlit** ou **Docker**.
3. Pour le SDK Streamlit :
   - Fichier d'entrée : `app.py`
   - Dans **Settings -> Repository secrets**, ajoutez `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`.
4. Pushez le code sur le dépôt Hugging Face.

---

## 7. Déploiement sur Render (via Blueprint)

GraphEin AI inclut un fichier `render.yaml` prêt à l'emploi (Render Blueprint) configurant l'API REST FastAPI backend et l'interface Web Streamlit UI.

### Étapes de déploiement en 1-clic :
1. Pushez vos modifications sur GitHub/GitLab.
2. Connectez-vous sur votre tableau de bord [Render Dashboard](https://dashboard.render.com).
3. Cliquez sur **New +** -> **Blueprint**.
4. Séléctionnez votre dépôt Git `GrapheinAI`.
5. Render détectera automatiquement le fichier [render.yaml](file:///c:/Users/chris/Desktop/GrapheinAI/render.yaml) et proposera de créer 2 services :
   - **`graphein-ai-api`** : Serveur REST FastAPI (`uvicorn src.app.api:app`) avec health check automatique (`/health`).
   - **`graphein-ai-ui`** : Application Streamlit UI (`streamlit run app.py`).
6. Saisissez les valeurs des variables d'environnement requises (`GEMINI_API_KEY`, etc.).
7. Cliquez sur **Apply**.

---

## 8. Supervision & Health Checks

Les endpoints suivants sont disponibles pour les sondes Kubernetes et outils SRE (Datadog, Prometheus, UptimeRobot) :

- **Sonde de Santé** : `GET /health` ou `GET /api/health`
  ```json
  {
    "status": "healthy",
    "uptime_seconds": 342.12,
    "components": {
      "opencv_ocr": true,
      "cv_chart_detector": true,
      "graph_interpreter": true,
      "safe_calculator_ast": true,
      "gemini_vlm": true
    }
  }
  ```

- **Statut SRE & Métriques Mémoire/CPU** : `GET /status` ou `GET /api/status`
- **Informations de Version** : `GET /version` ou `GET /api/version`

---

## 9. Rotation des Logs & Sauvegardes

### Logs de Production
Les logs applicatifs structurés sont enregistrés automatiquement dans `logs/graphein_app.log` avec une rotation de **5 MB x 5 fichiers**.

### Stratégie de Sauvegarde Automatisée
Pour sauvegarder les données, images téléversées, rapports PDF et logs :

```bash
# Exécuter la sauvegarde manuellement
python scripts/backup_manager.py

# Conserver les 15 dernières sauvegardes
python scripts/backup_manager.py --keep 15
```

---

## 10. Directives de Sécurité Production
- **En-têtes HTTP de Sécurité (OWASP)** : `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection` et `Referrer-Policy` sont injectés automatiquement.
- **Protection Anti-Injection** : Toutes les requêtes utilisateur sont inspectées par le module `PromptInjectionGuard`.
- **Calcul Déterministe** : Évaluation isolée via l'AST Python `SafeCalculator` (aucun `eval()` dangereux).
- **Isolation Conteneur** : Exécution sous l'utilisateur Unix non-privilégié `graphein` (UID 1000).
