# Autonomous SDLC Agents

The `autonomous/` layer turns a one-line spec into a packaged project —
the full development life cycle, unattended.

## Life cycle

```
queued → planning → coding → testing → fixing → reviewing
       → documenting → packaging → done | failed | cancelled
```

| Phase | What happens |
|---|---|
| planning | LLM decomposes the spec into ordered tasks (JSON plan) |
| coding | per-task code generation; complete files written to a sandboxed workspace |
| testing | **real** verification when shell tools are on: `compileall`, `pytest`/`unittest`, `node --check` run inside the workspace; otherwise static placeholder/content scan |
| fixing | failures (actual compiler/test output) fed back to the model; up to `MAX_FIX_ROUNDS` repair passes |
| reviewing | strict reviewer verdict (`PASS`/`FIX` + issues) recorded in the report |
| documenting | README.md (+ docs/API.md where applicable) generated from the final tree |
| packaging | workspace tarred to an artifact, downloadable via API/CLI |

## Safety model

- All file writes resolve inside `workspaces/<run_id>/`; traversal,
  absolute paths, and drive letters are rejected.
- Shell execution is **off by default**. Enable server-side with
  `ENABLE_SHELL_TOOLS=1`; per-run it still requires the caller to pass
  `enable_shell: true`. Commands run in the workspace dir with timeouts
  and capped output capture.
- Runs are cancellable at every phase boundary (`POST .../cancel`).

## API (:8050)

| Method | Path |
|---|---|
| POST | /auto/start `{spec, profile?, max_tasks?, enable_shell?}` → run_id |
| GET | /auto/runs · /auto/runs/{id} |
| POST | /auto/runs/{id}/cancel |
| GET | /auto/runs/{id}/artifact → tar.gz (404 until packaged) |
| POST | /auto/runs/{id}/shell `{command}` (guarded) |

## CLI

```bash
python3 tokugawa.py auto-start "Build a FastAPI notes service with tests" --watch 20
python3 tokugawa.py auto-runs
python3 tokugawa.py auto-fetch <run_id> -o my-project.tar.gz
```

## Deployment

- Compose: `autonomous` service on :8050 with a persistent workspaces volume.
- K8s: `k8s/autonomous-deployment.yml`.
