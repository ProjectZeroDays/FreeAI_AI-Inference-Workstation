import re

with open('dashboard/backend.py', 'r', encoding='utf-8') as f:
    ours = f.read()
with open('dashboard/backend_remote.py', 'r', encoding='utf-8') as f:
    remote = f.read()

def extract_routes(content):
    return set(re.findall(r'@app\.route\(["\']([^"\']+)["\']', content))

our_routes = extract_routes(ours)
remote_routes = extract_routes(remote)

missing = remote_routes - our_routes
extra = our_routes - remote_routes

print(f'Our routes: {len(our_routes)}')
print(f'Remote routes: {len(remote_routes)}')
print(f'Missing from ours: {len(missing)}')
print(f'Extra in ours: {len(extra)}')
print()
print('Routes in remote but missing from ours:')
for r in sorted(missing):
    print(f'  {r}')
print()
print('Routes in ours but not in remote (new):')
for r in sorted(extra):
    print(f'  {r}')
