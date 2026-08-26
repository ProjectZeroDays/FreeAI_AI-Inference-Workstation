---
name: compliance-validation
description: Validate compliance controls for Quantum C2 against NIST, SOC2, ISO, and other frameworks. Use when checking compliance status or generating compliance reports.
trigger_keywords: compliance, NIST, SOC2, ISO, audit, controls, regulatory, validation
---

## Purpose
Runs automated compliance checks against multiple regulatory frameworks and generates compliance reports with scores and gap analysis.

## When to Use
- Before regulatory audits
- When user asks about compliance status
- After infrastructure changes that might affect controls
- For continuous compliance monitoring

## Workflow
1. Run compliance scanner against NIST 800-53 framework
2. Check individual control status
3. Generate compliance score and report
4. Identify gaps and remediation items
5. Export report in required format

## Commands
```bash
# Run full compliance scan
python scripts/compliance_scanner.py

# Run compliance monitor
python scripts/compliance_monitor.py

# Export compliance report as JSON
python -c "from scripts.compliance_scanner import get_compliance_scanner; s = get_compliance_scanner(); print(s.export_report('json'))"

# Export as CSV
python -c "from scripts.compliance_scanner import get_compliance_scanner; s = get_compliance_scanner(); print(s.export_report('csv'))"

# Check scan history
python -c "from scripts.compliance_scanner import get_compliance_scanner; s = get_compliance_scanner(); print(s.get_scan_history(10))"
```

## Supported Frameworks
| Framework | Controls | Status |
|-----------|----------|--------|
| NIST 800-53 | 40+ | Compliant |
| NIST 800-171 | 110+ | Partial |
| FedRAMP | 325+ | Partial |
| PCI DSS 4.0 | 12 | Partial |
| HIPAA | 8 | Partial |
| SOC 2 | 6 | Partial |

## Compliance Score Calculation
```
Score = (Compliant × 100 + Partial × 50) / Total
Status: compliant (>=90%), partial (>=70%), non-compliant (<70%)
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

## Key Controls Mapped
- **AC-1 through AC-8**: Access Control
- **AU-1 through AU-12**: Audit and Accountability
- **CM-1 through CM-8**: Configuration Management
- **IA-1 through IA-5**: Identification and Authentication
- **SC-1 through SC-28**: System and Communications Protection
- **SI-1 through SI-5**: System and Information Integrity

## Notes
- Results stored in `.compliance_scans/` directory
- Historical scans available via `get_scan_history()`
- Partial status indicates controls implemented but not fully validated
- See `.learnings/FEATURE_REQUESTS.md` for planned compliance enhancements
