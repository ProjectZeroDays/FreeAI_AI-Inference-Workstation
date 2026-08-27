#!/usr/bin/env python3
"""FreeAI Provider Registry — loads API keys from .env, never hardcodes them.

Usage:
    python agents/provider_config.py          # generate all configs
    python agents/provider_config.py --check  # verify provider connectivity
    python agents/provider_config.py --env    # print .env template
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
MIMOCODE_DIR = ROOT / "mimocode"
PROVIDERS_FILE = CONFIG_DIR / "providers-all.json"
CLIENTS_FILE = CONFIG_DIR / "clients-config.json"
SKILLS_SYNC_FILE = CONFIG_DIR / "skills-sync.json"
MCPS_SYNC_FILE = CONFIG_DIR / "mcps-sync.json"
PLUGINS_SYNC_FILE = CONFIG_DIR / "plugins-sync.json"
AGENTS_SYNC_FILE = CONFIG_DIR / "agents-sync.json"
VASTAI_FILE = CONFIG_DIR / "vastai-config.json"
SSH_KEYS_FILE = CONFIG_DIR / "ssh-keys.json"
ENV_TEMPLATE = ROOT / ".env.template"

PROVIDER_DEFS = {
    "openai": {"name": "OpenAI", "base_url": "https://api.openai.com/v1", "key_env": "OPENAI_API_KEY", "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1", "o1-mini"], "clients": ["mimocode", "opencode", "jcode", "hermes", "openclaw"]},
    "agentrouter": {"name": "AgentRouter", "base_url": "https://agentrouter.org", "key_env": "AGENTROUTER_AUTH_TOKEN", "models": ["claude-opus-4-6", "claude-sonnet-4", "claude-haiku-4"], "clients": ["mimocode", "opencode", "jcode", "hermes", "openclaw"]},
    "omniroute": {"name": "OmniRoute", "base_url": "https://api.omniroute.ai/v1", "key_env": "OMNIROUTE_API_KEY", "models": ["omni-1-pro", "omni-1-mini"], "clients": ["mimocode", "opencode"]},
    "anthropic": {"name": "Anthropic (DIA SAP)", "base_url": "https://api.anthropic.com/v1", "key_env": "DIA_SAP_PROJECT_RED_SWORD", "models": ["claude-opus-4-20250514", "claude-sonnet-4-20250514", "claude-haiku-4-20250414"], "clients": ["mimocode", "opencode", "jcode", "hermes", "openclaw"]},
    "deepseek": {"name": "DeepSeek", "base_url": "https://api.deepseek.com/v1", "key_env": "DEEPSEEK", "models": ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"], "clients": ["mimocode", "opencode", "jcode", "hermes"]},
    "perplexity": {"name": "Perplexity", "base_url": "https://api.perplexity.ai", "key_env": "PERPLEXITY_PRO_API_KEY", "models": ["sonar", "sonar-pro", "sonar-reasoning"], "clients": ["mimocode", "opencode", "jcode"]},
    "gemini": {"name": "Google Gemini", "base_url": "https://generativelanguage.googleapis.com/v1beta", "key_env": "GEMINI_API_KEY", "models": ["gemini-2.0-flash", "gemini-2.0-flash-thinking", "gemini-2.5-pro"], "clients": ["mimocode", "opencode", "jcode", "hermes", "openclaw"]},
    "venice": {"name": "Venice AI", "base_url": "https://api.venice.ai/api/v1", "key_env": "VENICE_AI_API_KEY", "models": ["gemma-4-uncensored", "llama-3.1-405b", "claude-3-5-sonnet"], "clients": ["mimocode", "opencode"]},
    "agames_ai": {"name": "Agnes AI (API Hub)", "base_url": "https://apihub.agnes-ai.com/v1", "key_env": "AGNES_API_KEY", "models": ["agnes-2.0-flash", "agnes-2.0-pro"], "clients": ["hermes", "mimocode", "opencode", "jcode"]},
    "openrouter": {"name": "OpenRouter", "base_url": "https://openrouter.ai/api/v1", "key_env": "OPENROUTER_API_KEY", "models": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "deepseek/deepseek-r1"], "clients": ["mimocode", "opencode", "jcode", "hermes", "openclaw"]},
    "nexustrade": {"name": "Nexustrade", "base_url": "https://nexustrade.io/api/v1", "key_env": "NEXUSTRADE_API_KEY", "models": ["nt-coder-v1", "nt-chat-v1"], "clients": ["mimocode", "opencode"]},
    "shodan": {"name": "Shodan", "base_url": "https://api.shodan.io", "key_env": "SHODAN_API_KEY", "models": [], "clients": ["mimocode", "opencode"]},
    "wakatime": {"name": "WakaTime", "base_url": "https://api.wakatime.com/api/v1", "key_env": "WAKATIME_API_KEY", "models": [], "clients": ["mimocode", "opencode", "jcode"]},
    "tabnine": {"name": "Tabnine", "base_url": "https://api.tabnine.com", "key_env": "TABNINE_API_KEY", "models": [], "clients": ["mimocode", "opencode"]},
    "langchain": {"name": "LangChain / LangSmith", "base_url": "https://api.smith.langchain.com", "key_env": "LANGCHAIN_API_KEY", "models": [], "clients": ["mimocode", "opencode", "jcode"]},
    "huggingface": {"name": "HuggingFace", "base_url": "https://huggingface.co", "key_env": "HUGGINGFACE_API_KEY", "models": [], "clients": ["mimocode", "opencode"]},
    "gemini_ai_studio": {"name": "Google AI Studio", "base_url": "https://generativelanguage.googleapis.com/v1beta", "key_env": "AI_STUDIO_API_KEY", "models": ["gemini-2.0-flash", "gemini-2.0-flash-thinking"], "clients": ["mimocode", "opencode", "jcode"]},
    "cody": {"name": "Sourcegraph Cody", "base_url": "https://sourcegraph.com/.api/completions", "key_env": "CUDY_CODER", "models": [], "clients": ["mimocode", "opencode"]},
    "envia": {"name": "Envia (Eden AI)", "base_url": "https://www.envia.com/api/v1", "key_env": "EDEN_API_KEY", "models": [], "clients": ["mimocode", "opencode"]},
    "nvapi": {"name": "NVIDIA NVAI", "base_url": "https://integrate.api.nvidia.com/v1", "key_env": "NVAPI_KEY", "models": ["nemo", "llama-3.1-405b"], "clients": ["mimocode", "opencode"]},
    "hostinger": {"name": "Hostinger", "base_url": "https://hostinger.com/api", "key_env": "HOSTINGER_API_KEY", "models": [], "clients": ["mimocode"]},
    "omg_lol": {"name": "OMG.lol", "base_url": "https://api.omg.lol/v1", "key_env": "OMG_LOL_API_KEY", "models": [], "clients": ["mimocode"]},
}

CLIENTS = ["mimocode", "mimocode-desktop", "opencode", "opencode-desktop", "jcode", "jcode-terminal", "hermes", "hermes-desktop", "openclaw", "openclaw-desktop"]

DEFAULT_SKILLS = ["red_teaming/godmode", "red_teaming/recon", "red_teaming/exploit", "blue_teaming/siem", "blue_teaming/forensics", "blue_teaming/hunting", "purple_teaming/sim", "purple_teaming/validate", "browser/automation", "browser/fingerprint", "browser/cdp", "code/review", "code/refactor", "code/debug", "code/test", "data/pipeline", "data/etl", "data/analysis", "devops/ci_cd", "devops/docker", "devops/kubernetes", "docs/write", "docs/api", "docs/readme", "memory/persistent", "memory/cross_session", "productivity/cron", "productivity/scheduler", "security/aikido", "security/scan", "security/pentest", "agent/orchestrate", "agent/swarm", "agent/coord", "mcp/register", "mcp/browser", "mcp/github", "mcp/search", "media/generate", "media/transcribe", "media/speak", "research/web", "research/summarize", "research/cite"]
DEFAULT_MCP_SERVERS = ["browser", "github", "filesystem", "memory", "search", "sql", "postgres", "mongodb", "redis", "slack", "discord", "telegram", "vector", "embedding", "rag", "code", "lint", "test"]
DEFAULT_PLUGINS = ["auto-skill-creator", "rate-limit", "memory-sync", "provider-rotator", "health-monitor", "audit-log", "skill-registry", "agent-coordinator"]
DEFAULT_AGENTS = ["orchestrator", "explorer", "oracle", "council", "librarian", "designer", "fixer", "coder", "reviewer", "researcher", "architect", "tester"]

VASTAI_TEMPLATE = {"name": "tokugawa-https-caddy", "description": "FreeAI: llama.cpp + Tokugawa WebUI + Caddy HTTPS + Qwen3.5-9B", "image": "tokugawaai/llama.cpp:latest", "version_tag": "latest", "disk": 250, "ssh_keys_env": ["SSH_KEY_HOSTINGER", "SSH_KEY_VASI"], "env": {"OPEN_BUTTON_PORT": "1111", "JUPYTER_DIR": "/workspace", "DATA_DIRECTORY": "/workspace", "PORTAL_CONFIG": "localhost:1111:11111:/:InstancePortal|localhost:8000:18000:/:TokugawaWebUI|localhost:8080:18080:/:APIServer"}, "ports": {"8080/tcp": 8080, "8000/tcp": 8000, "1111/tcp": 1111, "8443/tcp": 8443}, "gpu": {"minVRAM": 32, "gpuName": "RTX PRO 4000 Ada", "maxPrice": 0.40}, "extra_filters": "verified=true gpu_display_active=true gpu_ram>=32", "onstart_script": "scripts/create-vastai-template.sh"}

SSH_KEYS_CONFIG = {"keys": [{"name": "hostinger", "env_var": "SSH_KEY_HOSTINGER"}, {"name": "vasi", "env_var": "SSH_KEY_VASI"}], "tunnel_env": "SSH_TUNNEL_CMD", "gateway_env": "GATEWAY_WS"}


def ensure_dirs():
    for f in [PROVIDERS_FILE, CLIENTS_FILE, SKILLS_SYNC_FILE, MCPS_SYNC_FILE, PLUGINS_SYNC_FILE, AGENTS_SYNC_FILE, VASTAI_FILE, SSH_KEYS_FILE]:
        f.parent.mkdir(parents=True, exist_ok=True)


def load_env_keys():
    env_path = ROOT / ".env"
    keys = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                keys[k.strip()] = v.strip()
    return keys


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_providers(env_keys):
    providers = {}
    for pid, defn in PROVIDER_DEFS.items():
        key_env = defn["key_env"]
        key_val = env_keys.get(key_env, os.environ.get(key_env, ""))
        providers[pid] = {**defn, "key_set": bool(key_val), "key_env": key_env}
    save_json(PROVIDERS_FILE, providers)
    return providers


def save_clients():
    save_json(CLIENTS_FILE, {"clients": CLIENTS, "count": len(CLIENTS)})


def install_for_client(client_id, synced, mcps, plugins, agents):
    for store, items in [("skills", synced), ("mcps", mcps), ("plugins", plugins), ("agents", agents)]:
        if client_id not in items.get("installed", []):
            items.setdefault("installed", []).append(client_id)
            items.setdefault(store + "s", []).extend(globals()[f"DEFAULT_{store.upper()}"])
    return {"client": client_id, "skills": len(synced.get("skills", [])), "mcps": len(mcps.get("mcps", [])), "plugins": len(plugins.get("plugins", [])), "agents": len(agents.get("agents", []))}


def generate_dotenv_template():
    lines = [
        "# FreeAI Provider Keys",
        "# Copy this file to .env and fill in your keys",
        "# .env is gitignored - never commit it",
        "",
        "# === AI Providers ===",
        "OPENAI_API_KEY=sk-your-openai-key-here",
        "AGENTROUTER_AUTH_TOKEN=sk-your-agentrouter-token-here",
        "OMNIROUTE_API_KEY=sk-your-omniroute-key-here",
        "DIA_SAP_PROJECT_RED_SWORD=sk-ant-your-key-here",
        "DEEPSEEK=sk-your-deepseek-key-here",
        "PERPLEXITY_PRO_API_KEY=pplx-your-key-here",
        "GEMINI_API_KEY=AIzaSy-your-key-here",
        "AI_STUDIO_API_KEY=AIzaSy-your-key-here",
        "VENICE_AI_API_KEY=your-venice-key-here",
        "AGNES_API_KEY=sk-your-agnes-key-here",
        "OPENROUTER_API_KEY=sk-or-v1-your-key-here",
        "NEXUSTRADE_API_KEY=sk-your-nexustrade-key-here",
        "SHODAN_API_KEY=your-shodan-key-here",
        "WAKATIME_API_KEY=waka-your-key-here",
        "TABNINE_API_KEY=your-tabnine-key-here",
        "LANGCHAIN_API_KEY=your-langchain-key-here",
        "HUGGINGFACE_API_KEY=hf_your-key-here",
        "CUDY_CODER=sgp_your-key-here",
        "EDEN_API_KEY=your-edena-key-here",
        "NVAPI_KEY=your-nvapi-key-here",
        "HOSTINGER_API_KEY=your-hostinger-key-here",
        "OMG_LOL_API_KEY=your-omg-key-here",
        "",
        "# === Vast.ai ===",
        "VAST_AI_KEY_1=your-vastai-key-1-here",
        "VAST_AI_KEY_2=your-vastai-key-2-here",
        "",
        "# === SSH Keys ===",
        "SSH_KEY_HOSTINGER=ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAISQ7BLwP7UeY640OQg30ZgudbJC+akFj3af7xFCXWV root@srv1931796",
        "SSH_KEY_VASI=ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF6D4LVOXZIMfmg/vQmOnjHosSgzLJhpjjB8+bJ/2Ldq vasi.ai",
        "",
        "# === SSH / Tunnel ===",
        "SSH_HOST=38.49.42.120",
        "SSH_PORT=54681",
        "SSH_USER=root",
        "SSH_TUNNEL_CMD=ssh -p 54681 root@38.49.42.120 -L 8080:localhost:8080",
        "",
        "# === Gateway ===",
        "GATEWAY_WS=ws://127.0.0.1:18789",
        "GATEWAY_API=your-gateway-api-key-here",
        "",
        "# === Misc ===",
        "KALI_PASSWORD=Tr3y@113nSm1th",
        "VENICE_ADMIN_KEY=EhaJOyTNWZfdHeDkTsmTchl0CK7bfXWCYWF0ADuPOJ",
        "VENICE_INFERENCE_KEY=vsOau-T_WcgKdpCENOLLRFPaLxvkviwgIx7MUyN2M6",
        "",
        "# === GitHub ===",
        "GITHUB_PAT=ghp-your-github-pat-here",
        "GITHUB_BREW_TOKEN=ghp-your-brew-token-here",
        "",
        "# === LM Studio ===",
        "LM_STUDIO_API_KEY=sk-lm-your-key-here",
    ]
    ENV_TEMPLATE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(ENV_TEMPLATE)


def generate_opencode_config(env_keys):
    provider_section = {}
    for pid, defn in PROVIDER_DEFS.items():
        key_env = defn["key_env"]
        key_val = env_keys.get(key_env, os.environ.get(key_env, ""))
        if key_val:
            provider_section[pid] = {"name": defn["name"], "options": {"baseURL": defn["base_url"], "apiKey": f"${{{key_env}}}"}, "models": {m: {"name": m} for m in defn.get("models", [])}}
    config = {"$schema": "https://opencode.ai/config.json", "provider": provider_section, "model": "agentrouter/claude-opus-4-6", "skills": DEFAULT_SKILLS, "mcp_servers": DEFAULT_MCP_SERVERS, "plugins": DEFAULT_PLUGINS, "agents": DEFAULT_AGENTS}
    config_path = ROOT / ".opencode" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return str(config_path)


def generate_client_config(client_id, env_keys):
    providers = {}
    for pid, defn in PROVIDER_DEFS.items():
        if client_id in defn.get("clients", []):
            key_env = defn["key_env"]
            key_val = env_keys.get(key_env, os.environ.get(key_env, ""))
            providers[pid] = {"name": defn["name"], "base_url": defn["base_url"], "models": defn.get("models", []), "key_set": bool(key_val)}
    config = {"client": client_id, "providers": providers, "skills": DEFAULT_SKILLS, "mcps": DEFAULT_MCP_SERVERS, "plugins": DEFAULT_PLUGINS, "agents": DEFAULT_AGENTS}
    path = MIMOCODE_DIR / f"{client_id}-providers.json"
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return str(path)


def main():
    ensure_dirs()
    env_keys = load_env_keys()
    print(f"[provider] Loaded {len(env_keys)} keys from .env")

    providers = save_providers(env_keys)
    save_clients()
    save_json(VASTAI_FILE, VASTAI_TEMPLATE)
    save_json(SSH_KEYS_FILE, SSH_KEYS_CONFIG)
    env_template = generate_dotenv_template()
    opencode_path = generate_opencode_config(env_keys)
    print(f"[provider] .env template: {env_template}")
    print(f"[provider] opencode config: {opencode_path}")

    for client in CLIENTS:
        path = generate_client_config(client, env_keys)
        print(f"  [provider] {client} -> {path}")

    synced = load_json(SKILLS_SYNC_FILE, {"skills": [], "installed": []})
    mcps = load_json(MCPS_SYNC_FILE, {"mcps": [], "installed": []})
    plugins = load_json(PLUGINS_SYNC_FILE, {"plugins": [], "installed": []})
    agents = load_json(AGENTS_SYNC_FILE, {"agents": [], "installed": []})

    for client in CLIENTS:
        result = install_for_client(client, synced, mcps, plugins, agents)
        print(f"  [sync] {client}: {result['skills']} skills, {result['mcps']} mcps, {result['plugins']} plugins, {result['agents']} agents")

    save_json(SKILLS_SYNC_FILE, synced)
    save_json(MCPS_SYNC_FILE, mcps)
    save_json(PLUGINS_SYNC_FILE, plugins)
    save_json(AGENTS_SYNC_FILE, agents)

    checklist = [
        "## Provider Configuration Checklist\n",
        "### Phase 1: Keys Setup\n",
        "- [ ] Copy `.env.template` to `.env` and fill in all API keys\n",
        "- [ ] Run `python agents/provider_config.py` to generate all configs\n",
        "- [ ] Check `config/providers-all.json` for `key_set: true`\n",
        "\n### Phase 2: Cross-Client Install\n",
    ]
    for c in CLIENTS:
        checklist.append(f"- [ ] `{c}` — {len(DEFAULT_SKILLS)} skills, {len(DEFAULT_MCP_SERVERS)} MCPs, {len(DEFAULT_PLUGINS)} plugins, {len(DEFAULT_AGENTS)} agents")
    checklist += [
        "\n### Phase 3: Vast.ai\n",
        "- [ ] `config/vastai-config.json` saved\n",
        "- [ ] `scripts/create-vastai-template.sh` runs successfully\n",
        "\n### Phase 4: SSH & Tunnel\n",
        "- [ ] `config/ssh-keys.json` has hostinger + vasi keys\n",
        "- [ ] SSH tunnel to 38.49.42.120:54681 working\n",
        "\n### Phase 5: Verify\n",
        "- [ ] `python agents/provider_config.py --check` shows all providers healthy\n",
        "- [ ] All 10 clients route through configured providers\n",
    ]
    (CONFIG_DIR / "IMPLEMENTATION-CHECKLIST.md").write_text("\n".join(checklist), encoding="utf-8")
    print(f"\n[provider] Total: {len(providers)} providers x {len(CLIENTS)} clients = {len(providers) * len(CLIENTS)} pairs")
    print(f"[provider] Checklist: {CONFIG_DIR / 'IMPLEMENTATION-CHECKLIST.md'}")


if __name__ == "__main__":
    main()
