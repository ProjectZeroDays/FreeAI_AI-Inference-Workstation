---
name: repetitive-task-detector
description: Analyzes historical activity and codebase patterns to identify repetitive tasks that can be automated via new skills. Use when the user expresses a desire to reduce workload or when you notice frequent manual repetitions.
---

# Repetitive Task Detector

## Workflow
1. **Analyze Logs**: Scan recent session history for repeated command sequences or prompting patterns.
2. **Codebase Grep**: Look for common "TODO" or "FIXME" markers that share similar theme or implementation pattern.
3. **Pattern Synthesis**: Group related repetitive tasks.
4. **Proposal**: Draft a skill modification proposal including:
   - Name: Proposed name for the new skill.
   - Description: What it automates.
   - Impact:Estimated time or effort saved.
5. **User Review**: Confirm which suggestions generate the most value.

## Guidance
- Focus on tasks that consume meaningfully positive time (more than 15 mins).
- Prefer skills that can be implemented via existing tools or simple scripts.
- Always confirm with the user before beginning implementation of a developed proposal.
