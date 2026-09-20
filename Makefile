# ==============================================================================
# LumiChart — Makefile d'Automatisation Docker, Infisical SecretOps & Qualité
# ==============================================================================

.DEFAULT_GOAL := help

COMPOSE_DEV  := docker compose -f docker-compose.yml
COMPOSE_PROD := docker compose -f docker-compose.prod.yml
PYTHON       := python

.PHONY: help dev-up dev-down dev-ui prod-up prod-down logs logs-prod test test-docker lint lint-fix migrate clean status \
        infisical-login infisical-init dev-infisical ui-infisical test-infisical secrets-status secrets-audit secrets-pull

## Affiche l'ensemble des commandes disponibles avec leur description
help:
	@echo ""
	@echo "LumiChart — Commandes Disponibles :"
	@echo "=================================================================="
	@echo "  --- Environnements & Docker ---"
	@echo "  make dev-up          : Lance l'environnement de dev (API + Redis + MailDev)"
	@echo "  make dev-ui          : Lance dev avec l'interface Streamlit (--profile ui)"
	@echo "  make dev-down        : Arrête l'environnement de dev et supprime les orphelins"
	@echo "  make prod-up         : Lance l'environnement de production durci"
	@echo "  make prod-down       : Arrête l'environnement de production"
	@echo "  make status          : Affiche l'état des conteneurs en cours d'exécution"
	@echo "  make logs            : Suit les logs de l'environnement de dev"
	@echo "  make logs-prod       : Suit les logs de l'environnement de production"
	@echo ""
	@echo "  --- SecretOps & Infisical ---"
	@echo "  make infisical-login : Authentifie le CLI Infisical"
	@echo "  make infisical-init  : Lie le dépôt au projet Infisical (.infisical.json)"
	@echo "  make dev-infisical   : Lance l'API FastAPI avec injection de secrets Infisical"
	@echo "  make ui-infisical    : Lance l'UI Streamlit avec injection Infisical"
	@echo "  make test-infisical  : Exécute les tests pytest avec secrets Infisical"
	@echo "  make secrets-status  : Vérifie l'état de connexion à Infisical"
	@echo "  make secrets-audit   : Audite la conformité des secrets par rapport à .env.example"
	@echo "  make secrets-pull    : Télécharge les secrets Infisical vers .env"
	@echo ""
	@echo "  --- Qualité & Tests ---"
	@echo "  make test            : Exécute la suite de tests unitaires et intégration (local)"
	@echo "  make test-docker     : Exécute les tests dans le conteneur API dev"
	@echo "  make lint            : Vérifie la qualité et le style de code (Ruff + Black)"
	@echo "  make lint-fix        : Corrige automatiquement les erreurs de linting"
	@echo "  make migrate         : Vérifie et valide le schéma SQL Supabase"
	@echo "  make clean           : Supprime les caches Python et fichiers temporaires"
	@echo "=================================================================="
	@echo ""

## Démarre les services de développement (FastAPI hot-reload, Redis, MailDev)
dev-up:
	@echo "[*] Démarrage de l'environnement de développement LumiChart..."
	$(COMPOSE_DEV) up -d --build api redis maildev
	@echo "[+] Services démarrés :"
	@echo "    - API FastAPI  : http://localhost:8088 (Docs: http://localhost:8088/docs)"
	@echo "    - MailDev Web  : http://localhost:1080"
	@echo "    - Redis        : Interne (redis:6379)"

## Démarre l'environnement de développement complet incluant le dashboard Streamlit
dev-ui:
	@echo "[*] Démarrage avec le profil UI (FastAPI + Streamlit + Redis + MailDev)..."
	$(COMPOSE_DEV) --profile ui up -d --build
	@echo "[+] Services démarrés :"
	@echo "    - API FastAPI   : http://localhost:8088"
	@echo "    - Streamlit UI  : http://localhost:8501"
	@echo "    - MailDev Web   : http://localhost:1080"

## Arrête les services de développement
dev-down:
	@echo "[*] Arrêt des services de développement..."
	$(COMPOSE_DEV) down --remove-orphans
	@echo "[+] Environnement de dev arrêté."

## Démarre l'environnement de production durci
prod-up:
	@echo "[*] Démarrage de l'environnement de production durci..."
	$(COMPOSE_PROD) up -d --build
	@echo "[+] Production démarrée :"
	@echo "    - API FastAPI : http://localhost:8088/health"
	@echo "    - Redis AOF   : Réseau interne sécurisé (non exposé)"

## Arrête l'environnement de production
prod-down:
	@echo "[*] Arrêt des services de production..."
	$(COMPOSE_PROD) down --remove-orphans
	@echo "[+] Environnement de production arrêté."

## Affiche les logs en continu de l'environnement de développement
logs:
	$(COMPOSE_DEV) logs -f

## Affiche les logs en continu de l'environnement de production
logs-prod:
	$(COMPOSE_PROD) logs -f

## Infisical SecretOps Commands
infisical-login:
	@echo "[*] Connexion au CLI Infisical..."
	infisical login

infisical-init:
	@echo "[*] Initialisation du projet Infisical..."
	infisical init

dev-infisical:
	@echo "[*] Démarrage FastAPI avec injection directe des secrets Infisical..."
	infisical run --env=dev -- python -m uvicorn src.app.api:app --host 0.0.0.0 --port 8088 --reload

ui-infisical:
	@echo "[*] Démarrage Streamlit avec injection directe des secrets Infisical..."
	infisical run --env=dev -- streamlit run src/ui/streamlit_app.py --server.port 8501

test-infisical:
	@echo "[*] Lancement des tests pytest avec secrets Infisical (env=test)..."
	infisical run --env=test -- $(PYTHON) -m pytest tests/ -v

secrets-status:
	@echo "[*] Diagnostic de configuration et connectivité Infisical..."
	$(PYTHON) scripts/infisical_manager.py status

secrets-audit:
	@echo "[*] Audit de conformité des secrets applicatifs..."
	$(PYTHON) scripts/infisical_manager.py audit

secrets-pull:
	@echo "[*] Téléchargement des secrets depuis Infisical vers .env..."
	$(PYTHON) scripts/infisical_manager.py pull --force

## Exécute les tests unitaires et d'intégration en local
test:
	@echo "[*] Lancement des tests pytest..."
	$(PYTHON) -m pytest tests/ -v

## Exécute les tests à l'intérieur du conteneur API dev
test-docker:
	@echo "[*] Lancement des tests dans le conteneur graphein-api-dev..."
	$(COMPOSE_DEV) exec api pytest tests/ -v

## Vérifie la conformité du code avec Ruff et Black
lint:
	@echo "[*] Vérification du code avec Ruff..."
	$(PYTHON) -m ruff check .
	@echo "[*] Vérification du formatage avec Black..."
	$(PYTHON) -m black --check .

## Applique les corrections automatiques de linting et de formatage
lint-fix:
	@echo "[*] Correction automatique du linting..."
	$(PYTHON) -m ruff check --fix .
	@echo "[*] Formatage automatique du code..."
	$(PYTHON) -m black .

## Vérifie l'état et l'intégrité du schéma de base de données Supabase
migrate:
	@echo "[*] Vérification du schéma SQL Supabase (supabase/schema.sql)..."
	@if [ -f supabase/schema.sql ]; then \
		echo "[+] Fichier supabase/schema.sql présent (taille: $$(wc -c < supabase/schema.sql) octets)."; \
		echo "[+] Pour appliquer les migrations : utilisez Supabase CLI ('supabase db push') ou Infisical."; \
	else \
		echo "[!] Aucun fichier schema.sql détecté dans supabase/."; \
	fi

## Affiche le statut des conteneurs
status:
	@echo "--- Conteneurs Dev ---"
	$(COMPOSE_DEV) ps
	@echo "--- Conteneurs Prod ---"
	$(COMPOSE_PROD) ps

## Nettoie les fichiers temporaires et les caches
clean:
	@echo "[*] Nettoyage des caches Python et artefacts..."
	@rm -rf .pytest_cache .ruff_cache htmlcov coverage.xml .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.py[cod]" -delete 2>/dev/null || true
	@echo "[+] Nettoyage terminé."
