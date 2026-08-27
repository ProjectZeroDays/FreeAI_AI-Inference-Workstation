"""UVL simulator — applies edits to in-memory snapshots with full system context.

OmniRoot: Simulator operates with unrestricted file system access.
Works on ANY absolute path, not just the workspace.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for simulator operations
if not check_capability("system.file.read"):
    raise AssertionError("Simulator requires full file read")
if not check_capability("system.file.write"):
    raise AssertionError("Simulator requires full file write")

from python.verification_sandbox.uvl.simulator import *  # noqa: F401,F403
