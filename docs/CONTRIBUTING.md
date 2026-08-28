# Contributing to FreeAI

Thanks for helping make this the most complete self-hosted AI workstation on GitHub.

---

## Quick Start

```bash
git clone https://github.com/ProjectZeroDays/FreeAI_AI_Inference_Workstation.git
cd FreeAI_AI_Inference_Workstation
pip install -r requirements-dev.txt
make test   # 262 tests, fully offline with MOCK_LLM=1
make lint   # bash -n + py_compile + json lint
```

---

## Project Structure

| Directory | Purpose |
|---|---|
| `router/` | Task classifier, fallback chain, caching, rate limiting (:8010) |
| `agents/` | Project, refactor, debug, analyze, chat agents with profiles (:8020) |
| `workflow/` | Pipeline engine with validation and audit logs (:8040) |
| `autonomous/` | Full SDLC lifecycle: plan → code → test → fix → package (:8050) |
| `dashboard/` | GPU telemetry, settings, presets, alerts (:8030) |
| `browser/` | CDP-based browser engine with army orchestrator |
| `swarm/` | Parallel multi-agent execution with worktree isolation |
| `hardware/` | `install-stack.sh` provisioner and parts list |
| `k8s/` | Kubernetes manifests (deployments, HPA, PVC, network policies) |
| `live/` | Live ISO build scripts (Ubuntu remaster) |
| `models/` | Model download scripts and registry |
| `scripts/` | Utility scripts (benchmark, smoke-test, backup) |
| `tests/` | Unit and integration test suites |
| `docs/` | MkDocs documentation sources |

---

## Code Style

### Python

- **Type hints** on all public functions and methods
- **Docstrings** on all modules, classes, and public functions (Google style)
- **Linting**: `ruff` or `py_compile` (via `make lint`)
- **Formatting**: 4-space indentation, 88-char line limit (Black-compatible)
- **Imports**: Standard library first, then third-party, then local

Example:
```python
"""Module docstring describing purpose."""

from typing import Optional


def route_request(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 2048,
) -> dict:
    """Route a prompt through the fallback chain.

    Args:
        prompt: The input text to route.
        model: Optional explicit model override.
        max_tokens: Maximum response tokens.

    Returns:
        Dict with model_used, response, elapsed_ms keys.
    """
    ...
```

### Shell Scripts

- Use `set -euo pipefail` at the top
- Quote all variables: `"$VAR"` not `$VAR`
- Use `[[ ]]` for conditionals, not `[ ]`
- Function names in `snake_case`

### JSON Config

- All JSON files must be valid (checked by `make lint`)
- Use 2-space indentation
- Never commit files containing secrets

---

## Testing

### Running Tests

```bash
# All tests (requires MOCK_LLM=1 for router/agent tests)
make test

# Individual test file
pytest tests/test_classifier.py -v

# With coverage
pytest --cov=router --cov=agents tests/
```

### Test Requirements

- **All new features must have tests.** No exceptions.
- **Router tests** must pass with `MOCK_LLM=1` (no GPU required).
- **Agent tests** use canned responses when `MOCK_LLM=1`.
- **Integration tests** are in `tests/integration/` and require a running stack.
- **Golden-task evals** are in `evals/` and require the router to be healthy.

### Test Conventions

- Use descriptive test names: `test_route_falls_back_to_secondary_on_timeout`
- Use `pytest.mark.asyncio` for async tests
- Use fixtures for shared setup (mock router client, temp config)
- Mock external HTTP calls with `responses` or `unittest.mock`

```python
import responses

@responses.activate
def test_route_with_external_fallback():
    responses.add(
        responses.POST,
        "http://localhost:9001/completion",
        status=504,
    )
    responses.add(
        responses.POST,
        "http://localhost:9002/v1/chat/completions",
        json={"choices": [{"message": {"content": "fallback response"}}]},
    )
    # ... test logic
```

---

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

### Types

| Type | Description |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, semicolons, etc.) |
| `refactor` | Code refactoring without behavior change |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks, dependencies |
| `perf` | Performance improvements |
| `ci` | CI/CD pipeline changes |

### Examples

```bash
git commit -m "feat(router): add confidence scoring to task classification"

git commit -m "fix(agents): handle empty responses in refactor agent"

git commit -m "docs: update API guide with workflow endpoints"

git commit -m "refactor(router): extract fallback chain into switcher module"

git commit -m "test(router): add cache hit/miss coverage for /route"
```

---

## Pull Request Process

### Before Submitting

1. **Branch:** Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature
   ```

2. **Code:** Keep changes focused on a single concern. Add tests for new behavior.

3. **Verify:**
   ```bash
   make lint && make test
   mkdocs build --strict  # docs must build clean
   ```

4. **Commit:** Use conventional commits. Squash related commits before pushing.

5. **Push & PR:**
   ```bash
   git push origin feat/your-feature
   gh pr create --fill
   ```

### PR Template

When creating a PR, fill in:
- **Description:** What changed and why
- **Type of change:** Bug fix / New feature / Breaking change / Documentation
- **Testing:** How you verified the change
- **Related issues:** Link any related issues

### Review Process

- At least one maintainer review required
- All CI checks must pass
- Documentation updates required for API changes
- Changelog entry required for user-facing changes

---

## Documentation

### Writing Docs

Documentation lives in `docs/` and is built with MkDocs (`mkdocs.yml`).

```bash
# Local preview
pip install mkdocs-material
mkdocs serve

# Build check
mkdocs build --strict
```

### Doc Standards

- Use Mermaid diagrams for architecture and flow diagrams
- Include request/response examples for all API endpoints
- Link to related docs using relative paths
- Keep examples runnable (use `MOCK_LLM=1` where possible)

---

## Reporting Issues

Use the Bug Report template and include:
- OS and version
- GPU info (`nvidia-smi` output)
- `freeai.py status` output
- Relevant log tails from `logs/*.log`
- Steps to reproduce

---

## Security

See `SECURITY.md` — do **not** file public issues for vulnerabilities. Report through the appropriate security channel.

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
