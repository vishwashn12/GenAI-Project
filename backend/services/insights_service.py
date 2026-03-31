from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

from services.data_service import load_dataframe, parse_possible_list, pick_column


def _latency_breakdown(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return [
            {"metric": "retrieval", "value": 0.0},
            {"metric": "llm", "value": 0.0},
            {"metric": "total", "value": 0.0},
        ]

    retrieval_col = pick_column(df, ["retrieval_latency", "latency_retrieval", "retrieval"])
    llm_col = pick_column(df, ["llm_latency", "latency_llm", "llm"])
    total_col = pick_column(df, ["total_latency", "latency", "response_latency"])

    retrieval = (
        float(pd.to_numeric(df[retrieval_col], errors="coerce").fillna(0).mean()) if retrieval_col else 0.0
    )
    llm = float(pd.to_numeric(df[llm_col], errors="coerce").fillna(0).mean()) if llm_col else 0.0
    total = float(pd.to_numeric(df[total_col], errors="coerce").fillna(0).mean()) if total_col else retrieval + llm

    return [
        {"metric": "retrieval", "value": round(retrieval, 3)},
        {"metric": "llm", "value": round(llm, 3)},
        {"metric": "total", "value": round(total, 3)},
    ]


def _mode_distribution(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []

    mode_col = pick_column(df, ["mode", "response_mode"])
    if not mode_col:
        return []

    counts = df[mode_col].fillna("unknown").astype(str).str.lower().value_counts().reset_index()
    counts.columns = ["label", "value"]
    return counts.to_dict(orient="records")


def _tool_usage(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []

    tool_col = pick_column(df, ["tool_calls", "tools", "used_tools"])
    if not tool_col:
        return []

    usage_counter: Counter[str] = Counter()
    for value in df[tool_col].tolist():
        tools = parse_possible_list(value)
        for tool in tools:
            usage_counter[str(tool)] += 1

    return [{"tool": key, "count": int(val)} for key, val in usage_counter.most_common()]


def build_insights_payload() -> dict[str, Any]:
    ticket_df = load_dataframe(["synthetic_tickets.parquet", "synthetic_tickets.csv"])

    return {
        "latency_breakdown": _latency_breakdown(ticket_df),
        "tool_usage": _tool_usage(ticket_df),
        "mode_distribution": _mode_distribution(ticket_df),
    }
