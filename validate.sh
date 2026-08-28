#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

fail=0

echo "[validate] Checking venv..."
if [ ! -d "venv" ]; then
  echo "FAIL venv missing"
  fail=1
fi

echo "[validate] Checking models directory..."
if [ ! -d "models" ]; then
  echo "FAIL models/ missing"
  fail=1
fi

echo "[validate] Checking registry..."
if [ ! -f "registry/registry.json" ]; then
  echo "FAIL registry/registry.json missing"
  fail=1
fi

echo "[validate] Checking manifests..."
for f in mimocode-models.json jcode-models.json opencode-models.json; do
  if [ ! -f "manifest/$f" ]; then
    echo "FAIL manifest/$f missing"
    fail=1
  fi
done

echo "[validate] Checking quantization sanity (Q4_K/Q5_K/Q6_K only)..."
bad_quant=0
for gguf in models/*.gguf; do
  [ -e "$gguf" ] || continue
  base="$(basename "$gguf")"
  if ! echo "$base" | grep -Eqi 'Q[4-6]_K|Q8_0|BF16|F16|IQ4'; then
    echo "WARN $base: aggressive quant (IQ2/IQ3?) hurts coherence"
    bad_quant=1
  fi
done
[ "$bad_quant" = "0" ] && echo "OK   all present models use sane quants"

echo "[validate] Checking llama.cpp server binary..."
if [ ! -x "llama.cpp/build/bin/llama-server" ] && ! command -v llama-server >/dev/null 2>&1; then
  echo "WARN llama-server not built yet (run ./install.sh)"
fi

check_port() {
  local port="$1" name="$2"
  if ss -tuln 2>/dev/null | grep -q ":$port"; then
    echo "OK   $name port $port open"
  else
    echo "WARN $name port $port not open"
  fi
}

check_port 8010 router
check_port 8020 agents
check_port 8030 dashboard
check_port 8040 workflow
check_port 8050 autonomous
check_port 8100 proxy
check_port 8110 memory
check_port 8120 agents-api
check_port 8130 registry
check_port 8140 rag
check_port 8150 brain
check_port 8160 skills
check_port 8170 pipeline
check_port 8180 knightshade
check_port 8190 godmode
check_port 8192 campaign
check_port 9001 llama

if [ "$fail" -eq 0 ]; then
  echo "[validate] Done — core checks passed."
else
  echo "[validate] FAILED — fix errors above."
  exit 1
fi
