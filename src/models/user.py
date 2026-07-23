"""Enterprise User and authentication Pydantic v2 data models for GrapheinAI."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    """Enterprise user profile data model with SaaS metrics and AI personalization context."""

    id: str = Field(..., description="Unique UUID identifier for the user")
    nom: str = Field(default="", description="Last name / Nom de famille")
    prenom: str = Field(default="", description="First name / Prénom")
    name: str = Field(..., description="Display full name of the user")
    email: str = Field(..., description="Registered user email address")
    avatar_url: str | None = Field(default=None, description="Optional avatar profile picture URL")
    entreprise: str | None = Field(default="", description="Company / Enterprise name")
    secteur_activite: str | None = Field(default="Finance", description="Activity sector (e.g., Finance, Santé, Marketing, Autre)")
    secteur_autre: str | None = Field(default="", description="Free text sector if secteur_activite is 'Autre'")
    fonction: str | None = Field(default="", description="Job title / Function")
    niveau_expertise: str = Field(default="Intermédiaire", description="Expertise level ('Débutant', 'Intermédiaire', 'Avancé', 'Expert')")
    annees_experience: int = Field(default=0, description="Years of professional experience")
    langue: str = Field(default="fr", description="Preferred UI language ('fr' or 'en')")
    pays: str | None = Field(default="France", description="Country of residence")
    role: str = Field(default="standard_user", description="SaaS role ('admin', 'standard_user', 'guest', 'collaborator')")
    is_suspended: bool = Field(default=False, description="True if user account is suspended by Admin")
    date_inscription: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="Member signup timestamp")
    derniere_connexion: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description="Last login timestamp")
    total_analyses: int = Field(default=0, description="Total private chart analysis sessions performed")
    total_pdfs: int = Field(default=0, description="Total ReportLab PDF reports generated")

    @property
    def language(self) -> str:
        """Alias property for preferred UI language."""
        return self.langue


class AuthCredentials(BaseModel):
    """Authentication credentials payload for login."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 characters)")
    remember_me: bool = Field(default=False, description="Remember login session flag")


class SignupRequest(BaseModel):
    """Registration payload with enterprise profile fields."""

    email: str = Field(..., description="Registered user email address")
    password: str = Field(..., min_length=6, description="Password")
    password_confirm: str | None = Field(default=None, description="Password confirmation")
    nom: str = Field(default="", description="Last name / Nom")
    prenom: str = Field(default="", description="First name / Prénom")
    name: str | None = Field(default=None, description="Display name")
    terms_accepted: bool = Field(default=True, description="Acceptance of terms of service")
    entreprise: str | None = Field(default="", description="Company name")
    secteur_activite: str | None = Field(default="Finance", description="Activity sector")
    secteur_autre: str | None = Field(default="", description="Free text sector if 'Autre' is selected")
    fonction: str | None = Field(default="", description="Professional role / title")
    niveau_expertise: str = Field(default="Intermédiaire", description="Expertise level ('Débutant', 'Intermédiaire', 'Avancé', 'Expert')")
    annees_experience: int = Field(default=0, description="Years of professional experience")
    pays: str = Field(default="France", description="Country")
    language: str = Field(default="fr", description="Preferred UI language")

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        import re
        if not re.search(r"[A-Z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une lettre majuscule.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une lettre minuscule.")
        if not re.search(r"\d", v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre.")
        return v


class AuthResponse(BaseModel):
    """Payload returned upon successful login or signup."""

    access_token: str = Field(..., description="JWT Bearer access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserProfile = Field(..., description="Authenticated user profile details")
    expires_in: int = Field(default=3600, description="Token validity duration in seconds")


class UpdateProfileRequest(BaseModel):
    """Request payload for updating user profile info."""

    nom: str | None = None
    prenom: str | None = None
    name: str | None = None
    avatar_url: str | None = None
    entreprise: str | None = None
    secteur_activite: str | None = None
    secteur_autre: str | None = None
    fonction: str | None = None
    niveau_expertise: str | None = None
    annees_experience: int | None = None
    langue: str | None = None
    pays: str | None = None


class ForgotPasswordRequest(BaseModel):
    """Request payload for forgot password trigger."""

    email: str


PasswordResetRequest = ForgotPasswordRequest


class ResetPasswordRequest(BaseModel):
    """Request payload for password reset."""

    token: str | None = None
    email: str | None = None
    new_password: str = Field(default="newPassword123", min_length=6)
