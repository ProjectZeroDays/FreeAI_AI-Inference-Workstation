---
name: quantum-c2-recon
description: >
  Quantum C2 reconnaissance and intelligence gathering skill. Use when the user needs to perform network scanning, domain reconnaissance, OSINT searches, vulnerability assessment, CVE lookups, or collect intelligence on targets. Triggers on: "scan network", "recon", "OSINT", "find vulnerabilities", "domain lookup", "WHOIS", "DNS records", "subdomain enumeration", "CVE search", "Shodan search", "reconnaissance", "target analysis", "port scan".
---

# Quantum C2 Reconnaissance Skill

Execute comprehensive reconnaissance operations against targets using Quantum C2's integrated tools.

## Reconnaissance Capabilities

### Network Scanning
- **nmap-based scanning**: Quick, full, stealth, vulnerability scans
- **ARP discovery**: Local network host discovery
- **Service enumeration**: Identify running services and versions
- **OS fingerprinting**: Detect target operating systems

### Domain Intelligence
- WHOIS/RDAP lookups
- DNS records (A, AAAA, MX, NS, TXT, CNAME, SOA, SRV)
- SSL certificate chain analysis
- CDN fingerprinting
- Reverse IP lookups
- Subdomain enumeration (crt.sh + brute force)
- Historical DNS records
- Technology stack detection

### OSINT Integration
- 13 integrated sources: Shodan, Censys, HIBP, VirusTotal, ThreatFox, AbuseIPDB, OTX, GreyNoise, URLScan, Hunter.io, RiskIQ
- Sentiment analysis feeds
- Exposure indexing
- Multi-source search (IP/domain/email/hash)

### Vulnerability Intelligence
- Real-time CVE database (NVD, CISA KEV, Exploit-DB, GHSA)
- Local caching with rate limiting
- Severity-based filtering
- MITRE ATT&CK mapping

## API Endpoints

### Network Scanning
```bash
# Quick scan
POST /api/network/
{"target": "192.168.1.0/24", "scan_type": "quick"}

# Full scan
POST /api/network/
{"target": "10.0.0.1", "scan_type": "full"}

# Stealth scan
POST /api/network/
{"target": "192.168.1.100", "scan_type": "stealth"}

# Vulnerability scan
POST /api/network/
{"target": "10.0.0.0/24", "scan_type": "vuln"}

# Get scan results
GET /api/network/scans/{scan_id}

# Local network info
GET /api/network/interfaces
GET /api/network/arp
GET /api/network/ports
```

### Domain Recon
```bash
# WHOIS lookup
POST /api/recon/domain/whois
{"domain": "example.com"}

# DNS records
POST /api/recon/domain/dns
{"domain": "example.com", "record_types": ["A", "MX", "NS", "TXT"]}

# SSL certificate
POST /api/recon/domain/ssl
{"domain": "example.com"}

# CDN fingerprint
POST /api/recon/domain/cdn
{"domain": "example.com"}

# Reverse IP
POST /api/recon/domain/reverse-ip
{"ip": "93.184.216.34"}

# Subdomain enumeration
POST /api/recon/domain/subdomains
{"domain": "example.com", "method": "crt_sh"}

# Historical DNS
POST /api/recon/domain/historical
{"domain": "example.com"}

# Tech stack detection
POST /api/recon/domain/techstack
{"url": "https://example.com"}
```

### OSINT
```bash
# Multi-source search
GET /api/osint/search?query=example.com&type=domain

# IP intelligence
GET /api/osint/ip?ip=93.184.216.34

# Email lookup
GET /api/osint/email?email=user@example.com

# Hash lookup
GET /api/osint/hash?hash=d41d8cd98f00b204e9800998ecf8427e

# Sentiment feed
GET /api/osint/sentiment

# Exposure index
GET /api/osint/exposure

# Keyword monitoring
POST /api/osint/keywords
{"keywords": ["company_name", "product_name"]}
```

### Vulnerabilities
```bash
# List vulnerabilities
GET /api/vulnerabilities/?target=192.168.1.100

# Get CVE details
GET /api/cve/{cve_id}

# Search CVEs
GET /api/cve/search?q=openssl&severity=critical

# Vulnerability scan results
GET /api/network/scans/{scan_id}/vulns
```

### Threat Intelligence
```bash
# Get threat intel
GET /api/threat-intel/

# Search feeds
GET /api/threat-intel/search?q=malware

# IOCs
GET /api/threat-intel/iocs

# APT tracking
GET /api/apt-hunting/
```

## Reconnaissance Workflows

### 1. Target Profile Creation
```bash
# Step 1: Domain reconnaissance
DOMAIN="target.com"
curl -X POST http://localhost:8000/api/recon/domain/whois -H "Content-Type: application/json" -d "{\"domain\":\"$DOMAIN\"}"
curl -X POST http://localhost:8000/api/recon/domain/dns -H "Content-Type: application/json" -d "{\"domain\":\"$DOMAIN\",\"record_types\":[\"A\",\"MX\",\"NS\",\"TXT\",\"CNAME\"]}"

# Step 2: Subdomain enumeration
curl -X POST http://localhost:8000/api/recon/domain/subdomains -H "Content-Type: application/json" -d "{\"domain\":\"$DOMAIN\",\"method\":\"crt_sh\"}"

# Step 3: Technology stack
curl -X POST http://localhost:8000/api/recon/domain/techstack -H "Content-Type: application/json" -d "{\"url\":\"https://$DOMAIN\"}"

# Step 4: OSINT search
curl "http://localhost:8000/api/osint/search?query=$DOMAIN&type=domain"
curl "http://localhost:8000/api/osint/search?query=admin@$DOMAIN&type=email"
```

### 2. Network Reconnaissance
```bash
# Step 1: Quick host discovery
curl -X POST http://localhost:8000/api/network/ -H "Content-Type: application/json" -d '{"target":"192.168.1.0/24","scan_type":"quick"}'

# Step 2: Full port scan on discovered hosts
curl -X POST http://localhost:8000/api/network/ -H "Content-Type: application/json" -d '{"target":"192.168.1.100","scan_type":"full"}'

# Step 3: Vulnerability scan
curl -X POST http://localhost:8000/api/network/ -H "Content-Type: application/json" -d '{"target":"192.168.1.0/24","scan_type":"vuln"}'

# Step 4: Get results
curl http://localhost:8000/api/network/scans/{scan_id}
```

### 3. Vulnerability Assessment
```bash
# Check CVE database
curl "http://localhost:8000/api/cve/search?q=openssh&severity=critical"

# Get exploit catalog
curl http://localhost:8000/api/exploits/

# Check specific CVE
curl http://localhost:8000/api/cve/CVE-2024-1234

# List vulnerabilities for target
curl "http://localhost:8000/api/vulnerabilities/?target=192.168.1.100&severity=critical"
```

### 4. OSINT Deep Dive
```bash
# Search multiple sources
curl "http://localhost:8000/api/osint/search?query=target.com&type=domain"
curl "http://localhost:8000/api/osint/search?query=employee@target.com&type=email"
curl "http://localhost:8000/api/osint/ip?ip=93.184.216.34"

# Check breach data
curl "http://localhost:8000/api/osint/search?query=user@target.com&type=email"

# Get threat intelligence
curl http://localhost:8000/api/threat-intel/
```

## Tool Reference

### Scan Types
| Type | Description | Use Case |
|------|-------------|----------|
| `quick` | Top 100 ports, basic OS detection | Fast discovery |
| `full` | All 65535 ports, detailed service info | Comprehensive recon |
| `stealth` | SYN scan with evasion | Evasion required |
| `vuln` | Vulnerability detection | Security assessment |

### DNS Record Types
- `A` — IPv4 address
- `AAAA` — IPv6 address
- `MX` — Mail exchange
- `NS` — Name server
- `TXT` — Text records (SPF, DKIM)
- `CNAME` — Canonical name
- `SOA` — Start of authority
- `SRV` — Service locator

### OSINT Sources
| Source | Capability |
|--------|------------|
| Shodan | Internet-wide device scanning |
| Censys | Certificate and host discovery |
| HIBP | Breach data lookup |
| VirusTotal | Malware analysis |
| ThreatFox | IOCs |
| AbuseIPDB | IP reputation |
| AlienVault OTX | Threat pulse |
| GreyNoise | Internet background noise |
| URLScan.io | Website analysis |
| Hunter.io | Email intelligence |
| RiskIQ | Passive DNS |

## Common Recon Patterns

### 1. Web Application Recon
```bash
# 1. WHOIS + DNS
curl -X POST http://localhost:8000/api/recon/domain/whois -d '{"domain":"target.com"}'
curl -X POST http://localhost:8000/api/recon/domain/dns -d '{"domain":"target.com"}'

# 2. Subdomains
curl -X POST http://localhost:8000/api/recon/domain/subdomains -d '{"domain":"target.com"}'

# 3. Tech stack
curl -X POST http://localhost:8000/api/recon/domain/techstack -d '{"url":"https://target.com"}'

# 4. SSL analysis
curl -X POST http://localhost:8000/api/recon/domain/ssl -d '{"domain":"target.com"}'

# 5. Web app scan
curl -X POST http://localhost:8000/api/webapp-scan/ -d '{"url":"https://target.com"}'
```

### 2. Infrastructure Recon
```bash
# 1. Network discovery
curl -X POST http://localhost:8000/api/network/ -d '{"target":"10.0.0.0/24","scan_type":"quick"}'

# 2. Service enumeration
curl -X POST http://localhost:8000/api/network/ -d '{"target":"10.0.0.1","scan_type":"full"}'

# 3. Vulnerability scan
curl -X POST http://localhost:8000/api/network/ -d '{"target":"10.0.0.0/24","scan_type":"vuln"}'

# 4. Host details
curl http://localhost:8000/api/hosts/
```

### 3. Human Intelligence Recon
```bash
# People OSINT
curl http://localhost:8000/api/people/search?name=John+Doe

# Email validation
curl http://localhost:8000/api/people/email-validate?email=user@target.com

# Social media
curl http://localhost:8000/api/people/social?query=target+company
```

## Output Formats

### Scan Results
```json
{
  "scan_id": "scan-abc123",
  "target": "192.168.1.100",
  "scan_type": "quick",
  "status": "completed",
  "hosts": [
    {
      "ip": "192.168.1.100",
      "hostname": "target.local",
      "status": "up",
      "ports": [
        {"port": 22, "service": "ssh", "version": "OpenSSH 8.9", "state": "open"}
      ],
      "os": "Linux 5.15",
      "vulnerabilities": []
    }
  ]
}
```

### Domain Recon Results
```json
{
  "domain": "example.com",
  "whois": {"registrar": "GoDaddy", "created": "1995-08-14", "expires": "2027-08-13"},
  "dns": {"A": ["93.184.216.34"], "MX": ["mail.example.com"]},
  "ssl": {"issuer": "Let's Encrypt", "valid_from": "2024-01-01", "valid_to": "2025-01-01"},
  "subdomains": ["www.example.com", "mail.example.com", "vpn.example.com"]
}
```

## Tips & Best Practices

1. **Start broad, narrow down**: Quick scan first, then full scan on interesting hosts
2. **Use stealth scans** when detection avoidance is required
3. **Correlate OSINT with technical recon** for comprehensive targeting
4. **Check CVE database** before selecting exploits
5. **Save scan results** for later analysis
6. **Use subdomain enumeration** to find attack surface
7. **Monitor threat intel feeds** for relevant IOCs

## Advanced Techniques

### Passive Reconnaissance
```bash
# OSINT without touching target
curl "http://localhost:8000/api/osint/search?query=target.com&type=domain"
curl "http://localhost:8000/api/threat-intel/?source=shodan&q=target.com"
```

### Active Reconnaissance
```bash
# Direct scanning
curl -X POST http://localhost:8000/api/network/ -d '{"target":"target.com","scan_type":"quick"}'
curl -X POST http://localhost:8000/api/recon/domain/dns -d '{"domain":"target.com"}'
```

### Mass Reconnaissance
```bash
# Scan multiple targets
for ip in $(seq 1 254); do
  curl -X POST http://localhost:8000/api/network/ -d "{\"target\":\"192.168.1.$ip\",\"scan_type\":\"quick\"}"
done
```
