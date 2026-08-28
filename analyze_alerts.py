import json, sys
from collections import Counter

data = json.loads(sys.stdin.read())
print(f'Total: {len(data)}')
print('Severity:', dict(Counter(a['rule']['security_severity_level'] for a in data)))
print('Rules:', dict(Counter(a['rule']['id'] for a in data)))
files = Counter(a['most_recent_instance']['location']['path'] for a in data)
for f, c in files.most_common(12):
    print(f'  {f}: {c}')
print()
for a in data:
    loc = a['most_recent_instance']['location']
    print(f"  {a['number']}:{a['rule']['id']} [{a['rule']['security_severity_level']}] {loc['path']}:{loc['start_line']}")
