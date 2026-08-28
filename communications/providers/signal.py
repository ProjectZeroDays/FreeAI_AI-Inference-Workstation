"""Signal Messenger provider (via signal-cli) for FreeAI communications."""
import json
import os
import time
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseProvider, _get_key, _load_json


class SignalProvider(BaseProvider):
    PROVIDER_ID = "signal"
    PROVIDER_NAME = "Signal"
    PROVIDER_TYPE = "messaging"
    REQUIRES_KEY = False
    DEFAULT_CONFIG = {
        "signal_cli_path": "signal-cli",
        "username": "",
        "config_dir": "~/.signal-cli",
        "rest_api": False,
        "rest_port": 8080,
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self._username = config.get("username", "") if config else ""
        self._cli_path = config.get("signal_cli_path", "signal-cli") if config else "signal-cli"
        self._config_dir = config.get("config_dir", "~/.signal-cli") if config else "~/.signal-cli"
        self._rest_api = config.get("rest_api", False) if config else False
        self._rest_port = config.get("rest_port", 8080) if config else 8080
        self._registered = False

    def connect(self) -> bool:
        try:
            result = subprocess.run(
                [self._cli_path, "-c", self._config_dir, "getRegistration"],
                capture_output=True, text=True, timeout=5,
            )
            self._registered = result.returncode == 0
            if self._registered:
                self._connected = True
                self._last_error = None
            else:
                self._last_error = "Signal not registered"
                self._connected = False
        except FileNotFoundError:
            self._last_error = "signal-cli not found — install signal-cli or enable REST mode"
            self._connected = False
        except Exception as e:
            self._last_error = str(e)
            self._connected = False
        return self._connected

    def send(self, recipient: str, content: str, **kwargs) -> Dict[str, Any]:
        if not self._registered:
            self.connect()
        if not self._registered:
            return {"ok": False, "error": self._last_error}

        try:
            args = [self._cli_path, "-c", self._config_dir, "send", "-m", content, recipient]
            result = subprocess.run(args, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                self._messages_sent += 1
                return {"ok": True, "recipient": recipient}
            else:
                self._last_error = result.stderr.strip()
                return {"ok": False, "error": self._last_error}
        except FileNotFoundError:
            return {"ok": False, "error": "signal-cli not found"}
        except Exception as e:
            self._last_error = str(e)
            return {"ok": False, "error": str(e)}

    def receive(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self._registered:
            self.connect()
        if not self._registered:
            return []
        try:
            result = subprocess.run(
                [self._cli_path, "-c", self._config_dir, "receive"],
                capture_output=True, text=True, timeout=10,
            )
            messages = []
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for msg in data.get("messages", []) if isinstance(data, dict) else []:
                        messages.append({
                            "from": msg.get("address", {}).get("number", "unknown"),
                            "text": msg.get("message", {}).get("messageBody", ""),
                            "timestamp": msg.get("dateReceived", ""),
                            "type": "message",
                        })
                except json.JSONDecodeError:
                    messages = [{"text": result.stdout[:200], "from": "unknown", "type": "raw"}]
            self._messages_received += len(messages)
            return messages[:limit]
        except Exception as e:
            self._last_error = str(e)
            return []

    def health_check(self) -> Dict[str, Any]:
        self.connect()
        return {
            "provider": self.PROVIDER_ID,
            "connected": self._connected,
            "registered": self._registered,
            "username": self._username,
            "rest_api": self._rest_api,
            "messages_sent": self._messages_sent,
            "messages_received": self._messages_received,
            "last_error": self._last_error,
            "type": self.PROVIDER_TYPE,
        }

    def register(self, phone_number: str) -> Dict:
        try:
            result = subprocess.run(
                [self._cli_path, "-c", self._config_dir, "register", phone_number, "--remove-if-exists"],
                capture_output=True, text=True, timeout=30,
            )
            self._username = phone_number
            return {"ok": result.returncode == 0, "output": result.stdout, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}
