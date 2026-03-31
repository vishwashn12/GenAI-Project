"""
LLM-based context compression — removes irrelevant sentences.
Exact replica of Phase 3 Cell 11.
"""
from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from retrievers.faiss_retriever import RetrievedDoc


COMPRESS_PROMPT = PromptTemplate(
    input_variables=['question', 'document'],
    template='''Given the customer support question below,
extract ONLY the sentences from the document that are directly relevant to answering it.
If no sentences are relevant, respond with: NO_RELEVANT_CONTENT
Do not add any new information or commentary.

Question: {question}
Document: {document}
Relevant extract:'''
)


def build_compress_chain(llm):
    """Build the compression chain with the given LLM."""
    return COMPRESS_PROMPT | llm | StrOutputParser()


def compress_context(
    query: str,
    docs: list[RetrievedDoc],
    compress_chain,
    min_score: float = 0.3,
) -> list[RetrievedDoc]:
    """
    Compress each retrieved doc to only relevant sentences.
    Drops docs where nothing is relevant.
    Trade-off: adds 1 LLM call per doc — use only when accuracy > speed.
    """
    compressed: list[RetrievedDoc] = []
    for doc in docs:
        if doc.rerank_score < min_score:
            continue  # skip low-confidence docs
        try:
            extract = compress_chain.invoke({
                'question': query,
                'document': doc.text,
            })
            if ('NO_RELEVANT_CONTENT' not in extract
                    and len(extract.strip()) > 20):
                doc.text = extract.strip()
                compressed.append(doc)
        except Exception:
            compressed.append(doc)  # keep original on error
    return compressed
