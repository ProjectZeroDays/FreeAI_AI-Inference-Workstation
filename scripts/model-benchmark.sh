#!/usr/bin/env bash
# Model performance scoring (ROADMAP 14)
set -euo pipefail
for m in qwen3.6-12b claude-code-9b moe-13b; do
  echo "Benchmarking $m..."
  curl -s http://localhost:8010/route -H "Content-Type: application/json" -d "{\"prompt\":\"benchmark $m\",\"max_tokens\":32}" | head -c 200
  echo
done
