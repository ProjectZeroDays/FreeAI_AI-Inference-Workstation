---
name: quantum-test-runner
description: Runs the Quantum framework test suites and reports results. Covers unit tests, integration tests, module tests, and end-to-end tests. Use when the user wants to run tests, verify modules, or check framework health.
---

# Quantum Test Runner

Runs all test suites and provides structured results.

## Test Commands

```bash
# All module tests (40 tests)
cd "C:\Users\Project Zero\Desktop\Quantum" && python -m pytest tests/ -v --tb=short 2>&1

# Import smoke test
python test_imports.py

# End-to-end integration tests
python run_end_to_end_tests.py

# Crypto tests
python test_quantum_crypto.py

# MiMoCode integration tests
python test_mimocode_integration.py

# Specific module test
python -m pytest tests/integration/test_<module>.py -v
```

## Test Inventory (Expected Counts)

| Suite | Count | Location |
|-------|-------|----------|
| Defensive modules | 40/40 | `tests/` |
| Simulations | 21/21 | `tests/` |
| Threat Intel | 8/8 | `tests/` |
| ML Pipeline | 8/8 | `tests/` |
| **Total** | **77/77** | All suites |

## After Test Run

1. Parse output for FAILURES and ERRORS
2. For each failure: identify file, line, assertion, root cause
3. Fix the failing test or the underlying code
4. Re-run only the failing suite to verify fix
5. Report final tally: `X/Y passed (Z%)`

## Common Failures

- **ImportError**: Missing dependency → add to requirements.txt
- **AssertionError**: Wrong expected value → check if code or test needs update
- **ConnectionRefused**: Flask not running → start app first
- **ModuleNotFoundError**: Path issue → ensure `PYTHONPATH=.` or run from project root
- **AttributeError**: API changed → check if function signature was updated

## Environment

```bash
# Ensure venv is active
.venv\Scripts\activate

# Or run with explicit python
.venv\Scripts\python.exe -m pytest tests/ -v
```
