# 📊 Code Analysis Skills

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.2.0-orange)](skill.yaml)

A **Git-history reflection report generator**. It scans Git repositories and aggregates commit history into multi-dimensional descriptive statistics — covering **commit patterns**, **commit timing**, **change patterns**, **code style**, and **code-quality artefacts**.

> ⚠️ **Acceptable use only:** (a) self-reflection on your own repository, or (b) opt-in team retrospectives with informed consent from every member.
> **Strictly NOT for** performance reviews, individual ranking, compensation / promotion / discipline decisions, or surveillance of non-consenting contributors.
> See “Usage Policy” below.

---

## ✨ Features

- 🔍 **Repository Scanning** — Analyze a single Git repo or recursively discover all `.git` repos under a directory
- 📝 **Commit Patterns** — Frequency, size distribution, merge ratio, commit message length
- ⏰ **Commit Timing Statistics** — Distribution by hour / day-of-week, weekend / late-night ratios, longest streaks (descriptive only — read with full context)
- 🚀 **Change Indicators** — Code churn rate, rework ratio, Bus Factor (a *repository-level* risk indicator), file ownership
- 🎨 **Code Style** — Language distribution, Conventional Commits compliance, file classification
- 🔎 **Code Quality artefacts** — Bug-fix ratio, revert frequency, large-commit ratio, test coverage in changes, Python complexity (via radon)
- 📉 **Cadence-Density Signals** — Per-dimension component values describing how sparse / bursty the Git activity looks. **Not** a productivity or engagement measure, **not** a composite score.
- 🪞 **Reflection Summary** — Supportive observations, points to consider with context, and personal reflection prompts. **No** composite score, **no** grade band, **no** verdict — by design.
- 🔒 **Self-scope by default** — Only analyses commits authored by the current local Git user. Multi-author analysis requires an explicit second opt-in (`--multi-author-team-retro` plus `--consented-author NAME` for every included person) and never produces a leaderboard or cross-author comparison table.
- 📄 **Multiple Output Formats** — Markdown, JSON, styled HTML, and PDF reports. Every output carries an explicit usage notice.

## 📦 Installation

### Prerequisites

- Python 3.9+
- Git

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install gitpython pydriller radon tabulate jinja2 click pyyaml reportlab
```

For higher quality PDF output, optionally install:

```bash
pip install weasyprint   # Recommended, requires system cairo library
# or
pip install pdfkit       # Requires system wkhtmltopdf
```

## 🚀 Usage

> All commands require the `--i-have-consent` flag. Without it, the tool prints the usage notice and refuses to run.

### Basic Commands

```bash
# Self-reflection / consented team retrospective
python -m src.main --i-have-consent -r /path/to/repo

# Recursively scan a directory for all Git repos (only ones you own / have consent for)
python -m src.main --i-have-consent -r /path/to/projects --scan-all

# Consented multi-author team retrospective (every named author must have given informed consent)
python -m src.main --i-have-consent --multi-author-team-retro \
    --consented-author "Alice <alice@example.com>" \
    --consented-author "Bob <bob@example.com>" \
    -r /path/to/repo

# Filter by date range
python -m src.main --i-have-consent -r /path/to/repo -s 2024-01-01 -u 2024-12-31

# Generate HTML report
python -m src.main --i-have-consent -r /path/to/repo -f html -o report.html

# Generate Markdown + HTML + PDF simultaneously
python -m src.main --i-have-consent -r /path/to/repo -f "markdown,html,pdf" -o report

# Generate PDF report
python -m src.main --i-have-consent -r /path/to/repo -f pdf -o report.pdf

# Save Markdown report to file
python -m src.main --i-have-consent -r /path/to/repo -o report.md
```

### CLI Options

| Option | Description | Default |
|---|---|---|
| `-r, --repo` | Path to Git repo or parent directory | *(required)* |
| `--i-have-consent` | Required. Confirms you have read the usage policy, have informed consent from every analyzed developer, and will NOT use the output for performance / ranking / HR decisions. **No** environment-variable bypass | *(required)* |
| `--multi-author-team-retro` | Opt out of self-scope mode and run a fully-consented team retrospective. Requires at least one `--consented-author` entry | `false` (i.e., self-scope by default) |
| `--consented-author NAME` | Author name/email of someone who has given informed consent to be included in this retrospective (repeatable). **Only** the listed authors are analysed | `[]` (in self-scope mode, only the current local Git user is analysed) |
| `--scan-all` | Recursively scan for all `.git` repos (each repo still respects self-scope / consented-author filters) | `false` |
| `-s, --since` | Start date (ISO format: `YYYY-MM-DD`) | — |
| `-u, --until` | End date (ISO format: `YYYY-MM-DD`) | — |
| `-b, --branch` | Branch to analyze | Current branch |
| `-f, --format` | Output format(s): `markdown`, `json`, `html`, `pdf` (comma-separated for multiple) | `markdown` |
| `-o, --output` | Output file path (base name for multiple formats) | stdout |

> **Note**: this tool intentionally does NOT expose a `-a/--author` filter. Analysing people other than the current local Git user requires the explicit two-step opt-in above (`--multi-author-team-retro` + `--consented-author NAME`).

## 📁 Project Structure

```
code-analysis-skills/
├── src/
│   ├── main.py                 # CLI entry point
│   ├── scanner.py              # Repository scanner (single & recursive)
│   ├── analyzers/
│   │   ├── base_analyzer.py    # Base analyzer with Git traversal & author filtering
│   │   ├── commit_analyzer.py  # Commit pattern analysis
│   │   ├── work_habit_analyzer.py  # Work habit analysis
│   │   ├── efficiency_analyzer.py  # Development efficiency analysis
│   │   ├── code_style_analyzer.py  # Code style analysis
│   │   ├── code_quality_analyzer.py # Code quality artefacts
│   │   └── cadence_signal_analyzer.py # Cadence component signals (no composite score, no band, no ranking)
│   ├── narrator/
│   │   └── reflection_narrator.py  # Self-reflection narrative builder (neutral observations / discussion points / reflection prompts; no scores)
│   ├── reporters/
│   │   ├── base_reporter.py    # Reporter base class
│   │   ├── markdown_reporter.py # Markdown report generator
│   │   ├── json_reporter.py    # JSON report generator
│   │   ├── html_reporter.py    # Styled HTML report generator
│   │   └── pdf_reporter.py     # PDF report generator
│   └── utils/
│       └── helpers.py          # Utility functions
├── tests/
│   ├── test_analyzers.py       # Analyzer unit tests
│   └── test_scanner.py         # Scanner unit tests
├── references/
│   └── metrics-guide.md        # Metrics definitions & healthy ranges
├── SKILL.md                    # ClawHub skill definition
├── skill.yaml                  # Skill configuration
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project metadata
└── pytest.ini                  # Test configuration
```

## 📊 Analysis Dimensions

> All dimensions are **descriptive statistics**, not judgements about the person. Every report carries an explicit usage notice at the top.

### 1. 📝 Commit Patterns
- Commit frequency (daily/weekly)
- Commit size (lines added/deleted per commit)
- Merge commit ratio
- Commit message length

### 2. ⏰ Commit Timing Statistics
- Hourly distribution
- Weekend commit percentage (descriptive — read with time-zone / on-call context)
- Late-night commit percentage (22:00–06:00, descriptive only)
- Maximum consecutive commit days

> ⚠️ These numbers reflect **commit timestamps**, not when the developer was working / resting. Time-zone, batched pushes, squash merges, and automation can distort them heavily.

### 3. 🚀 Change Indicators
- Code churn rate (lines deleted / lines added)
- Rework ratio (changes to recently modified files)
- Bus Factor (a **repository-level** risk indicator, not a personal score)
- File ownership distribution

### 4. 🎨 Code Style
- Programming language distribution
- Conventional Commits compliance rate
- File type classification (source / test / config / docs)

### 5. 🔍 Code Quality artefacts
- Bug-fix commit ratio
- Revert commit frequency
- Large-commit ratio
- Test-file coverage in changes
- Python code complexity (Cyclomatic Complexity via radon)

### 6. 📉 Cadence-Density Signals (descriptive only)
- Per-dimension component values describing how **sparse / concentrated** the Git activity looks (cadence sparsity, trivial-change ratio, long-gap ratio, low daily volume, non-code-only commits, late-week skew, add/delete imbalance)
- **No composite 0–100 score is exposed**, so these signals cannot be repurposed as a single "engagement number".

> ⚠️ Sparse cadence does **not** mean someone is "slacking". Architects, reviewers, on-call engineers, and people on leave naturally produce sparse cadence.

### 7. 🪞 Reflection Summary
- Supportive observations, points to consider with context, and personal reflection prompts — each backed by a specific component value
- **No composite 0–100 score, no S/A/B/C/D/E/F letter band, no "verdict" sentence** — these were removed because they invited misuse as a personal report card
- Each per-author result carries a mandatory `interpretation_notice` field that downstream renderers surface in the report

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_analyzers.py
```

## ⚠️ Notes

- Analyzing large repositories (100K+ commits) may take a long time — consider limiting the date range
- Python complexity analysis requires `radon` and only applies to `.py` files
- Author matching supports fuzzy matching (name or email substring match)
- Directory scanning defaults to a maximum depth of 5 levels to avoid deep recursion
- PDF generation prioritizes weasyprint, falls back to pdfkit, then reportlab
- Indicators are based solely on Git commit history and do **not** represent a developer’s full capabilities
- The cadence-sparsity indicator is descriptive only and must be interpreted in context

## ⚠️ Usage Policy (mandatory)

> **Important**: This tool extracts personal Git activity data from a repository’s commit history (timestamps, frequencies, change patterns, etc.).

**You must adhere to all of the following:**

- ✅ The tool runs **entirely locally** and does not transmit any data to external servers
- ✅ Acceptable use is limited to (1) self-reflection on **your own** repository or (2) opt-in team retrospectives where every analyzed developer has given **informed consent**
- ⚠️ **Obtain informed consent** from every analyzed developer before running it on shared / corporate repositories
- 🚫 Output **must NOT** be used for performance reviews, compensation, promotion, discipline, or any HR decision
- 🚫 Output **must NOT** be used for ranking, scoring, or publicly comparing individual workers
- 🚫 Output **must NOT** be used to surveil employees or non-consenting contributors
- 🔒 Generated reports contain personal information — **store securely** and do not share publicly
- 📋 Ensure compliance with your organization’s HR policies and local data-protection regulations (e.g., GDPR, local works-council rules)

**Structural safeguards (not just disclaimers):**

1. **Explicit consent flag (no env-var bypass)** — the CLI requires `--i-have-consent` and the skill entry point requires `acknowledge_usage_policy: true`. There is no environment-variable shortcut.
2. **Self-scope by default** — without further opt-in flags, analysers are locked to the current local Git user. Other authors in the repository are skipped entirely.
3. **Explicit multi-author opt-in** — analysing other people requires both `--multi-author-team-retro` and at least one `--consented-author NAME` entry. The tool refuses to run an implicit whole-repository person-level analysis.
4. **No composite score, grade band, leaderboard, or cross-author comparison** is rendered in any output format, even when multiple consented authors are analysed.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
