# WebSocket Streaming

Parallel to SSE: `ws://localhost:8011/ws/route`. Send `{"prompt":"...","max_tokens":512}` and receive `{"content":"..."}` frames until `{"done":true}`. Bridges the existing SSE generator via `asyncio.to_thread`. Add `?token=` header auth mirrors `X-API-Key`.
