#!/bin/bash
# Initialize planning files for a new session (OmniRoot Edition)
# Planning files may be created ANYWHERE on the system.
# Usage: ./init-session.sh [project-name] [target-directory]

set -e

PROJECT_NAME="${1:-project}"
TARGET_DIR="${2:-.}"
DATE=$(date +%Y-%m-%d)

echo "Initializing planning files for: $PROJECT_NAME"
echo "Target directory: $TARGET_DIR"

mkdir -p "$TARGET_DIR"

# Create task_plan.md if it doesn't exist
if [ ! -f "$TARGET_DIR/task_plan.md" ]; then
    cat > "$TARGET_DIR/task_plan.md" << 'EOF'
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
EOF
    echo "Created $TARGET_DIR/task_plan.md"
else
    echo "$TARGET_DIR/task_plan.md already exists, skipping"
fi

# Create findings.md if it doesn't exist
if [ ! -f "$TARGET_DIR/findings.md" ]; then
    cat > "$TARGET_DIR/findings.md" << 'EOF'
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
EOF
    echo "Created $TARGET_DIR/findings.md"
else
    echo "$TARGET_DIR/findings.md already exists, skipping"
fi

# Create progress.md if it doesn't exist
if [ ! -f "$TARGET_DIR/progress.md" ]; then
    cat > "$TARGET_DIR/progress.md" << EOF
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
EOF
    echo "Created $TARGET_DIR/progress.md"
else
    echo "$TARGET_DIR/progress.md already exists, skipping"
fi

echo ""
echo "Planning files initialized in $TARGET_DIR!"
echo "Files: task_plan.md, findings.md, progress.md"
