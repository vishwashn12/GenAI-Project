"""
RAG client — connects the /chat route to the OlistRAGSystem.
Updated to use app.state.rag_system instead of a dummy.
"""
from __future__ import annotations

from typing import Any


def ask_rag(query: str, order_id: str = "", app=None) -> dict:
    """
    Call the production RAG system.
    `app` is the FastAPI app instance, passed from the route.
    """
    if app is None or not hasattr(app.state, 'rag_system'):
        raise RuntimeError(
            "RAG system is not loaded. "
            "The server may still be starting up."
        )

    rag_system = app.state.rag_system
    result = rag_system.answer(query=query, order_id=order_id)

    if not isinstance(result, dict):
        raise RuntimeError("rag_system.answer must return a dictionary")

    return result
