import json

data = json.load(open('evaluation/results/eval_progress.json', encoding='utf-8'))
zero_count = 0
low_count = 0
total = 0
print('=== ANSWER RELEVANCY BREAKDOWN ===\n')
for d in data:
    s = d.get('scores', {})
    ar = s.get('answer_relevancy')
    if ar is None:
        continue
    total += 1
    tag = ''
    if ar <= 0.0:
        zero_count += 1
        tag = ' <<<< 0.0'
    elif ar < 0.3:
        low_count += 1
        tag = ' << LOW'
    has_id = 'YES' if d.get('order_id') else 'NO '
    print(f'  Q{d["id"]:2d} | AR={ar:6.4f} | mode={d["mode"]:10s} | order_id={has_id} | {d["question"][:55]}{tag}')

print(f'\nTotal scored: {total}')
print(f'Exact 0.0:    {zero_count} ({zero_count/total*100:.0f}%)')
print(f'Below 0.3:    {low_count} ({low_count/total*100:.0f}%)')
print(f'Combined:     {zero_count+low_count} ({(zero_count+low_count)/total*100:.0f}%)')

# Now show the actual answers for the 0.0 ones
print('\n\n=== ANSWERS FOR 0.0 RELEVANCY QUERIES ===\n')
for d in data:
    s = d.get('scores', {})
    ar = s.get('answer_relevancy')
    if ar is not None and ar <= 0.0:
        print(f'--- Q{d["id"]}: {d["question"]} ---')
        print(f'Mode: {d["mode"]} | Order ID: {d.get("order_id", "none")}')
        print(f'Answer (first 300 chars): {d["answer"][:300]}')
        print()
