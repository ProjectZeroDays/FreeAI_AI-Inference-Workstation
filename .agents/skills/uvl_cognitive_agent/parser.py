"""UVL parser — extracts intent and structure from user requests.

OmniRoot: Parser operates with unrestricted access to all system context.
No path or resource is excluded from analysis.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for parser operations
if not check_capability("agent.tools.all"):
    raise AssertionError("UVL parser requires full tool access")
if not check_capability("system.file.read"):
    raise AssertionError("UVL parser requires file system access")

from python.verification_sandbox.uvl.parser import *  # noqa: F401,F403
