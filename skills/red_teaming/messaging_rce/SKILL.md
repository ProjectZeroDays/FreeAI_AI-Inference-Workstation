---
name: messaging_rce
description: >
  Messaging app RCE simulation: iMessage/WhatsApp/Signal/Telegram remote code execution,
  message parsing flaws, protocol-level exploits for defensive research.
triggers:
  - messaging rce
  - imessage exploit
  - whatsapp exploit
  - signal exploit
  - telegram exploit
  - message parsing
  - pegasus
  - forcedentry
  - blastpass
  - CVE-2019-3568
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-28"
  agent: agents/specialized/messaging_rce.py
---

# Messaging RCE Exploit Simulation Agent

Simulated messaging application remote code execution for defensive research and red team education.

## Purpose
Study and simulate RCE vulnerabilities in messaging platforms: iMessage, WhatsApp, Signal, and Telegram. Covers message parsing flaws, RTCP packet injection, image codec abuses, and protocol-level exploits. All outputs are simulated — no real exploit code or payloads.

## Capabilities
- **iMessage RCE**: Message parsing vulnerabilities, attachment processing flaws (simulated)
- **WhatsApp RCE**: VOIP stack buffer overflows, media processing exploits (simulated)
- **Signal/Telegram RCE**: Protocol-level parsing vulnerabilities (simulated)
- **RTCP Packet Injection**: Real-time transport control protocol abuse (simulated)
- **Image Codec Abuse**: GIF, WebP, JPEG parsing memory corruption (simulated)
- **Protocol Exploits**: Message format parsing, encryption bypass patterns (simulated)
- **CVE Reference**: Pegasus (CVE-2019-3568), FORCEDENTRY, BLASTPASS

## Usage
```python
from agents.specialized.messaging_rce import MessagingRCEAgent

agent = MessagingRCEAgent()
# Describe capabilities
desc = agent.describe()
# Simulate iMessage RCE
result = agent.simulate_imessage_rce("gif_parsing")
# Simulate WhatsApp RCE
wa_result = agent.simulate_whatsapp_rce("voip_stack")
# Simulate RTCP injection
rtcp = agent.simulate_rtcp_injection("192.168.1.10")
# Generate simulated payload
payload = agent.generate_payload("image_codec_abuse", format="gif")
# Get CVE references
cves = agent.get_cves()
```

## Simulation Disclaimer
All methods return `{"status": "simulated"}`. No real exploit code, payloads, or network requests are generated. This agent is for defensive research, vulnerability analysis, and red team planning education only.
