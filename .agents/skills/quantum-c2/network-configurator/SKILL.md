---
name: quantum-c2-network-configurator
description: >
  Quantum C2 network configuration skill. Use when the user asks about VPN, proxy, Tor, DNSCrypt, or network configuration. Triggers on: "VPN", "proxy", "Tor", "DNSCrypt", "network config", "VPN configuration", "proxy configuration", "Tor circuit", "DoH", "DoT", "multi-hop", "anonymity level".
---

# Quantum C2 Network Configurator

Configure VPN, proxy, Tor, DNSCrypt, and network anonymity settings.

## VPN Configuration

### OpenVPN
```bash
# List available servers
GET /api/network/vpn/openvpn/servers

# Configure OpenVPN
POST /api/network/vpn/openvpn/config
{
  "server": "ro-nl.nordvpn.com",
  "port": 1194,
  "protocol": "udp",
  "cipher": "AES-256-GCM",
  "auth": "SHA512",
  "tls_version": "1.3",
  "kill_switch": true,
  "dns_leak_protection": true
}
```

### WireGuard
```bash
# List available servers
GET /api/network/vpn/wireguard/servers

# Configure WireGuard
POST /api/network/vpn/wireguard/config
{
  "server": "wireguard.nordvpn.com",
  "port": 51820,
  "private_key": "<client_private_key>",
  "public_key": "<server_public_key>",
  "allowed_ips": ["0.0.0.0/0"],
  "persistent_keepalive": 25
}
```

### VPN Status
```bash
GET /api/network/vpn/status
```

**Response:**
```json
{
  "type": "wireguard",
  "connected": true,
  "server": "wireguard.nordvpn.com",
  "port": 51820,
  "local_ip": "10.8.0.2",
  "external_ip": "185.220.101.45",
  "country": "Romania",
  "uptime_seconds": 3600,
  "bytes_sent": 1048576,
  "bytes_recv": 5242880,
  "dns_leak": false
}
```

### VPN Rotation
```bash
POST /api/network/vpn/rotate
{
  "strategy": "random|country|latency",
  "country": "Sweden",
  "min_latency_ms": 100
}
```

## Proxy Configuration

### HTTP Proxy
```bash
# Configure HTTP proxy
POST /api/network/proxy/http
{
  "host": "proxy.example.com",
  "port": 8080,
  "username": "user",
  "password": "pass",
  "authentication": "basic",
  "timeout_seconds": 30
}
```

### SOCKS5 Proxy
```bash
# Configure SOCKS5 proxy
POST /api/network/proxy/socks5
{
  "host": "socks.example.com",
  "port": 1080,
  "username": "user",
  "password": "pass",
  "timeout_seconds": 30
}
```

### Proxy Chain
```bash
# Create proxy chain
POST /api/network/proxy/chain
{
  "name": "Multi-hop Chain",
  "hops": [
    {"type": "http", "host": "proxy1.example.com", "port": 8080},
    {"type": "socks5", "host": "proxy2.example.com", "port": 1080}
  ]
}
```

### Proxy Status
```bash
GET /api/network/proxy/status
```

## Tor Configuration

### Tor Control
```bash
# Connect to Tor
POST /api/network/tor/connect
{
  "control_port": 9051,
  "socks_port": 9050
}
```

### Tor Circuit Management
```bash
# Get current circuit
GET /api/network/tor/circuit

# Build new circuit
POST /api/network/tor/circuit/new
{
  "hops": 3,
  "entry_nodes": [],
  "middle_nodes": [],
  "exit_nodes": []
}

# Refresh circuit
POST /api/network/tor/circuit/refresh

# Clear circuits
POST /api/network/tor/circuit/clear
```

### Tor Bridges
```bash
# Configure obfs4 bridges
POST /api/network/tor/bridges/obfs4
{
  "address": "198.129.67.146",
  "port": 443,
  "fingerprint": "ABCD1234..."
}

# Configure meek-amazon fronts
POST /api/network/tor/bridges/meek-amazon
{
  "domain": "widgets.s3.amazonaws.com"
}
```

### Tor Status
```bash
GET /api/network/tor/status
```

**Response:**
```json
{
  "connected": true,
  "circuit_count": 2,
  "current_circuit": {
    "id": "circ-abc123",
    "hops": [
      {"fingerprint": "1234...5678", "nickname": "ABC", "country": "US"},
      {"fingerprint": "2345...6789", "nickname": "DEF", "country": "DE"},
      {"fingerprint": "3456...7890", "nickname": "GHI", "country": "NL"}
    ]
  },
  "bandwidth": {"read_bps": 50000, "write_bps": 30000},
  "uptime_seconds": 7200
}
```

## DNSCrypt Configuration

### DNSCrypt Setup
```bash
# List available resolvers
GET /api/network/dnscrypt/resolvers
```

**Response:**
```json
{
  "resolvers": [
    {"name": "dns.google", "provider": "Google", "ipv4": ["8.8.4.4"], "supports_dnssec": true, "no_log": true},
    {"name": "cloudflare-dns", "provider": "Cloudflare", "ipv4": ["1.1.1.1"], "supports_dnssec": true, "no_log": true},
    {"name": "quad9", "provider": "Quad9", "ipv4": ["9.9.9.9"], "supports_dnssec": true, "no_log": true, "blocks_malware": true}
  ]
}
```

### Configure DNSCrypt
```bash
POST /api/network/dnscrypt/config
{
  "provider_name": "dns.google",
  "server_addresses": ["8.8.4.4:443"],
  "ipv6_enabled": true,
  "require_dnssec": true,
  "require_nolog": true,
  "require_nofilter": false
}
```

### DNS-over-HTTPS
```bash
POST /api/network/doh/config
{
  "provider": "cloudflare",
  "url": "https://cloudflare-dns.com/dns-query",
  "fallback_url": "https://dns.google/resolve",
  "bootstrap_resolvers": ["1.1.1.1", "8.8.8.8"]
}
```

### DNS-over-TLS
```bash
POST /api/network/dot/config
{
  "server": "dns.google",
  "port": 853,
  "verify_certificate": true
}
```

### DNS Status
```bash
GET /api/network/dns/status
```

**Response:**
```json
{
  "method": "dnscrypt",
  "provider": "dns.google",
  "ipv4": ["8.8.4.4"],
  "ipv6": ["2001:4860:4860::8844"],
  "dnssec": true,
  "no_log": true,
  "response_time_ms": 25,
  "queries_today": 15420
}
```

## Network Stealth Configuration

### Stealth Mode Levels
```bash
GET /api/network/stealth/modes
```

| Mode | VPN | Tor | Proxy Chain | DNS | Description |
|------|-----|-----|-------------|-----|-------------|
| `open` | off | off | off | system | No anonymity |
| `vpn_only` | on | off | off | system | VPN only |
| `balanced` | on | off | on | doh | Balanced protection |
| `stealth` | on | on | off | doh | Stealth mode |
| `paranoid` | on | on | on | doh | Maximum protection |

### Apply Stealth Mode
```bash
POST /api/network/stealth/mode
{
  "mode": "stealth"
}
```

## Multi-Hop Configuration

### Create Multi-Hop
```bash
POST /api/network/multi-hop
{
  "name": "Triple Hop",
  "hops": [
    {"type": "vpn", "provider": "nordvpn", "country": "Sweden"},
    {"type": "tor", "hops": 3},
    {"type": "proxy", "host": "proxy.example.com", "port": 1080}
  ],
  "failover": true
}
```

### Multi-Hop Status
```bash
GET /api/network/multi-hop/status
```

## Integrated Configuration

### All-in-One Setup
```bash
POST /api/network/configure/all
{
  "vpn": {"enable": true, "provider": "nordvpn", "country": "Sweden"},
  "tor": {"enable": true, "hops": 3},
  "proxy": {"enable": false},
  "dns": {"method": "dnscrypt", "provider": "dns.google"},
  "stealth_mode": "paranoid"
}
```

### Get Full Network Status
```bash
GET /api/network/status
```

**Response:**
```json
{
  "vpn": {"active": true, "provider": "nordvpn", "country": "Sweden", "ip": "185.220.101.45"},
  "tor": {"active": true, "circuit": "circ-abc123", "hops": 3},
  "proxy": {"active": false},
  "dns": {"method": "dnscrypt", "provider": "dns.google", "dnssec": true},
  "external_ip": "185.220.101.45",
  "dns_leak": false,
  "webRTC_leak": false,
  "stealth_score": 95
}
```

## API Reference

### VPN
```
GET    /api/network/vpn/status
POST   /api/network/vpn/rotate
GET    /api/network/vpn/openvpn/servers
POST   /api/network/vpn/openvpn/config
GET    /api/network/vpn/wireguard/servers
POST   /api/network/vpn/wireguard/config
```

### Proxy
```
POST   /api/network/proxy/http
POST   /api/network/proxy/socks5
POST   /api/network/proxy/chain
GET    /api/network/proxy/status
```

### Tor
```
POST   /api/network/tor/connect
GET    /api/network/tor/circuit
POST   /api/network/tor/circuit/new
POST   /api/network/tor/circuit/refresh
POST   /api/network/tor/circuit/clear
POST   /api/network/tor/bridges/obfs4
POST   /api/network/tor/bridges/meek-amazon
GET    /api/network/tor/status
```

### DNSCrypt
```
GET    /api/network/dnscrypt/resolvers
POST   /api/network/dnscrypt/config
POST   /api/network/doh/config
POST   /api/network/dot/config
GET    /api/network/dns/status
```

### Stealth
```
GET    /api/network/stealth/modes
POST   /api/network/stealth/mode
POST   /api/network/multi-hop
GET    /api/network/multi-hop/status
POST   /api/network/configure/all
GET    /api/network/status
```

## Workflows

### Basic VPN Setup
```bash
# 1. List VPN servers
curl http://localhost:8000/api/network/vpn/wireguard/servers

# 2. Configure VPN
curl -X POST http://localhost:8000/api/network/vpn/wireguard/config \
  -H "Content-Type: application/json" \
  -d '{"server": "wireguard.nordvpn.com", "port": 51820}'

# 3. Verify connection
curl http://localhost:8000/api/network/vpn/status
```

### Full Anonymity Setup
```bash
# 1. Enable VPN
curl -X POST http://localhost:8000/api/network/configure/all \
  -H "Content-Type: application/json" \
  -d '{"vpn": {"enable": true, "country": "Sweden"}, "tor": {"enable": true}, "dns": {"method": "dnscrypt", "provider": "dns.google"}}'

# 2. Verify
curl http://localhost:8000/api/network/status
```

## Best Practices

1. **Use WireGuard** — Faster and more secure than OpenVPN
2. **Enable kill switch** — Prevent leaks on disconnect
3. **Use DoH/DoT** — Encrypt DNS queries
4. **Rotate regularly** — Change exit nodes periodically
5. **Test for leaks** — Regular DNS/WebRTC leak tests
6. **Choose no-log providers** — Privacy-focused VPNs
7. **Use multiple layers** — VPN + Tor for maximum anonymity
8. **Monitor status** — Regular status checks

## Troubleshooting

### VPN Not Connecting
```bash
# Check status
curl http://localhost:8000/api/network/vpn/status

# Try different server
curl -X POST http://localhost:8000/api/network/vpn/rotate \
  -H "Content-Type: application/json" \
  -d '{"strategy": "random"}'
```

### DNS Leak Detected
```bash
# Check DNS status
curl http://localhost:8000/api/network/dns/status

# Enable DNSCrypt
curl -X POST http://localhost:8000/api/network/dnscrypt/config \
  -H "Content-Type: application/json" \
  -d '{"provider_name": "dns.google"}'
```

### Tor Not Connecting
```bash
# Check Tor status
curl http://localhost:8000/api/network/tor/status

# Reconnect
curl -X POST http://localhost:8000/api/network/tor/connect
```
