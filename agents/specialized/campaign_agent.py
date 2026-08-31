#!/usr/bin/env python3
"""
Campaign Agent — Autonomous Red Team phishing campaign orchestration.

Manages the full lifecycle of phishing simulation campaigns:
  1. Campaign design (A/B variants, templates, audience)
  2. Landing page deployment (local HTTP server)
  3. Email delivery (SMTP/API with tracking pixels)
  4. Results analysis (UCB bandit optimization)
  5. Report generation (conversion rates, recommendations)

Usage:
    from agents.specialized.campaign_agent import CampaignAgent
    agent = CampaignAgent()
    result = agent.run_campaign(config)
"""

import json
import os
import sys
import time
import asyncio
import threading
import subprocess
import http.server
import socketserver
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from urllib.parse import urlencode

# Add project root to path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.campaign_manager import (
    CampaignGenerator,
    CampaignType,
    AudienceSegment,
    CampaignVariant,
    CampaignMetrics,
)
from scripts.email_sender import CampaignEmailSender, EmailConfig, Recipient, EmailResult
from scripts.tracking_server import app as tracking_app
from scripts.landing_server import TrackingHandler

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class CampaignStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ApprovalGate(Enum):
    NONE = "none"
    MANUAL = "manual"
    AUTOMATED = "automated"


@dataclass
class CampaignConfig:
    """Configuration for a phishing campaign."""

    name: str
    campaign_type: str = "phishing"  # phishing | vishing | usb_drop
    variants: List[Dict[str, Any]] = field(default_factory=list)
    audience_size: int = 100
    budget: float = 1000.0
    duration_hours: int = 48
    landing_page: str = "microsoft_login.html"
    sender_name: str = "IT Security Team"
    sender_email: str = "it-support@company.com"
    smtp_server: str = "smtp.office365.com"
    smtp_port: int = 587
    approval_gate: str = "manual"
    test_mode: bool = True
    segments: List[Dict[str, Any]] = field(default_factory=list)
    custom_payloads: Optional[Dict[str, Any]] = None


@dataclass
class CampaignResult:
    """Results from a completed campaign."""

    campaign_id: str
    status: str
    variants: List[Dict[str, Any]] = field(default_factory=list)
    total_sent: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_converted: int = 0
    total_reported: int = 0
    winner_variant: Optional[str] = None
    confidence: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    raw_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

    @property
    def open_rate(self) -> float:
        return (self.total_opened / self.total_sent * 100) if self.total_sent > 0 else 0

    @property
    def click_rate(self) -> float:
        return (self.total_clicked / self.total_opened * 100) if self.total_opened > 0 else 0

    @property
    def conversion_rate(self) -> float:
        return (self.total_converted / self.total_clicked * 100) if self.total_clicked > 0 else 0

    @property
    def report_rate(self) -> float:
        return (self.total_reported / self.total_sent * 100) if self.total_sent > 0 else 0


# ---------------------------------------------------------------------------
# Campaign Agent
# ---------------------------------------------------------------------------


class CampaignAgent:
    """
    Autonomous phishing campaign orchestration agent.

    Manages the full campaign lifecycle with safety gates:
      - Campaign design & variant generation
      - Landing page deployment (local HTTP server)
      - Email delivery with tracking
      - UCB bandit optimization
      - Results analysis & reporting
    """

    NAME = "campaign_agent"
    CATEGORY = "red_team"
    ROLE = "Offensive Security — Phishing Campaigns"

    # Safe defaults
    DEFAULT_SMTP_SERVER = "smtp.office365.com"
    DEFAULT_SMTP_PORT = 587
    MAX_VARIANTS = 10
    MAX_AUDIENCE = 10000
    MIN_SAMPLE_SIZE = 30

    def __init__(
        self,
        config_path: Optional[str] = None,
        test_mode: bool = True,
        approval_required: bool = True,
        max_parallel_sends: int = 5,
    ):
        self.test_mode = test_mode
        self.approval_required = approval_required
        self.max_parallel_sends = max_parallel_sends

        # Internal state
        self._campaign_gen = CampaignGenerator()
        self._pending_approvals: Dict[str, Dict] = {}
        self._active_campaigns: Dict[str, Dict] = {}
        self._server_thread: Optional[threading.Thread] = None
        self._server_port: int = 0
        self._server_handle = None

        # Load config
        self._config: Dict[str, Any] = {}
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                self._config = json.load(f)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def create_campaign(self, config: CampaignConfig) -> Dict[str, Any]:
        """
        Design a campaign: generate variants, landing page URLs, tracking IDs.
        Returns campaign blueprint (draft state).
        """
        campaign_id = self._campaign_gen.generate_campaign_id()
        now = datetime.now().isoformat()

        # Validate config
        self._validate_config(config)

        # Generate variants using CampaignGenerator
        variants_data = []
        if config.variants:
            for v in config.variants:
                variants_data.append(
                    {
                        "id": v.get("id", f"V{len(variants_data)+1}"),
                        "name": v.get("name", f"Variant {len(variants_data)+1}"),
                        "weight": v.get("weight", 100 // max(len(config.variants), 1)),
                        "budget": v.get("budget", config.budget / max(len(config.variants), 1)),
                        "payload": v.get("payload", self._generate_default_payload(config.campaign_type)),
                        "max_allocation": v.get("max_allocation", float("inf")),
                    }
                )
        else:
            # Auto-generate variants based on campaign type
            variants_data = self._generate_default_variants(config)

        # Generate landing page URL with tracking params
        landing_base = f"http://127.0.0.1:{self._server_port}" if self._server_port else "http://localhost:8765"
        landing_url = f"{landing_base}/{config.landing_page}"

        # Build campaign blueprint
        blueprint = {
            "campaign_id": campaign_id,
            "type": config.campaign_type,
            "title": config.name,
            "status": CampaignStatus.PENDING_APPROVAL.value if self.approval_required else CampaignStatus.ACTIVE.value,
            "created_at": now,
            "variants": variants_data,
            "landing_page": {
                "url": landing_url,
                "template": config.landing_page,
                "tracking_enabled": True,
            },
            "audience": {
                "total_size": config.audience_size,
                "segments": config.segments,
            },
            "budget": {
                "total": config.budget,
                "currency": "test_credits",
                "allocated": 0,
            },
            "delivery": {
                "smtp_server": config.smtp_server,
                "smtp_port": config.smtp_port,
                "from_name": config.sender_name,
                "from_email": config.sender_email,
                "test_mode": config.test_mode,
            },
            "metrics": {
                "primary": "conversion_rate",
                "secondary": ["open_rate", "click_rate", "report_rate"],
                "target_confidence": 0.95,
                "minimum_sample_size": max(self.MIN_SAMPLE_SIZE, config.audience_size // 10),
            },
            "approval": {
                "gate": config.approval_gate,
                "required": self.approval_required,
                "approved_by": None,
                "approved_at": None,
            },
        }

        # Store for approval tracking
        if self.approval_required:
            self._pending_approvals[campaign_id] = blueprint

        return blueprint

    def request_approval(self, campaign_id: str, approver: str) -> Dict[str, Any]:
        """
        Request manual approval for a campaign.
        Returns approval result.
        """
        if campaign_id not in self._pending_approvals:
            return {"success": False, "error": f"Campaign {campaign_id} not found"}

        blueprint = self._pending_approvals[campaign_id]
        blueprint["approval"]["approved_by"] = approver
        blueprint["approval"]["approved_at"] = datetime.now().isoformat()
        blueprint["status"] = CampaignStatus.ACTIVE.value

        # Move to active
        self._active_campaigns[campaign_id] = blueprint
        del self._pending_approvals[campaign_id]

        # Start tracking server if not running
        self._ensure_tracking_server()

        return {
            "success": True,
            "campaign_id": campaign_id,
            "status": CampaignStatus.ACTIVE.value,
            "approved_by": approver,
        }

    def run_campaign(
        self,
        config: CampaignConfig,
        recipients: Optional[List[Dict[str, Any]]] = None,
    ) -> CampaignResult:
        """
        Full campaign execution: design → approve → deploy → send → analyze.
        """
        # Phase 1: Create blueprint
        blueprint = self.create_campaign(config)
        campaign_id = blueprint["campaign_id"]

        # Phase 2: Auto-approve in test mode
        if self.test_mode or not self.approval_required:
            self.request_approval(campaign_id, "auto-test-mode")
        else:
            return CampaignResult(
                campaign_id=campaign_id,
                status=CampaignStatus.PENDING_APPROVAL.value,
                errors=["Approval required. Call request_approval() first."],
            ).to_dict()

        # Phase 3: Deploy tracking server
        self._ensure_tracking_server()

        # Phase 4: Send emails
        recipient_objects = self._parse_recipients(recipients or [])
        sender_config = EmailConfig(
            smtp_server=config.smtp_server,
            smtp_port=config.smtp_port,
            from_name=config.sender_name,
            from_email=config.sender_email,
            campaign_id=campaign_id,
            tracking_enabled=True,
            test_mode=self.test_mode,
        )
        sender = CampaignEmailSender(sender_config)

        # Distribute recipients across variants
        total_recipients = len(recipient_objects)
        variant_assignments = self._assign_variants(recipient_objects, blueprint["variants"])

        all_results: List[EmailResult] = []
        variant_stats: Dict[str, Dict[str, int]] = {
            v["id"]: {"sent": 0, "opened": 0, "clicked": 0, "converted": 0, "reported": 0}
            for v in blueprint["variants"]
        }

        for variant_id, variant_recipients in variant_assignments.items():
            if not variant_recipients:
                continue
            # Build a temporary sender for this variant
            variant_sender_config = EmailConfig(
                smtp_server=config.smtp_server,
                smtp_port=config.smtp_port,
                from_name=config.sender_name,
                from_email=config.sender_email,
                campaign_id=campaign_id,
                tracking_enabled=True,
                test_mode=self.test_mode,
            )
            variant_sender = CampaignEmailSender(variant_sender_config)
            # Tag recipients with this variant
            for rec in variant_recipients:
                rec.variant_id = variant_id
            variant_results = variant_sender.send_campaign(
                variant_recipients,
                variant_type=variant_id,
                landing_page=blueprint["landing_page"]["url"],
            )
            all_results.extend(variant_results)
            for result in variant_results:
                if result.success:
                    variant_stats[variant_id]["sent"] += 1

        # Phase 5: Analyze results
        # Compute aggregate metrics from variant_stats
        total_sent = sum(s["sent"] for s in variant_stats.values())
        total_opened = sum(s["opened"] for s in variant_stats.values())
        total_clicked = sum(s["clicked"] for s in variant_stats.values())
        total_converted = sum(s["converted"] for s in variant_stats.values())
        total_reported = sum(s["reported"] for s in variant_stats.values())

        result = CampaignResult(
            campaign_id=campaign_id,
            status=CampaignStatus.COMPLETED.value,
            variants=blueprint["variants"],
            total_sent=total_sent,
            total_opened=total_opened,
            total_clicked=total_clicked,
            total_converted=total_converted,
            total_reported=total_reported,
            winner_variant=self._determine_winner(variant_stats),
            confidence=self._calculate_confidence(variant_stats),
            recommendations=self._generate_recommendations(variant_stats),
            started_at=blueprint["created_at"],
            completed_at=datetime.now().isoformat(),
            raw_metrics={"variant_stats": variant_stats, "sender_summary": sender.get_summary()},
        )

        # Clean up
        self._stop_tracking_server()

        return result.to_dict()

    def get_results(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve results for a completed campaign."""
        if campaign_id in self._active_campaigns:
            blueprint = self._active_campaigns[campaign_id]
            return {
                "campaign_id": campaign_id,
                "status": blueprint["status"],
                "variants": blueprint["variants"],
                "metrics": blueprint.get("metrics", {}),
            }
        return None

    def list_campaigns(self) -> List[Dict[str, Any]]:
        """List all campaigns (pending + active)."""
        all_campaigns = []
        for cid, bp in self._pending_approvals.items():
            all_campaigns.append({"id": cid, "status": bp["status"], "title": bp["title"]})
        for cid, bp in self._active_campaigns.items():
            all_campaigns.append({"id": cid, "status": bp["status"], "title": bp["title"]})
        return all_campaigns

    def describe(self) -> Dict[str, Any]:
        return {
            "name": self.NAME,
            "description": "Autonomous phishing campaign orchestration — A/B testing, UCB optimization, full lifecycle management",
            "category": self.CATEGORY,
            "role": self.ROLE,
            "capabilities": [
                "campaign_design",
                "ab_testing",
                "landing_page_deploy",
                "email_delivery",
                "tracking",
                "ucb_optimization",
                "results_analysis",
                "report_generation",
            ],
            "test_mode": self.test_mode,
            "approval_required": self.approval_required,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_config(self, config: CampaignConfig) -> None:
        if config.audience_size > self.MAX_AUDIENCE:
            raise ValueError(f"Audience size {config.audience_size} exceeds maximum {self.MAX_AUDIENCE}")
        if len(config.variants) > self.MAX_VARIANTS:
            raise ValueError(f"Max {self.MAX_VARIANTS} variants allowed")
        if config.budget <= 0:
            raise ValueError("Budget must be positive")

    def _generate_default_payload(self, campaign_type: str) -> Dict[str, Any]:
        """Generate default email payload based on campaign type."""
        templates = {
            "phishing": {
                "subject": "Security Alert: Action Required",
                "body_template": "Dear user,\n\nYour account requires immediate verification. Click here to update your credentials.\n\nIT Security Team",
                "cta": "Verify Now",
            },
            "vishing": {
                "caller_identity": "IT Helpdesk",
                "pretext": "password_reset",
                "script": "Identity verification required for account security.",
            },
            "usb_drop": {
                "label": "Confidential_Docs.pdf",
                "payload": "autorun.inf",
            },
        }
        return templates.get(campaign_type, templates["phishing"])

    def _generate_default_variants(self, config: CampaignConfig) -> List[Dict]:
        """Auto-generate A/B variants based on psychological triggers."""
        types = {
            "phishing": [
                {"name": "Urgency-Based", "weight": 40, "trigger": "urgency"},
                {"name": "Authority-Based", "weight": 35, "trigger": "authority"},
                {"name": "Social-Engineering", "weight": 25, "trigger": "social_proof"},
            ],
            "vishing": [
                {"name": "IT_Helpdesk", "weight": 50, "trigger": "authority"},
                {"name": "Security_Ops", "weight": 30, "trigger": "fear"},
                {"name": "Vendor_Support", "weight": 20, "trigger": "trust"},
            ],
        }
        triggers = types.get(config.campaign_type, types["phishing"])
        n = len(triggers)
        variants = []
        for i, t in enumerate(triggers):
            payload = self._generate_trigger_payload(t["trigger"], config)
            variants.append(
                {
                    "id": f"V{i+1}",
                    "name": t["name"],
                    "weight": t["weight"],
                    "budget": config.budget / n,
                    "payload": payload,
                    "max_allocation": float("inf"),
                }
            )
        return variants

    def _generate_trigger_payload(self, trigger: str, config: CampaignConfig) -> Dict:
        """Generate email payload targeting a specific psychological trigger."""
        payloads = {
            "urgency": {
                "subject": f"URGENT: {config.sender_name} Action Required",
                "body_template": "Immediate action required. Your account will be suspended in 24 hours.",
                "cta": "Act Now",
            },
            "authority": {
                "subject": f"From {config.sender_name}: Mandatory Update",
                "body_template": "This is an official communication from IT Security. Please verify your credentials.",
                "cta": "Verify Credentials",
            },
            "social_proof": {
                "subject": f"{config.sender_name} — Team Notification",
                "body_template": "Your colleagues have already completed this update. Please do the same.",
                "cta": "Complete Update",
            },
            "fear": {
                "subject": "Security Alert: Suspicious Activity Detected",
                "body_template": "We detected unusual login activity. Secure your account immediately.",
                "cta": "Secure Account",
            },
            "trust": {
                "subject": f"Support Ticket #{datetime.now().strftime('%Y%m%d')}-001",
                "body_template": "Our support team is assisting with a security update. Please follow the link.",
                "cta": "Contact Support",
            },
        }
        return payloads.get(trigger, payloads["urgency"])

    def _parse_recipients(self, recipients_data: List[Dict]) -> List[Recipient]:
        """Parse recipient dicts into Recipient objects."""
        recipients = []
        for r in recipients_data:
            recipients.append(
                Recipient(
                    email=r.get("email", f"test{len(recipients)}@company.com"),
                    first_name=r.get("first_name", ""),
                    last_name=r.get("last_name", ""),
                    department=r.get("department", ""),
                    role=r.get("role", ""),
                    segment=r.get("segment", "general"),
                )
            )
        # Generate test recipients if none provided
        if not recipients:
            for i in range(min(10, self.MAX_AUDIENCE)):
                recipients.append(Recipient(email=f"test{i}@company.com", segment="general"))
        return recipients

    def _assign_variants(
        self, recipients: List[Recipient], variants: List[Dict]
    ) -> Dict[str, List[Recipient]]:
        """Assign recipients to variants based on weight distribution."""
        assignment: Dict[str, List[Recipient]] = {v["id"]: [] for v in variants}
        total_weight = sum(v.get("weight", 100 // len(variants)) for v in variants) or 1

        for rec in recipients:
            # Simple weighted round-robin for demo
            idx = hash(rec.email) % total_weight
            cumulative = 0
            for v in variants:
                cumulative += v.get("weight", 100 // len(variants))
                if idx < cumulative:
                    assignment[v["id"]].append(rec)
                    break
            else:
                assignment[variants[-1]["id"]].append(rec)

        return assignment

    def _ensure_tracking_server(self) -> None:
        """Start tracking server in background thread if not running."""
        if self._server_port == 0:
            self._server_port = 8765
            # Start Flask tracking server
            def run_server():
                tracking_app.run(host="127.0.0.1", port=self._server_port, debug=False, use_reloader=False)

            self._server_thread = threading.Thread(target=run_server, daemon=True)
            self._server_thread.start()
            time.sleep(0.5)  # Allow server to start

    def _stop_tracking_server(self) -> None:
        """Stop tracking server."""
        # Server runs as daemon thread — no explicit stop needed
        pass

    def _determine_winner(self, variant_stats: Dict[str, Dict]) -> Optional[str]:
        """Determine winning variant by conversion rate."""
        if not variant_stats:
            return None
        winner = max(variant_stats.items(), key=lambda x: x[1].get("converted", 0))
        return winner[0] if winner[1].get("converted", 0) > 0 else None

    def _calculate_confidence(self, variant_stats: Dict[str, Dict]) -> float:
        """Calculate statistical confidence in results."""
        total = sum(s.get("sent", 0) for s in variant_stats.values())
        if total < self.MIN_SAMPLE_SIZE:
            return 0.0
        # Simple confidence heuristic
        return min(0.95, 0.5 + (total / 1000) * 0.3)

    def _generate_recommendations(self, variant_stats: Dict[str, Dict]) -> List[str]:
        """Generate actionable recommendations from campaign results."""
        recs = []
        winner = self._determine_winner(variant_stats)
        if winner:
            recs.append(f"Winner variant: {winner} — allocate 70% budget to this variant")
        else:
            recs.append("No clear winner — extend campaign duration")

        total_sent = sum(s.get("sent", 0) for s in variant_stats.values())
        if total_sent < self.MIN_SAMPLE_SIZE:
            recs.append(f"Insufficient sample size ({total_sent}). Target: {self.MIN_SAMPLE_SIZE}+ recipients")

        # Check for concerning metrics
        for vid, stats in variant_stats.items():
            if stats.get("sent", 0) > 0:
                report_rate = stats.get("reported", 0) / stats["sent"] * 100
                if report_rate > 5:
                    recs.append(f"High report rate on {vid} ({report_rate:.1f}%) — improve social engineering quality")

        return recs


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FreeAI Campaign Agent")
    parser.add_argument("--config", default="config/campaign-phishing-3v.json", help="Campaign config file")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--approve", action="store_true", help="Auto-approve campaign")
    args = parser.parse_args()

    agent = CampaignAgent(test_mode=args.test, approval_required=not args.approve)
    print(json.dumps(agent.describe(), indent=2))
