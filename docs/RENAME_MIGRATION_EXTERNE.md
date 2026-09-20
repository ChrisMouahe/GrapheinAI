# Procédure Opérationnelle de Migration Externe — GrapheinAI -> LumiChart

Ce document détaille les actions manuelles et configurations d'infrastructure **externes au code** que le fondateur et l'équipe DevOps doivent réaliser pour finaliser la transition de marque vers **LumiChart**.

---

## 1. Ordre d'Exécution Recommandé

Pour garantir une transition fluide et **zéro temps d'arrêt** (*Zero Downtime*), suivez rigoureusement l'ordonnancement ci-dessous :

```
┌───────────────────────────┐
│ 1. Infisical Project Name │ (Interne, zéro impact client)
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│ 2. Dépôt GitHub (Remote)  │ (Redirection automatique assurée par GitHub)
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│ 3. Registre Docker (GHCR) │ (Nouveaux tags/images sans supprimer l'ancien)
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│ 4. Domaines DNS & Emails  │ (Cloudflare + Resend avec période de transition 30j)
└─────────────┬─────────────┘
              ▼
┌───────────────────────────┐
│ 5. Mise à jour Docs Prod  │ (Bascule finale des URLs publiques)
└───────────────────────────┘
```

---

## 2. Procédures Détaillées par Service

### A. Projet Infisical Cloud (SecretOps)
- **Constat :** Le projet dans Infisical Cloud est actuellement intitulé `GrapheinAI` (Workspace ID : `0a5319ca-0b97-43a6-aadf-f778745f39a7`).
- **Actions :**
  1. Se connecter sur [app.infisical.com](https://app.infisical.com).
  2. Aller dans **Project Settings** > **General**.
  3. Renommer le projet en **LumiChart** (Slug : `lumichart` ou `lumichart-ai`).
  4. L'identifiant `workspaceId` dans `.infisical.json` demeure inchangé (`0a5319ca-0b97-43a6-aadf-f778745f39a7`).
  5. Tester la connexion locale :
     ```bash
     infisical secrets --env=dev
     ```

---

### B. Dépôt GitHub & Remotes Locaux
- **Constat :** Le dépôt distant est hébergé sur `https://github.com/ChrisMouahe/GrapheinAI`.
- **Actions :**
  1. Aller sur GitHub : `https://github.com/ChrisMouahe/GrapheinAI/settings`.
  2. Dans la section **Repository name**, renommer en `LumiChart` (ou `lumichart-ai`).
  3. Cliquer sur **Rename**. *(GitHub assure automatiquement la redirection de l'ancien lien).*
  4. Mettre à jour l'URL distante locale sur vos postes de travail :
     ```bash
     git remote set-url origin https://github.com/ChrisMouahe/LumiChart.git
     git remote -v
     ```

---

### C. Registre d'Images Docker (GHCR / Docker Hub)
- **Constat :** Les conteneurs locaux sont désormais nommés `lumichart-api-dev`, `lumichart-api-prod`, `lumichart-redis-dev`, etc.
- **Actions :**
  1. Lors du build des images de production, utiliser le nouveau namespace :
     ```bash
     docker build -t ghcr.io/chrismouahe/lumichart-api:latest -f Dockerfile .
     ```
  2. Conserver les anciens tags pendant au moins 30 jours pour éviter toute rupture lors d'un rollback éventuel.

---

### D. Noms de Domaine, DNS & Passerelle Email (Resend)
- **Constat :** Le domaine d'envoi actuel est `graphein.ai` (`no-reply@graphein.ai`).
- **Actions :**
  1. **Acquisition & DNS Cloudflare** :
     - Enregistrer le domaine cible (`lumichart.ai` ou `lumichart.com`).
     - Configurer la zone DNS sur Cloudflare avec SSL/TLS strict et proxy CDN.
  2. **Configuration Resend** :
     - Ajouter le domaine `lumichart.ai` dans [Resend Domains](https://resend.com/domains).
     - Renseigner les enregistrements DNS requis (DKIM, SPF `v=spf1 include:resend.com ~all`, MX, DMARC `v=DMARC1; p=none;`).
     - Vérifier la validation des 3 enregistrements dans la console Resend.
  3. **Période de Transition Double Domaine (30 jours minimum)** :
     - Maintenir le domaine `graphein.ai` actif avec redirection 301 permanente vers `lumichart.ai`.
     - Mettre à jour `EMAIL_FROM` et `APP_BASE_URL` dans Infisical une fois le domaine validé :
       ```bash
       infisical secrets set EMAIL_FROM="no-reply@lumichart.ai" --env=dev
       infisical secrets set APP_BASE_URL="https://app.lumichart.ai" --env=prod
       ```

---

## 3. Checklist de Validation de la Migration Externe

- [ ] Projet renommé dans Infisical Cloud Dashboard
- [ ] Dépôt GitHub renommé et remote local mis à jour
- [ ] Domaine `lumichart.ai` configuré et sécurisé sur Cloudflare
- [ ] SPF, DKIM, DMARC validés sur Resend pour `lumichart.ai`
- [ ] Variables `EMAIL_FROM` et `APP_BASE_URL` mises à jour dans Infisical
- [ ] Redirection DNS 301 de `graphein.ai` vers `lumichart.ai` active
