"""SSE streaming passthrough for /route (ROADMAP 2)."""
import json, time

def sse_event(data: dict):
    return f"data: {json.dumps(data)}\n\n"

def stream_tokens(tokens):
    for tok in tokens:
        yield sse_event({"content": tok, "ts": int(time.time()*1000)})
    yield "data: [DONE]\n\n"
