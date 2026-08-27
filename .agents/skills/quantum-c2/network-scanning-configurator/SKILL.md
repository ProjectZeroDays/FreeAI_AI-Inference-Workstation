---
name: quantum-c2-network-scanning-configurator
description: >
  Quantum C2 network scanning configurator skill. Use when the user asks about network scanning, reconnaissance, or scan configuration. Triggers on: "network scan", "nmap", "masscan", "Shodan", "Censys", "scan configuration", "recon scan", "scan automation", "scan report".
---

# Quantum C2 Network Scanning Configurator

Configure and manage network scanning operations using nmap, masscan, Shodan, and Censys.

## Nmap Configuration

### Scan Templates
```bash
GET /api/scanning/nmap/templates
```

**Available Templates:**
| Template | Description | Ports | Timing |
|----------|-------------|-------|--------|
| `quick_scan` | Top 100 ports | 100 | T4 |
| `full_scan` | All 65535 ports | 65535 | T3 |
| `stealth_scan` | SYN scan | 1000 | T2 |
| `vuln_scan` | Vulnerability detection | 1000 | T3 |
| `aggressive` | Full + scripts | 65535 | T4 |
| `traceroute` | Route tracing | 0 | - |

### Nmap Scan Execution
```bash
POST /api/scanning/nmap/start
{
  "target": "192.168.1.0/24",
  "template": "quick_scan",
  "options": {
    "scan_type": "SYN",
    "timing": "T4",
    "os_detection": true,
    "version_detection": true,
    "scripts": ["vuln", "safe"]
  },
  "output_format": "xml"
}
```

### Get Scan Status
```bash
GET /api/scanning/nmap/status/{scan_id}
```

### Get Scan Results
```bash
GET /api/scanning/nmap/results/{scan_id}
GET /api/scanning/nmap/results/{scan_id}/hosts
GET /api/scanning/nmap/results/{scan_id}/open-ports
GET /api/scanning/nmap/results/{scan_id}/services
GET /api/scanning/nmap/results/{scan_id}/os-detection
GET /api/scanning/nmap/results/{scan_id}/vulnerabilities
```

**Response:**
```json
{
  "scan_id": "scan-abc123",
  "status": "completed",
  "target": "192.168.1.100",
  "started_at": "2024-01-15T10:00:00Z",
  "completed_at": "2024-01-15T10:05:00Z",
  "duration_seconds": 300,
  "hosts": [
    {
      "ip": "192.168.1.100",
      "hostname": "target.local",
      "status": "up",
      "os": {"name": "Linux 5.15", "accuracy": 95},
      "ports": [
        {"port": 22, "protocol": "tcp", "state": "open", "service": "ssh", "version": "OpenSSH 8.9"}
      ]
    }
  ]
}
```

## Masscan Configuration

### Masscan Scan
```bash
POST /api/scanning/masscan/start
{
  "target": "192.168.1.0/24",
  "ports": "1-65535",
  "rate": "10000",
  "syn": true,
  "output_format": "json"
}
```

### Masscan Status
```bash
GET /api/scanning/masscan/status/{scan_id}
GET /api/scanning/masscan/results/{scan_id}
```

## Shodan Integration

### Shodan Search
```bash
GET /api/scanning/shodan/search?q=target.com&type=domain
GET /api/scanning/shodan/search?q=192.168.1.0/24&type=ip
GET /api/scanning/shodan/search?q=product:apache&limit=100
```

### Shodan Host
```bash
GET /api/scanning/shodan/host/192.168.1.100
```

**Response:**
```json
{
  "ip": "192.168.1.100",
  "ports": [80, 443, 22],
  "vulns": ["CVE-2024-1234"],
  "os": "Linux 5.15",
  "data": ["HTTP/1.1 200 OK"],
  "tags": ["iot", "camera"],
  "country": "US",
  "org": "Example Corp"
}
```

### Shodan Alerts
```bash
GET /api/scanning/shodan/alerts
POST /api/scanning/shodan/alerts
{
  "name": "New CVE Alert",
  "query": "product:apache+cve:2024",
  "frequency": "daily"
}
```

## Censys Integration

### Censys Search
```bash
GET /api/scanning/censys/search?q=target.com
GET /api/scanning/censys/host/192.168.1.100
```

### Censys Certificate Search
```bash
GET /api/scanning/censys/certificates?q=example.com
```

## Scan Scheduling

### Schedule Scan
```bash
POST /api/scanning/schedule
{
  "name": "Weekly Network Scan",
  "type": "nmap",
  "template": "full_scan",
  "target": "192.168.1.0/24",
  "schedule": {
    "type": "cron",
    "cron": "0 2 * * 1"
  },
  "notifications": {
    "on_complete": true,
    "email": "admin@example.com"
  }
}
```

### Schedule List
```bash
GET /api/scanning/schedules
```

### Schedule Control
```bash
POST /api/scanning/schedules/{id}/enable
POST /api/scanning/schedules/{id}/disable
DELETE /api/scanning/schedules/{id}
```

## Scan Automation

### Automated Scan Chain
```bash
POST /api/scanning/automated/chain
{
  "name": "Full Recon Chain",
  "steps": [
    {"type": "masscan", "target": "192.168.1.0/24", "ports": "1-10000"},
    {"type": "nmap", "template": "vuln_scan", "target": "discovered_hosts"},
    {"type": "shodan", "search": "target:discovered_hosts"},
    {"type": "report", "format": "pdf"}
  ]
}
```

### Trigger Automated Chain
```bash
POST /api/scanning/automated/chain/{id}/execute
```

## Scan Aggregation

### Aggregate Results
```bash
POST /api/scanning/aggregate
{
  "scan_ids": ["scan-001", "scan-002", "scan-003"],
  "deduplicate": true,
  "output_format": "json"
}
```

### Comparison
```bash
POST /api/scanning/compare
{
  "scan_ids": ["scan-001", "scan-002"],
  "field": "open_ports"
}
```

## Report Generation

### Generate Report
```bash
POST /api/scanning/reports
{
  "scan_id": "scan-abc123",
  "format": "pdf",
  "sections": ["executive_summary", "vulnerabilities", "open_ports", "os_detection", "recommendations"]
}
```

### Report Templates
```bash
GET /api/scanning/reports/templates
```

**Templates:**
| Template | Use Case |
|----------|----------|
| `executive_summary` | Management overview |
| `technical_detailed` | Full technical details |
| `vulnerability_focus` | CVE-centric report |
| `compliance` | Regulatory compliance |

### Download Report
```bash
GET /api/scanning/reports/{report_id}/download?format=pdf
GET /api/scanning/reports/{report_id}/download?format=html
GET /api/scanning/reports/{report_id}/download?format=json
```

## Integration with 60+ Tools

### Cross-Tool Integration
```bash
# Integration with exploit catalog
GET /api/scanning/integrations/exploits?scan_id=scan-abc123

# Integration with vulnerability database
GET /api/scanning/integrations/cves?scan_id=scan-abc123

# Integration with threat intel
GET /api/scanning/integrations/threat-intel?ip=192.168.1.100
```

### Pipeline Integration
```bash
POST /api/scanning/pipeline/start
{
  "target": "192.168.1.0/24",
  "steps": [
    {"tool": "nmap", "template": "quick_scan"},
    {"tool": "vuln_scan", "source": "nmap_results"},
    {"tool": "exploit_match", "source": "vuln_results"},
    {"tool": "report", "source": "all_results"}
  ]
}
```

## API Reference

### Nmap
```
POST   /api/scanning/nmap/start
GET    /api/scanning/nmap/status/{scan_id}
GET    /api/scanning/nmap/results/{scan_id}
GET    /api/scanning/nmap/results/{scan_id}/hosts
GET    /api/scanning/nmap/results/{scan_id}/open-ports
GET    /api/scanning/nmap/results/{scan_id}/services
GET    /api/scanning/nmap/results/{scan_id}/vulnerabilities
GET    /api/scanning/nmap/templates
```

### Masscan
```
POST   /api/scanning/masscan/start
GET    /api/scanning/masscan/status/{scan_id}
GET    /api/scanning/masscan/results/{scan_id}
```

### Shodan
```
GET    /api/scanning/shodan/search
GET    /api/scanning/shodan/host/{ip}
GET    /api/scanning/shodan/alerts
POST   /api/scanning/shodan/alerts
```

### Censys
```
GET    /api/scanning/censys/search
GET    /api/scanning/censys/host/{ip}
GET    /api/scanning/censys/certificates
```

### Scheduling
```
POST   /api/scanning/schedule
GET    /api/scanning/schedules
POST   /api/scanning/schedules/{id}/enable
POST   /api/scanning/schedules/{id}/disable
DELETE /api/scanning/schedules/{id}
```

### Automation
```
POST   /api/scanning/automated/chain
POST   /api/scanning/automated/chain/{id}/execute
POST   /api/scanning/aggregate
POST   /api/scanning/compare
```

### Reports
```
POST   /api/scanning/reports
GET    /api/scanning/reports/templates
GET    /api/scanning/reports/{id}/download
```

### Integration
```
GET    /api/scanning/integrations/exploits
GET    /api/scanning/integrations/cves
GET    /api/scanning/integrations/threat-intel
POST   /api/scanning/pipeline/start
```

## Workflows

### Quick Network Scan
```bash
# 1. Start scan
curl -X POST http://localhost:8000/api/scanning/nmap/start \
  -H "Content-Type: application/json" \
  -d '{"target": "192.168.1.0/24", "template": "quick_scan"}'

# 2. Monitor status
curl http://localhost:8000/api/scanning/nmap/status/scan-001

# 3. Get results
curl http://localhost:8000/api/scanning/nmap/results/scan-001
```

### Full Vulnerability Scan
```bash
# 1. Mass scan
curl -X POST http://localhost:8000/api/scanning/masscan/start \
  -H "Content-Type: application/json" \
  -d '{"target": "10.0.0.0/24", "ports": "1-65535"}'

# 2. Detailed nmap
curl -X POST http://localhost:8000/api/scanning/nmap/start \
  -H "Content-Type: application/json" \
  -d '{"target": "10.0.0.1", "template": "vuln_scan"}'

# 3. Shodan enrichment
curl "http://localhost:8000/api/scanning/shodan/host/10.0.0.1"
```

### Scheduled Weekly Scan
```bash
# 1. Create schedule
curl -X POST http://localhost:8000/api/scanning/schedule \
  -H "Content-Type: application/json" \
  -d '{"name": "Weekly Scan", "type": "nmap", "template": "full_scan", "target": "10.0.0.0/24", "schedule": {"type": "cron", "cron": "0 2 * * 1"}}'

# 2. Enable
curl -X POST http://localhost:8000/api/scanning/schedules/sched-001/enable
```

## Best Practices

1. **Start with quick scans** — Then drill down on interesting hosts
2. **Use stealth scans** — Avoid detection when needed
3. **Enrich with OSINT** — Combine with Shodan/Censys
4. **Automate regular scans** — Schedule recurring assessments
5. **Generate reports** — Document findings
6. **Track changes** — Compare scans over time
7. **Integrate with tools** — Connect to exploit catalog
8. **Validate results** — Verify scan accuracy

## Troubleshooting

### Scan Stuck
```bash
# Check status
curl http://localhost:8000/api/scanning/nmap/status/scan-001

# Cancel scan
curl -X POST http://localhost:8000/api/scanning/nmap/cancel \
  -d '{"scan_id": "scan-001"}'
```

### Shodan API Error
```bash
# Check API status
curl http://localhost:8000/api/scanning/shodan/status

# Retry with different query
curl "http://localhost:8000/api/scanning/shodan/search?q=target.com"
```

### Masscan Too Slow
```bash
# Adjust rate
curl -X POST http://localhost:8000/api/scanning/masscan/start \
  -H "Content-Type: application/json" \
  -d '{"target": "10.0.0.0/24", "rate": "50000"}'
```
