"""Conversation Manager module for tracking multi-turn chat history per chart session."""

import logging
import time
from typing import Any

from src.models.chart import ConversationTurn, QuestionIntent

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages chat message history for multi-turn chart analysis conversations."""

    def __init__(self, max_history_turns: int = 10) -> None:
        self.max_history_turns = max_history_turns
        self._sessions: dict[str, list[ConversationTurn]] = {}

    def get_history(self, session_id: str) -> list[ConversationTurn]:
        """Retrieves history turns for a session ID."""
        return self._sessions.get(session_id, [])

    def add_user_turn(self, session_id: str, message: str, intent: QuestionIntent | None = None) -> ConversationTurn:
        """Adds a user turn to session history."""
        turn = ConversationTurn(
            role="user",
            content=message.strip(),
            timestamp=time.time(),
            intent=intent,
        )
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append(turn)
        self._trim_session(session_id)
        return turn

    def add_assistant_turn(self, session_id: str, message: str) -> ConversationTurn:
        """Adds an assistant turn to session history."""
        turn = ConversationTurn(
            role="assistant",
            content=message.strip(),
            timestamp=time.time(),
            intent=None,
        )
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append(turn)
        self._trim_session(session_id)
        return turn

    def clear_session(self, session_id: str) -> None:
        """Clears all conversation turns for a session ID."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def format_history_prompt(self, session_id: str) -> str:
        """Formats conversation history into text suitable for LLM prompt context."""
        history = self.get_history(session_id)
        if not history:
            return "Historique de discussion : Aucun échange précédent."

        lines = ["Historique de la conversation liée à ce graphique :"]
        for turn in history[-self.max_history_turns:]:
            prefix = "Utilisateur" if turn.role == "user" else "Assistant AI"
            intent_str = f" [Intent: {turn.intent.value}]" if turn.intent else ""
            lines.append(f"- {prefix}{intent_str}: {turn.content}")

        return "\n".join(lines)

    def _trim_session(self, session_id: str) -> None:
        """Trims session history to max_history_turns."""
        if session_id in self._sessions and len(self._sessions[session_id]) > self.max_history_turns * 2:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history_turns * 2:]
