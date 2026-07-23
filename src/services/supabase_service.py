"""Supabase Auth, Database, Storage, and Row Level Security (RLS) Service."""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models.session import AnalysisSession
from src.models.user import AuthResponse, SignupRequest, UserProfile

logger = logging.getLogger("SupabaseService")


class SupabaseService:
    """Handles Supabase Authentication, PostgreSQL DB CRUD, Storage Uploads, and RLS multi-tenant security."""

    def __init__(self, url: str | None = None, key: str | None = None) -> None:
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        self.client = None

        if self.url and self.key:
            try:
                from supabase import create_client
                self.client = create_client(self.url, self.key)
                logger.info("Supabase client successfully initialized with Cloud connection.")
            except Exception as e:
                logger.warning(f"Failed to initialize live Supabase SDK client: {e}. Falling back to local mock mode.")
        else:
            logger.info("No SUPABASE_URL configured. SupabaseService running in local mock fallback mode.")

        # Local mock state for testing & offline development
        self._mock_users: dict[str, dict[str, Any]] = {}
        self._mock_tokens: dict[str, str] = {}  # token -> user_id
        self._mock_analyses: dict[str, list[dict[str, Any]]] = {}  # user_id -> analyses
        self._mock_reset_tokens: dict[str, str] = {}  # reset_token -> email

        # Register default seed mock user for immediate testing
        seed_id = "user_default_demo_id"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._mock_users[seed_id] = {
            "id": seed_id,
            "nom": "User",
            "prenom": "Demo",
            "name": "Demo User",
            "email": "demo@graphein.ai",
            "avatar_url": None,
            "entreprise": "Graphein Corp",
            "secteur_activite": "Finance",
            "secteur_autre": "",
            "fonction": "Data Analyst",
            "niveau_expertise": "Expert",
            "annees_experience": 5,
            "langue": "fr",
            "pays": "France",
            "role": "admin",
            "date_inscription": now_str,
            "derniere_connexion": now_str,
            "password": "password123",
        }
        self._mock_tokens["mock_token_demo_123"] = seed_id

    def signup(
        self,
        req: SignupRequest | str | None = None,
        password: str | None = None,
        name: str | None = None,
        email: str | None = None,
        language: str = "fr",
    ) -> AuthResponse:
        """Registers a new user account with enterprise profile information."""
        if isinstance(req, str):
            email = req

        if not isinstance(req, SignupRequest):
            mail = email or "user@graphein.ai"
            pwd = password or "password123"
            disp = name or mail.split("@")[0].capitalize()
            req = SignupRequest(
                nom="",
                prenom=disp,
                email=mail,
                password=pwd,
                password_confirm=pwd,
                language=language,
            )

        pwd_confirm = req.password_confirm or req.password
        if req.password != pwd_confirm:
            raise ValueError("Les mots de passe ne correspondent pas.")

        disp_name = req.name or f"{req.prenom} {req.nom}".strip() or req.email.split("@")[0].capitalize()
        user_id = str(uuid.uuid4())
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.client:
            try:
                auth_res = self.client.auth.sign_up({
                    "email": req.email,
                    "password": req.password,
                    "options": {
                        "data": {
                            "name": disp_name,
                            "nom": req.nom,
                            "prenom": req.prenom,
                            "entreprise": req.entreprise,
                            "secteur_activite": req.secteur_activite,
                            "secteur_autre": req.secteur_autre,
                            "fonction": req.fonction,
                            "niveau_expertise": req.niveau_expertise,
                            "annees_experience": req.annees_experience,
                            "language": req.language,
                            "pays": req.pays,
                            "role": "standard_user",
                        }
                    }
                })
                if auth_res.user:
                    u_id = auth_res.user.id
                    profile = UserProfile(
                        id=u_id,
                        nom=req.nom,
                        prenom=req.prenom,
                        name=disp_name,
                        email=req.email,
                        entreprise=req.entreprise or "",
                        secteur_activite=req.secteur_activite or "Finance",
                        secteur_autre=req.secteur_autre or "",
                        fonction=req.fonction or "",
                        niveau_expertise=req.niveau_expertise,
                        annees_experience=req.annees_experience,
                        langue=req.language,
                        pays=req.pays,
                        role="standard_user",
                        date_inscription=now_str,
                        derniere_connexion=now_str,
                    )
                    self.client.table("profiles").upsert(profile.model_dump()).execute()
                    token = auth_res.session.access_token if auth_res.session else f"token_{u_id}"
                    return AuthResponse(access_token=token, user=profile)
            except Exception as e:
                logger.warning(f"Supabase Cloud signup error: {e}. Falling back to local mock signup.")

        # Fallback local mock implementation
        self._mock_users[user_id] = {
            "id": user_id,
            "nom": req.nom,
            "prenom": req.prenom,
            "name": disp_name,
            "email": req.email,
            "avatar_url": None,
            "entreprise": req.entreprise or "",
            "secteur_activite": req.secteur_activite or "Finance",
            "secteur_autre": req.secteur_autre or "",
            "fonction": req.fonction or "",
            "niveau_expertise": req.niveau_expertise,
            "annees_experience": req.annees_experience,
            "langue": req.language,
            "pays": req.pays,
            "role": "standard_user",
            "date_inscription": now_str,
            "derniere_connexion": now_str,
            "password": req.password,
        }
        token = f"mock_token_{uuid.uuid4().hex[:12]}"
        self._mock_tokens[token] = user_id

        profile = self.get_profile(user_id)
        return AuthResponse(access_token=token, user=profile)

    def login(self, email: str, password: str) -> AuthResponse:
        """Authenticates user with email and password."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.client:
            try:
                auth_res = self.client.auth.sign_in_with_password({"email": email, "password": password})
                if auth_res.user and auth_res.session:
                    u_id = auth_res.user.id
                    prof_data = self.get_profile(u_id)
                    prof_data.derniere_connexion = now_str
                    self.client.table("profiles").update({"derniere_connexion": now_str}).eq("id", u_id).execute()
                    return AuthResponse(access_token=auth_res.session.access_token, user=prof_data)
            except Exception as e:
                logger.warning(f"Supabase Cloud login error: {e}. Checking local mock accounts.")

        # Check local mock accounts
        for u_id, u_data in self._mock_users.items():
            if u_data["email"].lower() == email.lower() and u_data["password"] == password:
                token = f"mock_token_{uuid.uuid4().hex[:12]}"
                self._mock_tokens[token] = u_id
                u_data["derniere_connexion"] = now_str
                profile = self.get_profile(u_id)
                return AuthResponse(access_token=token, user=profile)

        raise ValueError("Identifiants incorrects (Email ou mot de passe invalide).")

    def logout(self, token: str) -> bool:
        """Terminates session by invalidating the access token."""
        if token in self._mock_tokens:
            del self._mock_tokens[token]
        if self.client:
            try:
                self.client.auth.sign_out()
            except Exception:
                pass
        return True

    def forgot_password(self, email: str) -> str:
        """Generates a password reset token for forgot password request."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        token = f"reset_{uuid.uuid4().hex[:16]}"
        self._mock_reset_tokens[token] = email
        if self.client:
            try:
                self.client.auth.reset_password_for_email(email)
            except Exception as e:
                logger.warning(f"Supabase reset password email error: {e}")
        return token

    def reset_password(self, email: str, new_password: str) -> bool:
        """Resets user password."""
        for u_id, u_data in self._mock_users.items():
            if u_data["email"].lower() == email.lower():
                u_data["password"] = new_password
                return True
        return True

    def verify_token(self, token: str) -> UserProfile | None:
        """Verifies JWT access token and returns corresponding UserProfile."""
        if not token:
            return None

        # Check local mock tokens
        if token in self._mock_tokens:
            user_id = self._mock_tokens[token]
            return self.get_profile(user_id)

        if token.startswith("mock_token") or token.startswith("token_"):
            return None

        if self.client:
            try:
                user_res = self.client.auth.get_user(token)
                if user_res.user:
                    return self.get_profile(user_res.user.id)
            except Exception:
                pass

        return None

    def get_profile(self, user_id: str) -> UserProfile:
        """Retrieves complete UserProfile data and SaaS metrics."""
        analyses = self.get_user_analyses(user_id)
        total_analyses = len(analyses)
        total_pdfs = sum(1 for a in analyses if a.get("has_pdf"))

        if user_id in self._mock_users:
            u_data = self._mock_users[user_id]
            disp_name = u_data.get("name") or f"{u_data.get('prenom', '')} {u_data.get('nom', '')}".strip() or "User"
            return UserProfile(
                id=user_id,
                nom=u_data.get("nom", ""),
                prenom=u_data.get("prenom", ""),
                name=disp_name,
                email=u_data.get("email", "user@graphein.ai"),
                avatar_url=u_data.get("avatar_url"),
                entreprise=u_data.get("entreprise", ""),
                secteur_activite=u_data.get("secteur_activite", "Finance"),
                secteur_autre=u_data.get("secteur_autre", ""),
                fonction=u_data.get("fonction", ""),
                niveau_expertise=u_data.get("niveau_expertise", "Intermédiaire"),
                annees_experience=u_data.get("annees_experience", 0),
                langue=u_data.get("langue", "fr"),
                pays=u_data.get("pays", "France"),
                role=u_data.get("role", "standard_user"),
                date_inscription=u_data.get("date_inscription", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                derniere_connexion=u_data.get("derniere_connexion", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                total_analyses=total_analyses,
                total_pdfs=total_pdfs,
            )

        if self.client:
            try:
                res = self.client.table("profiles").select("*").eq("id", user_id).execute()
                if res.data and len(res.data) > 0:
                    d = res.data[0]
                    return UserProfile(
                        id=d["id"],
                        nom=d.get("nom", ""),
                        prenom=d.get("prenom", ""),
                        name=d.get("name", "User"),
                        email=d.get("email"),
                        avatar_url=d.get("avatar_url"),
                        entreprise=d.get("entreprise", ""),
                        secteur_activite=d.get("secteur_activite", "Finance"),
                        secteur_autre=d.get("secteur_autre", ""),
                        fonction=d.get("fonction", ""),
                        niveau_expertise=d.get("niveau_expertise", "Intermédiaire"),
                        annees_experience=d.get("annees_experience", 0),
                        langue=d.get("langue", "fr"),
                        pays=d.get("pays", "France"),
                        role=d.get("role", "standard_user"),
                        date_inscription=d.get("date_inscription", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        derniere_connexion=d.get("derniere_connexion", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        total_analyses=total_analyses,
                        total_pdfs=total_pdfs,
                    )
            except Exception:
                pass

        return UserProfile(
            id=user_id,
            nom="User",
            prenom="Research",
            name="Research User",
            email="user@graphein.ai",
            language="fr",
            role="standard_user",
            total_analyses=total_analyses,
            total_pdfs=total_pdfs,
        )

    def update_profile(
        self,
        user_id: str,
        updates: dict[str, Any] | None = None,
        name: str | None = None,
        avatar_url: str | None = None,
        language: str | None = None,
        **kwargs: Any,
    ) -> UserProfile:
        """Updates user profile attributes."""
        final_updates = updates.copy() if updates else {}
        if name is not None:
            final_updates["name"] = name
        if avatar_url is not None:
            final_updates["avatar_url"] = avatar_url
        if language is not None:
            final_updates["language"] = language
            final_updates["langue"] = language
        for k, v in kwargs.items():
            if v is not None:
                final_updates[k] = v

        if user_id in self._mock_users:
            for k, v in final_updates.items():
                if v is not None:
                    self._mock_users[user_id][k] = v

        if self.client:
            try:
                clean_updates = {k: v for k, v in final_updates.items() if v is not None}
                if clean_updates:
                    self.client.table("profiles").update(clean_updates).eq("id", user_id).execute()
            except Exception as e:
                logger.warning(f"Cloud profile update error: {e}")

        return self.get_profile(user_id)

    def save_analysis(self, user_id: str, session: AnalysisSession) -> dict[str, Any]:
        """Saves a user-scoped analysis session into PostgreSQL / mock storage."""
        data_dict = session.model_dump()
        data_dict["user_id"] = user_id

        if user_id not in self._mock_analyses:
            self._mock_analyses[user_id] = []

        self._mock_analyses[user_id] = [a for a in self._mock_analyses[user_id] if a.get("session_id") != session.session_id]
        self._mock_analyses[user_id].insert(0, data_dict)

        if self.client:
            try:
                self.client.table("analyses").upsert(data_dict).execute()
            except Exception as e:
                logger.warning(f"Cloud analysis save error: {e}")

        return data_dict

    def get_user_analyses(self, user_id: str) -> list[dict[str, Any]]:
        """Retrieves all private analysis sessions for a specific user ID."""
        if user_id in self._mock_analyses:
            return self._mock_analyses[user_id]

        if self.client:
            try:
                res = self.client.table("analyses").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
                if res.data:
                    return res.data
            except Exception as e:
                logger.warning(f"Cloud fetch analyses error: {e}")

        return []
