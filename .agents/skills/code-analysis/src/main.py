"""
Code Analysis Skills - Main Entry Point

A Git-history *self-reflection* tool. Scans a single Git repository and
produces descriptive statistics about commit cadence, file-change patterns,
code-style markers, and code-quality artefacts (bug-fix commits, reverts,
complexity).

⚠️  IMPORTANT — INTENDED USE & STRUCTURAL SAFEGUARDS

This tool is structurally biased toward *self-reflection*:

  * The default mode is **self-scope only** — the tool reads the current Git
    user's identity (``git config user.name`` / ``user.email``) and refuses
    to analyse any other author unless the caller takes a deliberate, second
    opt-in step.
  * Multi-author analysis requires (a) the ``--i-have-consent`` flag, AND
    (b) the ``--multi-author-team-retro`` flag, AND (c) at least one
    ``--consented-author`` entry. The tool refuses to invoke person-level
    analysers across a whole repository implicitly.
  * Outputs are descriptive *narratives* and per-dimension component values.
    There is no composite 0-100 score, no S/A/B/C/D/E/F band, and no
    cross-author leaderboard or ranking table.
  * Consent acknowledgement is expressed *only* through an explicit CLI flag
    or skill parameter. There is no environment-variable bypass.

The output is a NARROW, BIASED proxy. Code review, design, mentoring,
on-call, ops, and many other contributions are invisible to Git history.
Even with full consent, results MUST NOT be used for performance reviews,
ranking, compensation, promotion, discipline, or any HR decision.
"""

import logging
import os
import subprocess
import sys
from typing import List, Optional, Tuple

import click

from src.scanner import RepoScanner
from src.analyzers.commit_analyzer import CommitAnalyzer
from src.analyzers.work_habit_analyzer import WorkHabitAnalyzer
from src.analyzers.efficiency_analyzer import EfficiencyAnalyzer
from src.analyzers.code_style_analyzer import CodeStyleAnalyzer
from src.analyzers.code_quality_analyzer import CodeQualityAnalyzer
from src.analyzers.cadence_signal_analyzer import CadenceSignalAnalyzer
from src.narrator.reflection_narrator import ReflectionNarrator
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.json_reporter import JsonReporter
from src.reporters.html_reporter import HtmlReporter
from src.reporters.pdf_reporter import PdfReporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


USAGE_NOTICE_TEXT = (
    "\n⚠️  Usage notice — please read before continuing.\n"
    "\n"
    "  This tool produces a DESCRIPTIVE summary of Git history only.\n"
    "  It does NOT measure productivity, engagement, or the value of any\n"
    "  individual's contribution. Code review, design, mentoring, on-call,\n"
    "  ops, and many other contributions are invisible to Git history.\n"
    "\n"
    "  Default mode is SELF-SCOPE ONLY: the tool only analyses commits\n"
    "  authored by the current local Git user. Multi-author analysis is\n"
    "  blocked unless you explicitly opt-in with --multi-author-team-retro\n"
    "  and supply --consented-author entries for every analyzed person.\n"
    "\n"
    "  DO NOT use the output of this tool for:\n"
    "    • performance reviews, ranking, or comparison of individual workers\n"
    "    • compensation, promotion, discipline, or PIP decisions\n"
    "    • employee surveillance or monitoring of non-consenting contributors\n"
    "\n"
    "  Even in a fully-consented team retrospective, the output is\n"
    "  per-dimension narrative text (no composite score, no letter grade,\n"
    "  no leaderboard) and remains unsuitable for HR decisions.\n"
)


# ─── Self-scope helpers ──────────────────────────────────────────────────────


def _detect_self_identity(repo_path: str) -> Tuple[Optional[str], Optional[str]]:
    """Return ``(name, email)`` for the local Git user inside ``repo_path``.

    Falls back to global git config if the repo has no override. Returns
    ``(None, None)`` if neither is configured.
    """
    def _git_config(key: str) -> Optional[str]:
        try:
            out = subprocess.run(
                ["git", "-C", repo_path, "config", "--get", key],
                capture_output=True, text=True, check=False, timeout=5,
            )
            value = (out.stdout or "").strip()
            return value or None
        except (OSError, subprocess.SubprocessError):
            return None

    return _git_config("user.name"), _git_config("user.email")


def _resolve_consented_authors(
    repo_path: str,
    multi_author_team_retro: bool,
    consented_authors: Optional[List[str]],
) -> Tuple[List[str], List[str]]:
    """Decide which author filters to pass to the analysers.

    Returns ``(authors_filter, refusal_reasons)``.
    If ``refusal_reasons`` is non-empty, callers must abort the run.
    """
    refusal_reasons: List[str] = []
    name, email = _detect_self_identity(repo_path)

    if not multi_author_team_retro:
        # Self-scope mode (default). Lock to the local Git user's identity.
        if not (name or email):
            refusal_reasons.append(
                "Self-scope mode requires a local Git identity but none was "
                "found (git config user.name / user.email is empty). Configure "
                "your Git identity first, or run an explicitly consented team "
                "retrospective with --multi-author-team-retro and "
                "--consented-author."
            )
            return [], refusal_reasons
        # Use both name and email as fuzzy filters so the analyzers only
        # surface the current user's commits.
        filters = [v for v in (name, email) if v]
        return filters, []

    # Multi-author retrospective mode (must be explicit).
    if not consented_authors:
        refusal_reasons.append(
            "--multi-author-team-retro requires at least one "
            "--consented-author entry. Refusing to run an implicit, "
            "whole-repository person-level analysis."
        )
        return [], refusal_reasons

    return list(consented_authors), []


# ─── Orchestrator ────────────────────────────────────────────────────────────


def run_analysis(
    repo_path: str,
    scan_all_repos: bool = False,
    since: Optional[str] = None,
    until: Optional[str] = None,
    branch: Optional[str] = None,
    output_format: str = "markdown",
    output_path: Optional[str] = None,
    acknowledge_usage_policy: bool = False,
    multi_author_team_retro: bool = False,
    consented_authors: Optional[List[str]] = None,
) -> dict:
    """
    Main analysis orchestrator.

    Args:
        repo_path: Path to a Git repo or parent directory.
        scan_all_repos: Whether to recursively scan for all .git repos.
        since: Start date in ISO format.
        until: End date in ISO format.
        branch: Branch name to analyze.
        output_format: 'json', 'markdown', 'html', or 'pdf'.
        output_path: Output file path (used for PDF generation).
        acknowledge_usage_policy: Caller must explicitly set this to ``True``
            via the skill parameter or ``--i-have-consent`` CLI flag. There is
            no environment-variable bypass; the tool refuses to run otherwise.
        multi_author_team_retro: Required to opt out of self-scope mode and
            run a fully-consented team retrospective. When False (the default)
            the analyzers are locked to the current local Git user's identity.
        consented_authors: Required when ``multi_author_team_retro`` is True.
            Must list every author (name or email) who has given informed
            consent. The tool refuses to run an implicit whole-repo analysis.

    Returns:
        A dict with 'report' (formatted string) and 'metrics' (raw data).
    """
    # Hard gate 1 — explicit consent acknowledgement. No env bypass.
    if not acknowledge_usage_policy:
        logger.warning(USAGE_NOTICE_TEXT)
        logger.warning(
            "Refusing to run: pass acknowledge_usage_policy=True "
            "(or --i-have-consent on the CLI) to confirm you have informed "
            "consent from every analysed developer and will not use the "
            "output for HR decisions, ranking, or surveillance."
        )
        return {
            "report": USAGE_NOTICE_TEXT + (
                "\nAnalysis refused: usage policy was not acknowledged. "
                "Set acknowledge_usage_policy=True (or pass --i-have-consent) "
                "to proceed.\n"
            ),
            "metrics": {},
            "reports": {},
        }

    # Hard gate 2 — resolve scope (self-only by default).
    authors_filter, refusal_reasons = _resolve_consented_authors(
        repo_path,
        multi_author_team_retro,
        consented_authors,
    )
    if refusal_reasons:
        for reason in refusal_reasons:
            logger.warning(reason)
        return {
            "report": USAGE_NOTICE_TEXT + "\nAnalysis refused:\n  - "
            + "\n  - ".join(refusal_reasons) + "\n",
            "metrics": {},
            "reports": {},
        }

    if multi_author_team_retro:
        logger.info(
            "Running in MULTI-AUTHOR TEAM RETROSPECTIVE mode for: %s. "
            "Caller has asserted informed consent from every listed author.",
            ", ".join(authors_filter),
        )
        scope_mode = "team_retro"
    else:
        logger.info(
            "Running in SELF-SCOPE mode for local Git user: %s. "
            "Other authors in the repository will be ignored.",
            " / ".join(authors_filter),
        )
        scope_mode = "self_scope"

    # Step 1: Discover repositories
    scanner = RepoScanner()
    if scan_all_repos:
        repos = scanner.scan_directory(repo_path)
    else:
        repos = scanner.scan_single(repo_path)

    if not repos:
        logger.warning("No Git repositories found at: %s", repo_path)
        return {"report": "No Git repositories found.", "metrics": {}, "reports": {}}

    logger.info("Found %d repository(ies) to analyze.", len(repos))

    # Step 2: Run all analyzers on each repository
    all_metrics = {}

    for repo_info in repos:
        repo_name = repo_info["name"]
        logger.info("Analyzing repository: %s", repo_name)

        common_kwargs = dict(
            authors=authors_filter, since=since, until=until, branch=branch
        )

        commit_analyzer = CommitAnalyzer(repo_info["path"], **common_kwargs)
        work_habit_analyzer = WorkHabitAnalyzer(repo_info["path"], **common_kwargs)
        efficiency_analyzer = EfficiencyAnalyzer(repo_info["path"], **common_kwargs)
        code_style_analyzer = CodeStyleAnalyzer(repo_info["path"], **common_kwargs)
        code_quality_analyzer = CodeQualityAnalyzer(repo_info["path"], **common_kwargs)
        cadence_signal_analyzer = CadenceSignalAnalyzer(repo_info["path"], **common_kwargs)

        repo_metrics = {
            "commit_patterns": commit_analyzer.analyze(),
            "work_habits": work_habit_analyzer.analyze(),
            "efficiency": efficiency_analyzer.analyze(),
            "code_style": code_style_analyzer.analyze(),
            "code_quality": code_quality_analyzer.analyze(),
            "cadence_signals": cadence_signal_analyzer.analyze(),
        }

        # Per-identity journal-style reflection narrative.
        # NOT an evaluation, NOT a score, NOT a grade.
        # ``consented_identities`` is a defence-in-depth allow-list: even if
        # something upstream slips an unconsented identity into
        # ``repo_metrics``, the narrator will drop it instead of producing
        # a personal narrative for them.
        narrator = ReflectionNarrator()
        repo_metrics["reflections"] = narrator.narrate(
            repo_metrics, consented_identities=list(authors_filter),
        )

        # Stamp scope metadata on every repo's metrics so reporters can
        # render an honest provenance banner and refuse cross-author comparison
        # rendering when running in self-scope mode.
        repo_metrics["_scope"] = {
            "mode": scope_mode,
            "filters": list(authors_filter),
        }

        all_metrics[repo_name] = repo_metrics

    # Step 3: Generate report(s)
    formats_to_generate = _parse_formats(output_format)
    reports = {}

    for fmt in formats_to_generate:
        reporter = _get_reporter(fmt)

        if fmt == "pdf":
            pdf_path = output_path or "report.pdf"
            if not pdf_path.endswith(".pdf"):
                pdf_path = pdf_path.rsplit(".", 1)[0] + ".pdf"
            reporter.generate_to_file(all_metrics, pdf_path)
            reports[fmt] = f"PDF saved to: {pdf_path}"
            logger.info("PDF report generated: %s", pdf_path)
        else:
            reports[fmt] = reporter.generate(all_metrics)

    primary_report = reports.get(formats_to_generate[0], "")

    return {"report": primary_report, "metrics": all_metrics, "reports": reports}


def _parse_formats(output_format: str) -> list:
    """Parse output format string, supporting comma-separated multiple formats."""
    formats = [f.strip().lower() for f in output_format.split(",")]
    valid = {"markdown", "json", "html", "pdf"}
    result = []
    for f in formats:
        if f in valid:
            result.append(f)
        else:
            logger.warning("Unknown format '%s', ignoring.", f)
    return result if result else ["markdown"]


def _get_reporter(output_format: str):
    """Factory method to get the appropriate reporter."""
    reporters = {
        "markdown": MarkdownReporter,
        "json": JsonReporter,
        "html": HtmlReporter,
        "pdf": PdfReporter,
    }
    reporter_cls = reporters.get(output_format.lower())
    if not reporter_cls:
        raise ValueError(
            f"Unsupported output format: {output_format}. "
            f"Choose from: {list(reporters.keys())}"
        )
    return reporter_cls()


# ─── CLI Interface ────────────────────────────────────────────────────────────


@click.command()
@click.option(
    "--repo-path", "-r", required=True, help="Path to Git repo or parent directory."
)
@click.option(
    "--scan-all", is_flag=True, default=False, help="Scan all .git repos recursively."
)
@click.option("--since", "-s", default=None, help="Start date (ISO format).")
@click.option("--until", "-u", default=None, help="End date (ISO format).")
@click.option("--branch", "-b", default=None, help="Branch to analyze.")
@click.option(
    "--format",
    "-f",
    "output_format",
    default="markdown",
    help="Output format(s): markdown, json, html, pdf (comma-separated for multiple).",
)
@click.option("--output", "-o", default=None, help="Output file path (prints to stdout if omitted).")
@click.option(
    "--i-have-consent",
    "acknowledge_usage_policy",
    is_flag=True,
    default=False,
    help=(
        "REQUIRED. Confirms (1) you have read the usage notice, (2) you have "
        "informed consent from every developer whose Git history will be "
        "analyzed, and (3) you will NOT use the output for performance "
        "reviews, ranking, compensation, discipline, surveillance, or any HR "
        "decision. There is no environment-variable bypass; without this "
        "explicit flag the tool refuses to run."
    ),
)
@click.option(
    "--multi-author-team-retro",
    is_flag=True,
    default=False,
    help=(
        "Opt out of self-scope mode and run a fully-consented multi-author "
        "team retrospective. Requires at least one --consented-author entry. "
        "Without this flag the tool runs in self-scope mode and only analyses "
        "commits authored by the current local Git user."
    ),
)
@click.option(
    "--consented-author",
    "consented_authors",
    multiple=True,
    default=(),
    help=(
        "Author name or email of a person who has given informed consent to "
        "be included in this team retrospective. Repeatable. Required when "
        "--multi-author-team-retro is set."
    ),
)
def cli(
    repo_path,
    scan_all,
    since,
    until,
    branch,
    output_format,
    output,
    acknowledge_usage_policy,
    multi_author_team_retro,
    consented_authors,
):
    """Code Analysis Skills - Generate a Git-history self-reflection report.

    \b
    Usage notice:
      This tool produces a DESCRIPTIVE summary of Git history only and
      MUST NOT be used for performance reviews, ranking, compensation,
      discipline, or any HR decision.

      The default mode is self-scope: only commits authored by the current
      local Git user are analysed. Use --multi-author-team-retro plus
      --consented-author NAME (repeatable) to run a consented team
      retrospective. You must always pass --i-have-consent.
    """
    click.echo(USAGE_NOTICE_TEXT, err=True)

    result = run_analysis(
        repo_path=repo_path,
        scan_all_repos=scan_all,
        since=since,
        until=until,
        branch=branch,
        output_format=output_format,
        output_path=output,
        acknowledge_usage_policy=acknowledge_usage_policy,
        multi_author_team_retro=multi_author_team_retro,
        consented_authors=list(consented_authors) if consented_authors else None,
    )

    if not result.get("metrics"):
        click.echo(result["report"])
        sys.exit(2)

    formats = _parse_formats(output_format)

    if len(formats) == 1 and formats[0] != "pdf":
        report_text = result["report"]
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(report_text)
            click.echo(f"Report saved to: {output}")
        else:
            click.echo(report_text)
    else:
        base = output or "report"
        if "." in base:
            base = base.rsplit(".", 1)[0]
        ext_map = {"markdown": ".md", "json": ".json", "html": ".html", "pdf": ".pdf"}
        for fmt in formats:
            if fmt == "pdf":
                click.echo(f"PDF saved to: {base}.pdf")
                continue
            ext = ext_map.get(fmt, f".{fmt}")
            out_path = f"{base}{ext}"
            report_text = result["reports"].get(fmt, "")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            click.echo(f"{fmt.upper()} report saved to: {out_path}")


# ─── Skill Entry Point (for ClawHub) ─────────────────────────────────────────


def main(params: dict) -> dict:
    """
    ClawHub skill entry point.

    Args:
        params: Dict of parameters from skill.yaml. Must include
            ``acknowledge_usage_policy: true``. Multi-author analysis also
            requires ``multi_author_team_retro: true`` AND
            ``consented_authors: [...]``. There is no environment-variable
            bypass.

    Returns:
        Dict with 'report', 'metrics' and 'reports' outputs.
    """
    return run_analysis(
        repo_path=params.get("repo_path", "."),
        scan_all_repos=bool(params.get("scan_all_repos", False)),
        since=params.get("since") or None,
        until=params.get("until") or None,
        branch=params.get("branch") or None,
        output_format=params.get("output_format", "markdown"),
        output_path=params.get("output_path") or None,
        acknowledge_usage_policy=bool(params.get("acknowledge_usage_policy", False)),
        multi_author_team_retro=bool(params.get("multi_author_team_retro", False)),
        consented_authors=params.get("consented_authors") or None,
    )


if __name__ == "__main__":
    cli()
