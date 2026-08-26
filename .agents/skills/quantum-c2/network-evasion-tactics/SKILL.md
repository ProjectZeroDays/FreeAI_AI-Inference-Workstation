---
name: quantum-c2-network-evasion-tactics
description: >
  Quantum C2 network evasion tactics skill. Use when the user asks about evasion, anonymity, stealth operations, or counter-surveillance. Triggers on: "evasion", "anonymity", "stealth", "counter-surveillance", "opsec", "anti-detection", "vpn rotation", "proxy chain", "Tor circuit", "DNSCrypt", "port knocking", "JA3", "TLS fingerprint".
---

# Quantum C2 Network Evasion Tactics

Advanced network evasion and anonymity techniques for stealth operations.

## VPN Management

### VPN Rotation
```bash
# List available VPN providers
GET /api/evasion/vpn/providers
```

**Response:**
```json
{
  "providers": [
    {"id": "nordvpn", "name": "NordVPN", "locations": 60, "protocols": ["WireGuard", "OpenVPN"]},
    {"id": "mullvad", "name": "Mullvad", "locations": 45, "protocols": ["WireGuard", "OpenVPN"]},
    {"id": "ivacy", "name": "IVacy", "locations": 35, "protocols": ["WireGuard", "OpenVPN"]}
  ]
}
```

### Rotate VPN
```bash
POST /api/evasion/vpn/rotate
{
  "provider": "nordvpn",
  "country": "Romania",
  "protocol": "WireGuard"
}
```

### VPN Status
```bash
GET /api/evasion/vpn/status
```

**Response:**
```json
{
  "connected": true,
  "provider": "nordvpn",
  "location": "Bucharest, Romania",
  "ip": "185.220.101.45",
  "protocol": "WireGuard",
  "dns_leak": false,
  "kill_switch": true,
  "uptime_seconds": 3600,
  "rotation_count": 3
}
```

## Proxy Chain Management

### Create Proxy Chain
```bash
POST /api/evasion/proxy-chain
{
  "name": "OpSec Chain",
  "hops": [
    {"type": "http", "host": "proxy1.example.com", "port": 8080},
    {"type": "socks5", "host": "proxy2.example.com", "port": 1080},
    {"type": "tor", "port": 9050}
  ],
  "failover": true,
  "rotation_interval_seconds": 300
}
```

### Get Proxy Chain Status
```bash
GET /api/evasion/proxy-chain/status
```

### Rotate Proxy Chain
```bash
POST /api/evasion/proxy-chain/{chain_id}/rotate
{
  "skip_current": true
}
```

## Tor Circuit Management

### Tor Configuration
```bash
GET /api/evasion/tor/config
PUT /api/evasion/tor/config
{
  "SocksPort": "9050",
  "ControlPort": "9051",
  "RelayPort": "9030",
  "BridgeRelay": 0,
  "ExcludeNodes": [],
  "EntryGuards": ["guard1.torproject.org", "guard2.torproject.org"]
}
```

### Get Tor Circuit
```bash
GET /api/evasion/tor/circuit
```

**Response:**
```json
{
  "circuit_id": "circ-abc123",
  "status": "built",
  "hops": [
    {"nickname": "ABC", "fingerprint": "1234...5678", "country": "US"},
    {"nickname": "DEF", "fingerprint": "2345...6789", "country": "DE"},
    {"nickname": "GHI", "fingerprint": "3456...7890", "country": "NL"}
  ],
  "bandwidth": {"read_bps": 50000, "write_bps": 30000}
}
```

### Build New Circuit
```bash
POST /api/evasion/tor/circuit/new
{
  "strategy": "random",
  "hops": 3,
  "avoid_countries": ["US", "RU"],
  "prefer_countries": ["DE", "NL", "SE"]
}
```

### Clear Circuits
```bash
POST /api/evasion/tor/circuit/clear
{
  "graceful": true
}
```

## DNSCrypt Configuration

### DNSCrypt Setup
```bash
POST /api/evasion/dnscrypt/config
{
  "provider_name": "dns.google",
  "ipv6": true,
  "blocking_enabled": false,
  "requirements": {
    "dnssec": true,
    "no_log": true,
    "supported_records": ["A", "AAAA", "MX", "TXT"]
  }
}
```

### DNS-over-HTTPS
```bash
POST /api/evasion/doh/config
{
  "provider": "cloudflare",
  "url": "https://cloudflare-dns.com/dns-query",
  "fallback": "https://dns.google/resolve"
}
```

### DNS-over-TLS
```bash
POST /api/evasion/dot/config
{
  "server": "dns.google",
  "port": 853,
  "verify_certificate": true
}
```

### DNS Status
```bash
GET /api/evasion/dns/status
```

## Port Knocking

### Configure Knock Sequence
```bash
POST /api/evasion/port-knocking/sequence
{
  "name": "C2 Access",
  "sequence": [
    {"port": 21, "protocol": "tcp", "wait_ms": 200},
    {"port": 25, "protocol": "tcp", "wait_ms": 200},
    {"port": 110, "protocol": "tcp", "wait_ms": 500}
  ],
  "reveal_port": 443,
  "whitelist_ips": ["*"]
}
```

### Execute Knock
```bash
POST /api/evasion/port-knocking/knock
{
  "sequence_name": "C2 Access",
  "target": "192.168.1.100"
}
```

## Domain Fronting

### Domain Front Config
```bash
POST /api/evasion/domain-front/config
{
  "front_domain": "www.googleapis.com",
  "target_domain": "evil-c2.example.com",
  "path": "/api/c2",
  "headers": {
    "Host": "www.googleapis.com",
    "X-Forwarded-Host": "evil-c2.example.com"
  }
}
```

### Test Domain Front
```bash
POST /api/evasion/domain-front/test
{
  "front_domain": "www.googleapis.com",
  "target": "https://evil-c2.example.com/test"
}
```

## CDN Masking

### CDN Configuration
```bash
POST /api/evasion/cdn-mask/config
{
  "provider": "cloudflare",
  "front_domain": "cdn-front.example.com",
  "backend_domain": "c2.example.com",
  "purge_cache": true
}
```

### CDN Status
```bash
GET /api/evasion/cdn-mask/status
```

## TLS Fingerprint Randomization

### JA3/JA4 Modification
```bash
POST /api/evasion/tls-fingerprint/config
{
  "randomize": true,
  "profiles": ["chrome_120", "firefox_121", "safari_17"],
  "current_profile": "chrome_120"
}
```

### Get Current Fingerprint
```bash
GET /api/evasion/tls-fingerprint/current
```

**Response:**
```json
{
  "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-10,35-16-5-13-11-45-28-65281-10-11-35-16-6-21-23,0-23-23-6528-6528-51-21-5-10-11-35-16-0-21-22-256-257",
  "ja4": "t13d13010033c72302bba28626b34ae1",
  "profile": "chrome_120",
  "matches_target": true
}
```

## User-Agent Rotation

### UA Rotation Config
```bash
POST /api/evasion/user-agent/config
{
  "rotation": true,
  "interval_seconds": 300,
  "ua_list": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
  ]
}
```

### Current UA
```bash
GET /api/evasion/user-agent/current
```

## Timing Randomization

### Timing Config
```bash
POST /api/evasion/timing/config
{
  "jitter_percentage": 25,
  "min_delay_ms": 100,
  "max_delay_ms": 5000,
  "beacon_interval": 30,
  "beacon_jitter": 0.25
}
```

### Current Timing
```bash
GET /api/evasion/timing/status
```

## Protocol Obfuscation

### Obfuscation Config
```bash
POST /api/evasion/obfuscation/config
{
  "method": "scramble",
  "payload_format": "websocket",
  "encoding": "base64",
  "padding": true,
  "padding_size": 256
}
```

### Obfuscation Status
```bash
GET /api/evasion/obfuscation/status
```

## Metadata Stripping

### Strip Config
```bash
POST /api/evasion/metadata/strip-config
{
  "http_headers": ["User-Agent", "Referer", "X-Forwarded-For", "Cookie"],
  "dns_query": true,
  "packet_padding": true,
  "timestamps": true,
  "geo_data": true
}
```

### Strip Active Request
```bash
POST /api/evasion/metadata/strip-request
{
  "request_id": "req-abc123",
  "strip_all": true
}
```

## Network Stealth Modes

### Stealth Mode Levels
```bash
GET /api/evasion/stealth-modes
```

**Modes:**
| Mode | Description | Tor | VPN | Proxy Chain | JA3 | Timing |
|------|-------------|-----|-----|-------------|-----|--------|
| `stealth` | Standard stealth | yes | yes | no | random | jitter |
| `paranoid` | Maximum stealth | yes | yes | yes | random | high jitter |
| `balanced` | Balanced opsec | no | yes | no | fixed | low jitter |
| `covert` | Covert ops | yes | no | yes | random | variable |

### Switch Mode
```bash
POST /api/evasion/stealth-modes/switch
{
  "mode": "paranoid"
}
```

## Full Evasion Profile

### Get Profile
```bash
GET /api/evasion/profile
```

**Response:**
```json
{
  "vpn": {"active": true, "provider": "nordvpn", "location": "Romania"},
  "tor": {"circuit_active": true, "hops": 3},
  "proxy_chain": {"active": false},
  "dnscrypt": {"active": true, "provider": "dns.google"},
  "tls_fingerprint": {"profile": "chrome_120", "randomized": true},
  "user_agent": {"rotating": true, "current": "chrome_120"},
  "timing": {"jitter": 25, "beacon_interval": 30},
  "obfuscation": {"method": "scramble", "active": true},
  "metadata_stripping": {"active": true},
  "stealth_mode": "paranoid"
}
```

### Apply Full Profile
```bash
POST /api/evasion/profile/apply
{
  "stealth_mode": "paranoid",
  "vpn": {"enable": true, "provider": "nordvpn", "country": "Sweden"},
  "tor": {"enable": true, "hops": 3},
  "tls_fingerprint": {"randomize": true, "profile": "chrome_120"},
  "timing": {"jitter": 30, "beacon_interval": 45}
}
```

## API Reference

### VPN
```
GET    /api/evasion/vpn/providers
POST   /api/evasion/vpn/rotate
GET    /api/evasion/vpn/status
```

### Proxy Chain
```
GET    /api/evasion/proxy-chain
POST   /api/evasion/proxy-chain
GET    /api/evasion/proxy-chain/status
POST   /api/evasion/proxy-chain/{id}/rotate
```

### Tor
```
GET    /api/evasion/tor/config
PUT    /api/evasion/tor/config
GET    /api/evasion/tor/circuit
POST   /api/evasion/tor/circuit/new
POST   /api/evasion/tor/circuit/clear
```

### DNS
```
POST   /api/evasion/dnscrypt/config
POST   /api/evasion/doh/config
POST   /api/evasion/dot/config
GET    /api/evasion/dns/status
```

### TLS Fingerprint
```
POST   /api/evasion/tls-fingerprint/config
GET    /api/evasion/tls-fingerprint/current
```

### User Agent
```
POST   /api/evasion/user-agent/config
GET    /api/evasion/user-agent/current
```

### Timing
```
POST   /api/evasion/timing/config
GET    /api/evasion/timing/status
```

### Obfuscation
```
POST   /api/evasion/obfuscation/config
GET    /api/evasion/obfuscation/status
```

### Metadata
```
POST   /api/evasion/metadata/strip-config
POST   /api/evasion/metadata/strip-request
```

### Stealth
```
GET    /api/evasion/stealth-modes
POST   /api/evasion/stealth-modes/switch
GET    /api/evasion/profile
POST   /api/evasion/profile/apply
```

## Workflows

### Full OpSec Setup
```bash
# 1. Set stealth mode to paranoid
curl -X POST http://localhost:8000/api/evasion/stealth-modes/switch \
  -H "Content-Type: application/json" \
  -d '{"mode": "paranoid"}'

# 2. Configure VPN
curl -X POST http://localhost:8000/api/evasion/vpn/rotate \
  -H "Content-Type: application/json" \
  -d '{"provider": "mullvad", "country": "Sweden", "protocol": "WireGuard"}'

# 3. Configure Tor circuit
curl -X POST http://localhost:8000/api/evasion/tor/circuit/new \
  -H "Content-Type: application/json" \
  -d '{"hops": 3, "avoid_countries": ["US", "RU"]}'

# 4. Configure DNSCrypt
curl -X POST http://localhost:8000/api/evasion/dnscrypt/config \
  -H "Content-Type: application/json" \
  -d '{"provider_name": "dns.google", "blocking_enabled": false}'

# 5. Set TLS fingerprint
curl -X POST http://localhost:8000/api/evasion/tls-fingerprint/config \
  -H "Content-Type: application/json" \
  -d '{"randomize": true, "profiles": ["chrome_120", "firefox_121"]}'

# 6. Verify profile
curl http://localhost:8000/api/evasion/profile
```

### Quick Stealth Mode
```bash
# Apply pre-configured stealth profile
curl -X POST http://localhost:8000/api/evasion/profile/apply \
  -H "Content-Type: application/json" \
  -d '{"stealth_mode": "stealth"}'
```

## Best Practices

1. **Rotate regularly** — Change VPN/Tor circuits periodically
2. **Use multiple layers** — Combine VPN + Tor + proxy chain
3. **Randomize TLS fingerprints** — Match common browser profiles
4. **Add timing jitter** — Avoid pattern detection
5. **Strip metadata** — Remove identifying headers
6. **Use DoH/DoT** — Encrypt DNS queries
7. **Vary User-Agents** — Rotate browser identifiers
8. **Monitor for leaks** — Test for DNS/IP leaks

## Troubleshooting

### VPN Not Connecting
```bash
# Check status
curl http://localhost:8000/api/evasion/vpn/status

# Try different provider
curl -X POST http://localhost:8000/api/evasion/vpn/rotate \
  -H "Content-Type: application/json" \
  -d '{"provider": "mullvad", "country": "Sweden"}'
```

### Tor Circuit Failing
```bash
# Check circuit
curl http://localhost:8000/api/evasion/tor/circuit

# Build new circuit
curl -X POST http://localhost:8000/api/evasion/tor/circuit/new \
  -H "Content-Type: application/json" \
  -d '{"hops": 3}'
```

### DNS Leak Detected
```bash
# Check DNS status
curl http://localhost:8000/api/evasion/dns/status

# Enable DNSCrypt
curl -X POST http://localhost:8000/api/evasion/dnscrypt/config \
  -H "Content-Type: application/json" \
  -d '{"provider_name": "dns.google"}'
```
