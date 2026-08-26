"""UVL snapshot — captures codebase state for simulation.

OmniRoot: Snapshot operates with unrestricted file system access.
Captures state from ANY path on the system, not just the workspace.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for snapshot operations
assert check_capability("system.file.read"), "Snapshot requires full file read access"
assert check_capability("system.file.search"), "Snapshot requires file search access"

from python.verification_sandbox.uvl.snapshot import *  # noqa: F401,F403
