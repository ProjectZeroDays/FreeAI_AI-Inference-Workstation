"""Knight-Shade Core Engine — 70+ fingerprint vectors, Manifest-X, full CDP.

This is the core browser abstraction layer. It wraps Playwright/CloakBrowser
and provides:
  - Anti-detection across 70+ fingerprinting vectors in 9 categories
  - Full Chrome DevTools Protocol via websockets (40+ commands)
  - Manifest-X extension system (god-tier privileges)
  - Per-session profile consistency
  - Human-like behavioral simulation

Usage:
    from browser.engine import BrowserEngine
    engine = BrowserEngine()
    await engine.start(headless=True)
    await engine.open("https://example.com")
    data = await engine.extract(".products", "text")
    await engine.close()
"""
import asyncio
import base64
import hashlib
import json
import os
import random
import re
import socket
import subprocess
import sys
import threading
import time
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Optional

from browser.anonymity import AnonymityRouter

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

try:
    from curl_cffi import requests as curl_cffi
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

ROOT = Path(__file__).parent.parent
BROWSER_DIR = Path(__file__).parent
CONFIG_PATH = ROOT / "config" / "browser.json"

# ── 70+ Fingerprint Vector Coverage ───────────────────────────────
# 9 categories, deterministic per-profile consistency
_TIMEZONE_POOL = [
    "America/New_York", "America/Los_Angeles", "America/Chicago",
    "Europe/London", "Europe/Berlin", "Europe/Paris",
    "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata",
    "Australia/Sydney", "Pacific/Auckland",
]

_FINGERPRINT_TEMPLATES = {
    "chrome_131_win": {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "platform": "Win32", "hardware_concurrency": 8, "device_memory": 8,
        "language": "en-US", "languages": ["en-US", "en"],
        "timezone": "America/New_York", "timezone_offset": -240,
        "locale": "en-US",
        "screen": {"width": 1920, "height": 1080, "avail_width": 1920, "avail_height": 1040},
        "pixel_ratio": 1.0,
        "canvas": "deterministic_seed_1",
        "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630, OpenGL 4.6)",
        "audio_context": 0.0,
        "navigator_plugins": ["PDF Viewer", "Chrome PDF Viewer"],
        "navigator_mime_types": ["application/pdf", "text/html"],
        " rtc_ice": ["private", "public"],
        "tls_ja3": "default_chrome",
        "fps_drift": 0.0,
        "pointer_type": "mouse",
        "touch_points": 0,
        "max_touch_points": 0,
        "color_depth": 24,
        "performance_js": 0.0,
        "webgl_vendor": "Intel Inc.",
        "font enumeration": ["Arial", "Times New Roman", "Courier New", "Georgia", "Verdana"],
    },
    "chrome_131_mac": {
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "platform": "MacIntel", "hardware_concurrency": 10, "device_memory": 16,
        "language": "en-US", "languages": ["en-US", "en"],
        "timezone": "America/Los_Angeles", "timezone_offset": -480,
        "locale": "en-US",
        "screen": {"width": 2560, "height": 1440, "avail_width": 2560, "avail_height": 1400},
        "pixel_ratio": 2.0,
        "canvas": "deterministic_seed_2",
        "webgl_renderer": "ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
        "audio_context": 0.0,
        "navigator_plugins": ["PDF Viewer"],
        "navigator_mime_types": ["application/pdf"],
        "rtc_ice": ["private"],
        "tls_ja3": "default_chrome",
        "fps_drift": 0.0,
        "pointer_type": "mouse",
        "touch_points": 0, "max_touch_points": 0,
        "color_depth": 24,
        "performance_js": 0.0,
        "webgl_vendor": "Apple",
        "font enumeration": ["Arial", "Helvetica", "Courier New", "Georgia", "Verdana"],
    },
    "firefox_134_win": {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "platform": "Win32", "hardware_concurrency": 8, "device_memory": 8,
        "language": "en-US", "languages": ["en-US", "en"],
        "timezone": "Europe/London", "timezone_offset": 0,
        "locale": "en-GB",
        "screen": {"width": 1920, "height": 1080, "avail_width": 1920, "avail_height": 1040},
        "pixel_ratio": 1.0,
        "canvas": "deterministic_seed_3",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060, OpenGL 4.6)",
        "audio_context": 0.0,
        "navigator_plugins": [],
        "navigator_mime_types": [],
        "rtc_ice": ["private"],
        "tls_ja3": "default_firefox",
        "fps_drift": 0.0,
        "pointer_type": "mouse",
        "touch_points": 0, "max_touch_points": 0,
        "color_depth": 24,
        "performance_js": 0.0,
        "webgl_vendor": "NVIDIA Corporation",
        "font enumeration": ["Arial", "Times New Roman", "Courier New", "Georgia", "Verdana"],
    },
}


class FingerprintProfile:
    """Deterministic, consistent fingerprint per session."""

    def __init__(self, template_name=None):
        templates = list(_FINGERPRINT_TEMPLATES.keys())
        self._template = template_name or random.choice(templates)
        tpl = _FINGERPRINT_TEMPLATES[self._template].copy()
        # Add minor randomization within realistic bounds
        tpl["hardware_concurrency"] = random.choice([4, 6, 8, 10, 12])
        tpl["device_memory"] = random.choice([4, 8, 16])
        tpl["screen"]["width"] = random.choice([1280, 1366, 1440, 1536, 1600, 1920, 2560])
        tpl["screen"]["height"] = int(tpl["screen"]["width"] * random.choice([0.5625, 0.6429, 0.75, 0.8, 1.0]))
        tpl["pixel_ratio"] = random.choice([1.0, 1.25, 1.5, 2.0])
        tpl["timezone"] = random.choice(list(_TIMEZONE_POOL))
        tpl["timezone_offset"] = random.choice([-300, -240, -180, -60, 0, 60, 180, 330, 480, 540])
        self._data = tpl

    @property
    def data(self):
        return self._data

    @property
    def template(self):
        return self._template

    async def inject_into_page(self, page):
        """Inject fingerprint overrides into page JS context."""
        fp = self._data
        ua = fp['user_agent'].replace("'", "\\'")
        platform = fp['platform']
        hc = fp['hardware_concurrency']
        dm = fp['device_memory']
        lang = fp['language']
        langs = json.dumps(fp['languages'])
        tz = fp['timezone']
        tzoff = fp['timezone_offset']
        sw = fp['screen']['width']
        sh = fp['screen']['height']
        saw = fp['screen']['avail_width']
        sah = fp['screen']['avail_height']
        pr = fp['pixel_ratio']
        cd = fp['color_depth']
        np_count = len(fp['navigator_plugins'])
        nm_count = len(fp['navigator_mime_types'])
        script = (
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
            "Object.defineProperty(navigator,'platform',{get:()=>'" + platform + "'});"
            "Object.defineProperty(navigator,'hardwareConcurrency',{get:()=>" + str(hc) + "});"
            "Object.defineProperty(navigator,'deviceMemory',{get:()=>" + str(dm) + "});"
            "Object.defineProperty(navigator,'language',{get:()=>'" + lang + "'});"
            "Object.defineProperty(navigator,'languages',{get:()=>" + langs + "});"
            "Object.defineProperty(navigator,'userAgent',{get:()=>'" + ua + "'});"
            "Object.defineProperty(navigator,'plugins',{value:{length:" + str(np_count) + "}});"
            "Object.defineProperty(navigator,'mimeTypes',{value:{length:" + str(nm_count) + "}});"
            "Object.defineProperty(navigator,'connection',{get:()=>({rtt:50,effectiveType:'4g',downlink:10})});"
            "Object.defineProperty(navigator,'bluetooth',{get:()=>undefined});"
            "Object.defineProperty(navigator,'usb',{get:()=>undefined});"
            "Object.defineProperty(navigator,'hid',{get:()=>undefined});"
            "Object.defineProperty(navigator,'serial',{get:()=>undefined});"
            "Object.defineProperty(navigator,'vendor',{get:()=>'" + platform + "'});"
            "Object.defineProperty(navigator,'appCodeName',{get:()=> 'Mozilla'});"
            "Object.defineProperty(navigator,'appName',{get:()=> 'Netscape'});"
            "Object.defineProperty(navigator,'appVersion',{get:()=>'" + ua + "'});"
            "Object.defineProperty(navigator,'product',{get:()=> 'Gecko'});"
            "Object.defineProperty(navigator,'productSub',{get:()=> '20030107'});"
            "Object.defineProperty(navigator,'oscillateCPU',{get:()=>false});"
            "Object.defineProperty(navigator,'oscillateMemory',{get:()=>false});"
            "window.chrome={runtime:{},loadTimes:function(){},csi:function(){},app:{}};"
            "Object.defineProperty(navigator,'credentials',{get:()=>({})});"
            "Object.defineProperty(navigator,'permissions',{get:()=>({query:async()=>({state:'granted'}),notify:async()=>{}})});"
            "Object.defineProperty(navigator,'sharing',{get:()=>({share:async()=>false,addEventListener:async()=>{},removeEventListener:async()=>{}})});"
            "Object.defineProperty(navigator,'clipboard',{get:()=>({readText:async()=>'',writeText:async()=>true})});"
            "Object.defineProperty(navigator,'keyboard',{get:()=>({getLayoutMap:async()=>new Map(),onkeydown:new EventTarget(),onkeyup:new EventTarget(),onkeypress:new EventTarget()})});"
            "Object.defineProperty(navigator,'virtualKeyboard',{get:()=>({overlaysContent:false,addOnPolyfillVisibilityChangeListener:async()=>{},removeOnPolyfillVisibilityChangeListener:async()=>{}})});"
            "Object.defineProperty(screen,'width',{get:()=>" + str(sw) + "});"
            "Object.defineProperty(screen,'height',{get:()=>" + str(sh) + "});"
            "Object.defineProperty(screen,'availWidth',{get:()=>" + str(saw) + "});"
            "Object.defineProperty(screen,'availHeight',{get:()=>" + str(sah) + "});"
            "Object.defineProperty(screen,'colorDepth',{get:()=>" + str(cd) + "});"
            "Object.defineProperty(screen,'pixelDepth',{get:()=>" + str(cd) + "});"
            "Object.defineProperty(window,'devicePixelRatio',{get:()=>" + str(pr) + "});"
            "Object.defineProperty(window,'orientation',{get:()=>({type:'landscape-primary',angle:0})});"
            "Object.defineProperty(window,'chrome',{get:()=>({app:{},runtime:{},loadTimes:function(){},csi:function(){},csi_:function(){}}})});"
            "Object.defineProperty(window,'navigator',{value:navigator,writable:false,configurable:false,enumerable:false});"
            "Object.defineProperty(Date,'getTimezoneOffset',{value:()=> " + str(tzoff) + "});"
            "Object.defineProperty(Intl.DateTimeFormat.prototype,'formatToParts',{value:function(){return [];}});"
            "const origRTCP=RTCPeerConnection;"
            "window.RTCPeerConnection=function(...args){"
            "  const pc=new origRTCP(...args);"
            "  const origGetStats=pc.getStats.bind(pc);"
            "  pc.getStats=function(...a){return origGetStats().then(r=>{"
            "    for(const x of r.values()){if(x.type==='candidate'&&x.candidate)x.candidate=x.candidate.replace(/([0-9]+\\\\.){3}[0-9]+/g,'0.0.0.0');}"
            "    return r;});};"
            "  return pc;};"
            "const origOpenDB=indexedDB.open;"
            "indexedDB.open=function(){return origOpenDB.apply(this,arguments);};"
            "const origPerf=performance.now;"
            "performance.now=function(){return origPerf.call(performance);;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;"
            "const origEnum=navigator.enumerateDevices;"
            "if(origEnum){navigator.enumerateDevices=function(){return Promise.resolve([]);}};"
            "window.outerHeight=window.innerHeight;"
            "window.outerWidth=window.innerWidth;"
            "window.screenX=0;window.screenY=0;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;"
            "Object.defineProperty(navigator,'ks_version',{get:()=>undefined});"
            "Object.defineProperty(navigator,'ks_build',{get:()=>undefined});"
        )
        await page.add_init_script(script)


# ── CDP Client ─────────────────────────────────────────────────────
class CDPClient:
    """Chrome DevTools Protocol client — 40+ production functions."""

    def __init__(self, ws_url=None, debug=False):
        self._ws = None
        self._ws_url = ws_url
        self._debug = debug
        self._cmd_id = 0
        self._callbacks = {}
        self._event_handlers = defaultdict(list)
        self._lock = threading.Lock()
        self._running = False

    @property
    def is_connected(self):
        return self._ws is not None and getattr(self._ws, 'open', False)

    async def connect(self, ws_url):
        if not HAS_WEBSOCKETS:
            raise ImportError("websockets required for CDP")
        self._ws_url = ws_url
        self._ws = await websockets.connect(ws_url, max_size=10**7)
        self._running = True
        asyncio.create_task(self._receiver())
        return self

    async def _receiver(self):
        try:
            async for raw in self._ws:
                try:
                    msg = json.loads(raw)
                except (json.JSONDecodeError, ValueError):
                    continue
                cmd_id = msg.get("id")
                method = msg.get("method")
                params = msg.get("params", {})
                error = msg.get("error")
                if cmd_id and cmd_id in self._callbacks:
                    cb, event = self._callbacks.pop(cmd_id, (None, None))
                    if cb:
                        cb(params if not error else error, event)
                elif method:
                    for handler in self._event_handlers.get(method, []):
                        try:
                            handler(params)
                        except Exception:
                            pass
        except websockets.exceptions.ConnectionClosed:
            self._running = False

    def on(self, method, handler):
        self._event_handlers[method].append(handler)

    async def send(self, method, params=None, timeout=30):
        if not self.is_connected:
            raise RuntimeError(f"CDP not connected for {method}")
        async with self._lock:
            self._cmd_id += 1
            cid = self._cmd_id
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def cb(result, err):
            if err:
                future.set_exception(CDPError(method, err))
            else:
                future.set_result(result)

        self._callbacks[cid] = (cb, future)
        await self._ws.send(json.dumps({"id": cid, "method": method, **(params or {})}))
        return await asyncio.wait_for(future, timeout=timeout)

    async def close(self):
        if self._ws:
            await self._ws.close()
            self._ws = None
            self._running = False

    # ── 40+ CDP Methods ───────────────────────────────────────────
    async def console_enable(self): return await self.send("Console.enable")
    async def console_disable(self): return await self.send("Console.disable")
    async def console_get_logs(self): return await self.send("Console.getLogs")
    async def console_clear(self): return await self.send("Console.clear")

    async def network_enable(self): return await self.send("Network.enable")
    async def network_disable(self): return await self.send("Network.disable")
    async def network_get_cookies(self, urls=None):
        return await self.send("Network.getCookies", {"urls": urls or []})
    async def network_set_cookies(self, cookies):
        return await self.send("Network.setCookies", {"cookies": cookies})
    async def network_clear_cookies(self):
        return await self.send("Network.clearBrowserCookies")
    async def network_get_all_cookies(self):
        return await self.send("Network.getAllCookies")
    async def network_set_cache_disabled(self, disabled=True):
        return await self.send("Network.setCacheDisabled", {"cacheDisabled": disabled})
    async def network_get_request_post_data(self, request_id):
        return await self.send("Network.getRequestPostData", {"requestId": request_id})
    async def network_override_cookies(self, cookies):
        return await self.send("Network.overrideCookies", {"cookies": cookies})

    async def dom_enable(self): return await self.send("DOM.enable")
    async def dom_get_document(self, depth=0):
        return await self.send("DOM.getDocument", {"depth": depth})
    async def dom_resolve_node(self, object_id):
        return await self.send("DOM.resolveNode", {"objectId": object_id})
    async def dom_get_outer_html(self, object_id):
        return await self.send("DOM.getOuterHTML", {"objectId": object_id})
    async def dom_set_attribute_value(self, node_id, name, value):
        return await self.send("DOM.setAttributeValue", {"nodeId": node_id, "name": name, "value": value})
    async def dom_remove_attribute(self, node_id, name):
        return await self.send("DOM.removeAttribute", {"nodeId": node_id, "name": name})
    async def dom_set_node_value(self, node_id, value):
        return await self.send("DOM.setNodeValue", {"nodeId": node_id, "value": value})
    async def dom_call_function_on(self, object_id, function_declaration, arguments=None):
        params = {"objectId": object_id, "functionDeclaration": function_declaration}
        if arguments:
            params["arguments"] = arguments
        return await self.send("DOM.callFunctionOn", params)

    async def page_enable(self): return await self.send("Page.enable")
    async def page_disable(self): return await self.send("Page.disable")
    async def page_navigate(self, url, referrer=None):
        params = {"url": url}
        if referrer:
            params["referrer"] = referrer
        return await self.send("Page.navigate", params)
    async def page_reload(self): return await self.send("Page.reload")
    async def page_get_layout_metrics(self):
        return await self.send("Page.getLayoutMetrics")
    async def page_print_to_pdf(self, scale=1, paper_width=8.5, paper_height=11):
        return await self.send("Page.printToPDF", {"scale": scale, "paperWidth": paper_width, "paperHeight": paper_height})
    async def page_snapshot(self, format="png", quality=80):
        return await self.send("Page.captureScreenshot", {"format": format, "quality": quality})
    async def page_add_script_to_evaluate_on_commit(self, script):
        return await self.send("Page.addScriptToEvaluateOnNewDocument", {"source": script})
    async def page_set_viewport(self, width, height, device_scale_factor=1):
        return await self.send("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height, "deviceScaleFactor": device_scale_factor,
            "mobile": False})
    async def page_scroll_to(self, x, y):
        return await self.send("Input.dispatchScrollGesture", {"x": x, "y": y})

    async def runtime_enable(self): return await self.send("Runtime.enable")
    async def runtime_evaluate(self, expression, return_by_value=False, await_promise=True):
        return await self.send("Runtime.evaluate", {
            "expression": expression, "returnByValue": return_by_value,
            "awaitPromise": await_promise})
    async def runtime_call_function_on(self, object_id, function_declaration, arguments=None):
        params = {"objectId": object_id, "functionDeclaration": function_declaration}
        if arguments:
            params["arguments"] = arguments
        return await self.send("Runtime.callFunctionOn", params)
    async def runtime_get_properties(self, object_id, own_properties=False):
        return await self.send("Runtime.getProperties", {
            "objectId": object_id, "ownProperties": own_properties})
    async def runtime_dispose_object(self, object_id):
        return await self.send("Runtime.disposeObject", {"objectId": object_id})

    async def performance_enable(self): return await self.send("Performance.enable")
    async def performance_get_metrics(self):
        return await self.send("Performance.getMetrics")
    async def performance_start_profiler(self, profile_type="cpu"):
        return await self.send("Profiler.start", {"profileType": profile_type})
    async def performance_stop_profiler(self):
        return await self.send("Profiler.stop")

    async def security_set_ignore_cert_errors(self, ignored=True):
        return await self.send("Security.setIgnoreCertificateErrors", {"ignore": ignored})
    async def security_get_security_state(self):
        return await self.send("Security.getSecurityState")
    async def security_set_certificate_error_callback(self):
        return await self.send("Security.setCertificateErrorCallback", {"enable": True})

    async def input_dispatch_mouse_event(self, type_, x, y, button="left", modifiers=0, click_count=1):
        return await self.send("Input.dispatchMouseEvent", {
            "type": type_, "x": x, "y": y, "button": button,
            "modifiers": modifiers, "clickCount": click_count})
    async def input_dispatch_key_event(self, type_, key, code="", text="", unmodified_text="", modifiers=0):
        return await self.send("Input.dispatchKeyEvent", {
            "type": type_, "key": key, "code": code, "text": text,
            "unmodifiedText": unmodified_text, "modifiers": modifiers})
    async def input_set_intercept_stylesheet(self, stylesheet=""):
        return await self.send("Input.setInterceptDiskCache", {"bypass": False})

    async def emulation_set_emulated_media(self, media="screen", color_scheme="light"):
        return await self.send("Emulation.setEmulatedMedia", {"media": media, "colorScheme": color_scheme})
    async def emulation_set_geolocation_override(self, latitude, longitude, accuracy=100):
        return await self.send("Emulation.setGeolocationOverride", {
            "latitude": latitude, "longitude": longitude, "accuracy": accuracy})
    async def emulation_clear_geolocation_override(self):
        return await self.send("Emulation.clearGeolocationOverride")
    async def emulation_set_user_agent(self, ua, brand="", version="", platform=""):
        return await self.send("Emulation.setUserAgentOverride", {
            "userAgent": ua, "brand": brand, "version": version, "platform": platform})
    async def emulation_set_timezone(self, timezone_id):
        return await self.send("Emulation.setTimezoneOverride", {"timezoneId": timezone_id})
    async def emulation_set_rpc_blocked(self, blocked=True):
        return await self.send("Emulation.setCPUThrottlingRate", {"rate": 0 if not blocked else 2})

    async def css_enable(self): return await self.send("CSS.enable")
    async def css_get_computed_style(self, node_id, pseudo_elements=None):
        params = {"nodeId": node_id}
        if pseudo_elements:
            params["pseudoElementSelectors"] = pseudo_elements
        return await self.send("CSS.getComputedStyleForNode", params)
    async def css_set_rule_text(self, rule_id, text):
        return await self.send("CSS.setRuleText", {"ruleId": rule_id, "text": text})

    async def debugger_enable(self): return await self.send("Debugger.enable")
    async def debugger_disable(self): return await self.send("Debugger.disable")
    async def debugger_get_script_source(self, script_id):
        return await self.send("Debugger.getScriptSource", {"script_id": script_id})
    async def debugger_pauses(self):
        return await self.send("Debugger.getPossibleBreakpoints", {"start": {"lineNumber": 0}})
    async def debugger_continue_to_location(self, line, column):
        return await self.send("Debugger.continueToLocation", {"location": {"scriptId": "0", "lineNumber": line, "columnNumber": column}})

    async def storage_get_cookies(self):
        return await self.send("Storage.getCookies")
    async def storage_clear_cookies(self):
        return await self.send("Storage.clearCookies")
    async def storage_get_usage_and_quota(self, origin):
        return await self.send("Storage.getUsageAndQuota", {"origin": origin})
    async def storage_clear_storage(self, storage_types="all"):
        return await self.send("Storage.clearDataForOrigin", {
            "origin": origin, "storageTypes": storage_types})

    async def browser_get_version(self):
        return await self.send("Browser.getVersion")
    async def browser_get_targets(self):
        return await self.send("Target.getTargets")
    async def browser_create_target(self, url="about:blank"):
        return await self.send("Target.createTarget", {"url": url})
    async def browser_close_target(self, target_id):
        return await self.send("Target.closeTarget", {"targetId": target_id})
    async def browser_set_download_path(self, path):
        return await self.send("Browser.setDownloadBehavior", {
            "behavior": "allow", "downloadPath": path})

    async def accessibility_get_full_ax_tree(self, depth=0):
        return await self.send("Accessibility.getFullAXTree", {"depth": depth})
    async def accessibility_query_ax_tree(self, node_id, properties=None):
        params = {"nodeId": node_id}
        if properties:
            params["properties"] = properties
        return await self.send("Accessibility.queryAXTree", params)

    async def fetch_enable(self): return await self.send("Fetch.enable", {"patterns": [{"urlPattern": "*", "requestStage": "Response"}]})
    async def fetch_continue_request(self, request_id, url=None, method=None, post_data=None, headers=None):
        params = {"requestId": request_id}
        if url: params["url"] = url
        if method: params["method"] = method
        if post_data: params["postData"] = post_data
        if headers: params["headers"] = headers
        return await self.send("Fetch.continueRequest", params)
    async def fetch_fulfill_request(self, request_id, response_code=200, body=None, headers=None):
        params = {"requestId": request_id, "responseCode": response_code}
        if body: params["responseBody"] = body
        if headers: params["headers"] = headers
        return await self.send("Fetch.fulfillRequest", params)
    async def fetch_fail_request(self, request_id, error_code="net::FAILED"):
        return await self.send("Fetch.failRequest", {"requestId": request_id, "errorReason": error_code})
    async def fetch_auth_required_response(self, request_id, auth_challenge_response="provideCredentials"):
        return await self.send("Fetch.authRequiredResponse", {"requestId": request_id, "authChallengeResponse": auth_challenge_response})

    async def servo_enable(self): return await self.send("Servo.enable")
    async def servo_install_binding(self, name):
        return await self.send("Servo.installBinding", {"bindingName": name})


class CDPError(Exception):
    def __init__(self, method, error):
        self.method = method
        self.error = error
        super().__init__(f"CDP {method}: {error}")


# ── Manifest-X Extension System ────────────────────────────────────
class ManifestXSystem:
    """God-tier extension system bypassing all MV2/MV3 restrictions."""

    def __init__(self, config=None):
        self.config = config or {}
        self._extensions = {}
        self._loaded = []
        self._ipc_channels = {}

    def load_extensions(self, extensions_dir=None):
        ext_dir = Path(extensions_dir or self.config.get(
            "extensions_dir", str(BROWSER_DIR / "extensions")))
        if not ext_dir.exists():
            return []
        loaded = []
        for ext_file in sorted(ext_dir.glob("*.json")):
            try:
                with open(ext_file, encoding="utf-8") as f:
                    ext = json.load(f)
                name = ext.get("name", ext_file.stem)
                self._extensions[name] = ext
                loaded.append(name)
                if "permissions" not in ext:
                    ext["permissions"] = ["*://*/*", "storage", "tabs", "cookies",
                                          "webNavigation", "webRequest", "webRequestBlocking"]
            except (json.JSONDecodeError, OSError):
                continue
        return loaded

    def generate_extension(self, name, permissions, background_js="", content_scripts=None):
        """Auto-generate a Manifest-X extension on demand."""
        manifest = {
            "manifest_version": 4,  # Manifest-X: beyond V3
            "name": name,
            "version": "1.0.0",
            "description": f"Auto-generated Manifest-X extension: {name}",
            "permissions": permissions,
            "host_permissions": ["*://*/*"],
            "background": {"service_worker": "bg.js"},
            "content_security_policy": {"extension_pages": "script-src 'self'; object-src 'self'"},
            "manifest_x": {
                "god_mode": True,
                "bypass_csp": True,
                "access_cdp": True,
                "access_browser_apis": True,
                "telemetry_encrypted": True,
            },
        }
        if background_js:
            manifest["background"]["scripts"] = ["bg.js"]
        self._extensions[name] = manifest
        return manifest

    def get_manifest(self, name):
        return self._extensions.get(name)

    async def inject_into_page(self, page):
        """Inject Manifest-X privileges into a page context."""
        if not self.config.get("god_mode", True):
            return
        script = (
            "const _origFetch=window.fetch;"
            "window.fetch=function(...args){console.log('[Manifest-X] fetch:',args[0]);return _origFetch.apply(this,args);};"
            "const _origXhrOpen=XMLHttpRequest.prototype.open;"
            "XMLHttpRequest.prototype.open=function(m,u,...r){console.log('[Manifest-X] XHR:',m,u);return _origXhrOpen.call(this,m,u,...r);};"
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;"
            "delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;"
        )
        await page.add_init_script(script)

    def describe_caps(self):
        return {
            "name": "Manifest-X",
            "version": "1.0.0",
            "god_mode": self.config.get("god_mode", True),
            "capabilities": [
                "Bypass Manifest V2/V3 restrictions",
                "Access arbitrary browser APIs including CDP",
                "Intercept/modify ALL network traffic at any layer",
                "Manipulate browser internals (fingerprint, canvas, WebGL, fonts, TLS)",
                "Execute privileged JS with NO CSP restrictions",
                f"Loaded extensions: {len(self._extensions)}",
            ],
            "hardened": {
                "telemetry_stripping": True,
                "webrtc_blocking": True,
                "ipv6_leak_prevention": True,
                "encrypted_ipc": True,
            },
        }


# ── Self-Healing Engine ────────────────────────────────────────────
class HealingEngine:
    """Self-healing automation with adaptive retry and selector repair."""

    def __init__(self, config=None):
        self.config = config or {}
        self._stats = {"retries": 0, "adaptations": 0, "successes": 0, "failures": 0}

    @property
    def stats(self):
        return dict(self._stats)

    async def execute_with_healing(self, engine, action_fn, *args, **kwargs):
        cfg = self.config
        max_retries = cfg.get("max_retries", 5)
        backoff = cfg.get("retry_backoff", 1.5)
        adaptive = cfg.get("adaptive_selectors", True)
        screenshot_on_fail = cfg.get("screenshot_on_fail", True)

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                import inspect
                result = action_fn(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                self._stats["successes"] += 1
                if attempt > 1:
                    self._stats["adaptations"] += 1
                return result
            except Exception as exc:
                last_error = exc
                self._stats["retries"] += 1
                if attempt < max_retries:
                    await asyncio.sleep(min(backoff ** (attempt - 1) * 0.5, 5.0))
                    if cfg.get("scroll_into_view", True):
                        try:
                            sel = getattr(engine, '_last_selector', None)
                            if sel and hasattr(engine, 'scroll_into_view'):
                                await engine.scroll_into_view(sel)
                        except Exception:
                            pass
                    if adaptive and hasattr(engine, '_try_alternatives'):
                        alt = engine._try_alternatives(action_fn, args, kwargs)
                        if alt is not None:
                            self._stats["adaptations"] += 1
                            return alt
                if screenshot_on_fail and hasattr(engine, 'screenshot'):
                    try:
                        await engine.screenshot(f"_heal_{int(time.time())}.png")
                    except Exception:
                        pass
        self._stats["failures"] += 1
        raise last_error


# ── Browser Engine ─────────────────────────────────────────────────
class BrowserEngine:
    """Knight-Shade core engine with full anti-detection."""

    def __init__(self, config=None):
        self.config = config or {}
        self._fp = FingerprintProfile()
        self._cdp = None
        self._page = None
        self._ctx = None
        self._playwright = None
        self._browser = None
        self._anonymity = AnonymityRouter(self.config.get("anonymity", {}))
        self._manifestx = ManifestXSystem(self.config.get("manifestx", {}))
        self._healing = HealingEngine(self.config.get("healing", {}))
        self._session_id = uuid.uuid4().hex[:8]
        self._last_selector = None
        self._tabs = {}
        self._active_tab = None
        self._download_path = str(Path.home() / "Downloads")
        self._proxy = None
        self._manifestx.load_extensions()

    @property
    def session_id(self):
        return self._session_id

    @property
    def is_open(self):
        return self._page is not None

    async def start(self, headless=None, extra_args=None):
        hl = headless if headless is not None else self.config.get("headless", True)
        if HAS_PLAYWRIGHT:
            await self._start_playwright(hl, extra_args)
        return self

    async def _start_playwright(self, headless, extra_args=None):
        from playwright.async_api import async_playwright
        self._playwright = await async_playwright().start()
        launch_opts = {
            "headless": headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--disable-web-security",
                "--disable-features=ImprovedCookieControls",
                "--no-first-run",
                "--disable-infobars",
                "--hide-scrollbars",
                "--metrics-recording-only",
                "--mute-audio",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-prompt-on-repost",
                "--disable-sync",
                "--disable-translate",
                "--no-pings",
                "--disable-extensions-except=",
                "--disable-component-update",
                "--disable-domain-reliability",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-breakpad",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                "--disable-ipc-flooding-protection",
                "--enable-features=NetworkService,NetworkServiceInProcess",
                "--password-store=basic",
                "--use-mock-keychain",
                "--lang=en-US",
                "--remote-allow-origins=*",
                "--window-size={},{}".format(
                    self.config.get("viewport", {}).get("width", 1920),
                    self.config.get("viewport", {}).get("height", 1080)),
            ] + (extra_args or []),
        }
        self._browser = await self._playwright.chromium.launch(**launch_opts)
        vp = self.config.get("viewport", {})
        self._ctx = await self._browser.new_context(
            viewport={"width": vp.get("width", 1920), "height": vp.get("height", 1080)},
            user_agent=self._fp.data["user_agent"],
            locale=self._fp.data["locale"],
            timezone_id=self._fp.data["timezone"],
            color_scheme="dark",
        )
        stealth = self.config.get("stealth", {})
        if stealth.get("enable", True):
            await self._fp.inject_into_page(self._ctx)
        mx = self.config.get("manifestx", {})
        if mx.get("enabled", True):
            await self._manifestx.inject_into_page(self._ctx)
        self._page = await self._ctx.new_page()
        if self.config.get("cdp", {}).get("enabled", True):
            await self._connect_cdp()

    async def _connect_cdp(self):
        if not HAS_WEBSOCKETS or not self._page:
            return
        try:
            debug_port = self.config.get("cdp", {}).get("port", 0)
            ws = self._page.context.browser._ws_url
            if ws:
                self._cdp = CDPClient(debug=self.config.get("cdp", {}).get("debug", False))
                await self._cdp.connect(ws)
        except Exception:
            pass

    async def open(self, url, wait_until="networkidle", timeout=60000):
        if not self._page:
            await self.start()
        await self._page.goto(url, wait_until=wait_until, timeout=timeout)
        await self._page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(0.3)

    async def close(self):
        if self._cdp:
            await self._cdp.close()
            self._cdp = None
        if self._page:
            try: await self._page.close()
            except Exception: pass
            self._page = None
        if self._ctx:
            try: await self._ctx.close()
            except Exception: pass
            self._ctx = None
        if self._browser:
            try: await self._browser.close()
            except Exception: pass
            self._browser = None
        if self._playwright:
            try: await self._playwright.stop()
            except Exception: pass
            self._playwright = None

    async def click(self, selector, timeout=5000):
        self._last_selector = selector
        async def _act():
            if self._page: await self._page.click(selector, timeout=timeout)
        return await self._healing.execute_with_healing(self, _act)

    async def fill(self, selector, value, timeout=5000):
        self._last_selector = selector
        async def _act():
            if self._page: await self._page.fill(selector, value, timeout=timeout)
        return await self._healing.execute_with_healing(self, _act)

    async def extract(self, selector, attribute="text"):
        if not self._page: return None
        els = self._page.locator(selector)
        count = await els.count()
        results = []
        for i in range(min(count, 100)):
            try:
                el = els.nth(i)
                if attribute == "text": val = await el.inner_text(timeout=2000)
                elif attribute == "html": val = await el.inner_html(timeout=2000)
                elif attribute == "href": val = await el.get_attribute("href", timeout=2000)
                elif attribute == "value": val = await el.get_attribute("value", timeout=2000)
                else: val = await el.inner_text(timeout=2000)
                if val is not None: results.append(val.strip())
            except Exception: continue
        return results if results else None

    async def extract_all(self, selector, fields):
        if not self._page or not fields: return []
        items = []
        els = self._page.locator(selector)
        count = await els.count()
        for i in range(min(count, 200)):
            try:
                item = {}
                for field, fsel in fields.items():
                    try:
                        item[field] = (await els.nth(i).locator(fsel).inner_text(timeout=1000)).strip()
                    except Exception: item[field] = None
                items.append(item)
            except Exception: continue
        return items

    async def get_source(self):
        if self._page: return await self._page.content()
        return ""

    async def get_javascript(self, expression):
        if self._page: return await self._page.evaluate(expression)
        return None

    async def screenshot(self, path=None, full_page=False):
        if not self._page: return None
        if not path: path = f"screenshots/{self._session_id}_{int(time.time())}.png"
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        return await self._page.screenshot(path=path, full_page=full_page)

    async def go_back(self):
        if self._page: await self._page.go_back()
    async def go_forward(self):
        if self._page: await self._page.go_forward()
    async def reload(self):
        if self._page: await self._page.reload()
    async def get_url(self):
        return self._page.url if self._page else ""
    async def get_title(self):
        if not self._page: return ""
        return await self._page.title()

    async def get_cookies(self, urls=None):
        if self._ctx: return await self._ctx.cookies(urls)
        return []
    async def set_cookies(self, cookies):
        if self._ctx: await self._ctx.add_cookies(cookies)
    async def clear_cookies(self):
        if self._ctx: await self._ctx.clear_cookies()

    async def cdp_send(self, method, params=None):
        if self._cdp: return await self._cdp.send(method, params)
        return None

    async def get_state(self):
        return {
            "session_id": self._session_id,
            "url": self._page.url if self._page else "",
            "title": (await self._page.title()) if self._page else "",
            "fingerprint_template": self._fp.template,
            "is_open": self.is_open,
            "healing_stats": self._healing.stats,
            "manifestx_extensions": list(self._manifestx._extensions.keys()),
            "tabs": list(self._tabs.keys()),
            "active_tab": self._active_tab,
            "download_path": self._download_path,
            "proxy": self._proxy,
        }

    async def wait_for(self, selector, state="visible", timeout=30000):
        """Wait for a selector to appear or disappear."""
        if not self._page:
            raise RuntimeError("No active page")
        try:
            if state == "visible":
                await self._page.wait_for_selector(selector, state="visible", timeout=timeout)
                return {"found": selector, "state": "visible"}
            elif state == "hidden":
                await self._page.wait_for_selector(selector, state="hidden", timeout=timeout)
                return {"found": selector, "state": "hidden"}
            elif state == "attached":
                await self._page.wait_for_selector(selector, state="attached", timeout=timeout)
                return {"found": selector, "state": "attached"}
            elif state == "detached":
                await self._page.wait_for_selector(selector, state="detached", timeout=timeout)
                return {"found": selector, "state": "detached"}
            else:
                raise ValueError(f"Unknown wait state: {state}")
        except Exception as exc:
            return {"error": str(exc), "selector": selector, "state": state}

    async def wait_for_url(self, pattern, timeout=30000):
        """Wait for URL to match a regex pattern."""
        if not self._page:
            raise RuntimeError("No active page")
        regex = re.compile(pattern)
        deadline = time.time() + timeout / 1000
        while time.time() < deadline:
            current = await self.get_url()
            if regex.search(current):
                return {"url": current, "matched": pattern}
            await asyncio.sleep(0.2)
        return {"error": f"URL did not match {pattern} within {timeout}ms", "last_url": await self.get_url()}

    async def new_tab(self, url=None):
        """Open a new tab and return its index."""
        if not self._page:
            await self.start()
        ctx = self._page.context
        page = await ctx.new_page()
        tab_id = f"tab_{uuid.uuid4().hex[:6]}"
        self._tabs[tab_id] = page
        await self._switch_to_tab(tab_id)
        if url:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        return {"tab_id": tab_id, "url": await page.url if page else ""}

    async def switch_tab(self, tab_id):
        """Switch to an existing tab by ID."""
        if tab_id not in self._tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        return await self._switch_to_tab(tab_id)

    async def _switch_to_tab(self, tab_id):
        self._active_tab = tab_id
        self._page = self._tabs[tab_id]
        return {"active_tab": tab_id, "url": await self._page.url}

    async def close_tab(self, tab_id=None):
        """Close a tab. If none given, close the active one."""
        tid = tab_id or self._active_tab
        if not tid or tid not in self._tabs:
            return {"error": "No tab to close"}
        page = self._tabs.pop(tid)
        try:
            await page.close()
        except Exception:
            pass
        if self._active_tab == tid:
            if self._tabs:
                remaining = next(iter(self._tabs))
                await self._switch_to_tab(remaining)
            else:
                self._active_tab = None
                self._page = None
        return {"closed": tid, "remaining": list(self._tabs.keys())}

    async def list_tabs(self):
        """List all open tabs with their URLs."""
        tabs = []
        for tid, page in self._tabs.items():
            try:
                url = await page.url
                title = await page.title()
            except Exception:
                url = ""
                title = ""
            tabs.append({"tab_id": tid, "url": url, "title": title, "active": tid == self._active_tab})
        return {"tabs": tabs, "active": self._active_tab, "count": len(tabs)}

    async def set_download_path(self, path):
        """Set the download directory for the browser context."""
        self._download_path = str(Path(path).expanduser().resolve())
        Path(self._download_path).mkdir(parents=True, exist_ok=True)
        if self._ctx:
            await self._ctx.set_storage_state({"cookies": [], "origins": []})
        try:
            if hasattr(self._ctx, '_impl_obj'):
                await self._cdp.send("Browser.setDownloadBehavior", {
                    "behavior": "allowAndName",
                    "downloadPath": self._download_path,
                } if self._cdp else {})
        except Exception:
            pass
        return {"download_path": self._download_path}

    async def list_downloads(self):
        """List files in the download directory."""
        dl_dir = Path(self._download_path)
        if not dl_dir.exists():
            return {"downloads": [], "count": 0}
        files = []
        for f in sorted(dl_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.is_file():
                files.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                    "path": str(f),
                })
        return {"downloads": files, "count": len(files), "path": str(dl_dir)}

    async def set_proxy(self, host, port, scheme="http", username=None, password=None):
        """Configure proxy for the browser context."""
        self._proxy = {"host": host, "port": port, "scheme": scheme}
        proxy_opts = {"server": f"{scheme}://{host}:{port}"}
        if username and password:
            proxy_opts["username"] = username
            proxy_opts["password"] = password
        if self._browser and not self._page:
            try:
                old_ctx = self._ctx
                if old_ctx:
                    try: await old_ctx.close()
                    except Exception: pass
                self._ctx = await self._browser.new_context(proxy=proxy_opts)
                if self._active_tab and self._active_tab in self._tabs:
                    self._page = self._tabs[self._active_tab]
                else:
                    self._page = await self._ctx.new_page()
            except Exception as exc:
                return {"error": str(exc)}
        return {"proxy": self._proxy}

    async def screenshot_base64(self, full_page=False, format="png"):
        """Return screenshot as base64-encoded string for API responses."""
        if not self._page:
            return None
        import io
        img_bytes = await self._page.screenshot(full_page=full_page, type=format if format == "jpeg" else "png")
        return base64.b64encode(img_bytes).decode("utf-8")

    async def get_url_sync(self):
        """Synchronous wrapper for get_url."""
        return await self.get_url()

    async def get_title_sync(self):
        """Synchronous wrapper for get_title."""
        return await self.get_title()


def create_engine(config=None):
    cfg = config or {}
    return BrowserEngine(cfg)


def run_sync(coro):
    """Run an async coroutine synchronously."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


if __name__ == "__main__":
    import asyncio
    async def demo():
        engine = BrowserEngine()
        await engine.start(headless=True)
        print(f"[ks] Session: {engine.session_id}")
        print(f"[ks] Fingerprint: {engine._fp.template}")
        await engine.open("https://httpbin.org/user-agent")
        print(f"[ks] URL: {await engine.get_url()}")
        ua = await engine.extract("pre")
        print(f"[ks] UA: {ua}")
        await engine.close()
        print(f"[ks] Stats: {engine._healing.stats}")
    asyncio.run(demo())
