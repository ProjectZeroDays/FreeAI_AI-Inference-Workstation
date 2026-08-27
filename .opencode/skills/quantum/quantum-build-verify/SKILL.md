---
name: quantum-build-verify
description: Verifies build integrity across the Quantum C2 framework — Python syntax checks, FastAPI router validation, React frontend builds, and test suite execution. Use after any code change to ensure nothing is broken before committing.
---

# Quantum Build & Verify

Verifies full-stack build integrity for the Quantum C2 framework.

## Quick Verify (All-in-One)

```bash
# Run from project root
cd "C:\Users\Project Zero\Desktop\Stuff\Code Forge"

# 1. Backend syntax check
python -m py_compile backend/app/gateways/router_exploit/router_gateway.py
python -m py_compile backend/app/routers/router_exploit.py

# 2. Frontend build
cd frontend && npx vite build 2>&1 | Select-Object -Last 5

# 3. Run tests
cd .. && python -m pytest tests/unit/ -q
```

## Python Syntax Check

```bash
# Single file
python -m py_compile path/to/file.py

# All backend files
python -m py_compile backend/app/gateways/**/*.py backend/app/routers/**/*.py

# Enum consistency check (catches missing enum values)
python -c "
from app.gateways.router_exploit.router_gateway import RouterVulnType, get_router_vuln_db
db = get_router_vuln_db()
for vuln in db.VULNERABILITIES.values():
    try:
        RouterVulnType(vuln['type'])
    except ValueError:
        print(f'MISSING enum: {vuln[\"type\"]} in {vuln[\"cve\"]}')
"
```

## Frontend Build

```bash
cd frontend
npx vite build

# Check for specific errors
npx vite build 2>&1 | Select-String "error"
npx vite build 2>&1 | Select-String "failed"

# Watch mode for development
npx vite build --watch
```

## Test Suites

```bash
# All unit tests
python -m pytest tests/unit/ -q

# Specific test file
python -m pytest tests/unit/test_<module>.py -v

# Integration tests
python -m pytest tests/integration/ -q

# With coverage
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## API Endpoint Verification

```bash
# Health check
curl -s https://localhost:4433/api/status -k

# Router exploit endpoints
curl -s https://localhost:4433/api/router-exploit/devices -k
curl -s -X POST https://localhost:4433/api/router-exploit/devices/detect -k
curl -s https://localhost:4433/api/router-exploit/vulns -k
curl -s https://localhost:4433/api/router-exploit/stats -k

# Test with authentication if required
curl -s -H "Authorization: Bearer <token>" https://localhost:4433/api/router-exploit/devices -k
```

## Common Build Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError` | Missing import path | Check relative import from file location |
| `EnumValueError` | Missing enum value | Add to enum class definition |
| `Vite build failed` | JSX syntax error | Check unclosed tags, missing imports |
| `Route not found` | Missing route registration | Add to routes.jsx and Sidebar.jsx |
| `500 on endpoint` | NoneType access | Check dataclass initialization |
| `ImportError: cannot import` | Circular import | Restructure imports, use TYPE_CHECKING |

## Pre-Commit Checklist

```bash
# 1. Syntax check all modified Python files
find backend -name "*.py" -newer <last-commit> -exec python -m py_compile {} \;

# 2. Frontend build
cd frontend && npx vite build && cd ..

# 3. Run tests
python -m pytest tests/unit/ -q

# 4. Check git diff
git diff --stat

# 5. If all pass, commit
git add -A
git commit -m "Verify build after <change>"
```

## Environment

```bash
# Activate venv
.venv\Scripts\activate

# Check Python version
python --version  # Should be 3.10+

# Check dependencies
pip list | Select-String "fastapi|uvicorn|pydantic|react"

# Reinstall if needed
pip install -r requirements.txt
```
