---
name: quantum-c2-recon
description: >
  Reconnaissance operations for Quantum C2. Use when the user needs to scan networks, perform domain intelligence, run OSINT searches, check vulnerabilities, or collect target information. Triggers on: "scan network", "recon", "OSINT", "find vulnerabilities", "domain lookup", "WHOIS", "DNS scan", "subdomain enumeration", "target analysis", "port scan", "CVE search", "network discovery", "reconnaissance".
---

# Quantum C2 Reconnaissance Skill

Execute comprehensive reconnaissance operations against targets.

## Network Scanning

### Quick Scan (Top 100 ports)
```bash
curl -X POST http://localhost:8000/api/network/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.0/24","scan_type":"quick"}'
```

### Full Scan (All 65535 ports)
```bash
curl -X POST http://localhost:8000/api/network/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.100","scan_type":"full"}'
```

### Stealth Scan (SYN scan with evasion)
```bash
curl -X POST http://localhost:8000/api/network/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.0/24","scan_type":"stealth"}'
```

### Vulnerability Scan
```bash
curl -X POST http://localhost:8000/api/network/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"10.0.0.0/24","scan_type":"vuln"}'
```

### Get Scan Results
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/network/scans/{scan_id}
```

### Local Network Info
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/network/interfaces
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/network/arp
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/network/ports
```

## Domain Reconnaissance

### WHOIS Lookup
```bash
curl -X POST http://localhost:8000/api/recon/domain/whois \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"target.com"}'
```

### DNS Records
```bash
curl -X POST http://localhost:8000/api/recon/domain/dns \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"target.com","record_types":["A","MX","NS","TXT","CNAME"]}'
```

### SSL Certificate Analysis
```bash
curl -X POST http://localhost:8000/api/recon/domain/ssl \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"target.com"}'
```

### CDN Fingerprinting
```bash
curl -X POST http://localhost:8000/api/recon/domain/cdn \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"target.com"}'
```

### Reverse IP Lookup
```bash
curl -X POST http://localhost:8000/api/recon/domain/reverse-ip \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ip":"93.184.216.34"}'
```

### Subdomain Enumeration
```bash
curl -X POST http://localhost:8000/api/recon/domain/subdomains \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"target.com","method":"crt_sh"}'
```

### Technology Stack Detection
```bash
curl -X POST http://localhost:8000/api/recon/domain/techstack \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://target.com"}'
```

## OSINT Operations

### Multi-Source Search
```bash
# Domain search
curl -H "Authorization: Bearer $C2_TOKEN" \
  "http://localhost:8000/api/osint/search?query=target.com&type=domain"

# IP intelligence
curl -H "Authorization: Bearer $C2_TOKEN" \
  "http://localhost:8000/api/osint/ip?ip=93.184.216.34"

# Email lookup
curl -H "Authorization: Bearer $C2_TOKEN" \
  "http://localhost:8000/api/osint/email?email=user@target.com"

# Hash lookup
curl -H "Authorization: Bearer $C2_TOKEN" \
  "http://localhost:8000/api/osint/hash?hash=d41d8cd98f00b204e9800998ecf8427e"
```

### Exposure Index
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/osint/exposure
```

### Keyword Monitoring
```bash
curl -X POST http://localhost:8000/api/osint/keywords \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords":["company_name","product_name","executive_name"]}'
```

## Vulnerability Intelligence

### List Vulnerabilities
```bash
curl -H "Authorization: Bearer $C2_TOKEN" \
  "http://localhost:8000/api/vulnerabilities/?target=192.168.1.100&severity=critical"
```

### Search CVE Database
```bash
curl -H "Authorization: Bearer $C2_TOKEN" \
  "http://localhost:8000/api/cve/search?q=openssl&severity=critical"
```

### Get CVE Details
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/cve/CVE-2024-1234
```

### CVE Feed
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/cve/feed
```

## Threat Intelligence

### Get Threat Intel
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/threat-intel/
```

### Search Feeds
```bash
curl -X POST http://localhost:8000/api/threat-intel/search \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"malware","sources":["shodan","virustotal"]}'
```

### Trigger Full Sync
```bash
curl -X POST http://localhost:8000/api/threat-intel/sync \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Common Recon Patterns

### 1. Full Target Profile
```bash
DOMAIN="target.com"
IP="93.184.216.34"

# WHOIS + DNS
curl -s -X POST http://localhost:8000/api/recon/domain/whois -H "Authorization: Bearer $C2_TOKEN" -H "Content-Type: application/json" -d "{\"domain\":\"$DOMAIN\"}"
curl -s -X POST http://localhost:8000/api/recon/domain/dns -H "Authorization: Bearer $C2_TOKEN" -H "Content-Type: application/json" -d "{\"domain\":\"$DOMAIN\"}"

# Subdomains
curl -s -X POST http://localhost:8000/api/recon/domain/subdomains -H "Authorization: Bearer $C2_TOKEN" -H "Content-Type: application/json" -d "{\"domain\":\"$DOMAIN\"}"

# Tech stack
curl -s -X POST http://localhost:8000/api/recon/domain/techstack -H "Authorization: Bearer $C2_TOKEN" -H "Content-Type: application/json" -d "{\"url\":\"https://$DOMAIN\"}"

# OSINT
curl -s -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/osint/search?query=$DOMAIN&type=domain"
curl -s -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/osint/ip?ip=$IP"

# Network scan
curl -s -X POST http://localhost:8000/api/network/ -H "Authorization: Bearer $C2_TOKEN" -H "Content-Type: application/json" -d "{\"target\":\"$IP/32\",\"scan_type\":\"quick\"}"
```

### 2. Passive Recon (No Direct Contact)
```bash
# OSINT only - no direct scanning
curl -s -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/osint/search?query=target.com&type=domain"
curl -s -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/osint/search?query=admin@target.com&type=email"
curl -s -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/threat-intel/?source=shodan&q=target.com"
```

### 3. Mass Reconnaissance
```bash
# Scan range
for ip in $(seq 1 254); do
  curl -s -X POST http://localhost:8000/api/network/ \
    -H "Authorization: Bearer $C2_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"target\":\"192.168.1.$ip\",\"scan_type\":\"quick\"}" &
done
wait
```

## Reconnaissance Checklist

| Phase | Action | Endpoint |
|-------|--------|----------|
| 1 | Domain WHOIS | POST /api/recon/domain/whois |
| 2 | DNS Records | POST /api/recon/domain/dns |
| 3 | Subdomain Enum | POST /api/recon/domain/subdomains |
| 4 | SSL Analysis | POST /api/recon/domain/ssl |
| 5 | Tech Stack | POST /api/recon/domain/techstack |
| 6 | Network Scan | POST /api/network/ |
| 7 | Vuln Check | GET /api/vulnerabilities/ |
| 8 | OSINT Search | GET /api/osint/search |
| 9 | Threat Intel | GET /api/threat-intel/ |
| 10 | CVE Lookup | GET /api/cve/search |
