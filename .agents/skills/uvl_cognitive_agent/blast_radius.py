"""Blast radius analysis — scoped to workspace boundary.

Authorization model:
Blast radius operations require caller-scoped authorization and are restricted
to the configured workspace boundary. Analysis is limited to workspace files
and processes, not system-wide resources.
"""

from . import authorize_uvl_operation, WORKSPACE_ROOT


def analyze_blast_radius(caller_id: str, file_path: str) -> bool:
    """
    Authorize blast radius analysis for a specific file.

    Args:
        caller_id: Identity of the caller requesting analysis
        file_path: Path to the file to analyze

    Returns:
        True if authorized, False otherwise
    """
    return authorize_uvl_operation(
        caller_id=caller_id, operation="analyze", resource_path=file_path
    )


# Verify authorization framework is available
if not callable(authorize_uvl_operation):
    raise AssertionError("Blast radius requires authorization framework")

__all__ = ["analyze_blast_radius", "authorize_uvl_operation", "WORKSPACE_ROOT"]

# Note: Direct wildcard import removed. Blast radius analysis must explicitly
# authorize each operation with caller identity and path validation.
# System-wide resource access (processes, network, etc.) is no longer permitted.
