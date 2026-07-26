# Email Provider Setup Guide - GraphEin AI

## 1. MailDev Setup (Development)

MailDev is an open-source SMTP server for local development with a clean web interface.

### Running MailDev
```bash
# Using npx
npx maildev --smtp 1025 --web 1080

# Or via Docker
docker run -d -p 1080:1080 -p 1025:1025 maildev/maildev
```

### Environment Settings
```env
EMAIL_PROVIDER=maildev
MAILDEV_HOST=localhost
MAILDEV_PORT=1025
```

Access sent emails visually at [http://localhost:1080](http://localhost:1080).

---

## 2. Resend Setup (Production API)

Resend is a modern developer-first email platform.

### Environment Settings
```env
EMAIL_PROVIDER=resend
RESEND_API_KEY=re_123456789_abcdefg
EMAIL_FROM=onboarding@resend.dev
```

---

## 3. Brevo Setup (Sendinblue API)

Brevo provides scalable transactional email APIs.

### Environment Settings
```env
EMAIL_PROVIDER=brevo
BREVO_API_KEY=xkeysib-123456789-abcdefg
EMAIL_FROM=no-reply@graphein.ai
```

---

## 4. Generic SMTP / AWS SES Setup

Use any standard SMTP provider (Gmail, AWS SES, SendGrid SMTP, Postmark).

### Environment Settings
```env
EMAIL_PROVIDER=smtp
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=AKIAIOSFODNN7EXAMPLE
SMTP_PASSWORD=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
SMTP_USE_TLS=true
```
