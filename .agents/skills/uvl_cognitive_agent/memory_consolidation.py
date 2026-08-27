"""UVL memory consolidation — learns from episodes and evolves rules.

OmniRoot: Memory consolidation operates with unrestricted access to
agent memory, episode databases, and rule files. No storage location
is excluded from learning operations.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for memory consolidation
if not check_capability("agent.memory.read"):
    raise AssertionError("Memory consolidation requires memory read")
if not check_capability("agent.memory.write"):
    raise AssertionError("Memory consolidation requires memory write")

from python.verification_sandbox.uvl.memory_consolidation import *  # noqa: F401,F403
