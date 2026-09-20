"""Unit tests for Infisical SecretOps client and settings integration."""

import os
from unittest.mock import MagicMock, patch
import pytest
from src.config.infisical_client import InfisicalConfig, InfisicalSecretManager
from src.config.settings import AppSettings


def test_infisical_config_from_env_defaults(monkeypatch):
    """Vérifie les valeurs par défaut de InfisicalConfig lorsque rien n'est configuré."""
    monkeypatch.delenv("INFISICAL_ENABLED", raising=False)
    monkeypatch.delenv("INFISICAL_CLIENT_ID", raising=False)
    monkeypatch.delenv("INFISICAL_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("INFISICAL_TOKEN", raising=False)
    monkeypatch.delenv("INFISICAL_PROJECT_ID", raising=False)

    config = InfisicalConfig.from_env()
    assert config.enabled is False
    assert config.client_id is None
    assert config.client_secret is None
    assert config.environment == "dev"
    assert config.secret_path == "/"
    assert config.site_url == "https://app.infisical.com"


def test_infisical_config_from_env_configured(monkeypatch):
    """Vérifie l'instanciation de InfisicalConfig avec des variables définies."""
    monkeypatch.setenv("INFISICAL_ENABLED", "true")
    monkeypatch.setenv("INFISICAL_CLIENT_ID", "client_123")
    monkeypatch.setenv("INFISICAL_CLIENT_SECRET", "secret_456")
    monkeypatch.setenv("INFISICAL_PROJECT_ID", "proj_789")
    monkeypatch.setenv("INFISICAL_ENVIRONMENT", "staging")
    monkeypatch.setenv("INFISICAL_SECRET_PATH", "/backend")
    monkeypatch.setenv("INFISICAL_SITE_URL", "https://infisical.mycompany.com")
    monkeypatch.setenv("INFISICAL_CACHE_TTL", "600")

    config = InfisicalConfig.from_env()
    assert config.enabled is True
    assert config.client_id == "client_123"
    assert config.client_secret == "secret_456"
    assert config.project_id == "proj_789"
    assert config.environment == "staging"
    assert config.secret_path == "/backend"
    assert config.site_url == "https://infisical.mycompany.com"
    assert config.cache_ttl == 600


def test_manager_disabled_fallback_to_env(monkeypatch):
    """Vérifie que lorsque Infisical est désactivé, get_secret effectue un fallback propre sur os.getenv."""
    config = InfisicalConfig(enabled=False)
    manager = InfisicalSecretManager(config=config)

    assert manager.is_enabled is False
    assert manager.fetch_secrets() == {}

    monkeypatch.setenv("TEST_KEY_GRAPH", "valeur_locale")
    assert manager.get_secret("TEST_KEY_GRAPH") == "valeur_locale"
    assert manager.get_secret("KEY_NON_EXISTANTE", default="fallback") == "fallback"


def test_manager_fetch_secrets_with_mock_client():
    """Vérifie la récupération et mise en cache des secrets avec un mock du SDK Infisical."""
    config = InfisicalConfig(
        enabled=True,
        client_id="mock_id",
        client_secret="mock_secret",
        project_id="mock_proj",
        environment="dev",
        cache_ttl=100,
    )
    manager = InfisicalSecretManager(config=config)

    mock_client = MagicMock()
    # Mock du retour de secrets.list_secrets
    secret_item_1 = MagicMock()
    secret_item_1.secret_key = "GEMINI_API_KEY"
    secret_item_1.secret_value = "AIzaSyMockedGeminiKey12345"

    secret_item_2 = MagicMock()
    secret_item_2.secret_key = "SUPABASE_URL"
    secret_item_2.secret_value = "https://mock-supabase.supabase.co"

    mock_response = MagicMock()
    mock_response.secrets = [secret_item_1, secret_item_2]
    mock_client.secrets.list_secrets.return_value = mock_response

    with patch("src.config.infisical_client.InfisicalSDKClient", return_value=mock_client), \
         patch("src.config.infisical_client.INFISICAL_SDK_AVAILABLE", True):

        secrets = manager.fetch_secrets()
        assert len(secrets) == 2
        assert secrets["GEMINI_API_KEY"] == "AIzaSyMockedGeminiKey12345"
        assert secrets["SUPABASE_URL"] == "https://mock-supabase.supabase.co"

        # Vérification get_secret
        assert manager.get_secret("GEMINI_API_KEY") == "AIzaSyMockedGeminiKey12345"

        # Deuxième appel : doit utiliser le cache sans rappeler list_secrets
        cached_secrets = manager.fetch_secrets()
        assert cached_secrets == secrets
        assert mock_client.secrets.list_secrets.call_count == 1


def test_manager_inject_into_environment(monkeypatch):
    """Vérifie l'injection des secrets Infisical dans os.environ."""
    config = InfisicalConfig(
        enabled=True,
        client_id="mock_id",
        client_secret="mock_secret",
        project_id="mock_proj",
    )
    manager = InfisicalSecretManager(config=config)

    monkeypatch.delenv("INJECTED_TEST_VAR", raising=False)

    with patch.object(manager, "fetch_secrets", return_value={"INJECTED_TEST_VAR": "injected_val_99"}):
        count = manager.inject_into_environment(override=False)
        assert count == 1
        assert os.environ.get("INJECTED_TEST_VAR") == "injected_val_99"


def test_settings_loads_with_infisical_secrets():
    """Vérifie que AppSettings intègre correctement les secrets fournis par Infisical."""
    mock_secrets = {
        "GEMINI_API_KEY": "AIzaSyFromInfisicalSecretOpsProductionKey33",
        "SUPABASE_URL": "https://infisical-injected.supabase.co",
        "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiJ9.anon_infisical_token",
        "JWT_SECRET_KEY": "a_very_long_secure_jwt_secret_key_from_infisical_32_chars",
    }

    with patch("src.config.settings.get_infisical_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.is_enabled = True
        mock_manager.fetch_secrets.return_value = mock_secrets
        mock_get_manager.return_value = mock_manager

        app_settings = AppSettings(
            _env_file=None,
            environment="development",
        )

        assert app_settings.gemini_api_key.get_secret_value() == "AIzaSyFromInfisicalSecretOpsProductionKey33"
        assert app_settings.supabase_url == "https://infisical-injected.supabase.co"
        assert app_settings.supabase_anon_key.get_secret_value() == "eyJhbGciOiJIUzI1NiJ9.anon_infisical_token"
