# Email Templates Catalog & Customization Guide - GraphEin AI

## Overview
All email templates in GraphEin AI are designed to meet modern SaaS standards (Notion, Linear, GitHub, Figma, Vercel). They feature:
- Responsive mobile & desktop layouts
- Dark mode compatibility (`color-scheme: light dark`)
- GraphEin AI brand identity (indigo color palette `#6366F1`, dark canvas `#0F172A`, surface `#1E293B`)
- Dual HTML and Plain Text fallback rendering
- French (`fr`) and English (`en`) localizations

---

## Available Templates

### 1. Account & Security
- **`welcome`**: Onboarding email after account registration.
- **`verify_email`**: Email address verification with signed 24h JWT link.
- **`reset_password`**: Password reset link with signed 1h JWT link.
- **`otp`**: 6-digit temporary security code with 15m expiration.
- **`profile_updated`**: Confirmation when user updates professional profile.
- **`account_created`**: Notification upon account creation.
- **`account_deleted`**: Confirmation upon account deletion.

### 2. Workspace & Collaboration
- **`workspace_invitation`**: Invitation to join a workspace with assigned RBAC role.
- **`collaborator_invitation`**: Collaborator invitation to a private analysis session.
- **`workspace_created`**: Notification when a new workspace is created.
- **`workspace_deleted`**: Notification when a workspace is deleted.

### 3. Graph Analytics & Notifications
- **`analysis_shared`**: Shared VLM & AST graph analysis alert.
- **`analysis_finished`**: Completion alert for VLM vision extraction & AST calculation.
- **`notification`**: General in-app & comment notification alert.

---

## Template Variables

| Template Name | Context Variables |
| :--- | :--- |
| `welcome` | `user_name`, `company`, `role`, `action_url` |
| `verify_email` | `user_name`, `action_url` |
| `reset_password` | `user_name`, `action_url` |
| `workspace_invitation` | `inviter_name`, `workspace_name`, `role`, `action_url` |
| `analysis_finished` | `user_name`, `chart_title`, `confidence`, `latency`, `action_url` |
| `otp` | `user_name`, `otp_code` |
