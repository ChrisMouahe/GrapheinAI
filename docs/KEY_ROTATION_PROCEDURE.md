# Procédure de Rotation des Clés & Secrets d'API — LumiChart

Ce document consigne la procédure opérationnelle standard (SOP) pour effectuer la rotation périodique ou d'urgence des clés et secrets applicatifs de LumiChart.

---

## 1. Principes Fondamentaux de Rotation

1. **Zéro Interruption de Service (Zero-Downtime)** :
   - Toujours générer et tester la nouvelle clé avant de révoquer l'ancienne.
   - Injecter la nouvelle clé dans Infisical.
   - Redémarrer / recharger les services.
   - Vérifier la bonne exécution des endpoints applicatifs.
   - Révoquer immédiatement l'ancienne clé.
2. **Secrets P1 sous Surveillance** :
   - `GEMINI_API_KEY` (Coût financier direct)
   - `RESEND_API_KEY` (Réputation email et délivrabilité)
   - `SUPABASE_SERVICE_ROLE_KEY` (Sécurité critique bdd, bypass RLS)
   - `JWT_SECRET_KEY` (Session et intégrité auth)

---

## 2. Procédure par Fournisseur

### A. Google Gemini Vision VLM (`GEMINI_API_KEY`)
1. Se connecter à [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Cliquer sur **Create API key** (ou sélectionner le projet GCP associé).
3. Copier la nouvelle clé (`AIza...` ou `AQ...`).
4. Mettre à jour dans Infisical :
   ```bash
   infisical secrets set GEMINI_API_KEY="<NOUVELLE_CLE>" --env=dev
   infisical secrets set GEMINI_API_KEY="<NOUVELLE_CLE>" --env=staging
   infisical secrets set GEMINI_API_KEY="<NOUVELLE_CLE>" --env=prod
   ```
5. Valider avec le script de diagnostic :
   ```bash
   python scripts/verify_key_rotation.py
   ```
6. Une fois validé, retourner sur Google AI Studio et cliquer sur l'icône de corbeille (Delete) sur l'ancienne clé pour la révoquer.

---

### B. Resend Emailing Platform (`RESEND_API_KEY`)
1. Se connecter à [Resend Dashboard](https://resend.com/api-keys).
2. Cliquer sur **Create API Key**, nommer la clé (ex: `graphein-prod-2026-09`) avec permission *Full access* ou *Sending access*.
3. Copier la nouvelle clé (`re_...`).
4. Mettre à jour dans Infisical :
   ```bash
   infisical secrets set RESEND_API_KEY="<NOUVELLE_CLE>" --env=dev
   ```
5. Valider avec le script de diagnostic :
   ```bash
   python scripts/verify_key_rotation.py
   ```
6. Dans le dashboard Resend, cliquer sur le menu `...` de l'ancienne clé puis **Delete** pour la révoquer.

---

### C. Supabase Service Role & Anon Keys (`SUPABASE_SERVICE_ROLE_KEY`)
> [!CAUTION]
> **Avertissement critique :** La rotation du JWT Secret Supabase ou de la `service_role` révoque instantanément TOUS les tokens utilisateurs en cours et interrompt les requêtes backend jusqu'à synchronisation. À planifier obligatoirement en **fenêtre de maintenance programmée**.

1. Se connecter sur [Supabase Console](https://supabase.com/dashboard/project/_/settings/api).
2. Aller dans **Project Settings** > **API** > **JWT Settings**.
3. Cliquer sur **Generate a new JWT secret** (ou Roll keys).
4. Récupérer la nouvelle `anon key` et la nouvelle `service_role key`.
5. Mettre à jour immédiatement Infisical :
   ```bash
   infisical secrets set SUPABASE_KEY="<NOUVELLE_ANON_KEY>" --env=dev
   infisical secrets set SUPABASE_SERVICE_ROLE_KEY="<NOUVELLE_SERVICE_ROLE_KEY>" --env=dev
   ```
6. Redémarrer les conteneurs backend (`docker-compose restart`).
7. Exécuter la suite de tests d'isolation :
   ```bash
   pytest tests/test_service_role_isolation.py -v
   ```

---

## 3. Checklist de Fin de Rotation

- [ ] Nouvelle clé testée avec `python scripts/verify_key_rotation.py`
- [ ] Infisical synchronisé pour les environnements concernés
- [ ] Ancienne clé révoquée chez le fournisseur tiers
- [ ] Logs applicatifs surveillés (aucune erreur 401/403)
