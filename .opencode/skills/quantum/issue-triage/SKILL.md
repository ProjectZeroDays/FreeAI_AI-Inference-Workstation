---
name: issue-triage
description: Analyze, categorize, and triage GitHub issues for the Quantum C2 project. Use when the user asks to triage issues, categorize bugs, manage issue labels, or process new issue submissions.
trigger_keywords: triage, triage issue, categorize issue, issue management, label issue, bug report, issue workflow
---

## Purpose
Systematically analyze incoming GitHub issues, gather relevant repository context, and take evidence-based triage actions including labeling, assignment, deduplication, and closure decisions.

## When to Use
- When user asks to "triage issues" or "categorize issues"
- When a new issue is opened and needs classification
- When issues need labels, priority, or assignment
- When reviewing issue backlog for organization
- Before starting work on an issue to confirm scope

## Workflow

### Step 1: Gather Repository Context
Discover the repository's issue schema before taking any actions.

```bash
# Extract repo owner and name from remote
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

```bash
# List available labels and descriptions
gh label list
# or with curl:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/labels"
```

```bash
# Check for issue templates
cat .github/ISSUE_TEMPLATE/*.md 2>/dev/null
ls .github/ISSUE_TEMPLATE/ 2>/dev/null
```

```bash
# Check existing issues for label patterns
gh issue list --limit 30 --json number,title,labels
```

### Step 2: Read and Analyze the Issue

```bash
# View full issue details
gh issue view <ISSUE_NUMBER>
# or with curl:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/issues/<ISSUE_NUMBER>"
```

Analyze the issue for:
- **Type**: Bug report, feature request, documentation, question, enhancement
- **Severity**: Critical, High, Medium, Low
- **Component**: Backend, Frontend, Security, Network, Agents, C2, Tools
- **Clarity**: Is the issue complete and actionable?

### Step 3: Search for Similar Issues (Deduplication)

```bash
# Search by keywords from the issue title
gh issue list --search "<keywords from title> repo:$OWNER/$REPO"

# Search by label
gh issue list --label "bug" --state all --limit 50

# Search closed issues too (might be duplicates)
gh issue list --state all --search "<relevant terms> repo:$OWNER/$REPO"
```

If a matching open issue is found:
- Suggest closing the new issue as a duplicate
- Link to the original issue
- Do NOT close without confirming the match

If a matching closed issue is found:
- Note it as previously addressed
- Ask if the issue still persists

### Step 4: Apply Triage Actions (Evidence-Based Only)

**Apply labels based on issue content:**
```bash
# Bug labels
gh issue edit <NUMBER> --add-label "bug"

# Priority labels (only if clearly justified by the issue)
gh issue edit <NUMBER> --add-label "priority:critical"
gh issue edit <NUMBER> --add-label "priority:high"
gh issue edit <NUMBER> --add-label "priority:medium"
gh issue edit <NUMBER> --add-label "priority:low"

# Component labels
gh issue edit <NUMBER> --add-label "backend"
gh issue edit <NUMBER> --add-label "frontend"
gh issue edit <NUMBER> --add-label "security"
gh issue edit <NUMBER> --add-label "network"
gh issue edit <NUMBER> --add-label "agents"
gh issue edit <NUMBER> --add-label "documentation"

# Status labels
gh issue edit <NUMBER> --add-label "needs-triage"
gh issue edit <NUMBER> --add-label "needs-reproduction"
gh issue edit <NUMBER> --add-label "needs-clarification"
```

**Assign the issue when appropriate:**
```bash
# Assign to team member
gh issue edit <NUMBER> --add-assignee username

# Suggest assignment to Copilot / cloud agent for autonomous handling
# (when the issue is well-defined and executable)
```

**Change issue state:**
```bash
# Close as duplicate
gh issue close <NUMBER> --reason "not planned"
# Then comment with reference to the original issue

# Close as spam/gibberish
gh issue close <NUMBER> --reason "not planned"
# Comment explaining why
```

### Step 5: Request Missing Information

If the issue lacks critical information needed to act on it:
```bash
gh issue comment <NUMBER> --body "Thanks for the report. To help investigate, could you provide:

1. **Steps to reproduce** — exact commands or actions that trigger the issue
2. **Expected behavior** — what you expected to happen
3. **Actual behavior** — what actually happened
4. **Environment** — OS, Python version, Quantum C2 version
5. **Logs** — any relevant error output or logs

This will help us triage and resolve the issue faster."
```

### Step 6: Comment Only When Necessary

Comment on the issue when:
- You need information from the author (above)
- You are closing as duplicate (always link the original)
- You are closing as spam/gibberish (brief explanation)
- You are assigning to a cloud agent (explain why)
- You made significant triage changes

Do NOT comment for routine label/assignment changes that the author doesn't need to see.

## Issue Type Classification

| Type | Labels | Action |
|------|--------|--------|
| Bug (confirmed) | `bug`, `priority:<level>` | Assign or queue for fix |
| Bug (needs repro) | `bug`, `needs-reproduction` | Request steps to reproduce |
| Feature request | `enhancement`, `feature` | Assess feasibility |
| Documentation | `documentation` | Route to docs team |
| Duplicate | `duplicate` | Close with reference |
| Spam / gibberish | — | Close as not planned |
| Question | `question` | Answer or close |
| Needs info | `needs-clarification` | Request details from author |

## Cloud Agent Suitability Assessment

Suggest assigning to Copilot / cloud agent when the issue:
- Has clear, reproducible steps
- Has well-defined acceptance criteria
- Is scoped to a single component
- Does not require architectural decisions
- Is a bug fix or straightforward feature

Comment when suggesting cloud agent assignment:
```bash
gh issue comment <NUMBER> --body "This issue is well-scoped and has clear reproduction steps. Suitable for autonomous handling by a cloud agent. Assigned to Copilot for execution."
```

## Duplicate Detection Criteria

An issue is likely a duplicate when:
- Title is substantially the same as an existing issue
- Description matches an existing issue's content
- The same root cause is described in another open issue
- A fix for the same problem was already merged (check closed issues with related PRs)

When closing a duplicate:
```bash
gh issue close <NUMBER> --reason "not_planned"
gh issue comment <NUMBER> --body "This appears to be a duplicate of #<ORIGINAL_NUMBER>. Please follow that issue for updates."
```

## Notes
- Only apply labels and actions supported by evidence from the issue content
- Never hallucinate label names — discover them from the repo first
- Never assume metadata values not present in the issue
- When in doubt, mark as `needs-triage` and request more information
- Check `.learnings/ERRORS.md` for previously triaged issue patterns
- Review `gh issue list --label "needs-triage"` for backlog items
