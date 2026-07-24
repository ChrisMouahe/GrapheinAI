"""EnterpriseAdminService managing user governance, role assignments, API key lifecycle, system quotas, and backups."""

import hashlib
from datetime import datetime
import logging
import secrets
from typing import Any
import uuid

from src.models.admin import (
    AdminConsumptionReport,
    ApiKey,
    BackupPayload,
    SystemQuota,
    SystemSettings,
)
from src.models.user import UserProfile
from src.models.workspace import Workspace

logger = logging.getLogger("EnterpriseAdminService")


class EnterpriseAdminService:
    """Service managing admin governance, user suspension/roles, API keys, system settings, and backups."""

    def __init__(self, supabase_service: Any | None = None) -> None:
        self.supabase_service = supabase_service
        self.settings = SystemSettings()
        self.quotas: dict[str, SystemQuota] = {
            "Enterprise": SystemQuota(tier_name="Enterprise"),
            "Free": SystemQuota(tier_name="Free", max_analyses_per_month=15, max_workspaces=1, allow_api_keys=False),
        }
        self.api_keys: dict[str, ApiKey] = {}
        self.raw_api_secrets: dict[str, str] = {}  # key_id -> full raw secret for initial display
        self.mock_users: dict[str, UserProfile] = {
            "usr_admin_101": UserProfile(
                id="usr_admin_101",
                name="System Administrator",
                email="admin@graphein.ai",
                role="admin",
                secteur_activite="Finance",
            ),
            "demo_user_123": UserProfile(
                id="demo_user_123",
                name="Demo User",
                email="demo@graphein.ai",
                role="editor",
                secteur_activite="Marketing",
            ),
        }

    # ----------------------------------------------------------------
    # 1. USER GOVERNANCE
    # ----------------------------------------------------------------

    def list_all_users(self) -> list[UserProfile]:
        """Returns list of all registered user profiles."""
        return list(self.mock_users.values())

    def update_user_role(self, user_id: str, new_role: str) -> UserProfile:
        """Updates SaaS role for a user profile ('admin', 'editor', 'commenter', 'viewer')."""
        if user_id not in self.mock_users:
            self.mock_users[user_id] = UserProfile(id=user_id, name="User", email=f"{user_id}@enterprise.ai")
        
        usr = self.mock_users[user_id]
        usr.role = new_role
        logger.info(f"AdminService: Updated role for user '{user_id}' to '{new_role}'.")
        return usr

    def set_user_suspension(self, user_id: str, is_suspended: bool) -> UserProfile:
        """Toggles account suspension status for a user profile."""
        if user_id not in self.mock_users:
            self.mock_users[user_id] = UserProfile(id=user_id, name="User", email=f"{user_id}@enterprise.ai")

        usr = self.mock_users[user_id]
        usr.is_suspended = is_suspended

        if self.supabase_service and hasattr(self.supabase_service, "_mock_users"):
            if user_id in self.supabase_service._mock_users:
                self.supabase_service._mock_users[user_id]["is_suspended"] = is_suspended

        action = "suspended" if is_suspended else "reactivated"
        logger.info(f"AdminService: Account '{user_id}' has been {action}.")
        return usr

    def delete_user(self, user_id: str) -> bool:
        """Deletes user profile from system."""
        if user_id in self.mock_users:
            del self.mock_users[user_id]
            logger.info(f"AdminService: Account '{user_id}' deleted.")
            return True
        return False

    # ----------------------------------------------------------------
    # 2. API KEY LIFECYCLE
    # ----------------------------------------------------------------

    def generate_api_key(self, user_id: str, name: str, monthly_quota: int = 500) -> tuple[ApiKey, str]:
        """Generates a cryptographically secure API Key (gk_live_...)."""
        key_id = f"key_{uuid.uuid4().hex[:8]}"
        secret_part = secrets.token_urlsafe(24)
        raw_key = f"gk_live_{secret_part}"
        prefix = f"gk_live_{secret_part[:4]}..."
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        key_item = ApiKey(
            id=key_id,
            user_id=user_id,
            name=name,
            key_prefix=prefix,
            key_hash=key_hash,
            monthly_quota=monthly_quota,
        )
        self.api_keys[key_id] = key_item
        self.raw_api_secrets[key_id] = raw_key
        logger.info(f"AdminService: Generated API key '{key_id}' for user '{user_id}'.")
        return key_item, raw_key

    def list_api_keys(self, user_id: str | None = None) -> list[ApiKey]:
        """Lists API keys for a specific user or all keys if None."""
        if user_id:
            return [k for k in self.api_keys.values() if k.user_id == user_id]
        return list(self.api_keys.values())

    def revoke_api_key(self, key_id: str) -> bool:
        """Revokes an API Key."""
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            logger.info(f"AdminService: Revoked API key '{key_id}'.")
            return True
        return False

    # ----------------------------------------------------------------
    # 3. QUOTAS & SYSTEM SETTINGS
    # ----------------------------------------------------------------

    def get_system_settings(self) -> SystemSettings:
        return self.settings

    def update_system_settings(self, new_settings: SystemSettings) -> SystemSettings:
        self.settings = new_settings
        logger.info("AdminService: Updated system settings.")
        return self.settings

    def get_system_quotas(self) -> list[SystemQuota]:
        return list(self.quotas.values())

    def update_system_quota(self, quota: SystemQuota) -> SystemQuota:
        self.quotas[quota.tier_name] = quota
        return quota

    # ----------------------------------------------------------------
    # 4. GEMINI CONSUMPTION & METRICS
    # ----------------------------------------------------------------

    def record_gemini_usage(self, tokens_used: int) -> None:
        """Records consumed tokens from Gemini Flash Vision requests."""
        self.settings.gemini_consumed_tokens += tokens_used

    def get_consumption_report(self) -> AdminConsumptionReport:
        """Generates an AdminConsumptionReport."""
        return AdminConsumptionReport(
            gemini_consumed_tokens=self.settings.gemini_consumed_tokens,
            gemini_token_budget=self.settings.gemini_monthly_token_budget,
            total_charts_analyzed=142,
            active_users_count=len(self.mock_users),
            avg_analysis_latency_sec=0.85,
        )

    # ----------------------------------------------------------------
    # 5. BACKUP & RESTORE SYSTEM
    # ----------------------------------------------------------------

    def create_system_backup(self) -> BackupPayload:
        """Exports a complete system database snapshot to a BackupPayload model."""
        return BackupPayload(
            users=list(self.mock_users.values()),
            workspaces=[
                Workspace(id="ws_default", name="Mon Workspace", owner_id="usr_admin_101"),
                Workspace(id="ws_mkt", name="Workspace Marketing", owner_id="demo_user_123"),
            ],
            api_keys=list(self.api_keys.values()),
            system_settings=SystemSettings(**self.settings.model_dump()),
            system_quotas=list(self.quotas.values()),
        )

    def restore_system_backup(self, backup: BackupPayload) -> bool:
        """Restores system state from a BackupPayload object."""
        try:
            self.mock_users = {u.id: u for u in backup.users}
            self.api_keys = {k.id: k for k in backup.api_keys}
            self.settings = backup.system_settings
            self.quotas = {q.tier_name: q for q in backup.system_quotas}
            logger.info(f"AdminService: Restored system backup from timestamp '{backup.timestamp}'.")
            return True
        except Exception as e:
            logger.error(f"AdminService restore error: {e}")
            return False
