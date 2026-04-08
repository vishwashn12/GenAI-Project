# Intelligent E-Commerce Support System: Architecture and Technical Implementation

## 1. Executive Summary

This document details the architectural design and technical implementation of an advanced, production-grade Customer Support Retrieval-Augmented Generation (RAG) system tailored for the "Olist" Brazilian E-commerce dataset. Traditional RAG systems strictly parse unstructured documents (like PDFs), while traditional SQL Agents parse strictly tabular data. In an e-commerce context, a customer query dynamically requires both (e.g., retrieving an order's status from a table *and* checking the return policy from a PDF). 

To solve this, we implemented a **Dynamic Agentic RAG Architecture**: a deterministic routing matrix that combines a high-speed Hybrid Semantic Search engine for unstructured policies, and a Langchain ReAct (Reason + Act) Agent bounded by Pandas data integrations for dynamic tabular intelligence.

---

## 2. Infrastructure & Technology Stack

The pipeline is split into a layered distributed microservice architecture:

### 2.1 Backend Core
* **Framework:** Python 3.11 with `FastAPI` (Asynchronous HTTP routing, strictly typed Pydantic models).
* **LLM Engine:** Groq Cloud API, leveraging LPU (Language Processing Unit) acceleration for near-instant inference.
  * *Routing / Synthesis:* `llama3-70b-8192` (Used for rigorous reasoning, anaphora resolution, and complex agentic planning).
  * *Evaluator:* `mixtral-8x7b-32768` (Used exclusively within the Ragas evaluation module).
* **Embeddings & Re-ranking:**
  * *Dense Vectorizer:* HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional semantic space, local CPU inference for 0 latency).
  * *Cross-Encoder:* `cross-encoder/ms-marco-MiniLM-L-6-v2` (Used for precise contextual scoring post-retrieval).
* **Vector Database:** FAISS (Facebook AI Similarity Search) utilized with flat L2 indexing, partitioned into three namespaces (`main`, `policy`, `complaints`).
* **Tabular Datastore:** `.parquet` format (Optimized columnar storage, allowing Pandas to natively scan orders without a running PSQL server).

### 2.2 Frontend Client
* **Framework:** React 18 with Vite.
* **Component Library:** TailwindCSS configured with a highly responsive, modern Dark Mode aesthetic.
* **State Management:** React Hooks maintaining volatile conversation state across the browser session.

---

## 3. Data Ingestion & Pre-processing

The Olist dataset consists of millions of relational rows (sellers, orders, items, products, reviews) and extensive textual data.

1. **Tabular Denormalization:** 
   The initial raw `.csv` files were heavily joined and cleaned using Pandas. We pre-merged `orders.csv` with `order_items.csv` and `products.csv` into a massive `olist_orders_merged.parquet`. This guarantees that when the Agent requests tracking data, the item metadata and shipping estimates are available in a single constant-time read.
2. **Unstructured Chunking:**
   Support PDFs and textual complaints were parsed and chunked using Langchain's Text Splitters, generating overlapping chunks of 500-1000 characters to preserve paragraph context while ensuring isolated semantic meaning.
3. **Hybrid Index Generation:** 
   The chunks were embedded using `all-MiniLM-L6-v2`. Alongside the FAISS dense vectors, we maintain a sparse map equivalent (BM25 token mapping) to enable Hybrid Search logic, mathematically mitigating the "Lost in the Middle" RAG phenomenon.

---

## 4. The Core Pipeline: Request to Response

The execution lifecycle of a single user chat message follows a strict multi-stage deterministic tree.

### Stage 1: Query Enhancement & Anaphora Resolution
When a payload hits `POST /chat`, it includes the user's latest query and a short conversational memory array. 
The system invokes the LLM dynamically to rewrite the query. 
* *Example:* If Memory = ["My order is late", "What is your order ID?", "12345"] and the User Query = *"Where is it?"*, the LLM contextually rewrites the query to *"Where is order 12345?"*. This ensures semantic retrievers do not fail on pronouns.

### Stage 2: Intent Classification
The rewritten standalone query is passed to an LLM evaluator prompt configured as a Zero-Shot Classifier. The LLM strictly classifies the query into one of 7 mutually exclusive intents:
1. `general`
2. `order_status`
3. `delivery_issue`
4. `refund_request`
5. `product_issue`
6. `seller_issue`
7. `policy_query`

This ensures that the routing engine operates on structured enum logic rather than fuzzy heuristics.

### Stage 3: The Routing Engine
A static rule-based router assesses the classification combined with Regex pattern matching for 32-character hexadecimal alphanumeric strings (Olist Order/Seller IDs).

#### Route A: Hybrid Retrieval / Unstructured (FAISS RAG)
**Trigger:** If the intent is non-transactional (`policy_query`, `general`) OR the user intends a transaction but forgot to provide an ID.
1. **Dense Retrieval:** The system embeds the query and pulls the Top $K=5$ closest vectors locally via FAISS L2 indexing.
2. **Sparse Retrieval:** The system retrieves the Top $K=5$ token-matched vectors.
3. **Cross-Encoder Re-Ranking:** The 10 combined chunks are run through the `ms-marco` cross-encoder. The cross-encoder yields a probability logit score from 0-1 on how closely the passage conceptually answers the query. The chunks are sorted and filtered by a hard threshold (`MIN_SCORE = 0.25`).
4. **Context Injection:** The winning chunks are stuffed into a massive strict prompt dictating support tone.
5. **Generation:** The LLM generates the answer directly derived from policy text.

#### Route B: Multi-Hop Tabular Agent (ReAct)
**Trigger:** If the intent is transactional AND a valid 32-char ID is extracted.
1. **Agent Instantiation:** A Langchain `create_react_agent` is spun up.
2. **Tool Binding:** The Agent is provided internal Python Tools (`lookup_order_info`, `lookup_seller_info`). These tools natively load the `.parquet` datasets, filter via Pandas, and return JSON configurations detailing delivery dates, values, and metrics.
3. **ReAct Loop:** The LLM receives the prompt -> decides what tool to use -> inputs the ID into the tool -> the system executes the Python function -> returns an "Observation" -> The LLM processes the Observation.
4. **Final Answer Synthesis:** Once the LLM determines it has enough tabular context to resolve the user's issue, it generates a comprehensive human response.

---

## 5. Summary of System Achievements

1. **Elimination of Cross-Pollination Hallucinations:** Most RAG setups fail because they inject SQL tables alongside textual PDFs in the same prompt, confusing the LLM. By hard-routing between an Agent Pipeline and a Vector Pipeline based on LLM Intent analysis, we segregated unstructured inference from structured inference perfectly.
2. **Optimized Token Economy:** Vector DB lookups cost near 0 compute. By restricting the Heavy ReAct Agent module to trigger only when a 32-char ID is present, we prevent the system from wasting high-level compute and API tokens trying to "Tool Call" basic conversational pleasantries.
3. **Scalability:** FAISS and Parquet operate entirely in physical memory and local disk. The only cloud bottleneck is the Groq API. This architecture can support thousands of simultaneous concurrent users without spinning up Kubernetes orchestration for standard databases.
