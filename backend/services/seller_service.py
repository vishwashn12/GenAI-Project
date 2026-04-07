"""
Insights service — "Seller Intelligence"
Powered by seller_kpi dataset.
"""
from __future__ import annotations
from typing import Any

import pandas as pd

from services.data_service import load_dataframe


def _seller_summary(seller_df: pd.DataFrame) -> dict[str, Any]:
    if seller_df.empty:
        return {
            "total_sellers": 0,
            "flagged_sellers": 0,
            "avg_complaint_rate": 0.0,
            "avg_late_rate": 0.0,
        }
    return {
        "total_sellers": len(seller_df),
        "flagged_sellers": int(seller_df["is_flagged"].sum()) if "is_flagged" in seller_df.columns else 0,
        "avg_complaint_rate": round(float(seller_df["complaint_rate"].mean()) * 100, 1) if "complaint_rate" in seller_df.columns else 0.0,
        "avg_late_rate": round(float(seller_df["late_rate"].mean()) * 100, 1) if "late_rate" in seller_df.columns else 0.0,
    }


def _seller_risk_scatter(seller_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Top 500 sellers by order count — scatter data for risk quadrant."""
    if seller_df.empty:
        return []
    needed = ["seller_id", "complaint_rate", "avg_rating", "is_flagged", "total_orders"]
    if any(c not in seller_df.columns for c in needed):
        return []
    df = seller_df.nlargest(500, "total_orders").copy()
    result = []
    for _, row in df.iterrows():
        result.append({
            "seller_id": str(row["seller_id"])[:8],
            "complaint_rate": round(float(row["complaint_rate"]) * 100, 1),
            "avg_rating": round(float(row["avg_rating"]), 2),
            "is_flagged": bool(row["is_flagged"]),
            "total_orders": int(row["total_orders"]),
        })
    return result


def _worst_sellers(seller_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Top 10 sellers by complaint rate (min 5 orders)."""
    if seller_df.empty:
        return []
    needed = ["seller_id", "complaint_rate", "avg_rating", "late_rate", "total_revenue", "is_flagged", "total_orders"]
    if any(c not in seller_df.columns for c in needed):
        return []
    df = seller_df[seller_df["total_orders"] >= 5].nlargest(10, "complaint_rate").copy()
    result = []
    for _, row in df.iterrows():
        result.append({
            "seller_id": str(row["seller_id"])[:12],
            "complaint_rate": round(float(row["complaint_rate"]) * 100, 1),
            "avg_rating": round(float(row["avg_rating"]), 2),
            "late_rate": round(float(row["late_rate"]) * 100, 1),
            "total_revenue": round(float(row["total_revenue"]), 2),
            "total_orders": int(row["total_orders"]),
            "is_flagged": bool(row["is_flagged"]),
        })
    return result


def _best_sellers(seller_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Top 10 sellers by avg rating (min 10 orders)."""
    if seller_df.empty:
        return []
    needed = ["seller_id", "avg_rating", "complaint_rate", "late_rate", "total_revenue", "total_orders"]
    if any(c not in seller_df.columns for c in needed):
        return []
    df = seller_df[seller_df["total_orders"] >= 10].nlargest(10, "avg_rating").copy()
    result = []
    for _, row in df.iterrows():
        result.append({
            "seller_id": str(row["seller_id"])[:12],
            "avg_rating": round(float(row["avg_rating"]), 2),
            "complaint_rate": round(float(row["complaint_rate"]) * 100, 1),
            "late_rate": round(float(row["late_rate"]) * 100, 1),
            "total_revenue": round(float(row["total_revenue"]), 2),
            "total_orders": int(row["total_orders"]),
        })
    return result


def _rating_distribution(seller_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Histogram of seller avg_rating bucketed into 5 ranges."""
    if seller_df.empty or "avg_rating" not in seller_df.columns:
        return []
    bins = [1, 2, 3, 4, 4.5, 5.01]
    labels = ["1–2 ★", "2–3 ★", "3–4 ★", "4–4.5 ★", "4.5–5 ★"]
    bucketed = pd.cut(seller_df["avg_rating"].dropna(), bins=bins, labels=labels, right=False)
    counts = bucketed.value_counts().sort_index().reset_index()
    counts.columns = ["label", "count"]
    return counts.to_dict(orient="records")


def _revenue_concentration(seller_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Top 10 sellers by total revenue."""
    if seller_df.empty or "total_revenue" not in seller_df.columns:
        return []
    df = seller_df.nlargest(10, "total_revenue").copy()
    result = []
    for _, row in df.iterrows():
        result.append({
            "seller_id": str(row["seller_id"])[:10],
            "revenue": round(float(row["total_revenue"]), 2),
            "total_orders": int(row["total_orders"]),
            "avg_rating": round(float(row["avg_rating"]), 2),
        })
    return result


def build_insights_payload() -> dict[str, Any]:
    seller_df = load_dataframe(["seller_kpi.parquet", "seller_kpi.csv"])

    return {
        "summary": _seller_summary(seller_df),
        "seller_risk": _seller_risk_scatter(seller_df),
        "worst_sellers": _worst_sellers(seller_df),
        "best_sellers": _best_sellers(seller_df),
        "rating_distribution": _rating_distribution(seller_df),
        "revenue_concentration": _revenue_concentration(seller_df),
    }
