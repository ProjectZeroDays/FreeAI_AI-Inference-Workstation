---
name: expert-wiki
description: Expert wiki auto-updater for Quantum C2. Use when triggered by [WIKI-UPDATE] command to scan docs/ for new documentation and update the comprehensive wiki.
trigger_keywords: WIKI-UPDATE, wiki update, update wiki, sync wiki, generate wiki, wiki
---

## Purpose
Auto-scans the Quantum C2 `docs/` directory for new documentation, updates `docs/getting-started/WIKI.md` with new content, organizes into proper sections, and adds cross-references.

## When to Use
- Triggered explicitly by `[WIKI-UPDATE]` command
- After new documentation is added to `docs/`
- When wiki sections become stale or out of date
- Before releases to ensure wiki completeness

## Workflow

### Step 1: Scan Documentation Directory
```powershell
# Scan all docs/ subdirectories for markdown files
Get-ChildItem "docs/" -Recurse -Filter "*.md" | Where-Object { $_.FullName -notmatch "tasks/" }

# Check for new files in key subdirectories
Get-ChildItem "docs/architecture/" -Filter "*.md"
Get-ChildItem "docs/compliance/" -Filter "*.md"
Get-ChildItem "docs/guides/" -Filter "*.md"
Get-ChildItem "docs/zero-click/" -Filter "*.md"
Get-ChildItem "docs/reports/" -Filter "*.md"
Get-ChildItem "docs/exploit_catalog/" -Filter "*.md"
Get-ChildItem "docs/payload_catalog/" -Filter "*.md"
```

### Step 2: Read and Parse New Content
For each new/changed documentation file:
1. Extract the title and section headers
2. Identify the document category (architecture, compliance, guide, whitepaper, report, exploit)
3. Summarize key content (1-3 sentences)
4. Note any API endpoints, commands, or code examples
5. Identify cross-references to other documents

### Step 3: Update Wiki Structure
Update `docs/getting-started/WIKI.md` in this order:

1. **Table of Contents** — Add new section anchors
2. **Version/Header** — Update version and last-updated date
3. **New Sections** — Add entire new sections for new topics
4. **Existing Sections** — Append new content to existing sections
5. **Cross-References** — Add `[[Related Doc]]` links between sections
6. **Appendix** — Update appendices with new data

### Step 4: Organize Content into Proper Sections

New content should be categorized and placed in these wiki sections:

| Content Type | Wiki Section | Section Number |
|-------------|-------------|----------------|
| Architecture docs | Architecture | Section 3 |
| Backend services | Backend | Section 4 |
| Frontend pages | Frontend | Section 5 |
| AI agents | AI Agents | Section 6 |
| Security docs | Security | Section 7 |
| Compliance docs | Compliance | Section 8 |
| Network docs | Network Management | Section 9 |
| Exploit catalog | Exploit Catalog | Section 10 |
| Zero-click papers | Zero-Click Whitepapers | Section 11 |
| API docs | API Reference | Section 12 |
| Deployment guides | Deployment | Section 13 |
| Mobile docs | Mobile Apps | Section 14 |
| Testing docs | Testing | Section 15 |
| Troubleshooting | Troubleshooting | Section 16 |
| Roadmap/Planning | Roadmap | Section 18 |

### Step 5: Add Cross-References
Use wiki link syntax for cross-references:
- `[[docs/architecture/system-architecture.md]]` — Link to architecture docs
- `[[../guides/deployment-guide.md]]` — Link to deployment guide
- `[[#section-name]]` — Internal anchor link
- `[[#12-api-reference]]` — Link to specific section

### Step 6: Maintain Table of Contents
- Update TOC with new section entries
- Ensure all anchors match section headers exactly
- Use proper numbering (1., 2., 3., etc.)
- Add new appendix entries (A, B, C, etc.)

### Step 7: Commit Changes
```powershell
git add docs/getting-started/WIKI.md
git diff --cached docs/getting-started/WIKI.md  # Verify changes
git commit -m "docs: auto-update wiki with new documentation from docs/"
```

## Wiki Update Rules

### Adding New Sections
- Place new sections in numerical order in the TOC
- Use `## N. Section Title` format
- Add a `---` separator before the section
- Include a brief intro paragraph

### Updating Existing Sections
- Append new content after the last subsection
- Add a `### New Subsection` header
- Update any tables with new rows
- Add cross-references to related sections

### Cross-Reference Rules
- Every new section should link to at least one related section
- Use relative paths for docs within the same directory
- Use `../` to navigate up for cross-directory links
- Add internal anchor links for section-to-section references

## Content Extraction Patterns

### API Documentation Extraction
```powershell
# From backend route files, extract endpoints
Select-String -Path "backend/app/api/*.py" -Pattern "@router\.(get|post|put|delete)" | ForEach-Object { $_.Line }
```

### Architecture Diagram Extraction
```powershell
# From architecture docs, extract component lists
Select-String -Path "docs/architecture/*.md" -Pattern "^\|.*\|.*\|" | ForEach-Object { $_.Line }
```

### Compliance Framework Extraction
```powershell
# From compliance docs, extract framework lists
Select-String -Path "docs/compliance/*.md" -Pattern "Framework|Control|Standard" | ForEach-Object { $_.Line }
```

## Version Tracking
Update the wiki header on each change:
```markdown
> **Version:** 5.0.x | **Last Updated:** YYYY-MM-DD | **Status:** Production Ready
```

## Output
After completion, print a summary:
```
WIKI.md updated:
  - Added X new sections
  - Updated Y existing sections
  - Added Z cross-references
  - Total wiki lines: N (was M)
  - Commit: <sha>
```
