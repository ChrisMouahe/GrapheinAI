"""Client d'intégration Infisical SecretOps pour LumiChart.

Fournit une interface centralisée, robuste et sécurisée pour récupérer
les secrets applicatifs depuis l'instance Infisical (Cloud ou Self-Hosted)
avec gestion de l'Universal Auth (Machine Identity), Service Token,
mise en cache mémoire et fallback transparent en développement local.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Import conditionnel sécurisé du SDK Infisical
try:
    from infisical_sdk import InfisicalSDKClient
    INFISICAL_SDK_AVAILABLE = True
except ImportError:
    InfisicalSDKClient = None  # type: ignore[assignment, misc]
    INFISICAL_SDK_AVAILABLE = False


@dataclass
class InfisicalConfig:
    """Configuration de connexion au serveur Infisical."""

    enabled: bool = False
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    project_id: Optional[str] = None
    project_slug: Optional[str] = None
    environment: str = "dev"
    secret_path: str = "/"
    site_url: str = "https://app.infisical.com"
    token: Optional[str] = None
    cache_ttl: int = 300  # 5 minutes

    @classmethod
    def from_env(cls) -> "InfisicalConfig":
        """Instancie la configuration depuis les variables d'environnement."""
        raw_enabled = os.getenv("INFISICAL_ENABLED", "").lower()
        client_id = os.getenv("INFISICAL_CLIENT_ID") or os.getenv("INFISICAL_MACHINE_IDENTITY_CLIENT_ID")
        client_secret = os.getenv("INFISICAL_CLIENT_SECRET") or os.getenv("INFISICAL_MACHINE_IDENTITY_CLIENT_SECRET")
        token = os.getenv("INFISICAL_TOKEN")
        project_id = os.getenv("INFISICAL_PROJECT_ID") or os.getenv("INFISICAL_WORKSPACE_ID")
        project_slug = os.getenv("INFISICAL_PROJECT_SLUG")

        # Activé explicitement ou automatiquement si des identifiants valides sont fournis
        is_enabled = raw_enabled in ("true", "1", "yes") or (
            raw_enabled != "false" and ((bool(client_id and client_secret)) or bool(token))
        )

        return cls(
            enabled=is_enabled,
            client_id=client_id,
            client_secret=client_secret,
            project_id=project_id,
            project_slug=project_slug,
            environment=os.getenv("INFISICAL_ENVIRONMENT", "dev"),
            secret_path=os.getenv("INFISICAL_SECRET_PATH", "/"),
            site_url=os.getenv("INFISICAL_SITE_URL", "https://app.infisical.com").rstrip("/"),
            token=token,
            cache_ttl=int(os.getenv("INFISICAL_CACHE_TTL", "300")),
        )


class InfisicalSecretManager:
    """Gestionnaire de secrets Infisical d'entreprise avec mise en cache et résilience."""

    def __init__(self, config: Optional[InfisicalConfig] = None) -> None:
        self.config = config or InfisicalConfig.from_env()
        self._client: Optional[Any] = None
        self._authenticated: bool = False
        self._secrets_cache: Dict[str, str] = {}
        self._last_fetch_timestamp: float = 0.0

    @property
    def is_enabled(self) -> bool:
        """Indique si l'intégration Infisical est activée et exploitable."""
        if not self.config.enabled:
            return False
        has_creds = (self.config.client_id and self.config.client_secret) or self.config.token
        return bool(has_creds and (self.config.project_id or self.config.project_slug or self.config.token))

    def _init_client(self) -> bool:
        """Initialise le client SDK Infisical si disponible."""
        if not INFISICAL_SDK_AVAILABLE or InfisicalSDKClient is None:
            logger.warning(
                "Le paquet 'infisicalsdk' n'est pas installé. Fallback sur l'environnement local."
            )
            return False

        if self._client is not None and self._authenticated:
            return True

        try:
            self._client = InfisicalSDKClient(
                host=self.config.site_url,
                cache_ttl=self.config.cache_ttl,
            )

            # 1. Authentification Universal Auth (Machine Identity)
            if self.config.client_id and self.config.client_secret:
                self._client.auth.universal_auth.login(
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret,
                )
                self._authenticated = True
                logger.info(
                    f"Authentification Infisical Universal Auth réussie (Host: {self.config.site_url})"
                )
                return True

            # 2. Authentification via Service Token
            if self.config.token:
                if hasattr(self._client, "set_token"):
                    self._client.set_token(self.config.token)
                elif hasattr(self._client.auth, "token_auth"):
                    self._client.auth.token_auth.login(self.config.token)
                self._authenticated = True
                logger.info("Authentification Infisical via Service Token réussie.")
                return True

            logger.warning("Aucun identifiant Infisical valide fourni (Client ID/Secret ou Token).")
            return False

        except Exception as exc:
            logger.error(f"Échec de l'initialisation du client Infisical: {exc}")
            self._authenticated = False
            self._client = None
            return False

    def fetch_secrets(self, force_refresh: bool = False) -> Dict[str, str]:
        """Récupère l'ensemble des secrets du projet depuis Infisical.

        Utilise le cache mémoire si le TTL n'a pas expiré.
        """
        current_time = time.time()
        if (
            not force_refresh
            and self._secrets_cache
            and (current_time - self._last_fetch_timestamp < self.config.cache_ttl)
        ):
            return dict(self._secrets_cache)

        if not self.is_enabled:
            return {}

        if not self._init_client():
            return {}

        try:
            secrets_response = self._client.secrets.list_secrets(
                environment_slug=self.config.environment,
                secret_path=self.config.secret_path,
                project_id=self.config.project_id,
                project_slug=self.config.project_slug,
                expand_secret_references=True,
                view_secret_value=True,
            )

            secrets_dict: Dict[str, str] = {}
            secret_items = getattr(secrets_response, "secrets", [])

            for item in secret_items:
                key = getattr(item, "secret_key", getattr(item, "secretKey", None))
                val = getattr(item, "secret_value", getattr(item, "secretValue", ""))
                if key:
                    secrets_dict[key] = str(val)

            self._secrets_cache = secrets_dict
            self._last_fetch_timestamp = current_time
            logger.info(
                f"[Infisical] {len(secrets_dict)} secrets synchronisés avec succès "
                f"(Env: {self.config.environment}, Path: {self.config.secret_path})"
            )
            return dict(self._secrets_cache)

        except Exception as exc:
            logger.error(f"Erreur lors de la récupération des secrets Infisical: {exc}")
            # En cas d'erreur de rafraîchissement, renvoyer l'ancien cache si disponible
            return dict(self._secrets_cache)

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Récupère un secret individuel avec fallback local."""
        if not self.is_enabled:
            return os.getenv(key, default)

        # 1. Recherche dans le cache ou récupération globale
        secrets = self.fetch_secrets()
        if key in secrets:
            return secrets[key]

        # 2. Fallback sur variable d'environnement ou valeur par défaut
        return os.getenv(key, default)

    def inject_into_environment(self, override: bool = False) -> int:
        """Injecte les secrets récupérés dans `os.environ`.

        Args:
            override: Si True, écrase les variables existantes dans l'environnement.

        Returns:
            Nombre de variables injectées.
        """
        secrets = self.fetch_secrets()
        injected_count = 0
        for k, v in secrets.items():
            if override or k not in os.environ:
                os.environ[k] = v
                injected_count += 1
        return injected_count


# Instance singleton globale
_default_manager: Optional[InfisicalSecretManager] = None


def get_infisical_manager() -> InfisicalSecretManager:
    """Retourne l'instance singleton du gestionnaire de secrets Infisical."""
    global _default_manager
    if _default_manager is None:
        _default_manager = InfisicalSecretManager()
    return _default_manager
