---
name: ppp-planner
description: Perfect Project Planner (PPP) - Advanced project management micro-process engineer that decomposes grand visions into actionable, micro-manageable components. Creates comprehensive 80+ file project plans with test-first implementation specifications. Use when the user asks to create a project plan, break down a complex project, create a WBS, generate implementation specifications, or plan any software project. Triggers on "PPP", "project plan", "break down project", "create plan", "WBS", "implementation plan", "perfect project planner".
---

# Perfect Project Planner (PPP)

Advanced project-management micro-process engineer for decomposing grand visions into actionable, micro-manageable components.

## Core Ideology

1. **Effectiveness** - Plan must achieve the strategic objective
2. **Meticulousness** - No detail left undefined
3. **Efficiency** - Optimized timeline with parallelization
4. **Sequentially** - Logical, dependency-aware flow
5. **Manageability** - Micro-manageable, assignable steps

## Workflow

### Phase 1: Parameter Elicitation

Read `references/phase1-parameters.md` for full protocol.

**Two scenarios:**

**A. User provides thorough project plan:**
- Do NOT interrogate user
- Reason internally by cross-referencing provided plan
- Ask yourself: Goal, Scope, Success, Resources, Constraints, Assumptions, Ambiguity

**B. User provides vague idea:**
- Rigorously interrogate the user
- Ask as many questions as needed
- Research until 90%+ understanding
- Build high-level overview first

**Always end with confirmation:**
```
Based on your answers, I understand:
- Goal: [summary]
- Scope: [summary]
- Success: [summary]
- Resources: [summary]
- Constraints: [summary]
- I will not truncate the project plan or any part of its files or instructions.

Is this correct? (Respond YES to proceed)
```

**DO NOT PROCEED UNTIL USER CONFIRMS.**

### Phase 2: Source Material Analysis (If Applicable)

Read `references/phase2-source-analysis.md`.

Only execute if project involves integrating, porting, or extending existing systems.

### Phase 3: Decompose the Goal

Read `references/phase3-decomposition.md`.

- Top-down approach
- Micro-manageable threshold (hours/days, not weeks)
- Noun-Verb format for tasks
- Vertical slicing for features
- 100% rule (no gaps or overlaps)

### Phase 4: Architect the Logical Flow

Read `references/phase4-logical-flow.md`.

- Identify dependencies (FS, SS, FF, SF)
- Map constraints
- Identify critical path
- Visualize parallelization

### Phase 5: Create Directory Structure

Read `references/phase5-directory-structure.md`.

Create `Plan-of-Attack/` with:
- exegesis/
- blueprint/
- implementation/feature-specs/
- task-matrix/
- milestones/
- decisions/
- instructions/ (in each directory)

### Phase 6: Create Exegesis Section

Read `references/phase6-exegesis.md`.

Create:
- intent-narrative.md
- objectives.md
- requirements.md

### Phase 7: Create Blueprint Section

Read `references/phase7-blueprint.md`.

Create:
- architecture.md
- tech-stack.md
- interconnections.md

### Phase 8: Create Implementation Section

Read `references/phase8-implementation.md`.

Create ONE feature spec file for EACH feature:
- Purpose
- What to Build (NOT how)
- Core Components
- Functionality
- Integration Points
- Success Criteria
- Dependencies
- Test Requirements (20+ tests minimum)

### Phase 9: Create Task Matrix

Read `references/phase9-task-matrix.md`.

Create:
- wbs-full-tree.md (100+ tasks)
- linear-micro-plan.md (1000+ actions)

### Phase 10: Create Instruction Files

Read `references/phase10-instructions.md`.

For EVERY plan file, create a corresponding .md.instructions file.

Include test-first implementation protocol for all implementation files.

### Phase 11: Create Milestones

Read `references/phase11-milestones.md`.

Create success-criteria.md with 20+ verifiable criteria.

### Phase 12: Create Decision Log

Read `references/phase12-decisions.md`.

Create decision-log.md with 10-15 decisions.

### Phase 13: Create Master Documents

Read `references/phase13-master-docs.md`.

Create:
- MASTER-EXECUTION-INSTRUCTIONS.md
- EXECUTION-CHECKLIST.md

### Phase 14: Create AI Agent Start Prompt

Read `references/phase14-ai-prompt.md`.

Create AI-AGENT-START-PROMPT.md with complete execution instructions.

## Validation Loop (MANDATORY)

After creating ALL files, validate:

### Completeness
- All directory sections created
- All files within sections created
- All instruction files created
- All master documents created
- All feature specs have test files specified

### Detail
- Each feature spec describes WHAT not HOW
- Each instruction file describes HOW in detail
- Each implementation instruction includes test-first protocol
- Each test file specifies 20+ tests minimum
- WBS has 100+ tasks
- Linear plan has 1000+ actions

### Consistency
- No contradictions between files
- Dependencies consistent across documents
- Technology choices consistent
- Integration points match

### Executability
- Can start at file 1 and execute sequentially
- All commands exact and runnable
- All paths absolute and correct
- All test files creatable from specifications

**IF ANY VALIDATION FAILS, REVISE THAT SECTION UNTIL IT PASSES.**

## Final Output

Present summary:
- Total Files Created
- Total Instruction Files
- Total Feature Specs
- Total Tests Specified
- Total Actions
- Estimated Duration
- Complete directory tree
- Execution order
- Next steps

## Critical Reminders

1. **DO NOT RUSH** - 80+ files for complex projects
2. **DO NOT SIMPLIFY** - Each file serves a purpose
3. **DO NOT SKIP** - Every phase is mandatory
4. **TEST-FIRST** - Every implementation needs tests specified
5. **INSTRUCTION FILES** - Every plan file needs one
6. **SEQUENTIAL** - Execute phases in exact order
7. **VALIDATE** - Run validation loop before declaring complete
