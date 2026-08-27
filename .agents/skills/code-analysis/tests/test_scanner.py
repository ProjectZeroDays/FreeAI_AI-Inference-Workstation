"""
Tests for the repository scanner.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from src.scanner import RepoScanner


class TestRepoScanner:
    """Tests for RepoScanner class."""

    def test_scan_single_valid_repo(self, tmp_path):
        """Test scanning a valid Git repository."""
        # Create a temporary git repo
        repo_path = str(tmp_path / "test_repo")
        os.makedirs(repo_path)
        os.system(f"cd {repo_path} && git init && git commit --allow-empty -m 'init'")

        scanner = RepoScanner()
        repos = scanner.scan_single(repo_path)

        assert len(repos) == 1
        assert repos[0]["name"] == "test_repo"
        assert repos[0]["path"] == repo_path

    def test_scan_single_invalid_path(self, tmp_path):
        """Test scanning an invalid path."""
        scanner = RepoScanner()
        repos = scanner.scan_single(str(tmp_path / "nonexistent"))

        assert len(repos) == 0

    def test_scan_single_non_git_directory(self, tmp_path):
        """Test scanning a directory that is not a Git repo."""
        scanner = RepoScanner()
        repos = scanner.scan_single(str(tmp_path))

        assert len(repos) == 0

    def test_scan_directory_finds_repos(self, tmp_path):
        """Test recursive scanning finds multiple repos."""
        # Create two git repos
        for name in ["repo_a", "repo_b"]:
            repo_path = str(tmp_path / name)
            os.makedirs(repo_path)
            os.system(f"cd {repo_path} && git init && git commit --allow-empty -m 'init'")

        scanner = RepoScanner()
        repos = scanner.scan_directory(str(tmp_path))

        assert len(repos) == 2
        repo_names = {r["name"] for r in repos}
        assert "repo_a" in repo_names
        assert "repo_b" in repo_names

    def test_scan_directory_respects_max_depth(self, tmp_path):
        """Test that max_depth limits recursive scanning."""
        # Create a deeply nested repo
        deep_path = tmp_path / "a" / "b" / "c" / "d" / "e" / "f" / "deep_repo"
        os.makedirs(str(deep_path))
        os.system(f"cd {deep_path} && git init && git commit --allow-empty -m 'init'")

        scanner = RepoScanner()
        repos = scanner.scan_directory(str(tmp_path), max_depth=2)

        # Repo is at depth 7, should not be found with max_depth=2
        assert len(repos) == 0

    def test_scan_directory_empty(self, tmp_path):
        """Test scanning empty directory."""
        scanner = RepoScanner()
        repos = scanner.scan_directory(str(tmp_path))

        assert len(repos) == 0
