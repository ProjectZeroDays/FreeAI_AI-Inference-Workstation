---
name: self-heal
description: Diagnose and recover from broken tool calls, API failures, import errors, and environment problems inside opencode autonomously. Use when a tool or model call errors out (HTTP error, timeout, auth failure, "module not found", "command not found", ENOENT, ECONNREFUSED), when a subagent reports it couldn't finish, when a package/script can't be found, or when diagnosing why a provider stops working. Covers the decision tree from symptom → root cause → fix.
---

# Self-heal — diagnosing failures autonomously

When something breaks, don't guess and don't immediately retry. Diagnose first,
then apply the smallest fix that addresses the root cause. This skill is the
decision tree; pair it with `rate-limit-retry` for the backoff math.

## 0. First rule

A failure with a clear message is a task. A failure with a vague message is a
**research task**. Re-read the actual error text before doing anything. 80% of
"broken API" tickets are people who didn't read the message.

## 1. Decision tree (follow in order)

### A. Error mentions a status code or network condition

| signal                            | root cause class        | first move                          |
|-----------------------------------|-------------------------|-------------------------------------|
| 401 / 403                         | auth                    | check key is set + correct provider |
| 404 from `/v1/...`                | wrong baseURL/model id  | verify model id exists on server    |
| 429                               | rate limit              | go to `rate-limit-retry` §4         |
| 500/502/503/504                   | server/transient        | `rate-limit-retry` §3 backoff       |
| `ECONNREFUSED` / timeout          | server not up / network | probe endpoint, then start server   |
| `ECONNRESET` mid-stream           | broken keep-alive       | retry; reduce concurrency to 1      |
| `certificate` / `self-signed`     | TLS                     | never disable verification; fix certs |
| `socket hang up` to a local port  | local server crashed    | restart vLLM/Ollama/llama.cpp       |

### B. Error is about a module/package/script

| signal                            | first move                                  |
|-----------------------------------|---------------------------------------------|
| `Module not found` (Node)        | `npm ls <pkg>`; is it in `package.json`?    |
| `ModuleNotFoundError` (Python)   | is it in the active venv/`requirements.txt`?|
| `command not found`              | `where <cmd>` on Windows / `command -v` on *nix |
| `cannot find module '../x'`      | wrong cwd or stale relative path             |
| `SyntaxError` after fresh install| version mismatch — pin to the working major  |

Never `npm install -g` or `pip install` system-wide to "just make it work."
Install into the project's lockfile/venv and document it.

### C. Error came from a subagent's return

If a subagent's message ends with an error or trails off:
1. It did NOT finish — treat its output as partial, not authoritative.
2. Re-read the *exact* error it quoted. If it didn't quote one, that's the bug
   to fix in the prompt: instruct subagents to always paste the full error.
3. Fix the *root cause* (bad path, missing dep, wrong model id), not the symptom
   (don't just re-dispatch). Re-dispatch at most **once** after fixing.

### D. Everything "looks fine" but the call still fails

Run this probe sequence, in order, and report the results rather than looping:
1. `curl -sS -o /dev/null -w "%{http_code}" <baseURL>/models` — does the server
   answer at all? (For OpenAI-compatible local servers.)
2. `echo $KEY | wc -c` — is the env var actually set in *this* shell? (opencode
   env != your login shell env.)
3. Try the same call with the **next provider in the fallback chain**
   (`rate-limit-retry` §5). If it works, the first provider is the problem.

## 2. Fixing the most common opencode-specific failures

### Wrong model id
opencode models are `provider/model-id`. The `model-id` must match what the
provider's `/models` endpoint returns *exactly*. For Azure it's the **deployment
name**, not the OpenAI model name. For vLLM it's `--served-model-name`. For
Ollama it's `ollama list` output (tags included, e.g. `llama3.1:8b`).

### Local server not answering
- vLLM: `curl http://localhost:8000/v1/models` — empty = not started.
- Ollama: `ollama list` + `ollama ps` (is it loaded?).
- llama.cpp server: check the port; default is 8080.

Restart the server with `--host 0.0.0.0` only if exposing remotely; locally
keep `127.0.0.1`.

### Env var interpolation
`opencode.json` supports `{env:VAR}` (and `{file:path}`) in string values. The
shell `${VAR}` form is NOT substituted. If a key shows as literal `{env:...}` in
a server error log, you forgot to export it.

### Config won't load at all
opencode hard-fails on invalid config. Test with the escape hatch:
`OPENCODE_DISABLE_PROJECT_CONFIG=1` to start from globals, fix the broken file,
restart without the flag. Validate against `https://opencode.ai/config.json`.

## 3. Hardware/software fitness check (when a model "can't be supported")

Before recommending a local model, check the box instead of guessing:

```
# GPU / VRAM (NVIDIA)        → Windows: nvidia-smi   *nix: nvidia-smi / rocm-smi
# RAM                        → Windows: wmic OS get FreePhysicalMemory  *nix: free -h
# CPU                        → Windows: wmic cpu get name  *nix: lscpu
# Disk                       → Windows: fsutil  *nix: df -h
```

Rough rule for local LLM inference: a quantized model needs ~`params * 0.6 GB`
of VRAM at Q4 (e.g. 8B ≈ 5GB, 70B ≈ 42GB). Leave 2GB headroom for KV cache. If
`free_vram < needed`, recommend a smaller model or a cloud provider instead of
letting it OOM mid-generation.

## 4. Stop conditions — when NOT to keep trying

- Same error after fixing the diagnosed root cause and one re-dispatch → stop,
  report to the user with the full error and what you tried.
- Anything that requires disabling TLS verification, global installs, or
  `--no-verify` → stop, it's the wrong fix.
- A loop that would hit >12 total retries across a fallback chain → stop.

## 5. What to put in your final message

```
ROOT CAUSE: <one line>
FIX:        <one line, or "needs human input: ...">
PROOF:      <the command/output that confirms it's fixed, or "unverified: why">
FALBACK USED: <provider/model or "none">
```
No preamble, no apology.