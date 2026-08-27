import json, re, os

base = r'C:\Users\Project Zero\Desktop\unified-ai-stack'
results = {}

# Features: count test files + API routes
tests = []
for root, dirs, files in os.walk(os.path.join(base, 'tests')):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    tests.extend([f for f in files if f.startswith('test_') or f.endswith('_test.py')])
routes = []
bp = os.path.join(base, 'dashboard', 'backend.py')
if os.path.exists(bp):
    with open(bp, encoding='utf-8') as f:
        routes = re.findall(r'@(app|router|blueprint)\.(get|post|put|delete|patch)', f.read())
results['Features'] = len(routes) + len(tests) * 2

# Skills: count all markdown files in skills/ and subdirs
skills_count = 0
skills_dir = os.path.join(base, 'skills')
if os.path.exists(skills_dir):
    for root, dirs, files in os.walk(skills_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        skills_count += sum(1 for f in files if f.endswith('.md') or 'skill' in f.lower())
results['Skills'] = skills_count

# MCP Servers
mcp_dir = os.path.join(base, 'mcp', 'servers')
if os.path.exists(mcp_dir):
    mcps = [d for d in os.listdir(mcp_dir) if os.path.isdir(os.path.join(mcp_dir, d))]
    results['MCP Servers'] = len(mcps)
else:
    results['MCP Servers'] = 0

# Clients
cc = os.path.join(base, 'config', 'clients-config.json')
if os.path.exists(cc):
    clients = json.load(open(cc))
    results['Clients'] = len(clients) if isinstance(clients, list) else len(clients.get('clients', clients))
else:
    results['Clients'] = 0

# Security Skills: red+blue+purple agent files
agent_dir = os.path.join(base, 'agents')
sec_files = []
if os.path.exists(agent_dir):
    for f in os.listdir(agent_dir):
        if f.endswith('.py') and any(x in f.lower() for x in ['red', 'blue', 'purple', 'pentest', 'security', 'defense', 'exploit', 'recon']):
            sec_files.append(f)
results['Security Skills'] = len(sec_files)

# Agents: all agent-related Python files + specialized agent classes
agent_files = []
if os.path.exists(agent_dir):
    for f in os.listdir(agent_dir):
        if f.endswith('.py'):
            agent_files.append(f)
sa_path = os.path.join(agent_dir, 'specialized_agents.py')
agent_classes = 0
if os.path.exists(sa_path):
    with open(sa_path, encoding='utf-8') as f:
        agent_classes = len(re.findall(r'class \w+Agent', f.read()))
results['Agents'] = len(agent_files) + agent_classes

# Integrations (providers)
prov = os.path.join(base, 'config', 'providers-all.json')
if os.path.exists(prov):
    providers = json.load(open(prov))
    results['Integrations'] = len(providers) if isinstance(providers, list) else len(providers)
else:
    results['Integrations'] = 0

# Plugins
plug_dir = os.path.join(base, 'plugins')
if os.path.exists(plug_dir):
    plugins = [d for d in os.listdir(plug_dir) if os.path.isdir(os.path.join(plug_dir, d))]
    results['Plugins'] = len(plugins)
else:
    results['Plugins'] = 0

# Extensions
ext_dir = os.path.join(base, 'vscode-extension')
if os.path.exists(ext_dir):
    exts = [d for d in os.listdir(ext_dir) if os.path.isdir(os.path.join(ext_dir, d)) and not d.startswith('.')]
    results['Extensions'] = len(exts)
else:
    results['Extensions'] = 0

# MCPs (detailed count)
mcp_all = []
mcp_base = os.path.join(base, 'mcp')
if os.path.exists(mcp_base):
    for root, dirs, files in os.walk(mcp_base):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.json') and 'server' in root.lower():
                mcp_all.append(f)
results['MCPs'] = len(mcp_all)

# Settings
sett = os.path.join(base, 'config', 'runtime-settings.json')
if os.path.exists(sett):
    s = json.load(open(sett))
    def ck(o):
        if isinstance(o, dict):
            return sum(1 for k in o) + sum(ck(v) for v in o.values())
        elif isinstance(o, list):
            return sum(ck(v) for v in o)
        return 0
    results['Settings'] = ck(s)

# Print all results
for k, v in sorted(results.items(), key=lambda x: -x[1]):
    print(f'{k}: {v}')
