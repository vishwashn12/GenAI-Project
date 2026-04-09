"""
Quick sanity test for intent classifier fixes.
Tests keyword fallback (no LLM needed) against previously broken queries.
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import sys
sys.path.insert(0, r'c:\Users\User\Documents\GenAI\backend')

from rag.intent import classify_intent

previously_broken = [
    # (query, expected_intent, old_wrong_intent)
    ("How long does a refund take to process?", "policy_query", "was->general/refund_request"),
    ("What payment methods do you accept?",     "policy_query", "was->general"),
    ("Can I do a chargeback on my order?",       "policy_query", "was->general"),
    ("My order is late, it hasn't arrived yet",  "delivery_issue", "was->seller_issue"),
    ("delivery was supposed to arrive last week","delivery_issue", "was->seller_issue"),
    ("The estimated delivery date has passed",   "delivery_issue", "was->seller_issue"),
    ("What happened to my purchase?",            "order_status",  "was->seller_issue"),
    ("What is your return policy?",              "policy_query",  "check"),
    ("How many days do I have to return?",       "policy_query",  "check"),
    ("Am I eligible for a return on my order?",  "policy_query",  "check"),
    ("Thank you for your help",                  "general",       "check"),
    ("Hello, I need help with something",        "general",       "check"),
    ("Can you help me with my problem?",         "general",       "check"),
]

print("=== KEYWORD FALLBACK CLASSIFIER SANITY TEST ===\n")
passed = 0
failed = 0
for query, expected, note in previously_broken:
    got = classify_intent(query)
    ok = got.value == expected
    status = "[PASS]" if ok else "[FAIL]"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"{status} | Expected: {expected:20s} | Got: {got.value:20s} | {query[:50]}")
    if not ok:
        print(f"       Note: {note}")

print(f"\nResults: {passed}/{len(previously_broken)} passed ({passed/len(previously_broken)*100:.0f}%)")
