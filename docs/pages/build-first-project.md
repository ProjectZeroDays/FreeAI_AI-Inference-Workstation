# Run Your First Project — Autonomous SDLC Demo

Watch FreeAI plan, code, test, fix, and package a complete project from a single prompt.

## The One-Liner

```bash
python freeai.py auto-start "Build a FastAPI notes service with auth and tests" --watch
```

## What Happens

1. **Plan** — Agent analyzes the spec and creates a task list
2. **Code** — Writes files in a sandboxed workspace
3. **Verify** — Runs `pytest`, `node --check`, or `compileall` to validate
4. **Fix** — Reads error output and patches code (up to 3 rounds)
5. **Review** — Reviews the final implementation
6. **Document** — Generates README and API docs
7. **Package** — Creates a tarball artifact for download

## Check Progress

```bash
# List active runs
curl localhost:8050/auto/runs

# Get run status
curl localhost:8050/auto/runs/<run_id>

# Download artifact
curl localhost:8050/auto/runs/<run_id>/artifact -o project.tar.gz
```

## Shell Access (Optional)

Enable shell tools for real verification:

```bash
export ENABLE_SHELL_TOOLS=1
python freeai.py auto-start "Build a CLI tool" --watch --shell
```

## Concurrency Limits

Control parallel runs:

```bash
export MAX_CONCURRENT_RUNS=2
```

## Next Steps

- [Workflow Engine](build-workflows.md) — Chain multiple tasks
- [Agent API](../API.md) — Direct agent endpoints
- [Troubleshooting](../TROUBLESHOOTING.md) — Fix common issues
