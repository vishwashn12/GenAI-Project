from __future__ import annotations

from typing import Any

import pandas as pd

from services.data_service import load_dataframe, pick_column


def _issue_distribution(tickets_df: pd.DataFrame) -> list[dict[str, Any]]:
    issue_col = pick_column(
        tickets_df,
        ["issue_type", "issue_category", "intent", "category", "topic", "issue"],
    )
    if not issue_col or tickets_df.empty:
        return []

    counts = (
        tickets_df[issue_col]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .head(8)
        .reset_index()
    )
    counts.columns = ["label", "count"]
    return counts.to_dict(orient="records")


def _sla_compliance(tickets_df: pd.DataFrame) -> list[dict[str, Any]]:
    if tickets_df.empty:
        return []

    breached_col = pick_column(tickets_df, ["sla_breached", "breached", "is_sla_breached"])
    if breached_col:
        normalized = tickets_df[breached_col].astype(str).str.lower().str.strip()
        breached = normalized.isin(["true", "1", "yes"]).sum()
        compliant = len(normalized) - breached
        return [
            {"label": "Compliant", "value": int(compliant)},
            {"label": "Breached", "value": int(breached)},
        ]

    resolution_col = pick_column(tickets_df, ["resolution_hours", "resolution_time_hours", "resolution_time"])
    if resolution_col:
        series = pd.to_numeric(tickets_df[resolution_col], errors="coerce").fillna(0)
        compliant = (series <= 24).sum()
        breached = (series > 24).sum()
        return [
            {"label": "Compliant", "value": int(compliant)},
            {"label": "Breached", "value": int(breached)},
        ]

    return []


def _sentiment_stats(tickets_df: pd.DataFrame, complaints_df: pd.DataFrame) -> list[dict[str, Any]]:
    source_df = tickets_df if not tickets_df.empty else complaints_df
    if source_df.empty:
        return []

    sentiment_col = pick_column(source_df, ["sentiment", "sentiment_label", "polarity"])
    if not sentiment_col:
        return [
            {"label": "Positive", "count": 0},
            {"label": "Neutral", "count": int(len(source_df))},
            {"label": "Negative", "count": 0},
        ]

    counts = (
        source_df[sentiment_col]
        .fillna("neutral")
        .astype(str)
        .str.lower()
        .replace({"pos": "positive", "neg": "negative"})
        .value_counts()
        .reset_index()
    )
    counts.columns = ["label", "count"]
    return counts.to_dict(orient="records")


def _seller_kpi(seller_df: pd.DataFrame) -> list[dict[str, Any]]:
    if seller_df.empty:
        return []

    id_col = pick_column(seller_df, ["seller_id", "seller", "merchant_id", "id"])
    rating_col = pick_column(seller_df, ["rating", "seller_rating", "avg_rating"])
    response_col = pick_column(seller_df, ["response_time", "response_time_hours", "avg_response_time"])
    fulfillment_col = pick_column(seller_df, ["fulfillment_rate", "fill_rate", "on_time_rate"])

    frame = pd.DataFrame()
    if id_col:
        frame["seller_id"] = seller_df[id_col].astype(str)
    else:
        frame["seller_id"] = seller_df.index.astype(str)

    frame["rating"] = pd.to_numeric(seller_df[rating_col], errors="coerce") if rating_col else 0
    frame["response_time"] = pd.to_numeric(seller_df[response_col], errors="coerce") if response_col else 0
    frame["fulfillment_rate"] = (
        pd.to_numeric(seller_df[fulfillment_col], errors="coerce") if fulfillment_col else 0
    )

    frame = frame.fillna(0)
    frame = frame.sort_values(by=["rating", "fulfillment_rate"], ascending=False).head(10)

    result = frame.to_dict(orient="records")
    for row in result:
        row["rating"] = round(float(row["rating"]), 2)
        row["response_time"] = round(float(row["response_time"]), 2)
        row["fulfillment_rate"] = round(float(row["fulfillment_rate"]), 2)
    return result


def build_analytics_payload() -> dict[str, Any]:
    tickets_df = load_dataframe(["synthetic_tickets.parquet", "synthetic_tickets.csv"])
    seller_df = load_dataframe(["seller_kpi.parquet", "seller_kpi.csv"])
    complaints_df = load_dataframe(["amazon_complaints.parquet", "amazon_complaints.csv"])

    issue_distribution = _issue_distribution(tickets_df)
    sla_compliance = _sla_compliance(tickets_df)
    sentiment_stats = _sentiment_stats(tickets_df, complaints_df)
    seller_kpi = _seller_kpi(seller_df)

    total_queries = int(len(tickets_df))
    avg_latency = 0.0
    success_rate = 0.0

    latency_col = pick_column(tickets_df, ["latency", "total_latency", "response_latency"])
    if latency_col and not tickets_df.empty:
        avg_latency = round(float(pd.to_numeric(tickets_df[latency_col], errors="coerce").fillna(0).mean()), 3)

    status_col = pick_column(tickets_df, ["status", "resolved", "is_resolved", "success"])
    if status_col and not tickets_df.empty:
        status_vals = tickets_df[status_col].astype(str).str.lower().str.strip()
        positives = status_vals.isin(["resolved", "true", "1", "success", "closed", "yes"]).sum()
        success_rate = round((positives / len(status_vals)) * 100, 2)
    elif total_queries > 0:
        success_rate = 100.0

    return {
        "summary": {
            "total_queries": total_queries,
            "avg_latency": avg_latency,
            "success_rate": success_rate,
        },
        "issue_distribution": issue_distribution,
        "sla_compliance": sla_compliance,
        "seller_kpi": seller_kpi,
        "sentiment_stats": sentiment_stats,
    }
