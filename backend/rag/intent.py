"""
Rule-based intent classifier — exact replica of Phase 3 Cell 6.
"""
from __future__ import annotations

from enum import Enum


class QueryIntent(str, Enum):
    ORDER_STATUS = 'order_status'
    REFUND_REQUEST = 'refund_request'
    PRODUCT_ISSUE = 'product_issue'
    DELIVERY_ISSUE = 'delivery_issue'
    POLICY_QUERY = 'policy_query'
    SELLER_ISSUE = 'seller_issue'
    GENERAL = 'general'


INTENT_RULES: dict[QueryIntent, list[str]] = {
    QueryIntent.REFUND_REQUEST: [
        'refund', 'money back', 'reimbur', 'cancel', 'chargeback', 'return',
    ],
    QueryIntent.ORDER_STATUS: [
        'where is my order', 'order status', 'tracking', 'track',
        'shipped', 'dispatch',
        'whr iz', 'ordr',  # common typos
    ],
    QueryIntent.DELIVERY_ISSUE: [
        'late', 'delayed', 'not arrived', 'overdue',
        'estimated date', 'never came',
        'laet', 'delayd', 'lte', 'delvery',  # common typos
    ],
    QueryIntent.PRODUCT_ISSUE: [
        'broken', 'defective', 'damage', 'wrong item',
        'not as described', 'different', 'fake', 'counterfeit',
        'missing part', 'not working',
    ],
    QueryIntent.POLICY_QUERY: [
        'policy', 'can i return', 'am i eligible',
        'rules', 'rights', 'consumer', 'CDC',
        'within how many days', 'return window',
    ],
    QueryIntent.SELLER_ISSUE: [
        'seller', 'vendor', 'merchant', 'not responding', 'no reply',
    ],
}


def classify_intent(query: str) -> QueryIntent:
    """Classify customer query intent using keyword rules."""
    q = query.lower()
    for intent, keywords in INTENT_RULES.items():
        if any(kw in q for kw in keywords):
            return intent
    return QueryIntent.GENERAL
