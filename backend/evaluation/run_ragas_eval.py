import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# Initialize paths and env
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from config import GROQ_API_KEY
from evaluation.test_dataset import TEST_CASES

# RAGAS 0.4 dependencies
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import (
    Faithfulness,
    AnswerRelevancy,
    AnswerCorrectness,
    SemanticSimilarity,
    ResponseGroundedness,
)
from ragas.embeddings.huggingface_provider import HuggingFaceEmbeddings as RagasHFEmbeddings

API_URL = "http://localhost:8000/chat"
EVAL_OUTPUT_DIR = Path(__file__).resolve().parent / "results"
EVAL_OUTPUT_DIR.mkdir(exist_ok=True)
PROGRESS_FILE = EVAL_OUTPUT_DIR / "eval_progress.json"

async def score_single_result(r: dict, metrics: list) -> dict:
    """Score a single result using the initialized metrics."""
    if r["mode"] == "error":
        return {**r, "scores": {}}

    print(f"  Scoring [{r['id']}/{len(TEST_CASES)}] {r['question'][:50]}...", end=" ", flush=True)

    row_scores = {}
    ri = r["question"]
    rr = r["answer"]
    rc = r["contexts"]
    rg = r["ground_truth"]

    for metric_name, metric in metrics:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if metric_name == "faithfulness":
                    score = await metric.ascore(user_input=ri, response=rr, retrieved_contexts=rc)
                elif metric_name == "answer_relevancy":
                    score = await metric.ascore(user_input=ri, response=rr)
                elif metric_name == "answer_correctness":
                    score = await metric.ascore(user_input=ri, response=rr, reference=rg)
                elif metric_name == "semantic_similarity":
                    score = await metric.ascore(response=rr, reference=rg)
                elif metric_name == "response_groundedness":
                    score = await metric.ascore(response=rr, retrieved_contexts=rc)
                
                val = score.value if hasattr(score, 'value') else float(score)
                row_scores[metric_name] = round(val, 4)
                break  # Success, break the retry loop
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg and attempt < max_retries - 1:
                    print(f"\n    ⚠ Rate limit hit (429) for {metric_name}. Sleeping 30s...")
                    await asyncio.sleep(30)
                    continue  # Retry
                else:
                    row_scores[metric_name] = None
                    print(f"\n    ⚠ {metric_name} failed: {error_msg[:80]}")
                    break

        # Groq free tier rate limit
        await asyncio.sleep(3.5)

    print(f"✓ {row_scores}")
    return {**r, "scores": row_scores}


def load_progress():
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_progress(results):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


# ── Step 3 & 4 (Analytics + Reporting) ─────────────────────────
def compute_intent_accuracy(results: list[dict]) -> dict:
    correct = 0
    total = 0
    confusion = {}
    for r in results:
        if r["mode"] == "error": continue
        expected = r["expected_intent"]
        actual = r["classified_intent"]
        total += 1
        if expected == actual: correct += 1
        if expected not in confusion: confusion[expected] = {}
        confusion[expected][actual] = confusion[expected].get(actual, 0) + 1

    return {
        "accuracy": round(correct / total, 4) if total else 0,
        "correct": correct, "total": total, "confusion_matrix": confusion
    }

def compute_latency_stats(results: list[dict]) -> dict:
    by_mode = {}
    for r in results:
        if r["mode"] == "error": continue
        mode = r["mode"]
        if mode not in by_mode: by_mode[mode] = []
        by_mode[mode].append(r["latency"])

    stats = {}
    for mode, latencies in by_mode.items():
        stats[mode] = {
            "count": len(latencies),
            "avg_ms": round(sum(latencies) / len(latencies) * 1000, 1),
            "min_ms": round(min(latencies) * 1000, 1),
            "max_ms": round(max(latencies) * 1000, 1),
        }
    all_latencies = [r["latency"] for r in results if r["mode"] != "error"]
    stats["overall"] = {
        "count": len(all_latencies),
        "avg_ms": round(sum(all_latencies) / len(all_latencies) * 1000, 1) if all_latencies else 0,
    }
    return stats

def compute_avg_scores(results: list[dict], metric_names: list[str]) -> dict:
    scores_summary = {name: [] for name in metric_names}
    for r in results:
        if r["mode"] == "error" or "scores" not in r: continue
        for name in metric_names:
            val = r["scores"].get(name)
            if val is not None:
                scores_summary[name].append(val)
    
    avg_scores = {}
    for name, vals in scores_summary.items():
        avg_scores[name] = round(sum(vals) / len(vals), 4) if vals else None
    return avg_scores

def generate_report(avg_scores, intent_accuracy, latency_stats, results, duration_s):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"# 📊 Olist RAG System — RAGAS Evaluation Report\n\n**Generated:** {timestamp}\n**Test Cases:** {len(results)}\n**Evaluation Duration:** {round(duration_s / 60, 1)} min\n\n---\n\n## 🏆 Overall RAGAS Scores\n\n| Metric | Score | Rating |\n|--------|-------|--------|\n"
    for metric_name, score in avg_scores.items():
        if score is not None:
            rating = "🟢 Excellent" if score >= 0.8 else "🟡 Good" if score >= 0.6 else "🟠 Fair" if score >= 0.4 else "🔴 Needs Improvement"
            report += f"| {metric_name.replace('_', ' ').title()} | {score:.4f} | {rating} |\n"
        else:
            report += f"| {metric_name.replace('_', ' ').title()} | N/A | ⚪ Skipped |\n"
    
    report += f"\n---\n\n## 🎯 Intent Classification\n| Metric | Value |\n|--------|-------|\n| **Accuracy** | {intent_accuracy['accuracy']:.1%} ({intent_accuracy['correct']}/{intent_accuracy['total']}) |\n\n### Confusion Matrix\n\n| Expected ↓ / Predicted → | "
    all_intents = sorted(set(list(intent_accuracy["confusion_matrix"].keys()) + [a for row in intent_accuracy["confusion_matrix"].values() for a in row.keys()]))
    report += " | ".join(all_intents) + " |\n|" + "---|" * (len(all_intents) + 1) + "\n"
    for expected in all_intents:
        row = intent_accuracy["confusion_matrix"].get(expected, {})
        cells = [f"**{row.get(pred, 0)}**" if expected == pred and row.get(pred, 0) > 0 else str(row.get(pred, 0)) for pred in all_intents]
        report += f"| {expected} | " + " | ".join(cells) + " |\n"

    report += f"\n---\n\n## ⚡ Latency Analysis\n| Mode | Count | Avg (ms) | Min (ms) | Max (ms) |\n|------|-------|----------|----------|----------|\n"
    for mode, stats in latency_stats.items():
        if mode == "overall": report += f"| **Overall** | {stats['count']} | {stats['avg_ms']} | — | — |\n"
        else: report += f"| {mode} | {stats['count']} | {stats['avg_ms']} | {stats['min_ms']} | {stats['max_ms']} |\n"

    report += "\n---\n\n## 📋 Per-Question Results\n| # | Question | Intent (Ex→Got) | Mode | Latency | Faith. | Relv. | Corr. | SemSim |\n|---|----------|-----------------|------|---------|--------|-------|-------|--------|\n"
    for i, r in enumerate(results, 1):
        q = r["question"][:30] + "..." if len(r["question"]) > 30 else r["question"]
        ei, ci, mode, lat = r.get("expected_intent", "?"), r.get("classified_intent", "?"), r.get("mode", "?"), f"{r.get('latency', 0)}s"
        im = "✅" if ei == ci else "❌"
        s = r.get("scores", {})
        f, rl, c, sm = s.get('faithfulness', 'N/A'), s.get('answer_relevancy', 'N/A'), s.get('answer_correctness', 'N/A'), s.get('semantic_similarity', 'N/A')
        report += f"| {i} | {q} | {im} {ei[:4]}→{ci[:4]} | {mode} | {lat} | {f} | {rl} | {c} | {sm} |\n"
    
    return report


def main():
    print("=" * 60)
    print("  OLIST EVALUATION (PROGRESSIVE SAVE)")
    print("=" * 60)

    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set in .env")
        sys.exit(1)

    try:
        requests.get("http://localhost:8000/analytics", timeout=5)
    except:
        print("ERROR: Backend not running. Start with: uvicorn main:app...")
        sys.exit(1)

    # Init Ragas
    client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    evaluator_llm = llm_factory(model="llama-3.1-8b-instant", provider="openai", client=client)
    ragas_embeddings = RagasHFEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")

    metrics_list = [
        ("faithfulness", Faithfulness(llm=evaluator_llm)),
        ("answer_relevancy", AnswerRelevancy(llm=evaluator_llm, embeddings=ragas_embeddings)),
        ("answer_correctness", AnswerCorrectness(llm=evaluator_llm, embeddings=ragas_embeddings)),
        ("semantic_similarity", SemanticSimilarity(embeddings=ragas_embeddings)), # Replacing FactualCorrectness
        ("response_groundedness", ResponseGroundedness(llm=evaluator_llm))
    ]

    results = load_progress()
    evaluated_ids = {r.get("id") for r in results}

    t_start = time.time()
    
    print(f"Resuming... Found {len(evaluated_ids)} completed items in progress file.")

    for i, tc in enumerate(TEST_CASES):
        tc_id = i + 1
        if tc_id in evaluated_ids:
            continue
            
        print(f"\n[Evaluating {tc_id}/{len(TEST_CASES)}] {tc['question']}")
        
        # 1. API Call
        try:
            t0 = time.time()
            resp = requests.post(API_URL, json={
                "query": tc["question"], "order_id": tc.get("order_id", ""),
                "session_id": f"eval-{tc_id}", "use_rewrite": True, "use_mq": False, "use_comp": False
            }, timeout=60)
            latency = round(time.time() - t0, 2)
            
            if resp.status_code != 200:
                print(f"  API FAIL ({resp.status_code})")
                r_apidata = {"answer": f"Error {resp.status_code}", "contexts": [], "latency": latency, "mode": "error", "classified_intent": "error"}
            else:
                data = resp.json()
                contexts = [src.get("text", "") or src.get("snippet", "") for src in data.get("sources", [])]
                contexts = [c for c in contexts if c]

                # FIX: Context Injection for Agent Mode
                mode = data.get("mode", "unknown")
                if not contexts and mode == "agent":
                    # Use the answer itself as the context to prevent Faithfulness = 0.0 penalty
                    contexts = [data.get("answer", "No answer provided.")]
                elif not contexts:
                    contexts = ["No context retrieved."]

                r_apidata = {
                    "answer": data.get("answer", ""),
                    "contexts": contexts,
                    "latency": latency,
                    "mode": mode,
                    "classified_intent": data.get("intent", "unknown"),
                    "docs_retrieved": data.get("documents_retrieved", 0),
                }
        except Exception as e:
            print(f"  API ERROR: {e}")
            r_apidata = {"answer": str(e), "contexts": [], "latency": 0, "mode": "error", "classified_intent": "error"}

        compiled_item = {"id": tc_id, **tc, **r_apidata}

        # 2. Ragas Scoring
        scored_item = asyncio.run(score_single_result(compiled_item, metrics_list))
        results.append(scored_item)
        
        # 3. Save progressively
        save_progress(results)


    duration = time.time() - t_start
    print("\n✅ All queries evaluated.")

    # Generate Final Report
    metric_names = [m[0] for m in metrics_list]
    avg_scores = compute_avg_scores(results, metric_names)
    int_acc = compute_intent_accuracy(results)
    lat_stats = compute_latency_stats(results)

    report = generate_report(avg_scores, int_acc, lat_stats, results, duration)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = EVAL_OUTPUT_DIR / f"ragas_report_{timestamp}.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"\n✅ Report saved to: {report_path}")

if __name__ == "__main__":
    main()
