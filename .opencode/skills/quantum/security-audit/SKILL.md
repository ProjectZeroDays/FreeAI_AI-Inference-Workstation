---
name: security-audit
description: Perform comprehensive security audits on Quantum C2. Use when the user asks to audit security, scan for vulnerabilities, or check security posture.
trigger_keywords: security audit, scan, vulnerabilities, bandit, safety, security check, pentest
---

## Purpose
Performs comprehensive security audits on the Quantum C2 framework including code scanning, dependency checks, and configuration verification.

## When to Use
- Before deployment to any environment
- After receiving security advisories
- When user asks to "audit security" or "scan for vulnerabilities"
- As part of regular security maintenance

## Workflow
1. Run static analysis (bandit) on backend code
2. Check dependency vulnerabilities (safety)
3. Run linting with security rules (ruff)
4. Verify security headers and mTLS configuration
5. Check audit log retention and encryption
6. Generate security report

## Commands
```bash
# Static analysis - security vulnerabilities
bandit -r backend/app/ -ll -x backend/app/__pycache__

# Dependency vulnerability check
safety check --json

# License compliance check
pip-licenses --format=json

# Linting with security rules
ruff check backend/app/ --select=S,E,W,F

# Check security headers
curl -I http://127.0.0.1:8000/api/health

# Verify mTLS configuration
python scripts/mtls_setup.py

# Check audit log retention
python scripts/audit_retention.py

# Run security-focused test suite
python -m pytest tests/ -v -m security
```

## Security Checklist
| Area | Status | Tool |
|------|--------|------|
| Hardcoded Secrets | Clean | git-secrets |
| SQL Injection | Protected | Parameterized queries |
| XSS | Protected | Input sanitization |
| CSRF | Enabled | CSRF middleware |
| Rate Limiting | Active | TieredRateLimitMiddleware |
| Authentication | JWT + MFA | auth middleware |
| Authorization | RBAC | Role-based access |
| Encryption | FIPS 140-2/3 | cryptography library |
| Audit Logging | Enabled | AuditLogger |
| mTLS | Ready | mtls_setup.py |

## Output Report
```json
{
  "audit_id": "SEC-YYYYMMDD-XXX",
  "timestamp": "2026-08-14T12:00:00Z",
  "findings": [],
  "risk_score": 95,
  "status": "secure"
}
```

## Notes
- Bandit low+medium severity is the default threshold
- Safety checks for known CVEs in dependencies
- ruff S-select focuses on security issues
- See `.learnings/ERRORS.md` for previously found security issues
