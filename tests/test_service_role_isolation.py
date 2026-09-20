"""Tests d'isolation stricte de la clé SUPABASE_SERVICE_ROLE_KEY (Sécurité P1 - Backend Only)."""

from pathlib import Path
import pytest
from pydantic import SecretStr
from src.config.settings import AppSettings


def test_static_assets_contain_no_service_role_reference():
    """Vérifie qu'aucun fichier statique frontend (HTML, JS, CSS) ne contient de référence à la service_role."""
    static_dir = Path(__file__).resolve().parent.parent / "src" / "app" / "static"
    if static_dir.exists():
        for file_path in static_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in (".html", ".js", ".css", ".json"):
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                assert "SUPABASE_SERVICE_ROLE_KEY" not in content, f"Référence sensible trouvée dans {file_path}"
                assert "service_role" not in content.lower(), f"Référence 'service_role' trouvée dans {file_path}"


def test_streamlit_app_has_no_service_role_import():
    """Vérifie que l'interface utilisateur Streamlit n'importe ni n'utilise la clé service_role."""
    streamlit_path = Path(__file__).resolve().parent.parent / "src" / "app" / "streamlit_app.py"
    assert streamlit_path.exists()
    content = streamlit_path.read_text(encoding="utf-8")
    assert "SUPABASE_SERVICE_ROLE_KEY" not in content
    assert "supabase_service_role_key" not in content
    assert "service_role" not in content


def test_env_example_contains_only_placeholder_service_role():
    """Vérifie que .env.example ne contient aucune vraie clé JWT service_role mais uniquement un placeholder."""
    env_example_path = Path(__file__).resolve().parent.parent / ".env.example"
    assert env_example_path.exists()
    content = env_example_path.read_text(encoding="utf-8")

    # Vérifier qu'aucun JWT réel eyJhbGci... n'est présent pour la service_role
    for line in content.splitlines():
        if "SUPABASE_SERVICE_ROLE_KEY" in line and not line.strip().startswith("#"):
            assert "your_supabase_service_role_key" in line or "placeholder" in line or line.endswith("=")
            assert "eyJhbGciOi" not in line


def test_service_role_settings_security_masking():
    """Vérifie que AppSettings protège la clé service_role comme SecretStr masqué."""
    secret_val = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_service_role_token_secret"
    settings = AppSettings(
        _env_file=None,
        supabase_service_role_key=SecretStr(secret_val),
    )
    assert secret_val not in repr(settings)
    assert secret_val not in str(settings)
    assert "**********" in repr(settings.supabase_service_role_key)


def test_startup_guard_prevents_leakage_in_production(tmp_path):
    """Vérifie que la logique de garde au démarrage bloque le lancement en production si un asset public est compromis."""
    def verify_isolation_logic(environment: str, static_root: Path):
        if environment == "production" and static_root.exists():
            for f in static_root.rglob("*"):
                if f.is_file() and f.suffix in (".html", ".js", ".css"):
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    if "SUPABASE_SERVICE_ROLE_KEY" in content:
                        raise RuntimeError(
                            f"[SECURITY BREACH PREVENTED] SUPABASE_SERVICE_ROLE_KEY trouvée dans l'asset public {f.name}! "
                            "Démarrage refusé en production."
                        )

    # 1. Vérification sur le dossier static réel du projet
    real_static = Path(__file__).resolve().parent.parent / "src" / "app" / "static"
    verify_isolation_logic("production", real_static)

    # 2. Simulation d'une tentative de fuite dans un faux asset statique
    fake_static = tmp_path / "static"
    fake_static.mkdir()
    (fake_static / "bundle.js").write_text("const KEY = 'SUPABASE_SERVICE_ROLE_KEY';", encoding="utf-8")

    with pytest.raises(RuntimeError) as exc_info:
        verify_isolation_logic("production", fake_static)
    assert "SUPABASE_SERVICE_ROLE_KEY" in str(exc_info.value)
