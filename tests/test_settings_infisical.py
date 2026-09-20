"""Tests for Infisical settings integration in AppSettings (CLI and SDK modes)."""

import os
from unittest.mock import MagicMock, patch
import pytest
from pydantic import SecretStr, ValidationError
from src.config.settings import AppSettings


def test_cli_injection_mode(monkeypatch):
    """Vérifie que le mode CLI (défaut, INFISICAL_ENABLED=false) lit correctement les variables d'environnement."""
    monkeypatch.setenv("INFISICAL_ENABLED", "false")
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyCLIInjectedKey987654321")
    monkeypatch.setenv("SUPABASE_URL", "https://cli-supabase.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiJ9.anon_cli_token")
    monkeypatch.setenv("RESEND_API_KEY", "re_cli_injected_resend_key_123")
    monkeypatch.setenv("JWT_SECRET_KEY", "cli_injected_super_secure_jwt_secret_key_32_chars!")
    monkeypatch.setenv("ENVIRONMENT", "development")

    app_settings = AppSettings(_env_file=None)

    assert app_settings.infisical_enabled is False
    assert app_settings.gemini_api_key.get_secret_value() == "AIzaSyCLIInjectedKey987654321"
    assert app_settings.supabase_url == "https://cli-supabase.supabase.co"
    assert app_settings.supabase_anon_key.get_secret_value() == "eyJhbGciOiJIUzI1NiJ9.anon_cli_token"
    assert app_settings.resend_api_key.get_secret_value() == "re_cli_injected_resend_key_123"


def test_sdk_mode_with_mock_infisical(monkeypatch):
    """Vérifie que le mode SDK (INFISICAL_ENABLED=true) injecte les secrets récupérés via InfisicalSettingsSource."""
    mock_secrets = {
        "GEMINI_API_KEY": "AIzaSySDKInfisicalKey123456789",
        "SUPABASE_URL": "https://sdk-supabase.supabase.co",
        "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiJ9.anon_sdk_token",
        "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiJ9.service_role_sdk_token",
        "RESEND_API_KEY": "re_sdk_infisical_resend_key_999",
        "JWT_SECRET_KEY": "sdk_injected_super_secure_jwt_secret_key_32_chars!",
        "ENVIRONMENT": "development",
    }

    with patch("src.config.settings.get_infisical_manager") as mock_get_mgr:
        mock_manager = MagicMock()
        mock_manager.is_enabled = True
        mock_manager.fetch_secrets.return_value = mock_secrets
        mock_get_mgr.return_value = mock_manager

        # Instanciation avec INFISICAL_ENABLED=true
        app_settings = AppSettings(
            _env_file=None,
            infisical_enabled=True,
        )

        assert app_settings.infisical_enabled is True
        assert app_settings.gemini_api_key.get_secret_value() == "AIzaSySDKInfisicalKey123456789"
        assert app_settings.supabase_url == "https://sdk-supabase.supabase.co"
        assert app_settings.supabase_anon_key.get_secret_value() == "eyJhbGciOiJIUzI1NiJ9.anon_sdk_token"
        assert app_settings.supabase_service_role_key.get_secret_value() == "eyJhbGciOiJIUzI1NiJ9.service_role_sdk_token"
        assert app_settings.resend_api_key.get_secret_value() == "re_sdk_infisical_resend_key_999"


def test_secret_str_repr_masking():
    """Vérifie que les champs sensibles typés SecretStr masquent leur valeur dans repr() et str()."""
    app_settings = AppSettings(
        _env_file=None,
        gemini_api_key=SecretStr("AIzaSyUltraSecretValue999"),
        supabase_service_role_key=SecretStr("eyJhbGciOiJIUzI1NiJ9.super_secret_role"),
        jwt_secret_key=SecretStr("super_secret_jwt_key_that_must_not_leak_32_chars"),
        resend_api_key=SecretStr("re_ultra_secret_resend_key"),
    )

    # Vérification que le secret n'apparaît ni dans repr(), ni dans str()
    repr_str = repr(app_settings)
    assert "AIzaSyUltraSecretValue999" not in repr_str
    assert "super_secret_role" not in repr_str
    assert "super_secret_jwt_key_that_must_not_leak" not in repr_str
    assert "re_ultra_secret_resend_key" not in repr_str

    assert "**********" in repr(app_settings.gemini_api_key)
    assert "**********" in repr(app_settings.supabase_service_role_key)
    assert "**********" in repr(app_settings.resend_api_key)


def test_production_rejects_placeholder_gemini_key():
    """Vérifie qu'en environnement de production, une clé Gemini placeholder ou absente est rejetée."""
    with pytest.raises(ValidationError) as exc_info:
        AppSettings(
            _env_file=None,
            environment="production",
            gemini_api_key=SecretStr("mock_key"),
            jwt_secret_key=SecretStr("a_valid_random_production_jwt_secret_key_32_chars!"),
            supabase_url="https://prod.supabase.co",
            supabase_anon_key=SecretStr("valid_prod_anon_key"),
        )
    assert "GEMINI_API_KEY" in str(exc_info.value)


def test_production_rejects_insecure_jwt_secret():
    """Vérifie qu'en production, un JWT_SECRET_KEY de développement ou trop court est rejeté."""
    with pytest.raises(ValidationError) as exc_info:
        AppSettings(
            _env_file=None,
            environment="production",
            gemini_api_key=SecretStr("dummy_production_gemini_key_for_testing_only"),
            jwt_secret_key=SecretStr("graphein_dev_insecure_secret_key_minimum_32_chars!"),
            supabase_url="https://prod.supabase.co",
            supabase_anon_key=SecretStr("valid_prod_anon_key"),
        )
    assert "JWT_SECRET_KEY" in str(exc_info.value)


def test_production_rejects_invalid_resend_key_when_resend_active():
    """Vérifie qu'en production avec email_provider='resend', une clé Resend invalide est rejetée."""
    with pytest.raises(ValidationError) as exc_info:
        AppSettings(
            _env_file=None,
            environment="production",
            gemini_api_key=SecretStr("dummy_production_gemini_key_for_testing_only"),
            jwt_secret_key=SecretStr("a_valid_random_production_jwt_secret_key_32_chars!"),
            supabase_url="https://prod.supabase.co",
            supabase_anon_key=SecretStr("valid_prod_anon_key"),
            email_provider="resend",
            resend_api_key=SecretStr("invalid_resend_token"),
        )
    assert "RESEND_API_KEY" in str(exc_info.value)
