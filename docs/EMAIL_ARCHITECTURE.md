# Email Infrastructure Architecture - GraphEin AI Enterprise

## Overview
GraphEin AI implements a pluggable, asynchronous, enterprise-grade Email Infrastructure built on clean architecture principles. It abstracts email delivery providers, signs and verifies JWT security tokens, processes background dispatches via an async queue, renders localized dark-mode-ready HTML/Text email templates, and exposes Admin Observability endpoints.

```
                  ┌─────────────────────────────────────┐
                  │          GraphEin AI App            │
                  │ (FastAPI, Supabase, Workspaces)     │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │    EmailService     │
                          └──────────┬──────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
 ┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
 │   TokenService    │     │ InvitationManager │     │ TemplateRenderer  │
 │ (JWT, Signed,     │     │ (Workspaces, RBAC,│     │ (HTML/Text, Dark, │
 │   Revokable)      │     │ Replay Protection)│     │  FR/EN Responsive)│
 └───────────────────┘     └───────────────────┘     └───────────────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │     EmailQueue      │
                          │ (Async Pool, Retry, │
                          │  Metrics, Latency)  │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │ EmailProviderFactory│
                          └──────────┬──────────┘
                                     │
         ┌───────────────┬───────────┼───────────┬───────────────┐
         ▼               ▼           ▼           ▼               ▼
   ┌───────────┐   ┌───────────┐ ┌───────────┐ ┌───────────┐   ┌───────────┐
   │  MailDev  │   │  Resend   │ │   Brevo   │ │   SMTP    │   │  AWS SES  │
   │ (Dev 1025)│   │ (HTTP API)│ │ (HTTP API)│ │ (TLS/SSL) │   │ (HTTP API)│
   └───────────┘   └───────────┘ └───────────┘ └───────────┘   └───────────┘
```

---

## Core Components

### 1. `EmailService`
The primary entry point exposing 15 high-level methods:
- `sendWelcomeEmail()`
- `sendVerificationEmail()`
- `sendResetPassword()`
- `sendWorkspaceInvitation()`
- `sendCollaboratorInvitation()`
- `sendAnalysisShared()`
- `sendCommentNotification()`
- `sendAnalysisFinished()`
- `sendOTP()`
- `sendPasswordChanged()`
- `sendProfileUpdated()`
- `sendAccountCreated()`
- `sendAccountDeleted()`
- `sendWorkspaceCreated()`
- `sendWorkspaceDeleted()`

### 2. Provider Abstraction Layer (`providers/`)
All providers inherit from `BaseEmailProvider` (`send_email`, `verify_connection`).
- **`MailDevProvider`**: Local development SMTP targeting `localhost:1025` (MailDev UI at `http://localhost:1080`).
- **`ResendProvider`**: Production HTTP API (`https://api.resend.com/emails`).
- **`BrevoProvider`**: Production HTTP API (`https://api.brevo.com/v3/smtp/email`).
- **`SMTPProvider`**: Generic TLS/SSL SMTP server (`smtp.gmail.com`, AWS SES SMTP, etc.).
- **`EmailProviderFactory`**: Instantiates active provider from `EMAIL_PROVIDER` in `.env`.

### 3. JWT Token & Invitation Management (`tokens/`)
- **`TokenService`**: Signs and verifies JWT tokens with custom TTL, action isolation (`password_reset`, `email_verify`, `workspace_invite`, `otp`), and JTI revocation blacklist.
- **`InvitationManager`**: Guards against duplicate invitations, generates signed links, validates acceptances, auto-joins users to Workspaces, and revokes spent tokens.

### 4. Async Worker Queue (`queue/`)
- **`EmailQueue`**: Background ThreadPoolExecutor dispatches emails without blocking HTTP API requests.
- Tracks statuses (`pending`, `sending`, `sent`, `failed`, `retry`), execution latencies, and retry policies.

### 5. Multi-Channel Notification Service (`notifications/`)
- **`NotificationService`**: Routes dispatches between In-App notification feeds and Email dispatches.

---

## Security Features
- **Replay Protection**: Spent tokens are revoked via JTI blacklist.
- **Enumeration Protection**: Identical response payloads returned whether user email exists or not.
- **Action Scoping**: Password reset tokens cannot be used for invitation acceptances.
- **Expiration Policies**: OTP (15 min), Password Reset (1h), Invitations (7 days).
