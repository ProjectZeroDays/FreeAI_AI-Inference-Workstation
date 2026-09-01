---
name: skill-creator
description: Meta-skill for creating new skills within the Quantum C2 project. Use when the user asks to create a skill, add a new skill, build a skill template, generate skill scaffolding, or extend the agent's capabilities with modular knowledge packages. Triggers on "create skill", "new skill", "build skill", "add skill", "skill template", "scaffold skill".
---

# Skill Creator

Meta-skill for generating new skills. Produces valid SKILL.md files with proper frontmatter, bundled resources, and project-aware structure.

## Skill Structure

Every skill lives in `skills/<skill-name>/` and contains:

```
skills/<skill-name>/
├── SKILL.md          (required: frontmatter + instructions)
├── scripts/          (optional: executable code)
├── references/       (optional: domain docs loaded on demand)
└── assets/           (optional: templates, images, configs)
```

## SKILL.md Format

```yaml
---
name: skill-name
description: What this skill does and when to trigger it. Include specific trigger phrases.
---
# Skill Title
Instructions here.
```

**Description rules:**
- Include both what it does AND when to use it
- List trigger phrases explicitly
- Keep under 200 words

## Creation Process

### 1. Determine skill scope
- What task does this skill automate?
- What triggers it?
- What scripts/references/assets does it need?

### 2. Run init script
```bash
python skills/skill-creator/scripts/init_skill.py <skill-name>
```
Creates the directory scaffold with SKILL.md template.

### 3. Write SKILL.md body
- Use imperative form ("Run the script", not "You should run")
- Include concrete examples
- Reference bundled files with relative paths
- Keep under 500 lines

### 4. Add bundled resources
- **scripts/**: Executable code for deterministic tasks
- **references/**: Domain docs loaded on demand
- **assets/**: Templates and files used in output

### 5. Validate
```bash
python skills/skill-creator/scripts/validate_skill.py skills/<skill-name>
```

## Progressive Disclosure

1. **Metadata** (always loaded): name + description (~100 words)
2. **SKILL.md body** (on trigger): instructions (<5k words)
3. **Bundled resources** (as needed): unlimited

Keep SKILL.md lean. Move detailed reference material to `references/` files.

## Naming Convention

- Use kebab-case: `threat-intel`, not `threat_intel` or `ThreatIntel`
- Be descriptive: `compliance-checker` not `checker`
- Include domain: `network-monitoring` not just `monitor`

## Anti-Patterns

- Don't create README.md, CHANGELOG.md, or other auxiliary files
- Don't duplicate info between SKILL.md and references
- Don't include "When to Use" sections in body (put in description)
- Don't exceed 500 lines in SKILL.md
