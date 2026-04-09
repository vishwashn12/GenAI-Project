"""
Live API test — fires the previously broken queries against the running backend
and checks intent classification + response quality.
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import requests
import json

BASE = "http://localhost:8000/chat"

tests = [
    # (label, query, order_id, expected_intent, what_good_response_contains)
    ("POLICY - refund timeframe",
     "How long does a refund take to process?", "",
     "policy_query",
     ["5-7", "business days", "refund", "process"]),

    ("POLICY - payment methods",
     "What payment methods do you accept?", "",
     "policy_query",
     ["credit", "boleto", "payment"]),

    ("DELIVERY - date passed (no ID)",
     "The estimated delivery date has passed", "",
     "delivery_issue",
     ["order ID", "provide", "late", "delay"]),

    ("DELIVERY - supposed to arrive (with ID)",
     "delivery was supposed to arrive last week but nothing",
     "203096f03d82e0dffbc41ebc2e2bcfb7",
     "delivery_issue",
     ["11", "late", "delivered"]),

    ("ORDER STATUS - purchase (no ID)",
     "What happened to my purchase?", "",
     "order_status",
     ["order ID", "status", "provide"]),

    ("GENERAL - greeting",
     "Hello, I need help with something", "",
     "general",
     ["help", "how can"]),

    ("GENERAL - thank you",
     "Thank you for your help", "",
     "general",
     ["welcome", "help", "anything"]),

    ("REFUND - policy no ID",
     "Can I get my money back?", "",
     "refund_request",
     ["7", "return", "refund", "policy"]),

    ("POLICY - chargeback",
     "Can I do a chargeback on my order?", "",
     "policy_query",
     ["refund", "policy", "platform"]),
]

print("=" * 70)
print("  LIVE BACKEND RESPONSE QUALITY TEST")
print("=" * 70)

results = {"pass": 0, "warn": 0, "fail": 0}

for label, query, order_id, expected_intent, keywords in tests:
    print(f"\n[TEST] {label}")
    print(f"  Query: {query}")
    print(f"  OrderID: {order_id or '(none)'}")
    try:
        resp = requests.post(BASE, json={
            "query": query,
            "order_id": order_id,
            "session_id": f"test_{label[:10]}"
        }, timeout=40)
        data = resp.json()

        intent_got = data.get("intent", "?")
        mode = data.get("mode", "?")
        answer = data.get("answer", "")

        intent_ok = intent_got == expected_intent
        kw_hits = [k for k in keywords if k.lower() in answer.lower()]
        kw_ok = len(kw_hits) >= max(1, len(keywords) // 2)

        print(f"  Intent : {intent_got:20s} {'[OK]' if intent_ok else '[WRONG - expected ' + expected_intent + ']'}")
        print(f"  Mode   : {mode}")
        print(f"  KW hits: {kw_hits} ({len(kw_hits)}/{len(keywords)})")
        print(f"  Answer : {answer[:220]}...")

        if intent_ok and kw_ok:
            print("  STATUS : [PASS]")
            results["pass"] += 1
        elif intent_ok or kw_ok:
            print("  STATUS : [WARN] - partial")
            results["warn"] += 1
        else:
            print("  STATUS : [FAIL]")
            results["fail"] += 1

    except Exception as e:
        print(f"  ERROR  : {e}")
        results["fail"] += 1

print("\n" + "=" * 70)
print(f"  SUMMARY: {results['pass']} PASS | {results['warn']} WARN | {results['fail']} FAIL")
print("=" * 70)
