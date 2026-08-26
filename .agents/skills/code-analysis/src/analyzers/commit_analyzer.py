"""
Commit Analyzer - Analyzes commit patterns and behaviors.

Metrics include:
  - Total commits for the consented identity
  - Commit frequency (daily/weekly/monthly)
  - Average commits per day
  - Commit message length & quality
  - Commit size distribution (lines added/deleted)
  - Merge vs non-merge commit ratio
"""

import logging
from collections import defaultdict
from typing import Dict

from src.analyzers.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class CommitAnalyzer(BaseAnalyzer):
    """Computes descriptive commit-pattern markers per consented identity.

    The orchestrator restricts ``BaseAnalyzer._get_commits`` to either the
    local Git user (self-scope, default) or to authors who have given
    informed consent (``--multi-author-team-retro`` mode). This analyzer
    only operates on commits the orchestrator has already authorised.

    Output is descriptive only and MUST NOT be used for evaluation,
    ranking, surveillance, or HR decisions.
    """

    def analyze(self) -> Dict:
        """
        Compute descriptive commit-pattern markers on the *already-scoped*
        commit set.

        Returns:
            Dict keyed by the consented Git identity with descriptive
            commit-pattern markers. In self-scope mode this dict has at
            most one entry (the local Git user).
        """
        author_data = defaultdict(lambda: {
            "total_commits": 0,
            "merge_commits": 0,
            "commit_dates": [],
            "commit_hours": [],
            "message_lengths": [],
            "lines_added": [],
            "lines_deleted": [],
            "files_changed": [],
        })

        for commit in self._get_commits():
            author = commit.author.name
            data = author_data[author]

            data["total_commits"] += 1
            data["commit_dates"].append(commit.committer_date)
            data["commit_hours"].append(commit.committer_date.hour)
            data["message_lengths"].append(len(commit.msg))

            if commit.merge:
                data["merge_commits"] += 1

            total_added = 0
            total_deleted = 0
            files_count = 0
            for mod in commit.modified_files:
                total_added += mod.added_lines
                total_deleted += mod.deleted_lines
                files_count += 1

            data["lines_added"].append(total_added)
            data["lines_deleted"].append(total_deleted)
            data["files_changed"].append(files_count)

        # Build summary metrics
        result = {}
        for author, data in author_data.items():
            total = data["total_commits"]
            if total == 0:
                continue

            dates = sorted(data["commit_dates"])
            if len(dates) >= 2:
                active_days = (dates[-1] - dates[0]).days or 1
            else:
                active_days = 1

            unique_days = len(set(d.date() for d in dates))

            result[author] = {
                "total_commits": total,
                "merge_commits": data["merge_commits"],
                "non_merge_commits": total - data["merge_commits"],
                "merge_ratio": round(data["merge_commits"] / total, 3),
                "active_span_days": active_days,
                "unique_active_days": unique_days,
                "avg_commits_per_active_day": round(total / unique_days, 2) if unique_days else 0,
                "avg_message_length": round(
                    sum(data["message_lengths"]) / total, 1
                ),
                "avg_lines_added": round(
                    sum(data["lines_added"]) / total, 1
                ),
                "avg_lines_deleted": round(
                    sum(data["lines_deleted"]) / total, 1
                ),
                "avg_files_changed": round(
                    sum(data["files_changed"]) / total, 1
                ),
                "total_lines_added": sum(data["lines_added"]),
                "total_lines_deleted": sum(data["lines_deleted"]),
            }

        return result
