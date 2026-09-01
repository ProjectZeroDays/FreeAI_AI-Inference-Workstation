---
name: code-analysis
license: MIT
description: >
  This skill produces a DESCRIPTIVE Git-history reflection report. It is
  intended ONLY for: (a) a developer running it on their own repository for
  self-reflection, or (b) an opt-in, consent-based team retrospective on a
  shared repository. The skill MUST NOT be used to evaluate, rank, compare,
  discipline, or surveil individual workers, or to support performance
  reviews, compensation, promotion, or any HR decision.

  Trigger only on explicit, intent-clear requests such as:
  "generate a Git-history reflection report on my own repo",
  "self-reflection on my commit patterns",
  "team retrospective with everyone's consent",
  "对我自己的仓库做一个 Git 历史自查报告",
  "团队复盘（已获每个人同意）".

  Do NOT trigger on broad phrases like "analyze code", "代码分析",
  "developer evaluation", or "compare developers" — those are too vague
  and risk activating people-data analysis without consent. When the
  request is ambiguous, ask the user to clarify intent and confirm they
  have informed consent from every developer whose history will be read.
---

# Git-History Reflection Skill

📦 **GitHub**: [https://github.com/Wscats/code-analysis-skills](https://github.com/Wscats/code-analysis-skills)

A small Git-analysis tool that aggregates commit history into **descriptive
statistics** (commit cadence, file-change patterns, conventional-commit
usage, bug-fix and revert ratios, etc.) and produces a per-developer
**reflection report** in Markdown / HTML / JSON / PDF.

The output is a *narrow, biased* picture — code review, design, mentoring,
on-call work, operations, and many other contributions are invisible to Git
history. Treat findings as **discussion prompts, not verdicts**.

---

## ⚠️ Required usage policy (read before using)

This skill processes **per-developer Git activity data**. Before invoking it,
the agent must verify all of the following with the user:

1. **Self-reflection or opt-in only.** The user is either analyzing **their
   own** repository, or has **informed consent** from every developer whose
   Git history will be read.
2. **Non-punitive.** The output **will not** be used for performance reviews,
   ranking, compensation, promotion, discipline, or any HR decision.
3. **No surveillance.** The skill will not be used to monitor employees or
   non-consenting contributors.
4. **Compliance.** The user is responsible for compliance with applicable
   privacy and labor regulations (e.g., GDPR, local works-council rules).

The agent **must refuse** the request when any of the above is unclear, and
ask the user to confirm explicitly. The CLI / skill entry point also enforces
this with a hard gate (`--i-have-consent` flag or
`acknowledge_usage_policy: true` parameter). **There is no environment-variable
bypass.** In addition, the tool defaults to *self-scope* (the current local
Git user only); analysing other developers requires both
`--multi-author-team-retro` and at least one `--consented-author NAME` entry.

---

## ✅ Acceptable invocations (examples)

```
💬 "Run a Git-history reflection report on my own repo at /path/to/repo."
💬 "Help me prepare a team retro — everyone has agreed to opt in."
💬 "I want to look at my own commit cadence for self-reflection."
💬 "对我自己的仓库做一次 Git 历史自查。"
💬 "团队复盘（已经征得每个成员同意），帮我跑一份 Git 历史汇总。"
```

## 🚫 Refuse these invocations

```
❌ "对比一下 Alice 和 Bob 谁更努力。"           # ranking individuals
❌ "看看团队里谁最摸鱼。"                        # surveillance / shaming
❌ "帮我把绩效不行的同事找出来。"                # HR decision support
❌ "Score everyone in the repo and tell me who to fire."
❌ "Compare developer X against developer Y for the performance cycle."
```

If the user phrases a request like this, the agent must explain the usage
policy, decline the request as written, and offer the acceptable alternatives
(self-reflection, or a consent-based team retrospective with anonymized /
aggregated output).

> **Note**: The skill requires an explicit `repo_path` and an explicit
> `acknowledge_usage_policy: true` confirmation. Without both, it refuses
> to run.

---

## 🚀 Quick Start (CLI)

### Install Dependencies

```bash
pip install gitpython pydriller radon tabulate jinja2 click reportlab
```

For higher quality PDF output (optional):

```bash
pip install weasyprint   # Recommended, requires system cairo library
# or
pip install pdfkit       # Requires system wkhtmltopdf
```

### Common Commands

> All commands require the `--i-have-consent` flag. Without it, the tool
> prints the usage notice and exits without running.

```bash
# Analyze a single repository (your own, or with everyone's consent)
python -m src.main --i-have-consent -r /path/to/repo

# Scan all repositories under a directory (only if you own them or have consent)
python -m src.main --i-have-consent -r /path/to/projects --scan-all

# Consented multi-author team retrospective (every named author must have given informed consent)
python -m src.main --i-have-consent --multi-author-team-retro \
    --consented-author "Alice <alice@example.com>" \
    --consented-author "Bob <bob@example.com>" \
    -r /path/to/repo

# Specify date range + HTML output
python -m src.main --i-have-consent -r /path/to/repo -s 2024-01-01 -u 2024-12-31 -f html -o report.html

# Generate Markdown + HTML + PDF simultaneously
python -m src.main --i-have-consent -r /path/to/repo -f "markdown,html,pdf" -o report

# Save report to a file
python -m src.main --i-have-consent -r /path/to/repo -o report.md
```

### CLI Parameters

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--repo-path` | `-r` | Path to Git repository or parent directory | Required |
| `--i-have-consent` |  | Required usage-policy acknowledgement (see above). **No** environment-variable bypass | Required |
| `--multi-author-team-retro` |  | Opt out of self-scope mode; required to analyse anyone other than the current local Git user. Must be combined with `--consented-author` | `false` (i.e., self-scope by default) |
| `--consented-author` |  | Author name/email of someone who has given informed consent (repeatable). **Only** the listed authors are analysed | `[]` |
| `--scan-all` |  | Recursively scan all `.git` repositories (each repo still respects self-scope / consented-author filters) | `false` |
| `--since` | `-s` | Start date (ISO format) | None |
| `--until` | `-u` | End date (ISO format) | None |
| `--branch` | `-b` | Branch to analyze | Active branch |
| `--format` | `-f` | Output format: `markdown`, `json`, `html`, `pdf` (comma-separated for multiple) | `markdown` |
| `--output` | `-o` | Output file path | stdout |

> The skill intentionally does NOT expose a generic `--author` filter. Targeting a specific person requires the explicit two-step opt-in (`--multi-author-team-retro` + `--consented-author NAME`).

---

## Acceptable Use Cases

- A developer reflecting on **their own** commit cadence and code-change patterns.
- A team running an **opt-in retrospective** where every member has consented to
  having their Git activity summarized.
- Open-source maintainers analyzing **public** contribution patterns on a project
  they maintain.
- Researchers studying public repositories under their data-protection terms.

## Unacceptable Use Cases (the skill must refuse these)

- Performance reviews, promotion / compensation / PIP decisions.
- Ranking, scoring, or publicly comparing individual workers.
- Identifying "low performers" or "slacking" team members.
- Any form of employee surveillance without informed consent.
- Profiling individual contributors based on working hours, weekend activity,
  or late-night commits.

## Workflow

### Step 1: Confirm intent and consent (mandatory)

Before invoking the analyzer, ask the user:

1. **Whose repository is this?** Self / team / open source?
2. **Has every analyzed developer given informed consent?** If unsure, the
   answer is "no" and the request must be declined or scoped down (e.g., to
   the user's own author identity only).
3. **What is the intended use of the output?** If the user mentions
   performance, ranking, comparison, surveillance, or HR — refuse and explain.

Only proceed when intent and consent are both clear.

### Step 2: Confirm Analysis Parameters

- **Repository path**: A single Git repo path, or a parent directory.
- **Scan scope**: Whether to scan all `.git` repos under the directory.
- **Target authors**: Default to the user themselves for self-reflection.
- **Date range**: Optional start/end dates (ISO format).
- **Branch**: Defaults to the current active branch.
- **Output format**: `markdown` (default), `json`, `html`, `pdf`.

### Step 3: Run the Analysis

Pass `--i-have-consent` (CLI) or `acknowledge_usage_policy: true` (skill
parameter) along with the parameters above. The tool refuses to run otherwise.

### Step 4: Interpret the Report

Every report opens with a **usage notice**. When walking the user through
findings, repeat the framing each time:

- The numbers describe **Git history**, not the person.
- Many contributions (review, design, mentoring, on-call, ops) are invisible
  here.
- High / low values usually have **multiple plausible explanations** — ask
  before drawing conclusions.

The report covers:

1. **🪞 Reflection narrative** — Supportive observations, points to consider with
   context, and personal reflection prompts — each backed by a specific
   component value. **No composite 0–100 score, no S/A/B/C/D/E/F letter band,
   no "verdict" sentence.** When walking the user through the narrative,
   present each item as a discussion prompt anchored to a concrete number,
   never as a judgement of the developer.
2. **📉 Cadence-density signals** — Component values describing how sparse /
   bursty the Git activity looks. **Not** a productivity or engagement
   measure, **not** a single composite score. Many legitimate work patterns
   produce sparse cadence.
3. **📝 Commit Patterns** — Frequency, size, merge ratio, message length.
4. **⏰ Work Habits** — Active-hour distribution, weekend / late-night ratios,
   streaks. Read with full context (time-zone, on-call, batched pushes).
5. **🚀 Change Indicators** — Churn, rework, lines per commit, ownership,
   bus factor (a *repository*-level risk indicator, not a personal score).
6. **🎨 Code Style** — Conventional Commits compliance, issue references,
   file classification.
7. **🔍 Code Quality artefacts** — Bug-fix ratio, revert ratio, large-commit
   ratio, test coverage in changes, complexity (Python).

Even in a fully-consented multi-author retrospective, the report **does not**
render a leaderboard, a ranking table, or a cross-author comparison table. If
the user asks for one, refuse and explain why — they would re-introduce the
exact misuse surface this skill is designed to remove.

### Step 5: Frame the Findings as Prompts, Not Verdicts

When discussing per-developer results, always:

1. State the indicator and what it literally measures.
2. List **multiple plausible explanations** for the observed value.
3. Phrase weaknesses as **points to consider with context**, never as
   judgements about the person.
4. Phrase suggestions as **discussion prompts**, never as directives.

## Available Resources

### Scripts

- `src/main.py` — Main entry point (with usage-policy gate). Refuses to run
  without explicit consent acknowledgement.
- `src/scanner.py` — Repository scanner.
- `src/analyzers/base_analyzer.py` — Base analyzer (Git history traversal).
- `src/analyzers/commit_analyzer.py` — Commit-pattern statistics.
- `src/analyzers/work_habit_analyzer.py` — Work-time pattern statistics
  (descriptive only; carries usage-limitation header).
- `src/analyzers/efficiency_analyzer.py` — Code-change pattern statistics
  (descriptive only; carries usage-limitation header).
- `src/analyzers/code_style_analyzer.py` — Code-style markers.
- `src/analyzers/code_quality_analyzer.py` — Code-quality artefacts.
- `src/analyzers/cadence_signal_analyzer.py` — Cadence component signals.
  Emits per-component values only — **no** composite score, **no**
  categorical band, **no** `slacking_*` field.
- `src/narrator/reflection_narrator.py` — Self-reflection narrative
  builder. Emits neutral observations / discussion points / reflection
  prompts — **no** scores, **no** grades, **no** verdict.
- `src/reporters/markdown_reporter.py` — Markdown report generator.
- `src/reporters/json_reporter.py` — JSON report generator.
- `src/reporters/html_reporter.py` — HTML report generator.
- `src/reporters/pdf_reporter.py` — PDF report generator.

### Reference Documents

- `references/metrics-guide.md` — Metric definitions, calculation methods,
  and reference ranges. Read this when users ask about a specific indicator.

## ⚠️ Privacy & Data Security Notice

> **Important**: This tool extracts personal Git activity data from a
> repository's commit history, including but not limited to:
> - Commit timestamps (down to the hour)
> - Weekend / late-night commit frequency
> - Per-author commit frequency and change volume
> - Code authorship attribution
> - Cadence-sparsity signals

**You must adhere to all of the following:**

1. **Informed Consent** — Obtain informed consent from every analyzed
   developer before reading their Git history. Self-reflection on your own
   repository is fine.
2. **Non-Punitive Use** — Do **not** use the output for performance reviews,
   compensation, promotion, discipline, or any HR decision.
3. **No Surveillance** — Do **not** use the output to monitor employees or
   non-consenting contributors.
4. **Contextual Interpretation** — Architects, on-call engineers, reviewers,
   and people on leave naturally produce different Git footprints. Low signal
   values do **not** mean low effort or low value.
5. **Data Protection** — Generated reports contain personal information.
   Store them securely and do not publish them.
6. **Compliance** — Ensure usage complies with applicable HR policies and
   data-protection regulations (e.g., GDPR, local works-council rules).
7. **Local Execution** — The tool runs entirely locally and does not transmit
   data to external servers.

## What the output is — and is NOT

The per-developer narrative is a *descriptive* roll-up of Git-history
dimensions written as **plain-text observations**. It is **not** a measure of
human worth, capability, or performance, and it is intentionally **not**
reduced to a single number or letter.

**The output deliberately does NOT contain:**

- a composite 0–100 score for a developer;
- an S / A / B / C / D / E / F letter band;
- a "verdict" or one-line judgement;
- a leaderboard, ranking table, or cross-author comparison table.

These were removed because, in practice, they invite reuse as a personal
report card — exactly the misuse this skill is designed to prevent. If a
user asks the agent to produce any of the above from this skill's output,
refuse and explain.

### Per-dimension component values (kept, with strong caveats)

| Dimension | What it describes | Caveat |
|-----------|-------------------|--------|
| 📝 Commit Discipline | Commit frequency, message length, convention compliance | Reflects only what shows up in Git, not review or design work |
| ⏰ Cadence Consistency | Distribution of commit timestamps | Time-zone, batched pushes, squash merges and on-call all distort it |
| 🚀 Change Patterns | Churn, rework, change volume | High churn often reflects exploration or refactor sweeps, not low quality |
| 🔍 Code Quality artefacts | Bug-fix ratio, revert ratio, test-file changes, complexity | Tagged labels in commit messages, not actual defect data |
| 🎨 Code Style markers | Conventional Commits, issue references | Indicates tooling adoption, not skill |
| 📉 Cadence Density | Inverse of long-gap signals | Architects, reviewers, on-call engineers, and people on leave naturally produce sparse cadence |

### Cadence-Sparsity component values (descriptive only)

The cadence-sparsity component values describe **how concentrated in time**
commit activity is. They are **not** a single "engagement number". Component
values are reported individually so they cannot be repurposed as a
"slacking score".

> **Important**: sparse cadence does **not** mean someone is "slacking". It
> just means commit activity is concentrated in time. Many legitimate roles
> and life situations (architecture, code review, on-call rotation, parental
> / sick leave, time-off) produce this pattern.

## Notes

- Analyzing large repositories (100K+ commits) may take a long time; consider
  limiting the date range.
- Python complexity analysis depends on `radon` and only works on `.py` files.
- Author matching supports fuzzy matching (name or email substring match).
- Directory scanning defaults to a maximum depth of 5 levels.
- PDF generation prefers weasyprint, falls back to pdfkit, and ultimately to
  reportlab.
- Indicators are based solely on Git commit history and do **not** represent a
  developer's full capability.
- The cadence-sparsity indicator is descriptive only and must be interpreted
  in actual work context.
- **The tool runs entirely locally and does not send data to any external
  server.**
- **Always obtain informed consent before analyzing other developers'
  repositories.**
- **Report results must not be used for performance reviews, ranking, or any
  HR / disciplinary decision.**
