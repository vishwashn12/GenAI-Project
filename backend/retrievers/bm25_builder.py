"""
BM25 sparse index builder — exact replica of Phase 3 Cell 2 Part D.
"""
from __future__ import annotations

import re

from rank_bm25 import BM25Okapi


# Exact tokenizer from the notebook
_STOPWORDS = frozenset({
    'the', 'a', 'an', 'is', 'it', 'in', 'on', 'at', 'to', 'for',
    'of', 'and', 'or', 'but', 'not', 'this', 'that', 'with', 'was',
})


def tokenize_for_bm25(text: str) -> list[str]:
    """Tokenize text for BM25 — exact copy from notebook."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return [t for t in text.split()
            if t not in _STOPWORDS and len(t) > 1]


def build_bm25_index(chunked_docs: list[dict]) -> BM25Okapi:
    """Build a BM25Okapi index from the full chunk corpus."""
    print("Building BM25 index...")
    corpus_tokens = [tokenize_for_bm25(c['text']) for c in chunked_docs]
    bm25_index = BM25Okapi(corpus_tokens)
    print(f"✓ BM25 index built: {len(corpus_tokens):,} documents")
    return bm25_index
