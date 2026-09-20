"""Unit tests for centralized enterprise settings validation (Pydantic Settings V2)."""

import pytest
from pydantic import ValidationError
from src.config.settings import AppSettings


def test_settings_loads_default_in_dev():
    """Vérifie que les paramètres se chargent avec des valeurs par défaut sécurisées en dev."""
    app_settings = AppSettings(
        _env_file=None,
        environment="development",
        gemini_api_key="dev_mock_key_for_testing",
    )
    assert app_settings.environment == "development"
    assert app_settings.port == 8088
    assert app_settings.host == "0.0.0.0"
    assert app_settings.gemini_model == "gemini-2.5-flash"
    assert app_settings.email_provider == "maildev"
    assert app_settings.jwt_secret_key.get_secret_value() is not None


def test_settings_secret_masking():
    """Vérifie que SecretStr masque la valeur lors du cast en chaîne (anti-fuite logs)."""
    app_settings = AppSettings(
        _env_file=None,
        environment="development",
        gemini_api_key="super_secret_gemini_token_12345",
    )
    # Dans la représentation __repr__ ou __str__, la valeur réelle ne doit jamais apparaître
    assert "super_secret_gemini_token_12345" not in repr(app_settings.gemini_api_key)
    assert "super_secret_gemini_token_12345" not in str(app_settings.gemini_api_key)
    assert app_settings.gemini_api_key.get_secret_value() == "super_secret_gemini_token_12345"


def test_production_fails_without_gemini_api_key():
    """Vérifie qu'en production, l'absence de clé Gemini valide lève une exception bloquante."""
    with pytest.raises(ValidationError) as exc_info:
        AppSettings(
            _env_file=None,
            environment="production",
            gemini_api_key="",
            jwt_secret_key="a_very_long_secure_production_jwt_secret_key_exceeding_32_chars",
            supabase_url="https://valid-project.supabase.co",
            supabase_anon_key="valid_anon_key_token_for_supabase",
        )
    assert "GEMINI_API_KEY" in str(exc_info.value)


def test_production_fails_with_insecure_jwt():
    """Vérifie qu'en production, l'usage d'un secret JWT par défaut ou trop court est rejeté."""
    with pytest.raises(ValidationError) as exc_info:
        AppSettings(
            _env_file=None,
            environment="production",
            gemini_api_key="valid_production_gemini_key_123456789",
            jwt_secret_key="graphein_dev_insecure_secret_key_minimum_32_chars!",
            supabase_url="https://valid-project.supabase.co",
            supabase_anon_key="valid_anon_key_token_for_supabase",
        )
    assert "JWT_SECRET_KEY" in str(exc_info.value)


def test_production_fails_without_supabase_url():
    """Vérifie qu'en production, SUPABASE_URL est obligatoire."""
    with pytest.raises(ValidationError) as exc_info:
        AppSettings(
            _env_file=None,
            environment="production",
            gemini_api_key="valid_production_gemini_key_123456789",
            jwt_secret_key="a_very_long_secure_production_jwt_secret_key_exceeding_32_chars",
            supabase_url=None,
            supabase_anon_key="valid_anon_key_token_for_supabase",
        )
    assert "SUPABASE_URL" in str(exc_info.value)


def test_production_fails_without_supabase_anon_key():
    """Vérifie qu'en production, SUPABASE_KEY (anon) est obligatoire."""
    with pytest.raises(ValidationError) as exc_info:
        AppSettings(
            _env_file=None,
            environment="production",
            gemini_api_key="valid_production_gemini_key_123456789",
            jwt_secret_key="a_very_long_secure_production_jwt_secret_key_exceeding_32_chars",
            supabase_url="https://valid-project.supabase.co",
            supabase_anon_key=None,
        )
    assert "SUPABASE_KEY" in str(exc_info.value)


def test_production_fails_with_resend_missing_key():
    """Vérifie que si EMAIL_PROVIDER='resend' en production, la clé RESEND_API_KEY est requise."""
    with pytest.raises(ValidationError) as exc_info:
        AppSettings(
            _env_file=None,
            environment="production",
            gemini_api_key="valid_production_gemini_key_123456789",
            jwt_secret_key="a_very_long_secure_production_jwt_secret_key_exceeding_32_chars",
            supabase_url="https://valid-project.supabase.co",
            supabase_anon_key="valid_anon_key_token_for_supabase",
            email_provider="resend",
            resend_api_key=None,
        )
    assert "RESEND_API_KEY" in str(exc_info.value)


def test_production_valid_configuration():
    """Vérifie qu'une configuration de production complète et sécurisée valide avec succès."""
    app_settings = AppSettings(
        _env_file=None,
        environment="production",
        gemini_api_key="AIzaSyAValidGoogleGeminiProductionKey33Chars",
        jwt_secret_key="a_very_long_secure_production_jwt_secret_key_exceeding_32_chars",
        supabase_url="https://valid-project.supabase.co",
        supabase_anon_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.valid_anon_token",
        email_provider="resend",
        resend_api_key="re_ValidResendApiKeyProduction123456",
    )
    assert app_settings.environment == "production"
    assert app_settings.gemini_api_key.get_secret_value() == "AIzaSyAValidGoogleGeminiProductionKey33Chars"
    assert app_settings.supabase_url == "https://valid-project.supabase.co"
    assert app_settings.email_provider == "resend"
