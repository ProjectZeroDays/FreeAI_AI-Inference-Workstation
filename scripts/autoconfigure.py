#!/usr/bin/env python3
"""
FreeAI Universal Autoconfigure — step-by-step provider + GUI setup

Prompts for API keys for every supported provider and wires them into:
- .env (source of truth for router + docker compose)
- config/providers.json (enabled/fallback)
- opencode.json / jcode.json / hermes.json / openclaw.json (per-app provider.apiKey)
- FreeAI dashboard providers panel (via config/providers.json)

Providers covered:
  FreeAI (local, no key), Venice AI, Hugging Face, Opencode Zen,
  OpenRouter, Agnes AI, OpenAI, Google (Gemini), Anthropic Claude
  + extras from router/providers.py (Groq, Mistral, DeepSeek, etc. — optional)

Hermes + OpenClaw GUI are auto-enabled and pointed at FreeAI router.
"""
import os, json, pathlib, getpass, textwrap, sys, argparse, subprocess, shutil, re, shlex

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
PROVIDERS_JSON = ROOT / "config" / "providers.json"

PROVIDERS = [
  ("VENICE_API_KEY",     "Venice AI",          "https://api.venice.ai — uncensored (Red Team primary)", "venice"),
  ("HF_TOKEN",           "Hugging Face",       "https://huggingface.co/settings/tokens — Inference Router", "huggingface"),
  ("ZEN_API_KEY",        "Opencode Zen",       "https://opencode.ai/zen — local + cloud", "zen"),
  ("OPENROUTER_API_KEY", "OpenRouter",         "https://openrouter.ai/keys — 400+ models aggregator", "openrouter"),
  ("AGNES_API_KEY",      "Agnes AI",           "https://apihub.agnes-ai.com — Agnes 2.0 Flash", "agnes"),
  ("OPENAI_API_KEY",     "OpenAI",             "https://platform.openai.com/api-keys — GPT-4o / o3", "openai"),
  ("GOOGLE_API_KEY",     "Google Gemini",      "https://aistudio.google.com/app/apikey — Gemini 2.5", "google"),
  ("ANTHROPIC_API_KEY",  "Anthropic Claude",   "https://console.anthropic.com/settings/keys — Sonnet/Opus", "anthropic"),
  ("GROQ_API_KEY",       "Groq",               "https://console.groq.com/keys", "groq"),
  ("MISTRAL_API_KEY",    "Mistral",            "https://console.mistral.ai/api-keys", "mistral"),
  ("DEEPSEEK_API_KEY",   "DeepSeek",           "https://platform.deepseek.com/api_keys", "deepseek"),
]

APP_JSONS = ["opencode.json", "jcode.json", "hermes.json", "openclaw.json"]

def load_env():
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v=line.split("=",1); env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def save_env(env):
    lines = []
    if ENV_PATH.exists():
        raw = ENV_PATH.read_text(encoding="utf-8").splitlines()
        seen=set()
        for line in raw:
            if "=" in line and not line.strip().startswith("#"):
                k=line.split("=",1)[0].strip()
                if k in env:
                    v = env[k]
                    if re.search(r'[ \t#\"\']|\n|\r', v):
                        v = shlex.quote(v)
                    lines.append(f"{k}={v}"); seen.add(k); continue
            lines.append(line)
        for k,v in env.items():
            if k not in seen:
                if re.search(r'[ \t#\"\']|\n|\r', v):
                    v = shlex.quote(v)
                lines.append(f"{k}={v}")
    else:
        for k,v in env.items():
            if re.search(r'[ \t#\"\']|\n|\r', v):
                v = shlex.quote(v)
            lines.append(f"{k}={v}")
    tmp = ENV_PATH.with_suffix(".tmp")
    tmp.write_text("\n".join(lines)+"\n", encoding="utf-8")
    tmp.replace(ENV_PATH)
    try: ENV_PATH.chmod(0o600)
    except: pass

def prompt_key(env_key, label, hint, provider):
    existing = os.environ.get(env_key) or ""
    env = load_env()
    existing = env.get(env_key, existing)
    prompt = f"\n[{provider}] {label}\n  {hint}\n  Env: {env_key}\n"
    if existing:
        masked = "***" + existing[-4:] if len(existing) > 4 else "***"
        prompt += f"  Current: {masked} (len={len(existing)}, press Enter to keep)\n"
    prompt += "  Enter API key (or 'skip' / Enter to leave empty): "
    try:
        val = getpass.getpass(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled."); sys.exit(1)
    if val.lower() == "skip":
        return ""
    if val == "" and existing:
        return existing
    if "\n" in val or "\r" in val:
        print("  Invalid key (contains newline), skipping.")
        return existing
    return val

def update_app_jsons(keys):
    mapping = {
      "VENICE_API_KEY": "venice",
      "HF_TOKEN": "huggingface",
      "ZEN_API_KEY": "zen",
      "OPENROUTER_API_KEY": "openrouter",
      "AGNES_API_KEY": "agnes",
      "OPENAI_API_KEY": "openai",
      "ANTHROPIC_API_KEY": "anthropic",
      "GOOGLE_API_KEY": "google",
      "GROQ_API_KEY": "groq",
      "MISTRAL_API_KEY": "mistral",
      "DEEPSEEK_API_KEY": "deepseek",
    }
    for fname in APP_JSONS:
        p = ROOT / fname
        if not p.exists(): continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  warn: {fname} invalid JSON: {e}", file=sys.stderr)
            continue
        providers = data.get("provider") or data.get("providers") or {}
        changed=False
        for ek, prov in mapping.items():
            if prov in providers and ek in keys and keys[ek]:
                opts = providers[prov].get("options", {})
                key = "apiKey" if "apiKey" in opts else "api_key" if "api_key" in opts else None
                if key:
                    # Keep env-only: do not store real secret in tracked file
                    if opts[key] != "":
                        opts[key] = ""
                        changed=True
                else:
                    if providers[prov].get("apiKey") != "":
                        providers[prov]["apiKey"] = ""
                        changed=True
        if changed:
            tmp = p.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
            tmp.replace(p)
            print(f"  updated {fname} (secrets kept in .env only)")

def detect_system():
    info = {"gpu": "unknown", "vram": 0, "ram_gb": 0, "cpu": "unknown"}
    try:
        out = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"], stderr=subprocess.DEVNULL, text=True)
        if out.strip():
            name, mem = out.strip().split(",")
            info["gpu"] = name.strip()
            info["vram"] = int(mem.strip())
    except: pass
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    info["ram_gb"] = int(line.split()[1]) // 1024 // 1024
                    break
    except:
        try:
            import psutil
            info["ram_gb"] = int(psutil.virtual_memory().total // (1024**3))
        except: info["ram_gb"] = 16
    if info["vram"] >= 24000:
        rec = {"gpu_layers": 80, "ctx_size": 32768, "batch_size": 64, "mode": "balanced"}
    elif info["vram"] >= 16000:
        rec = {"gpu_layers": 60, "ctx_size": 16384, "batch_size": 48, "mode": "balanced"}
    elif info["vram"] >= 8000:
        rec = {"gpu_layers": 40, "ctx_size": 8192, "batch_size": 32, "mode": "eco"}
    else:
        rec = {"gpu_layers": 32, "ctx_size": 4096, "batch_size": 16, "mode": "eco"}
    rec.update(info)
    return rec

def apply_recommended_system_config(rec):
    runtime_path = ROOT / "config" / "runtime-settings.json"
    try:
        cfg = json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.exists() else {}
    except: cfg = {}
    cfg.update({
        "gpu_layers": rec["gpu_layers"],
        "ctx_size": rec["ctx_size"],
        "batch_size": rec["batch_size"],
        "mode": rec["mode"],
        "autonomous_setup": True,
        "detected_gpu": rec["gpu"],
        "detected_vram": rec["vram"],
        "detected_ram_gb": rec["ram_gb"],
    })
    runtime_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = runtime_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2)+"\n", encoding="utf-8")
    tmp.replace(runtime_path)
    env = load_env()
    env.update({
        "GPU_LAYERS": str(rec["gpu_layers"]),
        "CTX_SIZE": str(rec["ctx_size"]),
        "BATCH_SIZE": str(rec["batch_size"]),
        "FREEMODE": rec["mode"],
    })
    save_env(env)
    return cfg

def main():
    parser = argparse.ArgumentParser(description="FreeAI Universal Autoconfigure — autonomous or manual setup")
    parser.add_argument("--autonomous", "--yes", "-y", action="store_true", dest="autonomous", help="Autonomous mode: auto-detect system and apply recommended settings without prompting")
    parser.add_argument("--manual", action="store_true", help="Manual step-by-step configuration (default interactive)")
    parser.add_argument("--check", action="store_true", help="Check current config without prompting")
    args = parser.parse_args()

    if args.check:
        env = load_env()
        rec = detect_system()
        print(f"System: {rec['gpu']} ({rec['vram']} MB VRAM), {rec['ram_gb']} GB RAM")
        print(f"Recommended: layers={rec['gpu_layers']} ctx={rec['ctx_size']} batch={rec['batch_size']} mode={rec['mode']}")
        print(f"Env keys present: {[k for k,_l,_h,_p in PROVIDERS if k in env]}")
        return

    autonomous = args.autonomous or (not sys.stdin.isatty() and not args.manual)
    if os.environ.get("FREEAI_AUTONOMOUS_SETUP") == "1":
        autonomous = True

    if autonomous:
        print(textwrap.dedent("""
        ╔══════════════════════════════════════════════════════════╗
        ║  FreeAI Autonomous Setup (Recommended)                  ║
        ║  Auto-detecting hardware and applying optimal settings  ║
        ╚══════════════════════════════════════════════════════════╝
        """))
        rec = detect_system()
        print(f"  Detected: GPU={rec['gpu']} ({rec['vram']} MB), RAM={rec['ram_gb']} GB")
        print(f"  Applying: gpu_layers={rec['gpu_layers']} ctx_size={rec['ctx_size']} batch={rec['batch_size']} mode={rec['mode']}")
        cfg = apply_recommended_system_config(rec)
        print(f"  ✓ System config written to config/runtime-settings.json")
        env = load_env()
        collected = {k: env.get(k, "") for k,_l,_h,_p in PROVIDERS}
        if PROVIDERS_JSON.exists():
            try:
                pj = json.loads(PROVIDERS_JSON.read_text(encoding="utf-8"))
            except: pj = {"providers": {}}
        else:
            pj = {"providers": {}}
        for ek, label, hint, prov in PROVIDERS:
            if prov not in pj["providers"]: pj["providers"][prov] = {"enabled": True}
            has_key = bool(env.get(ek))
            is_local = prov in ("freeai","ollama","lmstudio","freetoken")
            pj["providers"][prov]["enabled"] = bool(has_key or is_local)
            if has_key:
                pj["providers"][prov]["fallback"] = prov in ("openrouter","huggingface","venice","agnes","zen","groq","mistral","deepseek")
            else:
                pj["providers"][prov]["fallback"] = False
        tmp = PROVIDERS_JSON.with_suffix(".tmp")
        tmp.write_text(json.dumps(pj, indent=2)+"\n", encoding="utf-8")
        tmp.replace(PROVIDERS_JSON)
        print(f"  ✓ Providers auto-configured ({len([k for k in collected if collected[k]])} keys found)")
        for mf in ["mimocode/hermes.json", "mimocode/openclaw.json"]:
            pp = ROOT / mf
            if pp.exists():
                try:
                    d=json.loads(pp.read_text(encoding="utf-8")); d["enabled"]=True
                    tmp2 = pp.with_suffix(".tmp")
                    tmp2.write_text(json.dumps(d, indent=2)+"\n", encoding="utf-8")
                    tmp2.replace(pp)
                except: pass
        print("  ✓ Hermes (7001) + OpenClaw (7002) GUI enabled")
        print(textwrap.dedent("""
        ── Autonomous Setup Complete ──────────────────────────
        No prompts needed. System is ready with recommended settings.
        To customize, run: python scripts/autoconfigure.py --manual
        Or edit .env and config/runtime-settings.json directly.
        Restart: docker compose up -d --build router agents
        Dashboard: http://localhost:8030
        """))
        return

    print(textwrap.dedent("""
    ╔══════════════════════════════════════════════════════════╗
    ║  FreeAI Universal Autoconfigure                         ║
    ║  Wires EVERY provider into EVERY app (FreeAI, OpenCode, ║
    ║  JCode, Hermes, OpenClaw) + GUI                        ║
    ╚══════════════════════════════════════════════════════════╝
    Providers will be prompted step-by-step. Leave empty to skip.
    Keys are saved to .env (never committed).
    Hermes TUI: hermes dashboard --tui  | GUI: http://localhost:7001
    OpenClaw GUI: http://localhost:7002 | FreeAI Dashboard: :8030

    Tip: Run with --autonomous for zero-prompt recommended setup.
    """))
    env = load_env()
    collected = {}
    for ek, label, hint, prov in PROVIDERS:
        if ek in ("GROQ_API_KEY", "MISTRAL_API_KEY", "DEEPSEEK_API_KEY") and not collected.get("_ask_extras"):
            try:
                ans = input("\nConfigure extra providers (Groq/Mistral/DeepSeek)? [y/N]: ").strip().lower()
            except: ans="n"
            collected["_ask_extras"] = ans
            if ans not in ("y","yes"):
                continue
        # validate key format
        while True:
            val = prompt_key(ek, label, hint, prov)
            if not val or re.match(r'^[A-Za-z0-9_\-./+=\s]+$', val):
                break
            print("  Invalid key format (contains illegal characters), try again or 'skip'.")
        collected[ek] = val
        if val:
            env[ek] = val
            os.environ[ek] = val
        else:
            env.pop(ek, None)

    save_env(env)
    print(f"\n✓ Saved {ENV_PATH} ({len([k for k,_l,_h,_p in PROVIDERS if k in env])} keys)")

    if PROVIDERS_JSON.exists():
        try:
            pj = json.loads(PROVIDERS_JSON.read_text(encoding="utf-8"))
        except: pj = {"providers": {}}
    else:
        pj = {"providers": {}}
    for ek, label, hint, prov in PROVIDERS:
        if prov not in pj["providers"]: pj["providers"][prov] = {"enabled": True}
        has_key = bool(collected.get(ek))
        is_local = prov in ("freeai","ollama","lmstudio","freetoken")
        pj["providers"][prov]["enabled"] = bool(has_key or is_local)
        if has_key:
            pj["providers"][prov]["fallback"] = prov in ("openrouter","huggingface","venice","agnes","zen","groq","mistral","deepseek")
        else:
            pj["providers"][prov].pop("fallback", None)
            if not is_local:
                pj["providers"][prov]["enabled"] = False
    tmp = PROVIDERS_JSON.with_suffix(".tmp")
    tmp.write_text(json.dumps(pj, indent=2)+"\n", encoding="utf-8")
    tmp.replace(PROVIDERS_JSON)
    print(f"✓ Updated {PROVIDERS_JSON}")

    update_app_jsons(collected)

    for mf in ["mimocode/hermes.json", "mimocode/openclaw.json"]:
        pp = ROOT / mf
        if pp.exists():
            try:
                d=json.loads(pp.read_text(encoding="utf-8")); d["enabled"]=True
                tmp2 = pp.with_suffix(".tmp")
                tmp2.write_text(json.dumps(d, indent=2)+"\n", encoding="utf-8")
                tmp2.replace(pp)
            except: pass
    print("✓ Hermes (7001) + OpenClaw (7002) GUI enabled (mimocode manifests)")

    print(textwrap.dedent("""
    ── Done ──────────────────────────────────────────────
    Keys saved to .env (gitignored). Restart stack to apply:

      docker compose up -d --build router agents  # or: ./start.sh
      opencode --version && hermes dashboard --tui  # verify

    Test a provider:
      curl -s http://localhost:8010/providers | python -m json.tool | head -40
      python freeai.py providers
      python freeai.py provider-test openai

    GUI:
      FreeAI Dashboard  http://localhost:8030
      Hermes TUI        hermes dashboard --tui  (container 172.16.1.2)
      Hermes GUI        http://localhost:7001
      OpenClaw GUI      http://localhost:7002
      OpenCode          http://localhost:3000
      JCode             http://localhost:5000
    """))

if __name__ == "__main__":
    main()
