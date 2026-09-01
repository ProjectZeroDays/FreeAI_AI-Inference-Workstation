---
name: threat-intel
description: Defensive threat intelligence operations for Quantum C2. Use when gathering, analyzing, or correlating threat data from public sources (CISA KEV, NVD, MITRE ATT&CK). Triggers on "threat intel", "threat intelligence", "CVE lookup", "KEV check", "MITRE mapping", "IOC analysis", "threat feed".
---

# Threat Intelligence (Defensive)

Gather and analyze threat data from public sources. All operations are read-only and defensive.

## CISA Known Exploited Vulnerabilities (KEV)

Fetch latest KEV entries:

```bash
curl -s "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json" | python -c "
import json,sys
data=json.load(sys.stdin)
for v in data['vulnerabilities'][:20]:
    print(f\"{v['cveID']}  {v['vendorProject']}  {v['product']}  {v['dateAdded']}\")
"
```

Filter by vendor/product:

```bash
curl -s "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json" | python -c "
import json,sys
data=json.load(sys.stdin)
keyword=sys.argv[1] if len(sys.argv)>1 else ''
for v in data['vulnerabilities']:
    if keyword.lower() in (v['vendorProject']+v['product']).lower():
        print(f\"{v['cveID']}  {v['vendorProject']}  {v['product']}  {v['dateAdded']}  {v.get('shortDescription','')[:80]}\")
" "$1"
```

## NVD CVE Lookup

Query NVD API for CVE details:

```bash
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=$CVE_ID" | python -c "
import json,sys
data=json.load(sys.stdin)
v=data['vulnerabilities'][0]['cve']
print(f\"ID: {v['id']}\")
print(f\"Published: {v['published']}\")
print(f\"Description: {v['descriptions'][0]['value'][:200]}\")
for m in v.get('metrics',{}).get('cvssMetricV31',[]):
    s=m['cvssData']
    print(f\"CVSS: {s['baseScore']} ({s['baseSeverity']}) Vector: {s['vectorString']}\")
"
```

## MITRE ATT&CK Mapping

Map findings to ATT&CK techniques:

```bash
curl -s "https://attack.mitre.org/enterprise/enterprise.json" | python -c "
import json,sys
data=json.load(sys.stdin)
for t in data['objects']:
    if t['type']=='attack-pattern':
        print(f\"{t['external_references'][0]['external_id']}  {t['name']}\")
" | head -30
```

## Workflow

1. **Identify** — User reports suspicious IOC or CVE
2. **Lookup** — Query CISA KEV, NVD, MITRE for context
3. **Correlate** — Check if vulnerability affects project components
4. **Report** — Generate findings with CVSS scores and MITRE mappings
5. **Recommend** — Suggest patches, mitigations, or detection rules

## Output Format

```
## Threat Intel Report: [CVE-ID]

**Source:** [CISA KEV / NVD / MITRE]
**Severity:** [Critical/High/Medium/Low] (CVSS: X.X)
**Affected:** [component/version]

### Summary
[Description]

### MITRE ATT&CK
- Technique: T#### — [name]
- Tactic: [tactic name]

### Mitigation
[Patch/update/detection recommendation]
```
