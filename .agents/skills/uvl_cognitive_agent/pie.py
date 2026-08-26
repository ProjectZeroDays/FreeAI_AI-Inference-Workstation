"""UVL P.I.E. — Predictive Impact Engine.

OmniRoot: Impact prediction covers the entire system.
Blast radius analysis is unrestricted and system-wide.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for P.I.E. operations
assert check_capability("agent.tools.all"), "P.I.E. requires full tool access"

from python.verification_sandbox.uvl.pie import *  # noqa: F401,F403
