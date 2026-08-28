"""SendGrid email provider for FreeAI communications."""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseProvider, _get_key, _load_json


class SendGridProvider(BaseProvider):
    PROVIDER_ID = "sendgrid"
    PROVIDER_NAME = "SendGrid"
    PROVIDER_TYPE = "email"
    REQUIRES_KEY = True
    DEFAULT_CONFIG = {
        "from_email": "noreply@freeai.local",
        "from_name": "FreeAI",
        "sandbox_enabled": False,
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self._api_key = _get_key("sendgrid", "SENDGRID_API_KEY", "sendgrid")
        self._templates: List[Dict] = []
        self._templates_path = Path(__file__).parent.parent.parent / "config" / "sendgrid-templates.json"

    def connect(self) -> bool:
        if not self._api_key:
            self._last_error = "No SendGrid API key configured"
            self._connected = False
            return False
        try:
            req = urllib.request.Request(
                "https://api.sendgrid.com/v3/user/account",
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    self._connected = True
                    self._last_error = None
                    return True
        except urllib.error.HTTPError as e:
            self._last_error = f"Auth failed: {e.code} {e.reason}"
            self._connected = False
        except Exception as e:
            self._last_error = str(e)
            self._connected = False
        return False

    def send(self, recipient: str, content: str, subject: str = "FreeAI Notification",
             html: bool = False, **kwargs) -> Dict[str, Any]:
        if not self._connected:
            self.connect()
        if not self._connected:
            return {"ok": False, "error": self._last_error}

        payload = {
            "personalizations": [{"to": [{"email": recipient}]}],
            "from": {"email": self.config.get("from_email", "noreply@freeai.local"),
                     "name": self.config.get("from_name", "FreeAI")},
            "subject": subject,
            "content": [{"type": "text/html" if html else "text/plain", "value": content}],
        }
        if self.config.get("sandbox_enabled"):
            payload["_sandbox"] = True

        try:
            data = json.dumps(payload).encode()
            req = urllib.request.Request(
                "https://api.sendgrid.com/v3/mail/send",
                data=data,
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                self._messages_sent += 1
                return {"ok": True, "message_id": f"sg-{int(time.time())}", "status": resp.status}
        except urllib.error.HTTPError as e:
            self._last_error = f"Send failed: {e.code}"
            return {"ok": False, "error": self._last_error}
        except Exception as e:
            self._last_error = str(e)
            return {"ok": False, "error": str(e)}

    def receive(self, limit: int = 20) -> List[Dict[str, Any]]:
        return []

    def health_check(self) -> Dict[str, Any]:
        self.connect()
        return {
            "provider": self.PROVIDER_ID,
            "connected": self._connected,
            "messages_sent": self._messages_sent,
            "last_error": self._last_error,
            "type": self.PROVIDER_TYPE,
        }

    def test_send(self, to_email: str, subject: str = "FreeAI Test", content: str = "Test email from FreeAI") -> Dict:
        return self.send(to_email, content, subject=subject, html=False)
