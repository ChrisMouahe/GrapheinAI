# Cartographie des Secrets Infisical — LumiChart

Ce document détaille la cartographie exhaustive des variables d'environnement et secrets gérés dans **Infisical SecretOps** pour les environnements `dev`, `staging` et `production`.

---

## 1. État des Lieux par Environnement dans Infisical

| Environnement Infisical | Statut | Nombre de Secrets | Actions requises |
| :--- | :--- | :--- | :--- |
| **`dev`** | ✅ Actif | 19 secrets configurés | À jour avec les nouvelles clés Gemini & Resend |
| **`staging`** | 🟡 Vide | 0 secret | À renseigner lors de la mise en place du Pilier 2 |
| **`prod`** | 🟡 Vide | 0 secret | À renseigner avant le déploiement en production |

---

## 2. Matrice Exhaustive des Variables et Secrets

| Variable / Secret | Catégorie | Requis en Dev | Requis en Prod | Description | Source / Où l'obtenir | Exemple Masqué |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- |
| `ENVIRONMENT` | Core | Oui | Oui | Type d'environnement (`development`, `staging`, `production`) | Config locale / CI-CD | `development` |
| `LOG_LEVEL` | Core | Oui | Oui | Niveau de logs (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | Config locale | `INFO` |
| `PORT` | Core | Oui | Oui | Port d'écoute du serveur ASGI / FastAPI | Config locale | `8088` |
| `APP_BASE_URL` | Core | Oui | Oui | URL de base de l'application | Dashboard hébergeur | `http://localhost:8088` |
| `JWT_SECRET_KEY` | Sécurité P1 | Oui | Oui | Clé secrète de signature des tokens JWT (min 32 chars) | `openssl rand -hex 32` | `800e8793...036ab3` |
| `GEMINI_API_KEY` | IA / Coût P1 | Oui | Oui | Clé API Google AI Studio pour le VLM Gemini Flash | [Google AI Studio](https://aistudio.google.com/) | `AQ.Ab8RN...R6kA` |
| `GEMINI_MODEL` | IA | Optionnel | Optionnel | Modèle Gemini Flash utilisé | Google AI Studio | `gemini-2.5-flash` |
| `SUPABASE_URL` | BDD | Oui | Oui | URL du projet Supabase PostgreSQL | [Supabase Console](https://supabase.com/dashboard) | `https://djhjnb...co` |
| `SUPABASE_KEY` / `ANON` | BDD | Oui | Oui | Clé publique Supabase Anon (respecte les règles RLS) | Supabase API Settings | `eyJhbGciOi...5Vk5pLo` |
| `SUPABASE_SERVICE_ROLE_KEY` | BDD P1 | Oui | Oui | Clé admin Supabase (Bypass RLS, STRICTEMENT Backend) | Supabase API Settings | `eyJhbGciOi...wzKgauBI` |
| `EMAIL_PROVIDER` | Email | Oui | Oui | Fournisseur actif (`maildev`, `resend`, `brevo`, `smtp`) | Architecture email | `resend` |
| `EMAIL_FROM` | Email | Oui | Oui | Adresse email expéditeur | Domaine validé | `no-reply@graphein.ai` |
| `EMAIL_NAME` | Email | Oui | Oui | Nom affiché de l'expéditeur | Config | `LumiChart Enterprise` |
| `RESEND_API_KEY` | Email P1 | Oui | Oui | Clé API Resend (si `EMAIL_PROVIDER=resend`) | [Resend Dashboard](https://resend.com/api-keys) | `re_M3c5GF...82G1w` |
| `BREVO_API_KEY` | Email | Optionnel | Optionnel | Clé API Brevo (si `EMAIL_PROVIDER=brevo`) | [Brevo Dashboard](https://brevo.com/) | `xkeysib-...cdefg` |
| `SMTP_HOST` | Email | Optionnel | Optionnel | Hôte SMTP | Serveur mail | `smtp.gmail.com` |
| `SMTP_PORT` | Email | Optionnel | Optionnel | Port SMTP | Serveur mail | `587` |
| `SMTP_USER` | Email | Optionnel | Optionnel | Utilisateur SMTP | Serveur mail | `notifications@graphein.ai` |
| `SMTP_PASSWORD` | Email | Optionnel | Optionnel | Mot de passe SMTP | Serveur mail | `votre_mot_de_...` |
| `SMTP_USE_TLS` | Email | Optionnel | Optionnel | Activer TLS pour SMTP | Serveur mail | `true` |
| `MAILDEV_HOST` | Email Dev | Optionnel | Non | Hôte MailDev local | Local Docker | `localhost` |
| `MAILDEV_PORT` | Email Dev | Optionnel | Non | Port SMTP MailDev | Local Docker | `1025` |
| `MAILDEV_WEB_PORT` | Email Dev | Optionnel | Non | Port UI Web MailDev | Local Docker | `1080` |
| `CINETPAY_API_KEY` | Paiement | Non | Non | Clé API Mobile Money (Sprint 2) | CinetPay Dashboard | `(À venir Sprint 2)` |
| `CINETPAY_SECRET_KEY` | Paiement | Non | Non | Clé secrète webhook CinetPay (Sprint 2) | CinetPay Dashboard | `(À venir Sprint 2)` |
| `REDIS_URL` | Cache/Queue | Optionnel | Oui | URL de connexion Redis (Sprint 3) | Upstash / Redis Cloud | `redis://localhost:6379/0` |
| `SENTRY_DSN` | Monitoring | Optionnel | Oui | DSN de capture Sentry | Sentry Dashboard | `https://...@sentry.io/...` |
| `BETTERSTACK_TOKEN` | Heartbeat | Optionnel | Oui | Token de monitoring Better Stack | Better Stack Dashboard | `(Optionnel)` |

---

## 3. Procédure de Synchronisation des Environnements `staging` et `prod`

Lorsque les environnements de préproduction et production seront déployés (Pilier 2) :

1. Se connecter à Infisical CLI ou Dashboard Cloud :
   ```bash
   # Injection d'un secret en staging
   infisical secrets set GEMINI_API_KEY="<CLE_GEMINI_STAGING>" --env=staging
   infisical secrets set SUPABASE_URL="<URL_SUPABASE_STAGING>" --env=staging

   # Injection d'un secret en production
   infisical secrets set GEMINI_API_KEY="<CLE_GEMINI_PROD>" --env=prod
   infisical secrets set SUPABASE_URL="<URL_SUPABASE_PROD>" --env=prod
   ```
2. Pour cloner les variables non-sensibles de `dev` vers `staging` :
   - Rendez-vous sur https://app.infisical.com > Projet LumiChart > Environments.
   - Sélectionnez les secrets partagés et utilisez la fonction d'import/export ou de synchronisation d'environnement.
