---
name: compliance-check
description: Defensive compliance validation for Quantum C2. Use when checking compliance status against NIST 800-53, FedRAMP, SOC2, ISO 27001, or other frameworks. Triggers on "compliance check", "compliance validation", "NIST check", "FedRAMP audit", "SOC2 validation", "compliance report", "control check".
---

# Compliance Check (Defensive)

Validate compliance controls against public frameworks. All operations are read-only audits.

## Supported Frameworks

| Framework | Full Name | Scope |
|-----------|-----------|-------|
| NIST 800-53 | Security and Privacy Controls | Federal systems |
| FedRAMP | Federal Risk and Authorization Management | Cloud services |
| SOC 2 | Service Organization Control 2 | SaaS/Cloud |
| ISO 27001 | Information Security Management | Enterprise |
| NIST 800-172 | CMMC Level 3 | Defense industrial base |

## NIST 800-53 Control Check

```bash
python -c "
controls = {
    'AC-2': ('Account Management', 'Identify and select system access controls'),
    'AC-3': ('Access Enforcement', 'Enforce approved authorizations'),
    'AC-6': ('Least Privilege', 'Authorize access to system functions'),
    'AU-2': ('Audit Events', 'Identify audit events to be logged'),
    'AU-3': ('Content of Audit Records', 'Record who, what, when, where, outcome'),
    'CA-7': ('Continuous Monitoring', 'Develop monitoring strategy'),
    'CM-6': ('Configuration Settings', 'Establish configuration settings'),
    'IA-2': ('Identification and Authentication', 'Authenticate users'),
    'IR-6': ('Incident Reporting', 'Report incidents to designated officials'),
    'RA-5': ('Vulnerability Monitoring', 'Scan for vulnerabilities'),
    'SC-8': ('Transmission Confidentiality', 'Protect transmission confidentiality'),
    'SC-13': ('Cryptographic Protection', 'Implement FIPS-validated cryptography'),
    'SI-2': ('Flaw Remediation', 'Identify and remediate flaws'),
}
for cid, (name, desc) in controls.items():
    print(f'{cid}  {name}')
    print(f'    {desc}')
"
```

## Audit Workflow

1. **Scope** — Identify systems/components to audit
2. **Map** — Map existing controls to framework requirements
3. **Assess** — Check each control for implementation status
4. **Report** — Generate compliance report with gaps
5. **Remediate** — Prioritize and track gap closure

## Control Status Values

| Status | Meaning |
|--------|---------|
| Implemented | Control is fully deployed and operational |
| Partial | Control exists but not fully applied |
| Planned | Control is in design/pipeline |
| Not Applicable | Control does not apply to this system |
| Gap | Control is required but missing |

## Report Format

```markdown
## Compliance Report: [Framework]

**Date:** YYYY-MM-DD
**Scope:** [System/Component]
**Overall Score:** XX/100

### Controls Assessment
| Control | Name | Status | Evidence |
|---------|------|--------|----------|
| AC-2 | Account Management | Implemented | auth/router.py |
| AC-3 | Access Enforcement | Implemented | rbac/middleware.py |
| ... | ... | ... | ... |

### Gaps Found
1. [Gap description] — Priority: High
2. [Gap description] — Priority: Medium

### Recommendations
- [Remediation action]
```
