"""AnalysisSessionManager service handling creation, storage, re-extraction, and reopening of isolated chart analysis sessions."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models.session import AnalysisSession, SessionStatus
from src.services.cache_manager import CacheManager

logger = logging.getLogger("AnalysisSessionManager")


class AnalysisSessionManager:
    """Manages independent chart analysis sessions, persistence, and state isolation."""

    def __init__(self, storage_dir: Path | str | None = None, cache_manager: CacheManager | None = None) -> None:
        if storage_dir is None:
            storage_dir = Path("data/sessions")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.cache_manager = cache_manager or CacheManager()
        self.active_session: AnalysisSession | None = None
        self._session_history: dict[str, AnalysisSession] = {}
        self._load_sessions_from_disk()

    def _load_sessions_from_disk(self) -> None:
        """Loads historical saved sessions from disk."""
        history_file = self.storage_dir / "sessions_index.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for s_dict in data:
                        session = AnalysisSession.model_validate(s_dict)
                        self._session_history[session.session_id] = session
            except Exception as e:
                logger.warning(f"Failed to load sessions index from disk: {e}")

    def _save_sessions_to_disk(self) -> None:
        """Persists historical sessions to disk."""
        history_file = self.storage_dir / "sessions_index.json"
        try:
            sessions_data = [s.model_dump() for s in self._session_history.values()]
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save sessions index to disk: {e}")

    def create_session(
        self,
        image_path: Path | str,
        file_name: str,
        target_language: str = "fr",
        flush_cache: bool = True,
    ) -> AnalysisSession:
        """Creates a brand new isolated analysis session and completely flushes previous active workspace context."""
        if flush_cache:
            self.cache_manager.clear_all()

        img_p = Path(image_path)
        session_id = f"session_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        new_session = AnalysisSession(
            session_id=session_id,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            file_name=file_name,
            image_path=str(img_p.resolve()),
            thumbnail_path=str(img_p.resolve()),
            chart_type="bar",
            target_language=target_language,
            status=SessionStatus.EXTRACTING,
        )

        self.active_session = new_session
        self._session_history[session_id] = new_session
        self._save_sessions_to_disk()

        logger.info(f"Created new isolated session '{session_id}' for file '{file_name}' [lang={target_language}]")
        return new_session

    def get_active_session(self) -> AnalysisSession | None:
        """Returns currently active workspace session."""
        return self.active_session

    def save_active_session(self) -> None:
        """Saves current active session to history store."""
        if self.active_session:
            self._session_history[self.active_session.session_id] = self.active_session
            self._save_sessions_to_disk()

    def get_session_history(self) -> list[AnalysisSession]:
        """Returns sorted list of all historical sessions (newest first)."""
        sessions = list(self._session_history.values())
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        return sessions

    def reopen_session(self, session_id: str) -> AnalysisSession:
        """Reopens a historical session into the active workspace."""
        if session_id not in self._session_history:
            raise KeyError(f"Session ID '{session_id}' not found in history.")

        session = self._session_history[session_id]
        self.active_session = session
        logger.info(f"Reopened historical session '{session_id}' into active workspace.")
        return session

    def clear_active_session(self) -> None:
        """Resets active workspace session."""
        self.active_session = None
