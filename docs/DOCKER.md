# Guide d'Architecture & Déploiement Docker — LumiChart

Ce document détaille la stratégie de conteneurisation de **LumiChart** (FastAPI, Streamlit, Supabase, Google Gemini 2.5 Flash, Redis, MailDev, Infisical). Il décrit le fonctionnement des environnements de développement et de production durcie, ainsi que l'utilisation du `Makefile` et de la CLI **Infisical**.

---

## 1. Vue d'Ensemble & Philosophie d'Architecture

La conteneurisation de LumiChart repose sur une séparation stricte entre deux topologies :

| Critère | Développement (`docker-compose.yml`) | Production (`docker-compose.prod.yml`) |
| :--- | :--- | :--- |
| **Objectif** | Itération rapide, debug, hot-reload | Haute disponibilité, immuabilité, sécurité |
| **Secrets** | Injection dynamique `infisical run` ou `.env.local` | Machine Identity Infisical ou `INFISICAL_TOKEN` |
| **Code Source** | Volume monté en temps réel (`.:/app`) | Bâti dans l'image (immuable, aucun montage de code) |
| **Serveur ASGI** | Uvicorn avec `--reload` (1 worker) | Uvicorn multi-workers (`--workers 4`) |
| **Streamlit UI** | Inclus sous profil optionnel (`--profile ui`) | Séparé (Cloud indépendant ou profil dédié) |
| **Persistance Redis**| En mémoire volatile (démarrage instantané) | AOF (*Append-Only File*) synchronisé chaque seconde |
| **Exposition Réseau**| Ports API (8088), MailDev UI (1080) | Port API (8088) uniquement ; **Redis non exposé** |
| **Emails** | MailDev local (capture SMTP sur 1025) | Provider transactionnel externe (Resend / Brevo) |
| **Ressources** | Non bridées (pleine puissance machine) | Limites strictes CPU (2.0) et RAM (2 Go) |

---

## 2. Démarrage Rapide avec Infisical (Recommandé)

Grâce à l'intégration Infisical SecretOps (Pilier 1), aucun secret réel n'est stocké en clair dans le fichier `.env`.

### A. Lancer en Développement avec Infisical CLI
```bash
# 1. Lancer l'API + Redis + MailDev avec injection des secrets 'dev'
infisical run --env=dev -- docker-compose up

# 2. Lancer avec le dashboard Streamlit inclus
infisical run --env=dev -- docker-compose --profile ui up

# 3. Exécuter en arrière-plan (mode détaché)
infisical run --env=dev -- docker-compose up -d
```

### B. Lancer en Développement sans Infisical CLI (Fallback local)
Si la CLI Infisical n'est pas installée :
```bash
# Créer .env.local depuis .env.example
cp .env.example .env.local

# Lancer Docker Compose directement
docker-compose up
```

---

## 3. Déploiement en Production (`docker-compose.prod.yml`)

En environnement de production, les secrets sont injectés via la Machine Identity Infisical ou le token de service système :

```bash
# Lancement avec Machine Identity
export INFISICAL_TOKEN="votre_token_machine_identity_prod"
docker-compose -f docker-compose.prod.yml up -d
```

---

## 4. Guide Rapide via le Makefile

Le projet dispose d'un `Makefile` standardisant toutes les opérations courantes :

```bash
# Afficher l'aide interactive
make help

# 1. Développement : Démarrer API + Redis + MailDev avec Infisical
make dev-up

# 2. Développement : Démarrer avec l'interface Streamlit
make dev-ui

# 3. Arrêter l'environnement de développement
make dev-down

# 4. Production : Lancer l'infrastructure durcie
make prod-up

# 5. Suivre les logs en direct
make logs          # Dev
make logs-prod     # Prod

# 6. Lancer les tests
make test          # En local
make test-docker   # Dans le conteneur API
```
