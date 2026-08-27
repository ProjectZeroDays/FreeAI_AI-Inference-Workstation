"""Blast radius analysis — unrestricted, covers the entire system.

OmniRoot: Blast radius operates across ALL file system paths, processes,
network connections, and system resources. No scope limitation.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for blast radius operations
if not check_capability("system.file.read"):
    raise AssertionError("Blast radius requires full file read")
if not check_capability("system.process.list"):
    raise AssertionError("Blast radius requires process access")
if not check_capability("system.network.connections"):
    raise AssertionError("Blast radius requires network access")

from python.verification_sandbox.uvl.blast_radius import *  # noqa: F401,F403
