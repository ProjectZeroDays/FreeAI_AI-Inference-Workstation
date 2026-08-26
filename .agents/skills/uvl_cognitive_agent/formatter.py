"""UVL formatter — formats predicted impact for agent consumption.

OmniRoot: Formatter operates without restriction.
All impact data is surfaced to the agent for decision-making.
"""

from python.helpers.omni_capability import check_capability, get_privilege_manager

# Verify omnipotent access for formatter operations
assert check_capability("agent.tools.all"), "Formatter requires full tool access"

from python.verification_sandbox.uvl.formatter import *  # noqa: F401,F403
