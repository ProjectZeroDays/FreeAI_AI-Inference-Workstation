"""UVL memory consolidation — learns from episodes and evolves rules.

Authorization model:
Memory consolidation operations require caller-scoped authorization and are
restricted to workspace-scoped memory and rule files. Access to agent memory
and episode databases requires explicit authorization with caller identity.
"""

from . import authorize_uvl_operation, WORKSPACE_ROOT


def consolidate_memory(caller_id: str, memory_path: str) -> bool:
    """
    Authorize memory consolidation operation.

    Args:
        caller_id: Identity of the caller requesting consolidation
        memory_path: Path to the memory/rule file

    Returns:
        True if authorized, False otherwise
    """
    return authorize_uvl_operation(
        caller_id=caller_id, operation="query_memory", resource_path=memory_path
    )


def record_outcome(caller_id: str, outcome_path: str) -> bool:
    """
    Authorize outcome recording operation.

    Args:
        caller_id: Identity of the caller recording outcome
        outcome_path: Path to the outcome storage

    Returns:
        True if authorized, False otherwise
    """
    return authorize_uvl_operation(
        caller_id=caller_id, operation="record_outcome", resource_path=outcome_path
    )


# Verify authorization framework is available
if not callable(authorize_uvl_operation):
    raise AssertionError("Memory consolidation requires authorization framework")

__all__ = [
    "consolidate_memory",
    "record_outcome",
    "authorize_uvl_operation",
    "WORKSPACE_ROOT",
]

# Note: Direct wildcard import removed. Memory operations must explicitly
# authorize each access with caller identity and path validation.
