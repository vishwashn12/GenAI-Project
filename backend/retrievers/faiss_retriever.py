"""
FAISSRetriever — exact replica of notebook Cell 12 + Phase 3 Cell 2.
FAISS-based retriever with intent routing across three indexes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import (
    DEFAULT_K,
    FAISS_DIR,
    FAISS_INDEXES,
    CHUNK_FILES,
    MIN_SCORE,
)


@dataclass
class RetrievedDoc:
    """Retrieved document with all scoring fields (Phase 3 version)."""
    text: str
    source: str
    metadata: dict
    dense_score: float = 0.0
    sparse_score: float = 0.0
    rerank_score: float = 0.0
    final_score: float = 0.0


class FAISSRetriever:
    """
    FAISS-based retriever with intent routing across three indexes.
    Interface identical to the original OlistRetriever.
    Works with Phase 3 RAG chain and LangGraph agent without any changes.
    """

    REFUND_KW = ['refund', 'return', 'cancel', 'money back', 'chargeback']
    POLICY_KW = ['policy', 'rules', 'allowed', 'eligible', 'rights',
                 'how many days', 'cdc']
    COMPLAINT_KW = ['broken', 'defective', 'late', 'delayed', 'lost',
                    'wrong item', 'damaged', 'not working']

    def __init__(
        self,
        embed_model: SentenceTransformer,
        idx_main: faiss.Index,
        chunks_main: list,
        idx_policy: faiss.Index,
        chunks_policy: list,
        idx_complaints: faiss.Index,
        chunks_complaints: list,
    ):
        self.model = embed_model
        self.indexes = {
            'main': (idx_main, chunks_main),
            'policy': (idx_policy, chunks_policy),
            'complaints': (idx_complaints, chunks_complaints),
        }

    # ── Query routing ─────────────────────────────────────────
    def _route(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in self.REFUND_KW + self.POLICY_KW):
            return 'policy'
        if any(k in q for k in self.COMPLAINT_KW):
            return 'complaints'
        return 'main'

    # ── Embed query ───────────────────────────────────────────
    def _embed(self, query: str) -> np.ndarray:
        return self.model.encode(
            [query], normalize_embeddings=True
        ).astype('float32')

    # ── Retrieve ──────────────────────────────────────────────
    def retrieve(
        self,
        query: str,
        k: int = DEFAULT_K,
        min_score: float = MIN_SCORE,
        source_filter: Optional[str] = None,
    ) -> list[RetrievedDoc]:
        """
        Retrieve top-k documents for query.
        Returns list of RetrievedDoc.
        """
        route = (source_filter
                 if source_filter in self.indexes
                 else self._route(query))
        index, chunks = self.indexes[route]

        q_vec = self._embed(query)

        # Search — fetch 2x to allow score filtering
        fetch_k = min(k * 2, index.ntotal)
        scores, indices = index.search(q_vec, fetch_k)

        results: list[RetrievedDoc] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for unfilled slots
                continue
            sim = float(score)  # inner product on normalised vecs = cosine sim
            if sim < min_score:
                continue
            c = chunks[int(idx)]
            results.append(RetrievedDoc(
                text=c['text'],
                source=c['source'],
                metadata=c.get('metadata', {}),
                dense_score=round(sim, 4),
            ))
            if len(results) >= k:
                break

        return results


def load_faiss_indexes() -> dict:
    """Load all FAISS indexes and chunk files from disk."""
    indexes = {}
    chunks = {}

    for name, index_file in FAISS_INDEXES.items():
        index_path = str(FAISS_DIR / index_file)
        idx = faiss.read_index(index_path)
        indexes[name] = idx
        print(f"  ✓ FAISS index '{name}': {idx.ntotal:,} vectors")

    for name, chunk_file in CHUNK_FILES.items():
        chunk_path = FAISS_DIR / chunk_file
        with open(chunk_path, 'r', encoding='utf-8') as f:
            chunks[name] = json.load(f)
        print(f"  ✓ Chunks '{name}': {len(chunks[name]):,} records")

    return indexes, chunks


def build_faiss_retriever(
    embed_model: SentenceTransformer,
) -> FAISSRetriever:
    """Load indexes from disk and build the FAISSRetriever."""
    print("Loading FAISS indexes...")
    indexes, chunks = load_faiss_indexes()

    retriever = FAISSRetriever(
        embed_model=embed_model,
        idx_main=indexes['main'],
        chunks_main=chunks['main'],
        idx_policy=indexes['policy'],
        chunks_policy=chunks['policy'],
        idx_complaints=indexes['complaints'],
        chunks_complaints=chunks['complaints'],
    )
    print("✓ FAISSRetriever ready")
    return retriever, chunks['main']
