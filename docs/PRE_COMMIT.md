# Guide des Hooks Pre-Commit & Détection de Secrets — LumiChart

Pour garantir qu'aucun secret (clés API, tokens JWT, clés privées) ne soit commité dans le dépôt Git de LumiChart, une suite de hooks **pre-commit** et le scanner **detect-secrets** sont configurés.

---

## 1. Installation des Hooks Pre-Commit

À la racine du projet :
```bash
# 1. Installer les dépendances de développement
pip install -r requirements-dev.txt

# 2. Installer les crochets Git
pre-commit install
```

---

## 2. Fonctionnement des Hooks

À chaque commande `git commit`, les vérifications suivantes s'exécutent automatiquement :
1. **detect-secrets** : Analyse les fichiers modifiés et bloque tout commit contenant un secret non répertorié dans `.secrets.baseline`.
2. **check-added-large-files** : Bloque l'ajout accidentel de fichiers volumineux (> 5 Mo).
3. **check-yaml / check-json** : Valide la syntaxe des fichiers de configuration.
4. **ruff** : Analyse statique et auto-correction du code Python.
5. **black** : Formatage standardisé du code Python.

---

## 3. Commandes Utiles

### Exécuter manuellement sur tous les fichiers du projet
```bash
pre-commit run --all-files
```

### Mettre à jour la baseline après l'ajout légitime d'une chaîne complexe (ex: mock de test)
```bash
python -m detect_secrets scan > .secrets.baseline
```

### Auditer les secrets de la baseline
```bash
detect-secrets audit .secrets.baseline
```
