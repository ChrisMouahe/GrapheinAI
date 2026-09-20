# Changelog — LumiChart

Toutes les modifications notables apportées à ce projet sont documentées dans ce fichier.
Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/) et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [Unreleased] — Renommage GrapheinAI -> LumiChart (2026-09-20)

### 🎨 Identité Visuelle & Branding (Vagues 1 & 2)
- **Nouvelle Identité de Marque** : Renommage de la plateforme de *GrapheinAI* vers **LumiChart** (LumiChart Enterprise SaaS Platform).
- **Interface Utilisateur (SPA)** : Mise à jour du logo, en-têtes, sidebar, balises OpenGraph, Twitter Cards et descriptions de thème.
- **Documentation Exhaustive** : Mise à jour intégrale de tous les guides (`README.md`, `ADMIN_GUIDE.md`, `API.md`, `Architecture.md`, `DATAFLOW.md`, `DEPLOYMENT.md`, `INSTALL.md`, `SECURITY.md`, `USER_GUIDE.md` et `docs/*.md`).
- **Templates Transactionnels** : Mise à jour des en-têtes d'emailing, mentions légales et styles HTML vers LumiChart Enterprise.
- **Internationalisation (i18n)** : Mise à jour des fichiers de traduction `fr.json` et `en.json`.

### ⚙️ Orchestration & Infrastructure (Vague 3)
- **Docker Compose** : Renommage des conteneurs locaux et de production (`lumichart-api-dev`, `lumichart-api-prod`, `lumichart-streamlit-dev`, `lumichart-redis-dev`, `lumichart-maildev-dev`), ainsi que des réseaux et volumes associés.
- **Logging Structuré** : Mise à jour du journal d'application vers `logs/lumichart_app.log`.
- **Packaging** : Métadonnées du projet `pyproject.toml` actualisées.

### 🛡️ Sécurité & Préservation (Catégorie C)
- **Zero Breakage Guarantee** : Maintien strict des schémas de base de données PostgreSQL Supabase, des secrets Infisical et des claims JWT pour éviter toute interruption.
