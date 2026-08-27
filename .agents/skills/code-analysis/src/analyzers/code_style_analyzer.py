"""
Code Style Analyzer - Analyzes code style consistency and patterns.

Metrics include:
  - File type distribution (languages used)
  - Naming convention adherence (snake_case, camelCase, etc.)
  - Average file size of modified files
  - Commit message convention analysis (conventional commits, etc.)
  - Common file patterns (test files, config files, etc.)
"""

import re
import logging
from collections import defaultdict, Counter
from typing import Dict

from src.analyzers.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

# Conventional commit pattern: type(scope): description
CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\(.+\))?:\s.+",
    re.IGNORECASE,
)


class CodeStyleAnalyzer(BaseAnalyzer):
    """Computes descriptive code-style markers per consented identity.

    The orchestrator restricts ``BaseAnalyzer._get_commits`` to either the
    local Git user (self-scope, default) or to authors who have given
    informed consent (``--multi-author-team-retro`` mode). This analyzer
    only ever sees commits the orchestrator has already authorised; it does
    not, on its own, scan or filter unconsented contributors.

    Output is descriptive only and MUST NOT be used for evaluation,
    ranking, surveillance, or HR decisions.
    """

    def analyze(self) -> Dict:
        """
        Compute descriptive code-style markers on the *already-scoped*
        commit set.

        Returns:
            Dict keyed by the consented Git identity with descriptive
            code-style markers. In self-scope mode this dict has at most
            one entry (the local Git user).
        """
        author_data = defaultdict(lambda: {
            "file_extensions": Counter(),
            "commit_messages": [],
            "file_sizes": [],
            "file_categories": Counter(),
        })

        for commit in self._get_commits():
            author = commit.author.name
            data = author_data[author]
            data["commit_messages"].append(commit.msg)

            for mod in commit.modified_files:
                filepath = mod.new_path or mod.old_path
                if not filepath:
                    continue

                # File extension tracking
                ext = self._get_extension(filepath)
                if ext:
                    data["file_extensions"][ext] += 1

                # File category
                category = self._categorize_file(filepath)
                data["file_categories"][category] += 1

                # File size tracking (added lines as proxy for new content)
                data["file_sizes"].append(mod.added_lines + mod.deleted_lines)

        result = {}
        for author, data in author_data.items():
            messages = data["commit_messages"]
            total = len(messages)
            if total == 0:
                continue

            # Commit message analysis
            conventional_count = sum(
                1 for m in messages if CONVENTIONAL_COMMIT_RE.match(m.strip())
            )
            avg_msg_len = round(sum(len(m) for m in messages) / total, 1)

            # Messages with issue/ticket references
            issue_ref_count = sum(
                1 for m in messages if re.search(r"#\d+|[A-Z]+-\d+", m)
            )

            # Top languages
            top_extensions = dict(data["file_extensions"].most_common(10))

            # File categories
            file_cats = dict(data["file_categories"])

            # Average change size
            sizes = data["file_sizes"]
            avg_change_size = round(sum(sizes) / len(sizes), 1) if sizes else 0

            result[author] = {
                "total_commits": total,
                "language_distribution": top_extensions,
                "file_category_distribution": file_cats,
                "conventional_commit_ratio": round(conventional_count / total, 3),
                "avg_message_length": avg_msg_len,
                "issue_reference_ratio": round(issue_ref_count / total, 3),
                "avg_change_size_lines": avg_change_size,
            }

        return result

    @staticmethod
    def _get_extension(filepath: str) -> str:
        """Extract file extension from a path."""
        parts = filepath.rsplit(".", 1)
        if len(parts) == 2 and len(parts[1]) <= 10:
            return f".{parts[1].lower()}"
        return ""

    @staticmethod
    def _categorize_file(filepath: str) -> str:
        """Categorize a file by its path and name patterns."""
        path_lower = filepath.lower()

        if any(
            pattern in path_lower
            for pattern in ["test", "spec", "__test__", "_test.", ".test."]
        ):
            return "test"
        if any(
            pattern in path_lower
            for pattern in [
                "config", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".env",
                "dockerfile", "makefile", ".json",
            ]
        ):
            return "config"
        if any(
            pattern in path_lower
            for pattern in [".md", ".rst", ".txt", "readme", "changelog", "license"]
        ):
            return "documentation"
        if any(
            pattern in path_lower
            for pattern in [".css", ".scss", ".less", ".html", ".jsx", ".tsx", ".vue"]
        ):
            return "frontend"
        if any(
            pattern in path_lower
            for pattern in [".sql", "migration", "schema"]
        ):
            return "database"
        if any(
            pattern in path_lower
            for pattern in [".github", ".gitlab", "ci", "cd", "pipeline", "workflow"]
        ):
            return "ci_cd"

        return "source"
