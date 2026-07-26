# 📖 Guide Utilisateur — GraphEin AI

Bienvenue dans le guide utilisateur officiel de **GraphEin AI**, votre assistant d'intelligence graphique multimodale.

---

## 📑 Table des Matières
1. [Prise en Main de l'Interface](#1-prise-en-main-de-linterface)
2. [Étape 1 : Importer un Graphique](#2-étape-1--importer-un-graphique)
3. [Étape 2 : Vérifier les Données (Grille HITL)](#3-étape-2--vérifier-les-données-grille-hitl)
4. [Étape 3 : Validation & Analyse Automatique IA](#4-étape-3--validation--analyse-automatique-ia)
5. [Étape 4 : Interroger l'IA dans le Chat](#5-étape-4--interroger-lia-dans-le-chat)
6. [Étape 5 : Télécharger et Exporter un Rapport PDF](#6-étape-5--télécharger-et-exporter-un-rapport-pdf)
7. [Personnalisation du Profil & Paramètres](#7-personnalisation-du-profil--paramètres)

---

## 1. Prise en Main de l'Interface

L'interface de **GraphEin AI** se compose de :
- **La Barre Latérale (Sidebar)** : Permet de naviguer entre le *Tableau de Bord*, le *Studio d'Analyse*, l'*Historique* et les *Paramètres*.
- **Le Stepper Horizontal** : Indique l'avancement du traitement en 5 étapes claires.
- **La Zone Principale de Travail** : Contient l'aperçu du graphique, la grille de données et le chat IA.

---

## 2. Étape 1 : Importer un Graphique

1. Rendez-vous dans le **Studio d'Analyse**.
2. Glissez-déposez votre image (PNG, JPG, WEBP) dans la zone centrale ou cliquez sur **Choisir un graphique**.
3. L'image s'affiche instantanément dans l'aperçu et le système procède à l'extraction VLM et OCR.

---

## 3. Étape 2 : Vérifier les Données (Grille HITL)

Une fois l'extraction terminée :
- La **Grille de Données (HITL DataGrid)** affiche les étiquettes et valeurs extraites.
- Vous pouvez inspecter chaque valeur et vérifier sa correspondance avec le graphique.
- Le chat reste **verrouillé** tant que vous n'avez pas confirmé les données.

---

## 4. Étape 3 : Validation & Analyse Automatique IA

1. Cliquez sur le bouton principal **VALIDER** situé en haut de la grille de données.
2. L'IA génère automatiquement le **Rapport Scientifique Narratif (GraphInterpreter)** :
   - Description de l'architecture du graphique.
   - Tendances et statistiques clés (moyenne, cumul, amplitude).
   - Pics maximums et seuils minimums.
   - Anomalies et corrélations éventuelles.
   - Recommandations stratégiques personnalisées.

---

## 5. Étape 4 : Interroger l'IA dans le Chat

Une fois l'analyse automatique générée :
- Le champ de saisie du chat est **automatiquement débloqué**.
- Saisissez vos questions en langage naturel (ex: *"Quel est le total de la distribution ?"*, *"Quelle est la différence entre Janvier et Mars ?"*).
- L'IA utilise l'AST déterministe `SafeCalculator` pour évaluer les calculs de manière 100% exacte.

---

## 6. Étape 5 : Télécharger et Exporter un Rapport PDF

1. Cliquez sur le bouton **PDF** dans le panneau de droite.
2. Le système génère un document PDF officiel d'entreprise vectoriel prêt pour impression ou partage par e-mail.

---

## 7. Personnalisation du Profil & Paramètres

Cliquez sur **Paramètres** dans la barre latérale pour accéder aux 6 sous-onglets :
- **Mon Profil** : Définissez votre rôle (ex: *Comptable*), votre entreprise (*Immobilière de construction*) et votre niveau d'expertise. L'IA adaptera son vocabulaire à votre contexte.
- **Préférences** : Changez la langue (Français 🇫🇷 / Anglais 🇬🇧).
- **Apparence** : Basculez entre le thème Clair et Sombre.
- **Assistant IA** : Ajustez le style de réponse (Analytique vs Synthétique).
