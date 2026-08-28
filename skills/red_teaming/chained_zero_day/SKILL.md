---
name: chained_zero_day
description: >
  Chained zero-day exploitation simulation: multi-stage attack chains with AI-assisted
  optimization, vulnerability correlation, and chain viability scoring.
triggers:
  - exploit chain
  - chained exploit
  - zero-day chain
  - multi-stage attack
  - pegasus
  - forcedentry
  - blastpass
  - chain optimization
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-28"
  agent: agents/specialized/chained_zero_day.py
---

# Chained Zero-Day Exploitation Agent

Multi-stage exploit chain simulation with AI-assisted chain optimization, automatic vulnerability correlation, and chain viability scoring.

## Purpose
Model and simulate chained zero-day exploits where multiple vulnerabilities are combined to achieve a complete attack lifecycle: initial access, privilege escalation, persistence, and data exfiltration.

## Capabilities
- **Chain Building**: Construct multi-stage exploit chains from individual vulnerability components
- **Chain Analysis**: Analyze chain viability, dependencies, and success probability
- **Chain Simulation**: Simulate chain execution against targets (returns `{"status": "simulated"}`)
- **Chain Optimization**: AI-assisted suggestions for improving chain reliability and stealth
- **Real-World Chains**: Reference database of documented exploit chains (Pegasus, FORCEDENTRY, BLASTPASS)
- **CVE Database**: CVE lookup for chain building components
- **Dependency Analysis**: Map inter-stage dependencies and failure modes
- **Success Probability**: Calculate overall chain success probability from individual stage probabilities

## Exploit Chain Stages

### Stage 1: Initial Access
- Messaging RCE (e.g., iMessage, WhatsApp, Signal)
- Browser exploitation (drive-by, malicious link)
- Document parsing (PDF, Office, image)
- Network service exploitation

### Stage 2: Privilege Escalation
- Kernel LPE (use-after-free, race condition)
- Sandbox escape (browser sandbox, app sandbox)
- Configuration abuse (misconfigured services, weak permissions)

### Stage 3: Persistence
- File system persistence (launch daemons, cron, scheduled tasks)
- Registry persistence (Windows registry, macOS preferences)
- Firmware persistence (UEFI, bootloader)
- Account persistence (backdoor accounts, SSH keys)

### Stage 4: Data Exfiltration
- Covert channels (DNS tunneling, ICMP, steganography)
- Encrypted exfiltration (HTTPS, custom C2)
- Timing-based exfiltration (low-and-slow)

## Real-World Exploit Chains

### Pegasus (NSO Group)
- CVE-2019-8641: iMessage vulnerability (initial access)
- CVE-2019-8646: Kernel vulnerability (privilege escalation)
- CVE-2019-8647: Sandbox escape (persistence)

### FORCEDENTRY
- Image parsing vulnerability in iMessage (initial access)
- Bypasses blast door protections
- No-click exploitation chain

### BLASTPASS
- Image parsing vulnerability (initial access)
- Kernel privilege escalation
- Full device compromise without user interaction

## AI Pattern: Chain Optimization
- Automatic vulnerability correlation across stages
- Chain viability scoring based on target environment
- Success probability calculation using Bayesian inference
- Alternative path suggestions when primary chain fails
- Stealth optimization to minimize detection probability

## Usage
```python
from agents.specialized.chained_zero_day import ChainedZeroDayAgent

agent = ChainedZeroDayAgent()

# Describe capabilities
info = agent.describe()

# Build a chain
chain = agent.build_chain(stages=[
    {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"},
    {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2019-8646"},
    {"stage": 3, "type": "sandbox_escape", "cve": "CVE-2019-8647"},
    {"stage": 4, "type": "covert_channel", "method": "dns_tunnel"}
])
chain_id = chain["chain_id"]

# Analyze chain viability
analysis = agent.analyze_chain(chain_id)

# Simulate chain execution
result = agent.simulate_chain(chain_id, target="192.168.1.100")

# List known real-world chains
chains = agent.list_chains()

# Get optimization suggestions
optimized = agent.optimize_chain(chain_id)

# Get CVE database
cves = agent.get_cves()
```

## Chain Visualization
- Dependency graph: stage-to-stage requirements
- Success probability tree: overall chain reliability
- Detection risk heatmap: per-stage detection probability
- Alternative path matrix: fallback chains when primary fails
