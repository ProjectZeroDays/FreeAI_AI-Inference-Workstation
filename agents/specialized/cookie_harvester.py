#!/usr/bin/env python3
"""Cookie Session Agent — cookie sniffing, session harvesting, and cookie crafting."""
import json
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent


class CookieHarvester:
    """Harvests and crafts cookies/sessions via browser engine."""

    def __init__(self, browser_engine=None):
        self.engine = browser_engine
        self.cookies = []
        self.sessions = []

    def describe(self):
        return {
            "name": "cookie_harvester",
            "description": "Cookie sniffing, session harvesting, and cookie crafting via browser engine",
            "category": "red_teaming",
            "capabilities": ["cookie_get", "cookie_set", "session_harvest", "cookie_craft"],
        }

    async def harvest_cookies(self, url):
        """Harvest all cookies for a given URL."""
        if not self.engine:
            return {"error": "No browser engine attached"}
        try:
            cookies = await self.engine.get_cookies(url)
            self.cookies.extend(cookies)
            return {"harvested": len(cookies), "url": url, "cookies": cookies}
        except Exception as e:
            logging.getLogger(__name__).exception("Cookie harvester error")
            return {"error": "An error occurred"}

    async def set_cookies(self, url, cookies):
        """Set cookies for a given URL."""
        if not self.engine:
            return {"error": "No browser engine attached"}
        try:
            await self.engine.set_cookies(url, cookies)
            return {"ok": True, "set": len(cookies)}
        except Exception as e:
            logging.getLogger(__name__).exception("Cookie harvester error")
            return {"error": "An error occurred"}

    def get_cookies(self):
        """Return all harvested cookies."""
        return self.cookies

    def craft_cookie(self, name, value, domain, path="/", max_age=3600, secure=True, http_only=True):
        """Craft a cookie dict for setting."""
        return {
            "name": name, "value": value, "domain": domain, "path": path,
            "secure": secure, "httpOnly": http_only, "sameSite": "Strict",
            "expires": int(time.time()) + max_age,
        }

    def export_netscape(self):
        """Export cookies in Netscape format."""
        lines = ["# Netscape HTTP Cookie File"]
        for c in self.cookies:
            lines.append(f"# http://{c.get('domain','')}{c.get('path','/')}")
            lines.append(f"{c.get('domain','')}\tTrue\t{c.get('path','/')}\t{'TRUE' if c.get('secure') else 'FALSE'}\t{int(c.get('expires',0))}\t{c.get('name','')}\t{c.get('value','')}")
        return "\n".join(lines)

    def export_json(self):
        """Export cookies as JSON."""
        return json.dumps(self.cookies, indent=2)


if __name__ == "__main__":
    agent = CookieHarvester()
    print(json.dumps(agent.describe(), indent=2))
