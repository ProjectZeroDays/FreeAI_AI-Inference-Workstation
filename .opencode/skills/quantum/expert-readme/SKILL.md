---
name: expert-readme
description: Expert README auto-updater for Quantum C2. Use when triggered by [README-UPDATE] command to scan codebase for new features/endpoints and update README.md with accurate documentation.
trigger_keywords: README-UPDATE, readme update, update readme, sync readme, generate readme, README
---

## Purpose
Auto-scans the Quantum C2 codebase for new features, endpoints, and architectural changes, then updates README.md to maintain accurate project documentation.

## When to Use
- Triggered explicitly by `[README-UPDATE]` command
- After significant code changes or new feature additions
- Before releases to ensure README reflects current state
- When README sections appear out of sync with the codebase

## Workflow

### Step 1: Scan Documentation Directories
```powershell
# Scan docs/ for new documentation files
Get-ChildItem "docs/" -Recurse -File | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-30) }

# Scan backend/ for new routers and services
Get-ChildItem "backend/app/api/" -Filter "*.py"
Get-ChildItem "backend/app/services/" -Recurse -Filter "*.py"

# Scan frontend/ for new pages
Get-ChildItem "frontend/src/pages/" -Recurse -Filter "*.tsx"
Get-ChildItem "frontend/src/pages/" -Recurse -Filter "*.ts"

# Check for new test files
Get-ChildItem "tests/" -Recurse -Filter "test_*.py"
```

### Step 2: Identify New Features and Endpoints
For each scanned file, extract:
- API endpoint paths and methods (GET, POST, PUT, DELETE)
- Feature descriptions from docstrings and comments
- New services, integrations, or modules
- Frontend page routes and descriptions

### Step 3: Update README.md Sections
Update the following sections in order:

1. **Table of Contents** — Add new anchor links for new top-level sections
2. **Overview** — Update key capabilities table with new categories
3. **Features** — Add new feature rows to existing tables or create new tables
4. **API Reference** — Add new endpoints to the Key Endpoints table
5. **New Features** — Add a new version subsection with date
6. **Project Statistics** — Update metrics (files, LOC, endpoints, tests)
7. **Documentation** — Add new documentation entries

### Step 4: Maintain Markdown Formatting
- Use consistent table formatting with pipe characters
- Match existing heading hierarchy (## for top, ### for subsections)
- Preserve existing badges and links
- Keep the `---` section separators
- Maintain the version/status footer

### Step 5: Update Project Statistics
Recalculate and update:
```powershell
# Count Python files and lines
(Get-ChildItem "backend/" -Recurse -Filter "*.py" | Measure-Object -Property Length -Sum).Count
(Get-ChildItem "backend/" -Recurse -Filter "*.py" | Get-Content | Measure-Object -Line).Lines

# Count frontend files
(Get-ChildItem "frontend/src/" -Recurse -Filter "*.tsx" | Measure-Object).Count
(Get-ChildItem "frontend/src/" -Recurse -Filter "*.ts" | Measure-Object).Count

# Count test files
(Get-ChildItem "tests/" -Recurse -Filter "test_*.py" | Measure-Object).Count

# Count API routers
(Get-ChildItem "backend/app/api/" -Filter "*_routes.py" | Measure-Object).Count
```

### Step 6: Commit Changes
```powershell
git add README.md
git diff --cached README.md  # Verify changes before committing
git commit -m "docs: auto-update README with new features and endpoints"
```

## README Sections to Maintain

| Section | Update Trigger | Action |
|---------|---------------|--------|
| Table of Contents | New top-level sections | Add anchor links |
| Overview capabilities table | New feature categories | Add rows |
| Features | New modules/endpoints | Add tables or rows |
| New Features | New version additions | Add version subsection |
| API Reference | New endpoints | Add rows to Key Endpoints table |
| Testing | New tests | Update test table and totals |
| Documentation | New docs | Add rows to documentation table |
| Project Statistics | Code changes | Recalculate metrics |
| Version footer | Every update | Bump version and date |

## Scan Patterns

### Backend API Detection
```python
# Search for new FastAPI router definitions
grep -r "APIRouter" backend/app/api/
grep -r "@router\." backend/app/api/
grep -r "app.include_router" backend/app/main.py
```

### Frontend Page Detection
```powershell
# Find new page components
Get-ChildItem "frontend/src/pages/" -Recurse -File | Select-Object Name, FullName
# Find new route definitions
Select-String -Path "frontend/src/router*" -Pattern "path.*=" | Select-Object Line
```

### Test Coverage Detection
```powershell
# Count new tests
Get-ChildItem "tests/" -Recurse -Filter "test_*.py" | Measure-Object
# Check test results
cd backend; python -m pytest tests/ --collect-only -q
```

## Version Bumping Rules
- **Patch** (x.x.1): Bug fixes, documentation updates, minor endpoints
- **Minor** (x.1.0): New features, new endpoints, new dashboards
- **Major** (1.x.0): Breaking changes, major architecture shifts

## Output
After completion, print a summary of changes made:
```
README.md updated:
  - Added X new API endpoints
  - Added Y new features
  - Updated Z sections
  - Version: x.x.x -> x.x.x+1
  - Commit: <sha>
```
