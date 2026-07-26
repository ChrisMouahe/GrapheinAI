"""Multi-channel Notification Service for GraphEin AI (Email, In-App, and Push)."""

import time
import uuid
import logging
from typing import Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class InAppNotification(BaseModel):
    """Data model for in-app notifications stored in user notification feed."""

    notification_id: str = Field(..., description="Unique notification ID")
    user_id: str = Field(..., description="Recipient user ID")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message body")
    type: str = Field(default="info", description="Notification type ('info', 'success', 'warning', 'comment', 'analysis')")
    link_url: str | None = Field(default=None, description="Navigation target URL")
    is_read: bool = Field(default=False, description="Read flag status")
    created_at: float = Field(default_factory=time.time, description="Creation epoch timestamp")


class NotificationService:
    """Centralized notification service dispatching across Email, In-App feeds, and Push channels."""

    def __init__(self, email_service: Any = None) -> None:
        self.email_service = email_service
        self._in_app_notifications: dict[str, list[InAppNotification]] = {}

    def set_email_service(self, email_service: Any) -> None:
        """Sets the email service reference."""
        self.email_service = email_service

    def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        user_email: str | None = None,
        type: str = "info",
        link_url: str | None = None,
        send_email: bool = True,
        lang: str = "fr",
    ) -> InAppNotification:
        """Dispatches notification via In-App feed and optionally queues an email dispatch."""
        notif_id = f"notif_{uuid.uuid4().hex[:12]}"
        notif = InAppNotification(
            notification_id=notif_id,
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            link_url=link_url,
            is_read=False,
        )

        if user_id not in self._in_app_notifications:
            self._in_app_notifications[user_id] = []
        self._in_app_notifications[user_id].insert(0, notif)

        logger.info(f"[NotificationService] Dispatched in-app notification to user {user_id}: '{title}'")

        if send_email and user_email and self.email_service:
            try:
                self.email_service.sendCommentNotification(
                    to_email=user_email,
                    user_name=user_id,
                    commenter_name="GraphEin AI",
                    comment_text=message,
                    chart_title=title,
                    workspace_name="GraphEin Workspace",
                    action_url=link_url or "http://localhost:8088",
                    lang=lang,
                )
            except Exception as e:
                logger.warning(f"[NotificationService] Failed to send notification email: {e}")

        return notif

    def get_user_notifications(self, user_id: str) -> list[InAppNotification]:
        """Retrieves in-app notification feed for a user."""
        return self._in_app_notifications.get(user_id, [])

    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """Marks a notification as read."""
        notifs = self._in_app_notifications.get(user_id, [])
        for n in notifs:
            if n.notification_id == notification_id:
                n.is_read = True
                return True
        return False
