#!/usr/bin/env python3
"""Messaging RCE Agent — with MITRE ATT&CK mappings and real CVE data."""
import json
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent

MITRE_TECHNIQUES = {
    "messaging_rce": {
        "id": "T1203",
        "name": "Exploitation for Client Execution",
        "tactic": "Execution",
        "description": "Attackers exploit vulnerabilities in messaging protocols and media processing to achieve remote code execution on target devices.",
        "mechanisms": [
            "iMessage: crafted media triggering WebKit or ImageIO vulnerabilities",
            "WhatsApp: video processing exploits in FFmpeg or libav codecs",
            "Signal: message parsing vulnerabilities in cryptographic libraries",
            "Telegram: document parsing exploits in MTProto handling",
            "Steganographic payloads: embedding shellcode in image/audio files"
        ],
        "mitigations": [
            "Keep messaging apps updated to latest versions",
            "Disable automatic media download from unknown contacts",
            "Use sandboxed media processing engines",
            "Implement content-type validation and sanitization",
            "Deploy application whitelisting on mobile devices"
        ]
    }
}

KNOWN_CVES = {
    "messaging_rce": [
        "CVE-2019-8641", "CVE-2019-8646", "CVE-2019-8647",
        "CVE-2021-30860", "CVE-2022-2051"
    ]
}

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
        tech = MITRE_TECHNIQUES["messaging_rce"]
        return {
            "name": "messaging_rce",
            "description": "Messaging protocol exploit simulation: iMessage, WhatsApp, Signal, Telegram RCE",
            "category": "red_teaming",
            "capabilities": ["imessage_exploit", "whatsapp_exploit", "signal_exploit", "telegram_exploit"],
            "mitre_technique": {
                "id": tech["id"],
                "name": tech["name"],
                "tactic": tech["tactic"],
                "description": tech["description"],
                "mechanisms": tech["mechanisms"],
                "mitigations": tech["mitigations"]
            }
        }

    def simulate_imessage_exploit(self, target="iphone_user", exploit_type="rce"):
        """Simulate iMessage exploit with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["messaging_rce"]
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "mitre_technique": tech["name"],
            "target": target,
            "vector": "iMessage media processing",
            "mechanism": tech["mechanisms"][0],
            "exploit_type": exploit_type,
            "exploitation_steps": [
                "Craft malicious image file with embedded exploit payload",
                "Payload targets WebKit rendering engine vulnerability",
                "Send crafted image via iMessage to target device",
                "Target receives message, iOS triggers image processing",
                "Buffer overflow in image decoder triggers memory corruption",
                "ROP chain bypasses ASLR, achieves code execution"
            ],
            "requirements": ["Target must receive iMessage", "iOS version vulnerable to CVE"],
            "example_cve": "CVE-2019-8641 (WebKit integer overflow)"
        }

    def simulate_whatsapp_exploit(self, target="whatsapp_user", exploit_type="rce"):
        """Simulate WhatsApp exploit with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["messaging_rce"]
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "mitre_technique": tech["name"],
            "target": target,
            "vector": "WhatsApp video/media processing",
            "mechanism": tech["mechanisms"][1],
            "exploit_type": exploit_type,
            "exploitation_steps": [
                "Create malformed MP4/3GP video file with crafted headers",
                "Payload targets FFmpeg/libavcodec vulnerability",
                "Send video file via WhatsApp message to target",
                "WhatsApp auto-downloads and previews the video",
                "Memory corruption during video decoding triggers RCE",
                "Attacker gains shell on target device"
            ],
            "requirements": ["Target must receive message", "WhatsApp version vulnerable"],
            "example_cve": "CVE-2019-8646 (FFmpeg heap overflow)"
        }

    def simulate_signal_exploit(self, target="signal_user", exploit_type="rce"):
        """Simulate Signal exploit with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["messaging_rce"]
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "mitre_technique": tech["name"],
            "target": target,
            "vector": "Signal media processing",
            "mechanism": tech["mechanisms"][2],
            "exploit_type": exploit_type,
            "exploitation_steps": [
                "Craft malicious attachment file targeting Signal's media parser",
                "Payload exploits vulnerability in libvpx or WebP decoder",
                "Send crafted file via Signal message to target",
                "Signal processes attachment, triggering decoder bug",
                "Heap corruption achieved via malformed frame data",
                "Control flow hijack leads to code execution"
            ],
            "requirements": ["Target must receive message", "Signal version vulnerable"],
            "example_cve": "CVE-2021-30860 (Libvpx integer overflow)"
        }

    def simulate_telegram_exploit(self, target="telegram_user", exploit_type="rce"):
        """Simulate Telegram exploit with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["messaging_rce"]
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "mitre_technique": tech["name"],
            "target": target,
            "vector": "Telegram media/processing",
            "mechanism": tech["mechanisms"][3],
            "exploit_type": exploit_type,
            "exploitation_steps": [
                "Create malicious document or sticker file",
                "Payload exploits TGS sticker format parser",
                "Send via Telegram message to target",
                "Telegram client parses sticker, triggering vulnerability",
                "Buffer overflow in SVG/PNG processing within TGS",
                "Achieve code execution on target device"
            ],
            "requirements": ["Target must receive message", "Telegram client vulnerable"],
            "example_cve": "CVE-2022-2051 (Telegram file parser)"
        }

    def generate_payload(self, platform="imessage", payload_type="rce"):
        """Generate messaging exploit payload with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["messaging_rce"]
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "mitre_technique": tech["name"],
            "platform": platform,
            "payload_type": payload_type,
            "format": "crafted_media",
            "payload_structure": {
                "imessage": "Malformed HEIC image with crafted EXIF data",
                "whatsapp": "Malformed MP4 with crafted GOP structure",
                "signal": "Corrupted WebP file with oversized frame dimensions",
                "telegram": "Malformed TGS sticker with integer overflow"
            },
            "example_usage": f"tool --platform {platform} --output payload.{platform}"
        }

    def get_cves(self):
        """Return CVE references for messaging vulnerabilities from NVD API."""
        cve_ids = KNOWN_CVES["messaging_rce"]
        results = []
        for cve_id in cve_ids:
            data = _fetch_cve_from_nvd(cve_id)
            if data:
                results.append(data)
            else:
                results.append({
                    "id": cve_id,
                    "title": f"Messaging vulnerability ({cve_id})",
                    "severity": "critical",
                    "published": "",
                    "references": [],
                    "mitre_technique": MITRE_TECHNIQUES["messaging_rce"]["id"]
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
