"""CollaborationService managing enterprise workspaces, multi-role RBAC, signed links, comments, activity logs, and notifications."""

from datetime import datetime, timedelta
import hashlib
import hmac
import json
import logging
import uuid
from typing import Any

from src.models.user import UserProfile
from src.models.workspace import (
    ActivityLog,
    AnalysisComment,
    AnalysisPermission,
    Invitation,
    Notification,
    ShareLinkResponse,
    Workspace,
    WorkspaceMember,
)
from src.services.email_service import EmailService

logger = logging.getLogger("CollaborationService")

# Secret key used to sign temporary share link tokens
HMAC_SECRET = b"graphein_enterprise_collaboration_secret_key_2026"

ROLE_HIERARCHY = {
    "owner": 4,
    "editor": 3,
    "commenter": 2,
    "viewer": 1,
}


class CollaborationService:
    """Enterprise Collaboration Engine for Workspaces, RBAC, Signed Links, Comments, Audit Logs, and Notifications."""

    def __init__(self, email_service: EmailService | None = None) -> None:
        self.email_service = email_service or EmailService()

        # In-memory storage structures simulating Supabase persistence
        self._workspaces: dict[str, Workspace] = {}
        self._workspace_members: list[WorkspaceMember] = []
        self._analysis_permissions: list[AnalysisPermission] = []
        self._invitations: dict[str, Invitation] = {}
        self._comments: list[AnalysisComment] = []
        self._notifications: list[Notification] = []
        self._activity_logs: list[ActivityLog] = []

    # --------------------------------------------------------------------
    # 1. Workspace Management
    # --------------------------------------------------------------------
    def create_workspace(self, name: str, owner: UserProfile, description: str = "") -> Workspace:
        """Creates a new workspace and automatically assigns owner membership."""
        ws_id = str(uuid.uuid4())
        ws = Workspace(
            id=ws_id,
            name=name,
            owner_id=owner.id,
            description=description,
        )
        self._workspaces[ws_id] = ws

        # Add owner membership
        member = WorkspaceMember(
            id=str(uuid.uuid4()),
            workspace_id=ws_id,
            user_id=owner.id,
            user_email=owner.email,
            user_name=owner.name,
            role="owner",
        )
        self._workspace_members.append(member)

        self.log_activity(
            user=owner,
            action="create_workspace",
            workspace_id=ws_id,
            details={"workspace_name": name},
        )
        return ws

    def get_or_create_default_workspace(self, user: UserProfile) -> Workspace:
        """Gets or creates default 'Mon Workspace' for user."""
        user_ws_list = self.get_user_workspaces(user.id)
        if user_ws_list:
            return user_ws_list[0]
        return self.create_workspace(name="Mon Workspace", owner=user, description="Espace de travail par défaut")

    def get_user_workspaces(self, user_id: str) -> list[Workspace]:
        """Returns all workspaces where user is an active member or owner."""
        ws_ids = {m.workspace_id for m in self._workspace_members if m.user_id == user_id}
        for ws in self._workspaces.values():
            if ws.owner_id == user_id:
                ws_ids.add(ws.id)
        return [self._workspaces[wid] for wid in ws_ids if wid in self._workspaces]

    def add_workspace_member(self, workspace_id: str, member_user: UserProfile, role: str = "viewer", actor: UserProfile | None = None) -> WorkspaceMember:
        """Adds or updates a workspace member."""
        for m in self._workspace_members:
            if m.workspace_id == workspace_id and m.user_id == member_user.id:
                m.role = role
                return m

        new_m = WorkspaceMember(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            user_id=member_user.id,
            user_email=member_user.email,
            user_name=member_user.name,
            role=role,
        )
        self._workspace_members.append(new_m)

        if actor:
            self.log_activity(
                user=actor,
                action="add_workspace_member",
                workspace_id=workspace_id,
                details={"added_user": member_user.email, "role": role},
            )

        # Notify user
        ws_name = self._workspaces.get(workspace_id, Workspace(id=workspace_id, name="Workspace", owner_id="")).name
        self.create_notification(
            user_id=member_user.id,
            type="invitation",
            title=f"Ajouté au Workspace {ws_name}",
            message=f"Vous avez été ajouté au workspace '{ws_name}' avec le rôle {role.upper()}.",
        )
        return new_m

    def remove_workspace_member(self, workspace_id: str, target_user_id: str, actor: UserProfile) -> bool:
        """Removes a member from a workspace."""
        initial_len = len(self._workspace_members)
        self._workspace_members = [
            m for m in self._workspace_members
            if not (m.workspace_id == workspace_id and m.user_id == target_user_id)
        ]
        removed = len(self._workspace_members) < initial_len
        if removed:
            self.log_activity(
                user=actor,
                action="remove_workspace_member",
                workspace_id=workspace_id,
                details={"removed_user_id": target_user_id},
            )
        return removed

    # --------------------------------------------------------------------
    # 2. Granular Permissions & Role Verification
    # --------------------------------------------------------------------
    def grant_analysis_permission(
        self,
        analysis_id: str,
        target_user: UserProfile,
        role: str = "editor",
        actor: UserProfile | None = None,
    ) -> AnalysisPermission:
        """Grants or updates granular permissions for an individual analysis session."""
        for p in self._analysis_permissions:
            if p.analysis_id == analysis_id and p.user_id == target_user.id:
                p.role = role
                return p

        perm = AnalysisPermission(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            user_id=target_user.id,
            user_email=target_user.email,
            user_name=target_user.name,
            role=role,
        )
        self._analysis_permissions.append(perm)

        if actor:
            self.log_activity(
                user=actor,
                action="share_analysis",
                analysis_id=analysis_id,
                details={"recipient": target_user.email, "role": role},
            )

        self.create_notification(
            user_id=target_user.id,
            type="share",
            title="Analyse Partagée",
            message=f"{actor.name if actor else 'Un utilisateur'} a partagé une analyse avec vous (Rôle: {role.upper()}).",
            link_url=f"/#analysis?session_id={analysis_id}",
        )
        return perm

    def has_analysis_permission(self, user_id: str, analysis_id: str, required_role: str = "viewer", session_owner_id: str | None = None) -> bool:
        """Verifies if user holds required minimum role hierarchy on target analysis."""
        # 1. Session owner holds full owner privileges
        if session_owner_id and session_owner_id == user_id:
            return True

        # 2. Check explicit analysis permissions
        req_level = ROLE_HIERARCHY.get(required_role.lower(), 1)
        for p in self._analysis_permissions:
            if p.analysis_id == analysis_id and p.user_id == user_id:
                user_level = ROLE_HIERARCHY.get(p.role.lower(), 1)
                return user_level >= req_level

        # 3. Default fallback check
        return False

    # --------------------------------------------------------------------
    # 3. Cryptographically Signed Expiring Share Links
    # --------------------------------------------------------------------
    def create_signed_share_link(
        self,
        actor: UserProfile,
        analysis_id: str | None = None,
        workspace_id: str | None = None,
        role: str = "editor",
        expires_in_hours: int = 168,
        base_url: str = "http://localhost:8088",
    ) -> ShareLinkResponse:
        """Generates a cryptographically signed expiring share link token."""
        exp_dt = datetime.now() + timedelta(hours=expires_in_hours)
        exp_str = exp_dt.strftime("%Y-%m-%d %H:%M:%S")
        token_uuid = str(uuid.uuid4())

        payload = f"{token_uuid}:{actor.id}:{analysis_id or ''}:{workspace_id or ''}:{role}:{exp_str}"
        sig = hmac.new(HMAC_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        signed_token = f"{token_uuid}.{sig[:16]}"

        invitation = Invitation(
            id=token_uuid,
            workspace_id=workspace_id,
            analysis_id=analysis_id,
            email="link_share@graphein.ai",
            inviter_id=actor.id,
            inviter_name=actor.name,
            role=role,
            token=signed_token,
            expires_at=exp_str,
        )
        self._invitations[signed_token] = invitation

        share_url = f"{base_url}/api/share/link/{signed_token}"
        self.log_activity(
            user=actor,
            action="create_signed_link",
            analysis_id=analysis_id,
            workspace_id=workspace_id,
            details={"expires_at": exp_str, "role": role},
        )
        return ShareLinkResponse(
            share_url=share_url,
            token=signed_token,
            expires_at=exp_str,
            role=role,
        )

    def verify_signed_share_link(self, token: str) -> Invitation | None:
        """Validates signed share link token signature, status, and expiration timestamp."""
        inv = self._invitations.get(token)
        if not inv or inv.status != "pending":
            return None

        # Check expiration
        exp_dt = datetime.strptime(inv.expires_at, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > exp_dt:
            inv.status = "revoked"
            return None

        return inv

    # --------------------------------------------------------------------
    # 4. In-App Threaded Comments System
    # --------------------------------------------------------------------
    def add_comment(
        self,
        analysis_id: str,
        author: UserProfile,
        text: str,
        parent_id: str | None = None,
    ) -> AnalysisComment:
        """Adds a new threaded comment or reply on an analysis session."""
        comment_id = str(uuid.uuid4())
        comment = AnalysisComment(
            id=comment_id,
            analysis_id=analysis_id,
            user_id=author.id,
            user_name=author.name,
            user_avatar=author.avatar_url,
            parent_id=parent_id,
            text=text,
        )
        self._comments.append(comment)

        self.log_activity(
            user=author,
            action="add_comment",
            analysis_id=analysis_id,
            details={"text_snippet": text[:40]},
        )

        # Notify parent author if this is a reply
        if parent_id:
            parent_comm = next((c for c in self._comments if c.id == parent_id), None)
            if parent_comm and parent_comm.user_id != author.id:
                self.create_notification(
                    user_id=parent_comm.user_id,
                    type="comment",
                    title="Réponse à votre commentaire",
                    message=f"{author.name} a répondu à votre commentaire.",
                    link_url=f"/#analysis?session_id={analysis_id}",
                )

        return comment

    def get_comments(self, analysis_id: str) -> list[AnalysisComment]:
        """Returns sorted list of comments for an analysis session."""
        return [c for c in self._comments if c.analysis_id == analysis_id]

    # --------------------------------------------------------------------
    # 5. Activity Audit Logs & Notifications Center
    # --------------------------------------------------------------------
    def log_activity(
        self,
        user: UserProfile,
        action: str,
        workspace_id: str | None = None,
        analysis_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> ActivityLog:
        """Records an audit trail action event."""
        log_entry = ActivityLog(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            analysis_id=analysis_id,
            user_id=user.id,
            user_name=user.name,
            action=action,
            details=details or {},
        )
        self._activity_logs.append(log_entry)
        return log_entry

    def get_activity_logs(self, workspace_id: str | None = None, analysis_id: str | None = None) -> list[ActivityLog]:
        """Returns audit trail logs filtered by workspace or analysis."""
        logs = self._activity_logs
        if workspace_id:
            logs = [l for l in logs if l.workspace_id == workspace_id]
        if analysis_id:
            logs = [l for l in logs if l.analysis_id == analysis_id]
        return sorted(logs, key=lambda l: l.created_at, reverse=True)

    def create_notification(self, user_id: str, type: str, title: str, message: str, link_url: str | None = None) -> Notification:
        """Creates an in-app notification for a user."""
        noti = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            link_url=link_url,
        )
        self._notifications.append(noti)
        return noti

    def get_user_notifications(self, user_id: str) -> list[Notification]:
        """Returns sorted notifications for a user."""
        user_notis = [n for n in self._notifications if n.user_id == user_id]
        return sorted(user_notis, key=lambda n: n.created_at, reverse=True)

    def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Marks a notification as read."""
        for n in self._notifications:
            if n.id == notification_id and n.user_id == user_id:
                n.is_read = True
                return True
        return False
