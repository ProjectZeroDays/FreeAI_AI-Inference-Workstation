"""
Base Analyzer - Abstract base class for all analyzers.

⚠️  IMPORTANT — INTERNAL CONSENT-GATED ENTRYPOINT

The ``authors`` constructor argument is **not** a public author filter for
library consumers. It is an internal channel that the CLI orchestrator
(``src.main``) populates **only after** it has:

  1. confirmed the operator's ``--i-have-consent`` acknowledgement, and
  2. resolved the authorised identity set (the local Git user under
     self-scope, or each ``--consented-author`` entry under the explicit
     ``--multi-author-team-retro`` opt-in).

Calling ``BaseAnalyzer`` (or any subclass) directly from another Python
module — e.g. to scan an arbitrary author's commits without going through
``src.main`` — bypasses that consent gate and is **not a supported use of
this skill**. Doing so would defeat the privacy and anti-surveillance
controls described in the skill manifest, and is the operator's own
responsibility, not a feature of this codebase.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from pydriller import Repository

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """
    Abstract base class providing common infrastructure for all analyzers.

    Each analyzer receives a repository path and **already-consented**
    identity filters from the CLI orchestrator, then implements the
    ``analyze()`` method to produce structured, descriptive markers.

    Direct instantiation outside the CLI orchestrator is not a supported
    use of this skill (see module docstring).
    """

    def __init__(
        self,
        repo_path: str,
        authors: Optional[List[str]] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        branch: Optional[str] = None,
    ):
        # NOTE: ``authors`` here is the *consent-resolved* identity list
        # produced by ``src.main``. It is NOT a generic public filter and
        # must not be repurposed to target arbitrary contributors.
        self.repo_path = repo_path
        self.authors = authors
        self.since = since
        self.until = until
        self.branch = branch

    def _get_commits(self):
        """
        Yield commits from the repository applying configured filters.

        Uses PyDriller for rich commit traversal. The ``self.authors``
        identity filter applied here is the *already-consented* set passed
        in by the CLI orchestrator; this method does not perform consent
        checks of its own.
        """
        kwargs = {"path_to_repo": self.repo_path}

        if self.since:
            from datetime import datetime
            kwargs["since"] = datetime.fromisoformat(self.since)
        if self.until:
            from datetime import datetime
            kwargs["to"] = datetime.fromisoformat(self.until)
        if self.branch:
            kwargs["only_in_branch"] = self.branch

        try:
            for commit in Repository(**kwargs).traverse_commits():
                if self.authors:
                    if not self._author_matches(commit.author.name, commit.author.email):
                        continue
                yield commit
        except Exception as e:
            logger.error("Error traversing commits in %s: %s", self.repo_path, e)

    def _author_matches(self, name: str, email: str) -> bool:
        """Check whether a commit's author name/email is in the
        consent-resolved identity set populated by the orchestrator."""
        for author_filter in self.authors:
            af_lower = author_filter.lower()
            if af_lower in name.lower() or af_lower in email.lower():
                return True
        return False

    @abstractmethod
    def analyze(self) -> Dict:
        """
        Run analysis and return structured, descriptive markers.

        Returns:
            A dict keyed by the consented Git identity. In self-scope mode
            this dict has at most one entry (the local Git user). In
            ``--multi-author-team-retro`` mode, only the explicitly
            consented identities appear.
        """
        ...
