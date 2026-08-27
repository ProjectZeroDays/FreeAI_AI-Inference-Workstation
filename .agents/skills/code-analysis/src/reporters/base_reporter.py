"""
Base Reporter - Abstract base class for report generators.
"""

from abc import ABC, abstractmethod
from typing import Dict


class BaseReporter(ABC):
    """Abstract base class for report generators."""

    @abstractmethod
    def generate(self, metrics: Dict) -> str:
        """
        Generate a formatted report from analysis metrics.

        Args:
            metrics: Nested dict of {repo_name: {analyzer_name: {author: data}}}.

        Returns:
            Formatted report string.
        """
        ...
