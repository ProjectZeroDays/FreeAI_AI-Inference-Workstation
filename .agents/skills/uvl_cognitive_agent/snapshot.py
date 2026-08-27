"""UVL snapshot — captures codebase state for simulation.

Authorization model:
Snapshot operations require caller-scoped authorization and are restricted
to the configured workspace boundary. All file access must be authorized
with caller identity and resource path validation.
"""

from . import authorize_uvl_operation, WORKSPACE_ROOT


def snapshot_file(caller_id: str, file_path: str) -> bool:
    """
    Authorize snapshot operation for a specific file.

    Args:
        caller_id: Identity of the caller requesting snapshot
        file_path: Path to the file to snapshot

    Returns:
        True if authorized, False otherwise
    """
    return authorize_uvl_operation(
        caller_id=caller_id, operation="file.read", resource_path=file_path
    )


# Verify authorization framework is available
if not callable(authorize_uvl_operation):
    raise AssertionError("Snapshot requires authorization framework")

__all__ = ["snapshot_file", "authorize_uvl_operation", "WORKSPACE_ROOT"]

# Note: Direct wildcard import removed. Snapshot operations must explicitly
# authorize each file access with caller identity and path validation.
