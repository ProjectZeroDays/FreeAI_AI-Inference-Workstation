"""Shared communication API layer — unified interface for all providers.

Provides a single entry point for all FreeAI clients (hermes, opencode,
mimocode, jcode, openclaw, freecode) to send/receive messages through
any configured communication channel.
"""
import json
import os
import time
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from .providers.base import BaseProvider


CONFIG_DIR = Path(__file__).parent.parent / "config"
COMMUNICATIONS_CONFIG_PATH = CONFIG_DIR / "communications.json"


class CommunicationsHub:
    """Central hub managing all communication providers."""

    PROVIDER_REGISTRY = {
        "sendgrid": "communications.providers.sendgrid.SendGridProvider",
        "twilio": "communications.providers.twilio.TwilioProvider",
        "telegram": "communications.providers.telegram.TelegramProvider",
        "whatsapp": "communications.providers.whatsapp.WhatsAppProvider",
        "signal": "communications.providers.signal.SignalProvider",
        "gmail": "communications.providers.gmail.GmailProvider",
        "hermes": "communications.providers.hermes.HermesProvider",
    }

    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}
        self._lock = threading.Lock()
        self._message_log: List[Dict] = []
        self._log_lock = threading.Lock()
        self._config = self._load_config()

    def _load_config(self) -> Dict:
        if COMMUNICATIONS_CONFIG_PATH.exists():
            try:
                return json.loads(COMMUNICATIONS_CONFIG_PATH.read_text())
            except (json.JSONDecodeError, OSError):
                pass
        return {"providers": {}, "global": {"max_log_entries": 500}}

    def _save_config(self) -> None:
        COMMUNICATIONS_CONFIG_PATH.write_text(
            json.dumps(self._config, indent=2), encoding="utf-8"
        )

    def register_provider(self, provider_id: str, config: Optional[Dict] = None) -> bool:
        """Register and instantiate a provider by ID."""
        if provider_id not in self.PROVIDER_REGISTRY:
            return False
        try:
            module_path, class_name = self.PROVIDER_REGISTRY[provider_id].rsplit(".", 1)
            import importlib
            module = importlib.import_module(module_path)
            provider_cls = getattr(module, class_name)
            provider = provider_cls(config=config)
            with self._lock:
                self._providers[provider_id] = provider
            return True
        except Exception:
            return False

    def get_provider(self, provider_id: str) -> Optional[BaseProvider]:
        with self._lock:
            return self._providers.get(provider_id)

    def list_providers(self) -> List[Dict]:
        results = []
        with self._lock:
            for pid, prov in self._providers.items():
                results.append(prov.to_dict())
        return results

    def health_all(self) -> Dict[str, Dict]:
        results = {}
        with self._lock:
            for pid, prov in self._providers.items():
                results[pid] = prov.health_check()
        return results

    def send(self, provider_id: str, recipient: str, content: str,
             **kwargs) -> Dict[str, Any]:
        """Send a message through the specified provider."""
        with self._lock:
            provider = self._providers.get(provider_id)
        if not provider:
            return {"ok": False, "error": f"Provider '{provider_id}' not registered"}
        result = provider.send(recipient, content, **kwargs)
        entry = {
            "ts": int(time.time()),
            "provider": provider_id,
            "recipient": recipient,
            "content": content[:200],
            "result": result,
        }
        with self._log_lock:
            self._message_log.insert(0, entry)
            max_entries = self._config.get("global", {}).get("max_log_entries", 500)
            if len(self._message_log) > max_entries:
                self._message_log = self._message_log[:max_entries]
        return result

    def receive(self, provider_id: str, limit: int = 20) -> List[Dict]:
        with self._lock:
            provider = self._providers.get(provider_id)
        if not provider:
            return []
        return provider.receive(limit)

    def test_all(self) -> Dict[str, Dict]:
        """Connect and test all providers."""
        results = {}
        for pid in self.PROVIDER_REGISTRY:
            if pid not in self._providers:
                self.register_provider(pid)
            prov = self._providers.get(pid)
            if prov:
                prov.connect()
                results[pid] = prov.health_check()
        return results

    def get_message_log(self, limit: int = 50) -> List[Dict]:
        with self._log_lock:
            return self._message_log[:limit]

    def clear_log(self) -> int:
        with self._log_lock:
            count = len(self._message_log)
            self._message_log.clear()
            return count


# Module-level singleton
_hub: Optional[CommunicationsHub] = None
_hub_lock = threading.Lock()


def get_hub() -> CommunicationsHub:
    global _hub
    with _hub_lock:
        if _hub is None:
            _hub = CommunicationsHub()
            _hub._auto_register()
        return _hub


def _init_hub():
    """Initialize and return the hub singleton."""
    return get_hub()


def register_providers_from_config(hub: CommunicationsHub) -> List[str]:
    """Auto-register providers from communications.json config."""
    config = hub._load_config()
    registered = []
    for pid, pconfig in config.get("providers", {}).items():
        if pconfig.get("enabled", False):
            if hub.register_provider(pid, pconfig.get("config")):
                registered.append(pid)
    return registered


def list_available_providers() -> List[Dict]:
    """Return metadata about all available provider types."""
    providers = []
    from .providers import sendgrid, twilio, telegram, whatsapp, signal, gmail, hermes
    for mod in [sendgrid, twilio, telegram, whatsapp, signal, gmail, hermes]:
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and issubclass(obj, BaseProvider) and obj.PROVIDER_ID:
                providers.append({
                    "id": obj.PROVIDER_ID,
                    "name": obj.PROVIDER_NAME,
                    "type": obj.PROVIDER_TYPE,
                    "requires_key": obj.REQUIRES_KEY,
                })
    return providers
