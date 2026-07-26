# 🔒 Politique de Sécurité & Architecture de Protection — GraphEin AI

Ce document décrit la politique de sécurité, les mécanismes d'isolation et la protection des données de la plateforme **GraphEin AI**.

---

## 📑 Table des Matières
1. [Vue d'Ensemble de la Sécurité](#1-vue-densemble-de-la-sécurité)
2. [Authentification JWT & PostgreSQL Row Level Security (RLS)](#2-authentification-jwt--postgresql-row-level-security-rls)
3. [Isolation Sandbox AST SafeCalculator](#3-isolation-sandbox-ast-safecalculator)
4. [Protection Anti-Injection PromptInjectionGuard](#4-protection-anti-injection-promptinjectionguard)
5. [En-têtes de Sécurité HTTP (OWASP)](#5-en-têtes-de-sécurité-http-owasp)
6. [Signalement des Vulnérabilités](#6-signalement-des-vulnérabilités)

---

## 1. Vue d'Ensemble de la Sécurité

GraphEin AI applique le principe de **Défense en Profondeur (Defense in Depth)** sur toutes les couches applicatives :
- **Réseau & Transport** : En-têtes HTTP de sécurité OWASP strictes.
- **Identité** : Jetons JWT Supabase signés et vérifiés par FastAPI.
- **Données** : Isolation multi-tenant au niveau de la base de données via PostgreSQL Row Level Security (RLS).
- **Moteur d'Exécution** : Évaluation arithmétique déterministe via l'AST Python `SafeCalculator` (aucun appel `eval()`).
- **Garde-fou LLM** : Inspection systématique des invites par `PromptInjectionGuard`.

---

## 2. Authentification JWT & PostgreSQL Row Level Security (RLS)

Chaque requête vers les endpoints protégés doit fournir un jeton Bearer JWT. Les politiques PostgreSQL RLS garantissent qu'un utilisateur ne peut interroger que les lignes correspondant à son `user_id` ou à ses workspaces partagés.

```sql
-- RLS Enforcement
CREATE POLICY "Tenant_Data_Isolation" ON public.analyses
    FOR ALL USING (auth.uid() = user_id);
```

---

## 3. Isolation Sandbox AST SafeCalculator

Pour éviter l'exécution de code arbitraire (Remote Code Execution), GraphEin AI remplace l'instruction `eval()` par un interpréteur d'Arbre Syntaxique Abstrait (`ast.parse`) ultra-strict :

- **Nœuds Autorisés** : `Add`, `Sub`, `Mult`, `Div`, `Pow`, `USub`, `UAdd`, `Constant`, `Num`.
- **Nœuds Interdits** : `Call`, `Import`, `Attribute`, `Name`, `Exec`, `Lambda`, `Subscript`.

Si une expression contient le moindre nœud non autorisé, l'exécution est immédiatement rejetée avec une exception `ForbiddenASTNodeError`.

---

## 4. Protection Anti-Injection PromptInjectionGuard

Le module `PromptInjectionGuard` analyse chaque question posée à l'IA avant transmission au modèle Gemini Vision.  
Il rejette automatiquement les tentatives de détournement d'instructions (*Jailbreaks*, *System Prompt Override*, *Data Exfiltration*).

---

## 5. En-têtes de Sécurité HTTP (OWASP)

Injectés sur toutes les réponses HTTP via le middleware FastAPI :
- `X-Frame-Options: SAMEORIGIN` (Empêche le Clickjacking)
- `X-Content-Type-Options: nosniff` (Empêche le MIME Sniffing)
- `X-XSS-Protection: 1; mode=block` (Empêche le Cross-Site Scripting)
- `Referrer-Policy: strict-origin-when-cross-origin`

---

## 6. Signalement des Vulnérabilités

Si vous découvrez une vulnérabilité de sécurité, veuillez contacter immédiatement l'équipe sécurité à **`security@graphein.ai`**.
