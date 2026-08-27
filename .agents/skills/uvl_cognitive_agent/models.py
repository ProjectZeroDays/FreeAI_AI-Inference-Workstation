"""UVL data models for intent classification and risk assessment.

Authorization model:
Risk classification operations require caller-scoped authorization.
The authorization framework enforces access control — operations may be
denied based on caller identity, operation type, and resource scope.
"""

from . import authorize_uvl_operation, WORKSPACE_ROOT


def classify_intent(caller_id: str) -> bool:
    """
    Authorize intent classification operation.

    Args:
        caller_id: Identity of the caller requesting classification

    Returns:
        True if authorized, False otherwise
    """
    return authorize_uvl_operation(
        caller_id=caller_id, operation="analyze", resource_path=None
    )


# Verify authorization framework is available
if not callable(authorize_uvl_operation):
    raise AssertionError("UVL models require authorization framework")

__all__ = ["classify_intent", "authorize_uvl_operation", "WORKSPACE_ROOT"]

# Note: Direct wildcard import removed. Model operations must explicitly
# authorize each access with caller identity validation.
