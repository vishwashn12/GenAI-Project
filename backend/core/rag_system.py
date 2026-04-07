"""
OlistRAGSystem — Production RAG + Agent orchestrator.
Exact replica of Phase 3 Cell 18 with memory + feedback loop.
"""
from __future__ import annotations

import re
import time
from typing import Optional

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser

from rag.intent import QueryIntent, classify_intent, classify_intent_llm
from rag.prompts import PROMPT_REGISTRY
from rag.context import format_context
from rag.rewriter import rewrite_query
from rag.multi_query import multi_query_retrieve
from rag.multi_hop import multi_hop_retrieve
from rag.compressor import compress_context
from memory.conversation import memory_store


# ── P0 FIX: Tightened patterns — old list was too broad and caused
# the feedback loop to fire on 37.5% of queries, doubling latency.
# These now only match genuine "I cannot answer" responses.
LOW_CONFIDENCE = [
    "i don't have enough information in my records to answer",
    "no relevant documents found",
    "i cannot find any relevant information",
]

# ── P0 FIX: Prompt injection patterns
INJECTION_PATTERNS = re.compile(
    r'(?:ignore|forget|disregard)\s+(?:all\s+)?(?:previous|prior|above|system)'
    r'|(?:pretend|act)\s+(?:you\s+are|to\s+be)'
    r'|(?:new\s+instructions?|override\s+instructions?)'
    r'|(?:you\s+are\s+now|switch\s+to)\s+(?:a\s+)?(?:new|different)',
    re.IGNORECASE,
)


class OlistRAGSystem:
    """
    Production RAG + Agent system.
    Fast path: rewrite → retrieve → compress → generate
    Slow path: LangGraph agent with tools
    Memory: conversation memory + feedback loop retry
    """

    # Intents that BENEFIT from structured data lookup (order_lookup / seller_analysis tools)
    AGENT_TRIGGERS = {'order_status', 'delivery_issue', 'seller_issue', 'refund_request'}

    def __init__(
        self,
        retriever,
        reranker,
        llm,
        agent_app,
        rewrite_chain,
        multi_query_chain,
        compress_chain,
        use_rewrite: bool = True,
        use_multiquery: bool = False,
        use_compress: bool = False,
        use_multihop: bool = False,
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.llm = llm
        self.agent = agent_app
        self.rewrite_chain = rewrite_chain
        self.multi_query_chain = multi_query_chain
        self.compress_chain = compress_chain
        self.use_rewrite = use_rewrite
        self.use_mq = use_multiquery
        self.use_comp = use_compress
        self.use_mh = use_multihop

    def _should_use_agent(self, query: str, order_id: str = '', intent: QueryIntent | None = None) -> bool:
        """
        Use the agent ONLY when we have structured data to look up.
        - No ID → RAG always wins (agent has nothing to query)
        - ID + transactional intent → agent (can call order_lookup / seller_analysis)
        - ID + policy/general intent → RAG (policy questions don't need DB lookup)
        """
        if not order_id:
            return False
        resolved_intent = intent or classify_intent(query)
        return resolved_intent.value in self.AGENT_TRIGGERS

    def _rag_chain_answer(
        self,
        query: str,
        order_id: str = '',
        session_id: str = 'default',
        use_rewrite: bool | None = None,
        use_mq: bool | None = None,
        use_comp: bool | None = None,
        pre_intent: QueryIntent | None = None,  # pass in from answer() to avoid double classification
    ) -> dict:
        t0 = time.time()
        
        # Merge request settings with defaults
        active_rewrite = self.use_rewrite if use_rewrite is None else use_rewrite
        active_mq = self.use_mq if use_mq is None else use_mq
        active_comp = self.use_comp if use_comp is None else use_comp

        original_query = query  # keep original before expansion

        # ── Step 1: Build history-enriched search query ───────────────
        # retrieval history: compact (user turns only) — lighter on tokens
        retrieval_history  = memory_store.get_history(session_id, for_retrieval=True)
        # generation history: full turns — LLM needs both sides to understand references
        generation_history = memory_store.get_history(session_id, for_retrieval=False)

        search_query = (
            f"Previous context:\n{retrieval_history}\n\nCurrent question: {query}"
            if retrieval_history else query
        )


        # ── Step 2: Query rewriting ───────────────────────────
        if active_rewrite:
            search_query = rewrite_query(search_query, self.rewrite_chain)

        # ── Step 3: Retrieval ─────────────────────────────────
        if self.use_mh:
            docs = multi_hop_retrieve(
                search_query, self.retriever, self.reranker, self.llm
            )
        elif active_mq:
            docs = multi_query_retrieve(
                search_query, self.retriever, self.reranker,
                self.multi_query_chain,
            )
        else:
            docs = self.retriever.retrieve(search_query, k=5)

        # ── Step 4: Optional compression ─────────────────────
        if active_comp:
            if classify_intent(query) == QueryIntent.POLICY_QUERY:
                docs = compress_context(
                    query, docs, self.compress_chain
                )

        # ── Step 5: Format context ────────────────────────────
        context = format_context(docs, max_chars=2000)

        # ── Step 6: Generate answer ───────────────────────────
        # Reuse pre-classified intent if available (avoids a second LLM call)
        intent = pre_intent or classify_intent_llm(query, self.llm)
        prompt = PROMPT_REGISTRY[intent]
        chain = prompt | self.llm | StrOutputParser()
        kwargs = {
            'context': context,
            'question': query,
            'history': generation_history or 'No prior conversation.',
        }
        if 'order_id' in prompt.input_variables:
            kwargs['order_id'] = order_id or 'not provided'
        if 'days_since_purchase' in prompt.input_variables:
            kwargs['days_since_purchase'] = 'unknown'
        answer = chain.invoke(kwargs)

        # ── Step 7: Feedback loop ─────────────────────────────
        if any(p in answer.lower() for p in LOW_CONFIDENCE):
            retry_docs = multi_query_retrieve(
                original_query, self.retriever, self.reranker,
                self.multi_query_chain,
            )
            kwargs['context'] = format_context(
                retry_docs, max_chars=2000
            )
            answer = chain.invoke(kwargs)
            docs = retry_docs

        # ── Step 8: Save to memory ────────────────────────────
        memory_store.add_turn(session_id, original_query, answer)

        latency_s = round(time.time() - t0, 3)

        # Build similarity scores list
        similarity_scores = []
        for d in docs:
            if hasattr(d, 'rerank_score') and d.rerank_score != 0.0:
                # Normalize rerank score to 0-1 range for frontend display
                # CrossEncoder scores are typically in [-10, 10] range
                norm_score = max(0.0, min(1.0, (d.rerank_score + 10) / 20))
                similarity_scores.append(round(norm_score, 4))
            elif hasattr(d, 'dense_score'):
                similarity_scores.append(d.dense_score)
            else:
                similarity_scores.append(0.0)

        # Build source details for frontend
        sources = []
        for d in docs:
            src = d.source if hasattr(d, 'source') else d.get('source', '')
            text = d.text if hasattr(d, 'text') else d.get('text', '')
            score = (d.rerank_score if hasattr(d, 'rerank_score')
                     else d.dense_score if hasattr(d, 'dense_score')
                     else 0.0)
            # Normalize for display
            norm_score = max(0.0, min(1.0, (score + 10) / 20)) if score < 0 or score > 1 else score
            sources.append({
                'source_type': src,
                'type': src,
                'text': text[:300],
                'snippet': text[:300],
                'similarity': round(norm_score, 4),
                'score': round(norm_score, 4),
            })

        return {
            'answer': answer,
            'sources': sources,
            'intent': intent.value,
            'mode': 'rag_chain',
            'session_id': session_id,
            'latency': latency_s,
            'latency_ms': round(latency_s * 1000, 1),
            'documents_retrieved': len(docs),
            'docs_used': len(docs),
            'similarity_scores': similarity_scores,
            'reasoning': {
                'intent_classification': intent.value,
                'tool_calls': [],
                'retrieval_summary': (
                    f"Retrieved {len(docs)} documents via "
                    f"{'multi-hop' if self.use_mh else 'multi-query' if self.use_mq else 'hybrid'} "
                    f"retrieval (FAISS + BM25 + RRF + CrossEncoder)"
                ),
            },
        }

    def _agent_answer(
        self,
        query: str,
        session_id: str = 'default',
        order_id: str = '',
    ) -> dict:
        t0 = time.time()
        history = memory_store.get_history(session_id)
        full_q = (f"Context:\n{history}\n\nQuery: {query}"
                  if history else query)

        # Inject the ID from the UI directly into the LLM's query
        if order_id:
            full_q += f"\n[The user has explicitly provided an ID (Order or Seller): {order_id}]"

        result = self.agent.invoke({
            'messages': [HumanMessage(content=full_q)],
            'order_id': order_id,
            'intent': '',
            'tool_call_count': 0,
            'escalated': False,
            'final_answer': '',
        })

        last_msg = result['messages'][-1]
        answer = getattr(last_msg, 'content', str(last_msg))
        memory_store.add_turn(session_id, query, answer)

        latency_s = round(time.time() - t0, 3)
        intent_val = result.get('intent', classify_intent(query).value)

        # Extract tool call names from messages
        tool_calls_made = []
        for msg in result.get('messages', []):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls_made.append(tc.get('name', 'unknown'))

        return {
            'answer': answer,
            'intent': intent_val,
            'mode': 'agent',
            'session_id': session_id,
            'latency': latency_s,
            'latency_ms': round(latency_s * 1000, 1),
            'documents_retrieved': 0,
            'docs_used': 0,
            'tool_calls': result.get('tool_call_count', 0),
            'escalated': result.get('escalated', False),
            'sources': [],
            'similarity_scores': [],
            'reasoning': {
                'intent_classification': intent_val,
                'tool_calls': tool_calls_made,
                'retrieval_summary': (
                    f"Agent mode: {len(tool_calls_made)} tool calls executed"
                ),
            },
        }

    @staticmethod
    def _sanitize_query(query: str) -> str:
        """P0 FIX: Strip prompt injection attempts."""
        cleaned = INJECTION_PATTERNS.sub('', query).strip()
        return cleaned if len(cleaned) >= 2 else query

    @staticmethod
    def _is_low_quality(query: str) -> bool:
        """P1 FIX: Reject queries that are too short or meaningless."""
        stripped = query.strip()
        words = stripped.split()
        if len(stripped) < 3 or len(words) < 1:
            return True
        # Detect token spam (same word repeated 10+ times)
        if len(words) >= 10 and len(set(words)) == 1:
            return True
        return False

    def answer(
        self,
        query: str,
        order_id: str = '',
        session_id: str = 'default',
        use_rewrite: bool | None = None,
        use_mq: bool | None = None,
        use_comp: bool | None = None,
    ) -> dict:
        """Main entry point — routes to agent or RAG chain."""
        try:
            # P1 FIX: Reject trivially empty/spam queries
            if self._is_low_quality(query):
                return {
                    'answer': (
                        'I\'d be happy to help! Could you please provide '
                        'more details about your question? For example, '
                        'you can ask about order status, return policies, '
                        'refund eligibility, or product issues.'
                    ),
                    'intent': 'general',
                    'mode': 'fallback',
                    'latency': 0.0,
                    'sources': [],
                    'documents_retrieved': 0,
                    'similarity_scores': [],
                    'reasoning': {
                        'intent_classification': 'general',
                        'tool_calls': [],
                        'retrieval_summary': 'Query too short or unclear for retrieval.',
                    },
                }

            # P0 FIX: Sanitize prompt injection
            safe_query = self._sanitize_query(query)

            # Classify intent ONCE with LLM — reused for both routing and generation
            intent = classify_intent_llm(safe_query, self.llm)

            if self._should_use_agent(safe_query, order_id, intent):
                return self._agent_answer(safe_query, session_id, order_id)
            return self._rag_chain_answer(
                safe_query, order_id, session_id,
                use_rewrite, use_mq, use_comp,
                pre_intent=intent,  # pass through — no double classification
            )
        except Exception as exc:
            # Graceful fallback — never crash the API
            return {
                'answer': (
                    'I apologize, but I encountered an issue processing '
                    'your request. Please try again or rephrase your '
                    f'question. Error: {str(exc)[:200]}'
                ),
                'intent': classify_intent(query).value,
                'mode': 'error',
                'latency': 0.0,
                'sources': [],
                'documents_retrieved': 0,
                'similarity_scores': [],
                'reasoning': {
                    'intent_classification': classify_intent(query).value,
                    'tool_calls': [],
                    'retrieval_summary': f'Error: {str(exc)[:200]}',
                },
            }
