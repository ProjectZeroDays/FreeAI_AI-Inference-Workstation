---
name: debug-workflow
description: Debug common Quantum C2 issues. Use when encountering errors, failures, or unexpected behavior.
trigger_keywords: debug, error, fix, troubleshoot, issue, problem, crash, failing
---

## Purpose
Systematic debugging workflow for common Quantum C2 issues including import errors, routing problems, database issues, and service failures.

## When to Use
- When user reports an error or issue
- Before/after code changes
- When tests fail
- When services won't start
- For recurring error patterns

## Workflow
1. Identify error from logs or output
2. Check `.learnings/ERRORS.md` for known patterns
3. Run targeted diagnostic commands
4. Apply fix based on error category
5. Verify resolution
6. Document new error patterns

## Common Error Patterns

### Import Errors
```bash
# Check module locations
find backend/app -name "*.py" | xargs grep -l "device_profiles"

# Fix circular imports - check routers/__init__.py
cat backend/app/routers/__init__.py

# Verify enum values exist
python -c "from app.gateways.router_exploit.router_gateway import RouterVulnType; print([m for m in dir(RouterVulnType)])"
```

### Git Lock Issues
```powershell
# Remove stale lock files
Remove-Item .git/index.lock -Force
```

### PowerShell Syntax
```powershell
# Use semicolons instead of &&
cd path; python script.py
# NOT: cd path && python script.py
```

### Database Issues
```bash
# Check database connection
python -c "from app.database.connection_unified import AsyncSessionLocal; print('OK')"

# Verify SQLite exists
ls backend/*.db

# Check PostgreSQL
docker exec quantum-db pg_isready -U quantum
```

### Service Startup
```bash
# Check backend logs
docker-compose logs backend --tail=50

# Check for port conflicts
netstat -ano | findstr :8000

# Verify dependencies
python -m pip list | findstr fastapi
```

## Diagnostic Commands
```bash
# Full syntax check
python -m py_compile backend/app/main.py

# Import check
python -c "from app.main import app; print('Import OK')"

# Run targeted test
python -m pytest tests/test_import.py -v

# Check ruff linting
ruff check backend/app/

# Check for unused imports
ruff check backend/app/ --select=F401
```

## Notes
- Always check `.learnings/ERRORS.md` first for known issues
- PowerShell `&&` does not work — use `;` or separate commands
- SQLAlchemy reserves `metadata` as a column name — use `extra_metadata`
- Device profiles module is in `app/api/` not `app/routers/`
- See `.learnings/LEARNINGS.md` for architectural insights
