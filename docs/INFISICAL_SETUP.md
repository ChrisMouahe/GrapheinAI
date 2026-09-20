# Guide d'installation et configuration Infisical CLI — LumiChart

Ce guide détaille l'installation, la configuration et l'utilisation de la CLI **Infisical** pour la gestion centralisée et sécurisée des secrets du projet LumiChart.

---

## 1. Installation de la CLI Infisical

### Windows (PowerShell / Terminal)
```powershell
# Option A : Scoop (Recommandé)
scoop bucket add infisical https://github.com/Infisical/scoop-infisical.git
scoop install infisical

# Option B : Winget
winget install Infisical.InfisicalCLI

# Option C : Script direct
irm https://cli.infisical.com/install.ps1 | iex
```

### macOS (Homebrew)
```bash
brew install infisical/get-cli/infisical
```

### Linux (Debian / Ubuntu)
```bash
curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | sudo -E bash
sudo apt-get update && sudo apt-get install -y infisical
```

### Vérification de l'installation
```bash
infisical --version
# Doit afficher: infisical version x.y.z (ex: 0.43.132)
```

---

## 2. Authentification et liaison au projet

### Connexion au compte Infisical Cloud
```bash
infisical login
```
Une page de navigateur s'ouvre pour vous authentifier sur le Cloud Infisical.

### Initialisation / Liaison au projet LumiChart
À la racine du projet (`c:\Users\chris\Desktop\LumiChart`) :
```bash
infisical init
```
Sélectionnez le projet **LumiChart** (Workspace ID : `0a5319ca-0b97-43a6-aadf-f778745f39a7`).
Le fichier `.infisical.json` est alors généré à la racine.

---

## 3. Commandes quotidiennes

### Visualiser les secrets d'un environnement (valeurs masquées)
```bash
infisical secrets --env=dev
infisical secrets --env=staging
infisical secrets --env=prod
```

### Exécuter l'application avec injection automatique des secrets
```bash
# Lancer l'API FastAPI en local avec injection des secrets
infisical run --env=dev -- uvicorn src.app.api:app --reload --port 8088

# Lancer les tests pytest avec les variables injectées
infisical run --env=dev -- pytest

# Lancer Docker Compose
infisical run --env=dev -- docker-compose up
```
