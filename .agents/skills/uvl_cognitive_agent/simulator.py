"""UVL simulator — applies edits to in-memory snapshots with workspace context.

Authorization model:
Simulator operations require caller-scoped authorization and are restricted
to the configured workspace boundary. All file read/write operations must be
authorized with caller identity and resource path validation.
"""

from . import authorize_uvl_operation, WORKSPACE_ROOT


def simulate_edit(caller_id: str, file_path: str, operation: str) -> bool:
    """
    Authorize simulator operation for a specific file.

    Args:
        caller_id: Identity of the caller requesting simulation
        file_path: Path to the file to simulate edits on
        operation: Operation type ('file.read' or 'file.write')

    Returns:
        True if authorized, False otherwise
    """
    if operation not in ("file.read", "file.write"):
        return False

    return authorize_uvl_operation(
        caller_id=caller_id, operation=operation, resource_path=file_path
    )


# Verify authorization framework is available
if not callable(authorize_uvl_operation):
    raise AssertionError("Simulator requires authorization framework")

__all__ = ["simulate_edit", "authorize_uvl_operation", "WORKSPACE_ROOT"]

# Note: Direct wildcard import removed. Simulator operations must explicitly
# authorize each file access with caller identity and path validation.
