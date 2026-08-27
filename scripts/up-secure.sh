#!/usr/bin/env bash
set -euo pipefail
# Decrypt with sops (preferred) or fall back to plain .env
if command -v sops >/dev/null 2>&1 && [ -f config/secrets.enc.yaml ]; then
  sops exec-env config/secrets.enc.yaml 'docker compose up -d --build'
elif command -v vault >/dev/null 2>&1; then
  echo "vault detected — export VAULT_ADDR and use vault kv get"
  vault kv get -format=json secret/freeai | jq -r '.data.data | to_entries[] | "\(.key)=\(.value)"' | docker compose --env-file /dev/stdin up -d --build
else
  docker compose up -d --build
fi
