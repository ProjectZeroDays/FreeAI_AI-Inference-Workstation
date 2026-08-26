---
name: docs-update
description: Update Quantum C2 documentation. Use when generating, updating, or syncing project documentation.
trigger_keywords: docs, documentation, README, generate docs, update docs, documentation sync, doc update
---

## Purpose
Manages and updates Quantum C2 project documentation including README, API docs, architecture diagrams, and inline documentation.

## When to Use
- After significant code changes
- When user asks to "update docs" or "generate documentation"
- Before releases
- When documentation is out of sync with code

## Workflow
1. Scan codebase for doc changes needed
2. Update README with new features
3. Generate/update API documentation
4. Update architecture diagrams
5. Sync inline docstrings
6. Verify documentation completeness

## Commands
```bash
# Update README from template
python scripts/update_frontend_styles.py

# Check docs coverage
python -m pytest tests/test_doc_sync.py -v

# Generate API docs
# Access at http://localhost:8000/docs after server starts

# Check for missing docstrings
ruff check backend/app/ --select=D

# Run documentation sync test
python -m pytest tests/test_doc_sync.py -v

# Update frontend styles
python scripts/update_frontend_styles.py

# Generate completions
./scripts/generate_completions.sh
```

## Documentation Areas
| Area | Location | Description |
|------|----------|-------------|
| README | `README.md` | Project overview and quick start |
| API Docs | `backend/app/docs/` | FastAPI auto-generated docs |
| Architecture | `docs/` | Architecture diagrams and guides |
| Inline Docs | `backend/app/**/*.py` | Docstrings and type hints |
| Compliance | `docs/compliance/` | Framework compliance docs |
| Blueprint | `BLUEPRINT.md` | System blueprint |

## README Sections to Maintain
- Overview and capabilities table
- Architecture diagram
- Quick start instructions
- API reference links
- Compliance status
- Security posture
- Contributing guidelines

## Documentation Standards
- All public functions must have docstrings
- Type hints required on all function signatures
- README must reflect current feature set
- API endpoints documented in code
- Compliance controls tracked in docs

## Notes
- FastAPI auto-generates `/docs` and `/redoc` from code
- Run `ruff --select=D` to check for missing docs
- README badge statuses should be updated manually
- See `.learnings/LEARNINGS.md` for documentation best practices
