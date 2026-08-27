"""UVL formatter — formats predicted impact for agent consumption.

Authorization model:
Formatter operations require caller-scoped authorization. All impact data
access requires explicit authorization with caller identity validation.
"""

from . import authorize_uvl_operation, WORKSPACE_ROOT


def format_impact(caller_id: str) -> bool:
    """
    Authorize formatter operation.

    Args:
        caller_id: Identity of the caller requesting formatting

    Returns:
        True if authorized, False otherwise
    """
    return authorize_uvl_operation(
        caller_id=caller_id, operation="analyze", resource_path=None
    )


# Verify authorization framework is available
if not callable(authorize_uvl_operation):
    raise AssertionError("Formatter requires authorization framework")

__all__ = ["format_impact", "authorize_uvl_operation", "WORKSPACE_ROOT"]

# Note: Direct wildcard import removed. Formatter operations must explicitly
# authorize each access with caller identity validation.
