from typing import Dict, List
from app.schemas.models import ChatMessage


class SessionStore:
    """In-memory store for chat sessions."""

    def __init__(self):
        self.sessions: Dict[str, List[ChatMessage]] = {}

    def get_session(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: list = None
    ):
        """Add a message to a session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        message = ChatMessage(
            role=role,
            content=content,
            citations=citations or []
        )
        self.sessions[session_id].append(message)

    def clear_session(self, session_id: str):
        """Clear a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def list_sessions(self) -> List[str]:
        """List all active session IDs."""
        return list(self.sessions.keys())


# Global session store
_store: SessionStore = None


def get_session_store() -> SessionStore:
    """Get or create session store."""
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
