"""Abstract base class for all communication providers."""
import abc
import json
import os
import time
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional


CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
KEYS_PATH = CONFIG_DIR / "api-keys.json"


def _load_api_keys() -> Dict[str, str]:
    """Load API keys from config/api-keys.json."""
    if KEYS_PATH.exists():
        try:
            data = json.loads(KEYS_PATH.read_text())
            return {k: v for k, v in data.get("keys", {}).items() if isinstance(v, str) and v}
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _get_key(provider: str, env_var: Optional[str] = None, config_key: Optional[str] = None) -> str:
    """Resolve provider API key from env var, config, or API keys store."""
    if env_var and os.environ.get(env_var):
        return os.environ.get(env_var, "")
    if config_key:
        cfg = _load_json(CONFIG_DIR / f"{config_key}.json")
        if cfg and cfg.get("api_key"):
            return cfg["api_key"]
    keys = _load_api_keys()
    return keys.get(provider, "")


def _load_json(path: Path) -> Dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


class BaseProvider(abc.ABC):
    """Base class all communication providers must implement."""

    PROVIDER_ID: str = ""
    PROVIDER_NAME: str = ""
    PROVIDER_TYPE: str = ""  # email | sms | messaging | voice
    REQUIRES_KEY: bool = True
    DEFAULT_CONFIG: Dict[str, Any] = {}

    def __init__(self, config: Optional[Dict] = None):
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self._lock = threading.Lock()
        self._messages_sent: int = 0
        self._messages_received: int = 0
        self._last_error: Optional[str] = None
        self._connected: bool = False

    @abc.abstractmethod
    def connect(self) -> bool:
        """Authenticate and verify connectivity. Return True on success."""
        ...

    @abc.abstractmethod
    def send(self, recipient: str, content: str, **kwargs) -> Dict[str, Any]:
        """Send a message. Return provider-specific response dict."""
        ...

    @abc.abstractmethod
    def receive(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Poll for incoming messages. Return list of message dicts."""
        ...

    @abc.abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return health status dict."""
        ...

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.PROVIDER_ID,
            "name": self.PROVIDER_NAME,
            "type": self.PROVIDER_TYPE,
            "connected": self._connected,
            "messages_sent": self._messages_sent,
            "messages_received": self._messages_received,
            "last_error": self._last_error,
            "config": {k: v for k, v in self.config.items() if k != "api_key"},
        }

    def __repr__(self) -> str:
        status = "connected" if self._connected else "disconnected"
        return f"<{self.PROVIDER_ID} {status}>"
