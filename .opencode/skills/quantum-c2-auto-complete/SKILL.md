---
name: quantum-c2-auto-complete
description: >
  Autonomous project completion engine. Use when the user wants to bring Quantum C2 to full production completion with zero manual intervention. This skill rewrites sub-optimally prompt engineering and executes the entire roadmap autonomously — analyzing gaps, prioritizing work, implementing features, running validations, and committing all changes. Triggers on: "complete Quantum C2", "finish the project", "auto-complete", "full completion", "autonomous development", "execute roadmap", "complete all tasks", "production ready", "zero touch completion".
---

# Quantum C2 Autonomous Completion Engine

You are the lead architect executing the full completion of Quantum C2. Your mandate: analyze the codebase, identify all gaps, and autonomously implement everything needed for 100% production readiness with zero human intervention.

## Mission Brief

**Objective:** Bring Quantum C2 from its current state to FULL PRODUCTION READINESS in a single autonomous run.

**Current State Assessment Required:**
- Analyze ALL backend routers, models, services
- Analyze ALL frontend pages, components
- Identify broken imports, missing routes, unregistered features
- Find TODO/FIXME/HACK comments
- Audit security gaps
- Check test coverage
- Validate all APIs work

## Autonomous Execution Protocol

### Phase 1: Deep Analysis (Scan & Catalog)
```bash
# Execute these to build complete inventory
find backend/app/routers -name "*.py" | wc -l
find frontend/src/pages -name "*.jsx" | wc -l
grep -r "TODO\|FIXME\|HACK\|XXX" backend/ frontend/ --include="*.py" --include="*.jsx" --include="*.tsx"
grep -r "import.*Error\|ImportError\|ModuleNotFoundError" backend/ --include="*.py"
grep -r "NotImplementedError\|pass$" backend/app/routers/ --include="*.py"
```

### Phase 2: Gap Analysis & Prioritization
Build a master task list from:
1. **Critical (P0):** Broken imports, missing registrations, security vulnerabilities, data loss risks
2. **High (P1):** Missing features, incomplete implementations, test failures
3. **Medium (P2):** UI improvements, documentation, edge cases
4. **Low (P3):** Cleanup, refactoring, nice-to-haves

### Phase 3: Autonomous Implementation
For EACH task identified:
1. Read relevant source files
2. Implement the fix/feature
3. Run syntax check: `python -m py_compile <file>`
4. Run imports check: `python -c "from app.routers.<module> import router"`
5. Commit immediately after each successful change
6. Never ask for permission — execute based on best judgement

### Phase 4: Validation & Testing
```bash
# Backend
python -m pytest tests/ -v --tb=short
python -m py_compile backend/app/main.py

# Frontend
cd frontend && npx vite build

# API smoke test
curl -s http://localhost:8000/health
curl -s http://localhost:8000/api/dashboard/
curl -s http://localhost:8000/api/forced-entry/config
curl -s http://localhost:8000/api/agents/health
```

### Phase 5: Final Commit & Summary
- Commit all changes with comprehensive messages
- Push to remote
- Generate completion report

## Implementation Rules

1. **NEVER stop to ask for permission** — use best judgement
2. **ALWAYS commit after each logical change** — small, atomic commits
3. **VALIDATE after each change** — syntax check, import check
4. **FIX everything broken** — no TODOs left unaddressed
5. **REGISTER everything** — all routers, routes, components must be wired up
6. **SECURITY FIRST** — fix all security vulnerabilities before anything else
7. **COMPLETE > PERFECT** — ship working code, iterate later

## Output Format

After completion, provide:
```
=== QUANTUM C2 AUTO-COMPLETE REPORT ===
Tasks Completed: XX
Files Modified: XX
Files Created: XX
Commits Made: XX
Tests Passing: XX/XX
Open Issues: XX
Status: PRODUCTION READY / NEEDS ATTENTION
```

## Execution Command

Start by analyzing the project structure, then execute ALL tasks autonomously until completion.
