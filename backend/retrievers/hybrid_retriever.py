"""
HybridRetriever — FAISS Dense + BM25 Sparse + RRF + Cross-Encoder Re-rank.
Exact replica of Phase 3 Cell 4.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
from sentence_transformers import CrossEncoder

from config import DENSE_WEIGHT, SPARSE_WEIGHT, RERANKER_MODEL_NAME
from retrievers.faiss_retriever import FAISSRetriever, RetrievedDoc
from retrievers.bm25_builder import tokenize_for_bm25, BM25Okapi


class HybridRetriever:
    """
    Hybrid retrieval: FAISS dense + BM25 sparse + RRF merge + cross-encoder rerank.
    Identical interface to original guide. ChromaDB replaced with FAISS.
    """

    PRIORITY_BOOST = {'high': 0.15, 'medium': 0.05, 'low': 0.0}

    def __init__(
        self,
        faiss_retriever: FAISSRetriever,
        bm25_index: BM25Okapi,
        chunked_docs: list[dict],
        reranker: CrossEncoder,
        dense_weight: float = DENSE_WEIGHT,
        sparse_weight: float = SPARSE_WEIGHT,
    ):
        self.fr = faiss_retriever
        self.bm25 = bm25_index
        self.docs = chunked_docs
        self.reranker = reranker
        self.dw = dense_weight
        self.sw = sparse_weight

    # ── Dense retrieval (FAISS) ───────────────────────────────
    def _dense_retrieve(self, query: str, k: int) -> list[RetrievedDoc]:
        return self.fr.retrieve(query, k=k, min_score=0.0)

    # ── Sparse retrieval (BM25) ───────────────────────────────
    def _sparse_retrieve(self, query: str, k: int) -> list[RetrievedDoc]:
        tokens = tokenize_for_bm25(query)
        scores = self.bm25.get_scores(tokens)
        top_k = np.argsort(scores)[::-1][:k]
        max_s = scores[top_k[0]] if scores[top_k[0]] > 0 else 1.0
        docs: list[RetrievedDoc] = []
        for idx in top_k:
            if scores[idx] > 0:
                d = self.docs[int(idx)]
                docs.append(RetrievedDoc(
                    text=d['text'],
                    source=d['source'],
                    metadata=d.get('metadata', {}),
                    sparse_score=round(float(scores[idx]) / max_s, 4),
                ))
        return docs

    # ── Reciprocal Rank Fusion ────────────────────────────────
    def _rrf(
        self,
        dense: list[RetrievedDoc],
        sparse: list[RetrievedDoc],
        k_rrf: int = 60,
    ) -> list[RetrievedDoc]:
        scores: dict[str, float] = {}
        dmap: dict[str, RetrievedDoc] = {}
        for rank, doc in enumerate(dense):
            key = doc.text[:80]
            scores[key] = scores.get(key, 0) + self.dw / (k_rrf + rank + 1)
            dmap[key] = doc
        for rank, doc in enumerate(sparse):
            key = doc.text[:80]
            scores[key] = scores.get(key, 0) + self.sw / (k_rrf + rank + 1)
            if key not in dmap:
                dmap[key] = doc
            else:
                dmap[key].sparse_score = doc.sparse_score

        merged: list[RetrievedDoc] = []
        for key, sc in sorted(scores.items(), key=lambda x: -x[1]):
            d = dmap[key]
            d.final_score = round(sc, 5)
            merged.append(d)
        return merged

    # ── Cross-encoder re-rank ─────────────────────────────────
    def _rerank(
        self,
        query: str,
        candidates: list[RetrievedDoc],
        top_n: int,
    ) -> list[RetrievedDoc]:
        if not candidates:
            return []
        scores = self.reranker.predict(
            [(query, d.text) for d in candidates]
        )
        for d, s in zip(candidates, scores):
            d.rerank_score = round(float(s), 4)
            boost = self.PRIORITY_BOOST.get(
                d.metadata.get('source_priority', 'low'), 0.0
            )
            d.final_score = round(d.rerank_score + boost, 4)
        candidates.sort(key=lambda x: -x.final_score)
        return candidates[:top_n]

    # ── Public retrieve ───────────────────────────────────────
    def retrieve(
        self,
        query: str,
        k: int = 5,
        fetch_k: int = 20,
        use_reranker: bool = True,
        source_filter: Optional[str] = None,
    ) -> list[RetrievedDoc]:
        dense = self._dense_retrieve(query, fetch_k)
        sparse = self._sparse_retrieve(query, fetch_k)
        if source_filter:
            dense = [d for d in dense if d.source == source_filter]
            sparse = [d for d in sparse if d.source == source_filter]
        merged = self._rrf(dense, sparse)
        if use_reranker:
            return self._rerank(query, merged[:fetch_k], top_n=k)
        return merged[:k]


def load_reranker() -> CrossEncoder:
    """Load the cross-encoder re-ranker model."""
    print(f"Loading cross-encoder: {RERANKER_MODEL_NAME}")
    reranker = CrossEncoder(RERANKER_MODEL_NAME, max_length=512)
    print("✓ Cross-encoder loaded")
    return reranker
