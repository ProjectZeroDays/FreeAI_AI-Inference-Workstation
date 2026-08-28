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
import re
import threading
import time
from pathlib import Path

def _secure_path(base: Path, user_path: str) -> Path | None:
    """Resolve user_path against base and verify it stays within base. Returns None if traversal detected."""
    try:
        safe_name = Path(user_path).name
        if not safe_name or safe_name != user_path.replace("/", "").replace("\\", "").replace("..", ""):
            return None
        result = base / safe_name
        base_str = str(base).rstrip("\\").rstrip("/")
        result_str = str(result).rstrip("\\").rstrip("/")
        if result_str.startswith(base_str + "\\"):
            return result
    except (OSError, ValueError):
        pass
    return None


def _sanitize_run_id(run_id: str) -> str:
    """Sanitize run_id to prevent path traversal when used as directory name."""
    if not run_id:
        return f"run_{int(time.time())}"
    # Strip any path separators and non-safe characters
    safe = re.sub(r'[^a-zA-Z0-9_\-]', '_', run_id)
    return safe if safe else f"run_{int(time.time())}"


def _safe_write(path: Path, content: str) -> None:
    """Safely write content to a known-fixed path (no user-controlled path component)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    run_id = _sanitize_run_id(run_id)
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
    _safe_write(output_dir / "ads.json", json.dumps(ads_data, indent=2))
    _safe_write(output_dir / "campaign_brief.md",
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
    run_id = _sanitize_run_id(run_id)

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
    _safe_write(output_dir / "leads.json", json.dumps(leads, indent=2))
    _safe_write(output_dir / "source.md",
        f"# Lead Collection: {source}\n\n"
        f"Params: {json.dumps(params, indent=2)}\n"
        f"Criteria: {criteria or 'Standard'}\n"
        f"Leads collected: {len(leads)}\n",
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
    run_id = _sanitize_run_id(run_id)
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
    _safe_write(output_dir / "pipeline.json", json.dumps({
        "product": product, "target_market": target_market,
        "goals": goals, "channels": channels,
        "results": results, "context": {k: v[:2000] for k, v in context.items()},
    }, indent=2))

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
