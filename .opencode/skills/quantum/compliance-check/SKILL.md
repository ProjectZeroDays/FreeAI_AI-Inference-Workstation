---
name: compliance-check
description: Run compliance checks and generate reports for Quantum C2. Use when checking compliance status, running assessments, or generating compliance reports.
trigger_keywords: compliance, compliance check, run compliance, compliance report, assessment, NIST, SOC2, ISO
---

# Compliance Check Skill

## Overview
This skill runs compliance checks against NIST 800-53 and other frameworks.

## Commands

### Run Full Compliance Scan
```bash
python scripts/compliance_scanner.py
```

### Check Compliance Status
```bash
python scripts/compliance_monitor.py
```

### Export Report
```bash
python -c "from scripts.compliance_scanner import get_compliance_scanner; s = get_compliance_scanner(); print(s.export_report('json'))"
```

## Supported Frameworks

| Framework | Controls | Status |
|-----------|----------|--------|
| NIST 800-53 | 40+ | ✅ Implemented |
| NIST 800-171 | 110+ | ⚠️ Partial |
| FedRAMP | 325+ | ⚠️ Partial |
| PCI DSS | 12 | ⚠️ Partial |
| HIPAA | 8 | ⚠️ Partial |
| SOC 2 | 6 | ⚠️ Partial |

## Compliance Score Calculation
```
Score = (Compliant × 100 + Partial × 50) / Total
```

## Output Format
```json
{
  "framework": "NIST_800_53",
  "score": 97.06,
  "status": "compliant",
  "controls_checked": 34,
  "compliant": 32,
  "partial": 2,
  "non_compliant": 0
}
```

## Commands
- `/compliance` - Run compliance check
- `/compliance-report` - Generate report
- `/control-status` - Check control status
- `/gap-analysis` - Find compliance gaps
