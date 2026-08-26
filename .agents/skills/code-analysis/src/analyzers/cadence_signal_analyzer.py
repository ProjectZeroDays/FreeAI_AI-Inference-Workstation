"""
Cadence Signal Analyzer — *self-reflection only*.

This module extracts low-level, descriptive cadence component values from a
Git repository (cadence sparsity, inter-commit gap size, trivial-change
ratio, lines-per-active-day, non-code-only commit ratio). It is
structurally constrained so the output cannot be misused as a single
"engagement number" or "productivity score":

  * **No composite 0–100 score is produced.** Each component value is
    exposed individually and consumers must interpret each one separately.
  * **No descriptive band label** (e.g., Dense / Regular / Mixed / Sparse /
    Very sparse) is emitted. Bands compress multi-dimensional behaviour
    into a single rank-friendly bucket and were therefore dropped.
  * **No "low output" / "slacking" / "disappearance" signal is computed.**
    Lines-per-day is not a productivity proxy (small refactors, reviews,
    on-call work, and design work don't appear in diffs), and turning a
    long inter-commit gap into a "disappearance score" misframes routine
    role variation as a behavioural problem.
  * **Caller is responsible for scope.** This analyzer only sees commits
    yielded by ``BaseAnalyzer._get_commits``, which the orchestrator
    locks to either the local Git user (self-scope) or the explicitly
    consented author list (multi-author team retro). It does not, on its
    own, scan unconsented contributors.

The signals are a NARROW, BIASED proxy. Code review, design, mentoring,
on-call, ops, security work, pair programming, and many other forms of
contribution are invisible to Git history. Low or high values therefore
carry no information about a person's productivity, engagement, or value
and MUST NOT be used to:

  - Make hiring, firing, promotion, compensation, or PIP decisions
  - Rank, grade, or publicly compare developers
  - Surveil employees or monitor non-consenting contributors
  - Generate "leaderboards" of individual workers

By using this module you accept responsibility for ensuring informed
consent from every developer whose data is analysed and for compliance
with applicable privacy and labor regulations (e.g., GDPR, local
works-council rules).
"""

import logging
from collections import defaultdict
from typing import Dict

from src.analyzers.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

# Thresholds (tuning knobs only — do not infer "performance" from these)
TRIVIAL_COMMIT_LINE_THRESHOLD = 5  # commits with <= 5 lines changed
LARGE_GAP_HOURS = 72  # 3 days without commits


class CadenceSignalAnalyzer(BaseAnalyzer):
    """Computes descriptive Git-cadence component values for each *consented identity*.

    The orchestrator restricts ``BaseAnalyzer._get_commits`` to the local Git
    user (self-scope, default) or to the explicitly listed
    ``consented_authors`` (multi-author team retrospective). This analyzer
    operates only on whatever subset of commits the orchestrator has already
    authorised; it never scans non-consenting contributors on its own.

    The output deliberately contains:
      * individual cadence component values (sparsity, trivial-change ratio,
        long-gap ratio, average gap, lines-per-active-day, non-code-only
        commit ratio);
      * an always-attached ``interpretation_notice`` warning string.

    The output deliberately does NOT contain:
      * a composite 0–100 "engagement" / "productivity" / "cadence" score;
      * a categorical cadence band label or its translation;
      * any "low-output" / "disappearance" / "slacking"-style signal that
        encodes a managerial judgement about the worker;
      * any weekday-distribution / Friday-skew / late-week-skew feature
        that could be recombined into an attendance proxy.

    These were removed because, in practice, a single number or a labelled
    band is the building block surveillance and ranking tools need; refusing
    to produce them is the structural safeguard.
    """

    def analyze(self) -> Dict:
        """Run the cadence-signal analysis on the *already-scoped* commit set.

        Returns a dict keyed by Git author identity (the local self-scope
        user, or one of the explicitly consented authors). Per-identity
        results contain individual component values only — never a composite
        score, never a categorical band.
        """
        author_data = defaultdict(lambda: {
            "commit_times": [],
            "commit_dates": [],
            "lines_added": [],
            "lines_deleted": [],
            "files_changed": [],
            "commit_messages": [],
            "file_paths": [],
        })

        for commit in self._get_commits():
            author = commit.author.name
            data = author_data[author]
            data["commit_times"].append(commit.committer_date)
            data["commit_dates"].append(commit.committer_date.date())
            data["commit_messages"].append(commit.msg)

            total_added = 0
            total_deleted = 0
            files = 0
            paths = []
            for mod in commit.modified_files:
                total_added += mod.added_lines
                total_deleted += mod.deleted_lines
                files += 1
                if mod.new_path:
                    paths.append(mod.new_path)

            data["lines_added"].append(total_added)
            data["lines_deleted"].append(total_deleted)
            data["files_changed"].append(files)
            data["file_paths"].append(paths)

        result = {}
        for author, data in author_data.items():
            total = len(data["commit_times"])
            if total == 0:
                continue

            # Signal 1: Cadence sparsity — unique active days / span days.
            dates = sorted(data["commit_dates"])
            if len(dates) >= 2:
                span_days = (dates[-1] - dates[0]).days or 1
            else:
                span_days = 1
            unique_days = len(set(dates))
            activity_ratio = unique_days / span_days if span_days > 0 else 1.0

            # Signal 2: Trivial-change ratio (commits with very few lines changed).
            trivial_count = sum(
                1 for a, d in zip(data["lines_added"], data["lines_deleted"])
                if (a + d) <= TRIVIAL_COMMIT_LINE_THRESHOLD
            )
            trivial_ratio = trivial_count / total

            # Signal 3: Long-gap ratio — proportion of inter-commit gaps over 72h.
            sorted_times = sorted(data["commit_times"])
            gap_hours = []
            large_gap_count = 0
            for i in range(1, len(sorted_times)):
                gap = (sorted_times[i] - sorted_times[i - 1]).total_seconds() / 3600
                gap_hours.append(gap)
                if gap > LARGE_GAP_HOURS:
                    large_gap_count += 1
            avg_gap = sum(gap_hours) / len(gap_hours) if gap_hours else 0
            large_gap_ratio = large_gap_count / len(gap_hours) if gap_hours else 0

            # Signal 4: Average lines per active day. Reported as a raw
            # average ONLY — the analyzer intentionally does not bucket this
            # value into a managerial-style "low output" or "high output"
            # score. Lines-per-day is a poor productivity proxy: small
            # refactors, reviews, design work, on-call work, and many other
            # high-value contributions do not show up in diffs.
            total_lines = sum(data["lines_added"]) + sum(data["lines_deleted"])
            lines_per_day = total_lines / unique_days if unique_days > 0 else 0

            # Signal 5: Non-code-only commit ratio (config / docs only commits).
            non_code_commits = 0
            for paths_list in data["file_paths"]:
                if paths_list and all(self._is_non_code(p) for p in paths_list):
                    non_code_commits += 1
            non_code_ratio = non_code_commits / total

            # NOTE: this analyzer intentionally does not synthesise any
            # composite cadence number, categorical band, weighted "signal
            # score", or weekday-distribution feature. Day-of-week patterns
            # were deliberately removed from this output because exposing
            # Friday/Monday shares (or any other weekday split) is a thin
            # repackaging of the previously-removed "late-week skew"
            # signal and can be recombined downstream into an attendance /
            # work-pattern surveillance proxy. Readers who genuinely need
            # day-of-week information for their own self-reflection should
            # consult ``work_habits`` instead, which is produced under the
            # same consent gate but framed as a personal-cadence feature
            # rather than a cadence-signal feature.

            result[author] = {
                # Always-attached interpretive guard so downstream renderers
                # cannot accidentally drop the disclaimer.
                "interpretation_notice": (
                    "Descriptive Git-cadence component values only. Each "
                    "value below is meaningful only with full context (role, "
                    "time-zone, on-call rotation, leave, refactor sweeps, "
                    "squash merges, batched pushes, vendored / generated "
                    "code, etc.). The output deliberately contains NO "
                    "composite score and NO categorical band, and MUST NOT "
                    "be used for performance evaluation, ranking, "
                    "comparison, surveillance, or HR decisions."
                ),

                "total_commits": total,
                "active_span_days": span_days,
                "unique_active_days": unique_days,
                "activity_ratio": round(activity_ratio, 3),
                "trivial_commit_ratio": round(trivial_ratio, 3),
                "large_gap_ratio": round(large_gap_ratio, 3),
                "avg_gap_hours": round(avg_gap, 1),
                "lines_per_active_day": round(lines_per_day, 1),
                "non_code_commit_ratio": round(non_code_ratio, 3),
            }

        return result

    @staticmethod
    def _is_non_code(filepath: str) -> bool:
        """Check if a file is a non-code file (config, docs, etc.)."""
        path_lower = filepath.lower()
        non_code_exts = [
            ".md", ".rst", ".txt", ".adoc", ".yml", ".yaml", ".json",
            ".toml", ".ini", ".cfg", ".env", ".lock", ".gitignore",
            ".editorconfig", ".prettierrc",
        ]
        non_code_names = [
            "readme", "changelog", "license", "contributing",
            "dockerfile", "makefile", ".github/",
        ]
        return (
            any(path_lower.endswith(ext) for ext in non_code_exts)
            or any(name in path_lower for name in non_code_names)
        )
