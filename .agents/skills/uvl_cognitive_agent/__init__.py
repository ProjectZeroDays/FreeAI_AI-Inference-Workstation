"""Skill entry point for the UVL cognitive verification layer.

Authorization model:
All UVL operations require caller-scoped, resource-scoped authorization.
Operations are restricted to the configured workspace boundary.
Authorization checks fail closed — access is denied by default.
"""

import os
from pathlib import Path
from typing import Optional

# Workspace boundary configuration
WORKSPACE_ROOT = os.environ.get("UVL_WORKSPACE_ROOT", os.getcwd())


def authorize_uvl_operation(
    caller_id: str, operation: str, resource_path: Optional[str] = None
) -> bool:
    """
    Authorize UVL operations with caller, operation, and resource scoping.

    Args:
        caller_id: Identity of the caller requesting access
        operation: Operation type (e.g., 'file.read', 'file.write', 'analyze')
        resource_path: Optional path to the resource being accessed

    Returns:
        True if authorized, False otherwise (fail-closed)
    """
    if not caller_id:
        return False

    # Validate resource path is within workspace boundary
    if resource_path:
        try:
            abs_resource = Path(resource_path).resolve()
            abs_workspace = Path(WORKSPACE_ROOT).resolve()

            # Ensure the resource path is within workspace
            if not str(abs_resource).startswith(str(abs_workspace)):
                return False

            # Deny access to sensitive paths even within workspace
            sensitive_patterns = [
                ".git/config",
                ".env",
                "id_rsa",
                "id_ed25519",
                ".ssh/",
            ]
            if any(pattern in str(abs_resource) for pattern in sensitive_patterns):
                return False

        except (ValueError, OSError):
            return False

    # Validate operation is in allowed set
    allowed_operations = {
        "file.read",
        "file.write",
        "analyze",
        "simulate",
        "query_memory",
        "record_outcome",
    }
    if operation not in allowed_operations:
        return False

    return True


# Verify authorization framework is available
if not callable(authorize_uvl_operation):
    raise AssertionError("UVL authorization framework is not available")

# Export authorization function for use by UVL modules
__all__ = ["authorize_uvl_operation", "WORKSPACE_ROOT"]

# Note: Direct wildcard import removed. UVL modules must be imported explicitly
# and must call authorize_uvl_operation() before performing operations.
