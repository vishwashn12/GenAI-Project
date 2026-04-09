# 📁 Project Structure — GenAI E-Commerce Customer Support

> Use this file to verify your local clone is complete.  
> Files marked with ⚠️ are **not tracked in Git** and must be created/generated locally.

---

## Root Directory

```
GenAI/
│
├── .gitignore
├── embeddings-vector-db.ipynb          # Jupyter notebook (Phase 2 — embedding & FAISS build)
├── RAG_EVALUATION_ANALYSIS.md          # Evaluation summary document
├── SYSTEM_ARCHITECTURE.md              # System architecture overview
├── PROJECT_STRUCTURE.md                # ← This file
│
├── backend/                            # FastAPI backend (Python)
├── frontend/                           # React + Vite frontend
├── embeddings/                         # Raw embedding artifacts (intermediate, not used at runtime)
├── faiss_indexes/                      # ⚠️ FAISS vector indexes (REQUIRED at runtime)
├── processed_dataset/                  # ⚠️ Parquet & JSON data files (REQUIRED at runtime)
└── phase docs/                         # Phase documentation (Word docs)
```

---

## `backend/` — FastAPI Server

```
backend/
│
├── .env                                # ⚠️ NOT in Git — must create manually (see .env.example)
├── .env.example                        # Template for environment variables
├── main.py                             # FastAPI app entry point + lifespan loader
├── config.py                           # Central configuration (paths, API keys, constants)
├── requirements.txt                    # Python dependencies
│
├── agent/                              # LangGraph Agent (multi-tool orchestration)
│   ├── __init__.py
│   ├── graph.py                        # LangGraph compilation (nodes → edges → app)
│   ├── nodes.py                        # Agent node logic (system prompt, tool routing)
│   ├── state.py                        # AgentState schema (messages, order_id, tool_call_count)
│   └── tools.py                        # Tool definitions (order_lookup, seller_analysis, rag_search, escalate)
│
├── core/                               # Core RAG orchestrator
│   ├── __init__.py
│   └── rag_system.py                   # OlistRAGSystem — routes queries to Agent or RAG chain
│
├── embeddings/                         # Embedding model loader
│   ├── __init__.py
│   └── embed_model.py                  # Loads sentence-transformers model (all-MiniLM-L6-v2)
│
├── evaluation/                         # Test suites & evaluation scripts
│   ├── __init__.py
│   ├── analyze_ar.py                   # Automated result analyzer
│   ├── run_ragas_eval.py               # RAGAS evaluation runner
│   ├── test_dataset.py                 # Dataset-level test cases
│   ├── test_intent.py                  # Intent classification tests
│   ├── test_live_api.py                # Live API integration tests
│   └── results/                        # Evaluation output files
│       ├── eval_progress.json
│       └── ragas_report_*.md
│
├── feedback/                           # Feedback collection
│   ├── __init__.py
│   └── store.py                        # In-memory FeedbackStore (thumbs up/down)
│
├── memory/                             # Conversation memory
│   ├── __init__.py
│   └── conversation.py                 # Sliding-window conversation history manager
│
├── models/                             # Data models (placeholder)
│   └── __init__.py
│
├── preprocessing/                      # Data preprocessing (placeholder)
│   └── __init__.py
│
├── rag/                                # RAG pipeline components
│   ├── __init__.py
│   ├── compressor.py                   # Context compression chain
│   ├── context.py                      # format_context() — prepares retrieved docs for LLM
│   ├── intent.py                       # Rule-based intent classifier (QueryIntent enum)
│   ├── multi_hop.py                    # Multi-hop retrieval (iterative refinement)
│   ├── multi_query.py                  # Multi-query retrieval (parallel query expansion)
│   ├── prompts.py                      # Prompt templates per intent (PROMPT_REGISTRY)
│   └── rewriter.py                     # Query rewriting chain
│
├── retrievers/                         # Retrieval engines
│   ├── __init__.py
│   ├── bm25_builder.py                 # BM25Okapi sparse index builder
│   ├── faiss_retriever.py              # FAISS dense retriever (loads .index files)
│   └── hybrid_retriever.py             # HybridRetriever (FAISS + BM25 + RRF + CrossEncoder)
│
├── routes/                             # FastAPI route handlers
│   ├── __init__.py
│   ├── analytics.py                    # GET /analytics
│   ├── chat.py                         # POST /chat
│   ├── feedback.py                     # POST /feedback
│   └── insights.py                     # GET /insights
│
├── services/                           # Business logic services
│   ├── __init__.py
│   ├── data_service.py                 # Parquet/CSV data loader utility
│   ├── operations_service.py           # Analytics payload builder (issue distribution, SLA, sentiment)
│   ├── rag_client.py                   # Bridges /chat route → OlistRAGSystem.answer()
│   └── seller_service.py              # Seller insights payload builder
│
└── .venv/                              # ⚠️ Python virtual environment (NOT in Git)
```

---

## `frontend/` — React + Vite + Tailwind CSS

```
frontend/
│
├── index.html                          # HTML entry point
├── package.json                        # Node dependencies & scripts
├── package-lock.json                   # Lockfile
├── vite.config.js                      # Vite configuration
├── tailwind.config.js                  # Tailwind CSS configuration (custom design tokens)
├── postcss.config.js                   # PostCSS config
│
├── src/
│   ├── main.jsx                        # React entry point (BrowserRouter + ThemeProvider)
│   ├── App.jsx                         # Root component (Sidebar + Routes)
│   ├── styles.css                      # Global CSS (Tailwind directives + custom utilities)
│   │
│   ├── components/                     # Reusable UI components
│   │   ├── ChatBubble.jsx              # Chat message bubble (user/assistant, metadata badges)
│   │   ├── Loader.jsx                  # Loading spinner / skeleton
│   │   ├── MetricCard.jsx              # Dashboard metric card with icon & trend
│   │   ├── Sidebar.jsx                 # Navigation sidebar (Chat, Operations, Sellers, Settings)
│   │   └── SourceCard.jsx              # Source citation card (similarity score, snippet)
│   │
│   ├── lib/                            # Utilities & context
│   │   ├── api.js                      # Axios API client (chatWithSupport, fetchAnalytics, etc.)
│   │   └── ThemeContext.jsx            # Dark/Light theme context provider
│   │
│   └── pages/                          # Page-level components
│       ├── Chat.jsx                    # Main chat interface
│       ├── Operations.jsx              # Operations analytics dashboard
│       ├── Sellers.jsx                 # Seller performance insights
│       └── Settings.jsx               # RAG pipeline toggle settings + theme switch
│
└── node_modules/                       # ⚠️ Node dependencies (NOT in Git — run `npm install`)
```

---

## `faiss_indexes/` — Vector Databases (⚠️ REQUIRED)

> These files are generated by `embeddings-vector-db.ipynb` (Phase 2).  
> They are large binary files and may be tracked via Git LFS or need manual generation.

```
faiss_indexes/
├── main.index                          # ~192 MB — 130,913 vectors (Olist + general support)
├── complaints.index                    # ~166 MB — 113,268 vectors (Amazon complaints)
├── policy.index                        # ~17 KB  — 11 vectors (store policies + CDC rules)
├── chunks_main.json                    # ~83 MB  — Text chunks for main index
├── chunks_complaints.json              # ~74 MB  — Text chunks for complaints index
└── chunks_policy.json                  # ~7 KB   — Text chunks for policy index
```

---

## `processed_dataset/` — Tabular & Document Data (⚠️ REQUIRED)

> These files are generated by `embeddings-vector-db.ipynb` (Phase 1 preprocessing).

```
processed_dataset/
├── order_lookup.parquet                # ~6 MB   — 99,441 orders (used by order_lookup tool)
├── seller_kpi.parquet                  # ~157 KB — 3,095 sellers (used by seller_analysis tool)
├── amazon_complaints.parquet           # ~50 MB  — Amazon complaint reviews
├── master_df.parquet                   # ~16 MB  — Master merged dataframe
├── synthetic_tickets.parquet           # ~1 MB   — Synthetic support tickets (analytics)
├── synthetic_tickets.csv               # ~3.4 MB — CSV version of above
├── policy_doc.txt                      # ~4 KB   — Plain text policy document
├── olist_rag_docs.json                 # ~26 MB  — Olist RAG document chunks
├── amazon_rag_docs.json                # ~31 MB  — Amazon RAG document chunks
├── ticket_rag_docs.json                # ~6 MB   — Ticket RAG document chunks
└── unified_rag_corpus.json             # ~58 MB  — Combined RAG corpus
```

---

## `embeddings/` — Raw Embedding Artifacts (NOT used at runtime)

> Intermediate output from Phase 2. Kept for reproducibility only.

```
embeddings/
├── vectors.npy                         # ~192 MB — Raw numpy float32 vectors
├── chunks_full.json                    # ~83 MB  — Full chunk text before splitting
└── chunk_meta.json                     # ~19 MB  — Chunk metadata
```

---

## `phase docs/` — Development Documentation

```
phase docs/
├── Phase1_Dataset_Preprocessing_Guide_Complete.docx
├── Phase2_FAISS_Complete_Working_Notebook.docx
└── Phase3_Complete_FAISS_All_Improvements.docx
```

---

## Setup Checklist

After cloning, verify the following:

| Step | Action | Command |
|------|--------|---------|
| 1 | Clone the repo | `git clone https://github.com/vishwashn12/GenAI-Project.git` |
| 2 | Create backend virtual env | `cd backend && python -m venv .venv` |
| 3 | Activate venv | `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac) |
| 4 | Install Python deps | `pip install -r requirements.txt` |
| 5 | Create `.env` file | Copy `.env.example` → `.env`, add your `GROQ_API_KEY` |
| 6 | Verify FAISS indexes exist | Check `faiss_indexes/` has 6 files (3 `.index` + 3 `.json`) |
| 7 | Verify processed dataset exists | Check `processed_dataset/` has 11 files |
| 8 | Start backend | `python -m uvicorn main:app --host 0.0.0.0 --port 8000` |
| 9 | Install frontend deps | `cd frontend && npm install` |
| 10 | Start frontend | `npm run dev` |

> ⚠️ **If `faiss_indexes/` or `processed_dataset/` are missing**, you must run the `embeddings-vector-db.ipynb` notebook first to generate them from the raw data.
