---
name: zero-day-research
description: Pull latest zero-click and zero-day exploitation research and mitigation techniques from public sources. Gathers intelligence from security blogs, CVE databases, threat intel feeds, vendor advisories, and researcher publications. Use when researching zero-day vulnerabilities, zero-click exploits, surveillance spyware, exploitation techniques, or mitigation strategies. Triggers on "zero-day", "zero-click", "exploit research", "vulnerability research", "CVE", "threat intel", "surveillance", "spyware", "Pegasus", "exploitation techniques".
---

# Zero-Day Research

Autonomous intelligence gathering for zero-click and zero-day exploitation research from public sources.

## Workflow

### Phase 1: Source Collection
1. Read `references/sources.md` for available public sources
2. Query vulnerability databases (NVD, MITRE, CISA KEV)
3. Monitor security research blogs
4. Check threat intelligence feeds
5. Review social media and communities

### Phase 2: Analysis
1. Read `references/zero-click.md` for zero-click exploitation patterns
2. Read `references/zero-day.md` for zero-day vulnerability research
3. Categorize findings by:
   - Platform (iOS, Android, Windows, Linux)
   - Component (Browser, OS, Application, Firmware)
   - Technique (Memory corruption, Logic flaw, Injection)
   - Severity (Critical, High, Medium, Low)
   - Status (Active exploit, PoC, Research only)

### Phase 3: Documentation
1. Create structured findings report
2. Document exploitation techniques
3. Map to MITRE ATT&CK
4. Identify mitigation strategies
5. Track disclosure timeline

### Phase 4: Mitigation
1. Read `references/mitigation.md` for defense strategies
2. Document immediate workarounds
3. Identify long-term fixes
4. Create detection rules

## Source Categories

### Vendor Advisories
- Microsoft Security Update Guide
- Apple Security Releases
- Google Android Security Bulletins
- Adobe Security Bulletins
- Cisco Security Advisories

### Research Blogs
- Google Project Zero
- Citizen Lab
- Amnesty International
- Trail of Bits
- NCC Group

### Vulnerability Databases
- NIST NVD
- MITRE CVE
- CISA KEV
- Exploit-DB

### Threat Intel
- Abuse.ch (URLhaus, MalBazaar, ThreatFox)
- AlienVault OTX
- CIRCL feeds

## Output Formats

### Vulnerability Report
```markdown
# Zero-Day Research Report

## Executive Summary
[Key findings]

## New Vulnerabilities
### CVE-YYYY-XXXXX
- **Platform**: [Affected platform]
- **Component**: [Affected component]
- **CVSS**: [Score]
- **Exploitation**: [Active/PoC/Research]
- **Zero-Click**: [Yes/No]
- **Description**: [Brief description]
- **Mitigation**: [Available fixes]
- **References**: [Links]

## Trends & Analysis
[Emerging patterns]

## Recommendations
[Action items]
```

### Threat Intel Report
```json
{
  "report_id": "ZDR-YYYY-XXX",
  "date": "YYYY-MM-DD",
  "findings": [
    {
      "cve": "CVE-YYYY-XXXXX",
      "title": "[Vulnerability name]",
      "severity": "critical",
      "platform": "iOS",
      "zero_click": true,
      "exploitation": "active",
      "threat_actors": ["APTXX"],
      "mitigations": ["Workaround 1"],
      "references": ["URL1"]
    }
  ],
  "indicators": {
    "ips": [],
    "domains": [],
    "hashes": [],
    "urls": []
  }
}
```

## MITRE ATT&CK Mapping

| Technique | ID | Description |
|-----------|-----|-------------|
| Exploitation for Client Execution | T1203 | Exploitation of client-side vulnerabilities |
| Drive-by Compromise | T1189 | Web-based exploitation |
| Supply Chain Compromise | T1195 | Compromised software updates |
| Phishing for Information | T1598 | Reconnaissance via phishing |

## Research Checklist

### Daily Monitoring
- [ ] Check CISA KEV updates
- [ ] Review NVD new CVEs
- [ ] Monitor security news sites
- [ ] Check researcher blogs
- [ ] Review social media

### Weekly Analysis
- [ ] Summarize new vulnerabilities
- [ ] Analyze trends
- [ ] Update mitigation strategies
- [ ] Document findings

### Monthly Report
- [ ] Comprehensive threat report
- [ ] Emerging trends analysis
- [ ] Tool evaluation
- [ ] Knowledge base updates

## Tools

Read `references/tools.md` for:
- Fuzzing frameworks (AFL++, LibFuzzer, Honggfuzz)
- Static analysis (Ghidra, Radare2, Binary Ninja)
- Dynamic analysis (Valgrind, ASAN, TSAN)
- Exploitation development (pwntools, ROPgadget)
- Network analysis (Wireshark, tshark)
- Mobile analysis (Frida, Objection)

## Legal & Ethical Guidelines

1. **Authorization**: Only test systems you own or have written authorization to test
2. **Disclosure**: Follow responsible disclosure practices
3. **Documentation**: Maintain detailed research notes
4. **Sharing**: Share findings with the security community when appropriate
5. **Impact**: Consider potential harm from public disclosure

## Quick Reference Commands

```bash
# Check CISA KEV
curl -s https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json | jq '.vulnerabilities[] | select(.dateAdded > "2024-01-01")'

# Search NVD
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=zero+click"

# Monitor researcher feeds
# Set up RSS readers for:
# - Google Project Zero
# - Citizen Lab
# - Amnesty Tech
```
