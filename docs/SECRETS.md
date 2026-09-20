# Guide Central de Gestion des Secrets & Sécurité — LumiChart

Ce document constitue la **documentation unique de référence** pour la gestion, la rotation, l'isolation et la gouvernance des secrets de l'application SaaS LumiChart.

---

## 1. Vue d'Ensemble de l'Architecture des Secrets

LumiChart utilise **Infisical SecretOps** comme source unique de vérité (*Single Source of Truth*) pour tous les environnements (`development`, `staging`, `production`).

```
                              ┌───────────────────────────────────┐
                              │     Infisical Cloud (Vault)       │
                              │   Workspace ID: 0a5319ca-...      │
                              └─────────────────┬─────────────────┘
                                                │
                     ┌──────────────────────────┼──────────────────────────┐
                     ▼                          ▼                          ▼
            [ Dev Local ]               [ Staging (CI/CD) ]         [ Production ]
         CLI: `infisical run`        Token: `INFISICAL_TOKEN`     Machine Identity
                 │                              │                          │
                 ▼                              ▼                          ▼
         os.environ injecté             os.environ injecté         os.environ / SDK
```

### Principes Clés
1. **Zéro Secret dans Git** : Aucun secret réel dans les fichiers `.env`, `.env.example`, commits ou branches.
2. **Pydantic `SecretStr`** : Tous les secrets sont typés en `SecretStr` dans [src/config/settings.py](file:///c:/Users/chris/Desktop/LumiChart/src/config/settings.py), garantissant le masquage automatique (`**********`) dans les logs et exceptions.
3. **Backend-Only Isolation** : La clé `SUPABASE_SERVICE_ROLE_KEY` (P1) est strictement réservée au backend et ne doit jamais atteindre le frontend.

---

## 2. Procédure d'Onboarding pour un Nouveau Développeur

1. **Installer la CLI Infisical** :
   ```powershell
   # Windows (Scoop ou Winget)
   scoop bucket add infisical https://github.com/Infisical/scoop-infisical.git
   scoop install infisical
   ```
   *(Voir guide complet : [docs/INFISICAL_SETUP.md](file:///c:/Users/chris/Desktop/LumiChart/docs/INFISICAL_SETUP.md))*

2. **S'authentifier et lier le projet** :
   ```bash
   infisical login
   infisical init
   ```
   *(Sélectionner le projet `LumiChart`)*

3. **Lancer l'application avec injection des secrets** :
   ```bash
   # Démarrer FastAPI en dev
   infisical run --env=dev -- uvicorn src.app.api:app --reload --port 8088

   # Lancer avec Docker Compose
   infisical run --env=dev -- docker-compose up
   ```

---

## 3. Matrice Exhaustive des Secrets

| Nom de Variable | Criticité | Environnements | Description & Impact |
| :--- | :---: | :---: | :--- |
| `GEMINI_API_KEY` | **P1 (Coût)** | dev, staging, prod | Clé API Google AI Studio pour le VLM Gemini 2.5 Flash |
| `SUPABASE_SERVICE_ROLE_KEY` | **P1 (Admin)** | dev, staging, prod | Clé d'administration Supabase (Bypass RLS, Backend Only) |
| `RESEND_API_KEY` | **P1 (Email)** | dev, staging, prod | Clé d'envoi d'emails transactionnels Resend |
| `JWT_SECRET_KEY` | **P1 (Auth)** | dev, staging, prod | Clé de signature des tokens JWT (min 32 caractères) |
| `SUPABASE_URL` | P2 | dev, staging, prod | URL d'instance PostgreSQL Supabase |
| `SUPABASE_KEY` / `ANON` | P2 | dev, staging, prod | Clé API publique Anon Supabase |
| `EMAIL_PROVIDER` | P2 | dev, staging, prod | Fournisseur actif (`maildev`, `resend`, `brevo`, `smtp`) |
| `REDIS_URL` | P3 | staging, prod | URL broker/cache Redis (Sprint 3) |

*(Voir détails exhaustifs : [docs/INFISICAL_SECRETS_MAP.md](file:///c:/Users/chris/Desktop/LumiChart/docs/INFISICAL_SECRETS_MAP.md))*

---

## 4. Procédure de Rotation des Clés

1. Générer la nouvelle clé chez le fournisseur tiers (Google AI Studio, Resend, Supabase).
2. Mettre à jour la variable dans Infisical :
   ```bash
   infisical secrets set GEMINI_API_KEY="<NOUVELLE_CLE>" --env=dev
   ```
3. Exécuter le script d'audit de rotation :
   ```bash
   python scripts/verify_key_rotation.py
   ```
4. Révoquer l'ancienne clé sur la console du fournisseur tiers.

*(Voir procédure détaillée : [docs/KEY_ROTATION_PROCEDURE.md](file:///c:/Users/chris/Desktop/LumiChart/docs/KEY_ROTATION_PROCEDURE.md))*

---

## 5. Procédure d'Urgence (Secret Compromis)

Si un secret est suspecté d'avoir fuité (ex: commit accidentel, alerte fournisseur) :

1. **Générer immédiatement** une nouvelle clé chez le fournisseur.
2. **Écraser instantanément** le secret dans Infisical pour tous les environnements (`dev`, `staging`, `prod`).
3. **Révoquer sans délai** la clé compromise sur le tableau de bord du fournisseur (bloque tout usage malveillant).
4. **Redémarrer les services** :
   ```bash
   docker-compose restart
   ```
5. **Vérifier les logs d'audit** (Google Cloud Console, Supabase logs, Resend logs) pour détecter d'éventuels abus.

---

## 6. Documents de Référence Associés

- 📖 [Guide d'Installation Infisical](file:///c:/Users/chris/Desktop/LumiChart/docs/INFISICAL_SETUP.md)
- 🗺️ [Cartographie des Secrets](file:///c:/Users/chris/Desktop/LumiChart/docs/INFISICAL_SECRETS_MAP.md)
- 🔄 [Procédure de Rotation des Clés](file:///c:/Users/chris/Desktop/LumiChart/docs/KEY_ROTATION_PROCEDURE.md)
- 🛡️ [Politique Supabase Service Role](file:///c:/Users/chris/Desktop/LumiChart/docs/SERVICE_ROLE_POLICY.md)
- 🪝 [Configuration Pre-Commit & Detect-Secrets](file:///c:/Users/chris/Desktop/LumiChart/docs/PRE_COMMIT.md)
- 🐳 [Guide Déploiement Docker](file:///c:/Users/chris/Desktop/LumiChart/docs/DOCKER.md)
- 📋 [Rapport de Clôture Pilier 1](file:///c:/Users/chris/Desktop/LumiChart/docs/SPRINT0_PILIER1_REPORT.md)
