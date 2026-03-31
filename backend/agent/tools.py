"""
LangGraph agent tool definitions — exact replica of Phase 3 Cell 13.
Tools are typed functions the LLM can call via function-calling.
"""
from __future__ import annotations

import pandas as pd
from langchain_core.tools import tool

from config import PROCESSED_DIR


# ── Load data once at module import ──────────────────────────
def _load_order_df() -> pd.DataFrame:
    path = PROCESSED_DIR / 'order_lookup.parquet'
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


def _load_seller_df() -> pd.DataFrame:
    path = PROCESSED_DIR / 'seller_kpi.parquet'
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()


_order_df: pd.DataFrame | None = None
_seller_df: pd.DataFrame | None = None


def _get_order_df() -> pd.DataFrame:
    global _order_df
    if _order_df is None:
        _order_df = _load_order_df()
    return _order_df


def _get_seller_df() -> pd.DataFrame:
    global _seller_df
    if _seller_df is None:
        _seller_df = _load_seller_df()
    return _seller_df


# ── Hybrid retriever + format_context will be injected at build time ──
# We store a reference that gets set when the system boots.
_rag_search_fn = None


def set_rag_search_fn(fn):
    """Inject the hybrid retriever search function at startup."""
    global _rag_search_fn
    _rag_search_fn = fn


@tool
def rag_search(query: str) -> str:
    """
    Search the knowledge base for policies, product complaints, and support history.
    Use this for: return policy, refund rules, product quality issues, similar complaints.
    Input: a natural language search query.
    """
    if _rag_search_fn is None:
        return "RAG search is not available."
    return _rag_search_fn(query)


@tool
def order_lookup(order_id: str) -> str:
    """
    Look up order status, delivery dates, and payment information by order ID.
    Use this when the customer provides an order ID or asks about a specific order.
    Input: the order ID string (e.g. 'abc123def456').
    """
    order_df = _get_order_df()
    if order_df.empty:
        return 'Order database not available.'
    row = order_df[order_df['order_id'] == order_id]
    if row.empty:
        return f'No order found with ID: {order_id}. Please verify the order ID.'
    r = row.iloc[0]
    delay = r.get('delivery_delay_days', None)
    delay_str = (f'{int(delay)} days late'
                 if pd.notna(delay) and delay > 0
                 else 'on time')
    return (
        f'Order {order_id}: status={r.order_status}, '
        f'purchased={r.order_purchase_timestamp}, '
        f'estimated_delivery={r.order_estimated_delivery_date}, '
        f'actual_delivery={r.order_delivered_customer_date}, '
        f'delivery={delay_str}, '
        f'payment_type={r.payment_type}, '
        f'payment_value=R${r.payment_value:.2f}, '
        f'category={r.category_en}, '
        f'issue_flag={r.issue_category}'
    )


@tool
def seller_analysis(seller_id: str) -> str:
    """
    Get seller performance metrics including complaint rate, late delivery rate, and rating.
    Use this when a customer reports issues with a specific seller.
    Input: the seller ID string.
    """
    seller_df = _get_seller_df()
    if seller_df.empty:
        return 'Seller database not available.'
    row = seller_df[seller_df['seller_id'] == seller_id]
    if row.empty:
        return f'No seller data for ID: {seller_id}'
    r = row.iloc[0]
    return (
        f'Seller {seller_id}: avg_rating={r.avg_rating:.1f}/5, '
        f'late_rate={r.late_rate * 100:.1f}%, '
        f'complaint_rate={r.complaint_rate * 100:.1f}%, '
        f'total_orders={int(r.total_orders)}, '
        f'flagged={r.is_flagged}'
    )


@tool
def escalate_to_human(reason: str) -> str:
    """
    Escalate the conversation to a human support agent.
    Use this when: the issue is complex, customer is very upset, fraud is suspected,
    or when 2 tool calls have not resolved the issue.
    Input: a brief description of why escalation is needed.
    """
    return (
        f'ESCALATED: This case has been flagged for human review. '
        f'Reason: {reason}. '
        f'A support specialist will contact you within 4 hours via email.'
    )


TOOLS = [rag_search, order_lookup, seller_analysis, escalate_to_human]
