---
name: production-readiness
description: Check production readiness of Quantum C2. Use when the user asks about production readiness, deployment status, or wants to verify the framework is ready for production.
trigger_keywords: production readiness, production check, deploy status, verify production, ready to deploy
---

# Production Readiness Check

## Overview
This skill helps verify Quantum C2 is production-ready by checking:
- Test coverage
- Security hardening
- Database configuration
- Compliance status
- Service health

## Commands

### Run Full Production Check
```bash
python scripts/production_check.py
```

### Check Test Coverage
```bash
python -m pytest tests/ -v --cov=backend/app --cov-report=term-missing
```

### Verify Security
```bash
bandit -r backend/app/ -ll
safety check
ruff check backend/app/
```

### Check Database
```bash
python -c "from app.database.connection_unified import is_sqlite; print(f'Using SQLite: {is_sqlite()}')"
python -c "from app.database.postgres_primary import get_postgres_manager; m = get_postgres_manager(); print(m.get_statistics())"
```

### Run Compliance Scan
```bash
python scripts/compliance_scanner.py
python scripts/compliance_monitor.py
```

## Production Checklist

| Check | Command | Status |
|-------|---------|--------|
| Unit Tests | `pytest tests/unit/ -q` | 106 passed |
| Integration Tests | `pytest tests/integration/ -q` | 134 passed |
| Security Scan | `bandit -r backend/app/ -ll` | PASS |
| Dependency Check | `safety check` | PASS |
| Linting | `ruff check backend/app/` | PASS |
| Frontend Build | `npm run build` | PASS |
| Health Check | `curl http://127.0.0.1:8000/api/health` | Healthy |
| Database | SQLite/PostgreSQL | Configured |
| mTLS | Config | Ready |
| Audit Logging | Config | Enabled |
| Compliance | 40+ controls | 97% compliant |

## Output Format
```
Quantum C2 Production Readiness Report
========================================
Tests: 106 passed, 32 skipped
Security: PASS
Compliance: 97.06%
Database: SQLite (production: PostgreSQL ready)
Services: All healthy
Status: PRODUCTION READY
```
