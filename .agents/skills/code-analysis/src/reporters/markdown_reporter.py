"""
Markdown Reporter - Renders the per-developer Git-history reflection
narrative.

⚠️  STRUCTURAL SAFEGUARDS

This reporter intentionally:

  * Does NOT render any composite 0-100 score, grade band, or verdict.
  * Does NOT emit any cross-author comparison table or leaderboard, even
    sorted alphabetically. Side-by-side person-level metrics enable
    informal ranking by readers regardless of label.
  * Always opens with an explicit usage notice.
  * Stamps a SCOPE banner at the top of every report (self-scope vs.
    consented multi-author retrospective) so readers cannot lose track of
    what they are looking at.

If multiple authors are present in the metrics dict (because the caller
opted into a consented multi-author team retrospective), their narratives
are emitted in separate, alphabetically-ordered sections. There is still
no comparative table.
"""

from typing import Dict, List

from src.reporters.base_reporter import BaseReporter


USAGE_NOTICE_MD = (
    "> ⚠️ **Usage notice — please read first.** This report is a **descriptive "
    "summary of Git history only**. It does **not** measure productivity, "
    "engagement, or the value of any individual's contribution. Code review, "
    "design, mentoring, on-call, ops, and many other contributions are "
    "invisible to Git history. **Do not** use this report for performance "
    "evaluation, ranking, compensation, promotion, discipline, or any HR "
    "decision. Run it only with the **informed consent** of every analyzed "
    "developer, and treat findings as **personal reflection prompts**, not "
    "verdicts.\n"
)


class MarkdownReporter(BaseReporter):
    """Generates Markdown reports from analysis metrics.

    Every report opens with a usage notice and a scope banner. Section copy
    is intentionally neutral and non-stigmatizing. No composite scores, no
    grade bands, no leaderboards, no cross-author comparison tables.
    """

    def generate(self, metrics: Dict) -> str:
        """Generate a Markdown report."""
        lines: List[str] = []
        lines.append("# 🪞 Git-History Reflection Report\n")
        lines.append(USAGE_NOTICE_MD)

        for repo_name, repo_metrics in metrics.items():
            lines.append(f"## 📁 Repository: {repo_name}\n")

            scope = repo_metrics.get("_scope") or {}
            lines.append(self._scope_banner(scope))

            # Collect all authors across analyzers (skip private keys).
            all_authors = set()
            for key, analyzer_data in repo_metrics.items():
                if (
                    isinstance(analyzer_data, dict)
                    and key not in ("evaluations", "_scope")
                ):
                    all_authors.update(analyzer_data.keys())

            if not all_authors:
                lines.append("_No data available for this repository._\n")
                continue

            for author in sorted(all_authors):
                lines.append(f"### 👤 {author}\n")
                self._render_reflection(lines, repo_metrics, author)
                self._render_cadence_signals(lines, repo_metrics, author)
                self._render_commit_patterns(lines, repo_metrics, author)
                self._render_work_habits(lines, repo_metrics, author)
                self._render_efficiency(lines, repo_metrics, author)
                self._render_code_style(lines, repo_metrics, author)
                self._render_code_quality(lines, repo_metrics, author)
                lines.append("---\n")

        # NOTE: cross-author comparison tables, leaderboards, and
        # composite-indicator overviews are intentionally NOT generated.
        return "\n".join(lines)

    # ─── Scope banner ────────────────────────────────────────────────────

    @staticmethod
    def _scope_banner(scope: Dict) -> str:
        mode = scope.get("mode")
        filters = scope.get("filters") or []
        if mode == "self_scope":
            return (
                f"> 🔒 **Scope: self-reflection only.** Analysis is locked to "
                f"the local Git user (`{' / '.join(filters)}`). Other authors "
                f"in the repository are not analysed.\n"
            )
        if mode == "team_retro":
            return (
                "> 👥 **Scope: consented team retrospective.** Caller has "
                "explicitly asserted informed consent from every listed "
                "author: " + ", ".join(f"`{a}`" for a in filters) + ".\n"
            )
        return (
            "> ℹ️ **Scope: unspecified.** Treat this report with extra caution "
            "and verify the consent basis before sharing.\n"
        )

    # ─── Per-section renderers ───────────────────────────────────────────

    def _render_reflection(self, lines: List[str], repo_metrics: Dict, author: str) -> None:
        ev = repo_metrics.get("evaluations", {}).get(author, {})
        if not ev:
            return
        lines.append("#### 🪞 Personal Reflection Narrative\n")
        lines.append(
            "_Descriptive observations only. Not a score, not a grade, not a "
            "verdict._\n"
        )

        strengths = ev.get("strengths") or []
        if strengths:
            lines.append("**✅ Supportive observations:**\n")
            for s in strengths:
                lines.append(f"- {s}")
            lines.append("")

        weaknesses = ev.get("weaknesses") or []
        if weaknesses:
            lines.append("**🔎 Points to consider (with context):**\n")
            for w in weaknesses:
                lines.append(f"- {w}")
            lines.append("")

        suggestions = ev.get("suggestions") or []
        if suggestions:
            lines.append("**💡 Reflection prompts:**\n")
            for sg in suggestions:
                lines.append(f"- {sg}")
            lines.append("")

        notice = ev.get("interpretation_notice")
        if notice:
            lines.append(f"> ℹ️ {notice}\n")

    def _render_cadence_signals(self, lines: List[str], repo_metrics: Dict, author: str) -> None:
        sd = repo_metrics.get("slacking", {}).get(author, {})
        if not sd:
            return
        lines.append("#### 📉 Commit-cadence component values (descriptive only)\n")
        lines.append(
            "_How sparse / bursty / low-volume the Git activity looks. "
            "**Not** a productivity or engagement measure. Many legitimate "
            "work patterns produce sparse cadence (architecture work, code "
            "review, on-call, time-off). No single composite score is "
            "emitted; readers should consider each component on its own._\n"
        )
        lines.append("| Component | Value |")
        lines.append("|-----------|-------|")
        lines.append(f"| Activity ratio | {sd.get('activity_ratio', 0):.1%} |")
        lines.append(f"| Trivial-change ratio | {sd.get('trivial_commit_ratio', 0):.1%} |")
        lines.append(f"| Long-gap ratio (>72h) | {sd.get('large_gap_ratio', 0):.1%} |")
        lines.append(f"| Avg gap (hours) | {sd.get('avg_gap_hours', 0)} |")
        lines.append(f"| Lines / active day | {sd.get('lines_per_active_day', 0)} |")
        lines.append(f"| Non-code-only commit ratio | {sd.get('non_code_commit_ratio', 0):.1%} |")
        lines.append("")

        notice = sd.get("interpretation_notice")
        if notice:
            lines.append(f"> ℹ️ {notice}\n")

    def _render_commit_patterns(self, lines: List[str], repo_metrics: Dict, author: str) -> None:
        cd = repo_metrics.get("commit_patterns", {}).get(author, {})
        if not cd:
            return
        lines.append("#### 📝 Commit Patterns\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total commits | {cd.get('total_commits', 0)} |")
        lines.append(f"| Non-merge commits | {cd.get('non_merge_commits', 0)} |")
        lines.append(f"| Merge ratio | {cd.get('merge_ratio', 0):.1%} |")
        lines.append(f"| Active span (days) | {cd.get('active_span_days', 0)} |")
        lines.append(f"| Unique active days | {cd.get('unique_active_days', 0)} |")
        lines.append(f"| Avg commits / active day | {cd.get('avg_commits_per_active_day', 0)} |")
        lines.append(f"| Avg message length | {cd.get('avg_message_length', 0)} |")
        lines.append(f"| Avg lines added | {cd.get('avg_lines_added', 0)} |")
        lines.append(f"| Avg lines deleted | {cd.get('avg_lines_deleted', 0)} |")
        lines.append(f"| Avg files changed | {cd.get('avg_files_changed', 0)} |")
        lines.append(f"| Total lines added | {cd.get('total_lines_added', 0):,} |")
        lines.append(f"| Total lines deleted | {cd.get('total_lines_deleted', 0):,} |")
        lines.append("")

    def _render_work_habits(self, lines: List[str], repo_metrics: Dict, author: str) -> None:
        hd = repo_metrics.get("work_habits", {}).get(author, {})
        if not hd:
            return
        lines.append("#### ⏰ Commit timestamp distribution\n")
        lines.append(
            "_Reflects when commits were authored, not when the developer was "
            "working / resting. Time-zone settings, batched pushes, and squash "
            "merges can distort these numbers._\n"
        )
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Peak hour | {hd.get('peak_hour', 'N/A')}:00 |")
        lines.append(f"| Weekday commits | {hd.get('weekday_commits', 0)} |")
        lines.append(f"| Weekend commits | {hd.get('weekend_commits', 0)} |")
        lines.append(f"| Weekend ratio | {hd.get('weekend_ratio', 0):.1%} |")
        lines.append(f"| Late-night ratio | {hd.get('late_night_ratio', 0):.1%} |")
        lines.append(f"| Longest streak (days) | {hd.get('longest_streak_days', 0)} |")
        lines.append(f"| Avg gap between commits (hrs) | {hd.get('avg_gap_between_commits_hours', 0)} |")
        lines.append("")

        notice = hd.get("interpretation_notice")
        if notice:
            lines.append(f"> ℹ️ {notice}\n")

    def _render_efficiency(self, lines: List[str], repo_metrics: Dict, author: str) -> None:
        ed = repo_metrics.get("efficiency", {}).get(author, {})
        if not ed:
            return
        lines.append("#### 🚀 Change patterns (descriptive)\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Churn rate | {ed.get('churn_rate', 0):.1%} |")
        lines.append(f"| Rework ratio | {ed.get('rework_ratio', 0):.1%} |")
        lines.append(f"| Lines / commit | {ed.get('lines_per_commit', 0)} |")
        lines.append(f"| Unique files touched | {ed.get('unique_files_touched', 0)} |")
        lines.append(f"| Owned files | {ed.get('owned_files_count', 0)} |")
        lines.append(f"| Ownership ratio | {ed.get('ownership_ratio', 0):.1%} |")
        lines.append(f"| Repo-level avg bus factor | {ed.get('repo_avg_bus_factor', 0)} |")
        lines.append("")

        notice = ed.get("interpretation_notice")
        if notice:
            lines.append(f"> ℹ️ {notice}\n")

    def _render_code_style(self, lines: List[str], repo_metrics: Dict, author: str) -> None:
        sd = repo_metrics.get("code_style", {}).get(author, {})
        if not sd:
            return
        lines.append("#### 🎨 Code-style markers\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Conventional Commits ratio | {sd.get('conventional_commit_ratio', 0):.1%} |")
        lines.append(f"| Issue-reference ratio | {sd.get('issue_reference_ratio', 0):.1%} |")
        lines.append(f"| Avg change size (lines) | {sd.get('avg_change_size_lines', 0)} |")
        lines.append("")

    def _render_code_quality(self, lines: List[str], repo_metrics: Dict, author: str) -> None:
        qd = repo_metrics.get("code_quality", {}).get(author, {})
        if not qd:
            return
        lines.append("#### 🔍 Code-quality artefacts\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Bug-fix commit ratio | {qd.get('bug_fix_ratio', 0):.1%} |")
        lines.append(f"| Revert commit ratio | {qd.get('revert_ratio', 0):.1%} |")
        lines.append(f"| Large-commit ratio (>500 lines) | {qd.get('large_commit_ratio', 0):.1%} |")
        lines.append(f"| Test-modification ratio | {qd.get('test_modification_ratio', 0):.1%} |")
        lines.append(f"| Doc-modification ratio | {qd.get('doc_modification_ratio', 0):.1%} |")
        lines.append(f"| Avg commit size | {qd.get('avg_commit_size', 0)} |")
        lines.append(f"| Median commit size | {qd.get('median_commit_size', 0)} |")
        if qd.get("avg_python_complexity", 0) > 0:
            lines.append(f"| Avg Python complexity | {qd['avg_python_complexity']} |")
        lines.append("")
