"""Approval profiles (ROADMAP 16) � suggest / auto / full-auto."""
from enum import Enum
class Approval(str, Enum):
    SUGGEST = "suggest"  # shell requires dashboard confirm
    AUTO = "auto"        # shell auto-approved, network off
    FULL_AUTO = "full-auto"  # everything auto (current default)

# Dashboard confirm queue: POST /api/approvals/{run_id}/confirm
# Stored in config/approvals.jsonl
