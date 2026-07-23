"""Email Providers package for GraphEin AI Enterprise Email Infrastructure."""

from src.services.email.providers.base import BaseEmailProvider, EmailMessage
from src.services.email.providers.brevo import BrevoProvider
from src.services.email.providers.factory import EmailProviderFactory
from src.services.email.providers.maildev import MailDevProvider
from src.services.email.providers.resend import ResendProvider
from src.services.email.providers.smtp import SMTPProvider

__all__ = [
    "BaseEmailProvider",
    "EmailMessage",
    "MailDevProvider",
    "ResendProvider",
    "BrevoProvider",
    "SMTPProvider",
    "EmailProviderFactory",
]
