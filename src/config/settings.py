"""Application configuration module using Pydantic Settings V2 and Infisical SecretOps."""

from functools import lru_cache
from typing import Any, Dict, Literal, Optional, Tuple
from pydantic import AliasChoices, Field, SecretStr, field_validator, model_validator
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from src.config.infisical_client import get_infisical_manager


class InfisicalSettingsSource(PydanticBaseSettingsSource):
    """Source personnalisée Pydantic Settings extrayant les secrets depuis Infisical."""

    def get_field_value(self, field: FieldInfo, field_name: str) -> Tuple[Any, str, bool]:
        """Méthode requise par PydanticBaseSettingsSource (non utilisée ici en mode batch)."""
        return None, field_name, False

    def __call__(self) -> Dict[str, Any]:
        """Récupère l'ensemble des secrets depuis le gestionnaire Infisical si actif."""
        try:
            manager = get_infisical_manager()
            if manager.is_enabled:
                return manager.fetch_secrets()
        except Exception:
            pass
        return {}


class AppSettings(BaseSettings):
    """Centralized enterprise settings with strict validation and secure defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Définit la priorité des sources : Init > Infisical > Env > .env > File Secrets."""
        return (
            init_settings,
            InfisicalSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    # ------------------------------------------------------------------
    # 1. Environnement & Serveur Core
    # ------------------------------------------------------------------
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        description="Environnement d'exécution de l'application",
    )
    port: int = Field(default=8088, ge=1, le=65535, description="Port d'écoute ASGI / Web")
    host: str = Field(default="0.0.0.0", description="Hôte d'écoute du serveur")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Niveau de journalisation"
    )
    app_base_url: str = Field(
        default="http://localhost:8088",
        description="URL de base de l'application pour les liens et callbacks",
    )

    # ------------------------------------------------------------------
    # 2. Sécurité & Authentification JWT
    # ------------------------------------------------------------------
    jwt_secret_key: SecretStr = Field(
        default=SecretStr("graphein_dev_insecure_secret_key_minimum_32_chars!"),
        validation_alias=AliasChoices("JWT_SECRET_KEY", "SECRET_KEY", "jwt_secret_key"),
        description="Clé secrète pour le chiffrement des tokens JWT",
    )

    # ------------------------------------------------------------------
    # 3. Google Gemini Vision VLM
    # ------------------------------------------------------------------
    gemini_api_key: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("GEMINI_API_KEY", "gemini_api_key"),
        description="Clé API pour le VLM Google Gemini",
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        validation_alias=AliasChoices("GEMINI_MODEL", "gemini_model"),
        description="Modèle de vision-langage par défaut",
    )

    # ------------------------------------------------------------------
    # 4. Supabase Database & Auth (PostgreSQL RLS)
    # ------------------------------------------------------------------
    supabase_url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_URL", "supabase_url"),
        description="URL du projet Supabase",
    )
    supabase_anon_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_KEY", "SUPABASE_ANON_KEY", "supabase_anon_key"),
        description="Clé publique Supabase Anon",
    )
    supabase_service_role_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="SUPABASE_SERVICE_ROLE_KEY",
        description="Clé d'administration Supabase Service Role",
    )

    # ------------------------------------------------------------------
    # 5. Infrastructure Emailing
    # ------------------------------------------------------------------
    email_provider: Literal["maildev", "resend", "brevo", "smtp"] = Field(
        default="maildev",
        validation_alias="EMAIL_PROVIDER",
        description="Fournisseur d'emailing actif",
    )
    email_from: str = Field(
        default="no-reply@graphein.ai",
        validation_alias="EMAIL_FROM",
        description="Adresse expéditeur des emails",
    )
    email_name: str = Field(
        default="LumiChart Enterprise",
        validation_alias="EMAIL_NAME",
        description="Nom d'affichage expéditeur",
    )
    resend_api_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="RESEND_API_KEY",
        description="Clé API Resend",
    )
    brevo_api_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="BREVO_API_KEY",
        description="Clé API Brevo / Sendinblue",
    )
    smtp_host: str = Field(
        default="localhost",
        validation_alias="SMTP_HOST",
        description="Hôte SMTP",
    )
    smtp_port: int = Field(
        default=1025,
        validation_alias="SMTP_PORT",
        description="Port SMTP",
    )
    smtp_user: Optional[str] = Field(
        default=None,
        validation_alias="SMTP_USER",
        description="Identifiant SMTP",
    )
    smtp_password: Optional[SecretStr] = Field(
        default=None,
        validation_alias="SMTP_PASSWORD",
        description="Mot de passe SMTP",
    )
    smtp_use_tls: bool = Field(
        default=True,
        validation_alias="SMTP_USE_TLS",
        description="Activer TLS pour SMTP",
    )
    maildev_host: str = Field(
        default="localhost",
        validation_alias="MAILDEV_HOST",
        description="Hôte MailDev local",
    )
    maildev_port: int = Field(
        default=1025,
        validation_alias="MAILDEV_PORT",
        description="Port SMTP MailDev",
    )

    # ------------------------------------------------------------------
    # 6. Passerelle Mobile Money (CinetPay - Sprint 2)
    # ------------------------------------------------------------------
    cinetpay_api_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="CINETPAY_API_KEY",
        description="Clé API CinetPay",
    )
    cinetpay_site_id: Optional[str] = Field(
        default=None,
        validation_alias="CINETPAY_SITE_ID",
        description="Site ID CinetPay",
    )
    cinetpay_secret_key: Optional[SecretStr] = Field(
        default=None,
        validation_alias="CINETPAY_SECRET_KEY",
        description="Secret HMAC CinetPay pour les webhooks",
    )

    # ------------------------------------------------------------------
    # 7. Asynchrone & Caching (Redis / Celery - Sprint 3)
    # ------------------------------------------------------------------
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL",
        description="URL de connexion Redis pour cache et Celery",
    )

    # ------------------------------------------------------------------
    # 8. Observabilité SRE
    # ------------------------------------------------------------------
    sentry_dsn: Optional[str] = Field(
        default=None,
        validation_alias="SENTRY_DSN",
        description="DSN Sentry pour le suivi des exceptions",
    )
    betterstack_token: Optional[SecretStr] = Field(
        default=None,
        validation_alias="BETTERSTACK_TOKEN",
        description="Token Better Stack Heartbeat",
    )

    # ------------------------------------------------------------------
    # 9. Gestion Centralisée des Secrets (Infisical SecretOps)
    # ------------------------------------------------------------------
    infisical_enabled: bool = Field(
        default=False,
        validation_alias="INFISICAL_ENABLED",
        description="Active la synchronisation des secrets via Infisical SDK",
    )
    infisical_client_id: Optional[SecretStr] = Field(
        default=None,
        validation_alias=AliasChoices(
            "INFISICAL_CLIENT_ID",
            "INFISICAL_MACHINE_IDENTITY_CLIENT_ID",
        ),
        description="Client ID Machine Identity Infisical (Universal Auth)",
    )
    infisical_client_secret: Optional[SecretStr] = Field(
        default=None,
        validation_alias=AliasChoices(
            "INFISICAL_CLIENT_SECRET",
            "INFISICAL_MACHINE_IDENTITY_CLIENT_SECRET",
        ),
        description="Client Secret Machine Identity Infisical",
    )
    infisical_project_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("INFISICAL_PROJECT_ID", "INFISICAL_WORKSPACE_ID"),
        description="Identifiant du projet ou workspace Infisical",
    )
    infisical_environment: str = Field(
        default="dev",
        validation_alias="INFISICAL_ENVIRONMENT",
        description="Slug de l'environnement Infisical (dev, staging, prod)",
    )
    infisical_secret_path: str = Field(
        default="/",
        validation_alias="INFISICAL_SECRET_PATH",
        description="Chemin du dossier des secrets au sein d'Infisical",
    )
    infisical_site_url: str = Field(
        default="https://app.infisical.com",
        validation_alias="INFISICAL_SITE_URL",
        description="URL de base de l'instance Infisical (Cloud ou Self-Hosted)",
    )

    @model_validator(mode="after")
    def validate_production_requirements(self) -> "AppSettings":
        """Vérifie que les variables obligatoires et sécurisées sont présentes en production."""
        is_prod = self.environment == "production"

        # 1. Vérification de la clé Gemini
        gemini_val = self.gemini_api_key.get_secret_value() if self.gemini_api_key else ""
        if is_prod and (not gemini_val or gemini_val.startswith("mock") or len(gemini_val) < 10):
            raise ValueError(
                "En environnement 'production', 'GEMINI_API_KEY' est strictement obligatoire et doit être valide."
            )

        # 2. Vérification du JWT Secret Key
        jwt_val = self.jwt_secret_key.get_secret_value() if self.jwt_secret_key else ""
        if is_prod:
            if not jwt_val or "dev_insecure" in jwt_val or len(jwt_val) < 32:
                raise ValueError(
                    "En environnement 'production', 'JWT_SECRET_KEY' doit comporter au moins 32 caractères "
                    "aléatoires et ne doit pas utiliser de valeur par défaut de développement."
                )

        # 3. Vérification des identifiants Supabase en production
        if is_prod:
            if not self.supabase_url:
                raise ValueError("En environnement 'production', 'SUPABASE_URL' est obligatoire.")
            anon_val = self.supabase_anon_key.get_secret_value() if self.supabase_anon_key else ""
            if not anon_val:
                raise ValueError("En environnement 'production', 'SUPABASE_KEY' (anon) est obligatoire.")

        # 4. Vérification de la configuration d'emailing en production
        if is_prod and self.email_provider == "resend":
            resend_val = self.resend_api_key.get_secret_value() if self.resend_api_key else ""
            if not resend_val or not resend_val.startswith("re_"):
                raise ValueError("Si EMAIL_PROVIDER='resend' en production, 'RESEND_API_KEY' valide est obligatoire.")

        return self


@lru_cache()
def get_settings() -> AppSettings:
    """Retourne une instance unique mise en cache des paramètres de configuration."""
    return AppSettings()


# Instance globale exportée
settings = get_settings()
