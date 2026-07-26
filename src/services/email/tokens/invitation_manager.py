"""Invitation Manager for GraphEin AI handling multi-tenant workspace & collaborator invitations."""

import logging
from typing import Any
from pydantic import BaseModel, Field

from src.services.email.tokens.token_service import TokenPayload, TokenService

logger = logging.getLogger(__name__)


class WorkspaceInvitationRecord(BaseModel):
    """Record storing workspace or session invitation details."""

    invitation_id: str = Field(..., description="Unique invitation ID")
    workspace_id: str = Field(..., description="Target Workspace ID")
    inviter_user_id: str = Field(..., description="Owner / Manager user ID who issued invitation")
    invitee_email: str = Field(..., description="Target invitee email address")
    role: str = Field(default="editor", description="Assigned RBAC role ('editor', 'commenter', 'viewer')")
    token: str = Field(..., description="Signed JWT invitation token")
    status: str = Field(default="pending", description="Status ('pending', 'accepted', 'expired', 'revoked')")
    created_at: str = Field(..., description="Creation ISO timestamp")


class InvitationManager:
    """Manages invitation creation, verification, duplicate checks, and workspace auto-joining."""

    def __init__(self, token_service: TokenService | None = None) -> None:
        self.token_service = token_service or TokenService()
        self._invitations: dict[str, WorkspaceInvitationRecord] = {}

    def create_invitation(
        self,
        inviter_user_id: str,
        workspace_id: str,
        invitee_email: str,
        role: str = "editor",
        ttl_seconds: int = 604800,  # 7 days
    ) -> WorkspaceInvitationRecord:
        """Creates a signed workspace invitation and guards against double invitations."""
        clean_email = invitee_email.strip().lower()

        # Check existing active invitation
        for record in self._invitations.values():
            if record.workspace_id == workspace_id and record.invitee_email == clean_email and record.status == "pending":
                logger.info(f"[InvitationManager] Re-using existing pending invitation for {clean_email} to workspace {workspace_id}")
                return record

        token = self.token_service.generate_token(
            action="workspace_invite",
            email=clean_email,
            user_id=inviter_user_id,
            workspace_id=workspace_id,
            role=role,
            ttl_seconds=ttl_seconds,
        )

        token_payload = self.token_service.verify_token(token)
        inv_record = WorkspaceInvitationRecord(
            invitation_id=token_payload.jti,
            workspace_id=workspace_id,
            inviter_user_id=inviter_user_id,
            invitee_email=clean_email,
            role=role,
            token=token,
            status="pending",
            created_at=str(token_payload.iat),
        )
        self._invitations[token_payload.jti] = inv_record
        logger.info(f"[InvitationManager] Issued invitation {inv_record.invitation_id} for {clean_email} to workspace {workspace_id}")
        return inv_record

    def verify_and_accept_invitation(self, token: str, accepting_user_id: str) -> dict[str, Any]:
        """Validates invitation token, marks it accepted, and joins workspace."""
        payload: TokenPayload = self.token_service.verify_token(token, expected_action="workspace_invite")

        record = self._invitations.get(payload.jti)
        if record and record.status != "pending":
            raise ValueError(f"Cette invitation a déjà été {record.status}.")

        # Revoke token to prevent Replay Attacks
        self.token_service.revoke_token(payload.jti)

        if record:
            record.status = "accepted"

        logger.info(f"[InvitationManager] User {accepting_user_id} accepted invitation to workspace {payload.workspace_id}")
        return {
            "status": "success",
            "workspace_id": payload.workspace_id,
            "role": payload.role,
            "invitee_email": payload.email,
            "user_id": accepting_user_id,
            "message": "Invitation acceptée avec succès. Accès au workspace accordé.",
        }

    def revoke_invitation(self, invitation_id: str) -> bool:
        """Revokes a pending invitation."""
        if invitation_id in self._invitations:
            self._invitations[invitation_id].status = "revoked"
            self.token_service.revoke_token(invitation_id)
            return True
        return False
