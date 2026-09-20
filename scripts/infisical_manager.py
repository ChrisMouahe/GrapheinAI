#!/usr/bin/env python3
"""Script de gestion et d'audit des secrets Infisical pour LumiChart.

Permet de :
1. Tester la connectivité et l'authentification avec Infisical (status)
2. Auditer la conformité des secrets par rapport à .env.example (audit)
3. Exporter les secrets Infisical vers un fichier local .env (pull)
4. Injecter les variables d'un fichier .env local vers Infisical (push)
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Permet l'import des modules src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.config.infisical_client import InfisicalConfig, InfisicalSecretManager
except ImportError:
    print("[!] Impossible d'importer InfisicalSecretManager. Vérifiez l'environnement Python.")
    sys.exit(1)


def parse_env_file(filepath: Path) -> Dict[str, str]:
    """Extrait les paires clé/valeur d'un fichier .env ou .env.example."""
    if not filepath.exists():
        return {}
    secrets = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r"^([A-Za-z0-9_]+)\s*=\s*(.*)$", line)
            if match:
                key = match.group(1)
                val = match.group(2).strip("\"'")
                secrets[key] = val
    return secrets


def cmd_status(manager: InfisicalSecretManager) -> int:
    """Affiche l'état de configuration et de connectivité d'Infisical."""
    print("=" * 65)
    print("  LumiChart -- Diagnostic Infisical SecretOps")
    print("=" * 65)
    print(f"[*] Infisical Enabled  : {manager.config.enabled}")
    print(f"[*] Site URL           : {manager.config.site_url}")
    print(f"[*] Environment        : {manager.config.environment}")
    print(f"[*] Secret Path        : {manager.config.secret_path}")
    print(f"[*] Project ID         : {manager.config.project_id or 'Non défini'}")
    print(f"[*] Client ID          : {manager.config.client_id[:8] + '...' if manager.config.client_id else 'Non défini'}")
    print(f"[*] Service Token      : {'Présent' if manager.config.token else 'Non défini'}")
    print("-" * 65)

    if not manager.is_enabled:
        print("[!] Infisical n'est pas complètement configuré.")
        print("    Veuillez définir INFISICAL_CLIENT_ID + INFISICAL_CLIENT_SECRET ou INFISICAL_TOKEN.")
        return 1

    print("[*] Tentative de connexion et de récupération des secrets...")
    secrets = manager.fetch_secrets(force_refresh=True)
    if secrets:
        print(f"[+] Succès : {len(secrets)} secrets récupérés depuis Infisical.")
        for k in sorted(secrets.keys()):
            val_masked = secrets[k][:4] + "********" if len(secrets[k]) > 4 else "********"
            print(f"    - {k:<30} : {val_masked}")
        return 0
    else:
        print("[!] Échec de la récupération des secrets ou aucun secret présent.")
        return 1


def cmd_audit(manager: InfisicalSecretManager) -> int:
    """Compare les variables requises par .env.example avec Infisical ou l'environnement."""
    example_path = PROJECT_ROOT / ".env.example"
    if not example_path.exists():
        print(f"[!] Fichier {example_path} introuvable.")
        return 1

    example_vars = parse_env_file(example_path)
    required_keys = set(example_vars.keys())

    # Exclure les méta-variables d'Infisical elles-mêmes de l'audit
    infisical_keys = {
        "INFISICAL_ENABLED",
        "INFISICAL_CLIENT_ID",
        "INFISICAL_CLIENT_SECRET",
        "INFISICAL_PROJECT_ID",
        "INFISICAL_ENVIRONMENT",
        "INFISICAL_SECRET_PATH",
        "INFISICAL_SITE_URL",
    }
    target_keys = required_keys - infisical_keys

    print("=" * 65)
    print("  LumiChart -- Audit de Conformite des Secrets")
    print("=" * 65)

    current_secrets: Dict[str, str] = {}
    if manager.is_enabled:
        print("[*] Source de reference : Instance Infisical")
        current_secrets = manager.fetch_secrets()
    else:
        print("[*] Source de reference : Environnement local / .env")
        env_file = PROJECT_ROOT / ".env"
        current_secrets = parse_env_file(env_file)
        # Compléter avec os.environ
        for k in target_keys:
            if k in os.environ and k not in current_secrets:
                current_secrets[k] = os.environ[k]

    missing: List[str] = []
    defaults_or_placeholders: List[str] = []
    configured: List[str] = []

    placeholder_patterns = ["your_", "mock_", "dev_insecure", "change_me", "example", "xxx"]

    for k in sorted(target_keys):
        if k not in current_secrets or not current_secrets[k].strip():
            missing.append(k)
        else:
            val = current_secrets[k]
            if any(p in val.lower() for p in placeholder_patterns):
                defaults_or_placeholders.append(k)
            else:
                configured.append(k)

    print(f"\n[+] Secrets Valides & Operationnels ({len(configured)}/{len(target_keys)}) :")
    for k in configured:
        print(f"    [OK] {k}")

    if defaults_or_placeholders:
        print(f"\n[!] Valeurs par defaut ou Placeholders detectes ({len(defaults_or_placeholders)}) :")
        for k in defaults_or_placeholders:
            print(f"    [WARN] {k} (valeur: {current_secrets[k]})")

    if missing:
        print(f"\n[!] Secrets Absents / Non Definis ({len(missing)}) :")
        for k in missing:
            print(f"    [MISSING] {k}")
        print("\n[!] Audit termine : certains secrets obligatoires sont absents.")
        return 1

    print("\n[+] Audit reussi : Tous les secrets requis sont documentes et provisionnes.")
    return 0


def cmd_pull(manager: InfisicalSecretManager, output_file: str, force: bool = False) -> int:
    """Télécharge les secrets depuis Infisical et génère un fichier .env local."""
    if not manager.is_enabled:
        print("[!] Infisical n'est pas configure. Impossible d'effectuer le pull.")
        return 1

    out_path = Path(output_file)
    if out_path.exists() and not force:
        print(f"[!] Le fichier {out_path} existe deja. Utilisez --force pour ecraser.")
        return 1

    secrets = manager.fetch_secrets(force_refresh=True)
    if not secrets:
        print("[!] Aucun secret recupere depuis Infisical.")
        return 1

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# ==============================================================================\n")
        f.write(f"# LumiChart -- Generated .env from Infisical ({manager.config.environment})\n")
        f.write("# DO NOT COMMIT THIS FILE TO GIT REPOSITORY\n")
        f.write("# ==============================================================================\n\n")
        for k in sorted(secrets.keys()):
            f.write(f"{k}={secrets[k]}\n")

    print(f"[+] Succes : {len(secrets)} secrets ecrits dans {out_path.resolve()}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gestionnaire SecretOps Infisical pour LumiChart"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Commande status
    subparsers.add_parser("status", help="Verifie l'etat de connexion a Infisical")

    # Commande audit
    subparsers.add_parser("audit", help="Audite les secrets par rapport a .env.example")

    # Commande pull
    pull_parser = subparsers.add_parser("pull", help="Telecharge les secrets vers un .env local")
    pull_parser.add_argument(
        "-o", "--output", default=".env", help="Fichier de destination (defaut: .env)"
    )
    pull_parser.add_argument(
        "-f", "--force", action="store_true", help="Ecrase le fichier existant"
    )

    args = parser.parse_args()

    manager = InfisicalSecretManager()

    if args.command == "status":
        sys.exit(cmd_status(manager))
    elif args.command == "audit":
        sys.exit(cmd_audit(manager))
    elif args.command == "pull":
        sys.exit(cmd_pull(manager, output_file=args.output, force=args.force))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
