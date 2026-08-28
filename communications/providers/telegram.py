"""Telegram Bot API provider for FreeAI communications."""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseProvider, _get_key, _load_json


class TelegramProvider(BaseProvider):
    PROVIDER_ID = "telegram"
    PROVIDER_NAME = "Telegram"
    PROVIDER_TYPE = "messaging"
    REQUIRES_KEY = True
    DEFAULT_CONFIG = {
        "poll_interval": 5,
        "allowed_chats": [],
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self._bot_token = _get_key("telegram", "TELEGRAM_BOT_TOKEN")
        self._base_url = f"https://api.telegram.org/bot{self._bot_token}" if self._bot_token else ""
        self._webhook_url = config.get("webhook_url", "") if config else ""
        self._allowed_chats = config.get("allowed_chats", []) if config else []
        self._last_update_id = 0

    def connect(self) -> bool:
        if not self._bot_token:
            self._last_error = "No Telegram bot token configured"
            self._connected = False
            return False
        try:
            req = urllib.request.Request(
                f"{self._base_url}/getMe",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get("ok") and data.get("result"):
                    self._connected = True
                    self._last_error = None
                    self._bot_name = data["result"].get("username", "")
                    return True
        except urllib.error.HTTPError as e:
            self._last_error = f"Bot token invalid: {e.code}"
            self._connected = False
        except Exception as e:
            self._last_error = str(e)
            self._connected = False
        return False

    def send(self, recipient: str, content: str, **kwargs) -> Dict[str, Any]:
        if not self._connected:
            self.connect()
        if not self._connected:
            return {"ok": False, "error": self._last_error}

        chat_id = recipient
        parse_mode = kwargs.get("parse_mode", "HTML")
        disable_notification = kwargs.get("disable_notification", False)

        try:
            payload = json.dumps({
                "chat_id": chat_id,
                "text": content,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification,
            }).encode()
            req = urllib.request.Request(
                f"{self._base_url}/sendMessage",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                self._messages_sent += 1
                return {"ok": True, "message_id": result.get("result", {}).get("message_id"), "result": result}
        except urllib.error.HTTPError as e:
            self._last_error = f"Send failed: {e.code}"
            return {"ok": False, "error": self._last_error}
        except Exception as e:
            self._last_error = str(e)
            return {"ok": False, "error": str(e)}

    def receive(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self._connected:
            self.connect()
        if not self._connected:
            return []

        try:
            url = f"{self._base_url}/getUpdates?offset={self._last_update_id + 1}&limit={limit}&timeout=0"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                if not data.get("ok"):
                    return []
                messages = []
                for update in data.get("result", []):
                    self._last_update_id = max(self._last_update_id, update.get("update_id", 0))
                    msg = update.get("message", {})
                    chat = msg.get("chat", {})
                    from_user = msg.get("from", {})
                    messages.append({
                        "id": msg.get("message_id"),
                        "chat_id": chat.get("id"),
                        "chat_title": chat.get("title", from_user.get("username", "")),
                        "from": from_user.get("username", ""),
                        "text": msg.get("text", ""),
                        "timestamp": msg.get("date", ""),
                        "type": "message",
                    })
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
            "bot_name": getattr(self, "_bot_name", None),
            "messages_sent": self._messages_sent,
            "messages_received": self._messages_received,
            "last_error": self._last_error,
            "type": self.PROVIDER_TYPE,
            "webhook_url": self._webhook_url,
        }

    def set_webhook(self, url: str) -> Dict:
        self._webhook_url = url
        try:
            payload = json.dumps({"url": url}).encode()
            req = urllib.request.Request(
                f"{self._base_url}/setWebhook",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read().decode())
                return {"ok": result.get("ok"), "result": result.get("result")}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete_webhook(self) -> Dict:
        try:
            req = urllib.request.Request(
                f"{self._base_url}/deleteWebhook",
                data=json.dumps({"drop_pending_updates": True}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read().decode())
                self._webhook_url = ""
                return {"ok": result.get("ok")}
        except Exception as e:
            return {"ok": False, "error": str(e)}
