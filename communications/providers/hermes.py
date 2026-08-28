"""Hermes native messaging provider — bridges FreeAI with Hermes agent platform."""
import json
import logging
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseProvider, _load_json


class HermesProvider(BaseProvider):
    PROVIDER_ID = "hermes"
    PROVIDER_NAME = "Hermes"
    PROVIDER_TYPE = "messaging"
    REQUIRES_KEY = False
    DEFAULT_CONFIG = {
        "port": 8090,
        "host": "127.0.0.1",
        "health_check_interval": 30,
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self._port = config.get("port", 8090) if config else 8090
        self._host = config.get("host", "127.0.0.1") if config else "127.0.0.1"
        self._hermes_config_path = Path(__file__).parent.parent.parent / "config" / "hermes.json"

    def connect(self) -> bool:
        try:
            req = urllib.request.Request(
                f"http://{self._host}:{self._port}/health",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    self._connected = True
                    self._last_error = None
                    return True
        except Exception:
            self._connected = False
            self._last_error = "Hermes not reachable"
        return False

    def send(self, recipient: str, content: str, **kwargs) -> Dict[str, Any]:
        if not self._connected:
            self.connect()
        if not self._connected:
            return {"ok": False, "error": self._last_error}
        try:
            payload = json.dumps({
                "recipient": recipient,
                "content": content,
                "source": "freeai",
                "timestamp": int(time.time()),
            }).encode()
            req = urllib.request.Request(
                f"http://{self._host}:{self._port}/api/messages/send",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                self._messages_sent += 1
                return {"ok": True, "hermes_id": result.get("id")}
        except urllib.error.HTTPError as e:
            self._connected = False
            self._last_error = f"Hermes error: {e.code}"
            return {"ok": False, "error": self._last_error}
        except Exception as e:
            self._last_error = str(e)
            logging.getLogger(__name__).exception("Hermes error")
            return {"ok": False, "error": "An error occurred"}

    def receive(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self._connected:
            self.connect()
        if not self._connected:
            return []
        try:
            req = urllib.request.Request(
                f"http://{self._host}:{self._port}/api/messages?limit={limit}",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                messages = data if isinstance(data, list) else data.get("messages", [])
                self._messages_received += len(messages)
                return messages
        except Exception as e:
            self._last_error = str(e)
            return []

    def health_check(self) -> Dict[str, Any]:
        self.connect()
        return {
            "provider": self.PROVIDER_ID,
            "connected": self._connected,
            "host": f"{self._host}:{self._port}",
            "messages_sent": self._messages_sent,
            "messages_received": self._messages_received,
            "last_error": self._last_error,
            "type": self.PROVIDER_TYPE,
        }
