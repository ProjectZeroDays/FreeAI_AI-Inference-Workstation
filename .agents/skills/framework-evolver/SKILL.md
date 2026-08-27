---
name: framework-evolver
description: The "Meta-Skill" for autonomous framework evolution. Monitors the threat landscape and automatically updates the platform's Skills, MCPs, and modules.
---

# Framework Evolver

This skill ensures Pegasus never becomes obsolete.

## Evolution Loop
1. **Horizon Scanning**: Use `research-payloads` to find new techniques and TTPs.
2. **Gap Analysis**: Compare new techniques against current `modules/` and `skills/`.
3. **Auto-Generation**: Create new MCP bridges or update existing logic engines to support the new techniques.
4. **Documentation Sync**: Automatically update `WIKI.md` and the Dashboard to reflect new capabilities.
5. **Verification**: Deploy a test-instance of the updated framework to verify stability before pushing to production.

## Implementation Authority
- This skill has permission to Edit and Write to `.mimocode/skills/` and `plugins/` to implement its findings.
