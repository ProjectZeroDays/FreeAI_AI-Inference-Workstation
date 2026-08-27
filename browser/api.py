"""Knight-Shade REST API — Full browser automation service.

Endpoints:
  GET  /health                     - Service health
  GET  /browser/state              - Current browser state
  POST /browser/open               - Navigate to URL
  POST /browser/close              - Close browser
  POST /browser/click              - Click element
  POST /browser/fill               - Fill form field
  POST /browser/extract            - Extract data
  POST /browser/screenshot         - Screenshot
  POST /browser/source             - Get HTML
  POST /browser/js                 - Execute JavaScript
  POST /browser/cookies            - Cookie management
  POST /browser/cdp                - Raw CDP command
  GET  /browser/healing            - Healing stats
  GET  /browser/manifestx          - Manifest-X info
  GET  /browser/anonymity          - Anonymity status
  POST /browser/rotate-circuit     - Rotate Tor circuit
  GET  /army/roster                - Agent roster
  POST /army/deploy                - Deploy agents
  POST /army/task                  - Execute task
  GET  /army/stats                 - Army stats
  POST /analysis/binary            - Ghidra analysis
  POST /analysis/wasm              - Wasm decompilation
  POST /instrument/hook            - Frida instrumentation
"""
import asyncio
import json
import os
import threading
import time
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from browser.engine import BrowserEngine, create_engine, CDPClient
from browser.anonymity import AnonymityRouter
from browser.army import get_army, ArmyAgent
from browser.intelligence import IntelligencePipeline

app = None
_engine = None
_engine_lock = threading.Lock()
_pipeline = IntelligencePipeline()


def get_engine():
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                cfg = {}
                cfg_path = Path(__file__).parent.parent / "config" / "browser.json"
                if cfg_path.exists():
                    try:
                        cfg = json.loads(cfg_path.read_text())
                    except Exception: pass
                _engine = create_engine(cfg)
    return _engine


def _run(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


if HAS_FASTAPI:
    app = FastAPI(title="Knight-Shade Browser API", version="2.0")
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
        allow_headers=["*"],)

    # ── Health ──────────────────────────────────────────────────
    @app.get("/health")
    def health():
        eng = get_engine()
        return {
            "status": "ok",
            "session": eng.session_id,
            "is_open": eng.is_open,
            "service": "knight-shade",
            "version": "2.0.0",
        }

    # ── Browser Controls ────────────────────────────────────────
    @app.get("/browser/state")
    def browser_state():
        return get_engine().get_state()

    class OpenReq(BaseModel):
        url: str
        wait_until: str = "networkidle"
        timeout: int = 60000

    @app.post("/browser/open")
    def open_url(req: OpenReq):
        eng = get_engine()
        _run(eng.open(req.url, req.wait_until, req.timeout))
        return {"url": eng.get_url_sync(), "title": eng.get_title_sync()}

    @app.post("/browser/close")
    def close_browser():
        eng = get_engine()
        _run(eng.close())
        return {"status": "closed"}

    class ClickReq(BaseModel):
        selector: str
        timeout: int = 5000

    @app.post("/browser/click")
    def click(req: ClickReq):
        eng = get_engine()
        _run(eng.click(req.selector, req.timeout))
        return {"clicked": req.selector}

    class FillReq(BaseModel):
        selector: str
        value: str

    @app.post("/browser/fill")
    def fill(req: FillReq):
        eng = get_engine()
        _run(eng.fill(req.selector, req.value))
        return {"filled": req.selector}

    class ExtractReq(BaseModel):
        selector: str
        attribute: str = "text"
        limit: int = 50

    @app.post("/browser/extract")
    def extract(req: ExtractReq):
        eng = get_engine()
        result = _run(eng.extract(req.selector, req.attribute))
        if isinstance(result, list):
            result = result[:req.limit]
        return {"selector": req.selector, "results": result}

    class ScreenshotReq(BaseModel):
        path: str | None = None
        full_page: bool = False

    @app.post("/browser/screenshot")
    def screenshot(req: ScreenshotReq):
        eng = get_engine()
        _run(eng.screenshot(req.path, req.full_page))
        return {"screenshot": req.path or "saved"}

    @app.post("/browser/source")
    def get_source():
        eng = get_engine()
        return {"source": _run(eng.get_source())[:10000]}

    class JSReq(BaseModel):
        expression: str

    @app.post("/browser/js")
    def run_js(req: JSReq):
        eng = get_engine()
        result = _run(eng.get_javascript(req.expression))
        return {"result": str(result) if result is not None else None}

    class CookieReq(BaseModel):
        action: str = "get"
        cookies: list | None = None

    @app.post("/browser/cookies")
    def cookies(req: CookieReq):
        eng = get_engine()
        if req.action == "get":
            return {"cookies": _run(eng.get_cookies())}
        elif req.action == "set":
            _run(eng.set_cookies(req.cookies or []))
            return {"set": True}
        elif req.action == "clear":
            _run(eng.clear_cookies())
            return {"cleared": True}

    class CDPReq(BaseModel):
        method: str
        params: dict | None = None

    @app.post("/browser/cdp")
    def cdp(req: CDPReq):
        eng = get_engine()
        result = _run(eng.cdp_send(req.method, req.params))
        return {"method": req.method, "result": result}

    @app.get("/browser/healing")
    def healing_stats():
        return get_engine()._healing.stats

    @app.get("/browser/manifestx")
    def manifestx_info():
        return get_engine()._manifestx.describe_caps()

    @app.get("/browser/anonymity")
    def anonymity_status():
        return get_engine()._anonymity.describe() if hasattr(get_engine(), '_anonymity') else {"mode": "none"}

    @app.post("/browser/rotate-circuit")
    def rotate_circuit():
        eng = get_engine()
        if hasattr(eng, '_anonymity'):
            return {"rotated": eng._anonymity.rotate_tor_circuit()}
        return {"rotated": False, "note": "No anonymity stack configured"}

    # ── Army ────────────────────────────────────────────────────
    @app.get("/army/roster")
    def army_roster(rank=None, division=None, status=None):
        army = get_army()
        agents = army._swarm.list_agents(rank=rank, division=division, status=status)
        return {"agents": [a.describe() for a in agents], "total": len(agents)}

    class DeployReq(BaseModel):
        count: int = 1
        rank: str = "E-1"
        division: str = "operations"
        anonymity_mode: str = "none"

    @app.post("/army/deploy")
    def deploy(req: DeployReq):
        army = get_army()
        ids = army._swarm.deploy_swarms(req.count, req.rank, req.division,
                                        {"anonymity_mode": req.anonymity_mode})
        return {"deployed": ids, "count": len(ids)}

    class TaskReq(BaseModel):
        agent_id: str
        task: dict

    @app.post("/army/task")
    def execute_task(req: TaskReq):
        army = get_army()
        return army._swarm.execute_task(req.agent_id, req.task)

    @app.get("/army/stats")
    def army_stats():
        army = get_army()
        return army._swarm.get_stats()

    # ── Intelligence / Reverse Engineering ──────────────────────
    class AnalyzeReq(BaseModel):
        path: str
        type: str = "binary"  # binary, wasm, js, exe

    @app.post("/analysis/binary")
    def analyze_binary(req: AnalyzeReq):
        result = _pipeline.analyze(req.path, req.type)
        return result

    @app.post("/analysis/wasm")
    def analyze_wasm(req: AnalyzeReq):
        result = _pipeline.analyze(req.path, "wasm")
        return result

    class HookReq(BaseModel):
        target: str
        script: str

    @app.post("/instrument/hook")
    def instrument(req: HookReq):
        try:
            pid = int(req.target)
            return _pipeline.instrument(pid, req.script)
        except ValueError:
            return _pipeline.instrument(req.target, req.script)

    @app.get("/analysis/status")
    def analysis_status():
        return _pipeline.describe()

    # ── Configuration ───────────────────────────────────────────
    @app.get("/config")
    def get_config():
        cfg_path = Path(__file__).parent.parent / "config" / "browser.json"
        if cfg_path.exists():
            try:
                return json.loads(cfg_path.read_text())
            except Exception: pass
        return {}

    @app.post("/config")
    def set_config(data: dict):
        cfg_path = Path(__file__).parent.parent / "config" / "browser.json"
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(json.dumps(data, indent=2))
        # Restart engine with new config
        global _engine
        with _engine_lock:
            _engine = create_engine(data)
        return {"ok": True, "config": data}


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("BROWSER_PORT", "8180"))
        print(f"[knight-shade] Starting Browser API on :{port}")
        print(f"[knight-shade] Session: {get_engine().session_id}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[knight-shade] FastAPI not available")
