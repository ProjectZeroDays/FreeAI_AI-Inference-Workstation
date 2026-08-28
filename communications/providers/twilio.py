"""Twilio SMS / Voice / WhatsApp provider for FreeAI communications."""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseProvider, _get_key, _load_json


class TwilioProvider(BaseProvider):
    PROVIDER_ID = "twilio"
    PROVIDER_NAME = "Twilio"
    PROVIDER_TYPE = "sms"
    REQUIRES_KEY = True
    DEFAULT_CONFIG = {
        "from_number": "",
        "whatsapp_from": "",
        "voice_enabled": True,
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        keys = _load_json(Path(__file__).parent.parent.parent / "config" / "twilio.json")
        self._account_sid = keys.get("account_sid") or os.environ.get("TWILIO_ACCOUNT_SID", "")
        self._auth_token = keys.get("auth_token") or os.environ.get("TWILIO_AUTH_TOKEN", "")
        self._api_key = keys.get("api_key") or os.environ.get("TWILIO_API_KEY", "")
        self._api_secret = keys.get("api_secret") or os.environ.get("TWILIO_API_SECRET", "")
        self._from_number = config.get("from_number", "") if config else ""

    def connect(self) -> bool:
        if not self._account_sid or not self._auth_token:
            self._last_error = "No Twilio credentials configured"
            self._connected = False
            return False
        try:
            import base64
            creds = f"{self._account_sid}:{self._auth_token}"
            encoded = base64.b64encode(creds.encode()).decode()
            req = urllib.request.Request(
                f"https://api.twilio.com/2010-04-01/Accounts/{self._account_sid}.json",
                headers={"Authorization": f"Basic {encoded}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data.get("sid"):
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

    def send(self, recipient: str, content: str, channel: str = "sms", **kwargs) -> Dict[str, Any]:
        if not self._connected:
            self.connect()
        if not self._connected:
            return {"ok": False, "error": self._last_error}

        if channel == "whatsapp":
            from_number = self.config.get("whatsapp_from", f"whatsapp:{self._from_number}")
            url_path = "Messages.json"
        else:
            from_number = self._from_number
            url_path = "Messages.json"

        if not from_number:
            return {"ok": False, "error": "No from_number configured"}

        payload = {
            "From": from_number,
            "To": f"whatsapp:{recipient}" if channel == "whatsapp" else recipient,
            "Body": content,
        }

        try:
            data = json.dumps(payload).encode()
            import base64
            creds = f"{self._account_sid}:{self._auth_token}"
            encoded = base64.b64encode(creds.encode()).decode()
            req = urllib.request.Request(
                f"https://api.twilio.com/2010-04-01/Accounts/{self._account_sid}/{url_path}",
                data=data,
                headers={"Authorization": f"Basic {encoded}", "Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                self._messages_sent += 1
                return {"ok": True, "sid": result.get("sid"), "channel": channel}
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
            import base64
            creds = f"{self._account_sid}:{self._auth_token}"
            encoded = base64.b64encode(creds.encode()).decode()
            req = urllib.request.Request(
                f"https://api.twilio.com/2010-04-01/Accounts/{self._account_sid}/Messages.json?Limit={limit}",
                headers={"Authorization": f"Basic {encoded}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                messages = []
                for m in data.get("messages", []):
                    messages.append({
                        "sid": m.get("sid"),
                        "from": m.get("from"),
                        "to": m.get("to"),
                        "body": m.get("body", "")[:200],
                        "timestamp": m.get("date_created", ""),
                        "direction": m.get("direction"),
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
            "messages_sent": self._messages_sent,
            "messages_received": self._messages_received,
            "last_error": self._last_error,
            "type": self.PROVIDER_TYPE,
            "channels": ["sms", "whatsapp", "voice"],
        }

    def send_voice(self, recipient: str, text: str, **kwargs) -> Dict:
        if not self._connected:
            self.connect()
        if not self._connected:
            return {"ok": False, "error": self._last_error}
        try:
            import base64
            creds = f"{self._account_sid}:{self._auth_token}"
            encoded = base64.b64encode(creds.encode()).decode()
            payload = f"From={self._from_number}&To={recipient}&Url=http://demo.twilio.com/docs/voice.xml"
            req = urllib.request.Request(
                f"https://api.twilio.com/2010-04-01/Accounts/{self._account_sid}/Calls.json",
                data=payload.encode(),
                headers={"Authorization": f"Basic {encoded}", "Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                self._messages_sent += 1
                return {"ok": True, "call_sid": json.loads(resp.read().decode()).get("sid")}
        except Exception as e:
            return {"ok": False, "error": str(e)}
