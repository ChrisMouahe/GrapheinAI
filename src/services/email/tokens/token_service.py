"""JWT Token Management Service for secure email verification, password resets, and invitations."""

import os
import time
import uuid
import jwt
from typing import Any
from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """Payload stored within a signed email infrastructure JWT token."""

    jti: str = Field(..., description="Unique Token Identifier")
    action: str = Field(..., description="Action type ('password_reset', 'email_verify', 'workspace_invite', 'collaborator_invite', 'otp')")
    email: str = Field(..., description="Target email address")
    user_id: str | None = Field(default=None, description="Associated user ID")
    workspace_id: str | None = Field(default=None, description="Associated workspace ID")
    role: str | None = Field(default="editor", description="Target workspace role")
    exp: int = Field(..., description="Expiration timestamp (unix epoch)")
    iat: int = Field(..., description="Issued at timestamp (unix epoch)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")


class TokenService:
    """Generates, signs, verifies, and revokes secure time-bound tokens for GraphEin AI email dispatches."""

    def __init__(self, secret_key: str | None = None) -> None:
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "graphein_enterprise_secret_key_2026"))
        self.algorithm = "HS256"
        self._blacklisted_jti: set[str] = set()

    def generate_token(
        self,
        action: str,
        email: str,
        user_id: str | None = None,
        workspace_id: str | None = None,
        role: str | None = "editor",
        ttl_seconds: int = 86400,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Generates a signed JWT token for a specific email action."""
        now = int(time.time())
        jti = f"tok_{uuid.uuid4().hex[:14]}"

        payload = {
            "jti": jti,
            "action": action,
            "email": email.lower().strip(),
            "user_id": user_id,
            "workspace_id": workspace_id,
            "role": role,
            "exp": now + ttl_seconds,
            "iat": now,
            "metadata": metadata or {},
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, expected_action: str | None = None) -> TokenPayload:
        """Verifies, decodes, and validates a JWT token.

        Raises ValueError if token is expired, tampered, revoked, or action mismatches.
        """
        try:
            decoded = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            payload = TokenPayload(**decoded)

            if payload.jti in self._blacklisted_jti:
                raise ValueError("Ce lien ou token a déjà été utilisé ou révoqué.")

            if expected_action and payload.action != expected_action:
                raise ValueError(f"Action de token invalide: attendu '{expected_action}', reçu '{payload.action}'.")

            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Le lien d'invitation ou de réinitialisation a expiré (durée de validité dépassée).")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Token de sécurité invalide ou corrompu: {e}")

    def revoke_token(self, jti_or_token: str) -> None:
        """Revokes a token by adding its JTI to the revoked blacklist."""
        if jti_or_token.startswith("ey"):
            try:
                decoded = jwt.decode(jti_or_token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
                self._blacklisted_jti.add(decoded["jti"])
            except Exception:
                pass
        else:
            self._blacklisted_jti.add(jti_or_token)

    def is_revoked(self, jti: str) -> bool:
        """Checks whether a token JTI has been revoked."""
        return jti in self._blacklisted_jti
