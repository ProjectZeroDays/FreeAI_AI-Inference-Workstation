import re

# Read remote backend
with open('dashboard/backend.py', 'r', encoding='utf-8') as f:
    remote = f.read()

# Read our backend
with open('dashboard/backend_ours.py', 'r', encoding='utf-8') as f:
    ours = f.read()

# Extract route patterns from both
def extract_routes(content):
    return set(re.findall(r'@app\.route\(["\']([^"\']+)["\']', content))

our_routes = extract_routes(ours)
remote_routes = extract_routes(remote)

# Find routes only in ours
new_routes = our_routes - remote_routes
print(f'Total routes in ours: {len(our_routes)}')
print(f'Total routes in remote: {len(remote_routes)}')
print(f'New routes to add: {len(new_routes)}')
for r in sorted(new_routes):
    print(f'  {r}')
