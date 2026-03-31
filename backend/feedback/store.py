"""
Simple in-memory feedback storage.
Stores user feedback on RAG responses for quality monitoring.
"""
from __future__ import annotations

import time
from typing import Any


class FeedbackStore:
    """In-memory feedback store. Replace with DB for production."""

    def __init__(self):
        self.entries: list[dict[str, Any]] = []

    def add(
        self,
        session_id: str,
        query: str,
        rating: int,
        comment: str = '',
    ) -> dict:
        entry = {
            'id': len(self.entries) + 1,
            'session_id': session_id,
            'query': query,
            'rating': rating,
            'comment': comment,
            'timestamp': time.time(),
        }
        self.entries.append(entry)
        return entry

    def get_all(self) -> list[dict]:
        return self.entries

    def average_rating(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e['rating'] for e in self.entries) / len(self.entries)


# Module-level singleton
feedback_store = FeedbackStore()
