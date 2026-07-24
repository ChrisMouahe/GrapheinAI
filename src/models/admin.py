"""Pydantic v2 data models for Enterprise Administration Console, API Keys, Quotas, and System Backups."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from src.models.user import UserProfile
from src.models.workspace import Workspace


class ApiKey(BaseModel):
    """Structured representation of an Enterprise API Key."""

    id: str = Field(..., description="Unique API key identifier")
    user_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="Descriptive key label")
    key_prefix: str = Field(..., description="Masked key prefix display (ex: gk_live_8f3a...)")
    key_hash: str = Field(..., description="SHA-256 hash of full secret key")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    expires_at: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    usage_count: int = Field(default=0)
    monthly_quota: int = Field(default=500)


class CreateApiKeyRequest(BaseModel):
    """Payload to create a new API key."""

    name: str = Field(..., description="Key description name")
    monthly_quota: int = Field(default=500, description="Monthly API calls limit")


class SystemQuota(BaseModel):
    """System quota limits per subscription tier."""

    tier_name: str = Field(default="Enterprise", description="Tier name")
    max_analyses_per_month: int = Field(default=100)
    max_file_size_mb: int = Field(default=20)
    max_workspaces: int = Field(default=5)
    allow_multi_chart: bool = Field(default=True)
    allow_api_keys: bool = Field(default=True)


class SystemSettings(BaseModel):
    """Global system configuration & feature flags."""

    maintenance_mode: bool = Field(default=False)
    allow_user_signups: bool = Field(default=True)
    default_user_role: str = Field(default="viewer")
    gemini_monthly_token_budget: int = Field(default=5000000)
    gemini_consumed_tokens: int = Field(default=124500)


class UpdateUserRoleRequest(BaseModel):
    """Payload to update user role."""

    role: str = Field(..., description="New role: 'admin', 'editor', 'commenter', 'viewer'")


class ToggleSuspensionRequest(BaseModel):
    """Payload to toggle user account suspension."""

    is_suspended: bool = Field(..., description="True to suspend account, False to activate")


class AdminConsumptionReport(BaseModel):
    """Gemini token and system consumption report."""

    gemini_consumed_tokens: int = Field(...)
    gemini_token_budget: int = Field(...)
    total_charts_analyzed: int = Field(...)
    active_users_count: int = Field(...)
    avg_analysis_latency_sec: float = Field(...)


class BackupPayload(BaseModel):
    """Complete JSON snapshot of system state for backup and restoration."""

    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    version: str = Field(default="5.0.0")
    users: list[UserProfile] = Field(default_factory=list)
    workspaces: list[Workspace] = Field(default_factory=list)
    api_keys: list[ApiKey] = Field(default_factory=list)
    system_settings: SystemSettings = Field(default_factory=SystemSettings)
    system_quotas: list[SystemQuota] = Field(default_factory=list)
