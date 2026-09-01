---
name: quantum-fullstack-dev
description: Builds complete full-stack features for the Quantum C2 framework — new pages, API endpoints, data models, and navigation. Covers the full workflow from frontend page creation through backend routing, React integration, and commit. Use when adding new modules, dashboards, or tools to the Quantum platform.
---

# Quantum Full-Stack Developer

End-to-end feature development for the Quantum C2 framework.

## Directory Structure

```
Quantum/
├── backend/
│   └── app/
│       ├── gateways/          # Business logic / data models
│       │   └── <feature>/
│       │       └── <feature>_gateway.py
│       └── routers/           # FastAPI route handlers
│           └── <feature>.py
├── frontend/
│   └── src/
│       ├── pages/             # React page components
│       │   └── <Feature>Page.jsx
│       ├── router/
│       │   └── routes.jsx     # Route registration
│       └── components/
│           └── layout/
│               └── Sidebar.jsx # Navigation entries
└── tests/
    └── unit/                  # Unit tests
```

## Development Workflow

### Step 1: Backend Gateway (Data Models + Logic)

```python
# backend/app/gateways/<feature>/<feature>_gateway.py
"""
Quantum C2 — [Feature Name]
"""
import logging
import secrets
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class SomeEnum(str, Enum):
    VALUE_A = "value_a"
    VALUE_B = "value_b"

@dataclass
class SomeModel:
    id: str
    name: str
    # ... fields ...

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            # ... serializable fields ...
        }

class SomeManager:
    def __init__(self):
        self._items: Dict[str, SomeModel] = {}

    def get_all(self) -> List[Dict]:
        return [item.to_dict() for item in self._items.values()]

    def create(self, name: str) -> Dict:
        item_id = secrets.token_hex(8)
        item = SomeModel(id=item_id, name=name)
        self._items[item_id] = item
        return item.to_dict()

# Global singleton
_manager: Optional[SomeManager] = None

def get_manager() -> SomeManager:
    global _manager
    if _manager is None:
        _manager = SomeManager()
    return _manager
```

### Step 2: FastAPI Router (HTTP Endpoints)

```python
# backend/app/routers/<feature>.py
"""
Quantum C2 — [Feature] API Router
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.gateways.<feature>.<feature>_gateway import get_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/<feature>", tags=["[Feature]"])

class CreateRequest(BaseModel):
    name: str

@router.get("")
async def list_items():
    mgr = get_manager()
    return {"items": mgr.get_all(), "count": len(mgr._items)}

@router.post("")
async def create_item(req: CreateRequest):
    mgr = get_manager()
    return mgr.create(req.name)

@router.get("/stats")
async def stats():
    mgr = get_manager()
    return {"total": len(mgr._items)}
```

### Step 3: Register Router in Main

```python
# backend/app/main.py — add near other router includes
from app.routers.<feature> import router as <feature>_router
app.include_router(<feature>_router)
```

### Step 4: Frontend Page Component

```jsx
// frontend/src/pages/<Feature>Page.jsx
import React, { useState, useEffect, useCallback } from 'react';

const API = '/api/<feature>';

export default function <Feature>Page() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const r = await fetch(API);
      const d = await r.json();
      setItems(d.items || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) {
    return (
      <div className="q-page-shell" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div style={{ color: 'var(--muted)', fontFamily: 'monospace', fontSize: 13 }}>
          <span style={{ animation: 'pulse 1.2s infinite', marginRight: 10 }}>◆</span>LOADING...
        </div>
      </div>
    );
  }

  return (
    <div className="q-page-shell">
      <div className="q-page-header">
        <div>
          <div className="q-eyebrow">Section</div>
          <h1>Feature Title</h1>
          <p>Description of the feature.</p>
        </div>
      </div>

      <div className="q-kpi-grid">
        <div className="q-kpi"><span>Total</span><strong>{items.length}</strong><small>items</small></div>
      </div>

      <div className="dashboard-grid">
        <section className="panel panel--system" style={{ gridColumn: 'span 2' }}>
          <div className="panel-title"><div>Items ({items.length})</div></div>
          <div className="module-preview">
            {items.length === 0 ? (
              <div style={{ color: 'var(--muted)', padding: 16, textAlign: 'center', fontSize: 12 }}>No items yet.</div>
            ) : items.map(item => (
              <div key={item.id} style={{ padding: '10px 12px', borderBottom: '1px solid var(--border)' }}>
                <span style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--light)' }}>{item.name}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
```

### Step 5: Register Route

```jsx
// frontend/src/router/routes.jsx
const <Feature>Page = lazy(() => import('../pages/<Feature>Page'));
// ...
<Route path="/<feature>" element={<<Feature>Page />} />
```

### Step 6: Add to Sidebar

```jsx
// frontend/src/components/layout/Sidebar.jsx
// Add inside the appropriate SECTIONS array:
{ label: "Feature Title", to: "/<feature>" },
```

### Step 7: Verify & Commit

```bash
# Backend syntax
python -m py_compile backend/app/gateways/<feature>/<feature>_gateway.py
python -m py_compile backend/app/routers/<feature>.py

# Frontend build
cd frontend && npx vite build

# Run tests
python -m pytest tests/unit/ -q

# Commit
git add -A
git commit -m "Add <Feature> module"
git push origin main
```

## UI Conventions

### Card Styles
```jsx
<section className="panel panel--system">        {/* Blue accent */}
<section className="panel panel--intel">         {/* Purple accent */}
<section className="panel panel--defense">       {/* Green accent */}
<section className="panel panel--offense">       {/* Red accent */}
```

### KPI Grid
```jsx
<div className="q-kpi-grid">
  <div className="q-kpi"><span>Label</span><strong>Value</strong><small>unit</small></div>
</div>
```

### Buttons
```jsx
<button className="module-btn" style={{ background: 'rgba(0,229,255,0.15)', color: '#00e5ff' }}>
  Action
</button>
```

### Colors
| Variable | Hex | Use |
|----------|-----|-----|
| `--accent` | `#00e5ff` | Primary actions |
| `--danger` | `#ff4b6b` | Critical/danger |
| `--success` | `#6ef0a3` | Success/online |
| `--warn` | `#ffd36b` | Warnings/medium |
| `--muted` | `#7fa2b8` | Labels/descriptions |
| `--light` | `#cfefff` | Primary text |
| `--panel` | `#030e1e` | Panel backgrounds |
| `--border` | `#103347` | Borders |

## Common Patterns

### Simulated Data (for demo/prototype)
```python
import random
item.id = f"ITEM-{secrets.token_hex(4).upper()}"
item.value = random.choice([True, False])
```

### Async Operations
```jsx
const [executing, setExecuting] = useState(false);
const handleAction = useCallback(async () => {
  setExecuting(true);
  try {
    const r = await fetch(API + '/action', { method: 'POST' });
    const d = await r.json();
    // handle result
  } catch (e) { /* error handling */ }
  finally { setExecuting(false); }
}, []);
```

### Auto-refresh
```jsx
useEffect(() => {
  const iv = setInterval(fetchData, 15000);
  return () => clearInterval(iv);
}, [fetchData]);
```

### Severity Coloring
```jsx
const severityColor = (s) => ({
  critical: '#ff4b6b',
  high: '#ff8c4b',
  medium: '#ffd36b',
  low: '#6ef0a3',
  info: '#00e5ff'
}[s] || '#7fa2b8');
```

## Error Handling

### 500 on API Call
- Check enum values match
- Check dataclass `to_dict()` includes all referenced fields
- Check router imports gateway correctly

### 404 on API Call
- Verify router is included in `main.py`
- Verify prefix matches frontend `API` constant
- Check for typos in route path

### Build Failure
- Check JSX syntax (self-closing tags, bracket matching)
- Verify lazy import path is correct
- Check for missing React imports

## Git Workflow

```bash
git add backend/app/gateways/<feature>/
git add backend/app/routers/<feature>.py
git add frontend/src/pages/<Feature>Page.jsx
git add frontend/src/router/routes.jsx
git add frontend/src/components/layout/Sidebar.jsx
git commit -m "Add <Feature> module"
git push origin main
```
