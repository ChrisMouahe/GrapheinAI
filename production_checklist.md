# ✅ Production Readiness Checklist — GraphEin AI Enterprise

**Projet** : GraphEin AI — SaaS Multimodal d'Analyse Graphique  
**Version Cible** : 5.0.0 Enterprise Production  
**Statut** : Grille de Validation Pré-Déploiement (Gatekeeper)

---

## 1. 🛡️ Sécurité & Conformité (Security Gate)

- [ ] **Gestion des Secrets & Environnement**
  - [ ] Les clés d'API de production (`GEMINI_API_KEY`, `SUPABASE_KEY`, `RESEND_API_KEY`, `SENTRY_DSN`) sont stockées dans un gestionnaire de secrets sécurisé (Vault / AWS Secrets Manager / Doppler) et ne résident jamais en clair dans le code.
  - [ ] Le fichier `.env` est exclu du contrôle de version (`.gitignore` validé).
  - [ ] La rotation automatique des clés et tokens est planifiée tous les 90 jours.
- [ ] **Authentification & Gestion des Droits**
  - [ ] Supabase Auth utilise des tokens JWT sécurisés avec expiration courte (1h) et refresh tokens rotatifs (7 jours).
  - [ ] Les politiques Row-Level Security (RLS) sont activées et vérifiées sur 100% des tables (`users`, `sessions`, `workspaces`, `workspace_members`, `comments`, `activity_logs`).
  - [ ] Le RBAC (`owner`, `admin`, `member`, `viewer`) bloque strictement les accès non autorisés aux endpoints de mutation.
- [ ] **Protection contre les Injections & Attaques**
  - [ ] Le module `PromptInjectionGuard` filtre toutes les requêtes entrantes avec expressions régulières et règles anti-jailbreak.
  - [ ] La validation des types MIME et des "Magic Bytes" bloque les fichiers non conformes (seuls PNG, JPEG, WEBP, PDF valides sont admis).
  - [ ] Les en-têtes HTTP de sécurité sont configurés (HSTS, CSP strict, X-Content-Type-Options, X-Frame-Options DENY).
  - [ ] Rate limiting actif au niveau Edge (Cloudflare WAF : 100 req/min/IP) et au niveau applicatif (`slowapi` / Redis).
- [ ] **Conformité RGPD & Souveraineté**
  - [ ] Registre des traitements de données validé par le DPO.
  - [ ] Fonctionnalité de suppression et d'anonymisation de compte ("Droit à l'oubli") testée et fonctionnelle.
  - [ ] Purge automatique des graphiques temporaires non sauvegardés après 24h d'inactivité.

---

## 2. ⚡ Architecture, Scalabilité & Performance (Infrastructure Gate)

- [ ] **Découpage & Conteneurisation**
  - [ ] Dockerfile multi-stage optimisé (taille d'image < 500 Mo, utilisateur non-root `appuser`).
  - [ ] Image Docker scannée contre les vulnérabilités CVE (Trivy / Snyk) sans vulnérabilité critique ou haute.
  - [ ] Séparation nette entre les conteneurs API FastAPI (ASGI) et les workers asynchrones (Celery / RQ).
- [ ] **Mise en Cache & Optimisation VLM**
  - [ ] Caching SHA-256 activé sur les graphiques pour éliminer 100% des appels VLM redondants.
  - [ ] Mode "Single-Pass Extraction" validé pour extraire métadonnées, séries et coordonnées en un seul appel API Gemini.
  - [ ] Index FAISS chargé en mémoire au démarrage (Lazy Loading des modèles lourds).
- [ ] **Haute Disponibilité & Résilience**
  - [ ] Déploiement multi-AZ (Minimum 2 réplicas API FastAPI avec Horizontal Pod Autoscaler).
  - [ ] Redis configuré en mode cluster avec persistance AOF/RDB et sentinelles de basculement.
  - [ ] Healthcheck endpoints actifs (`/health`, `/ready`) avec sondes Liveness & Readiness Kubernetes.

---

## 3. 🧪 Qualité du Code, Tests & MLOps (Quality Gate)

- [ ] **Couverture de Tests Automatisés**
  - [ ] 28 suites de tests unitaires et d'intégration exécutées avec succès (`pytest tests/`).
  - [ ] Tests de non-régression sur le moteur déterministe `SafeCalculator` (AST) validés à 100%.
  - [ ] Tests de charge et de concurrence exécutés (Locust / k6 : 200 utilisateurs simultanés avec p95 < 2.5s).
- [ ] **Garde-fous IA & Hallucination Zero**
  - [ ] Les calculs numériques sont systématiquement interceptés par l'AST et ne sont jamais confiés au texte brut du LLM.
  - [ ] Le `ValidationAgent` compare les séries VLM et les boîtes géométriques OpenCV pour attribuer un indice de confiance fiable.
  - [ ] Détection d'anomalies statistiques (Z-score / IQR) active sur les séries temporelles.
- [ ] **Qualité Statique & Linter**
  - [ ] Analyse statique de code validée avec Ruff et Flake8 (zéro avertissement bloquant).
  - [ ] Typage strict vérifié via `mypy` / Pydantic V2.

---

## 4. 📊 Observabilité, Logging & SRE (Operations Gate)

- [ ] **Logging Structuré**
  - [ ] Format de log JSON unifié (`Loguru`) avec corrélation `request_id` et `session_id`.
  - [ ] Anonymisation stricte des PII (adresses email, tokens) dans les flux de logs.
  - [ ] Rotation et rétention des logs configurées (30 jours sur disque / 1 an dans SIEM).
- [ ] **Métriques & Alerting**
  - [ ] Sentry APM configuré pour capturer 100% des erreurs 5xx avec stack trace complète.
  - [ ] Métriques Prometheus exposées (`http_requests_total`, `inference_duration_seconds`, `cache_hit_ratio`).
  - [ ] Alertes PagerDuty / Slack configurées sur les seuils critiques :
    - Taux d'erreur API > 1% sur 5 min.
    - Latence p95 > 5.0s.
    - Taux d'échec des appels Gemini API > 3%.
    - Espace disque base / stockage > 80%.

---

## 5. 💾 Sauvegardes, PCA & PRA (Business Continuity Gate)

- [ ] **Stratégie de Sauvegarde**
  - [ ] Sauvegardes PostgreSQL automatisées toutes les 24h avec conservation sur 30 jours.
  - [ ] Point-in-Time Recovery (PITR) activé sur Supabase (RPO < 5 minutes).
  - [ ] Stockage Cloudflare R2 / S3 configuré avec versioning des objets.
- [ ] **Plan de Continuité & Reprise d'Activité**
  - [ ] Procédure de Disaster Recovery documentée et testée en environnement de staging.
  - [ ] Objectif de RTO (Recovery Time Objective) < 30 minutes.
  - [ ] Objectif de RPO (Recovery Point Objective) < 15 minutes.

---

## 6. 💼 Support, Documentation & Go-to-Market (Product Gate)

- [ ] **Documentation & Contrats d'Interface**
  - [ ] Swagger OpenAPI interactif disponible sur `/docs` et `/redoc`.
  - [ ] Guides administrateur (`ADMIN_GUIDE.md`) et utilisateur (`USER_GUIDE.md`) à jour.
  - [ ] Conditions Générales d'Utilisation (CGU), Politique de Confidentialité et SLA d'entreprise (99.9%) rédigés et validés juridiquement.
- [ ] **Expérience Utilisateur & Validation Métier**
  - [ ] Interface Human-in-the-Loop (`AgGrid`) fonctionnelle pour corriger manuellement les extractions incertaines.
  - [ ] Export PDF vectoriel (`ReportLab`) et export Excel (`OpenPyXL`) validés sur tous les navigateurs.
  - [ ] Support multilingue (Français / Anglais) testé sur 100% des flux d'écrans et rapports.
