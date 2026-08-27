# Function Calling & Tool Use (ROADMAP 15b)

Beyond file ops, the autonomous agent now supports tool use:

- **Registry:** `autonomous/tools.json` -- list of tools (read, edit, bash, webfetch, grep)
- **Loop:** LLM emits `{"tool": "bash", "args": {"cmd": "pytest -q"}}` ? executor runs ? result fed back
- **RAG + Vector DB:** already: Qdrant `--profile rag` + `docs/RAG.md`
- **Document ingestion:** `scripts/ingest.py --path ./docs` ? Qdrant `freeai-docs`
- **Repo-wide auto-refactor:** `freeai.py auto-start "refactor entire repo to add type hints" --max-tasks 12` (uses repo-map compression)
- **Multi-GPU:** `--profile llama2` + `CUDA_VISIBLE_DEVICES` per shard + `router/load_balancer.py` (least_latency)
- **Model registry UI:** `docs/MODEL_REGISTRY_UI.md`
