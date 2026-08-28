"""Gmail / OAuth2 provider for FreeAI communications."""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseProvider, _get_key, _load_json


class GmailProvider(BaseProvider):
    PROVIDER_ID = "gmail"
    PROVIDER_NAME = "Gmail"
    PROVIDER_TYPE = "email"
    REQUIRES_KEY = True
    DEFAULT_CONFIG = {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com",
        "use_app_password": True,
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        keys = _load_json(Path(__file__).parent.parent.parent / "config" / "gmail.json")
        self._email = config.get("email") or keys.get("email") or os.environ.get("GMAIL_EMAIL", "")
        self._app_password = (
            config.get("app_password")
            or keys.get("app_password")
            or os.environ.get("GMAIL_APP_PASSWORD", "")
        )
        self._oauth_token = keys.get("oauth_token") or os.environ.get("GMAIL_OAUTH_TOKEN", "")
        self._smtp_host = config.get("smtp_host", "smtp.gmail.com") if config else "smtp.gmail.com"
        self._smtp_port = config.get("smtp_port", 587) if config else 587

    def connect(self) -> bool:
        if not self._email or not (self._app_password or self._oauth_token):
            self._last_error = "No Gmail credentials configured"
            self._connected = False
            return False
        try:
            import smtplib
            server = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=5)
            server.starttls()
            server.login(self._email, self._app_password or self._oauth_token)
            server.quit()
            self._connected = True
            self._last_error = None
            return True
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

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self._email
            msg["To"] = recipient
            msg.attach(MIMEText(content, "html" if html else "plain"))

            server = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10)
            server.starttls()
            server.login(self._email, self._app_password or self._oauth_token)
            server.sendmail(self._email, [recipient], msg.as_string())
            server.quit()
            self._messages_sent += 1
            return {"ok": True, "recipient": recipient, "subject": subject}
        except Exception as e:
            self._last_error = str(e)
            return {"ok": False, "error": str(e)}

    def receive(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self._connected:
            self.connect()
        if not self._connected:
            return []
        try:
            import imaplib
            imap = imaplib.IMAP4_SSL(self.config.get("imap_host", "imap.gmail.com"), timeout=5)
            imap.login(self._email, self._app_password or self._oauth_token)
            imap.select("INBOX")
            _, data = imap.search(None, "UNSEEN")
            ids = data[0].split() if data[0] else []
            messages = []
            for id in ids[-limit:]:
                _, msg_data = imap.fetch(id, "(RFC822)")
                import email
                msg = email.message_from_bytes(msg_data[0][1])
                messages.append({
                    "from": msg.get("From", ""),
                    "subject": msg.get("Subject", ""),
                    "date": msg.get("Date", ""),
                    "preview": (msg.get_payload(decode=True) or b"")[:200].decode("utf-8", errors="replace"),
                    "type": "email",
                })
            imap.close()
            imap.logout()
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
            "email": self._email,
            "messages_sent": self._messages_sent,
            "messages_received": self._messages_received,
            "last_error": self._last_error,
            "type": self.PROVIDER_TYPE,
        }
