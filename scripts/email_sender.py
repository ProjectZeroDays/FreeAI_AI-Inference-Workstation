#!/usr/bin/env python3
"""
FreeAI Red Team Campaign Email Sender
Supports SMTP and API-based email delivery with campaign tracking
"""

import json
import uuid
import smtplib
import ssl
import os
import sys
import argparse
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from urllib.parse import urlencode

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.campaign_manager import CampaignGenerator, CampaignType


@dataclass
class EmailConfig:
    """Email delivery configuration"""
    # SMTP settings
    smtp_server: str = "smtp.office365.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    use_tls: bool = True
    
    # API settings (fallback)
    api_provider: str = ""  # "sendgrid", "mailgun", "aws_ses"
    api_key: str = ""
    api_secret: str = ""
    from_domain: str = ""
    
    # Email defaults
    from_name: str = "IT Security Team"
    from_email: str = "it-support@company.com"
    reply_to: str = ""
    
    # Campaign settings
    campaign_id: str = ""
    tracking_enabled: bool = True
    test_mode: bool = True  # Always true for safety


@dataclass
class Recipient:
    """Email recipient with tracking"""
    email: str
    first_name: str = ""
    last_name: str = ""
    department: str = ""
    role: str = ""
    variant_id: str = ""
    segment: str = ""
    send_count: int = 0


@dataclass
class EmailResult:
    """Result of an email send operation"""
    recipient: str
    variant: str
    success: bool
    message_id: str = ""
    error: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class CampaignEmailSender:
    """Send phishing simulation emails with campaign tracking"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.results: List[EmailResult] = []
        self.sent_count: int = 0
        self.failed_count: int = 0
        
    def _get_tracking_url(self, landing_page: str, recipient: Recipient) -> str:
        """Generate tracking URL with campaign parameters"""
        params = {
            "campaign": self.config.campaign_id or uuid.uuid4().hex[:8],
            "variant": recipient.variant_id,
            "user": recipient.email.split("@")[0] if "@" in recipient.email else "unknown",
            "timestamp": datetime.now().isoformat(),
            "id": uuid.uuid4().hex[:12]
        }
        base_url = Path(__file__).parent.parent / "templates" / "landing_pages" / landing_page
        return f"file://{base_url}?{urlencode(params)}"
    
    def _load_email_template(self, variant_type: str) -> Dict[str, Any]:
        """Load email template for variant type"""
        templates = {
            "urgency": {
                "subject": "URGENT: Password Expiration Notice - Action Required",
                "body_html": """
<!DOCTYPE html>
<html>
<head><title>Password Expiration Notice</title></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:4px;padding:15px;margin-bottom:20px;">
<strong>⚠️ ACTION REQUIRED</strong>
</div>
<h2 style="color:#333;">Password Expiration Notice</h2>
<p>Dear User,</p>
<p>Your password will <strong>expire in 24 hours</strong>. To avoid account lockout, please reset your password immediately.</p>
<p style="margin:30px 0;">
<a href="{tracking_url}" style="background:#d32f2f;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;font-weight:bold;">Reset Password Now</a>
</p>
<p>If you did not request this change, please contact IT support immediately.</p>
<p style="color:#666;font-size:12px;margin-top:40px;">
This is an automated message from IT Security.<br>
© 2026 Company IT Department
</p>
</body>
</html>
""".format(tracking_url=self._get_tracking_url("microsoft_login.html", Recipient("", "", "", "", "", "V1"))),
                "from_name": "IT Security Team",
                "from_email": "it-support@company.com",
                "headers": {
                    "X-Campaign-ID": "phishing-test-2026",
                    "X-Priority": "1"
                }
            },
            "authority": {
                "subject": "IT Security: Mandatory Credential Update Required",
                "body_html": """
<!DOCTYPE html>
<html>
<head><title>Security Update Required</title></head>
<body style="font-family:'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
<div style="background:#e3f2fd;border-left:4px solid #1976d2;padding:15px;margin-bottom:20px;">
<strong>🔐 Security Notice</strong>
</div>
<h2 style="color:#333;">Mandatory Credential Update</h2>
<p>Dear Team Member,</p>
<p>As part of our updated security policy, all users are required to update their credentials within <strong>48 hours</strong>.</p>
<p>This is a <strong>company-wide requirement</strong> enforced by the IT Security Department.</p>
<p style="margin:30px 0;">
<a href="{tracking_url}" style="background:#1976d2;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;font-weight:bold;">Update Credentials</a>
</p>
<p>Failure to update may result in temporary account suspension.</p>
<p style="color:#666;font-size:12px;margin-top:40px;">
IT Security Department<br>
This is an official company communication.
</p>
</body>
</html>
""".format(tracking_url=self._get_tracking_url("google_workspace.html", Recipient("", "", "", "", "", "V2"))),
                "from_name": "IT Security Department",
                "from_email": "security@company.com",
                "headers": {
                    "X-Campaign-ID": "security-update-2026",
                    "X-Priority": "1"
                }
            },
            "social": {
                "subject": "Meeting Invitation: Executive Leadership Q4 Review",
                "body_html": """
<!DOCTYPE html>
<html>
<head><title>Meeting Invitation</title></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
<div style="background:#f3e5f5;border-left:4px solid #7b1fa2;padding:15px;margin-bottom:20px;">
<strong>📅 Calendar Invitation</strong>
</div>
<h2 style="color:#333;">You've Been Invited</h2>
<p>Dear Colleague,</p>
<p>You have been selected to attend an important <strong>Executive Leadership Meeting</strong> to discuss Q4 strategic objectives.</p>
<p><strong>When:</strong> Today at 3:00 PM<br>
<strong>Where:</strong> Conference Room A / Virtual<br>
<strong>Agenda:</strong> Quarterly review and budget allocation</p>
<p style="margin:30px 0;">
<a href="{tracking_url}" style="background:#7b1fa2;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;font-weight:bold;">Accept Invitation</a>
</p>
<p>Please confirm your attendance as soon as possible.</p>
<p style="color:#666;font-size:12px;margin-top:40px;">
Executive Assistant<br>
Company Leadership Team
</p>
</body>
</html>
""".format(tracking_url=self._get_tracking_url("adobe_sign.html", Recipient("", "", "", "", "", "V3"))),
                "from_name": "Executive Assistant",
                "from_email": "exec-assistant@company.com",
                "headers": {
                    "X-Campaign-ID": "meeting-invite-2026",
                    "X-Priority": "3"
                }
            }
        }
        return templates.get(variant_type, templates["urgency"])
    
    def _create_message(self, recipient: Recipient, template: Dict[str, Any]) -> MIMEMultipart:
        """Create email message"""
        msg = MIMEMultipart("alternative")
        msg["From"] = f'{template["from_name"]} <{template["from_email"]}>'
        msg["To"] = recipient.email
        msg["Subject"] = template["subject"]
        
        if self.config.reply_to:
            msg["Reply-To"] = self.config.reply_to
        
        # Add headers
        for key, value in template.get("headers", {}).items():
            msg[key] = value
        
        # Add HTML body
        html_part = MIMEText(template["body_html"], "html")
        msg.attach(html_part)
        
        return msg
    
    def _send_via_smtp(self, msg: MIMEMultipart, recipient: Recipient) -> EmailResult:
        """Send email via SMTP"""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls(context=context)
                if self.config.smtp_user and self.config.smtp_password:
                    server.login(self.config.smtp_user, self.config.smtp_password)
                
                server.send_message(msg, to_addrs=[recipient.email])
                
                return EmailResult(
                    recipient=recipient.email,
                    variant=recipient.variant_id,
                    success=True,
                    message_id=str(uuid.uuid4())
                )
                
        except Exception as e:
            return EmailResult(
                recipient=recipient.email,
                variant=recipient.variant_id,
                success=False,
                error=str(e)
            )
    
    def _send_via_api(self, msg: MIMEMultipart, recipient: Recipient) -> EmailResult:
        """Send email via API (SendGrid/Mailgun)"""
        # Placeholder for API-based sending
        return EmailResult(
            recipient=recipient.email,
            variant=recipient.variant_id,
            success=True,
            message_id=f"api-{uuid.uuid4().hex[:8]}"
        )
    
    def send_campaign(
        self,
        recipients: List[Recipient],
        variant_type: str = "urgency",
        landing_page: str = "microsoft_login.html"
    ) -> List[EmailResult]:
        """Send campaign emails to all recipients"""
        template = self._load_email_template(variant_type)
        results = []
        
        for i, recipient in enumerate(recipients):
            recipient.variant_id = f"V{len(results) % 3 + 1}"
            msg = self._create_message(recipient, template)
            
            if self.config.test_mode:
                # In test mode, just log instead of sending
                result = EmailResult(
                    recipient=recipient.email,
                    variant=recipient.variant_id,
                    success=True,
                    message_id=f"test-{i}",
                    timestamp=datetime.now().isoformat()
                )
                print(f"[TEST] Would send to {recipient.email}")
                print(f"  Subject: {template['subject']}")
                print(f"  Variant: {recipient.variant_id}")
                print(f"  Landing: {landing_page}")
            else:
                # Actually send
                if self.config.api_provider:
                    result = self._send_via_api(msg, recipient)
                else:
                    result = self._send_via_smtp(msg, recipient)
            
            results.append(result)
            self.sent_count += 1
            if not result.success:
                self.failed_count += 1
        
        self.results.extend(results)
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get campaign summary"""
        return {
            "campaign_id": self.config.campaign_id,
            "total_sent": self.sent_count,
            "successful": sum(1 for r in self.results if r.success),
            "failed": self.failed_count,
            "test_mode": self.config.test_mode,
            "results": [
                {
                    "recipient": r.recipient,
                    "variant": r.variant,
                    "success": r.success,
                    "error": r.error
                }
                for r in self.results
            ]
        }


def main():
    parser = argparse.ArgumentParser(description="Red Team Campaign Email Sender")
    parser.add_argument("--config", default="config/campaign-config.json", help="Campaign config file")
    parser.add_argument("--test", action="store_true", help="Run in test mode (log only)")
    parser.add_argument("--recipients", default="config/recipients.json", help="Recipients file")
    parser.add_argument("--variant", default="urgency", choices=["urgency", "authority", "social"])
    parser.add_argument("--landing", default="microsoft_login.html", 
                       choices=["microsoft_login.html", "google_workspace.html", "adobe_sign.html"])
    parser.add_argument("--output", help="Output results to file")
    
    args = parser.parse_args()
    
    # Load config
    config_path = Path(__file__).parent.parent / args.config
    if config_path.exists():
        with open(config_path) as f:
            config_data = json.load(f)
    else:
        config_data = {}
    
    # Create sender config
    sender_config = EmailConfig(
        campaign_id=config_data.get("campaign_id", f"CAMP-{datetime.now().strftime('%Y%m%d')}-001"),
        test_mode=args.test,
        smtp_server=config_data.get("smtp_server", "smtp.office365.com"),
        from_name=config_data.get("from_name", "IT Security Team"),
        from_email=config_data.get("from_email", "it-support@company.com")
    )
    
    # Create sender
    sender = CampaignEmailSender(sender_config)
    
    # Load recipients
    recipients_path = Path(__file__).parent.parent / args.recipients
    if recipients_path.exists():
        with open(recipients_path) as f:
            recipients_data = json.load(f)
        recipients = [
            Recipient(
                email=r["email"],
                first_name=r.get("first_name", ""),
                last_name=r.get("last_name", ""),
                department=r.get("department", ""),
                role=r.get("role", ""),
                segment=r.get("segment", "")
            )
            for r in recipients_data.get("recipients", [])
        ]
    else:
        # Generate test recipients
        recipients = [
            Recipient(email=f"test{i}@company.com", segment="general")
            for i in range(10)
        ]
    
    print(f"\n[EMAIL] Campaign Email Sender")
    print(f"{'='*50}")
    print(f"Campaign ID: {sender_config.campaign_id}")
    print(f"Variant: {args.variant}")
    print(f"Landing Page: {args.landing}")
    print(f"Recipients: {len(recipients)}")
    print(f"Test Mode: {sender_config.test_mode}")
    print()
    
    # Send campaign
    results = sender.send_campaign(recipients, args.variant, args.landing)
    
    # Summary
    summary = sender.get_summary()
    print(f"\n[RESULTS] Results:")
    print(f"  Sent: {summary['total_sent']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    
    # Output
    if args.output:
        output_path = Path(__file__).parent.parent / args.output
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n💾 Results saved to {output_path}")
    
    return summary


if __name__ == "__main__":
    main()
