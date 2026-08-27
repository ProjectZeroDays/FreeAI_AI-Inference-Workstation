# Red-Teaming Skills Catalog

## Overview

6 specialized red-teaming agents with corresponding skills, located in `skills/red_teaming/` and `agents/specialized/`.

## Skills

### 1. api_sniffer
- **Agent**: `agents/specialized/api_sniffer.py`
- **Purpose**: Reverse-engineer API transactions via CDP Network domain
- **Triggers**: `api sniff`, `api transaction`, `endpoint mapping`, `network intercept`
- **Output**: Transaction logs, API scheme mappings, auth detection

### 2. cookie_harvester
- **Agent**: `agents/specialized/cookie_harvester.py`
- **Purpose**: Cookie/session harvesting and crafting
- **Triggers**: `cookie harvest`, `session steal`, `cookie craft`, `netscape export`
- **Output**: Netscape format, JSON, Python dicts

### 3. payload_engine
- **Agent**: `agents/specialized/payload_engine.py`
- **Purpose**: Polymorphic encryption with runtime decoders
- **Triggers**: `payload generate`, `polymorphic encrypt`, `encoded shell`, `stub generator`
- **Formats**: PowerShell, Python, Bash, Go, Node.js, C, DLL, ELF, Mach-O
- **Encryption**: AES-256-GCM + XOR + base64

### 4. vuln_scanner
- **Agent**: `agents/specialized/vuln_scanner.py`
- **Purpose**: Multi-tool vulnerability scanning
- **Triggers**: `vuln scan`, `nmap scan`, `nuclei`, `sqlmap`, `bug bounty`
- **Tools**: nmap, nuclei, sqlmap, ffuf, OWASP ZAP
- **Reports**: NIST 800-115, MITRE ATT&CK, PDF/HTML

### 5. brute_force
- **Agent**: `agents/specialized/brute_force.py`
- **Purpose**: GPU-accelerated password cracking
- **Triggers**: `brute force`, `password crack`, `hash crack`, `hydra attack`
- **Targets**: NTLM SAM, bcrypt, SHA, ZIP/RAR/PDF/Office, SSH keys, JWT
- **Tools**: hashcat, hydra, rainbow tables, SecLists

### 6. exploitation
- **Agent**: `agents/specialized/exploitation.py`
- **Purpose**: Post-exploitation operations
- **Triggers**: `exploit`, `post-exploit`, `privilege escalation`, `lateral movement`
- **Capabilities**: Exploit, priv esc, persistence, lateral movement, keylogging, credential dump, data exfil
- **Integration**: Metasploit API

## Dashboard Pages

| Page | Route | Description |
|---|---|---|
| Loot | `/loot` | Harvested cookies, credentials, hashes |
| C2 | `/c2` | Connected hosts, listeners, shell |
| Browser V2 | `/browser-v2` | Army orchestrator status |

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/loot` | GET | Get all loot |
| `/api/loot/<tab>/<idx>` | DELETE | Delete loot item |
| `/api/loot/clear` | POST | Clear all loot |
| `/api/c2/events` | GET | Get C2 events |
| `/api/c2/scan` | POST | Trigger network scan |
| `/api/c2/shell` | POST | Execute shell command |
| `/api/browser/status` | GET | Browser engine status |
| `/army/close-all` | POST | Close all browsers |
