"""
Tests for analyzer modules.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from src.analyzers.commit_analyzer import CommitAnalyzer
from src.analyzers.work_habit_analyzer import WorkHabitAnalyzer
from src.analyzers.code_quality_analyzer import CodeQualityAnalyzer


class TestCommitAnalyzer:
    """Tests for CommitAnalyzer."""

    @patch.object(CommitAnalyzer, "_get_commits")
    def test_analyze_empty_repo(self, mock_commits):
        """Test analysis on repo with no commits."""
        mock_commits.return_value = iter([])
        analyzer = CommitAnalyzer("/fake/path")
        result = analyzer.analyze()
        assert result == {}

    @patch.object(CommitAnalyzer, "_get_commits")
    def test_analyze_single_author(self, mock_commits):
        """Test analysis with a single author's commits."""
        commits = []
        for i in range(5):
            commit = MagicMock()
            commit.author.name = "Alice"
            commit.author.email = "alice@example.com"
            commit.committer_date = datetime(2024, 1, i + 1, 10, 0, tzinfo=timezone.utc)
            commit.msg = f"Commit message {i}"
            commit.merge = False
            mod = MagicMock()
            mod.added_lines = 10
            mod.deleted_lines = 3
            commit.modified_files = [mod]
            commits.append(commit)

        mock_commits.return_value = iter(commits)
        analyzer = CommitAnalyzer("/fake/path")
        result = analyzer.analyze()

        assert "Alice" in result
        assert result["Alice"]["total_commits"] == 5
        assert result["Alice"]["merge_commits"] == 0
        assert result["Alice"]["avg_lines_added"] == 10.0
        assert result["Alice"]["avg_lines_deleted"] == 3.0


class TestWorkHabitAnalyzer:
    """Tests for WorkHabitAnalyzer."""

    def test_longest_streak(self):
        """Test consecutive streak calculation."""
        from datetime import date
        dates = [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 5)]
        result = WorkHabitAnalyzer._longest_streak(dates)
        assert result == 3

    def test_longest_streak_single(self):
        """Test streak with single date."""
        from datetime import date
        dates = [date(2024, 1, 1)]
        result = WorkHabitAnalyzer._longest_streak(dates)
        assert result == 1

    def test_longest_streak_empty(self):
        """Test streak with no dates."""
        result = WorkHabitAnalyzer._longest_streak([])
        assert result == 0

    def test_avg_time_gap(self):
        """Test average time gap calculation."""
        times = [
            datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
            datetime(2024, 1, 1, 16, 0, tzinfo=timezone.utc),
        ]
        result = WorkHabitAnalyzer._avg_time_gap(times)
        assert result == 3.0  # (2 + 4) / 2 = 3.0 hours


class TestCodeQualityAnalyzer:
    """Tests for CodeQualityAnalyzer."""

    def test_is_test_file(self):
        """Test file classification for test files."""
        assert CodeQualityAnalyzer._is_test_file("tests/test_main.py") is True
        assert CodeQualityAnalyzer._is_test_file("src/main.py") is False
        assert CodeQualityAnalyzer._is_test_file("app/__test__/utils.js") is True
        assert CodeQualityAnalyzer._is_test_file("app/utils.spec.ts") is True

    def test_is_doc_file(self):
        """Test file classification for documentation files."""
        assert CodeQualityAnalyzer._is_doc_file("README.md") is True
        assert CodeQualityAnalyzer._is_doc_file("docs/guide.rst") is True
        assert CodeQualityAnalyzer._is_doc_file("src/main.py") is False
        assert CodeQualityAnalyzer._is_doc_file("CHANGELOG.md") is True
