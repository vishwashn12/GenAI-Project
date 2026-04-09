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
    # POLICY first — must come before REFUND_REQUEST to avoid keyword collisions
    QueryIntent.POLICY_QUERY: [
        'policy', 'can i return', 'am i eligible', 'how do i return',
        'return window', 'rules', 'consumer rights', 'CDC',
        'within how many days', 'what happens if', 'allowed to',
        'payment method', 'how do i pay', 'what payment', 'accept',
        'how long does', 'how long will', 'processing time', 'take to process',
        'chargeback', 'how many days', 'refund take', 'when will i get my refund',
        'how long does a refund',
    ],
    QueryIntent.REFUND_REQUEST: [
        'refund', 'money back', 'reimbur',
        'want my money', 'get a refund', 'request refund',
        'cancel my order', 'i want to cancel',
    ],
    QueryIntent.ORDER_STATUS: [
        'where is my order', 'order status', 'tracking', 'track my',
        'shipped', 'dispatch', 'has my order', 'check my order',
        'my purchase', 'happened to my', 'status of my order',
        'whr iz', 'ordr',
    ],
    QueryIntent.DELIVERY_ISSUE: [
        'late', 'delayed', 'not arrived', 'not received', 'overdue',
        'never came', 'still waiting', 'not delivered', 'missing',
        'package not', 'parcel not', "hasn't arrived", "haven't received",
        'supposed to arrive', 'estimated delivery', 'delivery date has passed',
        'expected delivery', 'weeks and', 'overdue',
        'laet', 'delayd', 'lte', 'delvery',
    ],
    QueryIntent.PRODUCT_ISSUE: [
        'broken', 'defective', 'damage', 'wrong item', 'wrong product',
        'not as described', 'different product', 'fake', 'counterfeit',
        'missing part', 'not working', 'arrived broken', 'item is broken',
        'product is', 'quality',
    ],
    QueryIntent.SELLER_ISSUE: [
        'seller', 'vendor', 'merchant', 'not responding', 'no reply',
        "seller won't", 'shop is', "store won't",
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

order_status    - Asking WHERE an order is, its current status, or shipping/tracking info. The order exists and is presumably on its way.
                  Examples: "Where is my order?", "Has my order shipped yet?", "Track my package"

delivery_issue  - The order is CONFIRMED LATE, significantly overdue, never arrived, or lost. Focus is on a delivery PROBLEM.
                  Examples: "My package never came", "It's been 3 weeks and nothing", "My order is late"

refund_request  - Wants money back, to cancel an order, or initiate a return for a refund.
                  Examples: "I want a refund", "Can I cancel and get my money back?", "How do I return this?"

product_issue   - The received item is broken, defective, wrong, damaged, counterfeit, or missing parts.
                  Examples: "The product is broken", "I got the wrong item", "It's not working at all"

policy_query    - Asking about platform RULES, policies, eligibility, timeframes, or payment methods. General factual policy questions.
                  Examples: "What is your return policy?", "How long does a refund take?", "What payment methods do you accept?", "Am I eligible for a return?"

seller_issue    - Complaint specifically about a SELLER/VENDOR behaviour (not just a late delivery).
                  Examples: "The seller is not responding", "The vendor sent a fake product", "Merchant won't honor the warranty"

general         - Greetings, thank-yous, vague questions, or anything that doesn't fit the above.
                  Examples: "Hello", "Thank you", "Can you help me?"

IMPORTANT DISTINCTIONS:
- "My order is late" = delivery_issue (NOT seller_issue — logistics delays are not seller complaints)
- "How long does a refund take?" = policy_query (NOT refund_request — they are asking about policy, not requesting one)
- "What payment methods do you accept?" = policy_query (NOT general)
- "I want to cancel my order" = refund_request

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
