"""
Per-session conversation history with sliding context window.
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
        """Add one Q&A turn. Keep only most recent max_turns."""
        self.store[session_id].append({
            'user': user_query,
            'assistant': response,
        })
        if len(self.store[session_id]) > self.max_turns:
            self.store[session_id] = self.store[session_id][
                -self.max_turns:
            ]

    def get_history(self, session_id: str, for_retrieval: bool = False) -> str:
        """
        Return formatted history string.

        for_retrieval=True  → compact form, only user turns (used to enrich
                              the search query; no need for full answers)
        for_retrieval=False → full form with both sides, sent to the LLM
                              prompt so it can understand references like
                              "that order", "what about it", "as you said"
        """
        turns = self.store.get(session_id, [])
        if not turns:
            return ''

        lines: list[str] = []

        if for_retrieval:
            # Just user questions — lightweight, only affects vector search
            for t in turns:
                lines.append(f"User: {t['user']}")
        else:
            # Full turns for LLM generation context
            for i, t in enumerate(turns, 1):
                lines.append(f"[Turn {i}]")
                lines.append(f"Customer: {t['user']}")
                # Smart truncation: keep first 300 chars of answer
                # That captures the key info without flooding tokens
                answer_preview = t['assistant'][:300]
                if len(t['assistant']) > 300:
                    answer_preview += '…'
                lines.append(f"Agent: {answer_preview}")
                lines.append('')

        return '\n'.join(lines)

    def clear(self, session_id: str) -> None:
        self.store.pop(session_id, None)

    def sessions(self) -> list[str]:
        return list(self.store.keys())


# Module-level singleton
memory_store = ConversationMemory()
