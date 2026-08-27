"""Knight-Shade MCP Tools — Expose browser capabilities to AI agents."""
import asyncio
import json
from browser.engine import BrowserEngine, create_engine
from browser.army import get_army
from browser.intelligence import IntelligencePipeline

_browser_pipeline = IntelligencePipeline()
_engine = None
_engine_lock = None


def get_engine():
    global _engine
    if _engine is None:
        import threading
        if _engine_lock is None:
            _engine_lock = threading.Lock()
        with _engine_lock:
            if _engine is None:
                _engine = create_engine()
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


TOOL_DEFS = [
    {"name": "browser_open", "description": "Navigate to URL", "params": {"url": "str", "wait_until": "str", "timeout": "int"}},
    {"name": "browser_close", "description": "Close browser", "params": {}},
    {"name": "browser_click", "description": "Click element by selector", "params": {"selector": "str", "timeout": "int"}},
    {"name": "browser_fill", "description": "Fill form field", "params": {"selector": "str", "value": "str"}},
    {"name": "browser_extract", "description": "Extract text/HTML from page", "params": {"selector": "str", "attribute": "str", "limit": "int"}},
    {"name": "browser_screenshot", "description": "Take screenshot", "params": {"path": "str", "full_page": "bool"}},
    {"name": "browser_get_source", "description": "Get page HTML source", "params": {}},
    {"name": "browser_js", "description": "Execute JavaScript", "params": {"expression": "str"}},
    {"name": "browser_cookies", "description": "Get/set/clear cookies", "params": {"action": "str", "cookies": "list"}},
    {"name": "browser_cdp", "description": "Raw CDP command", "params": {"method": "str", "params": "dict"}},
    {"name": "browser_state", "description": "Get browser state", "params": {}},
    {"name": "browser_rotate_tor", "description": "Rotate Tor circuit", "params": {}},
    {"name": "army_deploy", "description": "Deploy N agents", "params": {"count": "int", "rank": "str", "division": "str"}},
    {"name": "army_roster", "description": "List all agents", "params": {}},
    {"name": "army_stats", "description": "Get army statistics", "params": {}},
    {"name": "analysis_binary", "description": "Ghidra binary analysis", "params": {"path": "str", "type": "str"}},
    {"name": "analysis_wasm", "description": "Ghidra Wasm decompilation", "params": {"path": "str"}},
    {"name": "instrument_hook", "description": "Frida process hooking", "params": {"target": "str", "script": "str"}},
]


def register_mcp_tools(server):
    """Register Knight-Shade tools with an MCP server."""
    for tool_def in TOOL_DEFS:
        server.add_tool(tool_def["name"], tool_def["description"])

    @server.tool()
    async def browser_open(url: str, wait_until: str = "networkidle", timeout: int = 60000):
        eng = get_engine()
        _run(eng.open(url, wait_until, timeout))
        return {"url": eng.get_url_sync(), "title": eng.get_title_sync()}

    @server.tool()
    async def browser_close():
        eng = get_engine()
        _run(eng.close())
        return {"status": "closed"}

    @server.tool()
    async def browser_click(selector: str, timeout: int = 5000):
        eng = get_engine()
        _run(eng.click(selector, timeout))
        return {"clicked": selector}

    @server.tool()
    async def browser_fill(selector: str, value: str):
        eng = get_engine()
        _run(eng.fill(selector, value))
        return {"filled": selector}

    @server.tool()
    async def browser_extract(selector: str, attribute: str = "text", limit: int = 50):
        eng = get_engine()
        results = _run(eng.extract(selector, attribute))
        if isinstance(results, list):
            results = results[:limit]
        return {"results": results}

    @server.tool()
    async def browser_screenshot(path: str = None, full_page: bool = False):
        eng = get_engine()
        _run(eng.screenshot(path, full_page))
        return {"screenshot": path or "saved"}

    @server.tool()
    async def browser_get_source():
        eng = get_engine()
        return {"source": _run(eng.get_source())[:5000]}

    @server.tool()
    async def browser_js(expression: str):
        eng = get_engine()
        result = _run(eng.get_javascript(expression))
        return {"result": str(result) if result is not None else None}

    @server.tool()
    async def browser_cookies(action: str = "get", cookies: list = None):
        eng = get_engine()
        if action == "get":
            return {"cookies": _run(eng.get_cookies())}
        elif action == "set":
            _run(eng.set_cookies(cookies or []))
            return {"set": True}
        elif action == "clear":
            _run(eng.clear_cookies())
            return {"cleared": True}

    @server.tool()
    async def browser_cdp(method: str, params: dict = None):
        eng = get_engine()
        return {"result": _run(eng.cdp_send(method, params))}

    @server.tool()
    async def browser_state():
        return await get_engine().get_state()

    @server.tool()
    async def browser_rotate_tor():
        eng = get_engine()
        if hasattr(eng, '_anonymity'):
            return {"rotated": eng._anonymity.rotate_tor_circuit()}
        return {"rotated": False}

    @server.tool()
    async def army_deploy(count: int = 1, rank: str = "E-1", division: str = "operations"):
        army = get_army()
        ids = army._swarm.deploy_swarms(count, rank, division)
        return {"deployed": ids}

    @server.tool()
    async def army_roster():
        army = get_army()
        return {"agents": [a.describe() for a in army._swarm.list_agents()]}

    @server.tool()
    async def army_stats():
        army = get_army()
        return army._swarm.get_stats()

    @server.tool()
    async def analysis_binary(path: str, type: str = "binary"):
        return _browser_pipeline.analyze(path, type)

    @server.tool()
    async def analysis_wasm(path: str):
        return _browser_pipeline.analyze(path, "wasm")

    @server.tool()
    async def instrument_hook(target: str, script: str):
        return _browser_pipeline.instrument(target, script)


if __name__ == "__main__":
    print("[knight-shade-mcp] Tools registered:")
    for t in TOOL_DEFS:
        print(f"  - {t['name']}: {t['description']}")
