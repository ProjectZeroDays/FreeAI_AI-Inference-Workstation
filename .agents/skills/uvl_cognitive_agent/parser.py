"""UVL parser — extracts intent and structure from user requests.

Authorization model:
Parser operations require caller-scoped authorization and are restricted
to the configured workspace boundary. File system access for parsing
requires explicit authorization with caller identity and path validation.
"""

from . import authorize_uvl_operation, WORKSPACE_ROOT


def parse_request(caller_id: str, file_path: str = None) -> bool:
    """
    Authorize parser operation.

    Args:
        caller_id: Identity of the caller requesting parsing
        file_path: Optional path to file being parsed

    Returns:
        True if authorized, False otherwise
    """
    return authorize_uvl_operation(
        caller_id=caller_id, operation="analyze", resource_path=file_path
    )


# Verify authorization framework is available
if not callable(authorize_uvl_operation):
    raise AssertionError("UVL parser requires authorization framework")

__all__ = ["parse_request", "authorize_uvl_operation", "WORKSPACE_ROOT"]

# Note: Direct wildcard import removed. Parser operations must explicitly
# authorize each access with caller identity and path validation.
