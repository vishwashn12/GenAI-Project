"""Full test output — writes to file to avoid terminal truncation."""
import urllib.request
import json

results = []

# Test 1: Chat - RAG chain
req = urllib.request.Request(
    'http://localhost:8000/chat',
    data=json.dumps({'query': 'What is the return policy for damaged products?'}).encode(),
    headers={'Content-Type': 'application/json'},
)
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read())
results.append({"test": "chat_rag", "data": data})

# Test 2: Health
resp2 = urllib.request.urlopen('http://localhost:8000/health')
data2 = json.loads(resp2.read())
results.append({"test": "health", "data": data2})

# Test 3: Feedback
req3 = urllib.request.Request(
    'http://localhost:8000/feedback',
    data=json.dumps({'query': 'test', 'rating': 5, 'comment': 'Great!'}).encode(),
    headers={'Content-Type': 'application/json'},
)
resp3 = urllib.request.urlopen(req3)
data3 = json.loads(resp3.read())
results.append({"test": "feedback", "data": data3})

# Write full output
with open("test_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("Results written to test_results.json")

# Print summary
for r in results:
    print(f"\n--- {r['test']} ---")
    d = r['data']
    if r['test'] == 'chat_rag':
        print(f"  intent: {d.get('intent')}")
        print(f"  mode: {d.get('mode')}")
        print(f"  latency: {d.get('latency')}s")
        print(f"  docs: {d.get('documents_retrieved')}")
        print(f"  sources: {len(d.get('sources', []))}")
        print(f"  sim_scores: {d.get('similarity_scores', [])[:3]}")
        print(f"  answer preview: {d.get('answer', '')[:200]}...")
    else:
        print(f"  {json.dumps(d)}")
