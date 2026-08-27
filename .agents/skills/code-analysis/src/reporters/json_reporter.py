"""
JSON Reporter - Generates analysis reports in JSON format.
"""

import json
from typing import Dict

from src.reporters.base_reporter import BaseReporter


class JsonReporter(BaseReporter):
    """Generates structured JSON reports from analysis metrics."""

    def generate(self, metrics: Dict) -> str:
        """Generate a JSON report."""
        # Clean metrics for JSON serialization
        cleaned = self._clean_for_json(metrics)
        return json.dumps(cleaned, indent=2, ensure_ascii=False, default=str)

    def _clean_for_json(self, obj):
        """Recursively clean objects for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._clean_for_json(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
