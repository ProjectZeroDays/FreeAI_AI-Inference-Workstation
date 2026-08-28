#!/usr/bin/env python3
"""Custom Code Builder — replaces FreeCode with intelligent code generation.

Generates custom code from natural language specs using the FreeAI router.
Supports multiple languages, frameworks, and patterns.
Includes a built-in code interpreter for verification.
"""
import json
import os
import subprocess
import threading
import time
import tempfile
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

import requests

ROOT = Path(__file__).parent.parent
WORKSPACES_DIR = ROOT / "workspaces" / "custom_code"
WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)

ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:8100/proxy")
AGENT_API = os.environ.get("AGENT_API", "http://localhost:8020")

_CODE_LOCK = threading.Lock()
_CODE_RUNS = {}

# ── Supported languages/frameworks ────────────────────────────────────
LANGUAGES = {
    "python": {
        "default_framework": "fastapi",
        "frameworks": ["fastapi", "django", "flask", "streamlit", "cli", "script"],
        "run_command": "python {file}",
        "test_command": "pytest {test_file} -v",
        "lint_command": "ruff check {file}",
    },
    "typescript": {
        "default_framework": "node",
        "frameworks": ["node", "express", "next", "react", "cli", "script"],
        "run_command": "node {file}",
        "test_command": "jest {test_file} --verbose",
        "lint_command": "eslint {file}",
    },
    "javascript": {
        "default_framework": "node",
        "frameworks": ["node", "express", "react", "cli", "script"],
        "run_command": "node {file}",
        "test_command": "jest {test_file} --verbose",
        "lint_command": "eslint {file}",
    },
    "go": {
        "default_framework": "standard",
        "frameworks": ["standard", "gin", "echo", "cli"],
        "run_command": "go run {file}",
        "test_command": "go test ./... -v",
        "lint_command": "golangci-lint run {file}",
    },
    "rust": {
        "default_framework": "standard",
        "frameworks": ["standard", "actix", "axum", "cli"],
        "run_command": "cargo run",
        "test_command": "cargo test --all",
        "lint_command": "cargo clippy",
    },
    "sh": {
        "default_framework": "standard",
        "frameworks": ["standard"],
        "run_command": "bash {file}",
        "test_command": "bash -n {file}",
        "lint_command": "shellcheck {file}",
    },
}

# ── Code generation prompts ───────────────────────────────────────────
Scaffold_PROMPTS = {
    "python": """You are a Python engineer. Generate a complete {framework} application.
Spec: {spec}
Requirements:
- Write production-ready code
- Include error handling, logging, and type hints
- Add a requirements.txt
- Add a README with setup instructions
- Output each file as: ```path/to/file\n<content>\n```""",
    "typescript": """You are a TypeScript engineer. Generate a complete {framework} application.
Spec: {spec}
Requirements:
- Write production-ready code with proper types
- Include error handling and logging
- Add package.json with all dependencies
- Add a README with setup instructions
- Output each file as: ```path/to/file\n<content>\n```""",
    "go": """You are a Go engineer. Generate a complete application.
Spec: {spec}
Requirements:
- Idiomatic Go code
- Proper error handling
- go.mod with dependencies
- README with build instructions
- Output each file as: ```path/to/file\n<content>\n```""",
    "rust": """You are a Rust engineer. Generate a complete application.
Spec: {spec}
Requirements:
- Safe Rust with proper error handling (Result/Option)
- Cargo.toml with dependencies
- README with build instructions
- Output each file as: ```path/to/file\n<content>\n```""",
}


def _call_llm(prompt, model=None, max_tokens=8192, temperature=0.2):
    import requests
    url = PROXY_URL if "/proxy" in PROXY_URL else f"{PROXY_URL.rsplit('/', 1)[0]}/proxy"
    payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}
    if model:
        payload["model"] = model
    try:
        r = requests.post(url, json=payload, timeout=660)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        try:
            r2 = requests.post(ROUTER_URL, json={
                "prompt": prompt, "max_tokens": max_tokens, "temperature": temperature},
                timeout=660)
            r2.raise_for_status()
            return r2.json()
        except Exception:
            raise HTTPException(status_code=502, detail=f"LLM unavailable: {exc}")


def _extract_text(result):
    resp = result.get("response", {})
    if isinstance(resp, dict):
        return resp.get("content", "") or str(resp.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return str(resp)


def _parse_file_blocks(text):
    import re
    blocks = []
    for match in re.finditer(r"```(?:\w+)?\n?(.*?)```", text, re.DOTALL):
        content = match.group(1).strip()
        if not content:
            continue
        lines = content.split("\n")
        first = lines[0].strip()
        if first and ("/" in first or "." in first) and not first.startswith("#"):
            path = first
            body = "\n".join(lines[1:]).strip()
        else:
            path = "."
            body = content
        if body:
            blocks.append((path, body))
    return blocks


def generate_code(spec, language="python", framework=None, run_id=None,
                  workspace_dir=None):
    """Generate code from a natural language spec."""
    run_id = run_id or f"code_{int(time.time())}"
    lang_cfg = LANGUAGES.get(language, LANGUAGES["python"])
    fw = framework or lang_cfg["default_framework"]

    prompt_template = Scaffold_PROMPTS.get(language, Scaffold_PROMPTS["python"])
    prompt = prompt_template.format(spec=spec, framework=fw)

    result = _call_llm(prompt, max_tokens=16384, temperature=0.1)
    text = _extract_text(result)

    blocks = _parse_file_blocks(text)
    ws_dir = Path(workspace_dir) if workspace_dir else WORKSPACES_DIR / run_id
    ws_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for path, content in blocks:
        if not content.strip():
            continue
        try:
            full = ws_dir / path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            written += 1
        except (OSError, ValueError):
            pass

    record = {
        "run_id": run_id,
        "language": language,
        "framework": fw,
        "spec": spec,
        "files_written": written,
        "workspace": str(ws_dir),
        "status": "done",
        "created_at": time.time(),
    }
    with _CODE_LOCK:
        _CODE_RUNS[run_id] = record
    return record


def verify_code(run_id, language="python"):
    """Run verification (lint + test) on generated code."""
    with _CODE_LOCK:
        record = _CODE_RUNS.get(run_id)
    if not record:
        return {"error": f"Run not found: {run_id}"}

    ws = Path(record["workspace"])
    lang_cfg = LANGUAGES.get(language, LANGUAGES["python"])
    results = {}

    # Lint
    lint_cmd = lang_cfg.get("lint_command", "")
    if lint_cmd:
        for py_file in ws.rglob("*.py"):
            cmd = lint_cmd.format(file=str(py_file))
            try:
                proc = subprocess.run(cmd, shell=True, capture_output=True,
                                      text=True, timeout=60, cwd=str(ws))
                results[f"lint:{py_file.name}"] = {"exit": proc.returncode,
                                                   "output": proc.stdout[-1000:]}
            except Exception as exc:
                results[f"lint:{py_file.name}"] = {"error": str(exc)}

    # Test
    test_cmd = lang_cfg.get("test_command", "")
    if test_cmd:
        for test_file in sorted(ws.rglob("*test*.py"))[:3]:
            cmd = test_cmd.format(test_file=str(test_file))
            try:
                proc = subprocess.run(cmd, shell=True, capture_output=True,
                                      text=True, timeout=120, cwd=str(ws))
                results[f"test:{test_file.name}"] = {"exit": proc.returncode,
                                                      "output": proc.stdout[-2000:]}
            except Exception as exc:
                results[f"test:{test_file.name}"] = {"error": str(exc)}

    record["verification"] = results
    record["verified_at"] = time.time()
    return record


def run_code(run_id, language="python", args=None):
    """Run the generated code."""
    with _CODE_LOCK:
        record = _CODE_RUNS.get(run_id)
    if not record:
        return {"error": f"Run not found: {run_id}"}

    ws = Path(record["workspace"])
    lang_cfg = LANGUAGES.get(language, LANGUAGES["python"])
    run_cmd = lang_cfg.get("run_command", "python {file}")

    # Find main entry point
    if language == "python":
        main_files = list(ws.glob("main.py")) + list(ws.glob("app.py"))
        entry = main_files[0] if main_files else next(ws.rglob("*.py"), None)
    else:
        entry = next(ws.rglob("*.js"), None) or next(ws.rglob("*.ts"), None)

    if not entry:
        return {"error": "No runnable entry point found", "workspace": str(ws)}

    cmd = run_cmd.format(file=str(entry), args=" ".join(args) if args else "")
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True,
                              text=True, timeout=30, cwd=str(ws))
        return {
            "exit_code": proc.returncode,
            "stdout": proc.stdout[-3000:],
            "stderr": proc.stderr[-1000:],
        }
    except subprocess.TimeoutExpired:
        return {"error": "timeout after 30s", "exit_code": -1}
    except Exception as exc:
        return {"error": str(exc), "exit_code": -1}


def improve_code(run_id, instruction, language="python"):
    """Improve existing code based on an instruction."""
    with _CODE_LOCK:
        record = _CODE_RUNS.get(run_id)
    if not record:
        return {"error": f"Run not found: {run_id}"}

    ws = Path(record["workspace"])
    # Read existing files
    existing = {}
    for f in ws.rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            try:
                existing[str(f.relative_to(ws))] = f.read_text(encoding="utf-8")
            except OSError:
                pass

    prompt = f"""You are improving existing code.

LANGUAGE: {language}
INSTRUCTION: {instruction}

Existing files:
"""
    for path, content in list(existing.items())[:5]:
        prompt += f"\n--- {path} ---\n{content[:1500]}\n"

    prompt += f"""
 Apply the instruction. Output each modified file as:
 ```path/to/file
 <full updated content>
 ```
Only output files that need changes."""

    result = _call_llm(prompt, max_tokens=8192, temperature=0.1)
    text = _extract_text(result)
    blocks = _parse_file_blocks(text)

    for path, content in blocks:
        try:
            full = ws / path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
        except (OSError, ValueError):
            pass

    record["improved_at"] = time.time()
    record["improvement_instruction"] = instruction
    return record


# ── FastAPI ───────────────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="Custom Code Builder API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class GenerateRequest(BaseModel):
        spec: str
        language: str = "python"
        framework: Optional[str] = None
        run_id: Optional[str] = None
        workspace_dir: Optional[str] = None

    class VerifyRequest(BaseModel):
        language: str = "python"

    class RunRequest(BaseModel):
        args: Optional[list[str]] = None

    class ImproveRequest(BaseModel):
        instruction: str
        language: str = "python"

    @app.get("/health")
    def health():
        return {"status": "ok", "languages": list(LANGUAGES.keys())}

    @app.get("/languages")
    def languages():
        return {k: {"frameworks": v["frameworks"]} for k, v in LANGUAGES.items()}

    @app.post("/code/generate")
    def generate(req: GenerateRequest):
        return generate_code(req.spec, req.language, req.framework, req.run_id, req.workspace_dir)

    @app.post("/code/verify/{run_id}")
    def verify(run_id: str, req: VerifyRequest = None):
        lang = req.language if req else "python"
        return verify_code(run_id, lang)

    @app.post("/code/run/{run_id}")
    def run(run_id: str, req: RunRequest = None):
        return run_code(run_id, args=req.args if req else None)

    @app.post("/code/improve/{run_id}")
    def improve(run_id: str, req: ImproveRequest):
        return improve_code(run_id, req.instruction, req.language)

    @app.get("/code/runs")
    def list_runs():
        with _CODE_LOCK:
            runs = list(_CODE_RUNS.values())
        return {"runs": runs, "total": len(runs)}

    @app.get("/code/run/{run_id}")
    def get_run(run_id: str):
        with _CODE_LOCK:
            run = _CODE_RUNS.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return run


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("CODEBUILDER_PORT", "8183"))
        print(f"[custom-code-builder] Starting on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[custom-code-builder] FastAPI not available. Use functions directly.")
