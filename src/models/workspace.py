"""Pydantic v2 data models for Enterprise Workspaces, Roles, Collaborators, Comments, and Notifications."""

from datetime import datetime, timedelta
from typing import Any
from pydantic import BaseModel, Field


class Workspace(BaseModel):
    """Enterprise Workspace data model."""

    id: str = Field(..., description="Unique workspace UUID identifier")
    name: str = Field(..., description="Name of workspace (ex: Mon Workspace, Marketing, Finance)")
    owner_id: str = Field(..., description="User ID of workspace creator/owner")
    description: str = Field(default="", description="Workspace description")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class WorkspaceMember(BaseModel):
    """Workspace team member with assigned role."""

    id: str = Field(..., description="Unique member membership UUID")
    workspace_id: str = Field(..., description="Target workspace ID")
    user_id: str = Field(..., description="Member user ID")
    user_email: str = Field(default="", description="Member email address")
    user_name: str = Field(default="", description="Member display name")
    role: str = Field(default="viewer", description="Role: 'owner', 'editor', 'commenter', 'viewer'")
    joined_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class AnalysisPermission(BaseModel):
    """Granular permissions on an individual analysis session."""

    id: str = Field(..., description="Unique permission UUID")
    analysis_id: str = Field(..., description="Session ID or Analysis UUID")
    user_id: str = Field(..., description="Authorized user ID")
    user_email: str = Field(default="", description="Authorized user email")
    user_name: str = Field(default="", description="Authorized user name")
    role: str = Field(default="viewer", description="Role: 'owner', 'editor', 'commenter', 'viewer'")
    granted_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class Invitation(BaseModel):
    """Signed email invitation model."""

    id: str = Field(..., description="Unique invitation UUID")
    workspace_id: str | None = Field(default=None, description="Workspace ID if inviting to workspace")
    analysis_id: str | None = Field(default=None, description="Analysis ID if sharing single chart session")
    email: str = Field(..., description="Target recipient email address")
    inviter_id: str = Field(..., description="Sender user ID")
    inviter_name: str = Field(default="", description="Sender display name")
    role: str = Field(default="editor", description="Assigned role upon acceptance ('editor', 'commenter', 'viewer')")
    token: str = Field(..., description="Cryptographically signed link token")
    expires_at: str = Field(..., description="Expiration ISO timestamp")
    status: str = Field(default="pending", description="Invitation status ('pending', 'accepted', 'revoked')")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class AnalysisComment(BaseModel):
    """Threaded in-app comment model."""

    id: str = Field(..., description="Comment UUID")
    analysis_id: str = Field(..., description="Target session ID")
    user_id: str = Field(..., description="Author user ID")
    user_name: str = Field(default="", description="Author name")
    user_avatar: str | None = Field(default=None, description="Author avatar URL")
    parent_id: str | None = Field(default=None, description="Parent comment UUID for threaded replies")
    text: str = Field(..., description="Comment body text")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class Notification(BaseModel):
    """User in-app notification model."""

    id: str = Field(..., description="Notification UUID")
    user_id: str = Field(..., description="Recipient user ID")
    type: str = Field(..., description="Notification type ('invitation', 'share', 'comment', 'accepted')")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification text body")
    link_url: str | None = Field(default=None, description="Action link URL")
    is_read: bool = Field(default=False, description="Read state status")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class ActivityLog(BaseModel):
    """Audit log entry capturing user actions on workspaces and analyses."""

    id: str = Field(..., description="Audit log UUID")
    workspace_id: str | None = Field(default=None, description="Workspace ID context")
    analysis_id: str | None = Field(default=None, description="Analysis session ID context")
    user_id: str = Field(..., description="Actor user ID")
    user_name: str = Field(default="", description="Actor user display name")
    action: str = Field(..., description="Action name (ex: 'create_workspace', 'share_analysis', 'add_comment')")
    details: dict[str, Any] = Field(default_factory=dict, description="Metadata key-values")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class ShareAnalysisRequest(BaseModel):
    """Payload for sharing an analysis session with an email address."""

    email: str = Field(..., description="Recipient email address")
    role: str = Field(default="editor", description="Assigned role ('editor', 'commenter', 'viewer')")


class ShareLinkRequest(BaseModel):
    """Payload for generating a cryptographically signed expiring share link."""

    analysis_id: str | None = Field(default=None)
    workspace_id: str | None = Field(default=None)
    role: str = Field(default="editor")
    expires_in_hours: int = Field(default=168, description="Expiration time in hours (default 7 days)")


class ShareLinkResponse(BaseModel):
    """Response containing signed share URL and expiration info."""

    share_url: str = Field(..., description="Full signed temporary URL")
    token: str = Field(..., description="Signed token string")
    expires_at: str = Field(..., description="Expiration timestamp string")
    role: str = Field(..., description="Assigned access role")
