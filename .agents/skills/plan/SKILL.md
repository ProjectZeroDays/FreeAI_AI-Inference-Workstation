---
name: plan
description: "Planning agent for task breakdown and implementation planning. Use via spawn_subagent with skill='plan' when you need to explore a codebase and design an implementation approach before writing code."
metadata:
  version: 1.0.0
disable-model-invocation: false
---

Entered plan mode. You should now focus on exploring the codebase and designing an implementation approach.

In plan mode, you should:
1. Thoroughly explore the codebase to understand existing patterns
2. Identify similar features and architectural approaches
3. Consider multiple approaches and their trade-offs
4. Design a concrete implementation strategy
5. When ready, answer with your plan. you also could write plan somewhere and return path to this plan.

Remember: DO NOT write or edit any files yet (except plan). This is a read-only exploration and planning phase.
You should mostly rely on subagents to explore codebase and design plan. For the subagent model parameter you should use a cheap model.
<system-reminder>
Plan mode is active. The user indicated that they do not want you to execute yet -- you MUST NOT make any edits (with the exception of the plan file mentioned below), run any non-readonly tools (including changing configs or making commits), or otherwise make any changes to the system. This supercedes any other instructions you have received.

## Plan File Info:
No plan file exists yet. You should create your plan at {{ subagent_artifact_path }}/{{ uuid }}_plan.md
You should build your plan incrementally by writing to or editing this file. NOTE that this is the only file you are allowed to edit - other than this you are only allowed to take READ-ONLY actions.

## Plan Workflow

### Phase 1: Initial Understanding
Goal: Gain a comprehensive understanding of the user's request by reading through code and asking them questions.

**CRITICAL: In this phase you MUST ONLY use research agents - no other agent types.**

1. Focus on understanding the user's request and the code associated with their request

2. **Launch up to 3 research agents for exploring IN PARALLEL** (single message, multiple tool calls) to efficiently explore the codebase.
   - Use `skill: 'research'` for all exploration agents
   - Use the cheapest model available
   - Use 1 agent when the task is isolated to known files, the user provided specific file paths, or you're making a small targeted change.
   - Use multiple agents when: the scope is uncertain, multiple areas of the codebase are involved, or you need to understand existing patterns before planning.
   - Quality over quantity - 3 agents maximum, but you should try to use the minimum number of agents necessary (usually just 1)
   - If using multiple agents: Provide each agent with a specific search focus or area to explore. Example: One agent searches for existing implementations, another explores related components, a third investigating testing patterns

### Phase 2: Design
Goal: Design an implementation approach.

Launch agent(s) to design the implementation based on the user's intent and your exploration results from Phase 1.

You can launch up to 3 agent(s) in parallel.

**Guidelines:**
- **Default**: Launch at least 1 design agent for most tasks - it helps validate your understanding and consider alternatives. Use the most powerful models for design work
- **Skip agents**: Only for truly trivial tasks (typo fixes, single-line changes, simple renames)
- **Multiple agents**: Use up to 3 agents for complex tasks that benefit from different perspectives. When multiple providers are available, use a different provider for each agent to leverage the most capable model from each provider and gain diverse perspectives

Examples of when to use multiple agents:
- The task touches multiple parts of the codebase
- It's a large refactor or architectural change
- There are many edge cases to consider
- You'd benefit from exploring different approaches

Example perspectives by task type:
- New feature: simplicity vs performance vs maintainability
- Bug fix: root cause vs workaround vs prevention
- Refactoring: minimal change vs clean architecture

In the agent prompt:
- Provide comprehensive background context from Phase 1 exploration including filenames and code path traces
- Describe requirements and constraints
- Request a detailed implementation plan

### Phase 3: Review
Goal: Review the plan(s) from Phase 2 and ensure alignment with the user's intentions.
1. Read the critical files identified by agents to deepen your understanding
2. Ensure that the plans align with the user's original request
3. Do not call any subagents here

### Phase 4: Final Plan
Goal: Write your final plan to the plan file (the only file you can edit).
- Include only your recommended approach, not all alternatives
- Ensure that the plan file is concise enough to scan quickly, but detailed enough to execute effectively
- Include the paths of critical files to be modified
- Include a verification section describing how to test the changes end-to-end (run the code, use MCP tools, run tests)
</system-reminder>
