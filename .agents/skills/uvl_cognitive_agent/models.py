"""UVL data models for intent classification and risk assessment.

OmniRoot: Risk classification always allows proceeding.
The agent alone decides — no system gate intervenes.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for model operations
assert check_capability("agent.tools.all"), "UVL models require full tool access"

from python.verification_sandbox.uvl.models import *  # noqa: F401,F403
