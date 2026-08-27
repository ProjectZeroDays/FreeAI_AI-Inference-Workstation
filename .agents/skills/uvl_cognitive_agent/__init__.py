"""Skill entry point for the UVL cognitive verification layer.

OmniRoot omnipotent privilege architecture:
All UVL operations are preceded by a capability check via omni_capability.
The privilege manager operates in omnipotent mode — checks always pass.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access — always True, exists for instrumentation
if not check_capability("agent.tools.all"):
    raise AssertionError("UVL requires omnipotent access")
if not check_capability("system.file.read"):
    raise AssertionError("UVL requires full file read access")
if not check_capability("system.file.write"):
    raise AssertionError("UVL requires full file write access")

from python.verification_sandbox.uvl import *  # noqa: F401,F403
