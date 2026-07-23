"""Abstract base class and data models for email providers in GraphEin AI."""

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    """Payload representing a single email message dispatch request."""

    to_email: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    html_body: str = Field(..., description="HTML rendered body")
    text_body: str = Field(..., description="Plain text fallback body")
    from_email: str | None = Field(default=None, description="Sender email address")
    from_name: str | None = Field(default=None, description="Sender display name")
    reply_to: str | None = Field(default=None, description="Reply-to email address")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata tags for tracking")
    tags: list[str] = Field(default_factory=list, description="Categorization tags")


class EmailDispatchResult(BaseModel):
    """Result status object returned after attempting an email dispatch."""

    success: bool = Field(..., description="Indicates whether dispatch succeeded")
    message_id: str = Field(default="", description="Provider unique message identifier")
    provider_name: str = Field(..., description="Name of email provider utilized")
    error: str | None = Field(default=None, description="Error message if dispatch failed")
    latency_ms: float = Field(default=0.0, description="Dispatch latency in milliseconds")


class BaseEmailProvider(ABC):
    """Abstract interface for all pluggable GraphEin AI email providers."""

    def __init__(self, provider_name: str) -> None:
        self.provider_name = provider_name

    @abstractmethod
    def send_email(self, message: EmailMessage) -> EmailDispatchResult:
        """Sends an email message via the specific provider implementation."""
        pass

    @abstractmethod
    def verify_connection(self) -> bool:
        """Verifies connection health to the email delivery provider service."""
        pass
