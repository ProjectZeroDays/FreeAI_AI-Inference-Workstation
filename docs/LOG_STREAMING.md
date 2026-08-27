# Log Streaming

- **SSE:** `GET /api/events` already pushes settings/model changes.
- **Logs:** `GET /api/logs?service=router&tail=200` streams the last N lines from `/logs/<service>.log` (FluentBit tails these to Loki).
- **Follow:** `GET /api/logs/stream?service=router` -- SSE that tails the file.

Implemented as a thin Flask endpoint reading the log directory; when Loki is enabled (`--profile observability`) logs are also queryable in Grafana.
