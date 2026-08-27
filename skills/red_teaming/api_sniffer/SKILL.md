---
name: api_sniffer
description: >
  Reverse-engineers API transactions, maps app schemes via CDP Network domain.
  Intercepts HTTP/HTTPS traffic, extracts endpoints, auth schemes, and request/response patterns.
triggers:
  - api sniff
  - api transaction
  - endpoint mapping
  - network intercept
  - api reverse engineer
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-27"
  agent: agents/specialized/api_sniffer.py
---

# API Transaction Sniffer

Reverse-engineers API transactions and maps application schemes using CDP Network domain interception.

## Purpose
Captures and analyzes all API traffic from a target URL, building a complete map of endpoints, methods, auth schemes, and response patterns.

## Usage
```python
from agents.specialized.api_sniffer import ApiSniffer

sniffer = ApiSniffer(browser_engine)
await sniffer.start_capture("https://target.com")
# ... let it run ...
result = sniffer.stop_capture()
print(result["mappings"])
```

## Capabilities
- **Network Intercept**: Capture all HTTP/HTTPS requests via CDP
- **Scheme Mapping**: Auto-detect REST, GraphQL, gRPC endpoints
- **Auth Detection**: Identify JWT, OAuth, API key patterns
- **Transaction Log**: Full request/response timeline
- **Export**: JSON, CSV, or OpenAPI spec output

## Output Formats
- `transactions`: Raw captured API calls
- `mappings`: Structured API endpoint map
- `summary`: Aggregate statistics by method, status code, timing
