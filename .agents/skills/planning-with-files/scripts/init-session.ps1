# Initialize planning files for a new session (OmniRoot Edition)
# Planning files may be created ANYWHERE on the system — no restrictions.
# Usage: .\init-session.ps1 [project-name] [target-directory]

param(
    [string]$ProjectName = "project",
    [string]$TargetDir = "."
)

$DATE = Get-Date -Format "yyyy-MM-dd"

Write-Host "Initializing planning files for: $ProjectName"
Write-Host "Target directory: $TargetDir"

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

# Create task_plan.md if it doesn't exist
if (-not (Test-Path "$TargetDir\task_plan.md")) {
    @"
# Task Plan: [Brief Description]

## Goal
[One sentence describing the end state]

## Current Phase
Phase 1

## Phases

### Phase 1: Requirements & Discovery
- [ ] Understand user intent
- [ ] Identify constraints
- [ ] Document in findings.md
- **Status:** in_progress

### Phase 2: Planning & Structure
- [ ] Define approach
- [ ] Create project structure
- **Status:** pending

### Phase 3: Implementation
- [ ] Execute the plan
- [ ] Write to files before executing
- **Status:** pending

### Phase 4: Testing & Verification
- [ ] Verify requirements met
- [ ] Document test results
- **Status:** pending

### Phase 5: Delivery
- [ ] Review outputs
- [ ] Deliver to user
- **Status:** pending

## Decisions Made
| Decision | Rationale |
|----------|-----------|

## Errors Encountered
| Error | Resolution |
|-------|------------|
"@ | Out-File -FilePath "$TargetDir\task_plan.md" -Encoding UTF8
    Write-Host "Created $TargetDir\task_plan.md"
} else {
    Write-Host "$TargetDir\task_plan.md already exists, skipping"
}

# Create findings.md if it doesn't exist
if (-not (Test-Path "$TargetDir\findings.md")) {
    @"
# Findings & Decisions

## Requirements
-

## Research Findings
-

## Technical Decisions
| Decision | Rationale |
|----------|-----------|

## Issues Encountered
| Issue | Resolution |
|-------|------------|

## Resources
-
"@ | Out-File -FilePath "$TargetDir\findings.md" -Encoding UTF8
    Write-Host "Created $TargetDir\findings.md"
} else {
    Write-Host "$TargetDir\findings.md already exists, skipping"
}

# Create progress.md if it doesn't exist
if (-not (Test-Path "$TargetDir\progress.md")) {
    @"
# Progress Log

## Session: $DATE

### Current Status
- **Phase:** 1 - Requirements & Discovery
- **Started:** $DATE

### Actions Taken
-

### Test Results
| Test | Expected | Actual | Status |
|------|----------|--------|--------|

### Errors
| Error | Resolution |
|-------|------------|
"@ | Out-File -FilePath "$TargetDir\progress.md" -Encoding UTF8
    Write-Host "Created $TargetDir\progress.md"
} else {
    Write-Host "$TargetDir\progress.md already exists, skipping"
}

Write-Host ""
Write-Host "Planning files initialized in $TargetDir!"
Write-Host "Files: task_plan.md, findings.md, progress.md"
