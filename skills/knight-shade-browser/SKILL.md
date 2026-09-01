---
name: knight-shade-browser
description: >
  Knight-Shade browser automation framework for FreeAI. Invisible Playwright headless browser with 16-category stealth JS injection,
  3 fingerprint profiles (chrome_131_win, chrome_131_mac, firefox_134_win), CDP client, army orchestrator,
  anonymity stack (Tor/VPN/Shadowsocks), and reverse engineering pipeline. Use when building browser automation,
  stealth scraping, fingerprint switching, CDP commands, or army deployment. Triggers: "browser automation",
  "headless browser", "stealth scraping", "fingerprint", "CDP", "Knight-Shade", "browser engine", "playwright stealth".
triggers:
  - browser automation
  - headless browser
  - stealth scraping
  - fingerprint
  - CDP
  - Knight-Shade
  - browser engine
  - playwright stealth
  - army deploy
  - anonymity
metadata:
  version: "2.0"
  location: "ai-workstation/browser/"
  ports:
    browser_api: 8180
    browser_v2: 8181
---

# Knight-Shade Browser Automation Framework

## Architecture

```
browser/
  engine.py        — BrowserEngine (Playwright async), FingerprintProfile, CDPClient, ManifestXSystem, HealingEngine
  army.py          — ArmyAgent, FleetCoordinator, swarm orchestration
  anonymity.py     — AnonymityRouter (5-tier: none/tor/VPN/SS/DNSCrypt)
  intelligence.py  — IntelligencePipeline (Ghidra/Frida/MITM optional)
  api.py           — FastAPI REST on :8180
  mcp_tools.py     — MCP tools (browser_open, browser_extract, army_deploy, etc.)
  config/          — browser.json, army.json
```

## Quick Start

```python
import asyncio, sys
sys.path.insert(0, r'C:\Users\Project Zero\ai-workstation')
from browser.engine import BrowserEngine

async def main():
    eng = BrowserEngine()
    await eng.start(headless=True)           # invisible Chrome, headless="new"
    await eng.open('https://example.com')
    title = await eng.get_title()
    data = await eng.extract('h1')
    stealth = await eng.get_javascript('navigator.webdriver')  # None = hidden
    await eng.close()
    print(title, data, stealth)

asyncio.run(main())
```

## Profile Switching

```python
eng.set_profile('chrome_131_win')   # Windows Chrome 131
eng.set_profile('chrome_131_mac')   # macOS Chrome 131
eng.set_profile('firefox_134_win')  # Windows Firefox 134
await eng.start(headless=True)       # must restart after profile change
```

## Stealth Checklist

After any page load, verify:
- `navigator.webdriver` → `None`
- `window.__playwright` → `None`
- `window.cdc_*` → `undefined`
- `window.chrome` → may be present (legit Chrome)

## REST API (:8180)

```
GET  /health                    — service health
POST /browser/open  {"url":".."} — navigate
POST /browser/extract {"selector":".."} — CSS extract
GET  /browser/state             — current state
POST /browser/screenshot        — PNG base64
POST /browser/js    {"expression":".."} — JS eval
GET  /browser/manifestx         — Manifest-X capabilities
GET  /browser/anonymity         — anonymity mode
GET  /army/roster               — agent list
POST /army/deploy  {"count":N}  — spawn agents
```

## Gotchas

- **Playwright 1.62**: `headless=bool(headless)` (not `"new"` string — new headless is default)
- **JS comments in Python strings**: use `"/* ... */"` not `// ...`
- **Em dash `—` (U+2014)**: never use in Python source strings — edit tool mangles it
- **API endpoints must be async**: FastAPI runs in same event loop; `_run()` threadpool breaks Playwright connections
- **`browser/engine_fixed.py`**: temp scratch file — delete if it exists
- **`config/browser.json` and `config/army.json`**: required for defaults; auto-created on first use
- **Windows PowerShell**: no `&&` — use separate bash calls
