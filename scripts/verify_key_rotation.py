"""Script de diagnostic et d'audit de la rotation des clés d'API (Gemini & Resend).

Vérifie l'état (ACTIVE / REVOKED / NOT_PROVIDED) des nouvelles et anciennes clés API.
Usage:
    python scripts/verify_key_rotation.py
    OLD_GEMINI_API_KEY="AIza..." OLD_RESEND_API_KEY="re_..." python scripts/verify_key_rotation.py
"""

from __future__ import annotations

import io
import os
import sys
import httpx
from dotenv import load_dotenv

# Fixer le flux stdout pour Windows terminal UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Charger l'environnement local s'il existe
load_dotenv()


def test_gemini_key(api_key: str | None) -> tuple[str, str]:
    """Teste la validité d'une clé API Google Gemini via un appel REST léger sur models."""
    if not api_key or not api_key.strip():
        return "NOT_PROVIDED", "Aucune cle fournie"

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key.strip()}"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                return "ACTIVE", "Appel 200 OK (Cle operationnelle)"
            elif resp.status_code in (400, 401, 403):
                msg = resp.json().get("error", {}).get("message", "Non autorise")
                return "REVOKED / INVALID", f"Erreur {resp.status_code} ({msg})"
            else:
                return "UNKNOWN", f"Statut inattendu {resp.status_code}: {resp.text[:100]}"
    except Exception as exc:
        return "ERROR", f"Erreur reseau: {exc}"


def test_resend_key(api_key: str | None) -> tuple[str, str]:
    """Teste la validité d'une clé API Resend via un appel REST sur /domains."""
    if not api_key or not api_key.strip():
        return "NOT_PROVIDED", "Aucune cle fournie"

    url = "https://api.resend.com/domains"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                return "ACTIVE", "Appel 200 OK (Cle operationnelle)"
            elif resp.status_code in (401, 403):
                msg = resp.json().get("message", "Cle revoquee ou invalide")
                return "REVOKED / INVALID", f"Erreur {resp.status_code} ({msg})"
            else:
                return "UNKNOWN", f"Statut inattendu {resp.status_code}: {resp.text[:100]}"
    except Exception as exc:
        return "ERROR", f"Erreur reseau: {exc}"


def mask_key(key: str | None) -> str:
    """Masque une clé en affichant seulement les 8 premiers caractères."""
    if not key:
        return "<NON_FOURNIE>"
    if len(key) <= 8:
        return key[:3] + "..."
    return f"{key[:8]}...{key[-4:]}"


def main() -> int:
    print("=" * 70)
    print("[AUDIT] ROTATION DES CLES D'API (GEMINI & RESEND)")
    print("=" * 70)

    # Récupération des clés
    new_gemini = os.getenv("GEMINI_API_KEY")
    old_gemini = os.getenv("OLD_GEMINI_API_KEY")

    new_resend = os.getenv("RESEND_API_KEY")
    old_resend = os.getenv("OLD_RESEND_API_KEY")

    # Tests Gemini
    print("\n[1/2] VERIFICATION DES CLES GEMINI (Google AI Studio)")
    print(f"  * Nouvelle cle (GEMINI_API_KEY) : {mask_key(new_gemini)}")
    status_new_gemini, detail_new_gemini = test_gemini_key(new_gemini)
    print(f"    -> Statut : [{status_new_gemini}] - {detail_new_gemini}")

    print(f"  * Ancienne cle (OLD_GEMINI_API_KEY) : {mask_key(old_gemini)}")
    status_old_gemini, detail_old_gemini = test_gemini_key(old_gemini)
    print(f"    -> Statut : [{status_old_gemini}] - {detail_old_gemini}")

    # Tests Resend
    print("\n[2/2] VERIFICATION DES CLES RESEND")
    print(f"  * Nouvelle cle (RESEND_API_KEY) : {mask_key(new_resend)}")
    status_new_resend, detail_new_resend = test_resend_key(new_resend)
    print(f"    -> Statut : [{status_new_resend}] - {detail_new_resend}")

    print(f"  * Ancienne cle (OLD_RESEND_API_KEY) : {mask_key(old_resend)}")
    status_old_resend, detail_old_resend = test_resend_key(old_resend)
    print(f"    -> Statut : [{status_old_resend}] - {detail_old_resend}")

    print("\n" + "=" * 70)
    print("BILAN DE L'AUDIT DE ROTATION :")

    all_good = True

    # Vérification nouvelle clé Gemini
    if status_new_gemini == "ACTIVE":
        print("  [OK] Nouvelle cle Gemini : Operationnelle (200 OK)")
    else:
        print(f"  [KO] Nouvelle cle Gemini : Non fonctionnelle ({status_new_gemini})")
        all_good = False

    # Vérification nouvelle clé Resend
    if status_new_resend == "ACTIVE":
        print("  [OK] Nouvelle cle Resend : Operationnelle (200 OK)")
    else:
        print(f"  [KO] Nouvelle cle Resend : Non fonctionnelle ({status_new_resend})")
        all_good = False

    # Vérification ancienne clé Gemini
    if status_old_gemini in ("REVOKED / INVALID", "NOT_PROVIDED"):
        print(f"  [OK] Ancienne cle Gemini : {status_old_gemini}")
    else:
        print("  [ATTENTION] Ancienne cle Gemini : ENCORE ACTIVE ! (A revoquer sur Google AI Studio)")
        all_good = False

    # Vérification ancienne clé Resend
    if status_old_resend in ("REVOKED / INVALID", "NOT_PROVIDED"):
        print(f"  [OK] Ancienne cle Resend : {status_old_resend}")
    else:
        print("  [ATTENTION] Ancienne cle Resend : ENCORE ACTIVE ! (A revoquer sur Resend Dashboard)")
        all_good = False

    print("=" * 70)
    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())
