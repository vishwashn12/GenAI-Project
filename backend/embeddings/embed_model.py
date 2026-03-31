"""
SentenceTransformer embedding model loader.
Singleton pattern to avoid reloading the model.
Mirrors notebook Cell 6 / Phase 3 Cell 2.
"""
from __future__ import annotations

from sentence_transformers import SentenceTransformer

from config import EMBED_MODEL_NAME

_model: SentenceTransformer | None = None


def get_embed_model() -> SentenceTransformer:
    """Return the cached embedding model (loaded once on first call)."""
    global _model
    if _model is None:
        # CPU-only for backend server (no CUDA dependency needed)
        _model = SentenceTransformer(EMBED_MODEL_NAME, device="cpu")
        dim = _model.get_sentence_embedding_dimension()
        print(f"✓ Embedding model loaded: {EMBED_MODEL_NAME} (dim={dim})")
    return _model
