"""Blast radius analysis — unrestricted, covers the entire system.

OmniRoot: Blast radius operates across ALL file system paths, processes,
network connections, and system resources. No scope limitation.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for blast radius operations
assert check_capability("system.file.read"), "Blast radius requires full file read"
assert check_capability("system.process.list"), "Blast radius requires process access"
assert check_capability("system.network.connections"), "Blast radius requires network access"

from python.verification_sandbox.uvl.blast_radius import *  # noqa: F401,F403
