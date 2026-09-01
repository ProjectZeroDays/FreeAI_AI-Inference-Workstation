---
name: darkweb_scanner
description: >
  Dark web (.onion) content scanner via Tor proxy -- safe read-only crawling,
  indexing, and structured result export for display in the dark web browser.
triggers:
  - darkweb
  - onion
  - tor
  - dark web crawler
  - DARKWEB_SCANNER
  - dark web scan
  - onion scan
  - tor browse
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-09-01"
  agent: agents/specialized/darkweb_scanner/darkweb_scanner_agent.py
---

# DarkWebScanner

Dark web (.onion) content scanner via Tor proxy. Read-only, safe browsing with structured results.

## Purpose
Index and display .onion service content through Tor isolation. No exploitation -- read-only crawling with structured output for the dark web browser UI.

## Safety
- **Read-only**: never writes to or interacts with target services beyond HTTP GET
- **Tor-isolated**: all traffic routed through local Tor SOCKS proxy (port 9050)
- **No authentication bypass**: does not attempt login or credential harvesting
- **Rate-limited**: respects crawl depth and page count limits to avoid flooding

## Capabilities
- `.onion` URL resolution via Tor SOCKS5 proxy
- Multi-depth BFS crawling with configurable depth and page limits
- Title extraction, content length, link discovery
- Structured JSON/CSV report generation
- Quick single-host lookup for known .onion addresses

## Usage
```python
from agents.specialized.darkweb_scanner.darkweb_scanner_agent import DarkWebScanner

scanner = DarkWebScanner(tor_socks_port=9050)

# Check Tor connectivity
print(scanner.is_tor_available())  # True if Tor running

# Quick single-page lookup
result = scanner.quick_lookup('duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twHQwzur4q.onion')

# Crawl starting from a known .onion directory
crawl = scanner.crawl('http://exampleonion123.onion/', max_depth=2, max_pages=20)

# Generate report
report_json = scanner.generate_report('json')
report_csv = scanner.export_csv()
report_dict = scanner.generate_report('dict')

# Agent describe
info = scanner.describe()
```

## Result Display
Results are structured for the dark web browser UI:
- `title`: page title extracted from HTML
- `content_length`: bytes of content retrieved
- `onion_links`: discovered .onion links on the page (up to 20)
- `preview`: first 2000 chars of page content
- `status`: HTTP status code or error message
- `timestamp`: scan timestamp

## Dependencies
- Python stdlib only (urllib, socket, re, json, csv, io)
- Tor running locally on port 9050 (SOCKS5) or 9150 (Tor Browser)
- No external packages required
