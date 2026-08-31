#!/usr/bin/env python3
"""
FreeAI Campaign Agent — Orchestrator for Red Team Email Campaigns

Wraps existing modular tools:
  - campaign_manager.py  (CampaignGenerator, BudgetAllocator, SegmentAnalyzer)
  - email_sender.py      (CampaignEmailSender)
  - tracking_server.py   (Flask tracking endpoints)
  - landing_server.py    (Landing page HTTP server)

Usage:
  python scripts/campaign_agent.py --brief "phishing campaign targeting IT admins, 3 variants, 2000 credits"
  python scripts/campaign_agent.py --brief "authority-based email campaign, engineering segment, 1000 recipients"
  python scripts/campaign_agent.py --status
  python scripts/campaign_agent.py --report <campaign_id>
"""

import json
import sys
import subprocess
import time
import uuid
import argparse
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.campaign_manager import (
    CampaignGenerator,
    CampaignType,
    BudgetAllocator,
    SegmentAnalyzer,
    AudienceSegment,
    AudienceSegmentConfig,
)
from scripts.email_sender import CampaignEmailSender, EmailConfig, Recipient

TRACKING_SERVER_PORT = 9090
LANDING_SERVER_PORT = 8080
DATA_DIR = PROJECT_ROOT / "data" / "campaign_results"
CONFIG_DIR = PROJECT_ROOT / "config"
TEMPLATES_DIR = PROJECT_ROOT / "templates" / "landing_pages"

# Track background server PIDs
_server_processes: Dict[str, subprocess.Popen] = {}


# ─────────────────────────────────────────────
# Natural language brief parser
# ─────────────────────────────────────────────

def parse_brief(brief: str) -> Dict[str, Any]:
    """Parse a natural language brief into campaign parameters."""
    brief_lower = brief.lower()

    # Determine campaign type
    if any(w in brief_lower for w in ["phishing", "phish"]):
        campaign_type = CampaignType.PHISHING_SIM
    elif "vishing" in brief_lower:
        campaign_type = CampaignType.VISHING
    elif "usb" in brief_lower:
        campaign_type = CampaignType.USB_DROP
    elif "rogue ap" in brief_lower or "rogue_access" in brief_lower:
        campaign_type = CampaignType.ROGUE_AP
    elif "abn" in brief_lower or ("a/b/n" in brief_lower):
        campaign_type = CampaignType.ABN_TEST
    else:
        campaign_type = CampaignType.AB_TEST

    # Determine variants
    variant_count = 2
    for word in brief_lower.split():
        if word.startswith("3v") or "three variant" in brief_lower:
            variant_count = 3
            break
        if word.startswith("4v") or "four variant" in brief_lower:
            variant_count = 4
            break

    # Determine budget
    budget = 1000.0
    import re
    budget_match = re.search(r"(\d+)\s*(credits?|budget|recipients?)", brief_lower)
    if budget_match:
        budget = float(budget_match.group(1))

    # Determine audience size
    audience_size = int(budget)  # default 1 credit = 1 recipient
    size_match = re.search(r"(\d+)\s*recipients?", brief_lower)
    if size_match:
        audience_size = int(size_match.group(1))
        budget = float(audience_size)

    # Determine target segment
    segment = AudienceSegment.GENERAL
    if any(w in brief_lower for w in ["it admin", "it staff", "it department"]):
        segment = AudienceSegment.IT_STAFF
    elif "c-level" in brief_lower or "executive" in brief_lower:
        segment = AudienceSegment.C_LEVEL
    elif "finance" in brief_lower or "accounting" in brief_lower:
        segment = AudienceSegment.FINANCE
    elif "hr" in brief_lower or "human resources" in brief_lower:
        segment = AudienceSegment.HR
    elif "engineering" in brief_lower or "dev" in brief_lower:
        segment = AudienceSegment.ENGINEERING
    elif "sales" in brief_lower:
        segment = AudienceSegment.FINANCE  # closest match

    # Determine variant types
    variant_types = []
    if any(w in brief_lower for w in ["urgency", "urgent", "expiration", "lockout"]):
        variant_types.append("urgency")
    if any(w in brief_lower for w in ["authority", "mandatory", "security policy"]):
        variant_types.append("authority")
    if any(w in brief_lower for w in ["social", "meeting", "invitation", "co-worker"]):
        variant_types.append("social")

    # Default variants if none specified
    if not variant_types:
        variant_types = ["urgency", "authority", "social"][:variant_count]

    # Determine landing page
    landing_page = "microsoft_login.html"
    if any(w in brief_lower for w in ["google", "workspace"]):
        landing_page = "google_workspace.html"
    elif any(w in brief_lower for w in ["adobe", "sign"]):
        landing_page = "adobe_sign.html"

    return {
        "campaign_type": campaign_type,
        "variant_count": variant_count,
        "budget": budget,
        "audience_size": audience_size,
        "segment": segment,
        "variant_types": variant_types,
        "landing_page": landing_page,
        "raw_brief": brief,
    }


# ─────────────────────────────────────────────
# Campaign lifecycle
# ─────────────────────────────────────────────

def start_tracking_server() -> subprocess.Popen:
    """Start the Flask tracking server in the background."""
    if "tracking" in _server_processes and _server_processes["tracking"].poll() is None:
        return _server_processes["tracking"]

    proc = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "tracking_server.py"),
         "--port", str(TRACKING_SERVER_PORT)],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _server_processes["tracking"] = proc
    time.sleep(0.5)  # let Flask bind
    return proc


def start_landing_server(port: int = LANDING_SERVER_PORT) -> subprocess.Popen:
    """Start the landing page HTTP server in the background."""
    key = f"landing_{port}"
    if key in _server_processes and _server_processes[key].poll() is None:
        return _server_processes[key]

    proc = subprocess.Popen(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "landing_server.py"),
         "--port", str(port), "--host", "127.0.0.1"],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    _server_processes[key] = proc
    time.sleep(0.5)
    return proc


def stop_servers() -> None:
    """Stop all background servers."""
    for key, proc in _server_processes.items():
        if proc.poll() is None:
            proc.terminate()
    _server_processes.clear()


def create_campaign(brief: str) -> Dict[str, Any]:
    """Create a campaign from a natural language brief."""
    params = parse_brief(brief)

    generator = CampaignGenerator()
    tracking_server = start_tracking_server()
    landing_server = start_landing_server()

    # Build variants
    variant_configs = []
    landing_pages = ["microsoft_login.html", "google_workspace.html", "adobe_sign.html"]
    for i, vtype in enumerate(params["variant_types"]):
        variant_configs.append({
            "name": vtype.capitalize() + "-Based",
            "weight": 100 // len(params["variant_types"]),
            "payload": {
                "variant_type": vtype,
                "landing_page": landing_pages[i % len(landing_pages)],
            },
        })

    campaign = generator.generate_ab_test(
        name=f"Campaign: {brief[:60]}",
        variants=variant_configs,
        audience_size=params["audience_size"],
        budget=params["budget"],
    )
    campaign["brief"] = brief
    campaign["params"] = params
    campaign["tracking_server_port"] = TRACKING_SERVER_PORT
    campaign["landing_server_port"] = LANDING_SERVER_PORT
    campaign["status"] = "draft"

    return campaign


def load_recipients(path: str = "config/recipients.json") -> List[Recipient]:
    """Load recipients from config file or generate test data."""
    recipients_path = CONFIG_DIR / path
    if recipients_path.exists():
        with open(recipients_path) as f:
            data = json.load(f)
        recipients = [
            Recipient(
                email=r["email"],
                first_name=r.get("first_name", ""),
                last_name=r.get("last_name", ""),
                department=r.get("department", ""),
                role=r.get("role", ""),
                segment=r.get("segment", ""),
            )
            for r in data.get("recipients", [])
        ]
        return recipients

    # Generate test recipients
    return [
        Recipient(email=f"user{i}@company.com", segment="general", role="employee")
        for i in range(1, 11)
    ]


def run_campaign(campaign: Dict[str, Any], test_mode: bool = True) -> Dict[str, Any]:
    """Execute a campaign: send emails, track results, report."""
    campaign_id = campaign["campaign_id"]
    params = campaign["params"]
    variants = campaign["variants"]

    # Setup budget allocator
    allocator = BudgetAllocator(
        total_budget=params["budget"],
        num_variants=len(variants),
    )

    # Load recipients
    recipients = load_recipients()
    # Assign segments based on campaign params
    for r in recipients:
        r.segment = params["segment"].value if hasattr(params["segment"], "value") else str(params["segment"])

    # Setup email sender
    sender_config = EmailConfig(
        campaign_id=campaign_id,
        test_mode=test_mode,
        smtp_server="smtp.office365.com",
        from_name="IT Security Team",
        from_email="it-support@company.com",
        tracking_enabled=True,
    )
    sender = CampaignEmailSender(sender_config)

    # Send with UCB-driven variant assignment
    print(f"\n{'='*60}")
    print(f"🚀 Campaign: {campaign['title']}")
    print(f"   ID: {campaign_id}")
    print(f"   Type: {params['campaign_type'].value}")
    print(f"   Variants: {len(variants)}")
    print(f"   Recipients: {len(recipients)}")
    print(f"   Budget: {params['budget']} credits")
    print(f"   Test Mode: {test_mode}")
    print(f"{'='*60}\n")

    # Distribute recipients across variants using allocator
    sent_results = []
    for recipient in recipients:
        variant_id, _ = allocator.allocate_next()
        if variant_id:
            recipient.variant_id = variant_id
            # Map variant_id to variant type
            vidx = int(variant_id.replace("V", "")) - 1
            vtype = params["variant_types"][vidx] if vidx < len(params["variant_types"]) else "urgency"
            landing = variants[vidx]["payload"].get("landing_page", "microsoft_login.html")
        else:
            recipient.variant_id = "V1"
            vtype = params["variant_types"][0]
            landing = params["landing_page"]

        result = sender.send_campaign([recipient], variant_type=vtype, landing_page=landing)
        sent_results.extend(result)

        # Record result in allocator
        if result and result[0].success:
            allocator.record_result(variant_id or "V1", success=True)

    # Print summary
    summary = sender.get_summary()
    stats = allocator.get_stats()

    print(f"\n📊 Campaign Results:")
    print(f"   Sent: {summary['total_sent']}")
    print(f"   Successful: {summary['successful']}")
    print(f"   Failed: {summary['failed']}")
    print()

    print("   Variant Performance (UCB):")
    for v, s in stats.items():
        print(f"     {v}: spent={s['budget_spent']:.1f}, conversions={s['conversions']}, "
              f"rate={s['conversion_rate']:.1f}%, UCB={s['ucb_score']:.4f}")

    # Save campaign data
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    campaign_data = {
        "campaign_id": campaign_id,
        "brief": campaign.get("brief", ""),
        "created_at": campaign.get("created", datetime.now().isoformat()),
        "type": params["campaign_type"].value,
        "segment": params["segment"].value if hasattr(params["segment"], "value") else str(params["segment"]),
        "variants": variants,
        "summary": summary,
        "allocator_stats": stats,
        "test_mode": test_mode,
    }

    output_path = DATA_DIR / f"{campaign_id}.json"
    with open(output_path, "w") as f:
        json.dump(campaign_data, f, indent=2)

    print(f"\n💾 Campaign data saved to: {output_path}")
    print(f"   Tracking server: http://127.0.0.1:{TRACKING_SERVER_PORT}")
    print(f"   Landing server:  http://127.0.0.1:{LANDING_SERVER_PORT}")
    print()

    return campaign_data


def get_status() -> None:
    """Show current campaign status and running servers."""
    print(f"\n📡 Campaign Agent Status")
    print(f"{'='*50}")

    # Check servers
    for key, proc in _server_processes.items():
        status = "running" if proc.poll() is None else "stopped"
        print(f"  {key}: {status} (pid={proc.pid})")

    # List saved campaigns
    if DATA_DIR.exists():
        campaigns = sorted(DATA_DIR.glob("*.json"), reverse=True)
        if campaigns:
            print(f"\n  Recent campaigns ({len(campaigns)}):")
            for f in campaigns[:5]:
                with open(f) as fp:
                    data = json.load(fp)
                print(f"    {data.get('campaign_id', '?')} — {data.get('type', '?')} "
                      f"({data.get('created_at', '?')[:10]})")
        else:
            print("\n  No campaigns saved yet.")
    else:
        print("\n  No campaigns saved yet.")

    print()


def get_report(campaign_id: str) -> None:
    """Print a detailed report for a campaign."""
    campaign_file = DATA_DIR / f"{campaign_id}.json"
    if not campaign_file.exists():
        print(f"❌ Campaign {campaign_id} not found.")
        print(f"   Available campaigns:")
        if DATA_DIR.exists():
            for f in sorted(DATA_DIR.glob("*.json"), reverse=True):
                print(f"     {f.name.replace('.json', '')}")
        else:
            print("     (none)")
        return

    with open(campaign_file) as f:
        data = json.load(f)

    print(f"\n📋 Campaign Report: {campaign_id}")
    print(f"{'='*60}")
    print(f"  Brief:      {data.get('brief', '(none)')}")
    print(f"  Type:       {data.get('type', '?')}")
    print(f"  Segment:    {data.get('segment', '?')}")
    print(f"  Created:    {data.get('created_at', '?')}")
    print()

    summary = data.get("summary", {})
    print(f"  Sent:       {summary.get('total_sent', 0)}")
    print(f"  Success:    {summary.get('successful', 0)}")
    print(f"  Failed:     {summary.get('failed', 0)}")
    print(f"  Test Mode:  {data.get('test_mode', False)}")
    print()

    stats = data.get("allocator_stats", {})
    if stats:
        print("  Variant Performance:")
        for v, s in stats.items():
            print(f"    {v}: conversions={s['conversions']}, "
                  f"rate={s['conversion_rate']:.1f}%, "
                  f"remaining={s['budget_remaining']:.1f}")
    print()


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="FreeAI Campaign Agent — Red Team Email Campaign Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--brief", type=str, help="Natural language campaign brief")
    parser.add_argument("--test", action="store_true", default=True,
                        help="Run in test mode (log only, no actual sends)")
    parser.add_argument("--live", action="store_true", help="Run live (send real emails)")
    parser.add_argument("--status", action="store_true", help="Show campaign agent status")
    parser.add_argument("--report", type=str, metavar="CAMPAIGN_ID",
                        help="Show detailed report for a campaign")
    parser.add_argument("--no-server", action="store_true",
                        help="Skip starting tracking/landing servers")
    parser.add_argument("--kill-servers", action="store_true",
                        help="Stop all background servers and exit")

    args = parser.parse_args()

    if args.kill_servers:
        stop_servers()
        print("All campaign servers stopped.")
        return

    if args.status:
        get_status()
        return

    if args.report:
        get_report(args.report)
        return

    if args.brief:
        campaign = create_campaign(args.brief)
        campaign_data = run_campaign(campaign, test_mode=not args.live)
        print(f"\n✅ Campaign complete: {campaign_data['campaign_id']}")
        if not args.live:
            print("   (test mode — no emails were sent)")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
