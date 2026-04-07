"""
Analytics service — "Operations Dashboard"
Powered by synthetic_tickets + order_lookup datasets.
"""
from __future__ import annotations
from typing import Any

import pandas as pd

from services.data_service import load_dataframe


def _kpi_summary(tickets_df: pd.DataFrame, orders_df: pd.DataFrame) -> dict[str, Any]:
    total_tickets = len(tickets_df)

    sla_compliance = 0.0
    if not tickets_df.empty and "sla_met" in tickets_df.columns:
        sla_compliance = round(float(tickets_df["sla_met"].sum() / len(tickets_df) * 100), 1)

    late_delivery_rate = 0.0
    never_delivered = 0
    if not orders_df.empty:
        if "is_late" in orders_df.columns:
            late_delivery_rate = round(float(orders_df["is_late"].sum() / len(orders_df) * 100), 1)
        if "never_delivered" in orders_df.columns:
            never_delivered = int(orders_df["never_delivered"].sum())

    avg_review = 0.0
    if not orders_df.empty and "review_score" in orders_df.columns:
        avg_review = round(float(orders_df["review_score"].mean()), 2)

    return {
        "total_tickets": total_tickets,
        "sla_compliance_pct": sla_compliance,
        "late_delivery_rate": late_delivery_rate,
        "avg_review_score": avg_review,
        "never_delivered": never_delivered,
    }


def _issue_distribution(tickets_df: pd.DataFrame) -> list[dict[str, Any]]:
    if tickets_df.empty or "issue_category" not in tickets_df.columns:
        return []
    counts = (
        tickets_df["issue_category"]
        .fillna("unknown")
        .str.replace("_", " ")
        .str.title()
        .value_counts()
        .reset_index()
    )
    counts.columns = ["label", "count"]
    return counts.to_dict(orient="records")


def _order_status_distribution(orders_df: pd.DataFrame) -> list[dict[str, Any]]:
    if orders_df.empty or "order_status" not in orders_df.columns:
        return []
    counts = (
        orders_df["order_status"]
        .fillna("unknown")
        .str.replace("_", " ")
        .str.title()
        .value_counts()
        .reset_index()
    )
    counts.columns = ["label", "count"]
    return counts.to_dict(orient="records")


def _channel_distribution(tickets_df: pd.DataFrame) -> list[dict[str, Any]]:
    if tickets_df.empty or "channel" not in tickets_df.columns:
        return []
    counts = (
        tickets_df["channel"]
        .fillna("unknown")
        .str.title()
        .value_counts()
        .reset_index()
    )
    counts.columns = ["label", "count"]
    return counts.to_dict(orient="records")


def _resolution_status(tickets_df: pd.DataFrame) -> list[dict[str, Any]]:
    if tickets_df.empty or "resolution_status" not in tickets_df.columns:
        return []
    counts = (
        tickets_df["resolution_status"]
        .fillna("unknown")
        .str.title()
        .value_counts()
        .reset_index()
    )
    counts.columns = ["label", "count"]
    return counts.to_dict(orient="records")


def _priority_distribution(tickets_df: pd.DataFrame) -> list[dict[str, Any]]:
    if tickets_df.empty or "priority" not in tickets_df.columns:
        return []
    order_map = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    counts = (
        tickets_df["priority"]
        .fillna("unknown")
        .str.lower()
        .value_counts()
        .reset_index()
    )
    counts.columns = ["label", "count"]
    counts["sort_key"] = counts["label"].map(lambda x: order_map.get(x, 99))
    counts = counts.sort_values("sort_key").drop("sort_key", axis=1)
    counts["label"] = counts["label"].str.title()
    return counts.to_dict(orient="records")


def _top_cities(tickets_df: pd.DataFrame) -> list[dict[str, Any]]:
    if tickets_df.empty or "customer_city" not in tickets_df.columns:
        return []
    counts = (
        tickets_df["customer_city"]
        .fillna("unknown")
        .str.title()
        .value_counts()
        .head(10)
        .reset_index()
    )
    counts.columns = ["city", "tickets"]
    return counts.to_dict(orient="records")


def build_analytics_payload() -> dict[str, Any]:
    tickets_df = load_dataframe(["synthetic_tickets.parquet", "synthetic_tickets.csv"])
    orders_df = load_dataframe(["order_lookup.parquet"])

    return {
        "summary": _kpi_summary(tickets_df, orders_df),
        "issue_distribution": _issue_distribution(tickets_df),
        "order_status_distribution": _order_status_distribution(orders_df),
        "channel_distribution": _channel_distribution(tickets_df),
        "resolution_status": _resolution_status(tickets_df),
        "priority_distribution": _priority_distribution(tickets_df),
        "top_cities": _top_cities(tickets_df),
    }
