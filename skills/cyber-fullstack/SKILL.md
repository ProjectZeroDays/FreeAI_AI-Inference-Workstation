---
name: cyber-fullstack
description: Expert full stack development with autonomous AI red teaming, blue teaming, purple teaming, and NIST 800-172 CMMC Level 3 compliance. Use when building secure full stack applications, conducting security assessments, implementing compliance controls, performing offensive/defensive security operations, or creating CMMC-compliant systems. Triggers on "full stack", "security assessment", "red team", "blue team", "purple team", "CMMC", "NIST 800-172", "compliance", "secure development", "vulnerability assessment".
---

# Cyber Full Stack

Expert full stack development integrated with autonomous security operations and CMMC compliance.

## Core Domains

### 1. Full Stack Development
Read `references/fullstack.md` for:
- Clean Architecture patterns
- Frontend (React/Next.js, state management)
- Backend (Node.js, Python/FastAPI)
- Database (Repository pattern, Unit of Work)
- Testing strategy (Unit, Integration, E2E)

### 2. AI Red Teaming (Offensive)
Read `references/red-team.md` for:
- Autonomous attack lifecycle
- Reconnaissance (passive/active)
- Exploitation framework
- Web application attacks (SQLi, XSS, SSRF)
- API exploitation
- LLM/AI specific attacks
- Social engineering

### 3. AI Blue Teaming (Defensive)
Read `references/blue-team.md` for:
- Autonomous defense lifecycle
- SIEM integration and Sigma rules
- Threat detection (network/host)
- Incident response playbooks
- Vulnerability management
- Hardening standards (CIS benchmarks)
- Threat intelligence

### 4. AI Purple Teaming (Collaborative)
Read `references/purple-team.md` for:
- MITRE ATT&CK integration
- Collaborative testing framework
- Metrics and reporting
- Continuous improvement
- Detection rule optimization

### 5. NIST 800-172 CMMC L3 Compliance
Read `references/nist-cmmc.md` for:
- 14 CMMC control families
- 110+ security practices
- Implementation checklists
- Evidence collection requirements
- Assessment process

## Workflow Selection

| Task | Primary Reference | Secondary |
|------|-------------------|-----------|
| Build secure web app | fullstack.md | nist-cmmc.md |
| Conduct security assessment | red-team.md | purple-team.md |
| Implement defense monitoring | blue-team.md | nist-cmmc.md |
| Create compliance system | nist-cmmc.md | fullstack.md |
| Security testing | purple-team.md | red-team.md |
| Incident response | blue-team.md | nist-cmmc.md |

## Secure Development Lifecycle

```
Plan -> Design -> Build -> Test -> Deploy -> Monitor -> Respond
  |       |        |        |        |          |          |
  v       v        v        v        v          v          v
Risk    Threat   Secure   Pen    Hardened   SIEM/EDR   IR
Assess  Model    Code     Test   Config     Monitoring Playbook
```

### Phase 1: Planning
- [ ] Security requirements defined
- [ ] Compliance scope identified
- [ ] Risk assessment completed
- [ ] Threat model created

### Phase 2: Design
- [ ] Architecture review
- [ ] Data flow diagram
- [ ] Security controls selected
- [ ] CMMC controls mapped

### Phase 3: Build
- [ ] Secure coding practices
- [ ] Input validation
- [ ] Output encoding
- [ ] Parameterized queries

### Phase 4: Test
- [ ] SAST/DAST scanning
- [ ] Dependency scanning
- [ ] Penetration testing
- [ ] Purple team exercises

### Phase 5: Deploy
- [ ] Hardened configuration
- [ ] Security headers
- [ ] TLS configuration
- [ ] Access controls

### Phase 6: Monitor
- [ ] SIEM integration
- [ ] Log collection
- [ ] Alert rules
- [ ] Threat detection

### Phase 7: Respond
- [ ] IR playbooks
- [ ] Evidence collection
- [ ] Remediation tracking
- [ ] Lessons learned

## CMMC Level 3 Quick Reference

### Control Families
1. **AC** - Access Control
2. **AT** - Awareness and Training
3. **AU** - Audit and Accountability
4. **CM** - Configuration Management
5. **IA** - Identification and Authentication
6. **MA** - Maintenance
7. **MP** - Media Protection
8. **PS** - Personnel Security
9. **PE** - Physical Protection
10. **RA** - Risk Assessment
11. **CA** - Security Assessment
12. **SC** - System and Communications Protection
13. **SI** - System and Information Integrity
14. **PM** - Program Management

### Key Requirements
- **Encryption**: FIPS 140-2 validated modules
- **MFA**: Required for CUI access
- **Logging**: 1-year minimum retention
- **Incident Response**: Documented plan
- **Vulnerability Management**: 30-day critical SLA
- **Training**: Annual security awareness

## Output Formats

### Security Assessment Report
```markdown
# Security Assessment Report

## Executive Summary
[High-level findings]

## Scope
[Systems assessed]

## Methodology
[Assessment approach]

## Findings
### Critical
[Findings]
### High
[Findings]
### Medium
[Findings]
### Low
[Findings]

## Recommendations
[Remediation steps]

## Compliance Status
[CMMC control status]
```

### Purple Team Report
```markdown
# Purple Team Exercise Report

## Objectives
[What was tested]

## ATT&CK Coverage
[Techniques tested]

## Detection Results
[What was detected, what wasn't]

## Gaps Identified
[Detection gaps]

## Recommendations
[Improvement steps]

## Metrics
[MTTD, MTR, coverage %]
```

## Tool Recommendations

| Category | Tools |
|----------|-------|
| Full Stack | Next.js, FastAPI, PostgreSQL |
| Red Team | Burp Suite, Metasploit, custom |
| Blue Team | Wazuh, Zeek, Velociraptor |
| Purple Team | Atomic Red Team, CALDERA |
| Compliance | CIS-CAT, OpenVAS, Trivy |
| SIEM | ELK, Splunk, Microsoft Sentinel |
