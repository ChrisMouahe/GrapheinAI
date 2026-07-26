# 🛠️ Guide d'Installation & Dépannage — GraphEin AI

Ce guide contient toutes les instructions pour installer et exécuter **GraphEin AI** sur votre environnement local, dans un conteneur Docker ou sur les plateformes cloud.

---

## 📑 Table des Matières
1. [Prérequis Système](#1-prérequis-système)
2. [Méthode 1 : Installation Locale (Python Virtualenv)](#2-méthode-1--installation-locale-python-virtualenv)
3. [Méthode 2 : Déploiement Docker & Docker Compose](#3-méthode-2--déploiement-docker--docker-compose)
4. [Méthode 3 : Déploiement Streamlit Cloud & Hugging Face](#4-méthode-3--déploiement-streamlit-cloud--hugging-face)
5. [Foire Aux Questions (FAQ) & Dépannage](#5-foire-aux-questions-faq--dépannage)

---

## 1. Prérequis Système

| Composant | Version Minimale | Recommandé |
| :--- | :--- | :--- |
| **Système d'Exploitation** | Windows 10/11, Linux (Ubuntu 22.04+), macOS 13+ | Linux Ubuntu 22.04 LTS |
| **Python** | `3.12.0` | `3.12.3` |
| **Mémoire RAM** | 4 GB | 8 GB+ |
| **Espace Disque** | 1 GB | 5 GB |
| **Docker** | 24.0+ | Docker Desktop / Engine 25+ |

---

## 2. Méthode 1 : Installation Locale (Python Virtualenv)

### Étape 1 : Obtenir le Code Source
```bash
git clone https://github.com/your-org/GrapheinAI.git
cd GrapheinAI
```

### Étape 2 : Créer et Activer l'Environnement Virtuel
- **Sur Linux / macOS** :
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **Sur Windows (PowerShell)** :
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

### Étape 3 : Installer les Dépendances
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 4 : Configurer le Fichier d'Environnement
Créez un fichier `.env` à la racine du projet :
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

### Étape 5 : Lancer l'Application
```bash
# Lancer le serveur web REST API & SPA
python -m uvicorn src.app.api:app --host 127.0.0.1 --port 8088
```

Ouvrez votre navigateur sur `http://127.0.0.1:8088`.

---

## 3. Méthode 2 : Déploiement Docker & Docker Compose

### Lancement Simplifié avec Docker Compose
```bash
# Lancer l'API FastAPI et Streamlit simultanément
docker-compose up -d --build
```

### Lancement avec Docker CLI
```bash
# 1. Obtenir l'image
docker build -t graphein-ai:5.0.0 .

# 2. Exécuter
docker run -d \
  -p 8088:8088 \
  -e GEMINI_API_KEY="your_api_key" \
  --name graphein-container \
  graphein-ai:5.0.0
```

---

## 4. Méthode 3 : Déploiement Streamlit Cloud & Hugging Face

### Streamlit Community Cloud
1. Déposez votre projet sur GitHub.
2. Rendez-vous sur `share.streamlit.io` -> **New App**.
3. Choisissez le fichier d'entrée : `app.py`.
4. Dans **Settings -> Secrets**, ajoutez `GEMINI_API_KEY`.
5. Cliquez sur **Deploy**.

---

## 5. Foire Aux Questions (FAQ) & Dépannage

### ❓ Erreur : `ImportError: libGL.so.1: cannot open shared object file`
**Cause** : OpenCV nécessite les bibliothèques système Mesa sous Linux.  
**Solution** : Installez le paquet système sous Ubuntu/Debian :
```bash
sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

### ❓ Erreur : `GEMINI_API_KEY not configured`
**Cause** : La clé d'API Google Gemini n'est pas présente dans l'environnement.  
**Solution** : Assurez-vous d'avoir défini la variable d'environnement `GEMINI_API_KEY` dans votre fichier `.env` ou dans le terminal.
