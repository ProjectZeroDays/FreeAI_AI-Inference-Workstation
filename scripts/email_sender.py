#!/usr/bin/env python3
"""
Email Campaign Sender
Sends phishing simulation emails with tracking pixels and landing pages.

Usage:
    python scripts/email_sender.py --config config/email-sender-config.json --campaign data/campaign-phishing-3v.json --send
    python scripts/email_sender.py --config config/email-sender-config.json --simulate
    python scripts/email_sender.py --config config/email-sender-config.json --status
"""

import argparse
import csv
import json
import os
import smtplib
import ssl
import sys
import uuid
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Error: Jinja2 required. Install with: pip install jinja2")
    sys.exit(1)

try:
    from campaign_manager import CampaignGenerator
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from campaign_manager import CampaignGenerator


class EmailCampaignSender:
    """Send phishing simulation emails with tracking."""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.template_dir = Path(__file__).parent.parent / "templates" / "email_templates"
        self.landing_dir = Path(__file__).parent.parent / "templates" / "landing_pages"
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        self.results: List[Dict] = []
        self.stats = {
            "total_sent": 0,
            "total_opened": 0,
            "total_clicked": 0,
            "total_submitted": 0,
            "by_variant": {}
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _load_recipients(self) -> List[Dict]:
        """Load recipients from CSV file."""
        recipients_file = self.config.get("recipients", {}).get("source_file", "data/recipients.csv")
        recipients_path = Path(__file__).parent.parent / recipients_file
        
        if not recipients_path.exists():
            print(f"Warning: Recipients file not found: {recipients_path}")
            return []
        
        recipients = []
        with open(recipients_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                recipients.append(row)
        
        return recipients
    
    def _load_email_content(self, variant_id: str) -> Dict:
        """Load email content for a variant."""
        content_file = self.template_dir.parent / "content.json"
        with open(content_file, 'r') as f:
            data = json.load(f)
        return data["variants"].get(variant_id, {})
    
    def _render_email(self, template_name: str, context: Dict) -> str:
        """Render email template with Jinja2."""
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def _create_email(
        self,
        recipient_email: str,
        recipient_name: str,
        variant_id: str,
        campaign_id: str
    ) -> MIMEMultipart:
        """Create email message with tracking."""
        variant_config = self.config.get("variants", {}).get(variant_id, {})
        email_content = self._load_email_content(variant_id)
        
        # Tracking URLs
        tracking_base = self.config.get("tracking", {}).get("link_rewrite_base", "https://tracking.test/redirect")
        tracking_id = uuid.uuid4().hex[:8]
        tracking_url = f"{tracking_base}/{campaign_id}/{variant_id}/{tracking_id}"
        pixel_url = f"{tracking_base}/pixel/{campaign_id}/{variant_id}/{tracking_id}"
        
        # Build context
        context = {
            "recipient_email": recipient_email,
            "recipient_name": recipient_name,
            "company": self.config.get("sender", {}).get("name", "Company").split()[0],
            "sender_name": "IT Security Team",
            "doc_name": "Q4_Financial_Review_2026.pdf",
            "expiry_date": datetime.now().strftime("%B %d, %Y"),
            "expiry_time": "23:59",
            "campaign_id": campaign_id,
            "variant_id": variant_id,
            "tracking_url": tracking_url,
            "tracking_pixel": pixel_url,
            "landing_url": variant_config.get("landing_page", ""),
            "unsubscribe_text": self.config.get("campaign_defaults", {}).get("unsubscribe_text", ""),
            "disclaimer": self.config.get("campaign_defaults", {}).get("disclaimer", ""),
            "year": datetime.now().year,
            **email_content
        }
        
        # Render email body
        html_body = self._render_email("base.html", context)
        text_body = self._render_email("base.txt.j2", context) if (self.template_dir / "base.txt.j2").exists() else html_body
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = email_content.get("subject", "Security Notice")
        msg["From"] = f"{self.config['sender']['name']} <{self.config['sender']['email']}>"
        msg["To"] = recipient_email
        msg["Reply-To"] = "security@company.com"
        msg["X-Campaign-ID"] = campaign_id
        msg["X-Variant-ID"] = variant_id
        msg["X-Tracking-ID"] = tracking_id
        
        # Attach HTML and text versions
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        
        return msg, tracking_url
    
    def _send_email(self, msg: MIMEMultipart, recipient: str) -> bool:
        """Send email via SMTP."""
        smtp_config = self.config.get("smtp", {})
        
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
                server.starttls(context=context)
                
                if smtp_config.get("username") and smtp_config.get("password"):
                    server.login(smtp_config["username"], smtp_config["password"])
                
                server.send_message(msg, to_addrs=[recipient])
                return True
                
        except Exception as e:
            print(f"  ✗ Failed to send to {recipient}: {e}")
            return False
    
    def _record_result(
        self,
        campaign_id: str,
        variant_id: str,
        recipient_email: str,
        recipient_name: str,
        action: str,
        tracking_id: str,
        success: bool
    ):
        """Record campaign result."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "campaign_id": campaign_id,
            "variant_id": variant_id,
            "recipient_email": recipient_email,
            "recipient_name": recipient_name,
            "action": action,
            "tracking_id": tracking_id,
            "success": success
        }
        self.results.append(result)
        
        # Update stats
        if action == "sent" and success:
            self.stats["total_sent"] += 1
        elif action == "opened" and success:
            self.stats["total_opened"] += 1
        elif action == "clicked" and success:
            self.stats["total_clicked"] += 1
        elif action == "submitted" and success:
            self.stats["total_submitted"] += 1
        
        if variant_id not in self.stats["by_variant"]:
            self.stats["by_variant"][variant_id] = {
                "sent": 0, "opened": 0, "clicked": 0, "submitted": 0
            }
        if success and action in self.stats["by_variant"][variant_id]:
            self.stats["by_variant"][variant_id][action] += 1
    
    def run_campaign(self, campaign_config: Dict, recipients: Optional[List[Dict]] = None, dry_run: bool = True):
        """Run email campaign."""
        # Handle nested campaign structure (from generator)
        if "campaign" in campaign_config:
            campaign_config = campaign_config["campaign"]
        
        campaign_id = campaign_config.get("campaign_id", f"CAMP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}")
        
        print(f"\n{'='*60}")
        print(f"  CAMPAIGN: {campaign_id}")
        print(f"{'='*60}\n")
        
        # Load recipients if not provided
        if recipients is None:
            recipients = self._load_recipients()
        
        if not recipients:
            print("No recipients found. Check data/recipients.csv")
            return
        
        # Get variants
        variants = campaign_config.get("variants", [])
        if not variants:
            print("No variants in campaign config")
            return
        
        print(f"Recipients: {len(recipients)}")
        print(f"Variants: {len(variants)}")
        print(f"Dry run: {'YES' if dry_run else 'NO'}\n")
        
        # Send emails
        for i, recipient in enumerate(recipients):
            email = recipient.get("email", "")
            name = recipient.get("name", "User")
            
            if not email:
                continue
            
            # Assign variant based on round-robin or weighted
            variant_idx = i % len(variants)
            variant = variants[variant_idx]
            variant_id = variant.get("id", f"variant_{variant_idx+1}")
            
            print(f"[{i+1}/{len(recipients)}] Sending to {name} <{email}> (Variant: {variant.get('name', variant_id)})")
            
            try:
                msg, tracking_url = self._create_email(email, name, variant_id, campaign_id)
                
                if dry_run:
                    print(f"  ✓ [DRY RUN] Would send to {email}")
                    self._record_result(campaign_id, variant_id, email, name, "sent", tracking_url, True)
                else:
                    success = self._send_email(msg, email)
                    self._record_result(campaign_id, variant_id, email, name, "sent", tracking_url, success)
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                self._record_result(campaign_id, variant_id, email, name, "sent", "", False)
        
        # Save results
        self._save_results(campaign_id)
        
        # Print summary
        self._print_summary()
    
    def _save_results(self, campaign_id: str):
        """Save campaign results to JSON."""
        results_dir = Path(__file__).parent.parent / self.config.get("tracking", {}).get("results_dir", "data/campaign_results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = results_dir / f"{campaign_id}-results.json"
        
        output = {
            "campaign_id": campaign_id,
            "generated_at": datetime.now().isoformat(),
            "stats": self.stats,
            "results": self.results
        }
        
        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to: {results_file}")
    
    def _print_summary(self):
        """Print campaign summary."""
        print(f"\n{'='*60}")
        print(f"  CAMPAIGN SUMMARY")
        print(f"{'='*60}")
        print(f"  Total Sent:    {self.stats['total_sent']}")
        print(f"  Total Opened:  {self.stats['total_opened']}")
        print(f"  Total Clicked: {self.stats['total_clicked']}")
        print(f"  Total Submit:  {self.stats['total_submitted']}")
        
        if self.stats['total_sent'] > 0:
            open_rate = (self.stats['total_opened'] / self.stats['total_sent']) * 100
            click_rate = (self.stats['total_clicked'] / self.stats['total_sent']) * 100
            print(f"  Open Rate:     {open_rate:.1f}%")
            print(f"  Click Rate:    {click_rate:.1f}%")
        
        print(f"\n  By Variant:")
        for variant_id, vstats in self.stats['by_variant'].items():
            print(f"    {variant_id}: sent={vstats['sent']}, opened={vstats['opened']}, clicked={vstats['clicked']}")
        print(f"{'='*60}\n")
    
    def simulate_campaign(self, campaign_config: Dict):
        """Simulate campaign without sending emails."""
        # Handle nested campaign structure
        if "campaign" in campaign_config:
            campaign_config = campaign_config["campaign"]
        
        campaign_id = campaign_config.get("campaign_id", f"CAMP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}")
        
        print(f"\n{'='*60}")
        print(f"  SIMULATING CAMPAIGN: {campaign_id}")
        print(f"{'='*60}\n")
        
        recipients = self._load_recipients()
        variants = campaign_config.get("variants", [])
        
        import random
        random.seed(42)
        
        for i, recipient in enumerate(recipients):
            email = recipient.get("email", "")
            name = recipient.get("name", "User")
            
            if not email:
                continue
            
            variant_idx = i % len(variants)
            variant = variants[variant_idx]
            variant_id = variant.get("id", f"variant_{variant_idx+1}")
            
            print(f"[{i+1}/{len(recipients)}] Simulating: {name} <{email}> -> {variant.get('name', variant_id)}")
            
            # Simulate open (70% chance)
            opened = random.random() < 0.7
            if opened:
                self._record_result(campaign_id, variant_id, email, name, "opened", "", True)
            
            # Simulate click (50% of opens)
            clicked = opened and random.random() < 0.5
            if clicked:
                self._record_result(campaign_id, variant_id, email, name, "clicked", "", True)
            
            # Simulate submission (30% of clicks)
            submitted = clicked and random.random() < 0.3
            if submitted:
                self._record_result(campaign_id, variant_id, email, name, "submitted", "", True)
        
        self._save_results(campaign_id)
        self._print_summary()


def main():
    parser = argparse.ArgumentParser(description="Email Campaign Sender")
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--campaign", help="Path to campaign JSON")
    parser.add_argument("--recipients", help="Path to recipients CSV")
    parser.add_argument("--send", action="store_true", help="Actually send emails (requires SMTP config)")
    parser.add_argument("--simulate", action="store_true", help="Simulate campaign without sending")
    parser.add_argument("--status", action="store_true", help="Show campaign status")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be sent")
    
    args = parser.parse_args()
    
    sender = EmailCampaignSender(args.config)
    
    if args.status:
        # Load and display campaign status
        if args.campaign:
            with open(args.campaign) as f:
                campaign = json.load(f)
            print(json.dumps(campaign, indent=2))
        return
    
    if args.simulate:
        if not args.campaign:
            print("Error: --campaign required with --simulate")
            return
        with open(args.campaign) as f:
            campaign = json.load(f)
        sender.simulate_campaign(campaign)
        return
    
    if args.send or args.dry_run:
        if not args.campaign:
            print("Error: --campaign required")
            return
        with open(args.campaign) as f:
            campaign = json.load(f)
        
        recipients = None
        if args.recipients:
            import csv
            with open(args.recipients) as f:
                recipients = list(csv.DictReader(f))
        
        sender.run_campaign(campaign, recipients, dry_run=not args.send)
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
