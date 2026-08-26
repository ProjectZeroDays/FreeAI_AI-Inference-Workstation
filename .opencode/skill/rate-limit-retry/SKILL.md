---
name: rate-limit-retry
description: Rate limiting (RPM/TPM/concurrency) and self-healing retry/backoff for LLM provider calls and tool calls in opencode. Use when a model or API call returns 429/5xx/timeout, when batching many subagent dispatches, when planning around provider quotas, or when deciding fallback strategy across OpenAI/Azure/Anthropic/local models. Covers token-bucket budgeting, retry-after honoring, exponential backoff with jitter, circuit breakers, idempotency keys, and fallback chains.
---

# Rate limit + self-healing retry

Provider failures and quota errors are **expected**, not exceptional. Treat
them as flow control. This skill defines the budget math, the backoff schedule,
and the fallback chain used across this project.

## 1. Budget per provider (client-side limits)

Don't rely on the server to tell you you're over limit. Track client-side caps
that are *below* the server's real limits so you leave headroom:

| provider        | typical RPM | typical TPM      | notes                              |
|-----------------|-------------|------------------|------------------------------------|
| openai          | 500 (tier 2)| 30k–10M           | raises with usage tier             |
| azure openai    | per-deployment | per-deployment | quota is per *deployment*, not key  |
| anthropic       | ~50 (build) → 1000+ | 40k–400k | tiers scale fast                    |
| vllm / ollama   | unlimited   | GPU memory bound  | limit by **concurrency**, not RPM   |
| llama.cpp       | unlimited   | single-stream     | concurrency = 1 unless multi-slot   |

For local providers, there is no real RPM but there *is* a hard concurrency
floor: GPU memory and KV-cache size. Cap concurrent in-flight requests at
`floor((free_vram_gb - 2) / per_request_gb)` and queue beyond that.

## 2. Token-bucket, the only model you need

One bucket per (provider, model) keyed by RPM and one by TPM. Refill
continuously:

```
now = time.monotonic()
elapsed = now - last_refill
rpm_tokens = min(rpm_limit,   rpm_tokens   + elapsed * rpm_limit/60)
tpm_tokens = min(tpm_limit,   tpm_tokens   + elapsed * tpm_limit/60)
last_refill = now
if rpm_tokens >= 1 and tpm_tokens >= est_tokens:
    rpm_tokens -= 1; tpm_tokens -= est_tokens; return OK
else:
    sleep(min(rpm_limit/60, (1-rpm_tokens)/rpm_limit*60))  # wait for refill
```

This avoids the thundering-herd problem that a naive fixed-window limiter causes
at the window boundary.

## 3. Backoff schedule (use this exact one)

For retries on 429/5xx/timeout/network error:

```
attempt 1: immediate
attempt 2: 0.5s  + jitter(0, 0.25)
attempt 3: 1.0s  + jitter(0, 0.5)
attempt 4: 2.0s  + jitter(0, 1.0)
attempt 5: 4.0s  + jitter(0, 2.0)
attempt 6: 8.0s  + jitter(0, 4.0)
# then stop and fall back (see §5). Max 6 attempts for a single call.
```

`jitter(min, max)` = uniform random in [min, max). Jitter is mandatory — without
it, every retry hits the server at the same instant after a transient outage.

## 4. Honor server hints above your own schedule

- **`Retry-After` header** (429/503): sleep exactly that long, not your backoff.
- **`retry-after` / `retry_after` in a JSON body** (some Azure/Anthropic
  responses): same — server wins.
- **Anthropic `anthropic-ratelimit-*` headers** (`requests-remaining`,
  `tokens-remaining`, `requests-reset`, `tokens-reset`): if `*-remaining` is 0,
  sleep until the corresponding `*-reset` timestamp instead of guessing.

## 5. Fallback chain

When a call exhausts its 6 attempts, fall back; don't just fail.

```
anthropic/claude-sonnet  →  openai/gpt-4o  →  azure/gpt-4o  →  vllm/local-model
openai/gpt-4o            →  azure/gpt-4o   →  anthropic     →  local
local (any)              →  (no fallback; report capacity error to user)
```

Rules:
- Fall back for *this call only*. Don't silently rewrite the whole session's
  model after one hiccup.
- Log which provider you fell back to so the user knows.
- Local models are a last resort for complex tasks; prefer them for
  planner/maintainer-style triage, not generation-quality work, unless they're
  big enough.

## 6. Idempotency for writes

Any tool call that *mutates* state (an HTTP POST/PATCH, a git push, an MCP tool
with side effects) must carry an idempotency key so a retry doesn't double-apply:

- HTTP: send `Idempotency-Key: <uuid>` header when the API supports it (Stripe,
  OpenAI, many do).
- Git: stage before commit, and never `push` twice — after a push timeout, run
  `git status` + `git log @{u}..` to see whether it actually landed before
  retrying.
- A subagent that retries: include the attempt number in any temp path so
  re-runs don't collide.

## 7. Circuit breaker

Per (provider, model), keep a small sliding window (last 10 calls). If ≥5 are
failures, **open the breaker**: stop sending traffic to that provider for 60s,
go straight to fallback. After 60s, allow one probe call; if it succeeds, close
the breaker. This prevents retry storms against a hard-down endpoint.

The bundled plugin (`.opencode/plugin/rate-limit.ts`) implements this breaker as
a live example you can wire up to event hooks.

## 8. What you must NOT do

- Retry without jitter. Ever.
- Retry more than 6 times for one logical call.
- Ignore a `Retry-After` header because your own backoff is shorter.
- Sweep failures under the rug — surface the provider/error and what you tried
  in your final message to the user.