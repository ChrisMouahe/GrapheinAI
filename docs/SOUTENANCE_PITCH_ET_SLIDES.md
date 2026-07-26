# 🎓 Kit de Soutenance Master — GraphEin AI

**Rôles** : Professeur d'université, Président de Jury, Senior AI Architect & Coach en Soutenance  
**Projet** : GraphEin AI — Plateforme SaaS d'Intelligence Graphique Multimodale d'Entreprise  

---

## 📑 Sommaire du Kit
1. [Pitch Oral d'Ouverture (3 à 5 minutes)](#1-pitch-oral-douverture-3-à-5-minutes)
2. [Structure des Slides PowerPoint & Visuels](#2-structure-des-slides-powerpoint--visuels)
3. [Notes Détaillées du Présentateur (Slide par Slide)](#3-notes-détaillées-du-présentateur-slide-par-slide)
4. [Script de Démonstration Vidéo (3 minutes)](#4-script-de-démonstration-vidéo-3-minutes)
5. [Scénarios de Secours & Mode Déconnecté](#5-scénarios-de-secours--mode-déconnecté)

---

## 1. Pitch Oral d'Ouverture (3 à 5 minutes)

*(Chrono : 4 minutes 15 secondes — À réciter avec conviction, calme et assurance)*

> **"Monsieur le Président du Jury, Mesdames et Messieurs les membres du Jury, bonjour.**
>
> Aujourd'hui, les entreprises produisent des millions de graphiques financiers, scientifiques et industriels. Pourtant, exploiter ces graphiques pose deux défis majeurs :
> 1. **Le risque d'hallucination** : Les modèles de vision classiques inventent parfois des chiffres ou se trompent sur les calculs.
> 2. **L'effet 'Boîte Noire'** : Les décideurs refusent d'utiliser un outil IA s'ils ne peuvent pas vérifier l'origine des données.
>
> C'est pour résoudre ce problème crucial que j'ai conçu **GraphEin AI** : une plateforme SaaS d'intelligence graphique multimodale d'entreprise.
>
> **Notre innovation repose sur 3 piliers majeurs :**
>
> **1. Un Pipeline Multimodal Hybride (Vision + OCR)**
> Plutôt que de tout confier aveuglément à un Grand Modèle de Vision, GraphEin AI combine l'analyse de conteneurs géométriques d'OpenCV avec la puissance du modèle VLM **Gemini 1.5 Flash Vision**. Cela garantit une précision d'extraction exceptionnelle des axes, légendes et points de données.
>
> **2. La Grille Human-in-the-Loop (HITL) & le Workflow Sécurisé**
> L'utilisateur conserve le contrôle total. Une grille de données lui permet de valider ou corriger les valeurs extraites. Le chat IA est **strictement verrouillé** tant que l'utilisateur n'a pas cliqué sur le bouton 'VALIDER'. Une fois validé, un rapport narratif scientifique complet d'une page est généré automatiquement.
>
> **3. Le Raisonnement Déterministe via SafeCalculator AST**
> Pour éliminer à 100% les erreurs de calcul, GraphEin AI n'utilise **jamais** l'IA pour faire de l'arithmétique. L'IA extrait la formule mathématique en langage naturel, et notre moteur **SafeCalculator AST** l'évalue dans un bac à sable Python ultra-sécurisé. Résultat : zéro hallucination mathématique et zéro risque d'injection de code.
>
> L'ensemble est propulsé par une architecture backend FastAPI moderne, une isolation multi-tenant Supabase PostgreSQL Row Level Security, et une suite de tests automatisés validant 100% du système.
>
> Je vous propose de découvrir dès maintenant l'architecture et la démonstration pratique de GraphEin AI."

---

## 2. Structure des Slides PowerPoint & Visuels

### Slide 1 : Titre & Introduction
- **Titre** : GraphEin AI — Intelligence Graphique Multimodale d'Entreprise
- **Sous-titre** : Extraction Hybride Vision/OCR, Validation Human-in-the-Loop et Calcul Déterministe AST
- **Visuel** : Logo GraphEin AI + Capture d'écran du Dashboard Dark Mode

### Slide 2 : Le Problème & La Proposition de Valeur
- **Problème** : Erreurs d'extraction sur graphiques complexes, hallucinations LLM sur les calculs, manque de vérifiabilité.
- **Solution GraphEin AI** : Pipeline hybride, validation HITL obligatoire et bac à sable AST.

### Slide 3 : Architecture Système Hexagonale
- **Visuel** : Diagramme Mermaid d'architecture (Frontend SPA, FastAPI, Gemini, SafeCalculator AST, Supabase RLS).

### Slide 4 : Le Workflow de Validation à 5 Étapes
- **Visuel** : Stepper Horizontal 5 étapes (Upload ➔ OCR/HITL ➔ Validation ➔ Rapport IA ➔ Chat débloqué).

### Slide 5 : Moteur SafeCalculator AST & Sécurité
- **Visuel** : Comparatif `eval()` (Dangereux/Hallucinatoire) vs `SafeCalculator AST` (Déterministe/Sécurisé).

### Slide 6 : Résultats, Performance & Déploiement
- **Métriques** : Latence moyenne < 0.8s, 182 tests unitaires validés (100%), déploiement Docker & Streamlit Cloud en < 10 min.

---

## 3. Notes Détaillées du Présentateur (Slide par Slide)

- **Slide 1** : Respirer profondément. Accueillir le jury. Présenter le sujet avec dynamisme.
- **Slide 2** : Insister sur l'enjeu financier et stratégique des erreurs de calcul dans un rapport d'entreprise.
- **Slide 3** : Expliquer clairement la séparation des responsabilités entre la partie explicative (Gemini) et la partie calculatoire (SafeCalculator AST).
- **Slide 4** : Montrer l'écran DataGrid. Expliquer pourquoi le bouton VALIDER garantit la confiance de l'utilisateur.
- **Slide 5** : Anticiper la question du jury sur la sécurité et le risque d'injection RCE (`eval`). Expliquer l'analyse d'Arbre Syntaxique Abstrait.
- **Slide 6** : Conclure en présentant les métriques de performance et la facilité de déploiement DevOps.

---

## 4. Script de Démonstration Vidéo (3 minutes)

- **00:00 - 00:30** : Présentation du Dashboard et téléversement d'un graphique d'entreprise.
- **00:30 - 01:15** : Extraction instantanée, affichage du Stepper à l'Étape 2 et vérification dans la grille HITL.
- **01:15 - 02:00** : Clic sur le bouton **VALIDER** ➔ Animation de chargement ➔ Génération du rapport scientifique d'une page par `GraphInterpreter`.
- **02:00 - 02:45** : Déblocage automatique du Chat ➔ Saisie d'une question de calcul ➔ Évaluation par `SafeCalculator AST` et affichage du résultat exact avec métriques XAI.
- **02:45 - 03:00** : Génération et téléchargement du rapport PDF officiel.

---

## 5. Scénarios de Secours & Mode Déconnecté

| Type d'Incident | Cause Potentielle | Solution de Secours Immédiate |
| :--- | :--- | :--- |
| **Coupure Internet** | Perte de connexion Wi-Fi pendant la soutenance | Activer le mode Mock local (`SUPABASE_URL` non configuré) et utiliser les réponses pré-cachées du RAG FAISS. |
| **Quota API Gemini Épuisé** | Erreur 429 Too Many Requests | Le système bascule automatiquement sur le fallback déterministe local (`MockVLM` + OCR OpenCV). |
| **Base de Données Inaccessible** | Latence réseau Supabase | SupabaseService passe automatiquement en mode `in-memory mock storage` sans interrompre la démo. |
