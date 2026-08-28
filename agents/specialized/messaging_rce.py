#!/usr/bin/env python3
"""Messaging RCE Agent — with real CVE data from NVD API."""
import json
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Cache for NVD API results
_cve_cache = {}
_cache_lock = threading.Lock()
_CACHE_TTL = 3600  # 1 hour


def _fetch_cve_from_nvd(cve_id):
    """Fetch CVE details from NVD API."""
    cache_key = f"nvd:{cve_id}"
    with _cache_lock:
        if cache_key in _cve_cache:
            entry = _cve_cache[cache_key]
            if time.time() - entry["timestamp"] < _CACHE_TTL:
                return entry["data"]
    
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}&resultsPerPage=1"
    headers = {"Accept": "application/json"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            vulns = data.get("vulnerabilities", [])
            if vulns:
                cve_data = vulns[0].get("cve", {})
                result = {
                    "id": cve_data.get("id", cve_id),
                    "title": cve_data.get("descriptions", [{}])[0].get("value", "")[:100],
                    "severity": _get_severity(cve_data),
                    "published": cve_data.get("publishedDate", ""),
                    "references": [r.get("url", "") for r in cve_data.get("references", [])],
                }
                with _cache_lock:
                    _cve_cache[cache_key] = {"timestamp": time.time(), "data": result}
                return result
    except Exception:
        pass
    return None


def _get_severity(cve_data):
    """Extract severity from CVE data."""
    for metric in cve_data.get("metrics", {}).values():
        for key, val in metric.items():
            if key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                if isinstance(val, list):
                    for v in val:
                        sev = v.get("cvssData", {}).get("baseMetricV3", {}).get("severity", "")
                        if sev:
                            return sev.lower()
                        sev = v.get("cvssData", {}).get("baseMetricV2", {}).get("severity", "")
                        if sev:
                            return sev.lower()
    return "unknown"


class MessagingRCEAgent:
    """Messaging RCE exploit simulation for defensive research."""

    def __init__(self):
        self.sessions = []
        self.primitives = {}
        self._lock = threading.Lock()

    def describe(self):
        return {
            "name": "messaging_rce",
            "description": "Messaging protocol exploit simulation: iMessage, WhatsApp, Signal, Telegram RCE",
            "category": "red_teaming",
            "capabilities": ["imessage_exploit", "whatsapp_exploit", "signal_exploit", "telegram_exploit"],
        }

    def simulate_imessage_exploit(self, target="iphone_user", exploit_type="rce"):
        """Simulate iMessage exploit."""
        return {
            "status": "simulated",
            "target": target,
            "vector": "iMessage media processing",
            "exploit": f"{exploit_type} via crafted image",
            "requirements": ["target must receive iMessage", "iOS vulnerability"],
        }

    def simulate_whatsapp_exploit(self, target="whatsapp_user", exploit_type="rce"):
        """Simulate WhatsApp exploit."""
        return {
            "status": "simulated",
            "target": target,
            "vector": "WhatsApp video/media processing",
            "exploit": f"{exploit_type} via crafted media",
            "requirements": ["target must receive message", "WhatsApp vulnerability"],
        }

    def simulate_signal_exploit(self, target="signal_user", exploit_type="rce"):
        """Simulate Signal exploit."""
        return {
            "status": "simulated",
            "target": target,
            "vector": "Signal media processing",
            "exploit": f"{exploit_type} via crafted attachment",
            "requirements": ["target must receive message", "Signal vulnerability"],
        }

    def simulate_telegram_exploit(self, target="telegram_user", exploit_type="rce"):
        """Simulate Telegram exploit."""
        return {
            "status": "simulated",
            "target": target,
            "vector": "Telegram media/processing",
            "exploit": f"{exploit_type} via crafted message",
            "requirements": ["target must receive message", "Telegram vulnerability"],
        }

    def generate_payload(self, platform="imessage", payload_type="rce"):
        """Generate messaging exploit payload."""
        return {
            "status": "simulated",
            "platform": platform,
            "payload_type": payload_type,
            "format": "crafted_media",
            "content": f"<simulated_{platform}_{payload_type}_payload>",
        }

    def get_cves(self):
        """Return CVE references for messaging vulnerabilities from NVD API."""
        cve_ids = ["CVE-2019-8641", "CVE-2019-8646", "CVE-2019-8647", "CVE-2021-30860", "CVE-2022-2051"]
        results = []
        for cve_id in cve_ids:
            data = _fetch_cve_from_nvd(cve_id)
            if data:
                results.append(data)
            else:
                results.append({
                    "id": cve_id,
                    "title": f"Simulated messaging CVE ({cve_id})",
                    "severity": "critical",
                    "published": "",
                    "references": []
                })
        return results

    def list_primitives(self):
        """Return list of messaging primitives."""
        return ["media_processing", "protocol_parsing", "code_injection", "file_format_abuse"]

    def map_to_exploit(self, primitive):
        """Map primitive to real-world messaging exploit techniques."""
        mappings = {
            "media_processing": ["image parsing RCE", "video codec exploit", "audio file RCE"],
            "protocol_parsing": ["message parsing", "packet manipulation", "protocol violation"],
            "code_injection": ["script injection", "template injection", "format string"],
            "file_format_abuse": ["zip slip", "path traversal", "content type confusion"],
        }
        return mappings.get(primitive, ["generic messaging exploitation"])


# Module-level state for Flask
_exploit_lock = threading.Lock()
_exploit_data = {}
