# 🛠️ Guide d'Administration & SRE — GraphEin AI

Ce guide est destiné aux administrateurs système, DevOps et ingénieurs SRE responsables de l'exploitation de **GraphEin AI**.

---

## 📑 Table des Matières
1. [Gestion des Rôles & Sécurité RBAC](#1-gestion-des-rôles--sécurité-rbac)
2. [Console d'Administration Enterprise](#2-console-dadministration-enterprise)
3. [Monitoring SRE & Observabilité](#3-monitoring-sre--observabilité)
4. [Gestion des Logs & Inspection](#4-gestion-des-logs--inspection)
5. [Procédures de Sauvegarde & Restauration](#5-procédures-de-sauvegarde--restauration)

---

## 1. Gestion des Rôles & Sécurité RBAC

GraphEin AI prend en charge 4 rôles d'utilisateurs distincts :

| Rôle | Privilèges & Accès |
| :--- | :--- |
| **admin** | Accès complet : Console Admin, gestion des utilisateurs, quotas API, monitoring SRE. |
| **editor** | Modification des données, exécution des analyses VLM, génération de PDF et partage. |
| **commenter** | Consultation des graphiques et ajout de commentaires collaboratifs. |
| **viewer** | Consultation en lecture seule. |

---

## 2. Console d'Administration Enterprise

Accessible via l'onglet **Console Admin** pour les utilisateurs possédant le rôle `admin` :
- **Gestion des Utilisateurs** : Suspension/réactivation de comptes et mise à jour des rôles.
- **Clés API & Quotas** : Génération de clés d'accès API pour l'intégration de systèmes tiers.
- **Suivi de Consommation Gemini** : Monitoring du nombre de tokens consommés par jour et par utilisateur.

---

## 3. Monitoring SRE & Observabilité

### Endpoints de Supervision
- **Health Probe** : `GET /health` (Statut des composants)
- **Status Probe** : `GET /status` (Mémoire RAM, CPU, sessions actives)
- **Version Metadata** : `GET /version`

---

## 4. Gestion des Logs & Inspection

Les logs applicatifs structurés JSON sont stockés avec rotation dans `logs/graphein_app.log` (5 MB x 5 fichiers).

### Visualiser les Logs en Temps Réel (Linux/macOS)
```bash
tail -f logs/graphein_app.log | grep ERROR
```

---

## 5. Procédures de Sauvegarde & Restauration

### Exécuter une Sauvegarde Automatique
```bash
python scripts/backup_manager.py
```

L'archive `.tar.gz` est générée dans le dossier `backups/`.

### Restaurer une Sauvegarde
```bash
tar -xzf backups/graphein_backup_YYYYMMDD_HHMMSS.tar.gz -C /app/
```
