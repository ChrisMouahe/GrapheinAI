# Politique d'Isolation de la Clé Supabase Service Role — LumiChart

Ce document formalise la politique de sécurité et de gouvernance d'accès régissant la variable critique `SUPABASE_SERVICE_ROLE_KEY` au sein de LumiChart.

---

## 1. Règle Fondamentale : Backend-Only Strict

La clé `SUPABASE_SERVICE_ROLE_KEY` dispose des privilèges maximaux sur la base PostgreSQL Supabase et **contourne l'ensemble des règles de sécurité au niveau des lignes (Row Level Security - RLS)**.

> [!CAUTION]
> **Interdiction Absolue :**
> - La clé `service_role` ne doit **JAMAIS** être exposée à un client (navigateur, mobile, API publique).
> - L'interface utilisateur (`src/app/streamlit_app.py`) ne doit **JAMAIS** importer ni manipuler la `service_role`.
> - Les fichiers statiques (`src/app/static/*`) ne doivent contenir **AUCUNE** référence à cette variable.
> - Aucun endpoint FastAPI ne doit retourner cette clé dans une réponse JSON ou un en-tête HTTP.

---

## 2. Utilisations Légitimes & Exceptions Autorisées

L'utilisation de la clé `service_role` est **exclusivement restreinte** aux composants d'infrastructure suivants :
1. **API FastAPI Backend Sécurisée** (`src/services/supabase_service.py`) :
   - Exécution de tâches système administratives internes (ex: synchronisation de quota, purges automatisées).
2. **Workers Asynchrones & Background Jobs** (Sprint 3) :
   - Traitement des files d'attente hors contexte utilisateur direct.
3. **Scripts de Migration & Maintenance CLI** (`supabase/migrations/*`) :
   - Exécution des migrations SQL depuis un environnement CI/CD sécurisé.

---

## 3. Mécanismes de Contrôle & Garde-Fous Automatisés

1. **Check au Démarrage de l'API (`src/app/api.py`)** :
   En environnement `production`, l'API analyse les assets statiques et refuse de démarrer en cas de détection d'une fuite potentielle.
2. **Suite de Tests de Non-Exposition (`tests/test_service_role_isolation.py`)** :
   Intégrée dans la CI/CD pour vérifier l'étanchéité des endpoints et l'absence de régression.
3. **Typage `SecretStr` Pydantic** :
   Masquage automatique de la valeur dans tous les logs, traces d'erreurs et représentations d'objets (`**********`).
