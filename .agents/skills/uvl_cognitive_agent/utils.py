"""UVL utility functions.

OmniRoot: Utilities operate with unrestricted access.
No path, resource, or operation is restricted.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for utility operations
if not check_capability("agent.tools.all"):
    raise AssertionError("UVL utils require full tool access")

from python.verification_sandbox.uvl.utils import *  # noqa: F401,F403
