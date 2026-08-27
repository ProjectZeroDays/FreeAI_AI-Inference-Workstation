# Model Registry UI

The dashboard **Models** tab (and `/api/models-status`) is the registry UI.

- **Registry:** `registry/registry.json` (8-model roster, roles, strengths)
- **Scoring:** `scripts/model-benchmark.sh` writes `config/model-scores.json` (tok/s per task, measured on this GPU). The UI sorts by score.
- **UI:** Model shelf shows present/missing + free disk + load time (from `GET /api/models/timings`).
