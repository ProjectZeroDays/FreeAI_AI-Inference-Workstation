"""WhatsApp Business Cloud API provider for FreeAI communications."""
import json
import logging
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseProvider, _get_key, _load_json


class WhatsAppProvider(BaseProvider):
    PROVIDER_ID = "whatsapp"
    PROVIDER_NAME = "WhatsApp Business"
    PROVIDER_TYPE = "messaging"
    REQUIRES_KEY = True
    DEFAULT_CONFIG = {
        "phone_number_id": "",
        "business_account_id": "",
        "message_template_lang": "en",
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        keys = _load_json(Path(__file__).parent.parent.parent / "config" / "whatsapp.json")
        self._access_token = (
            config.get("access_token")
            or keys.get("access_token")
            or os.environ.get("WHATSAPP_ACCESS_TOKEN", "")
        )
        self._phone_number_id = config.get("phone_number_id") or keys.get("phone_number_id", "")
        self._business_account_id = config.get("business_account_id") or keys.get("business_account_id", "")
        self._api_version = "v18.0"

    def connect(self) -> bool:
        if not self._access_token or not self._phone_number_id:
            self._last_error = "No WhatsApp credentials configured"
            self._connected = False
            return False
        try:
            req = urllib.request.Request(
                f"https://graph.facebook.com/{self._api_version}/{self._phone_number_id}?fields=id,name&access_token={self._access_token}",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get("id"):
                    self._connected = True
                    self._last_error = None
                    return True
        except urllib.error.HTTPError as e:
            self._last_error = f"Auth failed: {e.code}"
            self._connected = False
        except Exception as e:
            self._last_error = str(e)
            self._connected = False
        return False

    def send(self, recipient: str, content: str, template: Optional[str] = None,
             **kwargs) -> Dict[str, Any]:
        if not self._connected:
            self.connect()
        if not self._connected:
            return {"ok": False, "error": self._last_error}

        try:
            if template:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": recipient,
                    "type": "template",
                    "template": {
                        "name": template,
                        "language": {"code": self.config.get("message_template_lang", "en")},
                    },
                }
            else:
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": recipient,
                    "type": "text",
                    "text": {"body": content},
                }

            data = json.dumps(payload).encode()
            req = urllib.request.Request(
                f"https://graph.facebook.com/{self._api_version}/{self._phone_number_id}/messages",
                data=data,
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                self._messages_sent += 1
                msg_id = result.get("messages", [{}])[0].get("id", "") if result.get("messages") else ""
                return {"ok": True, "message_id": msg_id}
        except urllib.error.HTTPError as e:
            self._last_error = f"Send failed: {e.code}"
            return {"ok": False, "error": self._last_error}
        except Exception as e:
            self._last_error = str(e)
            logging.getLogger(__name__).exception("WhatsApp error")
            return {"ok": False, "error": "An error occurred"}

    def receive(self, limit: int = 20) -> List[Dict[str, Any]]:
        return []

    def health_check(self) -> Dict[str, Any]:
        self.connect()
        return {
            "provider": self.PROVIDER_ID,
            "connected": self._connected,
            "phone_number_id": self._phone_number_id,
            "messages_sent": self._messages_sent,
            "messages_received": self._messages_received,
            "last_error": self._last_error,
            "type": self.PROVIDER_TYPE,
        }
