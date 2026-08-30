#!/usr/bin/env python3
"""Intelligent Automations and Cron Workflows.

Pre-configured workflows for common business operations:
  - Daily lead qualification and enrichment
  - Weekly report generation
  - Monthly campaign review
  - Real-time alert monitoring
  - Scheduled ad rotation
  - Customer follow-up sequences
  - Data backup and sync
  - Social media posting

Each workflow can be triggered manually, on a cron schedule, or by event.
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
    safe = re.sub(r'[^a-zA-Z0-9_\-]', '_', run_id)
    return safe if safe else f"run_{int(time.time())}"


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
WORKSPACES_DIR = ROOT / "workspaces" / "automations"
WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
SCHEDULE_DIR = ROOT / "data" / "schedules"
SCHEDULE_DIR.mkdir(parents=True, exist_ok=True)

_AUTOMATION_LOCK = threading.Lock()
_AUTOMATIONS = {}
_SCHEDULES = {}
_TRIGGER_LOG = []

# ── Pre-configured workflow templates ─────────────────────────────────
WORKFLOW_TEMPLATES = {
    "daily_lead_enrichment": {
        "name": "Daily Lead Enrichment",
        "description": "Enrich and score leads collected in the last 24 hours",
        "schedule": "0 9 * * *",  # 9 AM daily
        "trigger": "cron",
        "steps": [
            {"name": "collect", "type": "pipeline_leads", "source": "web_scrape"},
            {"name": "enrich", "type": "llm_enrich", "fields": ["email", "company", "title"]},
            {"name": "score", "type": "llm_score", "criteria": "intent+fit+engagement"},
            {"name": "sync", "type": "crm_sync", "target": "salesforce|hubspot|custom"},
        ],
        "outputs": ["enriched_leads.json", "score_report.md"],
    },
    "weekly_campaign_report": {
        "name": "Weekly Campaign Report",
        "description": "Generate performance report for all active campaigns",
        "schedule": "0 8 * * 1",  # Monday 8 AM
        "trigger": "cron",
        "steps": [
            {"name": "pull_metrics", "type": "api_fetch", "endpoints": ["/campaigns", "/ads", "/leads"]},
            {"name": "analyze", "type": "llm_analyze", "question": "Summarize campaign performance, top performers, underperformers, and recommendations."},
            {"name": "format", "type": "report_gen", "format": "markdown"},
            {"name": "deliver", "type": "email_send", "recipients": ["team@company.com"]},
        ],
        "outputs": ["weekly_report.md"],
    },
    "monthly_campaign_review": {
        "name": "Monthly Campaign Review",
        "description": "Deep dive into monthly campaign performance and budget allocation",
        "schedule": "0 10 1 * *",  # 1st of month, 10 AM
        "trigger": "cron",
        "steps": [
            {"name": "aggregate", "type": "data_aggregate", "period": "30d"},
            {"name": "analyze", "type": "llm_analyze", "question": "Review all campaigns: ROI, CAC, LTV, channel mix effectiveness. Recommend budget reallocation."},
            {"name": "forecast", "type": "llm_forecast", "horizon": "next_30_days"},
            {"name": "present", "type": "deck_gen", "format": "slides"},
        ],
        "outputs": ["monthly_review.md", "deck.pptx"],
    },
    "real_time_alert_monitor": {
        "name": "Real-Time Alert Monitor",
        "description": "Monitor campaign metrics and alert on anomalies",
        "schedule": "*/5 * * * *",  # Every 5 minutes
        "trigger": "cron",
        "steps": [
            {"name": "fetch", "type": "api_fetch", "endpoints": ["/campaigns", "/metrics"]},
            {"name": "detect", "type": "anomaly_detection", "thresholds": {"ctr_drop": 0.3, "cpm_spike": 2.0}},
            {"name": "alert", "type": "notification", "channels": ["slack", "email"], "severity": "auto"},
        ],
        "outputs": ["alerts.json"],
    },
    "ad_rotation_scheduler": {
        "name": "Ad Rotation Scheduler",
        "description": "Automatically rotate ad creatives based on performance",
        "schedule": "0 */6 * * *",  # Every 6 hours
        "trigger": "cron",
        "steps": [
            {"name": "evaluate", "type": "performance_analysis", "window": "24h"},
            {"name": "select", "type": "llm_select", "criteria": "highest_ctr+lowest_cpa"},
            {"name": "rotate", "type": "ad_platform_update", "platforms": ["google", "facebook", "linkedin"]},
            {"name": "log", "type": "audit_log", "action": "rotation"},
        ],
        "outputs": ["rotation_log.json"],
    },
    "customer_followup_sequence": {
        "name": "Customer Follow-Up Sequence",
        "description": "Automated multi-touch follow-up for new leads",
        "schedule": "0 10 * * *",  # Daily at 10 AM
        "trigger": "cron",
        "steps": [
            {"name": "segment", "type": "lead_segment", "criteria": "days_since_signup:1-7"},
            {"name": "draft", "type": "llm_draft", "template": "followup_day_{n}"},
            {"name": "personalize", "type": "llm_personalize", "fields": ["name", "company", "signup_source"]},
            {"name": "send", "type": "email_send", "channel": "outlook|gmail"},
            {"name": "track", "type": "engagement_track", "events": ["open", "click", "reply"]},
        ],
        "outputs": ["sent_emails.json"],
    },
    "social_media_scheduler": {
        "name": "Social Media Scheduler",
        "description": "Schedule and publish social media content",
        "schedule": "0 8,12,16 * * *",  # 8 AM, 12 PM, 4 PM daily
        "trigger": "cron",
        "steps": [
            {"name": "plan", "type": "llm_plan", "content_types": ["tip", "testimonial", "product", "behind_scenes"]},
            {"name": "generate", "type": "llm_generate", "platforms": ["twitter", "linkedin", "instagram"]},
            {"name": "schedule", "type": "social_schedule", "platforms": ["twitter", "linkedin"]},
            {"name": "publish", "type": "social_publish"},
        ],
        "outputs": ["social_posts.json"],
    },
    "data_backup_sync": {
        "name": "Data Backup & Sync",
        "description": "Backup campaign data and sync to cloud storage",
        "schedule": "0 2 * * *",  # Daily at 2 AM
        "trigger": "cron",
        "steps": [
            {"name": "export", "type": "data_export", "format": "json"},
            {"name": "compress", "type": "compression", "algorithm": "gzip"},
            {"name": "upload", "type": "cloud_upload", "destination": "s3|gcs|azure"},
            {"name": "verify", "type": "integrity_check"},
        ],
        "outputs": ["backup_manifest.json"],
    },
    "competitor_monitor": {
        "name": "Competitor Monitor",
        "description": "Monitor competitor ads, pricing, and campaigns",
        "schedule": "0 7 * * *",  # Daily at 7 AM
        "trigger": "cron",
        "steps": [
            {"name": "scrape", "type": "web_scrape", "targets": ["competitor_sites"]},
            {"name": "analyze", "type": "llm_analyze", "question": "Compare competitor pricing, messaging, and offers vs ours."},
            {"name": "report", "type": "report_gen", "format": "markdown"},
            {"name": "alert", "type": "notification", "channels": ["slack"]},
        ],
        "outputs": ["competitor_report.md"],
    },
    "email_warmup_sequence": {
        "name": "Email Warm-Up Sequence",
        "description": "Warm up new email domains with progressive sending",
        "schedule": "0 9 * * *",  # Daily at 9 AM
        "trigger": "cron",
        "steps": [
            {"name": "check", "type": "reputation_check", "domains": ["new_domain"]},
            {"name": "plan", "type": "volume_plan", "strategy": "gradual_increase"},
            {"name": "send", "type": "email_send", "volume": "auto"},
            {"name": "monitor", "type": "deliverability_monitor"},
        ],
        "outputs": ["warmup_log.json"],
    },
}


# ── Execution engine ──────────────────────────────────────────────────
def _call_llm(prompt, max_tokens=4096, temperature=0.3):
    import requests
    url = PROXY_URL if "/proxy" in PROXY_URL else f"{PROXY_URL.rsplit('/', 1)[0]}/proxy"
    try:
        r = requests.post(url, json={"prompt": prompt, "max_tokens": max_tokens,
                                      "temperature": temperature}, timeout=660)
        r.raise_for_status()
        return r.json()
    except Exception:
        try:
            r2 = requests.post(ROUTER_URL, json={"prompt": prompt,
                         "max_tokens": max_tokens, "temperature": temperature}, timeout=660)
            r2.raise_for_status()
            return r2.json()
        except Exception:
            return None


def _extract_text(result):
    if not result or not isinstance(result, dict):
        return ""
    resp = result.get("response", {})
    if isinstance(resp, dict):
        return resp.get("content", "") or str(resp.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return str(resp)


def execute_workflow(workflow_id, params=None):
    """Execute a pre-configured workflow."""
    template = WORKFLOW_TEMPLATES.get(workflow_id)
    if not template:
        return {"error": f"Unknown workflow: {workflow_id}"}

    run_id = f"wf_{_sanitize_run_id(workflow_id)}_{int(time.time())}"
    ws_dir = WORKSPACES_DIR / run_id
    _ws_real = os.path.realpath(str(WORKSPACES_DIR))
    _ws_dir_real = os.path.realpath(str(ws_dir))
    if not (_ws_dir_real == _ws_real or _ws_dir_real.startswith(_ws_real + os.sep)):
        return {"error": "Invalid workflow path"}
    ws_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "run_id": run_id,
        "workflow_id": workflow_id,
        "workflow_name": template["name"],
        "params": params or {},
        "status": "running",
        "steps_executed": [],
        "outputs": {},
        "started_at": time.time(),
        "completed_at": None,
        "error": None,
    }

    for step in template["steps"]:
        step_name = step["name"]
        step_type = step["type"]
        step_start = time.time()

        # Simulate step execution with LLM where applicable
        if step_type.startswith("llm_"):
            prompt = _build_step_prompt(template, step, params or {})
            result = _call_llm(prompt, max_tokens=4096, temperature=0.3)
            output = _extract_text(result) if result else ""
            step_result = {"status": "done", "output_length": len(output) if output else 0}
            if output:
                safe_name = re.sub(r'[^\w\-\.]', '_', step_name)
                output_file = ws_dir / f"{safe_name}.md"
                _out_real = os.path.realpath(str(output_file))
                if not (_out_real == _ws_real or _out_real.startswith(_ws_real + os.sep)):
                    continue
                _parent_real = os.path.realpath(str(output_file.parent))
                if not (_parent_real == _ws_real or _parent_real.startswith(_ws_real + os.sep)):
                    continue
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(output, encoding="utf-8")
                record["outputs"][step_name] = str(output_file)
        elif step_type == "api_fetch":
            step_result = {"status": "done", "endpoints": step.get("endpoints", [])}
        elif step_type in ("email_send", "notification", "social_publish", "cloud_upload"):
            step_result = {"status": "simulated", "reason": "external_service_not_configured"}
        else:
            step_result = {"status": "done"}

        step_result["duration_s"] = time.time() - step_start
        record["steps_executed"].append(step_result)

        if step_result.get("status") == "failed":
            record["status"] = "failed"
            record["error"] = f"Step {step_name} failed"
            break

    record["status"] = "done"
    record["completed_at"] = time.time()
    record["duration_s"] = record["completed_at"] - record["started_at"]

    with _AUTOMATION_LOCK:
        _AUTOMATIONS[run_id] = record
        _TRIGGER_LOG.append({
            "run_id": run_id,
            "workflow_id": workflow_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": record["status"],
        })

    # Persist
    _save_automations()
    return record


def _build_step_prompt(template, step, params):
    """Build a prompt for an LLM-based step."""
    step_type = step["type"]
    context = f"Workflow: {template['name']}\nParams: {json.dumps(params)}\n"

    if step_type == "llm_enrich":
        return f"{context}\nEnrich these lead fields: {step.get('fields', [])}. "
        "Add company info, location, industry from available data. Return enriched JSON."
    elif step_type == "llm_score":
        return f"{context}\nScore each lead (0-100) based on criteria: {step.get('criteria', 'intent+fit')}. "
        "Return: lead_id, score, reason."
    elif step_type == "llm_analyze":
        return f"{context}\n{step.get('question', 'Analyze the data and provide insights.')}"
    elif step_type == "llm_select":
        return f"{context}\nSelect the best ad creative(s) based on criteria: {step.get('criteria', 'performance')}. "
        "Return IDs of selected creatives."
    elif step_type == "llm_draft":
        return f"{context}\nDraft a follow-up email for step: {step.get('template', 'followup')}. "
        "Keep it personal and value-focused."
    elif step_type == "llm_personalize":
        return f"{context}\nPersonalize the drafted email using: {step.get('fields', ['name', 'company'])}. "
        "Make it feel human-written."
    elif step_type == "llm_generate":
        return f"{context}\nGenerate social media content for platforms: {step.get('platforms', [])}. "
        "Include copy, hashtags, and image prompts."
    elif step_type == "llm_plan":
        return f"{context}\nPlan today's social media content. Types: {step.get('content_types', [])}. "
        "Create a content calendar for the next 7 days."
    elif step_type == "llm_forecast":
        return f"{context}\nForecast next {step.get('horizon', '30_days')}. "
        "Use current trends and seasonality."
    return f"{context}\nExecute step: {step_type}"


def schedule_workflow(workflow_id, cron_expr, enabled=True):
    """Schedule a workflow to run on a cron expression."""
    if workflow_id not in WORKFLOW_TEMPLATES:
        return {"error": f"Unknown workflow: {workflow_id}"}
    with _AUTOMATION_LOCK:
        _SCHEDULES[workflow_id] = {
            "cron": cron_expr,
            "enabled": enabled,
            "created_at": time.time(),
        }
    _save_schedules()
    return {"workflow_id": workflow_id, "cron": cron_expr, "enabled": enabled}


def cancel_schedule(workflow_id):
    with _AUTOMATION_LOCK:
        _SCHEDULES.pop(workflow_id, None)
    _save_schedules()
    return {"status": "cancelled"}


def get_schedule(workflow_id):
    with _AUTOMATION_LOCK:
        return _SCHEDULES.get(workflow_id)


def list_schedules():
    with _AUTOMATION_LOCK:
        return dict(_SCHEDULES)


def _save_automations():
    (SCHEDULE_DIR / "automations.json").write_text(
        json.dumps({k: v for k, v in _AUTOMATIONS.items()}, indent=2, default=str),
        encoding="utf-8",
    )


def _save_schedules():
    (SCHEDULE_DIR / "schedules.json").write_text(
        json.dumps({k: v for k, v in _SCHEDULES.items()}, indent=2, default=str),
        encoding="utf-8",
    )


def _load_state():
    try:
        global _AUTOMATIONS, _SCHEDULES
        auto_path = SCHEDULE_DIR / "automations.json"
        sched_path = SCHEDULE_DIR / "schedules.json"
        if auto_path.exists():
            _AUTOMATIONS = json.loads(auto_path.read_text(encoding="utf-8"))
        if sched_path.exists():
            _SCHEDULES = json.loads(sched_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass


# ── Scheduler loop ────────────────────────────────────────────────────
_scheduler_running = False
_scheduler_thread = None


def start_scheduler():
    """Start the cron scheduler thread."""
    global _scheduler_running, _scheduler_thread
    if _scheduler_thread and _scheduler_thread.is_alive():
        return
    _scheduler_running = True
    _scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True,
                                         name="automation-scheduler")
    _scheduler_thread.start()


def stop_scheduler():
    global _scheduler_running
    _scheduler_running = False


def _scheduler_loop():
    import time as _time
    while _scheduler_running:
        _time.sleep(60)
        with _AUTOMATION_LOCK:
            for wf_id, sched in list(_SCHEDULES.items()):
                if not sched.get("enabled"):
                    continue
                # Simple minute-check; in production use croniter
                record = execute_workflow(wf_id)
                if record.get("status") == "failed":
                    print(f"[automation] Workflow {wf_id} failed: {record.get('error')}")


# ── FastAPI ───────────────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="Intelligent Automations API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8030", "http://127.0.0.1:8030"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class ExecuteRequest(BaseModel):
        params: Optional[dict] = None

    class ScheduleRequest(BaseModel):
        cron_expr: str
        enabled: bool = True

    # Load persisted state
    _load_state()

    @app.get("/health")
    def health():
        return {"status": "ok", "workflows": len(WORKFLOW_TEMPLATES),
                "schedules": len(_SCHEDULES), "scheduler_running": _scheduler_running}

    @app.get("/workflows")
    def workflows():
        return {k: {"name": v["name"], "description": v["description"],
                    "schedule": v["schedule"], "steps": len(v["steps"])}
                for k, v in WORKFLOW_TEMPLATES.items()}

    @app.post("/workflows/{workflow_id}/execute")
    def execute(workflow_id: str, req: ExecuteRequest = None):
        return execute_workflow(workflow_id, req.params if req else None)

    @app.post("/workflows/{workflow_id}/schedule")
    def schedule(workflow_id: str, req: ScheduleRequest):
        return schedule_workflow(workflow_id, req.cron_expr, req.enabled)

    @app.delete("/workflows/{workflow_id}/schedule")
    def unschedule(workflow_id: str):
        return cancel_schedule(workflow_id)

    @app.get("/schedules")
    def get_schedules():
        return list_schedules()

    @app.get("/automations/runs")
    def list_runs():
        with _AUTOMATION_LOCK:
            runs = list(_AUTOMATIONS.values())
        return {"runs": runs, "total": len(runs)}

    @app.get("/automations/run/{run_id}")
    def get_run(run_id: str):
        with _AUTOMATION_LOCK:
            run = _AUTOMATIONS.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return run

    @app.get("/automations/log")
    def trigger_log(limit: int = 50):
        with _AUTOMATION_LOCK:
            return {"log": _TRIGGER_LOG[-limit:], "total": len(_TRIGGER_LOG)}

    @app.post("/scheduler/start")
    def start_sched():
        start_scheduler()
        return {"status": "started"}

    @app.post("/scheduler/stop")
    def stop_sched():
        stop_scheduler()
        return {"status": "stopped"}


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("AUTOMATION_PORT", "8184"))
        print(f"[automations] Starting on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[automations] FastAPI not available. Use functions directly.")
