---
name: production-readiness-check
description: Verify Quantum C2 production readiness before deployment. Use when the user asks about production readiness, wants to verify the system is deployable, or needs a production health assessment.
trigger_keywords: production readiness, deploy, verify, health check, pre-flight, production check, is ready
---

## Purpose
Verifies Quantum C2 is production-ready by running systematic checks across tests, security, database, compliance, and service health.

## When to Use
- Before any production deployment
- When user asks "is Quantum C2 ready for production?"
- After major code changes before shipping
- As a pre-deployment gate check

## Workflow
1. Run production health check script
2. Execute security scans (bandit, safety, ruff)
3. Verify test coverage meets threshold
4. Check database connectivity and configuration
5. Run compliance scan
6. Generate readiness report

## Commands
```bash
# Run full production health check
python scripts/production_check.py http://localhost:8000

# Run security audit
bandit -r backend/app/ -ll -x backend/app/__pycache__
safety check --json
ruff check backend/app/

# Run test suite with coverage
python -m pytest tests/ -v --cov=backend/app --cov-report=term-missing

# Run compliance scan
python scripts/compliance_scanner.py

# Check database
python -c "from app.database.connection_unified import is_sqlite; print(f'Using SQLite: {is_sqlite()}')"
```

## Output Format
```
Quantum C2 Production Readiness Report
========================================
Tests: {passed} passed, {skipped} skipped
Security: PASS/FAIL
Compliance: {score}%
Database: {type} (production: {status})
Services: All healthy
Status: PRODUCTION READY / ISSUES FOUND
```

## Notes
- Results saved to `health_check_results.json`
- All checks must pass for READY status
- Warnings are non-blocking but should be reviewed
- See `.learnings/ERRORS.md` for known production issues and fixes
