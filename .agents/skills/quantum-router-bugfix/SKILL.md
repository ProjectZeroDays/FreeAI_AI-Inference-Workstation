---
name: quantum-router-bugfix
description: Diagnoses and fixes routing errors in the Quantum C2 framework — missing enum values, 500 errors on API endpoints, FastAPI type mismatches, and React build failures. Use when a feature crashes with 500 errors, when new code references undefined enums, or when frontend builds fail after adding new pages.
---

# Quantum Router Bugfix

Diagnoses and repairs routing/endpoint failures in the Quantum C2 framework.

## Common Failure Modes

### 1. Missing Enum Value (500 on API call)

**Symptom**: `assess_device` or similar endpoint returns 500. Check gateway code for `RouterVulnType` references.

**Root cause**: A vulnerability record or code path references an enum value not defined in the enum class.

**Fix**:
```python
# In router_gateway.py, add missing value to RouterVulnType
class RouterVulnType(str, Enum):
    # ... existing values ...
    INJECTION = "injection"  # Add missing enum
```

### 2. FastAPI Router Not Registered

**Symptom**: 404 on `/api/router-exploit/*` endpoints.

**Root cause**: Router not imported/registered in `app/main.py`.

**Fix**:
```python
# In main.py or app initialization
from app.routers.router_exploit import router as router_exploit_router
app.include_router(router_exploit_router)
```

### 3. Pydantic Model Mismatch

**Symptom**: 422 Validation Error on POST requests.

**Root cause**: Request body schema doesn't match Pydantic model.

**Fix**: Verify `CustomExploitRequest` and `DisclosureRequest` models match frontend payload.

### 4. React Build Failure

**Symptom**: `npx vite build` fails with import errors.

**Root cause**: Page component not exported, route not added, or syntax error in JSX.

**Fix**:
```bash
# Check for syntax errors
python -m py_compile path/to/file.py

# Check frontend build
cd frontend && npx vite build 2>&1 | tail -20
```

## Diagnostic Workflow

```bash
# Step 1: Reproduce the error
curl -s -X POST https://localhost:4433/api/router-exploit/assess/DEVICE_ID \
  -H "Content-Type: application/json"

# Step 2: Check backend logs
# Look for: AttributeError, KeyError, ValueError

# Step 3: Verify enum completeness
python -c "
from app.gateways.router_exploit.router_gateway import RouterVulnType
print([e.value for e in RouterVulnType])
"

# Step 4: Check all vulnerability records reference valid enums
python -c "
from app.gateways.router_exploit.router_gateway import get_router_vuln_db
db = get_router_vuln_db()
for vuln in db.VULNERABILITIES.values():
    try:
        t = RouterVulnType(vuln['type'])
    except ValueError as e:
        print(f'INVALID type for {vuln[\"cve\"]}: {vuln[\"type\"]}')
"

# Step 5: Rebuild frontend
cd frontend && npx vite build
```

## Fix Patterns

### Adding Missing Enum Value

```python
# File: backend/app/gateways/router_exploit/router_gateway.py
class RouterVulnType(str, Enum):
    # existing values...
    INJECTION = "injection"  # NEW
```

### Adding New API Endpoint

```python
# File: backend/app/routers/router_exploit.py
from pydantic import BaseModel

class NewRequest(BaseModel):
    field1: str
    field2: int = 0

@router.post("/new/endpoint")
async def new_endpoint(req: NewRequest):
    mgr = get_router_exploit_manager()
    return mgr.new_method(req.field1, req.field2)
```

### Adding Frontend Page

```jsx
// File: frontend/src/pages/NewPage.jsx
export default function NewPage() {
  return (
    <div className="q-page-shell">
      <header className="q-page-header">
        <div>
          <div className="q-eyebrow">Section</div>
          <h1>Page Title</h1>
          <p>Description.</p>
        </div>
      </header>
      {/* Content */}
    </div>
  );
}
```

```jsx
// File: frontend/src/router/routes.jsx
const NewPage = lazy(() => import('../pages/NewPage'));
// ...
<Route path="/new-page" element={<NewPage />} />
```

```jsx
// File: frontend/src/components/layout/Sidebar.jsx
{ label: "New Page", to: "/new-page" },
```

## Verification Checklist

- [ ] Backend compiles: `python -m py_compile <file>.py`
- [ ] Frontend builds: `npx vite build` exits 0
- [ ] API endpoint responds: `curl` returns JSON, not 500
- [ ] Enum values match all references
- [ ] New routes registered in routes.jsx
- [ ] New navigation item added to Sidebar.jsx
- [ ] Tests pass: `python -m pytest tests/unit/ -q`
