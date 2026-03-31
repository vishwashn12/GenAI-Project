"""
Per-session conversation history with sliding context window.
Exact replica of Phase 3 Cell 18A.
"""
from __future__ import annotations

from collections import defaultdict

from config import MEMORY_MAX_TURNS


class ConversationMemory:
    """
    Per-session conversation history with sliding context window.
    Production upgrade: replace self.store with Redis or a database.
    """

    def __init__(self, max_turns: int = MEMORY_MAX_TURNS):
        self.store: dict[str, list[dict]] = defaultdict(list)
        self.max_turns = max_turns

    def add_turn(
        self, session_id: str, user_query: str, response: str
    ) -> None:
        """Add one Q&A turn.  Keep only most recent max_turns."""
        self.store[session_id].append({
            'user': user_query,
            'assistant': response,
        })
        if len(self.store[session_id]) > self.max_turns:
            self.store[session_id] = self.store[session_id][
                -self.max_turns:
            ]

    def get_history(self, session_id: str) -> str:
        """Return formatted history string for context injection."""
        turns = self.store.get(session_id, [])
        if not turns:
            return ''
        lines: list[str] = []
        for t in turns:
            lines.append(f"User: {t['user']}")
            # truncate saves tokens
            lines.append(f"Assistant: {t['assistant'][:500]}...")
        return '\n'.join(lines)

    def clear(self, session_id: str) -> None:
        self.store.pop(session_id, None)

    def sessions(self) -> list[str]:
        return list(self.store.keys())


# Module-level singleton
memory_store = ConversationMemory()
