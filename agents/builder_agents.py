#!/usr/bin/env python3
"""Builder Agents — scaffold projects from templates.

Agents:
  fullstack_app   - Complete web app with auth, DB, API, frontend
  website         - Static/dynamic marketing or portfolio site
  crm             - Customer relationship management system
  customer_service_chatbot - Support/chatbot for customer queries
  appointment_chatbot  - Scheduling/booking chatbot

Each agent scaffolds a project directory from a spec using the
FreeAI router/proxy, producing a complete runnable project.
"""
import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path

def _secure_path(base: Path, user_path: str) -> Path | None:
    """Resolve user_path against base and verify it stays within base. Returns None if traversal detected."""
    try:
        safe_name = Path(user_path).name
        if not safe_name or ".." in safe_name:
            return None
        result = base / safe_name
        base_real = os.path.realpath(str(base))
        result_real = os.path.realpath(str(result))
        if result_real == base_real or result_real.startswith(base_real + os.sep):
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

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

import requests

ROOT = Path(__file__).parent.parent
WORKSPACES_DIR = ROOT / "workspaces" / "builders"
WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)

AGENT_API = os.environ.get("AGENT_API", "http://localhost:8120")
ROUTER_URL = os.environ.get("ROUTER_URL", "http://localhost:8010/route")
PROXY_URL = os.environ.get("PROXY_URL", "http://localhost:8100/proxy")

_BUILDER_LOCK = threading.Lock()
_BUILDER_RUNS = {}

# ── Builder type definitions ─────────────────────────────────────────
BUILDER_AGENTS = {
    "fullstack_app": {
        "model": "claude-sonnet-4-5",
        "description": "Complete web application with auth, database, API, and frontend",
        "profile": "creative",
    },
    "website": {
        "model": "claude-sonnet-4-5",
        "description": "Marketing site, portfolio, or landing page",
        "profile": "creative",
    },
    "crm": {
        "model": "claude-sonnet-4-5",
        "description": "Customer relationship management system with leads, contacts, deals",
        "profile": "balanced",
    },
    "customer_service_chatbot": {
        "model": "gemini-2.5-flash",
        "description": "AI chatbot for customer support and FAQs",
        "profile": "balanced",
    },
    "appointment_chatbot": {
        "model": "gemini-2.5-flash",
        "description": "Scheduling and booking chatbot with calendar integration",
        "profile": "balanced",
    },
}

# ── Project templates ────────────────────────────────────────────────
TEMPLATES = {
    "fullstack_app": {
        "stacks": {
            "python_fastapi": {
                "description": "FastAPI + PostgreSQL + React frontend",
                "files": [
                    "backend/app/main.py",
                    "backend/app/database.py",
                    "backend/app/models.py",
                    "backend/app/routers/auth.py",
                    "backend/app/routers/api.py",
                    "backend/app/crud.py",
                    "backend/app/config.py",
                    "backend/requirements.txt",
                    "backend/Dockerfile",
                    "frontend/package.json",
                    "frontend/src/App.jsx",
                    "frontend/src/components/Layout.jsx",
                    "frontend/src/components/Auth.jsx",
                    "frontend/src/api/client.js",
                    "frontend/Dockerfile",
                    "docker-compose.yml",
                    "README.md",
                ],
            },
            "node_express": {
                "description": "Express + MongoDB + Vue.js frontend",
                "files": [
                    "server/index.js",
                    "server/models/User.js",
                    "server/routes/auth.js",
                    "server/routes/api.js",
                    "server/middleware/auth.js",
                    "server/config.js",
                    "server/package.json",
                    "server/Dockerfile",
                    "client/package.json",
                    "client/vue.config.js",
                    "client/src/App.vue",
                    "client/src/router/index.js",
                    "client/src/store/index.js",
                    "client/src/components/Layout.vue",
                    "client/Dockerfile",
                    "docker-compose.yml",
                    "README.md",
                ],
            },
            "python_django": {
                "description": "Django + PostgreSQL + HTMX/Alpine frontend",
                "files": [
                    "project/settings.py",
                    "project/urls.py",
                    "app/models.py",
                    "app/views.py",
                    "app/urls.py",
                    "app/templates/base.html",
                    "app/templates/index.html",
                    "manage.py",
                    "requirements.txt",
                    "Dockerfile",
                    "docker-compose.yml",
                    "README.md",
                ],
            },
        },
    },
    "website": {
        "stacks": {
            "static_html": {
                "description": "Pure HTML/CSS/JS static site",
                "files": [
                    "index.html",
                    "css/styles.css",
                    "js/app.js",
                    "images/.gitkeep",
                    "about.html",
                    "contact.html",
                    "404.html",
                    "README.md",
                ],
            },
            "nextjs": {
                "description": "Next.js 14+ with Tailwind CSS",
                "files": [
                    "app/page.tsx",
                    "app/layout.tsx",
                    "app/globals.css",
                    "components/Header.tsx",
                    "components/Footer.tsx",
                    "components/Hero.tsx",
                    "components/Features.tsx",
                    "components/CTA.tsx",
                    "components/Testimonials.tsx",
                    "next.config.js",
                    "tailwind.config.js",
                    "package.json",
                    "tsconfig.json",
                    "README.md",
                ],
            },
            "astro": {
                "description": "Astro static site with islands architecture",
                "files": [
                    "src/pages/index.astro",
                    "src/layouts/Base.astro",
                    "src/components/Header.astro",
                    "src/components/Footer.astro",
                    "src/components/Hero.astro",
                    "public/favicon.svg",
                    "astro.config.mjs",
                    "package.json",
                    "README.md",
                ],
            },
        },
    },
    "crm": {
        "stacks": {
            "python_fastapi": {
                "description": "FastAPI + SQLite/PostgreSQL CRM",
                "files": [
                    "app/main.py",
                    "app/database.py",
                    "app/models.py",
                    "app/routers/contacts.py",
                    "app/routers/deals.py",
                    "app/routers/leads.py",
                    "app/routers/tasks.py",
                    "app/routers/reports.py",
                    "app/auth.py",
                    "app/config.py",
                    "requirements.txt",
                    "Dockerfile",
                    "docker-compose.yml",
                    "README.md",
                ],
            },
            "vue_django": {
                "description": "Django REST + Vue.js CRM",
                "files": [
                    "crm/settings.py",
                    "crm/urls.py",
                    "contacts/models.py",
                    "contacts/views.py",
                    "contacts/urls.py",
                    "contacts/serializers.py",
                    "contacts/migrations/0001_initial.py",
                    "frontend/src/App.vue",
                    "frontend/src/views/Dashboard.vue",
                    "frontend/src/views/Contacts.vue",
                    "frontend/src/views/Deals.vue",
                    "frontend/src/api/index.js",
                    "frontend/src/router/index.js",
                    "frontend/package.json",
                    "requirements.txt",
                    "Dockerfile",
                    "docker-compose.yml",
                    "README.md",
                ],
            },
        },
    },
    "customer_service_chatbot": {
        "stacks": {
            "streamlit": {
                "description": "Streamlit chatbot with RAG knowledge base",
                "files": [
                    "app.py",
                    "chatbot/engine.py",
                    "chatbot/knowledge_base.py",
                    "chatbot/memory.py",
                    "chatbot/prompts.py",
                    "config.py",
                    "requirements.txt",
                    "knowledge/*.md",
                    ".streamlit/config.toml",
                    "README.md",
                ],
            },
            "flask_websocket": {
                "description": "Flask + WebSocket real-time chatbot",
                "files": [
                    "app.py",
                    "routes/chat.py",
                    "routes/api.py",
                    "services/llm.py",
                    "services/memory.py",
                    "services/intent.py",
                    "templates/index.html",
                    "static/js/chat.js",
                    "requirements.txt",
                    "Dockerfile",
                    "README.md",
                ],
            },
        },
    },
    "appointment_chatbot": {
        "stacks": {
            "python_fastapi": {
                "description": "FastAPI + SQLite booking system",
                "files": [
                    "app/main.py",
                    "app/database.py",
                    "app/models.py",
                    "app/routers/appointments.py",
                    "app/routers/services.py",
                    "app/routers/availability.py",
                    "app/routers/notifications.py",
                    "app/services/calendar.py",
                    "app/services/notifications.py",
                    "app/auth.py",
                    "requirements.txt",
                    "migrations/",
                    "Dockerfile",
                    "docker-compose.yml",
                    "README.md",
                ],
            },
            "node_express": {
                "description": "Express + MongoDB booking system",
                "files": [
                    "server/index.js",
                    "server/models/Appointment.js",
                    "server/models/Service.js",
                    "server/models/User.js",
                    "server/routes/appointments.js",
                    "server/routes/services.js",
                    "server/routes/auth.js",
                    "server/services/calendar.js",
                    "server/services/email.js",
                    "server/config.js",
                    "client/src/App.jsx",
                    "client/src/components/Booking.jsx",
                    "client/src/components/Calendar.jsx",
                    "client/src/components/Services.jsx",
                    "client/package.json",
                    "server/package.json",
                    "docker-compose.yml",
                    "README.md",
                ],
            },
        },
    },
}

# ── Business type templates ──────────────────────────────────────────
BUSINESS_TYPES = {
    "salon": {
        "description": "Hair salon / beauty salon",
        "builders": ["website", "appointment_chatbot"],
        "features": {
            "website": ["services menu", "pricing", "gallery", "booking CTA", "reviews"],
            "appointment_chatbot": ["service selection", "stylist preference", "time slots", "SMS reminders", "cancellation"],
        },
        "default_stack": {"website": "static_html", "appointment_chatbot": "python_fastapi"},
    },
    "clinic": {
        "description": "Medical clinic / dental practice",
        "builders": ["website", "appointment_chatbot", "crm"],
        "features": {
            "website": ["services", "doctors", "insurance info", "patient portal link", "emergency info"],
            "appointment_chatbot": ["specialty selection", "doctor preference", "insurance verification", "pre-visit forms", "reminder SMS"],
            "crm": ["patient records", "appointment history", "treatment plans", "follow-up scheduling", "HIPAA notes"],
        },
        "default_stack": {
            "website": "nextjs",
            "appointment_chatbot": "python_fastapi",
            "crm": "python_fastapi",
        },
    },
    "auto_shop": {
        "description": "Automotive repair shop",
        "builders": ["website", "appointment_chatbot", "crm"],
        "features": {
            "website": ["services (oil change, brakes, etc.)", "pricing estimates", "vehicle lookup", "hours/location"],
            "appointment_chatbot": ["service type", "vehicle make/model", "preferred time", "reminder", "service history"],
            "crm": ["customer vehicles", "service history", "maintenance reminders", "parts inventory", "estimates"],
        },
        "default_stack": {
            "website": "nextjs",
            "appointment_chatbot": "python_fastapi",
            "crm": "python_fastapi",
        },
    },
    "restaurant": {
        "description": "Restaurant / cafe",
        "builders": ["website", "appointment_chatbot"],
        "features": {
            "website": ["menu", "hours", "location", "online ordering", "events"],
            "appointment_chatbot": ["table reservation", "party size", "date/time", "special requests", "waitlist"],
        },
        "default_stack": {"website": "astro", "appointment_chatbot": "python_fastapi"},
    },
    "consulting": {
        "description": "Professional consulting / coaching",
        "builders": ["website", "crm", "customer_service_chatbot"],
        "features": {
            "website": ["about/services", "case studies", "blog", "testimonials", "contact"],
            "crm": ["client management", "project tracking", "proposal generation", "invoice tracking"],
            "customer_service_chatbot": ["FAQ", "service inquiry", "booking consultation", "resource library"],
        },
        "default_stack": {"website": "nextjs", "crm": "python_fastapi", "customer_service_chatbot": "streamlit"},
    },
    "ecommerce": {
        "description": "E-commerce store",
        "builders": ["fullstack_app", "customer_service_chatbot"],
        "features": {
            "fullstack_app": ["product catalog", "cart", "checkout", "user accounts", "order tracking", "reviews"],
            "customer_service_chatbot": ["order status", "returns", "product recommendations", "FAQ"],
        },
        "default_stack": {"fullstack_app": "python_fastapi", "customer_service_chatbot": "streamlit"},
    },
    "fitness": {
        "description": "Gym / fitness studio",
        "builders": ["website", "appointment_chatbot", "crm"],
        "features": {
            "website": ["classes schedule", "membership plans", "trainers", "transformations"],
            "appointment_chatbot": ["class booking", "personal training", "trial session", "cancellation"],
            "crm": ["membership management", "attendance tracking", "progress notes", "renewal reminders"],
        },
        "default_stack": {"website": "nextjs", "appointment_chatbot": "python_fastapi", "crm": "python_fastapi"},
    },
}


# ── LLM call helper ──────────────────────────────────────────────────
def _call_llm(prompt, model=None, max_tokens=8192, temperature=0.3):
    import requests
    url = PROXY_URL if "/proxy" in PROXY_URL else f"{PROXY_URL.rsplit('/', 1)[0]}/proxy"
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if model:
        payload["model"] = model
    try:
        r = requests.post(url, json=payload, timeout=660)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        try:
            r2 = requests.post(ROUTER_URL, json={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }, timeout=660)
            r2.raise_for_status()
            return r2.json()
        except Exception:
            raise HTTPException(status_code=502, detail=f"LLM unavailable: {exc}")


def _extract_text(result):
    resp = result.get("response", {})
    if isinstance(resp, dict):
        return resp.get("content", "") or str(resp.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return str(resp)


# ── Core scaffold builder ─────────────────────────────────────────────
def _parse_file_blocks(text):
    """Extract ```path\ncontent``` blocks from LLM output."""
    blocks = []
    pattern = r"```(?:\w+)?\n?(.*?)```"
    for match in re.finditer(pattern, text, re.DOTALL):
        content = match.group(1).strip()
        if not content:
            continue
        lines = content.split("\n")
        # First line might be the path
        first_line = lines[0].strip()
        if not re.match(r'^[\w/\.\-\_]+(\.\w+)?$', first_line) and not first_line.startswith("/"):
            # Not a path, treat whole content as one file
            blocks.append((".", content))
            continue
        if "/" in first_line or "." in first_line:
            path = first_line
            body = "\n".join(lines[1:]).strip()
        else:
            path = first_line
            body = "\n".join(lines[1:]).strip()
        if body:
            blocks.append((path, body))
    return blocks


def scaffold_builder(build_type, spec, business_type=None, stack=None,
                     workspace_dir=None, run_id=None):
    """Scaffold a project using the specified builder agent."""
    run_id = run_id or f"builder_{int(time.time())}_{os.getpid()}"
    run_id = _sanitize_run_id(run_id)
    ws_dir = Path(workspace_dir) if workspace_dir else WORKSPACES_DIR / run_id
    _ws_real = os.path.realpath(str(WORKSPACES_DIR))
    _ws_dir_real = os.path.realpath(str(ws_dir))
    if not (_ws_dir_real == _ws_real or _ws_dir_real.startswith(_ws_real + os.sep)):
        return {"error": "Invalid workspace path", "run_id": run_id, "status": "error"}
    ws_dir.mkdir(parents=True, exist_ok=True)

    builder_info = BUILDER_AGENTS.get(build_type)
    if not builder_info:
        return {"error": f"Unknown builder type: {build_type}",
                "run_id": run_id, "status": "error"}

    # Resolve business type
    biz_info = None
    if business_type and business_type in BUSINESS_TYPES:
        biz_info = BUSINESS_TYPES[business_type]

    # Resolve stack
    resolved_stack = stack
    if not resolved_stack and biz_info:
        resolved_stack = biz_info.get("default_stack", {}).get(build_type)
    if not resolved_stack:
        builders_templates = TEMPLATES.get(build_type, {})
        stacks = builders_templates.get("stacks", {})
        resolved_stack = next(iter(stacks)) if stacks else None

    # Build scaffold prompt
    prompt = _build_scaffold_prompt(build_type, spec, biz_info, resolved_stack)

    # Call LLM
    result = _call_llm(prompt, model=builder_info["model"],
                       max_tokens=16384, temperature=0.2)
    text = _extract_text(result)

    # Write files
    blocks = _parse_file_blocks(text)
    written = 0
    for path, content in blocks:
        if not content.strip():
            continue
        try:
            full = _secure_path(ws_dir, path)
            if full is None:
                continue
            _full_real = os.path.realpath(str(full))
            if not (_full_real == _ws_real or _full_real.startswith(_ws_real + os.sep)):
                continue
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            written += 1
        except (OSError, ValueError):
            pass

    # Write metadata
    metadata = {
        "run_id": run_id,
        "build_type": build_type,
        "spec": spec,
        "business_type": business_type,
        "stack": resolved_stack,
        "files_written": written,
        "workspace": str(ws_dir),
        "status": "done",
        "created_at": time.time(),
    }
    (ws_dir / "_meta.json").write_text(json.dumps(metadata, indent=2),
                                        encoding="utf-8")

    with _BUILDER_LOCK:
        _BUILDER_RUNS[run_id] = metadata

    return metadata


def _build_scaffold_prompt(build_type, spec, biz_info, stack):
    type_labels = {
        "fullstack_app": "Full-Stack Web Application",
        "website": "Website / Landing Page",
        "crm": "Customer Relationship Management System",
        "customer_service_chatbot": "Customer Service Chatbot",
        "appointment_chatbot": "Appointment / Booking Chatbot",
    }
    label = type_labels.get(build_type, build_type)
    biz_desc = f"\n\nBusiness context: {biz_info['description']}" if biz_info else ""
    biz_features = ""
    if biz_info and build_type in biz_info.get("features", {}):
        features = biz_info["features"][build_type]
        biz_features = f"\n\nRequired features:\n" + "\n".join(f"- {f}" for f in features)

    stack_desc = ""
    if stack:
        builders_templates = TEMPLATES.get(build_type, {})
        stacks = builders_templates.get("stacks", {})
        if stack in stacks:
            stack_desc = f"\n\nTarget stack: {stacks[stack]['description']}\n"
            stack_desc += "Expected files:\n" + "\n".join(f"  - {f}" for f in stacks[stack]["files"][:12])

    prompt = f"""You are a senior fullstack engineer. Build a complete, production-ready project.

PROJECT TYPE: {label}
SPEC: {spec}{biz_desc}{biz_features}{stack_desc}

 Deliver the COMPLETE project as file blocks. For each file:
 ```path/to/file.ext
 <full file content>
 ```

CRITICAL RULES:
1. Write REAL, WORKING code — no placeholders, no TODOs
2. Include error handling, input validation, and security basics
3. Use sensible defaults (port 8000 for backend, 3000 for frontend)
4. Include a README with setup instructions
5. Make it deployable (Dockerfile + docker-compose)
6. The project should run immediately after `pip install -r requirements.txt && python main.py`

Start with the most important files first. Be thorough — this will be used in production."""
    return prompt


def scaffold_business(business_type, spec="", run_id=None):
    """Scaffold all builders for a business type."""
    biz_info = BUSINESS_TYPES.get(business_type)
    if not biz_info:
        return {"error": f"Unknown business type: {business_type}",
                "run_id": run_id or "unknown"}

    results = {}
    safe_biz = re.sub(r'[^a-zA-Z0-9_\-]', '_', business_type) if business_type else "default"
    base_ws = WORKSPACES_DIR / safe_biz
    base_ws.mkdir(parents=True, exist_ok=True)

    for build_type in biz_info["builders"]:
        stack = biz_info["default_stack"].get(build_type)
        rid = f"{business_type}_{build_type}"
        results[build_type] = scaffold_builder(
            build_type, spec or f"{biz_info['description']} project",
            business_type=business_type, stack=stack,
            workspace_dir=str(base_ws / build_type),
            run_id=rid,
        )

    return {"business_type": business_type, "results": results}


# ── FastAPI endpoints ────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="Builder Agents API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8030", "http://127.0.0.1:8030"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class ScaffoldRequest(BaseModel):
        build_type: str
        spec: str
        business_type: Optional[str] = None
        stack: Optional[str] = None
        workspace_dir: Optional[str] = None
        run_id: Optional[str] = None

    class BusinessRequest(BaseModel):
        business_type: str
        spec: str = ""

    @app.get("/health")
    def health():
        return {"status": "ok", "builders": list(BUILDER_AGENTS.keys()),
                "businesses": list(BUSINESS_TYPES.keys())}

    @app.get("/builders")
    def list_builders():
        return {name: {"description": info["description"],
                       "model": info["model"]}
                for name, info in BUILDER_AGENTS.items()}

    @app.get("/business-types")
    def list_business_types():
        return {name: {"description": info["description"],
                       "builders": info["builders"]}
                for name, info in BUSINESS_TYPES.items()}

    @app.post("/builder/scaffold")
    def scaffold(req: ScaffoldRequest):
        result = scaffold_builder(req.build_type, req.spec,
                                  business_type=req.business_type,
                                  stack=req.stack,
                                  workspace_dir=req.workspace_dir,
                                  run_id=req.run_id)
        return result

    @app.post("/builder/business/{business_type}")
    def scaffold_business_endpoint(business_type: str, req: BusinessRequest = None):
        spec = req.spec if req else ""
        return scaffold_business(business_type, spec)

    @app.get("/builder/runs")
    def list_runs():
        with _BUILDER_LOCK:
            runs = list(_BUILDER_RUNS.values())
        return {"runs": runs, "total": len(runs)}

    @app.get("/builder/run/{run_id}")
    def get_run(run_id: str):
        with _BUILDER_LOCK:
            run = _BUILDER_RUNS.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        return run


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("BUILDER_PORT", "8180"))
        print(f"[builder-agents] Starting on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[builder-agents] FastAPI not available. Use scaffold_builder() directly.")
