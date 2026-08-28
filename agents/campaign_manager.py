#!/usr/bin/env python3
"""Campaign Lifecycle Manager + Ad/Lead Pipeline Manager.

Manages campaigns from creation through execution to retirement.
Tracks budget, performance, and leads generated per campaign.
Integrates with builder_agents and pipeline_agents for end-to-end operations.
"""
import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

import requests

ROOT = Path(__file__).parent.parent
DB_DIR = ROOT / "data" / "campaigns"
DB_DIR.mkdir(parents=True, exist_ok=True)
CAMPAIGN_DB = DB_DIR / "campaigns.json"

_CAMPAIGN_LOCK = threading.Lock()
_CAMPAIGNS = {}

# ── Campaign lifecycle states ─────────────────────────────────────────
LIFECYCLE_STATES = ["draft", "planning", "active", "paused", "completed", "archived"]
LIFECYCLE_TRANSITIONS = {
    "draft": ["planning", "archived"],
    "planning": ["active", "draft"],
    "active": ["paused", "completed"],
    "paused": ["active", "completed"],
    "completed": ["archived"],
    "archived": [],
}

# ── Campaign types ────────────────────────────────────────────────────
CAMPAIGN_TYPES = {
    "product_launch": {"description": "New product or feature launch", "default_channels": ["email", "social", "ppc"]},
    "seasonal": {"description": "Holiday or seasonal promotion", "default_channels": ["email", "social", "display"]},
    "lead_gen": {"description": "Lead generation campaign", "default_channels": ["linkedin", "google", "email"]},
    "retention": {"description": "Customer retention / re-engagement", "default_channels": ["email", "sms", "push"]},
    "brand_awareness": {"description": "Brand awareness and reach", "default_channels": ["social", "display", "video"]},
    "webinar": {"description": "Webinar or event campaign", "default_channels": ["email", "linkedin", "social"]},
}


# ── Core data model ───────────────────────────────────────────────────
def _load_db():
    if CAMPAIGN_DB.exists():
        try:
            return json.loads(CAMPAIGN_DB.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_db(db):
    CAMPAIGN_DB.write_text(json.dumps(db, indent=2, default=str), encoding="utf-8")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ── Campaign operations ───────────────────────────────────────────────
def create_campaign(name, campaign_type, budget=None, start_date=None,
                    end_date=None, channels=None, description="", owner=""):
    """Create a new campaign in draft state."""
    cam_type = CAMPAIGN_TYPES.get(campaign_type, {})
    cid = f"camp_{int(time.time())}_{os.getpid()}"
    campaign = {
        "id": cid,
        "name": name,
        "type": campaign_type,
        "type_description": cam_type.get("description", ""),
        "status": "draft",
        "budget": budget,
        "budget_spent": 0,
        "start_date": start_date or _now_iso(),
        "end_date": end_date,
        "channels": channels or cam_type.get("default_channels", ["email"]),
        "description": description,
        "owner": owner,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "metrics": {"impressions": 0, "clicks": 0, "leads": 0, "conversions": 0, "revenue": 0},
        "ads": [],
        "leads": [],
        "artifacts": {},
        "lifecycle_log": [{"state": "draft", "timestamp": _now_iso(), "note": "Created"}],
    }
    with _CAMPAIGN_LOCK:
        _CAMPAIGNS[cid] = campaign
        _load_db()[cid] = campaign
        _save_db(_load_db())
    return campaign


def get_campaign(campaign_id):
    with _CAMPAIGN_LOCK:
        return _CAMPAIGNS.get(campaign_id)


def list_campaigns(status=None, owner=None):
    with _CAMPAIGN_LOCK:
        campaigns = list(_CAMPAIGNS.values())
    if status:
        campaigns = [c for c in campaigns if c["status"] == status]
    if owner:
        campaigns = [c for c in campaigns if c.get("owner") == owner]
    return campaigns


def transition_campaign(campaign_id, new_state, note=""):
    """Move campaign to a new lifecycle state."""
    with _CAMPAIGN_LOCK:
        camp = _CAMPAIGNS.get(campaign_id)
        if not camp:
            raise ValueError(f"Campaign not found: {campaign_id}")
        current = camp["status"]
        allowed = LIFECYCLE_TRANSITIONS.get(current, [])
        if new_state not in allowed:
            raise ValueError(f"Cannot transition from '{current}' to '{new_state}'. "
                             f"Allowed: {allowed}")
        camp["status"] = new_state
        camp["updated_at"] = _now_iso()
        camp["lifecycle_log"].append({
            "state": new_state, "timestamp": _now_iso(), "note": note,
        })
        _save_db(_load_db())
    return camp


def add_ad_to_campaign(campaign_id, ad_data):
    """Add an ad creative to a campaign."""
    with _CAMPAIGN_LOCK:
        camp = _CAMPAIGNS.get(campaign_id)
        if not camp:
            raise ValueError(f"Campaign not found: {campaign_id}")
        ad_id = f"ad_{int(time.time())}"
        ad = {"id": ad_id, **ad_data, "added_at": _now_iso()}
        camp["ads"].append(ad)
        camp["updated_at"] = _now_iso()
        _save_db(_load_db())
    return ad


def add_leads_to_campaign(campaign_id, leads):
    """Add collected leads to a campaign."""
    with _CAMPAIGN_LOCK:
        camp = _CAMPAIGNS.get(campaign_id)
        if not camp:
            raise ValueError(f"Campaign not found: {campaign_id}")
        for lead in (leads if isinstance(leads, list) else [leads]):
            lead["campaign_id"] = campaign_id
            lead["added_at"] = _now_iso()
            camp["leads"].append(lead)
            camp["metrics"]["leads"] = len(camp["leads"])
        camp["updated_at"] = _now_iso()
        _save_db(_load_db())
    return camp["metrics"]["leads"]


def update_metrics(campaign_id, metrics_delta):
    """Update campaign metrics (impressions, clicks, etc.)."""
    with _CAMPAIGN_LOCK:
        camp = _CAMPAIGNS.get(campaign_id)
        if not camp:
            raise ValueError(f"Campaign not found: {campaign_id}")
        for key, value in metrics_delta.items():
            if key in camp["metrics"]:
                camp["metrics"][key] += value
        camp["updated_at"] = _now_iso()
        _save_db(_load_db())
    return camp["metrics"]


def build_campaign_assets(campaign_id, force_rebuild=False):
    """Use builder/pipeline agents to generate campaign assets."""
    with _CAMPAIGN_LOCK:
        camp = dict(_CAMPAIGNS.get(campaign_id, {}))
    if not camp:
        raise ValueError(f"Campaign not found: {campaign_id}")

    results = {}

    # Try to import and use builder/pipeline agents
    try:
        from agents.builder_agents import scaffold_builder, scaffold_business
        from agents.pipeline_agents import generate_ads, collect_leads
    except ImportError:
        return {"error": "builder_agents or pipeline_agents not available",
                "campaign_id": campaign_id}

    # Generate ads for the campaign
    if "ads" not in camp.get("artifacts", {}) or force_rebuild:
        ad_result = generate_ads(
            product=camp.get("description", camp["name"]),
            target_audience="customers in this campaign",
            platforms=camp.get("channels", ["email", "social"]),
            run_id=f"{campaign_id}_ads",
        )
        results["ads"] = ad_result

    # Collect leads if lead_gen type
    if camp["type"] == "lead_gen" and "leads" not in camp.get("artifacts", {}) or force_rebuild:
        lead_result = collect_leads(
            source="web_scrape",
            params={"query": camp["name"]},
            run_id=f"{campaign_id}_leads",
        )
        results["leads"] = lead_result

    # Build a landing page if website builder available
    if "landing_page" not in camp.get("artifacts", {}) or force_rebuild:
        try:
            page_result = scaffold_builder(
                "website",
                spec=camp.get("description", f"Landing page for {camp['name']}"),
                run_id=f"{campaign_id}_landing",
            )
            results["landing_page"] = page_result
        except Exception:
            pass

    # Store artifacts
    with _CAMPAIGN_LOCK:
        camp["artifacts"] = {**camp.get("artifacts", {}), **{k: v.get("workspace", "") for k, v in results.items()}}
        camp["updated_at"] = _now_iso()
        _CAMPAIGNS[campaign_id] = camp
        _save_db(_load_db())

    return results


def delete_campaign(campaign_id):
    with _CAMPAIGN_LOCK:
        _CAMPAIGNS.pop(campaign_id, None)
        db = _load_db()
        db.pop(campaign_id, None)
        _save_db(db)
    return True


# ── FastAPI ───────────────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="Campaign Manager API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class CreateCampaignRequest(BaseModel):
        name: str
        campaign_type: str
        budget: Optional[float] = None
        start_date: Optional[str] = None
        end_date: Optional[str] = None
        channels: Optional[list[str]] = None
        description: str = ""
        owner: str = ""

    class TransitionRequest(BaseModel):
        new_state: str
        note: str = ""

    class AdRequest(BaseModel):
        creative: dict
        platform: str
        variant: str = "A"

    class LeadBatchRequest(BaseModel):
        leads: list[dict]

    class MetricsRequest(BaseModel):
        impressions: Optional[int] = None
        clicks: Optional[int] = None
        leads: Optional[int] = None
        conversions: Optional[int] = None
        revenue: Optional[float] = None

    @app.get("/health")
    def health():
        return {"status": "ok", "campaigns": len(_CAMPAIGNS),
                "types": list(CAMPAIGN_TYPES.keys())}

    @app.get("/campaigns")
    def campaigns(status: Optional[str] = None, owner: Optional[str] = None):
        return list_campaigns(status=status, owner=owner)

    @app.get("/campaigns/{campaign_id}")
    def campaign(campaign_id: str):
        camp = get_campaign(campaign_id)
        if not camp:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return camp

    @app.post("/campaigns")
    def create(req: CreateCampaignRequest):
        return create_campaign(req.name, req.campaign_type, req.budget,
                               req.start_date, req.end_date, req.channels,
                               req.description, req.owner)

    @app.post("/campaigns/{campaign_id}/transition")
    def transition(campaign_id: str, req: TransitionRequest):
        try:
            return transition_campaign(campaign_id, req.new_state, req.note)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/campaigns/{campaign_id}/ads")
    def add_ad(campaign_id: str, req: AdRequest):
        try:
            return add_ad_to_campaign(campaign_id, req.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @app.post("/campaigns/{campaign_id}/leads")
    def add_leads(campaign_id: str, req: LeadBatchRequest):
        try:
            return {"lead_count": add_leads_to_campaign(campaign_id, req.leads)}
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @app.post("/campaigns/{campaign_id}/metrics")
    def update_metrics_endpoint(campaign_id: str, req: MetricsRequest):
        try:
            return update_metrics(campaign_id, req.model_dump(exclude_none=True))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @app.post("/campaigns/{campaign_id}/build")
    def build_assets(campaign_id: str, force: bool = False):
        try:
            return build_campaign_assets(campaign_id, force_rebuild=force)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @app.delete("/campaigns/{campaign_id}")
    def remove(campaign_id: str):
        delete_campaign(campaign_id)
        return {"status": "deleted"}

    @app.get("/campaign-types")
    def campaign_types():
        return {k: v["description"] for k, v in CAMPAIGN_TYPES.items()}


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("CAMPAIGN_PORT", "8182"))
        print(f"[campaign-manager] Starting on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[campaign-manager] FastAPI not available. Use functions directly.")
