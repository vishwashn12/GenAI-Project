"""
Intent classification — hybrid: LLM (primary) + keyword rules (fallback).
"""
from __future__ import annotations

from enum import Enum


class QueryIntent(str, Enum):
    ORDER_STATUS   = 'order_status'
    REFUND_REQUEST = 'refund_request'
    PRODUCT_ISSUE  = 'product_issue'
    DELIVERY_ISSUE = 'delivery_issue'
    POLICY_QUERY   = 'policy_query'
    SELLER_ISSUE   = 'seller_issue'
    GENERAL        = 'general'


# ── Keyword rules (fallback only) ─────────────────────────────
INTENT_RULES: dict[QueryIntent, list[str]] = {
    QueryIntent.REFUND_REQUEST: [
        'refund', 'money back', 'reimbur', 'chargeback',
        'want my money', 'get a refund', 'request refund',
    ],
    QueryIntent.ORDER_STATUS: [
        'where is my order', 'order status', 'tracking', 'track my',
        'shipped', 'dispatch', 'has my order', 'check my order',
        'whr iz', 'ordr',
    ],
    QueryIntent.DELIVERY_ISSUE: [
        'late', 'delayed', 'not arrived', 'not received', 'overdue',
        'never came', 'still waiting', 'not delivered', 'missing',
        'package not', 'parcel not', 'hasn\'t arrived', 'haven\'t received',
        'laet', 'delayd', 'lte', 'delvery',
    ],
    QueryIntent.PRODUCT_ISSUE: [
        'broken', 'defective', 'damage', 'wrong item', 'wrong product',
        'not as described', 'different product', 'fake', 'counterfeit',
        'missing part', 'not working', 'arrived broken', 'item is broken',
        'product is', 'quality',
    ],
    QueryIntent.POLICY_QUERY: [
        'policy', 'can i return', 'am i eligible', 'how do i return',
        'return window', 'rules', 'consumer rights', 'CDC',
        'within how many days', 'what happens if', 'allowed to',
    ],
    QueryIntent.SELLER_ISSUE: [
        'seller', 'vendor', 'merchant', 'not responding', 'no reply',
        'seller won\'t', 'shop is', 'store won\'t',
    ],
}


def classify_intent(query: str) -> QueryIntent:
    """Keyword-rule classifier — used as fallback."""
    q = query.lower()
    for intent, keywords in INTENT_RULES.items():
        if any(kw in q for kw in keywords):
            return intent
    return QueryIntent.GENERAL


# ── LLM classifier ─────────────────────────────────────────────
_CLASSIFICATION_PROMPT = """\
You are a customer support intent classifier for an e-commerce platform.
Classify the customer message into exactly ONE of these categories:

order_status    - asking where their order is, tracking, shipping status
delivery_issue  - order is late, delayed, not arrived, never received
refund_request  - wants a refund, money back, or to cancel an order
product_issue   - item is broken, wrong, defective, damaged, or fake
policy_query    - asking about rules, policies, return/refund eligibility
seller_issue    - complaint about a specific seller or vendor
general         - anything else, greetings, unclear questions

Customer message: "{query}"

Reply with ONLY the category name, nothing else. No explanation."""

_VALID_INTENTS = {i.value for i in QueryIntent}


def classify_intent_llm(query: str, llm) -> QueryIntent:
    """
    LLM-based intent classifier using the already-loaded Groq LLM.
    Falls back to keyword rules on any error or unexpected output.
    """
    try:
        prompt = _CLASSIFICATION_PROMPT.format(query=query[:400])
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        label = response.content.strip().lower().split()[0]  # take first word only
        # Strip punctuation
        label = label.rstrip('.,;:')
        if label in _VALID_INTENTS:
            return QueryIntent(label)
        # LLM returned something unexpected — fall back to keyword rules
        return classify_intent(query)
    except Exception:
        return classify_intent(query)
