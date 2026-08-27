"""
Code Quality Analyzer - Analyzes code quality signals from Git history.

Metrics include:
  - Bug fix commit ratio
  - Hotfix/revert frequency
  - Large commit ratio (potential code smell)
  - Test file modification ratio
  - Code complexity trend (via radon for Python files)
  - Documentation update ratio
"""

import logging
import os
import re
import tempfile
from collections import defaultdict
from typing import Dict

from src.analyzers.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

# Patterns for identifying bug fix / hotfix commits
BUG_FIX_PATTERNS = [
    re.compile(r"\bfix(es|ed)?\b", re.IGNORECASE),
    re.compile(r"\bbug\b", re.IGNORECASE),
    re.compile(r"\bpatch\b", re.IGNORECASE),
    re.compile(r"\bhotfix\b", re.IGNORECASE),
    re.compile(r"\bresolve[sd]?\b", re.IGNORECASE),
]

REVERT_PATTERN = re.compile(r"\brevert\b", re.IGNORECASE)

LARGE_COMMIT_THRESHOLD = 500  # lines changed


class CodeQualityAnalyzer(BaseAnalyzer):
    """Computes descriptive code-quality artefacts per consented identity.

    The orchestrator restricts ``BaseAnalyzer._get_commits`` to either the
    local Git user (self-scope, default) or to authors who have given
    informed consent (``--multi-author-team-retro`` mode). This analyzer
    only operates on commits the orchestrator has already authorised.

    Output is descriptive only and MUST NOT be used for evaluation,
    ranking, surveillance, or HR decisions.
    """

    def analyze(self) -> Dict:
        """
        Compute descriptive code-quality artefacts on the *already-scoped*
        commit set.

        Returns:
            Dict keyed by the consented Git identity with descriptive
            code-quality artefacts. In self-scope mode this dict has at
            most one entry (the local Git user).
        """
        author_data = defaultdict(lambda: {
            "total_commits": 0,
            "bug_fix_commits": 0,
            "revert_commits": 0,
            "large_commits": 0,
            "test_file_modifications": 0,
            "doc_file_modifications": 0,
            "total_file_modifications": 0,
            "commit_sizes": [],
            "python_files_content": [],  # for complexity analysis
        })

        for commit in self._get_commits():
            author = commit.author.name
            data = author_data[author]
            data["total_commits"] += 1

            msg = commit.msg

            # Bug fix detection
            if any(p.search(msg) for p in BUG_FIX_PATTERNS):
                data["bug_fix_commits"] += 1

            # Revert detection
            if REVERT_PATTERN.search(msg):
                data["revert_commits"] += 1

            # Analyze modified files
            total_lines_changed = 0
            for mod in commit.modified_files:
                filepath = mod.new_path or mod.old_path or ""
                lines_changed = mod.added_lines + mod.deleted_lines
                total_lines_changed += lines_changed
                data["total_file_modifications"] += 1

                # Test file detection
                if self._is_test_file(filepath):
                    data["test_file_modifications"] += 1

                # Documentation file detection
                if self._is_doc_file(filepath):
                    data["doc_file_modifications"] += 1

                # Collect Python file content for complexity analysis
                if filepath.endswith(".py") and mod.source_code:
                    data["python_files_content"].append(mod.source_code)

            data["commit_sizes"].append(total_lines_changed)
            if total_lines_changed > LARGE_COMMIT_THRESHOLD:
                data["large_commits"] += 1

        result = {}
        for author, data in author_data.items():
            total = data["total_commits"]
            if total == 0:
                continue

            total_mods = data["total_file_modifications"]

            # Calculate complexity metrics for Python files
            avg_complexity = self._compute_avg_complexity(data["python_files_content"])

            sizes = data["commit_sizes"]
            avg_commit_size = round(sum(sizes) / len(sizes), 1) if sizes else 0
            median_size = sorted(sizes)[len(sizes) // 2] if sizes else 0

            result[author] = {
                "total_commits": total,
                "bug_fix_commits": data["bug_fix_commits"],
                "bug_fix_ratio": round(data["bug_fix_commits"] / total, 3),
                "revert_commits": data["revert_commits"],
                "revert_ratio": round(data["revert_commits"] / total, 3),
                "large_commits": data["large_commits"],
                "large_commit_ratio": round(data["large_commits"] / total, 3),
                "test_modification_ratio": round(
                    data["test_file_modifications"] / total_mods, 3
                ) if total_mods else 0,
                "doc_modification_ratio": round(
                    data["doc_file_modifications"] / total_mods, 3
                ) if total_mods else 0,
                "avg_commit_size": avg_commit_size,
                "median_commit_size": median_size,
                "avg_python_complexity": avg_complexity,
            }

        return result

    @staticmethod
    def _is_test_file(filepath: str) -> bool:
        """Check if a file is a test file."""
        path_lower = filepath.lower()
        return any(
            pattern in path_lower
            for pattern in [
                "test", "spec", "__test__", "_test.", ".test.",
                "tests/", "test/", "spec/",
            ]
        )

    @staticmethod
    def _is_doc_file(filepath: str) -> bool:
        """Check if a file is a documentation file."""
        path_lower = filepath.lower()
        return any(
            path_lower.endswith(ext)
            for ext in [".md", ".rst", ".txt", ".adoc"]
        ) or any(
            name in path_lower
            for name in ["readme", "changelog", "contributing", "license", "docs/"]
        )

    @staticmethod
    def _compute_avg_complexity(python_sources: list) -> float:
        """
        Compute average cyclomatic complexity for Python source code samples.

        Uses radon library for complexity analysis.
        """
        if not python_sources:
            return 0.0

        try:
            from radon.complexity import cc_visit
        except ImportError:
            logger.warning("radon not installed, skipping complexity analysis")
            return 0.0

        complexities = []
        for source in python_sources[:50]:  # Limit to avoid performance issues
            try:
                results = cc_visit(source)
                for block in results:
                    complexities.append(block.complexity)
            except Exception:
                continue

        if not complexities:
            return 0.0

        return round(sum(complexities) / len(complexities), 2)
