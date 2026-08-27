"""UVL utility functions.

Authorization model:
Utility operations require caller-scoped authorization and are restricted
to the configured workspace boundary. All resource access requires explicit
authorization with caller identity and path validation.
"""

from . import authorize_uvl_operation, WORKSPACE_ROOT


def access_resource(caller_id: str, resource_path: str, operation: str) -> bool:
    """
    Authorize utility operation for a specific resource.

    Args:
        caller_id: Identity of the caller requesting access
        resource_path: Path to the resource
        operation: Operation type

    Returns:
        True if authorized, False otherwise
    """
    return authorize_uvl_operation(
        caller_id=caller_id, operation=operation, resource_path=resource_path
    )


# Verify authorization framework is available
if not callable(authorize_uvl_operation):
    raise AssertionError("UVL utils require authorization framework")

__all__ = ["access_resource", "authorize_uvl_operation", "WORKSPACE_ROOT"]

# Note: Direct wildcard import removed. Utility operations must explicitly
# authorize each access with caller identity and path validation.
