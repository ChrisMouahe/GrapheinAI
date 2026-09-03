# ⚠️ Matrice d'Évaluation des Risques & Plan d'Atténuation — GraphEin AI

**Document** : Risk Assessment Matrix & Disaster Recovery Plan  
**Auteurs** : Équipe d'Audit Technique & VC Due Diligence  
**Version** : 5.0.0 Enterprise  

---

## 1. Méthodologie d'Évaluation des Risques

Chaque risque est évalué selon deux axes cardinaux notés de 1 à 5 :
- **Probabilité (P)** : 1 (Rare) à 5 (Quasi-certain).
- **Impact Métier (I)** : 1 (Négligeable) à 5 (Critique / Bloquant).
- **Criticité Globale (C = P x I)** :
  - 🟢 **Faible (1 - 6)** : Risque acceptable sous surveillance périodique.
  - 🟡 **Moyen (8 - 12)** : Risque nécessitant des mesures d'atténuation actives.
  - 🟠 **Élevé (15 - 16)** : Risque majeur exigeant un plan de contingence prioritaire.
  - 🔴 **Critique (20 - 25)** : Risque vital nécessitant un arbitrage architectural immédiat.

---

## 2. Matrice Globale des Risques Identifiés

| ID | Domaine | Intitulé du Risque | P | I | Criticité | Niveau | Plan d'Atténuation Stratégique |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **R-01** | **IA / VLM** | Hallucinations sur calculs et agrégations | 4 | 5 | **20** | 🔴 Critique | Interception systématique par le moteur AST déterministe (`SafeCalculator`). Zéro calcul délégué au LLM. |
| **R-02** | **Fournisseur** | Dépendance exclusive à l'API Google Gemini (Lock-in / Pannes) | 3 | 5 | **15** | 🟠 Élevé | Couche d'abstraction `BaseAIService` déjà implémentée. Intégrer un fallback automatique vers Claude 3.5 Sonnet ou Mistral Pixtral. |
| **R-03** | **Performance** | Latence élevée sur analyse de graphiques complexes (> 5s) | 4 | 3 | **12** | 🟡 Moyen | Caching persistant SHA-256 des extractions + bascule vers architecture asynchrone Celery/Redis avec polling WebSocket. |
| **R-04** | **Sécurité** | Jailbreak par Prompt Injection via le texte du graphique | 3 | 4 | **12** | 🟡 Moyen | Filtre en amont `PromptInjectionGuard`, balisage strict des prompts systèmes et neutralisation des instructions contradictoires. |
| **R-05** | **Qualité Données**| Erreurs d'extraction sur graphiques bruités ou basse résolution | 4 | 3 | **12** | 🟡 Moyen | Prétraitement OpenCV (seuillage adaptatif, débruitage) + interface de validation Human-in-the-Loop (Ag-Grid) avec scoring de confiance. |
| **R-06** | **Sécurité** | Fuite de données inter-tenants sur les espaces collaboratifs | 2 | 5 | **10** | 🟡 Moyen | Politiques Row Level Security (RLS) PostgreSQL natives dans Supabase + tests automatisés de non-régression multi-tenant. |
| **R-07** | **FinOps** | Explosion imprévue des coûts d'API VLM en cas d'attaque par déni de service | 3 | 3 | **9** | 🟡 Moyen | Rate limiting Cloudflare WAF + quotas stricts par utilisateur/workspace dans `GeminiQuotaManager`. |
| **R-08** | **Infrastructure**| Défaillance du noeud unique ou crash mémoire du serveur ASGI | 2 | 4 | **8** | 🟡 Moyen | Déploiement multi-instances Kubernetes avec HPA + supervision Prometheus/Grafana avec sondes liveness. |
| **R-09** | **Juridique** | Non-conformité RGPD sur la conservation d'images sensibles d'entreprises | 2 | 4 | **8** | 🟡 Moyen | Purge automatique des graphiques après 24h d'inactivité + chiffrement AES-256 au repos sur les compartiments de stockage R2/S3. |
| **R-10** | **DevOps** | Rupture de service lors d'un déploiement (Breaking change) | 2 | 3 | **6** | 🟢 Faible | Pipeline CI/CD GitHub Actions avec tests unitaires obligatoires (28 suites) + stratégie de déploiement Blue/Green. |

---

## 3. Analyse Détaillée des Risques Majeurs & Protocoles de Contingence

### 3.1. Risque R-01 : Hallucinations Numériques et Dérives Statistiques
- **Description** : Les modèles de vision-langage (VLM) sont intrinsèquement probabilistes et sujets à des erreurs d'arrondis ou des inventions de données lorsqu'ils effectuent des opérations arithmétiques directes.
- **Impact** : Perte totale de crédibilité auprès des analystes financiers, contrôleurs de gestion et scientifiques.
- **Réponse Architecturale GraphEin AI** :
  1. Le pipeline sépare strictement l'extraction perceptuelle (VLM) de l'évaluation logique (AST).
  2. Le module `SafeCalculator` analyse l'expression mathématique et compile un arbre syntaxique sécurisé via `ast.parse`.
  3. L'exécution s'effectue dans un bac à sable déterministe avec précision flottante garantie par NumPy/Pandas.
  4. L'`ExplainabilityEngine` fournit la formule exacte et les variables sources utilisées.

### 3.2. Risque R-02 : Dépendance Fournisseur (Vendor Lock-in Google GenAI)
- **Description** : Une interruption du service Google Gemini, une modification unilatérale des tarifs de l'API ou un changement de politique de quotas pourrait impacter la disponibilité de la plateforme.
- **Impact** : Indisponibilité du cœur analytique ou hausse subite du coût de revient.
- **Réponse Architecturale GraphEin AI** :
  1. Le code respecte le pattern **Ports & Adapters** via l'interface `BaseAIService`.
  2. Création d'un connecteur secondaire `ClaudeService` (Anthropic Claude 3.5 Sonnet) et d'un connecteur open-source `PixtralService` (Mistral AI hébergé sur vLLM).
  3. Le routeur de secours (`Circuit Breaker`) bascule automatiquement sur le fournisseur alternatif dès 3 échecs consécutifs (HTTP 429 ou 5xx).

### 3.3. Risque R-06 : Isolation Multi-Tenant et Risque de Fuite de Données
- **Description** : Dans une architecture SaaS B2B, un utilisateur pourrait accéder aux analyses, graphiques ou commentaires confidentiels d'une autre organisation.
- **Impact** : Violation critique de la confidentialité, poursuites judiciaires et perte de certification ISO 27001 / SOC2.
- **Réponse Architecturale GraphEin AI** :
  1. Utilisation exclusive de la sécurité au niveau des lignes (**Row Level Security - RLS**) directement dans le moteur PostgreSQL de Supabase.
  2. Aucune requête n'utilise de compte super-administrateur pour les opérations utilisateurs : chaque requête injecte le JWT de la session (`auth.uid()`).
  3. Les politiques RLS vérifient l'appartenance de l'utilisateur au `workspace_id` pour chaque opération `SELECT`, `INSERT`, `UPDATE` et `DELETE`.

---

## 4. Plan de Continuité & Reprise d'Activité (PCA / PRA)

```
[Incident Majeur Détecté] 
       ↓
[Alerte Sentry / PagerDuty en < 60s]
       ↓
[Basculement DNS Automatique Cloudflare] (TTR < 2 min)
       ↓
[Restauration Base Supabase via PITR] (RPO < 5 min, RTO < 15 min)
       ↓
[Validation Sanity Checks & Réouverture] (Reprise Complète < 30 min)
```

- **RPO (Recovery Point Objective)** : 5 minutes (Perte maximale de données tolérée).
- **RTO (Recovery Time Objective)** : 30 minutes (Temps maximal d'indisponibilité pour rétablir le service).
- **Tests Périodiques** : Exercice de simulation de sinistre programmé semestriellement en environnement de Staging.
