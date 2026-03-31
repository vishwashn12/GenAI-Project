"""Quick test of the /chat endpoint."""
import urllib.request
import json

# Test 1: Chat - RAG chain (policy query)
print("=" * 60)
print("TEST 1: Policy query (RAG chain)")
print("=" * 60)
req = urllib.request.Request(
    'http://localhost:8000/chat',
    data=json.dumps({'query': 'What is the return policy for damaged products?'}).encode(),
    headers={'Content-Type': 'application/json'},
)
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read())

print(f"Response keys: {list(data.keys())}")
print(f"\nAnswer (first 300 chars):\n{data['answer'][:300]}")
print(f"\nIntent: {data['intent']}")
print(f"Mode: {data['mode']}")
print(f"Latency: {data['latency']}s")
print(f"Documents retrieved: {data['documents_retrieved']}")
print(f"Sources count: {len(data.get('sources', []))}")
print(f"Similarity scores: {data.get('similarity_scores', [])[:3]}")
print(f"Reasoning: {data.get('reasoning', {})}")

# Test 2: Health
print("\n" + "=" * 60)
print("TEST 2: Health check")
print("=" * 60)
resp2 = urllib.request.urlopen('http://localhost:8000/health')
print(json.loads(resp2.read()))

# Test 3: Feedback
print("\n" + "=" * 60)
print("TEST 3: Feedback")
print("=" * 60)
req3 = urllib.request.Request(
    'http://localhost:8000/feedback',
    data=json.dumps({
        'query': 'test',
        'rating': 5,
        'comment': 'Great response!',
    }).encode(),
    headers={'Content-Type': 'application/json'},
)
resp3 = urllib.request.urlopen(req3)
print(json.loads(resp3.read()))

print("\n✓ ALL TESTS PASSED")
