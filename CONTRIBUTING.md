# Contributing to FreeAI

Thanks for helping make this the most complete self-hosted AI workstation on GitHub.

## Quick Start

```bash
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation
pip install -r requirements-dev.txt
make test   # 88 tests, fully offline with MOCK_LLM=1
make lint   # bash -n + py_compile + json lint
```

## Development Workflow

1. **Branch:** `git checkout -b feat/your-feature`
2. **Code:** Keep changes focused; add tests for new behavior.
3. **Verify:**
   ```bash
   make lint && make test
   mkdocs build --strict  # docs must build clean
   ```
4. **Commit:** `git commit -m "feat: ..."` — follow Conventional Commits.
5. **Push & PR:** `gh pr create --fill` — fill the template, link any issue.

## Project Structure

- `router/` — task classifier + fallback chain (8010)
- `agents/` — project/refactor/debug/analyze + red/blue/purple teaming (8020)
- `workflow/` — pipeline engine (8040)
- `autonomous/` — full SDLC lifecycle (8050)
- `dashboard/` — GPU telemetry + control plane (8030) + `SAMPLE_TELEMETRY=1` demo
- `hardware/` — `install-stack.sh` provisioner
- `docs/` — MkDocs sources (see `mkdocs.yml`)

## Testing

- `MOCK_LLM=1` runs the entire API surface without a GPU.
- Golden-task evals: `python evals/run_eval.py` (needs router up).

## Reporting Issues

Use the Bug Report template — include OS, GPU (`nvidia-smi`), `freeai.py status`, and relevant `*.log` tails.

## Security

See `SECURITY.md` — do **not** file public issues for vulnerabilities.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
