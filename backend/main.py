"""
FastAPI application with lifespan startup loading all models and indexes.
"""
from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the backend directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.analytics import router as analytics_router
from routes.chat import router as chat_router
from routes.feedback import router as feedback_router
from routes.insights import router as insights_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all heavy models and indexes once at startup."""
    from dotenv import load_dotenv
    load_dotenv()  # load .env file

    # Set GROQ_API_KEY from env
    from config import GROQ_API_KEY
    if not os.environ.get("GROQ_API_KEY"):
        print("⚠ WARNING: GROQ_API_KEY not set. LLM calls will fail.")
        print("  Set it in .env or as environment variable.")

    print("=" * 60)
    print("  LOADING RAG SYSTEM — this may take 30-60 seconds...")
    print("=" * 60)

    # 1. Load embedding model
    from embeddings.embed_model import get_embed_model
    embed_model = get_embed_model()

    # 2. Load FAISS indexes and build FAISSRetriever
    from retrievers.faiss_retriever import build_faiss_retriever
    faiss_retriever, chunked_docs = build_faiss_retriever(embed_model)

    # 3. Build BM25 index
    from retrievers.bm25_builder import build_bm25_index
    bm25_index = build_bm25_index(chunked_docs)

    # 4. Load cross-encoder re-ranker
    from retrievers.hybrid_retriever import load_reranker, HybridRetriever
    reranker = load_reranker()

    # 5. Build HybridRetriever
    hybrid_retriever = HybridRetriever(
        faiss_retriever=faiss_retriever,
        bm25_index=bm25_index,
        chunked_docs=chunked_docs,
        reranker=reranker,
    )
    print("✓ HybridRetriever ready (FAISS + BM25 + RRF + CrossEncoder)")

    # 6. Setup LLM (Groq)
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        max_tokens=600,
    )
    print("✓ LLM configured (Groq llama-3.1-8b-instant)")

    # 7. Build LangChain chains
    from rag.rewriter import build_rewrite_chain
    from rag.multi_query import build_multi_query_chain
    from rag.compressor import build_compress_chain

    rewrite_chain = build_rewrite_chain(llm)
    multi_query_chain = build_multi_query_chain(llm)
    compress_chain = build_compress_chain(llm)

    # 8. Inject rag_search function into agent tools
    from agent.tools import set_rag_search_fn, TOOLS
    from rag.context import format_context

    def _rag_search_impl(query: str) -> str:
        docs = hybrid_retriever.retrieve(query, k=4)
        return format_context(docs, max_chars=1200)

    set_rag_search_fn(_rag_search_impl)

    # 9. Compile LangGraph agent
    from agent.graph import compile_agent
    llm_with_tools = llm.bind_tools(TOOLS)
    agent_app = compile_agent(llm_with_tools)

    # 10. Build OlistRAGSystem
    from core.rag_system import OlistRAGSystem
    rag_system = OlistRAGSystem(
        retriever=hybrid_retriever,
        reranker=reranker,
        llm=llm,
        agent_app=agent_app,
        rewrite_chain=rewrite_chain,
        multi_query_chain=multi_query_chain,
        compress_chain=compress_chain,
        use_rewrite=True,
        use_multiquery=False,
        use_compress=False,
        use_multihop=False,
    )
    print("✓ OlistRAGSystem ready")

    # Store on app.state for access in routes
    app.state.rag_system = rag_system

    print("=" * 60)
    print("  ✓ ALL SYSTEMS LOADED — SERVER READY")
    print("=" * 60)

    yield  # Server runs here

    # Shutdown
    print("Shutting down RAG system...")


app = FastAPI(
    title="AI E-commerce Customer Support API",
    version="2.0.0",
    description=(
        "Production-grade RAG API with FAISS vector retrieval, "
        "BM25 hybrid search, cross-encoder re-ranking, "
        "LangGraph agent, and conversation memory."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(insights_router)
app.include_router(feedback_router)


@app.get("/health")
def health_check() -> dict:
    has_rag = hasattr(app.state, 'rag_system') and app.state.rag_system is not None
    return {
        "status": "ok",
        "rag_system_loaded": has_rag,
        "version": "2.0.0",
    }
