---
name: cookie_harvester
description: >
  Cookie sniffing, session harvesting, and cookie crafting.
  Extracts cookies from browser sessions, crafts custom cookies, and exports in Netscape/JSON formats.
triggers:
  - cookie harvest
  - session steal
  - cookie craft
  - netscape export
  - session harvesting
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-27"
  agent: agents/specialized/cookie_harvester.py
---

# Cookie Session Harvester

Harvests and crafts cookies/sessions via the browser engine for authentication testing and session management.

## Purpose
Extract cookies from browser sessions, craft custom cookies for authentication bypass testing, and export in standard formats.

## Usage
```python
from agents.specialized.cookie_harvester import CookieHarvester

harvester = CookieHarvester(browser_engine)
await harvester.harvest_cookies("https://target.com")
cookies = harvester.get_cookies()
# Craft a custom cookie
cookie = harvester.craft_cookie("session", "hijacked123", "target.com")
await harvester.set_cookies("https://target.com", [cookie])
# Export
print(harvester.export_netscape())
```

## Capabilities
- **Cookie Harvest**: Extract all cookies for a URL/domain
- **Cookie Set**: Inject custom cookies into browser session
- **Cookie Craft**: Build cookie dicts with proper attributes
- **Netscape Export**: Standard format for Burp/OWASP tools
- **JSON Export**: Machine-readable format

## Formats
- Netscape HTTP Cookie File
- JSON array
- Python dict
