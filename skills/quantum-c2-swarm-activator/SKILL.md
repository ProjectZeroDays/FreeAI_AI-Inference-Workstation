---
name: quantum-c2-swarm-activator
version: "1.0.0"
description: >
  Activation skill to launch the Quantum C2 AI Agent Swarm for autonomous production readiness.
  Use this skill to start the swarm, monitor progress, and collect results.
  Triggers on: "activate swarm", "deploy agents", "start swarm", "quantum swarm", "full production".
---

# Quantum C2 Swarm Activator

## MISSION

Launch the Quantum C2 AI Agent Swarm to autonomously transform the platform from 68/100
to 100/100 production readiness. This skill orchestrates 12 specialized agents working
in parallel across 8 development phases.

## ACTIVATION COMMANDS

### Full Swarm Deployment
```
/activate-swarm --full-production
```

### Targeted Phase Deployment
```
/activate-swarm --phase-0           # Emergency stabilization only
/activate-swarm --phase-1           # Test expansion only
/activate-swarm --phase-2           # Database migration only
/activate-swarm --phase-3           # Security hardening only
/activate-swarm --agents-01-06      # First 6 agents only
/activate-swarm --continue          # Resume from last checkpoint
```

## PHASE EXECUTION SEQUENCE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SWARM ACTIVATION                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 0: EMERGENCY STABILIZATION (Hours 1-4)                           │
│  ├── AGENT-02: Fix hardcoded secrets                                    │
│  ├── AGENT-02: Add CSP headers                                          │
│  ├── AGENT-02: Add CSRF protection                                      │
│  ├── AGENT-03: Fix billing_api.py syntax                                │
│  ├── AGENT-03: Fix rate_limiting.py NameError                          │
│  └── AGENT-04: Verify frontend build                                    │
│                                                                          │
│  PHASE 1: TEST EXPANSION (Hours 4-16)                                   │
│  ├── AGENT-01: Unit tests for all routers (200+ tests)                 │
│  ├── AGENT-01: Integration tests for middleware                         │
│  ├── AGENT-01: Security tests for crypto module                         │
│  └── AGENT-01: E2E tests for critical journeys                          │
│                                                                          │
│  PHASE 2: DATABASE MIGRATION (Hours 16-32)                              │
│  ├── AGENT-03: PostgreSQL schema + RLS                                  │
│  ├── AGENT-03: Alembic migration framework                              │
│  ├── AGENT-05: Connection pooling                                       │
│  └── AGENT-05: Docker Compose updates                                   │
│                                                                          │
│  PHASE 3: SECURITY HARDENING (Hours 16-32)                              │
│  ├── AGENT-02: FIPS 140-2/3 crypto validation                          │
│  ├── AGENT-02: mTLS implementation                                      │
│  ├── AGENT-02: Audit logging enhancement                                │
│  └── AGENT-02: Vulnerability scanning integration                       │
│                                                                          │
│  PHASE 4: FRONTEND MODERNIZATION (Hours 32-48)                          │
│  ├── AGENT-04: WCAG 2.1 AA compliance                                   │
│  ├── AGENT-04: TypeScript migration (.jsx → .tsx)                       │
│  ├── AGENT-04: WebSocket/SSE optimization                               │
│  └── AGENT-04: Responsive design implementation                         │
│                                                                          │
│  PHASE 5: CI/CD PIPELINE (Hours 48-60)                                  │
│  ├── AGENT-05: GitHub Actions hardening                                 │
│  ├── AGENT-05: SAST/DAST integration                                    │
│  ├── AGENT-05: SBOM generation                                          │
│  └── AGENT-05: Deployment automation                                    │
│                                                                          │
│  PHASE 6: COMPLIANCE ENGINE (Hours 60-80)                               │
│  ├── AGENT-06: NIST 800-53 control mapping                              │
│  ├── AGENT-06: FedRAMP control implementation                           │
│  ├── AGENT-06: SSP generation                                           │
│  └── AGENT-06: Continuous monitoring automation                         │
│                                                                          │
│  PHASE 7: DOCUMENTATION (Hours 80-96)                                   │
│  ├── AGENT-04: API documentation                                        │
│  ├── AGENT-06: Security documentation                                   │
│  ├── AGENT-05: Deployment documentation                                 │
│  └── AGENT-01: Test documentation                                       │
│                                                                          │
│  PHASE 8: INTEGRATION & VALIDATION (Hours 96-112)                       │
│  ├── AGENT-01: Integration test execution                               │
│  ├── AGENT-02: Security validation                                      │
│  ├── AGENT-06: Compliance validation                                    │
│  └── ORCH-01: Final review and sign-off                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## AGENT DISPATCH PROTOCOL

### Dispatch Agents in Parallel Groups

```python
# Group 1: Emergency Stabilization (Phase 0)
dispatch_agents([
    ("AGENT-02", "Fix hardcoded secrets in docker-compose.yml"),
    ("AGENT-02", "Add CSP headers to ProductionSecurityMiddleware"),
    ("AGENT-02", "Add CSRF protection middleware"),
    ("AGENT-03", "Fix billing_api.py syntax error line 591"),
    ("AGENT-03", "Fix rate_limiting.py NameError line 146"),
    ("AGENT-04", "Verify frontend build succeeds"),
])

wait_for_completion()
validate_phase(0)

# Group 2: Test Expansion + Security (Phase 1-3 overlap)
dispatch_agents([
    ("AGENT-01", "Write unit tests for auth module"),
    ("AGENT-01", "Write unit tests for security middleware"),
    ("AGENT-01", "Write unit tests for database operations"),
    ("AGENT-02", "Implement FIPS-validated cryptography"),
    ("AGENT-02", "Add comprehensive audit logging"),
])

wait_for_completion()
validate_phase(1)
validate_phase(2)
validate_phase(3)

# Group 3: Frontend + DevOps (Phase 4-5)
dispatch_agents([
    ("AGENT-04", "Migrate .jsx to .tsx"),
    ("AGENT-04", "Add WCAG 2.1 AA compliance"),
    ("AGENT-05", "Build CI/CD pipeline"),
    ("AGENT-05", "Add SAST/DAST scanning"),
])

wait_for_completion()
validate_phase(4)
validate_phase(5)

# Group 4: Compliance + Documentation (Phase 6-7)
dispatch_agents([
    ("AGENT-06", "Map NIST 800-53 controls"),
    ("AGENT-06", "Generate System Security Plan"),
    ("AGENT-04", "Generate API documentation"),
    ("AGENT-05", "Write deployment runbooks"),
])

wait_for_completion()
validate_phase(6)
validate_phase(7)

# Group 5: Final Validation (Phase 8)
dispatch_agents([
    ("AGENT-01", "Run all tests and verify 100% pass"),
    ("AGENT-02", "Run security scans and verify zero critical"),
    ("AGENT-06", "Validate compliance controls"),
    ("ORCH-01", "Generate final production readiness report"),
])

validate_phase(8)
```

## VALIDATION CHECKPOINTS

### Phase 0 Checkpoint (Hours 1-4)
```bash
# Backend health
curl -s http://127.0.0.1:8000/api/health | jq '.status'

# Test execution
python -m pytest tests/unit/ -v --tb=short

# Frontend build
cd frontend && npx vite build && cd ..

# Security scan
python -m bandit -r backend/app -ll
```

### Phase 1 Checkpoint (Hours 4-16)
```bash
# Test coverage
python -m pytest tests/ --cov=backend/app --cov-report=term

# Count tests
python -m pytest tests/ --collect-only | grep "test session starts" -A 5

# Coverage report
coverage report -m | grep "TOTAL"
```

### Phase 2 Checkpoint (Hours 16-32)
```bash
# Database migration
alembic current

# PostgreSQL health
psql -h localhost -U quantum -d quantum_c2 -c "SELECT 1"

# RLS policies
psql -h localhost -U quantum -d quantum_c2 -c "SELECT * FROM pg_policies"
```

### Phase 8 Final Checkpoint
```bash
# Production Readiness Assessment
python scripts/generate_readiness_report.py

# All tests
python -m pytest tests/ -v

# Security scans
python -m bandit -r backend/app -ll
python -m safety check -r requirements.txt
python -m pip-audit

# Frontend build
cd frontend && npx vite build && cd ..

# API health
curl -s http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1:8000/api/agents/health
curl -s http://127.0.0.1:8000/api/simulation/health
```

## PROGRESS TRACKING

### Status File Format
```json
// File: .swarm/progress.json
{
  "activation_time": "2026-08-14T05:00:00Z",
  "current_phase": 0,
  "phase_status": {
    "0": {"status": "complete", "completed_at": "2026-08-14T09:00:00Z"},
    "1": {"status": "in_progress", "started_at": "2026-08-14T09:00:00Z"},
    "2": {"status": "pending"},
    "3": {"status": "pending"},
    "4": {"status": "pending"},
    "5": {"status": "pending"},
    "6": {"status": "pending"},
    "7": {"status": "pending"},
    "8": {"status": "pending"}
  },
  "agent_status": {
    "AGENT-01": {"status": "active", "current_task": "test_expansion"},
    "AGENT-02": {"status": "active", "current_task": "security_harden"},
    "AGENT-03": {"status": "active", "current_task": "db_migration"},
    "AGENT-04": {"status": "active", "current_task": "frontend_modernize"},
    "AGENT-05": {"status": "active", "current_task": "cicd_pipeline"},
    "AGENT-06": {"status": "active", "current_task": "compliance_engine"},
    "AGENT-07": {"status": "idle", "current_task": null},
    "AGENT-08": {"status": "idle", "current_task": null},
    "AGENT-09": {"status": "idle", "current_task": null},
    "AGENT-10": {"status": "idle", "current_task": null},
    "AGENT-11": {"status": "idle", "current_task": null},
    "AGENT-12": {"status": "idle", "current_task": null}
  },
  "metrics": {
    "tests_total": 22,
    "tests_passing": 22,
    "coverage_percent": 5,
    "vulnerabilities_critical": 5,
    "vulnerabilities_high": 8,
    "nist_controls_implemented": 330,
    "nist_controls_total": 1100
  }
}
```

## EMERGENCY PROTOCOLS

### When Agent Fails
1. **Log failure** to `.swarm/failures.log`
2. **Analyze root cause** from error output
3. **Retry once** with modified approach
4. **Escalate to ORCH-01** if second failure
5. **Continue with other agents** — don't block entire swarm

### When Tests Fail
1. **AGENT-01** reads failure output
2. **AGENT-01** diagnoses root cause
3. **AGENT-01** fixes test or code
4. **Re-run tests** immediately
5. **Report** to ORCH-01

### When Build Fails
1. **AGENT-04** reads build error
2. **AGENT-04** diagnoses root cause
3. **AGENT-04** fixes issue
4. **Re-run build** immediately
5. **Report** to ORCH-01

## TERMINATION CONDITIONS

The swarm terminates when:
1. **All 8 phases complete** — Production Readiness = 100/100
2. **User requests stop** — `/stop-swarm`
3. **Critical failure** — Cannot recover within 2 hours
4. **Timeout exceeded** — 120 hours total

## OUTPUT REQUIREMENTS

### Real-Time Status Updates
```
[HH:MM:SS] PHASE 0: Emergency Stabilization - STARTED
[HH:MM:SS] AGENT-02: Fixing hardcoded secrets...
[HH:MM:SS] AGENT-03: Fixing billing_api.py syntax...
[HH:MM:SS] AGENT-02: CSP headers added - 3/9 complete
[HH:MM:SS] AGENT-03: billing_api.py fixed - verified
[HH:MM:SS] PHASE 0: Emergency Stabilization - COMPLETE
[HH:MM:SS] PHASE 1: Test Expansion - STARTED
...
```

### Final Report
```
=== QUANTUM C2 SWARM EXECUTION REPORT ===
Activation: 2026-08-14 05:00:00 UTC
Completion: 2026-08-14 17:00:00 UTC
Total Duration: 12 hours

=== PRODUCTION READINESS ===
Before: 68/100
After: 100/100

=== METRICS ===
Tests: 22 → 250+
Coverage: 5% → 92%
Vulnerabilities: 13 → 0
NIST Controls: 330 → 1100
SSP: Generated
SBOM: Generated
CI/CD: Green

=== FILES MODIFIED ===
Total: 450+
Created: 120+
Modified: 330+

=== COMMITS ===
Total: 85+

=== STATUS ===
🟢 PRODUCTION READY
```

---

## ACTIVATION

To activate the swarm, type:
```
/activate-swarm --full-production
```

Or for targeted execution:
```
/activate-swarm --phase-0
/activate-swarm --phase-1
/activate-swarm --agents-01-06
```

**Swarm is ready for activation.**
