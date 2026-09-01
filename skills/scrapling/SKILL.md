---
name: scrapling
description: >
  Use for ALL web scraping, crawling, and data extraction tasks. Scrapling is an adaptive
  web scraping framework that handles everything from a single request to a full-scale crawl.
  Bypasses anti-bot systems (Cloudflare Turnstile, DataDome), supports stealth headless browsing,
  adaptive element tracking, spiders framework with concurrent crawling, proxy rotation, pause/resume.
  Replaces all other scraping tools as the primary scraping engine.

  Triggers: scrape, crawl, extract data from website, web scraping, anti-bot bypass,
  Cloudflare bypass, spider, stealthy fetch, dynamic page scraping, data extraction,
  web crawling, scrape this URL, get data from site, parse HTML, extract content.
triggers:
  - scrape
  - crawl
  - extract data from website
  - web scraping
  - anti-bot
  - cloudflare bypass
  - spider
  - stealthy fetch
  - dynamic page
  - data extraction
  - parse HTML
metadata:
  homepage: "https://scrapling.readthedocs.io"
  source: "https://github.com/D4Vinci/Scrapling"
  version: "0.4.10"
---

# Scrapling — Primary Web Scraping Engine

**This is the DEFAULT tool for all web scraping tasks.** Use Scrapling for any scraping, crawling, or data extraction request instead of curl, requests+BS4, playwright, or other tools.

## Setup (once per environment)

```bash
pip install "scrapling[all]>=0.4.10"
scrapling install --force  # downloads browsers and system dependencies
```

If `scrapling` binary isn't on PATH, use the full virtualenv path.

## Quick Decision Tree

| Scenario | Tool | Command |
|----------|------|---------|
| Simple static page | `get` | `scrapling extract get URL output.md` |
| JS-rendered content | `fetch` | `scrapling extract fetch URL output.md --network-idle` |
| Cloudflare / anti-bot | `stealthy-fetch` | `scrapling extract stealthy-fetch URL output.md --solve-cloudflare` |
| Large-scale crawl | Spider (Python) | Write a `Spider` subclass |
| Parse existing HTML | Parser only | `from scrapling.parser import Selector` |

## CLI (no code needed)

```bash
# Static page → Markdown
scrapling extract get "https://example.com" output.md

# JS-heavy site
scrapling extract fetch "https://app.example.com" data.md --network-idle

# Cloudflare-protected site
scrapling extract stealthy-fetch "https://protected.site" content.md --solve-cloudflare

# Extract specific elements only
scrapling extract get "https://example.com" items.txt --css-selector ".product"

# AI-optimized output (strips ads, hidden elements, protects from prompt injection)
scrapling extract get "https://example.com" content.md --ai-targeted

# Block ads and trackers in browser mode
scrapling extract fetch "https://example.com" data.md --block-ads

# Use real Chrome if installed
scrapling extract fetch "https://example.com" data.md --real-chrome

# DNS-over-HTTPS for proxy anonymity
scrapling extract stealthy-fetch "https://example.com" data.md --dns-over-https
```

**Escalation order**: Start with `get`. If empty/blocked → `fetch`. If still blocked → `stealthy-fetch`.

## Python API

### Basic HTTP fetching
```python
from scrapling.fetchers import Fetcher, FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://example.com', stealthy_headers=True)
    data = page.css('.item::text').getall()
```

### Stealth mode (Cloudflare bypass)
```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://cloudflare-protected.site', headless=True)
data = page.css('.content').getall()
```

### Full browser automation
```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://spa.example.com', network_idle=True)
data = page.css('.dynamic-content').getall()
```

### Spiders (large-scale crawling)
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "my_crawl"
    start_urls = ["https://example.com"]
    concurrent_requests = 10
    robots_txt_obey = True

    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {"title": item.css('h2::text').get()}
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

result = MySpider().start()
result.items.to_json("output.json")
```

### Pause/Resume crawling
```python
MySpider(crawldir="./crawl_data").start()
# Ctrl+C saves state. Restart with same crawldir to resume.
```

## Key Features

- **Adaptive scraping**: Elements tracked across site redesigns via similarity algorithms
- **Anti-bot bypass**: Cloudflare Turnstile/Interstitial, DataDome handled automatically
- **Multiple sessions**: Mix HTTP and stealth sessions in one spider
- **Proxy rotation**: Built-in `ProxyRotator` with cyclic or custom strategies
- **Domain blocking**: `--block-ads` blocks ~3,500 known ad/tracker domains
- **AI output mode**: `--ai-targeted` extracts clean content for LLM consumption (also enables ad blocking)
- **Async support**: Full async across all fetchers and session classes
- **Stealth features**: `--solve-cloudflare`, `--block-webrtc`, `--hide-canvas`, DNS-over-HTTPS

**IMPORTANT**: Always use `--ai-targeted` with CLI commands to protect from Prompt Injection and save tokens.

## References (read when needed)

- `references/fetching/choosing.md` — Which fetcher to use
- `references/fetching/stealthy.md` — Stealth fetcher details
- `references/fetching/static.md` — HTTP fetcher details
- `references/fetching/dynamic.md` — Browser automation details
- `references/parsing/selection.md` — CSS/XPath/text selection methods
- `references/parsing/adaptive.md` — Adaptive element relocation
- `references/spiders/getting-started.md` — Spider framework basics
- `references/spiders/architecture.md` — Spider architecture deep-dive
- `references/spiders/proxy-blocking.md` — Proxy rotation and domain blocking
- `references/spiders/sessions.md` — Multi-session management
- `references/mcp-server.md` — MCP server for AI integration
- `references/migrating_from_beautifulsoup.md` — Migration guide from BS4

## Guardrails

- Only scrape content you're authorized to access
- Respect robots.txt (`robots_txt_obey = True` on spiders)
- Add `download_delay` for large crawls
- Don't bypass paywalls or auth without permission
- Never scrape personal/sensitive data without consent
