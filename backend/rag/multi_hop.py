"""
Multi-hop retrieval — iterative query refinement with LLM.
Exact replica of Phase 3 Cell 10A.
"""
from __future__ import annotations

from retrievers.faiss_retriever import RetrievedDoc


def multi_hop_retrieve(
    query: str,
    retriever,
    reranker,
    llm,
    hops: int = 2,
    k_per_hop: int = 3,
) -> list[RetrievedDoc]:
    """
    Iterative retrieval with LLM-guided query refinement.
    Hop 1: retrieve on original query.
    Hop 2: LLM reads context, generates refined query, retrieve again.
    Final: dedup + rerank union of all hops.
    """
    current_query = query
    all_docs: dict[str, RetrievedDoc] = {}

    for hop in range(hops):
        docs = retriever.retrieve(
            current_query, k=k_per_hop, use_reranker=False
        )
        for d in docs:
            key = d.text[:100]
            if (key not in all_docs
                    or d.dense_score > all_docs[key].dense_score):
                all_docs[key] = d

        if hop == hops - 1:
            break  # no refinement after last hop

        # Refine query from retrieved context
        context_snippet = " ".join([d.text[:150] for d in docs])
        refinement_prompt = (
            f"You are refining a customer support search query.\n"
            f"Original query: {query}\n"
            f"Context found: {context_snippet[:400]}\n"
            f"Write ONE focused follow-up search query to find missing "
            f"information.\n"
            f"Output ONLY the query, nothing else."
        )
        try:
            refined = llm.invoke(refinement_prompt).content.strip()
            if refined and len(refined) < 200:
                current_query = refined
        except Exception:
            break  # use what we have

    # Final dedup + rerank
    candidates = list(all_docs.values())
    if len(candidates) > 1:
        scores = reranker.predict(
            [(query, d.text) for d in candidates]
        )
        for d, s in zip(candidates, scores):
            d.rerank_score = round(float(s), 4)
        candidates.sort(key=lambda x: -x.rerank_score)

    return candidates[:6]
