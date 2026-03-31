"""
Multi-query retrieval — generates 3 search sub-queries, deduplicates, re-ranks.
Exact replica of Phase 3 Cell 10.
"""
from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from retrievers.faiss_retriever import RetrievedDoc


MULTI_QUERY_PROMPT = PromptTemplate(
    input_variables=['question'],
    template='''Generate 3 different search queries to retrieve documents
that would help answer this customer support question.
Use different phrasings and synonyms. Output ONLY the 3 queries,
one per line, no numbering, no explanation.
Question: {question}
Queries:'''
)


def build_multi_query_chain(llm):
    """Build the multi-query generation chain."""
    return MULTI_QUERY_PROMPT | llm | StrOutputParser()


def multi_query_retrieve(
    question: str,
    retriever,
    reranker,
    multi_query_chain,
    k_per_query: int = 4,
    final_k: int = 6,
) -> list[RetrievedDoc]:
    """Generate 3 sub-queries, retrieve for each, deduplicate, re-rank."""
    raw = multi_query_chain.invoke({'question': question})
    sub_queries = [q.strip() for q in raw.strip().split('\n') if q.strip()][:3]
    sub_queries.append(question)

    all_docs: dict[str, RetrievedDoc] = {}
    for sq in sub_queries:
        docs = retriever.retrieve(sq, k=k_per_query, use_reranker=False)
        for doc in docs:
            key = doc.text[:100]
            if (key not in all_docs
                    or doc.dense_score > all_docs[key].dense_score):
                all_docs[key] = doc

    candidates = list(all_docs.values())
    if len(candidates) > 1:
        scores = reranker.predict(
            [(question, d.text) for d in candidates]
        )
        for d, s in zip(candidates, scores):
            d.rerank_score = round(float(s), 4)
        candidates.sort(key=lambda x: -x.rerank_score)

    return candidates[:final_k]
