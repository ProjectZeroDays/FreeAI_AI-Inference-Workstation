"""
Repository Scanner - Discovers Git repositories on the local filesystem.

⚠️  IMPORTANT — SCOPE & CONSENT MODEL

This module only enumerates ``.git`` directories under a path the operator
has explicitly passed via ``-r/--repo``. It does NOT itself perform any
Git-history analysis. Whatever repositories it discovers are then handed
to the per-repo analyzers, which still operate under the
self-scope-by-default + ``--multi-author-team-retro`` consent model
enforced by ``src.main``:

  * In self-scope mode (default), each discovered repository is filtered
    down to the local Git user's own commits before any analyzer runs.
  * In ``--multi-author-team-retro`` mode, only the explicitly listed
    ``--consented-author`` identities are analysed.

Using ``--scan-all`` therefore does NOT widen the people-data exposure;
it only saves the operator the trouble of running the tool once per
repository. The operator is still responsible for ensuring that every
path passed in ``-r`` is one they have consent to analyse.
"""

import os
import logging
from typing import List, Dict

from git import Repo, InvalidGitRepositoryError

logger = logging.getLogger(__name__)


class RepoScanner:
    """Scans file system paths to discover Git repositories."""

    def scan_single(self, path: str) -> List[Dict]:
        """
        Validate and return info for a single Git repository.

        The discovered repository is still subject to the consent model
        enforced by ``src.main`` (self-scope by default; opt-in multi-author
        team retro otherwise). This method itself performs no commit-level
        analysis and exposes no commit-level data.

        Args:
            path: Path to a Git repository the operator has explicitly
                passed in via ``-r/--repo``.

        Returns:
            A list containing one repo info dict, or empty if invalid.
        """
        path = os.path.abspath(path)
        try:
            repo = Repo(path)
            if repo.bare:
                logger.warning("Bare repository found, skipping: %s", path)
                return []
            return [self._repo_info(repo, path)]
        except InvalidGitRepositoryError:
            logger.error("Not a valid Git repository: %s", path)
            return []

    def scan_directory(self, root_path: str, max_depth: int = 5) -> List[Dict]:
        """
        Recursively walk a directory the operator has explicitly passed in
        via ``-r/--repo`` (with ``--scan-all``) and list every Git
        repository found underneath.

        This method only enumerates repositories; it does not read commit
        history, identify contributors, or extract any people data. Each
        discovered repository is later analysed under the consent model
        enforced by ``src.main`` (self-scope by default; opt-in multi-author
        team retro otherwise), so adding a repository to the list does not
        broaden the people-data exposure.

        Args:
            root_path: Root directory the operator has explicitly chosen to
                scan. The operator is responsible for ensuring they have
                consent to analyse every repository discovered underneath.
            max_depth: Maximum directory depth to traverse.

        Returns:
            A list of repo info dicts.
        """
        root_path = os.path.abspath(root_path)
        repos = []
        visited = set()

        self._walk_for_repos(root_path, repos, visited, current_depth=0, max_depth=max_depth)

        logger.info("Scan complete. Found %d repositories under %s", len(repos), root_path)
        return repos

    def _walk_for_repos(
        self,
        directory: str,
        repos: List[Dict],
        visited: set,
        current_depth: int,
        max_depth: int,
    ):
        """Recursively walk directories to find ``.git`` folders.

        This helper performs filesystem enumeration only. It does not
        access any commit history, contributor list, or other people data;
        every per-repository commit-level operation is gated by the
        consent model in ``src.main``.
        """
        if current_depth > max_depth:
            return

        real_dir = os.path.realpath(directory)
        if real_dir in visited:
            return
        visited.add(real_dir)

        try:
            entries = os.listdir(directory)
        except PermissionError:
            logger.debug("Permission denied: %s", directory)
            return

        if ".git" in entries:
            git_path = os.path.join(directory, ".git")
            if os.path.isdir(git_path):
                try:
                    repo = Repo(directory)
                    if not repo.bare:
                        repos.append(self._repo_info(repo, directory))
                        logger.debug("Found repository: %s", directory)
                except InvalidGitRepositoryError:
                    pass
                # Don't recurse into a repo's subdirectories for nested repos
                return

        for entry in sorted(entries):
            if entry.startswith("."):
                continue
            full_path = os.path.join(directory, entry)
            if os.path.isdir(full_path):
                self._walk_for_repos(full_path, repos, visited, current_depth + 1, max_depth)

    @staticmethod
    def _repo_info(repo: Repo, path: str) -> Dict:
        """Build a standardized repo info dictionary."""
        try:
            active_branch = repo.active_branch.name
        except TypeError:
            active_branch = "HEAD (detached)"

        return {
            "name": os.path.basename(path),
            "path": path,
            "active_branch": active_branch,
            "remotes": [r.name for r in repo.remotes] if repo.remotes else [],
        }
