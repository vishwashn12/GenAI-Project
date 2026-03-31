"""
Query rewriter — expands abbreviated / vague customer queries.
Exact replica of Phase 3 Cell 9.
"""
from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


REWRITE_PROMPT = PromptTemplate(
    input_variables=['query'],
    template='''You are a query rewriting assistant for an e-commerce support system.
Your task: rewrite the customer query to be more specific and retrieval-friendly.

Rules:
- Expand abbreviations (e.g. 'ord' → 'order')
- Add relevant context terms (e.g. 'broken' → 'broken defective product quality')
- Keep it concise (max 2 sentences)
- Preserve the original intent completely
- Do NOT answer the question — only rewrite it

Original query: {query}
Rewritten query:'''
)


def build_rewrite_chain(llm):
    """Build the rewrite chain with the given LLM."""
    return REWRITE_PROMPT | llm | StrOutputParser()


def rewrite_query(query: str, rewrite_chain) -> str:
    """Rewrite query for better retrieval. Falls back to original on error."""
    try:
        rewritten = rewrite_chain.invoke({'query': query})
        return rewritten.strip()
    except Exception:
        return query  # graceful fallback
