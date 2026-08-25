SHELL := /bin/bash

.PHONY: help install vllm test lint up down logs backup restore clean update-llama

help:
	@echo "install      - provision venv + build llama.cpp (CUDA if nvcc)"
	@echo "vllm-install - bare-metal vLLM backend into .venv-vllm"
	@echo "test         - pytest suite (offline)"
	@echo "lint         - bash/py/js/json static checks"
	@echo "up / down    - docker compose core stack up/down"
	@echo "logs         - tail stack logs"
	@echo "backup       - config/registry/manifest snapshot"
	@echo "restore F=   - restore from backups/F"
	@echo "update-llama - pull latest llama.cpp + rebuild"

install:
	bash install.sh

vllm-install:
	bash vllm/install-vllm.sh

test:
	python3 -m pytest

lint:
	@status=0; \
	for f in $$(git ls-files '*.sh'); do bash -n $$f || status=1; done; \
	for f in $$(git ls-files '*.py'); do python3 -m py_compile $$f || status=1; done; \
	for f in $$(git ls-files '*.js'); do node --check $$f || status=1; done; \
	for f in $$(git ls-files '*.json'); do python3 -m json.tool $$f >/dev/null || status=1; done; \
	exit $$status

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	tail -n 50 logs/*.log

backup:
	bash scripts/backup.sh

restore:
	bash scripts/backup.sh restore $(F)

clean:
	find . -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache

update-llama:
	bash install.sh --update-llama
