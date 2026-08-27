"""
Utility functions for the code analysis skills.
"""

import os
from datetime import datetime
from typing import Optional


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse a date string in ISO format.

    Args:
        date_str: Date string like '2024-01-01' or '2024-01-01T10:00:00'.

    Returns:
        datetime object or None if input is empty/None.
    """
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'. Use ISO format (e.g., '2024-01-01').")


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """Format a decimal ratio as percentage string."""
    return f"{value * 100:.{decimal_places}f}%"


def format_number(value: int) -> str:
    """Format a number with thousands separator."""
    return f"{value:,}"


def ensure_directory(path: str) -> str:
    """Ensure a directory exists, create if needed, return absolute path."""
    abs_path = os.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
