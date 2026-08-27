# Knight-Shade / UniverSight — Browser Automation Framework

## What It Is

A unified headless browser automation system providing:
- **Full CDP access** — Chrome DevTools Protocol via websockets
- **Manifest-X extensions** — god-tier browser extension privileges
- **Anonymity stack** — Tor/VPN/Shadowsocks/DNSCrypt routing (default: off)
- **Self-healing** — automatic retry with adaptive selectors
- **AI-native** — MCP tools + REST API for agent integration
- **Stealth** — fingerprint randomization, webdriver masking, CSP bypass

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  BrowserEngine                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Playwright│  │ CDP/WS   │  │ Anonymity Router │  │
│  │ (core)    │  │ (40+ cmd)│  │ (Tor/VPN/SS/DNS) │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │             │                  │            │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────────▼─────────┐  │
│  │ Stealth  │  │Manifest-X│  │  Self-Healing     │  │
│  │ (fp rand)│  │(ext sys) │  │  (retry/adapt)    │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
         │                         │
    REST API (:8180)         MCP Tools
```

## Quick Start

```python
from browser.engine import BrowserEngine
import asyncio

async def main():
    engine = BrowserEngine()
    await engine.start(headless=True)

    # Navigate
    await engine.open("https://example.com")
    print(f"Title: {await engine.get_title()}")

    # Extract data
    links = await engine.extract('a[href]', 'href')
    print(f"Found {len(links)} links")

    # Screenshot
    await engine.screenshot("page.png", full_page=True)

    # Execute JS
    ua = await engine.get_javascript("navigator.userAgent")
    print(f"UA: {ua}")

    await engine.close()

asyncio.run(main())
```

## REST API (:8180)

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Service health |
| `/browser/open` | POST | Navigate to URL |
| `/browser/close` | POST | Close browser |
| `/browser/click` | POST | Click element |
| `/browser/fill` | POST | Fill form field |
| `/browser/extract` | POST | Extract text/HTML |
| `/browser/screenshot` | POST | Take screenshot |
| `/browser/source` | POST | Get HTML source |
| `/browser/js` | POST | Execute JavaScript |
| `/browser/cookies` | POST | Manage cookies |
| `/browser/cdp` | POST | Raw CDP command |
| `/browser/state` | GET | Browser state |
| `/browser/healing` | GET | Healing statistics |
| `/browser/manifestx` | GET | Manifest-X capabilities |
| `/browser/extensions` | GET | Loaded extensions |

## Configuration

Edit `config/browser.json`:

```json
{
  "stealth": {
    "enable": true,
    "randomize_fingerprint": true,
    "mask_webdriver": true,
    "fake_headers": true,
    "override_navigator": true,
    "canvas_noise": true,
    "webgl_noise": true
  },
  "anonymity": {
    "mode": "none",
    "tor_socks_port": 9150
  },
  "healing": {
    "max_retries": 5,
    "retry_backoff": 1.5,
    "adaptive_selectors": true,
    "screenshot_on_fail": true
  },
  "manifestx": {
    "enabled": true,
    "god_mode": true
  }
}
```

## MCP Integration

Register browser tools with any MCP server:

```python
from browser.mcp_tools import register_mcp_tools
from mcp.server import Server

server = Server("knight-shade")
register_mcp_tools(server)
```

Available tools: `browser_open`, `browser_click`, `browser_fill`, `browser_extract`,
`browser_screenshot`, `browser_get_source`, `browser_js`, `browser_state`,
`browser_cookies`, `browser_cdp`, `browser_healing_stats`, `browser_manifestx_info`

## Anonymity Modes

| Mode | Description |
|---|---|
| `none` | Direct connection (default) |
| `tor` | Route through Tor network (SOCKS5) |
| `vpn` | Route through WireGuard VPN interface |
| `shadowsocks` | Route through Shadowsocks proxy |
| `mix` | Full stack: DNSCrypt → VPN → Shadowsocks → Tor |

## Healing System

Automatic recovery from common failures:
- Selector not found → tries alternative selectors
- Element not visible → scrolls into view
- Timeout → exponential backoff retry
- Page crash → takes screenshot, retries
- Max retries reached → raises error with context

## File Structure

```
browser/
  engine.py          # Core BrowserEngine class
  cdp/
    client.py        # CDP websocket client
  stealth.py         # Fingerprint randomization
  anonymity/
    router.py        # Anonymity stack router
  manifestx/
    extensions.py    # Extension system
  healing.py         # Self-healing engine
  observability.py   # DOM mirror
  mcp_tools.py       # MCP tool registration
  api.py             # REST API server
  __init__.py
```

## Dependencies

- Python 3.10+
- playwright (with browsers installed: `playwright install chromium`)
- curl_cffi
- websockets
- fastapi + uvicorn (for API server)

## License

MIT — part of FreeAI Workstation
