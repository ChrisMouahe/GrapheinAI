# Email Configuration Guide - GraphEin AI

## Environment Variables (.env)

Configure all email infrastructure options in your root `.env` file:

```env
# ====================================================================
# ENTERPRISE EMAIL PLATFORM CONFIGURATION
# ====================================================================

# Active Provider ('maildev', 'resend', 'brevo', 'smtp')
EMAIL_PROVIDER=maildev

# Default Sender Identity
EMAIL_FROM=no-reply@graphein.ai
EMAIL_NAME=GraphEin AI Enterprise

# Application Public Base URL
APP_BASE_URL=http://localhost:8088

# JWT Signing Secret Key
JWT_SECRET_KEY=graphein_enterprise_secret_key_2026

# Local MailDev Configuration (Development)
MAILDEV_HOST=localhost
MAILDEV_PORT=1025
MAILDEV_WEB_PORT=1080

# Resend API Key (Production)
RESEND_API_KEY=re_123456789_abcdefg

# Brevo (Sendinblue) API Key (Production)
BREVO_API_KEY=xkeysib-123456789-abcdefg

# Generic SMTP Configuration (Production)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@graphein.ai
SMTP_PASSWORD=your_app_password_here
SMTP_USE_TLS=true
```

---

## Provider Selection Matrix

| `EMAIL_PROVIDER` | Environment | Protocol / Transport | Required Credentials |
| :--- | :--- | :--- | :--- |
| `maildev` | Development / Local | SMTP (`localhost:1025`) | None |
| `resend` | Production | HTTPS REST API | `RESEND_API_KEY` |
| `brevo` | Production | HTTPS REST API | `BREVO_API_KEY` |
| `smtp` | Production / Staging | Generic SMTP (`TLS/SSL`) | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` |

---

## Switching Providers in Production

To switch providers, update `EMAIL_PROVIDER` in `.env` or issue an admin REST API request:

```bash
curl -X POST "http://localhost:8088/api/admin/email/provider" \
     -H "Authorization: Bearer <ADMIN_JWT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"provider_name": "resend"}'
```
