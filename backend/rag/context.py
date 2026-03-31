"""
format_context — Fixed typing import + safe attribute access.
Exact replica of Phase 3 Cell 7.
Handles both RetrievedDoc objects and plain dicts.
"""
from __future__ import annotations

from typing import List, Union


SOURCE_LABELS = {
    'policy': 'PLATFORM POLICY',
    'olist_review': 'CUSTOMER REVIEW',
    'support_ticket': 'SUPPORT RECORD',
    'amazon_complaint': 'PRODUCT FEEDBACK',
    'seller_kpi': 'SELLER DATA',
}


def format_context(
    docs: list,
    max_chars: int = 2000,
    add_scores: bool = False,
) -> str:
    """
    Formats retrieved documents into a numbered context block.
    Works with both RetrievedDoc objects and plain dicts.
    """
    sections: list[str] = []
    total = 0

    for i, doc in enumerate(docs, 1):
        # Safe attribute access — works for RetrievedDoc and dict
        if hasattr(doc, 'text'):
            text = doc.text
            source = doc.source
            score = getattr(doc, 'rerank_score',
                            getattr(doc, 'dense_score', 0.0))
        else:
            text = doc.get('text', '')
            source = doc.get('source', '')
            score = doc.get('similarity',
                            doc.get('rerank_score', 0.0))

        label = SOURCE_LABELS.get(
            source, source.upper().replace('_', ' ')
        )
        score_str = f' [relevance: {score:.2f}]' if add_scores else ''
        header = f'[Source {i} — {label}]{score_str}'
        body = text.strip()
        remaining = max_chars - total - len(header) - 4
        if remaining <= 50:
            break
        if len(body) > remaining:
            body = body[:remaining] + '...'
        section = f'{header}\n{body}'
        sections.append(section)
        total += len(section)

    return '\n\n'.join(sections)
