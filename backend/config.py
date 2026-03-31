"""
Central configuration — all paths, model names, and retrieval parameters.
Mirrors the exact settings from the Kaggle notebook (retriever_config.json).
"""
from __future__ import annotations

import os
from pathlib import Path

# ── Directory Layout ──────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent          # backend/
PROJECT_DIR = BASE_DIR.parent                       # GenAI/
FAISS_DIR = PROJECT_DIR / "faiss_indexes"
EMBEDDINGS_DIR = PROJECT_DIR / "embeddings"
PROCESSED_DIR = PROJECT_DIR / "processed_dataset"

# ── Embedding Model ──────────────────────────────────────────
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384

# ── Cross-Encoder Re-ranker ──────────────────────────────────
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ── FAISS Index Files ────────────────────────────────────────
FAISS_INDEXES = {
    "main": "main.index",
    "policy": "policy.index",
    "complaints": "complaints.index",
}
CHUNK_FILES = {
    "main": "chunks_main.json",
    "policy": "chunks_policy.json",
    "complaints": "chunks_complaints.json",
}

# ── Retrieval Parameters ─────────────────────────────────────
DEFAULT_K = 5
MIN_SCORE = 0.25
DENSE_WEIGHT = 0.6
SPARSE_WEIGHT = 0.4

# ── LLM (Groq) ──────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
LLM_MODEL = "llama-3.1-8b-instant"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 600

# ── Conversation Memory ─────────────────────────────────────
MEMORY_MAX_TURNS = 5
