---
name: update-protocol
description: Autonomous update protocol for Quantum C2. Use when the user types [UPDATE] or asks to update, extend, or enhance the Quantum C2 framework.
trigger_keywords: UPDATE, update, enhance, implement suggestions, update protocol, generate improvements
---

# Quantum C2
**Opencode Skill — Autonomous Update Protocol**

## Description

Use when the user types `[UPDATE]` or asks to update, extend, or enhance the Quantum C2 framework. This skill orchestrates the full update lifecycle: generation of suggestions, implementation, testing, documentation, and deployment.

## Trigger Keywords

- `[UPDATE]`
- "update Quantum C2"
- "enhance Quantum"
- "implement suggestions"
- "run update protocol"
- "generate improvements"

---

## Workflow

### Step 1: Generate Suggestions

Generate suggestions across ALL categories:

1. **Enhancements**: New features, capabilities, improvements
2. **Changes**: Bug fixes, refactoring, optimization
3. **Configurations**: Settings, environment, deployment
4. **Plugins**: New plugin types, marketplace features
5. **Extensions**: Third-party integrations, API connections
6. **Skills**: New AI agent skills, operator workflows
7. **Settings**: Security, performance, monitoring
8. **Web Cards**: Dashboard widgets, real-time panels
9. **Workflows**: Automation, orchestration, lifecycle
10. **Jobs**: Scheduled tasks, background workers
11. **AI Agents**: New agent types, capabilities, behaviors

Save all suggestions to:
```
docs/guides/SUGGESTED_IMPLEMENTATIONS.md
```

### Step 2: Implement Suggestions

For each suggestion:
1. Analyze requirements and dependencies
2. Design implementation approach
3. Write backend service/router
4. Write frontend component/page
5. Write integration tests
6. Update configuration as needed
7. Verify no breaking changes

### Step 3: Check Backend Imports

After implementing new code, verify import integrity:

```bash
cd backend
python -c "
import sys
sys.path.insert(0, '.')
try:
    import app.main
    print('✅ Main imports OK')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
```

Check for circular imports:
```bash
python -c "
import ast
import sys
from pathlib import Path

def check_circular_imports(file_path):
    '''Detect circular import dependencies.'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
    except Exception as e:
        return []

# Check all Python files
backend_dir = Path('backend/app')
all_imports = {}
for py_file in backend_dir.rglob('*.py'):
    if '__pycache__' in str(py_file):
        continue
    all_imports[str(py_file)] = check_circular_imports(py_file)

# Report any problematic imports
for file, imports in all_imports.items():
    for imp in imports:
        if 'app' in imp and file.endswith('.py'):
            print(f'  {file}: {imp}')
print('✅ Circular import check complete')
"
```

Verify backend functionality:
```bash
python -m pytest tests/ -q --tb=short
```

### Step 4: Verify WebSocket Connections

Test WebSocket connectivity after changes:

```bash
python -c "
import asyncio
import websockets
import json

async def test_websocket():
    try:
        uri = 'ws://localhost:8000/ws'
        async with websockets.connect(uri, timeout=5) as ws:
            await ws.send(json.dumps({'event': 'ping'}))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f'✅ WebSocket OK: {response}')
    except Exception as e:
        print(f'❌ WebSocket error: {e}')

asyncio.run(test_websocket())
"
```

Test WebSocket event handlers:
```bash
# Check WebSocket router is registered
grep -r "websocket" backend/app/routers/ || echo "No WebSocket routers found"
grep -r "@app.websocket" backend/app/ || echo "No WebSocket decorators found"
```

### Step 5: Validate Database Migrations

Ensure migrations are current and apply correctly:

```bash
cd backend
python -m alembic check
python -m alembic upgrade head
python -m pytest tests/test_database.py -v
```

Validate no schema conflicts:
```bash
python -c "
from sqlalchemy import create_engine
from sqlalchemy import inspect
engine = create_engine('sqlite:///./quantum.db')
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'✅ Database OK: {len(tables)} tables')
for table in tables[:10]:
    cols = inspector.get_columns(table)
    print(f'  {table}: {len(cols)} columns')
"
```

### Step 6: Create New Tests

For all new features:
- Unit tests (pytest, 80%+ coverage target)
- Integration tests (API endpoints, workflows)
- Security tests (authentication, authorization)
- Performance tests (load, stress)

Run tests:
```bash
cd backend
python -m pytest tests/ -v
```

### Step 7: Mobile/Desktop UI Sync

Ensure all frontend changes are mirrored between desktop and mobile:

#### Sync React Components

```bash
# Check for component differences
diff -r frontend/src/components/ mobile/www/components/ 2>/dev/null || \
    echo "Mobile components directory not found — manual sync required"

# Identify components that need mirroring
find frontend/src -name "*.tsx" -o -name "*.jsx" | while read f; do
    component=$(basename "$f" | sed 's/\.[tj]sx//')
    if [ ! -f "mobile/www/components/${component}.tsx" ] && \
       [ ! -f "mobile/www/components/${component}.jsx" ]; then
        echo "⚠️  Mirror to mobile: $f"
    fi
done
```

#### Update Mobile App with New API Endpoints

```bash
# Check mobile app API client configuration
grep -r "API_BASE_URL\|apiEndpoint\|baseUrl" mobile/ 2>/dev/null || \
    echo "Mobile API config not found"

# Verify mobile app can reach new endpoints
for endpoint in $(grep -r "router\." backend/app/routers/ | grep -o '"[^"]*"' | sort -u); do
    echo "Checking endpoint: $endpoint"
done
```

#### Ensure PWA Manifest is Current

```bash
# Update service worker and manifest
cat > mobile/www/manifest.json << 'EOF'
{
  "name": "Quantum C2 Mobile",
  "short_name": "Quantum",
  "description": "Enterprise C2 Framework - Mobile",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0a0a0f",
  "theme_color": "#00ff88",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
EOF

# Update service worker
cat > mobile/www/service-worker.js << 'EOF'
const CACHE_NAME = 'quantum-c2-mobile-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  );
});
EOF
```

#### Verify Responsive Design

```bash
# Check responsive breakpoints in styles
grep -r "media.*query\|@media\|responsive" frontend/src/ | head -20
grep -r "media.*query\|@media\|responsive" mobile/ 2>/dev/null | head -20

# Verify mobile-first CSS approach
find frontend/src -name "*.css" -o -name "*.scss" | while read f; do
    if grep -q "max-width.*768\|@media.*max-width" "$f"; then
        echo "✅ Responsive: $f"
    else
        echo "⚠️  Check responsive: $f"
    fi
done
```

#### Update Mobile-Specific Stylesheets

```bash
# Create or update mobile stylesheet
cat > mobile/www/css/mobile.css << 'EOF'
/* Mobile-specific styles for Quantum C2 */
@media (max-width: 768px) {
  .quantum-sidebar {
    display: none;
  }
  .quantum-main {
    margin-left: 0;
    padding: 1rem;
  }
  .quantum-nav {
    flex-direction: column;
  }
  .quantum-nav-item {
    width: 100%;
    padding: 0.75rem 1rem;
  }
  .quantum-card {
    margin-bottom: 1rem;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .quantum-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Touch-friendly interactions */
@media (hover: none) and (pointer: coarse) {
  button, a {
    min-height: 44px;
    min-width: 44px;
  }
  .quantum-input {
    font-size: 16px; /* Prevents iOS zoom */
  }
}
EOF

# Ensure mobile build includes new styles
grep -q "mobile.css" mobile/www/index.html || \
    echo '<link rel="stylesheet" href="css/mobile.css">' >> mobile/www/index.html
```

### Step 8: Test and Debug

1. Run full test suite
2. Verify backend health:
   ```bash
   curl http://localhost:8000/api/health
   ```
3. Verify frontend build:
   ```bash
   cd frontend && npm run build
   ```
4. Check for linting errors:
   ```bash
   ruff check backend/app/
   bandit -r backend/app/ -ll
   ```
5. Verify mobile build:
   ```bash
   cd mobile && npx cap build android 2>/dev/null || echo "Mobile build skipped"
   ```
6. Fix any issues found

### Step 9: Update file_structure.txt

Regenerate the file structure documentation:
```bash
# Generate file structure
tree -L 3 -I 'node_modules|venv|.git|__pycache__|*.pyc' > file_structure.txt
```

### Step 10: Update All Documentation

Update the following files as needed:
- `README.md` — Features, API endpoints, status
- `docs/getting-started/wiki.md` — New sections
- `docs/MASTER_IMPLEMENTATION_PROTOCOL_v3.md` — Protocol updates
- `docs/CHANGELOG.md` — Version history
- `docs/reports/app-report.md` — Metrics update
- `docs/production/readiness-report.md` — Readiness status

### Step 11: Commit and Push

```bash
git add -A
git commit -m "feat: Quantum C2 update - [feature descriptions]"
git push origin main
```

### Step 12: Record Output Locations

Save locations of all output files for future reference:

| File Type | Location |
|-----------|----------|
| Suggestions | `docs/guides/SUGGESTED_IMPLEMENTATIONS.md` |
| Features | `docs/getting-started/FEATURES.md` |
| Protocol | `docs/MASTER_IMPLEMENTATION_PROTOCOL_v3.md` |
| Changelog | `docs/CHANGELOG.md` |
| App Report | `docs/reports/app-report.md` |
| Readiness | `docs/production/readiness-report.md` |
| Wiki | `docs/getting-started/wiki.md` |
| File Structure | `file_structure.txt` |
| Mobile UI Sync | `mobile/www/manifest.json`, `mobile/www/service-worker.js` |
| Mobile Styles | `mobile/www/css/mobile.css` |

---

## Categories for Suggestions

### Security
- New authentication methods
- Encryption enhancements
- Audit logging improvements
- Penetration testing features
- Threat detection capabilities

### Features
- New API endpoints
- Dashboard widgets
- Integration capabilities
- Automation workflows
- Reporting features

### Configuration
- Environment variables
- Deployment options
- Scaling settings
- Performance tuning
- Security policies

### Plugins
- Plugin types
- Plugin lifecycle
- Marketplace features
- Security scanning
- Version management

### Extensions
- Third-party integrations
- API connections
- Data exporters
- Webhook handlers
- Protocol adapters

### Skills
- AI agent skills
- Operator workflows
- Automation scripts
- Response templates
- Playbook definitions

### Settings
- UI customization
- Notification preferences
- Security settings
- Performance options
- Integration configs

### Web Cards
- Dashboard panels
- Real-time widgets
- Data visualizations
- Alert displays
- Status indicators

### Workflows
- Automation sequences
- Trigger conditions
- Action chains
- State management
- Error handling

### Jobs
- Scheduled tasks
- Background workers
- Batch processors
- Data sync operations
- Cleanup routines

### AI Agents
- New agent types
- Behavior configurations
- Skill assignments
- Team compositions
- Orchestration rules

---

## Output Format

After each update cycle, provide a summary:

```
[UPDATE] Complete

Suggestions Generated: {N}
Implemented: {N}
Tests Added: {N}
Tests Passing: {N}
Files Updated: {N}
Documentation Updated: {N}
Production Readiness: {X}/100

Backend Health:
  - Import Check: ✅/❌
  - Circular Imports: ✅/❌
  - WebSocket: ✅/❌
  - DB Migrations: ✅/❌

Mobile/Desktop Sync:
  - React Components Synced: ✅/❌
  - API Endpoints Updated: ✅/❌
  - PWA Manifest: ✅/❌
  - Responsive Design: ✅/❌
  - Mobile Styles: ✅/❌

Output Files:
- docs/guides/SUGGESTED_IMPLEMENTATIONS.md
- docs/getting-started/FEATURES.md
- docs/MASTER_IMPLEMENTATION_PROTOCOL_v3.md
- docs/CHANGELOG.md
- docs/reports/app-report.md
- docs/production/readiness-report.md
- docs/getting-started/wiki.md
- file_structure.txt
- mobile/www/manifest.json
- mobile/www/css/mobile.css
```

---

## Constraints

- Do NOT modify existing working code without justification
- All new features MUST include tests
- All changes MUST maintain backward compatibility
- Security must NEVER be compromised for features
- Documentation MUST be updated with every change
- Commit messages MUST follow conventional commits format
- Mobile/Desktop UI changes MUST be synced
- Backend imports MUST work after changes
- WebSocket connections MUST be verified
- Database migrations MUST be validated

---

## Success Criteria

- [ ] All suggestions documented
- [ ] All implemented features tested
- [ ] Test coverage >= 90%
- [ ] No linting or security errors
- [ ] All documentation updated
- [ ] Changes committed and pushed
- [ ] Production readiness maintained or improved
- [ ] Backend imports working (no errors)
- [ ] No circular imports detected
- [ ] WebSocket connections verified
- [ ] Database migrations validated
- [ ] Mobile/Desktop UI synced
- [ ] PWA manifest current
- [ ] Responsive design verified
- [ ] Mobile stylesheets updated

---

*Skill Version: 2.0*
*Last Updated: 2026-08-16*
