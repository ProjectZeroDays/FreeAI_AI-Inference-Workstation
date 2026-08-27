---
name: test-runner
description: Run and analyze Quantum C2 test suites. Use when executing tests, checking coverage, or diagnosing test failures.
trigger_keywords: test, run tests, coverage, pytest, validate, verify tests
---

## Purpose
Executes and analyzes Quantum C2 test suites including unit, integration, security, and E2E tests with coverage reporting.

## When to Use
- Before commits or deployments
- When user asks to "run tests" or "check coverage"
- After code changes to verify nothing broke
- For CI/CD integration

## Workflow
1. Run targeted test suite
2. Check for failures and generate report
3. Run coverage analysis
4. Analyze test results
5. Fix failing tests if needed

## Commands
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=backend/app --cov-report=term-missing

# Run specific test category
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/e2e/ -v
python -m pytest tests/fuzzing/ -v

# Run by marker
python -m pytest tests/ -v -m security
python -m pytest tests/ -v -m network
python -m pytest tests/ -v -m slow

# Run specific file
python -m pytest tests/test_exploits.py -v
python -m pytest tests/test_comprehensive_defensive.py -v

# Run with detailed output on failure
python -m pytest tests/ -v --tb=long --maxfail=3

# Check test counts
python -m pytest tests/ --collect-only -q

# Run quick test subset
python -m pytest tests/test_quantum_quick.py -v

# Coverage report as HTML
python -m pytest tests/ --cov=backend/app --cov-report=html
```

## Test Categories
| Category | Path | Marker | Description |
|----------|------|--------|-------------|
| Unit | `tests/unit/` | `unit` | Individual module tests |
| Integration | `tests/integration/` | `integration` | Cross-module tests |
| E2E | `tests/e2e/` | `e2e` | End-to-end flows |
| Security | `tests/test_*.py` | `security` | Security tests |
| Fuzzing | `tests/fuzzing/` | `fuzzing` | Chaos/fuzz tests |
| Stealth | `tests/test_stealth/` | `opsec` | Stealth tests |
| Zero-Click | `tests/test_zero_click/` | `zero_trust` | Zero-click tests |
| Rootkit | `tests/test_rootkit/` | `persistence` | Persistence tests |

## Pytest Configuration
- Config: `tests/pytest.ini`
- Min version: 7.4.3
- Max failures: 5
- Strict markers enabled
- Warnings filtered

## Test Markers Available
```
unit, integration, slow, network, security, mobile, hardware,
cloud, cryptocurrency, quantum, rf, psyops, insider,
counter_intel, wiper, persistence, zero_trust, planning,
legal, opsec
```

## Output Examples
```
============================= test session starts ==============================
platform win32 -- Python 3.12.0
collected 240 items

tests/test_exploits.py::TestExploitsModule::test_catalogue_importable PASSED [  0%]
tests/test_exploits.py::TestExploitsModule::test_catalogue_has_exploits PASSED [  0%]

======================== 240 passed in 45.23s ========================
```

## Notes
- Tests use fixtures from `tests/conftest.py`
- Backend path injected automatically via conftest
- Results saved to `tests/test_results.json`
- See `.learnings/ERRORS.md` for known test issues
