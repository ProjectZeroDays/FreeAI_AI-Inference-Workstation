#!/usr/bin/env python3
"""Pipeline Agents — ad generation, sales/lead collection, marketing pipelines.

Agents:
  ad_generator     - Create ad copy, images, video scripts, landing pages
  lead_collector   - Scrape, qualify, and organize leads from multiple sources
  marketing_pipeline - End-to-end marketing automation: awareness → conversion

Each agent produces artifacts (copy, media plans, lead lists) and can
orchestrate multi-step campaigns through the workflow engine.
"""
import json
import os
import threading
import time
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

import requests

ROOT = Path(__file__).parent.parent
WORKSPACES_DIR = ROOT / "workspaces" / "pipelines"
WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)

AGENT_API = os.environ.get("AGENT_API", "http://localhost:8020")
ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:8100/proxy")

_PIPELINE_LOCK = threading.Lock()
_PIPELINE_RUNS = {}

# ── Pipeline agent definitions ───────────────────────────────────────
PIPELINE_AGENTS = {
    "ad_generator": {
        "model": "claude-sonnet-4-5",
        "description": "Generate ad copy, creative briefs, landing pages, and video scripts",
        "profile": "creative",
    },
    "lead_collector": {
        "model": "gemini-2.5-flash",
        "description": "Scrape, qualify, enrich, and organize leads from websites and APIs",
        "profile": "balanced",
    },
    "marketing_pipeline": {
        "model": "claude-sonnet-4-5",
        "description": "Orchestrate full marketing campaigns from awareness to conversion",
        "profile": "creative",
    },
}

# ── Ad formats ────────────────────────────────────────────────────────
AD_FORMATS = {
    "google_search": {
        "description": "Google Search ads (text)",
        "fields": ["headline_1", "headline_2", "headline_3", "description_1", "description_2", "display_path", "final_url"],
        "constraints": {"max_headline_chars": 30, "max_desc_chars": 90},
    },
    "google_display": {
        "description": "Google Display ads (image)",
        "fields": ["headline", "description", "cta", "image_prompt", "final_url", "background_color"],
        "constraints": {"max_headline_chars": 25, "max_desc_chars": 50},
    },
    "facebook_feed": {
        "description": "Facebook/Instagram feed ad",
        "fields": ["primary_text", "headline", "description", "cta", "image_prompt", "video_script", "final_url"],
        "constraints": {"max_primary_chars": 125, "max_headline_chars": 40},
    },
    "linkedin_sponsor": {
        "description": "LinkedIn Sponsored Content",
        "fields": ["headline", "body_text", "cta", "image_prompt", "final_url", "audience_hint"],
        "constraints": {"max_headline_chars": 70, "max_body_chars": 150},
    },
    "youtube_prejoin": {
        "description": "YouTube pre-roll video ad",
        "fields": ["hook_3s", "value_prop", "cta", "script_15s", "script_30s", "script_60s", "thumbnail_prompt"],
        "constraints": {},
    },
    "twitter_x": {
        "description": "X/Twitter promoted tweet",
        "fields": ["text", "image_prompt", "video_script", "cta", "hashtags", "final_url"],
        "constraints": {"max_text_chars": 280, "max_hashtags": 2},
    },
    "email_campaign": {
        "description": "Email marketing campaign",
        "fields": ["subject_line", "preview_text", "header_text", "body_copy", "cta_text", "cta_url", "footer"],
        "constraints": {"max_subject_chars": 50},
    },
    "landing_page": {
        "description": "Dedicated landing page for conversion",
        "fields": ["headline", "subheadline", "benefits", "testimonials", "cta_sections", "faq"],
        "constraints": {},
    },
}

# ── Lead sources ──────────────────────────────────────────────────────
LEAD_SOURCES = {
    "web_scrape": {
        "description": "Scrape leads from target websites",
        "params": ["url", "selectors", "pagination", "filters"],
    },
    "linkedin": {
        "description": "LinkedIn prospecting via company/role search",
        "params": ["company", "title_keywords", "location", "seniority"],
    },
    "crunchbase": {
        "description": "Funding and company intelligence",
        "params": ["industry", "funding_stage", "company_size", "location"],
    },
    "events": {
        "description": "Conference and event attendee lists",
        "params": ["event_name", "year", "attendee_list_url"],
    },
    "competitor_sites": {
        "description": "Find prospects from competitor customer lists",
        "params": ["competitor_domain", "review_sites", "keywords"],
    },
}


# ── LLM helpers ───────────────────────────────────────────────────────
def _call_llm(prompt, model=None, max_tokens=4096, temperature=0.5):
    import requests
    url = PROXY_URL if "/proxy" in PROXY_URL else f"{PROXY_URL.rsplit('/', 1)[0]}/proxy"
    payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}
    if model:
        payload["model"] = model
    try:
        r = requests.post(url, json=payload, timeout=660)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        try:
            r2 = requests.post(ROUTER_URL, json={
                "prompt": prompt, "max_tokens": max_tokens, "temperature": temperature},
                timeout=660)
            r2.raise_for_status()
            return r2.json()
        except Exception:
            raise HTTPException(status_code=502, detail=f"LLM unavailable: {exc}")


def _extract_text(result):
    resp = result.get("response", {})
    if isinstance(resp, dict):
        return resp.get("content", "") or str(resp.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return str(resp)


# ── Ad generator ──────────────────────────────────────────────────────
def generate_ads(product, target_audience, platforms, brand_voice="professional",
                 run_id=None):
    """Generate ad copy for multiple platforms."""
    run_id = run_id or f"ads_{int(time.time())}"
    platforms_str = ", ".join(platforms)

    prompt = f"""You are a senior copywriter and media strategist.

PRODUCT: {product}
TARGET AUDIENCE: {target_audience}
PLATFORMS: {platforms_str}
BRAND VOICE: {brand_voice}

For each platform, generate complete ad creatives following the format specs:

PLATFORMS TO COVER:
"""
    for plat in platforms:
        plat_lower = plat.lower()
        for fmt_key, fmt_info in AD_FORMATS.items():
            if plat_lower in fmt_key or fmt_key in plat_lower:
                prompt += f"\n\n### {fmt_info['description']}\n"
                prompt += f"Fields needed: {', '.join(fmt_info['fields'])}\n"
                if fmt_info.get("constraints"):
                    prompt += f"Constraints: {fmt_info['constraints']}\n"
                prompt += "Generate the ad copy now.\n"

    prompt += """
Format your output as JSON:
{
  "campaign": {
    "name": "...",
    "platforms": {
      "<platform>": {
        "creative_brief": "...",
        "variants": [
          {"name": "A/B variant 1", "fields": {...}},
          {"name": "A/B variant 2", "fields": {...}}
        ]
      }
    }
  }
}
"""
    result = _call_llm(prompt, model=PIPELINE_AGENTS["ad_generator"]["model"],
                       max_tokens=8192, temperature=0.7)
    text = _extract_text(result)

    # Parse and save
    try:
        ads_data = json.loads(text)
    except json.JSONDecodeError:
        ads_data = {"raw": text, "parsed": False}

    output_dir = WORKSPACES_DIR / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ads.json").write_text(json.dumps(ads_data, indent=2), encoding="utf-8")
    (output_dir / "campaign_brief.md").write_text(
        f"# Campaign: {ads_data.get('campaign', {}).get('name', run_id)}\n\n"
        f"Product: {product}\nTarget: {target_audience}\n\n"
        f"Generated: {time.strftime('%Y-%m-%d %H:%M')}\n",
        encoding="utf-8",
    )

    record = {
        "run_id": run_id,
        "product": product,
        "target_audience": target_audience,
        "platforms": platforms,
        "brand_voice": brand_voice,
        "status": "done",
        "workspace": str(output_dir),
        "created_at": time.time(),
    }
    with _PIPELINE_LOCK:
        _PIPELINE_RUNS[run_id] = record
    return record


# ── Lead collector ────────────────────────────────────────────────────
def collect_leads(source, params, criteria=None, run_id=None):
    """Collect and qualify leads from a source."""
    run_id = run_id or f"leads_{int(time.time())}"

    source_info = LEAD_SOURCES.get(source, {})
    prompt = f"""You are a lead generation specialist.

TASK: Collect and qualify leads from {source}
SOURCE_PARAMS: {json.dumps(params)}
QUALIFICATION CRITERIA: {criteria or 'High intent, decision-maker, fits ICP'}

For each lead, extract:
- Name / Company
- Email (if available)
- Phone (if available)
- Title / Role
- Company size
- Lead score (1-100)
- Source
- Notes

Output as JSON array:
[
  {{"name": "...", "company": "...", "email": "...", "title": "...",
     "lead_score": 85, "source": "{source}", "notes": "..."}}
]

Aim for 10-30 high-quality leads. Quality over quantity."""

    result = _call_llm(prompt, model=PIPELINE_AGENTS["lead_collector"]["model"],
                       max_tokens=4096, temperature=0.1)
    text = _extract_text(result)

    try:
        leads = json.loads(text)
        if isinstance(leads, dict):
            leads = [leads]
    except json.JSONDecodeError:
        leads = [{"raw_output": text, "count": 0}]

    output_dir = WORKSPACES_DIR / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "leads.json").write_text(json.dumps(leads, indent=2), encoding="utf-8")
    (output_dir / "source.md").write_text(
        f"# Lead Collection: {source}\n\n"
        f"Params: {json.dumps(params, indent=2)}\n"
        f"Criteria: {criteria or 'Standard'}\n"
        f"Leads collected: {len(leads)}\n",
        encoding="utf-8",
    )

    record = {
        "run_id": run_id,
        "source": source,
        "params": params,
        "criteria": criteria,
        "lead_count": len(leads),
        "status": "done",
        "workspace": str(output_dir),
        "created_at": time.time(),
    }
    with _PIPELINE_LOCK:
        _PIPELINE_RUNS[run_id] = record
    return record


# ── Marketing pipeline ────────────────────────────────────────────────
def run_marketing_pipeline(product, target_market, goals, channels=None,
                           budget=None, run_id=None):
    """Run a full marketing pipeline: strategy → creative → distribution → measurement."""
    run_id = run_id or f"mktg_{int(time.time())}"
    channels = channels or ["google", "facebook", "email", "linkedin"]

    pipeline_phases = [
        ("strategy", "Marketing Strategy", """
You are a CMO. Design a marketing strategy.

Product: {product}
Target market: {target_market}
Goals: {goals}
Budget: {budget or ' TBD'}

Deliver:
1. ICP (Ideal Customer Profile)
2. Channel mix recommendation with rationale
3. Key messaging pillars
4. KPI targets per channel
5. 90-day rollout plan
"""),
        ("creative", "Creative Production", """
Using this strategy:
{strategy}

Generate:
1. Ad copy for: {channels}
2. Email sequence (5 emails: welcome, nurture, offer, reminder, win-back)
3. Landing page brief
4. Social media content calendar (30 days)
"""),
        ("distribution", "Distribution Plan", """
Execute this distribution plan:
{creative}

For each channel, specify:
1. Exact posting schedule
2. Budget allocation
3. A/B test plan
4. Conversion tracking setup
5. Retargeting strategy
"""),
        ("measurement", "Measurement Framework", """
Set up measurement for:
{channels}

Include:
1. Dashboard metrics per channel
2. Attribution model recommendation
3. Reporting cadence
4. Optimization triggers
5. Budget reallocation rules
"""),
    ]

    context = {}
    results = {}
    for phase_id, phase_name, phase_prompt_template in pipeline_phases:
        prompt = phase_prompt_template
        for k, v in context.items():
            prompt = prompt.replace(f"{{{k}}}", str(v)[:3000])
        prompt = prompt.format(product=product, target_market=target_market,
                               goals=goals, channels=", ".join(channels),
                               budget=budget or "TBD")

        result = _call_llm(prompt, model=PIPELINE_AGENTS["marketing_pipeline"]["model"],
                           max_tokens=8192, temperature=0.5)
        text = _extract_text(result)
        context[phase_id] = text
        results[phase_id] = {"status": "done", "tokens": len(text)}

    output_dir = WORKSPACES_DIR / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "pipeline.json").write_text(json.dumps({
        "product": product, "target_market": target_market,
        "goals": goals, "channels": channels,
        "results": results, "context": {k: v[:2000] for k, v in context.items()},
    }, indent=2), encoding="utf-8")

    record = {
        "run_id": run_id,
        "product": product,
        "target_market": target_market,
        "goals": goals,
        "channels": channels,
        "status": "done",
        "workspace": str(output_dir),
        "created_at": time.time(),
    }
    with _PIPELINE_LOCK:
        _PIPELINE_RUNS[run_id] = record
    return record


# ── FastAPI ───────────────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="Pipeline Agents API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class AdRequest(BaseModel):
        product: str
        target_audience: str
        platforms: list[str]
        brand_voice: str = "professional"
        run_id: Optional[str] = None

    class LeadRequest(BaseModel):
        source: str
        params: dict
        criteria: Optional[str] = None
        run_id: Optional[str] = None

    class MarketingRequest(BaseModel):
        product: str
        target_market: str
        goals: str
        channels: Optional[list[str]] = None
        budget: Optional[str] = None
        run_id: Optional[str] = None

    @app.get("/health")
    def health():
        return {"status": "ok", "pipelines": list(PIPELINE_AGENTS.keys())}

    @app.get("/pipelines")
    def list_pipelines():
        return {name: {"description": info["description"],
                       "model": info["model"]}
                for name, info in PIPELINE_AGENTS.items()}

    @app.get("/ad-formats")
    def ad_formats():
        return {k: v["description"] for k, v in AD_FORMATS.items()}

    @app.get("/lead-sources")
    def lead_sources():
        return {k: v["description"] for k, v in LEAD_SOURCES.items()}

    @app.post("/pipeline/ads")
    def ads(req: AdRequest):
        return generate_ads(req.product, req.target_audience, req.platforms,
                            req.brand_voice, req.run_id)

    @app.post("/pipeline/leads")
    def leads(req: LeadRequest):
        return collect_leads(req.source, req.params, req.criteria, req.run_id)

    @app.post("/pipeline/marketing")
    def marketing(req: MarketingRequest):
        return run_marketing_pipeline(req.product, req.target_market, req.goals,
                                      req.channels, req.budget, req.run_id)

    @app.get("/pipeline/runs")
    def list_runs():
        with _PIPELINE_LOCK:
            runs = list(_PIPELINE_RUNS.values())
        return {"runs": runs, "total": len(runs)}

    @app.get("/pipeline/run/{run_id}")
    def get_run(run_id: str):
        with _PIPELINE_LOCK:
            run = _PIPELINE_RUNS.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return run


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("PIPELINE_PORT", "8181"))
        print(f"[pipeline-agents] Starting on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[pipeline-agents] FastAPI not available. Use functions directly.")
