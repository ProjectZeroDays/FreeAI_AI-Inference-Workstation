"""Knight-Shade / UniverSight — AI-Native Autonomous Browser Automation.

Converges 55+ open-source projects into a unified system for:
- Autonomous, undetectable web interaction
- God-tier extensions via Manifest-X
- Full CDP access (browser-harness cannibalized, 40+ functions)
- Default Tor anonymity (tor_full)
- Self-healing automation
- AI-native design (Agent Zero, MCP, army orchestration)
- Reverse engineering pipeline (Ghidra, Frida, Burp Suite)

Usage:
    from browser import BrowserEngine, get_army, IntelligencePipeline
    engine = BrowserEngine()
    await engine.start(headless=True)
    await engine.open("https://example.com")
    data = await engine.extract(".product", "text")
    await engine.close()
"""
from browser.engine import (
    BrowserEngine, FingerprintProfile, CDPClient, CDPError,
    ManifestXSystem, HealingEngine, create_engine, run_sync,
)
from browser.anonymity import AnonymityRouter
from browser.army import (
    ArmyAgent, SwarmCoordinator, FleetCoordinator,
    get_army, RANKS, DIVISIONS,
)
from browser.intelligence import (
    GhidraAnalyzer, FridaInstrumentor, BurpProxy, IntelligencePipeline,
)
from browser.api import app as browser_app, get_engine as get_browser_engine
from browser.mcp_tools import (
    TOOL_DEFS as BROWSER_TOOLS,
    register_mcp_tools,
)

from browser.extensions import Extension, ExtensionManager, get_manager

__version__ = "2.0.0"
__all__ = [
    "BrowserEngine", "FingerprintProfile", "CDPClient", "CDPError",
    "ManifestXSystem", "HealingEngine", "create_engine", "run_sync",
    "AnonymityRouter",
    "ArmyAgent", "SwarmCoordinator", "FleetCoordinator", "get_army",
    "RANKS", "DIVISIONS",
    "GhidraAnalyzer", "FridaInstrumentor", "BurpProxy", "IntelligencePipeline",
    "browser_app", "get_browser_engine",
    "BROWSER_TOOLS", "register_mcp_tools",
    "Extension", "ExtensionManager", "get_manager",
]
