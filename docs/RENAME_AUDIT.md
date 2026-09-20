# Rapport d'Audit — Renommage LumiChart -> LumiChart

**Date de l'audit :** 2026-09-20  
**Portée de l'audit :** Scan exhaustif en lecture seule (code source, documentation, configurations, scripts, tests).  
**Statut :** Étape 0 terminée — En attente de validation explicite du fondateur.

---

## 1. Synthèse Chiffrée

- **Total d'occurrences dans le code source & documentation :** 464
- **Catégorie A (Identité Visuelle — Safe) :** 358
- **Catégorie B (Technique Visible — À valider) :** 83
- **Catégorie C (Technique Invisible & Interdit — Strictement Préservé) :** 23

*(Note : 884 occurrences supplémentaires dans les journaux `logs/graphein_app.log` et les sessions locales de test `data/sessions/` sont des données d'exécution volatiles et sont exclues du périmètre de refactorisation).*

---

## 2. Détail par Catégorie

### A. Catégorie A : Identité Visuelle & Documentation (Renommage en Vague 1 - Safe)
Ces éléments n'ont aucun impact sur la logique applicative, les tests ou les protocoles réseau.

| Composant / Fichier | Nombre | Nature du Contenu | Exemples de Chaînes | Risque |
| :--- | :---: | :--- | :--- | :---: |
| `DEPLOYMENT.md` | 15 | Documentation Markdown / texte explicatif | `# 🚀 Guide de Déploiement Production — LumiChart...` | `Safe` |
| `docs\SECRETS.md` | 15 | Documentation Markdown / texte explicatif | `# Guide Central de Gestion des Secrets & Sécurité — GraphEin...` | `Safe` |
| `src\app\static\index.html` | 14 | Texte d'interface utilisateur (titres, labels, boutons) | `<title>LumiChart \| Enterprise Data Analytics SaaS Platform<...` | `Safe` |
| `src\services\email\templates\template_renderer.py` | 14 | Commentaire ou docstring de code Python | `"""Email Template Renderer for LumiChart Enterprise Platfo...` | `Safe` |
| `docs\SPRINT0_PILIER1_REPORT.md` | 13 | Documentation Markdown / texte explicatif | `**Projet :** LumiChart Enterprise SaaS...` | `Safe` |
| `scripts\generate_all_pdfs.py` | 13 | Commentaire ou docstring de code Python | `"""High-grade ReportLab PDF Generator for LumiChart Techni...` | `Safe` |
| `scripts\generate_audit_md.py` | 13 | Commentaire ou docstring de code Python | `"""Script to generate the comprehensive, exhaustive master a...` | `Safe` |
| `scripts\build_full_comprehensive_audit_pdf.py` | 12 | Texte affiché, titre de rapport PDF ou template email | `OUTPUT_PDF = ROOT_DIR / "audit_complet_graphein_ai.pdf"...` | `Safe` |
| `scripts\build_full_v6_audit_pdf.py` | 10 | Texte affiché, titre de rapport PDF ou template email | `OUTPUT_PDF = ROOT_DIR / "audit_complet_graphein_ai_v6_produc...` | `Safe` |
| `docker-compose.yml` | 9 | Commentaire ou docstring de code Python | `# LumiChart — Docker Compose (Développement Local)...` | `Safe` |
| `Architecture.md` | 8 | Documentation Markdown / texte explicatif | `# 🏗 Manuel Spécificatif & Architecture Technique — GrapheinA...` | `Safe` |
| `archive\scripts\generate_soutenance_pdf.py` | 8 | Commentaire ou docstring de code Python | `"""Script de Génération des PDF de Soutenance Master — Graph...` | `Safe` |
| `docs\INFISICAL_GUIDE.md` | 8 | Documentation Markdown / texte explicatif | `# Guide Complet de Gestion des Secrets avec Infisical — Grap...` | `Safe` |
| `docker-compose.prod.yml` | 7 | Commentaire ou docstring de code Python | `# LumiChart — Docker Compose (Production Durcie)...` | `Safe` |
| `INSTALL.md` | 7 | Documentation Markdown / texte explicatif | `# 🛠️ Guide d'Installation & Dépannage — LumiChart...` | `Safe` |
| `README.md` | 7 | Documentation Markdown / texte explicatif | `# 📊 LumiChart — Plateforme SaaS d'Intelligence Graphique En...` | `Safe` |
| `ADMIN_GUIDE.md` | 6 | Documentation Markdown / texte explicatif | `# 🛠️ Guide d'Administration & SRE — LumiChart...` | `Safe` |
| `docs\API_KEYS_GUIDE.md` | 6 | Documentation Markdown / texte explicatif | `# 🔑 Guide des Clés API & Configuration d'Environnement - Gra...` | `Safe` |
| `scripts\build_full_roadmap_pdf.py` | 6 | Texte affiché, titre de rapport PDF ou template email | `self.drawString(36, 11 * 72 - 30, "LUMICHART AI — FEUILLE DE ...` | `Safe` |
| `Dockerfile` | 5 | Commentaire ou docstring de code Python | `# Multi-Stage Production Dockerfile for LumiChart...` | `Safe` |
| `SECURITY.md` | 5 | Documentation Markdown / texte explicatif | `# 🔒 Politique de Sécurité & Architecture de Protection — Gra...` | `Safe` |
| `docs\INFISICAL_SETUP.md` | 5 | Documentation Markdown / texte explicatif | `# Guide d'installation et configuration Infisical CLI — Grap...` | `Safe` |
| `scripts\build_full_exec_summary_pdf.py` | 5 | Texte affiché, titre de rapport PDF ou template email | `self.drawString(36, 11 * 72 - 30, "LUMICHART AI — EXECUTIVE S...` | `Safe` |
| `scripts\infisical_manager.py` | 5 | Commentaire ou docstring de code Python | `"""Script de gestion et d'audit des secrets Infisical pour G...` | `Safe` |
| `src\services\email_service.py` | 5 | Texte affiché, titre de rapport PDF ou template email | `self.sender_email = self.smtp_user if self.smtp_user and "@"...` | `Safe` |
| `src\services\supabase_service.py` | 5 | Texte affiché, titre de rapport PDF ou template email | `"email": "demo@graphein.ai",...` | `Safe` |
| `Makefile` | 4 | Commentaire ou docstring de code Python | `# LumiChart — Makefile d'Automatisation Docker, Infisical ...` | `Safe` |
| `scripts\backup_manager.py` | 4 | Commentaire ou docstring de code Python | `"""Production Automated Backup Manager for LumiChart....` | `Safe` |
| `scripts\build_full_bmc_pdf.py` | 4 | Texte affiché, titre de rapport PDF ou template email | `self.drawString(36, 11 * 72 - 30, "LUMICHART AI — BUSINESS MO...` | `Safe` |
| `scripts\generate_diagrams.py` | 4 | Commentaire ou docstring de code Python | `"""Script to generate architecture_target.drawio and archite...` | `Safe` |
| `src\app\api.py` | 4 | Texte affiché, titre de rapport PDF ou template email | `description="REST API backend for LumiChart Multimodal Visu...` | `Safe` |
| `.env.example` | 3 | Commentaire ou docstring de code Python | `# LumiChart — Enterprise Environment Variables Configurati...` | `Safe` |
| `API.md` | 3 | Documentation Markdown / texte explicatif | `# 🔌 Spécification Technique des API REST — LumiChart...` | `Safe` |
| `render.yaml` | 3 | Commentaire ou docstring de code Python | `# Render Blueprint configuration for LumiChart...` | `Safe` |
| `USER_GUIDE.md` | 3 | Documentation Markdown / texte explicatif | `# 📖 Guide Utilisateur — LumiChart...` | `Safe` |
| `docs\DOCKER.md` | 3 | Documentation Markdown / texte explicatif | `# Guide d'Architecture & Déploiement Docker — LumiChart...` | `Safe` |
| `docs\EMAIL_ARCHITECTURE.md` | 3 | Documentation Markdown / texte explicatif | `# Email Infrastructure Architecture - LumiChart Enterprise...` | `Safe` |
| `docs\EMAIL_CONFIGURATION.md` | 3 | Documentation Markdown / texte explicatif | `# Email Configuration Guide - LumiChart...` | `Safe` |
| `docs\EMAIL_TEMPLATES.md` | 3 | Documentation Markdown / texte explicatif | `# Email Templates Catalog & Customization Guide - GraphEin A...` | `Safe` |
| `docs\INFISICAL_SECRETS_MAP.md` | 3 | Documentation Markdown / texte explicatif | `# Cartographie des Secrets Infisical — LumiChart...` | `Safe` |
| `docs\KEY_ROTATION_PROCEDURE.md` | 3 | Documentation Markdown / texte explicatif | `# Procédure de Rotation des Clés & Secrets d'API — GrapheinA...` | `Safe` |
| `scripts\generate_excel_costs.py` | 3 | Commentaire ou docstring de code Python | `"""Generate professional Excel workbook for LumiChart cost...` | `Safe` |
| `src\app\user_journey_audit.py` | 3 | Commentaire ou docstring de code Python | `"""Automated User Journey Audit & UI/UX Evaluation Script fo...` | `Safe` |
| `src\i18n\translations\en.json` | 3 | Texte affiché, titre de rapport PDF ou template email | `"title": "LumiChart",...` | `Safe` |
| `src\i18n\translations\fr.json` | 3 | Texte affiché, titre de rapport PDF ou template email | `"title": "LumiChart",...` | `Safe` |
| `src\services\email\email_service.py` | 3 | Commentaire ou docstring de code Python | `"""Central EmailService module for LumiChart Enterprise Pl...` | `Safe` |
| `src\services\email\notifications\notification_service.py` | 3 | Commentaire ou docstring de code Python | `"""Multi-channel Notification Service for LumiChart (Email...` | `Safe` |
| `src\services\email\providers\brevo.py` | 3 | Commentaire ou docstring de code Python | `"""Brevo (Sendinblue) Email Provider for production email de...` | `Safe` |
| `.env` | 2 | Commentaire ou docstring de code Python | `# LUMICHART AI ENTERPRISE - CONFIGURATION DES RESSOURCES & CL...` | `Safe` |
| `.env.backup-20260920-131354` | 2 | Commentaire ou docstring de code Python | `# LUMICHART AI ENTERPRISE - CONFIGURATION DES RESSOURCES & CL...` | `Safe` |
| `DATAFLOW.md` | 2 | Documentation Markdown / texte explicatif | `# 🔄 Flux de Données & Pipelines — LumiChart...` | `Safe` |
| `docker-compose.infisical.yml` | 2 | Commentaire ou docstring de code Python | `# LumiChart — Docker Compose Override : Infisical Agent Si...` | `Safe` |
| `archive\scripts\render_optimized_video.py` | 2 | Texte affiché, titre de rapport PDF ou template email | `out_video = "0729/LumiChart_Demo_Optimized.mp4"...` | `Safe` |
| `docs\GEMINI_OPTIMIZATION.md` | 2 | Documentation Markdown / texte explicatif | `Ce document présente l'architecture optimisée du module IA d...` | `Safe` |
| `docs\PRE_COMMIT.md` | 2 | Documentation Markdown / texte explicatif | `# Guide des Hooks Pre-Commit & Détection de Secrets — Graphe...` | `Safe` |
| `docs\project_cleanup_report.md` | 2 | Documentation Markdown / texte explicatif | `# 📋 Rapport Officiel d'Audit & Nettoyage — LumiChart...` | `Safe` |
| `docs\SERVICE_ROLE_POLICY.md` | 2 | Documentation Markdown / texte explicatif | `# Politique d'Isolation de la Clé Supabase Service Role — Gr...` | `Safe` |
| `src\app\static\js\theme_manager.js` | 2 | Texte d'interface utilisateur (titres, labels, boutons) | `* ThemeManager - Instant Client-Side Light / Dark Theme Cont...` | `Safe` |
| `src\config\settings.py` | 2 | Texte affiché, titre de rapport PDF ou template email | `default=SecretStr("graphein_dev_insecure_secret_key_minimum_...` | `Safe` |
| `src\services\admin_service.py` | 2 | Texte affiché, titre de rapport PDF ou template email | `email="admin@graphein.ai",...` | `Safe` |
| `src\services\collaboration_service.py` | 2 | Texte affiché, titre de rapport PDF ou template email | `HMAC_SECRET = b"graphein_enterprise_collaboration_secret_key...` | `Safe` |
| `src\services\email\providers\base.py` | 2 | Commentaire ou docstring de code Python | `"""Abstract base class and data models for email providers i...` | `Safe` |
| `src\services\email\providers\maildev.py` | 2 | Commentaire ou docstring de code Python | `"""MailDev Email Provider for local development in GraphEin ...` | `Safe` |
| `src\services\email\providers\resend.py` | 2 | Commentaire ou docstring de code Python | `"""Resend Email Provider for production email delivery in Gr...` | `Safe` |
| `src\services\email\providers\smtp.py` | 2 | Commentaire ou docstring de code Python | `"""Generic Enterprise SMTP Email Provider for LumiChart.""...` | `Safe` |
| `src\services\email\tokens\token_service.py` | 2 | Commentaire ou docstring de code Python | `"""Generates, signs, verifies, and revokes secure time-bound...` | `Safe` |
| `.env.local` | 1 | Commentaire ou docstring de code Python | `# LUMICHART AI ENTERPRISE - CONFIGURATION LOCALE NON-SENSIBLE...` | `Safe` |
| `.pre-commit-config.yaml` | 1 | Commentaire ou docstring de code Python | `# LumiChart — Pre-commit Hooks Configuration...` | `Safe` |
| `app.py` | 1 | Commentaire ou docstring de code Python | `"""Root Application Entrypoint for LumiChart....` | `Safe` |
| `requirements-dev.txt` | 1 | Documentation Markdown / texte explicatif | `# LumiChart — Development & CI/CD Dependencies...` | `Safe` |
| `requirements.txt` | 1 | Documentation Markdown / texte explicatif | `# LumiChart Commercial Production Dependencies...` | `Safe` |
| `archive\scripts\test_zoom_keyframe.py` | 1 | Texte affiché, titre de rapport PDF ou template email | `cv2.putText(resized, f"LumiChart: {name.upper()}", (60, 78)...` | `Safe` |
| `docs\EMAIL_PROVIDER_GUIDE.md` | 1 | Documentation Markdown / texte explicatif | `# Email Provider Setup Guide - LumiChart...` | `Safe` |
| `docs\README.md` | 1 | Documentation Markdown / texte explicatif | `# Documentation Index — LumiChart...` | `Safe` |
| `scripts\audit_secrets.py` | 1 | Commentaire ou docstring de code Python | `"""Comprehensive Secret Scanner for LumiChart Codebase."""...` | `Safe` |
| `src\app\static\css\design_system.css` | 1 | Texte d'interface utilisateur (titres, labels, boutons) | `/* Enterprise SaaS Design System V2 - LumiChart */...` | `Safe` |
| `src\config\infisical_client.py` | 1 | Commentaire ou docstring de code Python | `"""Client d'intégration Infisical SecretOps pour LumiChart...` | `Safe` |
| `src\config\__init__.py` | 1 | Commentaire ou docstring de code Python | `"""Configuration package for LumiChart."""...` | `Safe` |
| `src\i18n\__init__.py` | 1 | Commentaire ou docstring de code Python | `"""Internationalization package for LumiChart."""...` | `Safe` |
| `src\models\user.py` | 1 | Commentaire ou docstring de code Python | `"""Enterprise User and authentication Pydantic v2 data model...` | `Safe` |
| `src\services\queue_manager.py` | 1 | Texte affiché, titre de rapport PDF ou template email | `self.executor = ThreadPoolExecutor(max_workers=max_workers, ...` | `Safe` |
| `src\services\__init__.py` | 1 | Commentaire ou docstring de code Python | `"""Services package for LumiChart."""...` | `Safe` |
| `src\services\email\__init__.py` | 1 | Commentaire ou docstring de code Python | `"""Email Services package for LumiChart Enterprise Infrast...` | `Safe` |
| `src\services\email\notifications\__init__.py` | 1 | Commentaire ou docstring de code Python | `"""Notification Service package for LumiChart."""...` | `Safe` |
| `src\services\email\providers\factory.py` | 1 | Commentaire ou docstring de code Python | `"""Email Provider Factory for dynamic provider instantiation...` | `Safe` |
| `src\services\email\providers\__init__.py` | 1 | Commentaire ou docstring de code Python | `"""Email Providers package for LumiChart Enterprise Email ...` | `Safe` |
| `src\services\email\queue\__init__.py` | 1 | Commentaire ou docstring de code Python | `"""Async Email Queue package for LumiChart."""...` | `Safe` |
| `src\services\email\templates\__init__.py` | 1 | Commentaire ou docstring de code Python | `"""Email Templates package for LumiChart."""...` | `Safe` |
| `src\services\email\tokens\invitation_manager.py` | 1 | Commentaire ou docstring de code Python | `"""Invitation Manager for LumiChart handling multi-tenant ...` | `Safe` |
| `src\services\email\tokens\__init__.py` | 1 | Commentaire ou docstring de code Python | `"""Tokens and Invitation Management package for LumiChart....` | `Safe` |
| `tests\test_email_platform.py` | 1 | Docstring / commentaire de test unitaire | `"""Comprehensive Unit & Integration Test Suite for GraphEin ...` | `Safe` |

---

### B. Catégorie B : Identifiants Techniques Visibles (Renommage en Vague 2 & 3 - À valider)
Ces éléments touchent à la configuration d'orchestration (Docker), à la documentation d'API (OpenAPI) ou aux jeux de données de test.

| Fichier / Emplacement | Ligne | Occurrence / Contexte | Raison / Impact | Risque |
| :--- | :---: | :--- | :--- | :---: |
| `docker-compose.infisical.yml` | L14 | `container_name: graphein-infisical-agent` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.infisical.yml` | L24 | `- graphein-dev-network` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L23 | `container_name: graphein-api-prod` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L73 | `- graphein-prod-network` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L81 | `container_name: graphein-redis-prod` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L108 | `- graphein-prod-network` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L114 | `graphein-prod-network:` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L116 | `name: graphein-prod-network` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L120 | `name: graphein-prod-data` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L122 | `name: graphein-prod-logs` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L124 | `name: graphein-prod-backups` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.prod.yml` | L126 | `name: graphein-redis-prod-data` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L26 | `container_name: graphein-api-dev` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L68 | `- graphein-dev-network` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L79 | `container_name: graphein-streamlit-dev` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L100 | `- graphein-dev-network` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L108 | `container_name: graphein-redis-dev` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L121 | `- graphein-dev-network` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L128 | `container_name: graphein-maildev-dev` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L140 | `- graphein-dev-network` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L146 | `graphein-dev-network:` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L148 | `name: graphein-dev-network` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L152 | `name: graphein-dev-data` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L154 | `name: graphein-dev-logs` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L156 | `name: graphein-dev-backups` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `docker-compose.yml` | L158 | `name: graphein-redis-dev-data` | Noms de conteneurs, réseaux et volumes Docker (ex: graphein-api-dev) | `À valider` |
| `pyproject.toml` | L9 | `authors = [{ name = "LumiChart Team" }]` | Métadonnées de nom de projet et auteurs dans pyproject.toml | `À valider` |
| `src\app\api.py` | L105 | `title="LumiChart SaaS Enterprise API",` | Titre OpenAPI FastAPI exposé aux clients de l'API | `À valider` |
| `src\utils\structured_logger.py` | L14 | `LOG_FILE = LOG_DIR / "graphein_app.log"` | Nom de fichier du journal applicatif | `À valider` |
| `tests\test_admin_console.py` | L93 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_admin_console.py` | L154 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_auth_supabase.py` | L21 | `auth_res = service.signup(email="alice@graphein.ai", password="Pa` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_auth_supabase.py` | L23 | `assert auth_res.user.email == "alice@graphein.ai"` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_auth_supabase.py` | L28 | `login_res = service.login(email="alice@graphein.ai", password="Pa` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_auth_supabase.py` | L47 | `user_a = service.signup(email="usera@graphein.ai", password="Pass` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_auth_supabase.py` | L48 | `user_b = service.signup(email="userb@graphein.ai", password="Pass` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_auth_supabase.py` | L74 | `res_signup = client.post("/api/auth/signup", json={"email": "bob@` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_auth_supabase.py` | L84 | `assert me_data["email"] == "bob@graphein.ai"` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_chart_intelligence.py` | L139 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_collaboration_workspaces.py` | L23 | `email="alice.owner@graphein.ai",` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_collaboration_workspaces.py` | L35 | `email="bob.teammate@graphein.ai",` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_collaboration_workspaces.py` | L151 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L36 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L67 | `to_email="test.user@graphein.ai",` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L99 | `email="collab@graphein.ai",` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L109 | `assert payload.email == "collab@graphein.ai"` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L131 | `invitee_email="invitee@graphein.ai",` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L141 | `invitee_email="invitee@graphein.ai",` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L162 | `to_email="queue.test@graphein.ai",` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L211 | `assert "Graphein" in html_fr` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L228 | `job1 = svc.sendWelcomeEmail("user1@graphein.ai", "User One")` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L231 | `job2 = svc.sendVerificationEmail("user2@graphein.ai", "User Two")` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L234 | `job3 = svc.sendResetPassword("user3@graphein.ai", "User Three")` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L237 | `job4 = svc.sendWorkspaceInvitation("user4@graphein.ai", "Owner", ` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L240 | `job5 = svc.sendCollaboratorInvitation("user5@graphein.ai", "Owner` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L243 | `job6 = svc.sendAnalysisShared("user6@graphein.ai", "User Six", "B` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L246 | `job7 = svc.sendCommentNotification("user7@graphein.ai", "User Sev` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L249 | `job8 = svc.sendAnalysisFinished("user8@graphein.ai", "User Eight"` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L252 | `job9 = svc.sendOTP("user9@graphein.ai", "User Nine", "554433")` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L255 | `job10 = svc.sendPasswordChanged("user10@graphein.ai", "User Ten")` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L258 | `job11 = svc.sendProfileUpdated("user11@graphein.ai", "User Eleven` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L261 | `job12 = svc.sendAccountCreated("user12@graphein.ai", "User Twelve` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L264 | `job13 = svc.sendAccountDeleted("user13@graphein.ai", "User Thirte` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L267 | `job14 = svc.sendWorkspaceCreated("user14@graphein.ai", "User Four` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L270 | `job15 = svc.sendWorkspaceDeleted("user15@graphein.ai", "User Fift` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L279 | `json={"workspace_id": "ws_finance_2026", "invitee_email": "new.co` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_email_platform.py` | L292 | `assert data_ver["email"] == "new.collab@graphein.ai"` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_enterprise_hardening.py` | L212 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_enterprise_identity.py` | L106 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_enterprise_identity.py` | L115 | `assert me_res.json()["email"] == "demo@graphein.ai"` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_enterprise_identity.py` | L129 | `"email": "standard@graphein.ai",` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_enterprise_identity.py` | L151 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_enterprise_identity.py` | L197 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_explainability.py` | L116 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_gemini_optimization.py` | L162 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_multi_chart_intelligence.py` | L214 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_performance.py` | L178 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_personalized_ai.py` | L138 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_personalized_ai.py` | L160 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_product_polish.py` | L62 | `assert "Graphein" in res_html.text` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_session_management.py` | L78 | `login_res = client.post("/api/auth/login", json={"email": "demo@g` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_ui_design_system.py` | L87 | `assert "graphein_theme" in content` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |
| `tests\test_user_experience_polish.py` | L21 | `json={"email": "demo@graphein.ai", "password": "password123"},` | Données d'assertion ou mocks dans les tests (ex: demo@graphein.ai, LumiChart Corp) | `À valider` |

---

### C. Catégorie C : Identifiants Techniques Invisibles (STRICTEMENT INTERDITS DE RENOMMAGE)
> [!CAUTION]
> Ces éléments constituent le socle d'infrastructure externe (Supabase, Infisical, DNS, JWT, Git). **AUCUNE MODIFICATION** ne sera apportée à ces occurrences lors de cette mission.

| Fichier / Emplacement | Ligne | Valeur / Contexte | Raison de l'interdiction | Risque |
| :--- | :---: | :--- | :--- | :---: |
| `.env` | L29 | `EMAIL_FROM=no-reply@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `.env` | L41 | `SMTP_USER=notifications@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `.env.backup-20260920-131354` | L24 | `EMAIL_FROM=no-reply@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `.env.backup-20260920-131354` | L36 | `SMTP_USER=notifications@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `.env.example` | L72 | `EMAIL_FROM=no-reply@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `.env.example` | L84 | `SMTP_USER=notifications@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `.gitignore` | L2 | `# LumiChart — Reinforced .gitignore` | URL distante du dépôt Git (graphein-ai) | `Interdit` |
| `docs\API_KEYS_GUIDE.md` | L33 | `EMAIL_FROM=no-reply@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `docs\API_KEYS_GUIDE.md` | L42 | `SMTP_USER=notifications@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `docs\API_KEYS_GUIDE.md` | L84 | `EMAIL_FROM=no-reply@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `docs\API_KEYS_GUIDE.md` | L96 | `SMTP_USER=notifications@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `docs\EMAIL_CONFIGURATION.md` | L16 | `EMAIL_FROM=no-reply@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `docs\EMAIL_CONFIGURATION.md` | L39 | `SMTP_USER=notifications@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `docs\EMAIL_PROVIDER_GUIDE.md` | L48 | `EMAIL_FROM=no-reply@graphein.ai` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `docs\INFISICAL_SECRETS_MAP.md` | L32 | `\| `EMAIL_FROM` \| Email \| Oui \| Oui \| Adresse email expéditeur \| D` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `docs\INFISICAL_SECRETS_MAP.md` | L38 | `\| `SMTP_USER` \| Email \| Optionnel \| Optionnel \| Utilisateur SMTP ` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `src\config\settings.py` | L131 | `default="no-reply@graphein.ai",` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `src\services\email\providers\brevo.py` | L26 | `self.from_email = from_email or os.getenv("EMAIL_FROM", "no-reply` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `src\services\email\providers\maildev.py` | L29 | `self.from_email = from_email or os.getenv("EMAIL_FROM", "no-reply` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `src\services\email\providers\smtp.py` | L35 | `self.from_email = from_email or os.getenv("EMAIL_FROM", "no-reply` | Domaine d'envoi email actuel (graphein.ai actif jusqu'à migration DNS Vague 4) | `Interdit` |
| `supabase\schema.sql` | L3 | `-- LumiChart ChartQA SaaS Enterprise Platform` | Schéma/tables Supabase SQL (non modifiable sans migration BDD) | `Interdit` |
| `tests\test_settings.py` | L57 | `jwt_secret_key="graphein_dev_insecure_secret_key_minimum_32_chars` | Graine de clé secrète JWT de test (claims d'authentification) | `Interdit` |
| `tests\test_settings_infisical.py` | L104 | `jwt_secret_key=SecretStr("graphein_dev_insecure_secret_key_minimu` | Graine de clé secrète JWT de test (claims d'authentification) | `Interdit` |

---

## 3. Fichiers et Dossiers à Renommer

- **Fichiers Python / Packages :** Aucun package interne n'est nommé `graphein` (l'architecture utilise `src.agents`, `src.app`, `src.config`, `src.models`, `src.services`, `src.utils`, `src.i18n`).
- **Fichiers Journaux :** `logs/graphein_app.log` pourra être renommé en `logs/lumichart_app.log` lors de la Vague 3 (configuré dans `src/utils/structured_logger.py`).
- **Dossiers :** Aucun dossier source ne porte le nom `graphein`.

---

## 4. Occurrences dans l'Historique Git (Lecture Seule)

- Analyse de l'arbre Git : 0 commit ne contient le terme `graphein` dans son message de commit direct.
- L'historique Git reste **100% intact et non modifié**, conformément aux règles strictes du projet.

---

## 5. Points de Blocage & Dépendances Externes Identifiés

1. **Projet Infisical Cloud** :
   - Le nom du projet dans le dashboard Infisical est actuellement `LumiChart` (Workspace ID `0a5319ca-0b97-43a6-aadf-f778745f39a7`).
   - Action : Ce renommage se fera manuellement dans l'interface Infisical par le fondateur (documenté en Vague 4). Le fichier `.infisical.json` ne doit pas être altéré.
2. **Domaine Email & DNS (`graphein.ai`)** :
   - L'adresse expéditeur `no-reply@graphein.ai` et le domaine `graphein.ai` restent en place tant que le domaine `lumichart.ai` n'est pas validé chez Cloudflare et Resend.
3. **Conteneurs Docker** :
   - Le renommage des conteneurs (`graphein-api-dev` -> `lumichart-api-dev`) et volumes dans `docker-compose.yml` sera effectué en Vague 3 avec recréation des conteneurs au prochain démarrage.

---

## 6. Prochaine Étape (Sur Validation du Fondateur)

Dès validation de cette cartographie, exécution de la **Vague 1 (Renommage Cosmétique & Safe)** :
- `README.md`, `docs/*.md`
- Textes d'en-tête, docstrings et templates d'email
- `.env.example` (commentaires uniquement)
- Génération du diff complet pour revue avant commit.