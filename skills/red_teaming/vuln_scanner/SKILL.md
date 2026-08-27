---
name: vuln_scanner
description: >
  Multi-tool vulnerability scanner: nmap, nuclei, sqlmap, ffuf, OWASP ZAP, Burp Suite.
  Generates audit reports in NIST 800-115 and MITRE ATT&CK formats (PDF/HTML).
triggers:
  - vuln scan
  - vulnerability assess
  - nmap scan
  - nuclei
  - sqlmap
  - bug bounty
  - pentest
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-27"
  agent: agents/specialized/vuln_scanner.py
---

# Vulnerability Scanner

Multi-tool vulnerability scanner with comprehensive reporting.

## Purpose
Discover and classify vulnerabilities using industry-standard tools with structured reporting.

## Tools
- **nmap**: Network discovery and port scanning
- **nuclei**: Template-based vulnerability scanning
- **sqlmap**: SQL injection detection and exploitation
- **ffuf**: Web fuzzing for hidden endpoints
- **OWASP ZAP**: Automated web application scanner
- **Burp Suite**: Manual/automated web testing

## Usage
```python
from agents.specialized.vuln_scanner import VulnScanner

scanner = VulnScanner()
# Network scan
nmap_result = scanner.nmap_scan("192.168.1.1", scan_type="syn")
# Web scan
nuclei_result = scanner.nuclei_scan("https://target.com")
# Fuzzing
ffuf_result = scanner.ffuf_scan("https://target.com", wordlist="SecLists/...")
# Generate report
report = scanner.generate_report("192.168.1.1", fmt="html")
pdf_path = scanner.export_pdf(report)
```

## Report Formats
- **HTML**: Web-readable report with findings table
- **PDF**: Printable report (requires reportlab)
- **JSON**: Machine-readable findings

## Report Standards
- NIST 800-115 compliance
- MITRE ATT&CK mapping for each finding
- CVSS severity scoring
- Remediation recommendations
