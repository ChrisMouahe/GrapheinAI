# 🔑 Guide des Clés API & Configuration d'Environnement - GraphEin AI Enterprise

Ce document répertorie l'ensemble des **clés API, identifiants et secrets d'environnement** nécessaires au fonctionnement optimal de la plateforme GraphEin AI Enterprise.

---

## 1. 🤖 Clés API Principales & Moteurs d'Intelligence

| Variable `.env` | Module / Composant Utilisateur | Description & Utilisation | Obligatoire | Lien d'Obtention |
| :--- | :--- | :--- | :---: | :--- |
| `GEMINI_API_KEY` | **ReasoningAgent & PromptBuilder** | Analyse visuelle VLM des graphiques, OCR intelligent, détection de type de graphique, calculs contextuels et chat interactif. | **OBLIGATOIRE** | [Google AI Studio](https://aistudio.google.com/) |
| `SUPABASE_URL` | **SupabaseService** | URL de l'instance PostgreSQL Supabase pour l'authentification et l'isolation RLS multi-tenant. | **OBLIGATOIRE** | [Supabase Console](https://supabase.com/) |
| `SUPABASE_KEY` | **SupabaseService** | Clé publique anonyme ou rôle de service pour la gestion des sessions JWT et profils utilisateurs. | **OBLIGATOIRE** | [Supabase Console](https://supabase.com/) |

---

## 2. ✉️ Infrastructure Email (Selon le Fournisseur Choisi)

Le système d'emails est pluggable et s'adapte dynamiquement selon la variable `EMAIL_PROVIDER`.

### 🔹 Option A : Resend (Production Recommandée)
```env
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_123456789_abcdefg
EMAIL_FROM=onboarding@resend.dev
```
- **Obtention** : [Resend Console](https://resend.com/)

### 🔹 Option B : Brevo / Sendinblue (Production Alternative)
```env
EMAIL_PROVIDER=brevo
BREVO_API_KEY=xkeysib-123456789-abcdefg
EMAIL_FROM=no-reply@graphein.ai
```
- **Obtention** : [Brevo API Keys](https://www.brevo.com/)

### 🔹 Option C : SMTP Classique (AWS SES, Gmail, Postmark)
```env
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@graphein.ai
SMTP_PASSWORD=votre_mot_de_passe_application
SMTP_USE_TLS=true
```

### 🔹 Option D : MailDev (Développement Local)
```env
EMAIL_PROVIDER=maildev
MAILDEV_HOST=localhost
MAILDEV_PORT=1025
```
- **Aucune clé API requise**. Les emails sont visualisables sur l'UI locale `http://localhost:1080`.

---

## 3. 🛡️ Secrets de Sécurité & Configuration Système

| Variable `.env` | Usage Technique | Exemple de Valeur |
| :--- | :--- | :--- |
| `JWT_SECRET_KEY` | Signature cryptographique HMAC-SHA256 des tokens d'invitation workspace, de réinitialisation de mot de passe et de sécurité OTP par le `TokenService`. | `graphein_enterprise_secret_key_2026_x98f` |
| `APP_BASE_URL` | URL de base publique pour la génération des liens d'invitation et de réinitialisation dans les emails. | `http://localhost:8088` *(Dev)* / `https://app.graphein.ai` *(Prod)* |

---

## 📄 Modèle de Fichier `.env` Prêt à l'Emploi

Copiez ce contenu dans un fichier `.env` situé à la racine du projet :

```env
# ====================================================================
# GRAPHEIN AI ENTERPRISE - CONFIGURATION SYSTEME & CLES API
# ====================================================================

# 1. Moteur Gemini Flash Vision VLM
GEMINI_API_KEY=votre_cle_gemini_api_ici

# 2. Supabase Backend Services
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre_cle_anon_supabase_ici

# 3. Email Platform Config (maildev | resend | brevo | smtp)
EMAIL_PROVIDER=maildev
EMAIL_FROM=no-reply@graphein.ai
EMAIL_NAME=GraphEin AI Enterprise

# Si EMAIL_PROVIDER=resend
RESEND_API_KEY=re_123456789_abcdefg

# Si EMAIL_PROVIDER=brevo
BREVO_API_KEY=xkeysib-123456789-abcdefg

# Si EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@graphein.ai
SMTP_PASSWORD=votre_mot_de_passe_application

# 4. JWT & Application Base URL
JWT_SECRET_KEY=votre_cle_secrete_jwt_entreprise_tres_securisee
APP_BASE_URL=http://localhost:8088
```
