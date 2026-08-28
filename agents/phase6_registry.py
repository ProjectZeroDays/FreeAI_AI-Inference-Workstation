#!/usr/bin/env python3
"""Phase 6 Module Registry — wires all builder/pipeline/campaign/automation modules.

Registers endpoints, workflows, and agents into the FreeAI unified system.
Run this to activate all Phase 6 capabilities.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── Module discovery ──────────────────────────────────────────────────
MODULES = {
    "builder_agents": {
        "module": "agents.builder_agents",
        "port": int(os.environ.get("BUILDER_PORT", "8180")),
        "description": "5 builder agents: fullstack_app, website, crm, customer_service_chatbot, appointment_chatbot",
        "business_types": list(__import__("workflow.workflows.business_templates", fromlist=["BUSINESS_WORKFLOWS"]).BUSINESS_WORKFLOWS.keys())
                        if "workflow.workflows.business_templates" in sys.modules or True else [],
    },
    "pipeline_agents": {
        "module": "agents.pipeline_agents",
        "port": int(os.environ.get("PIPELINE_PORT", "8181")),
        "description": "3 pipeline agents: ad_generator, lead_collector, marketing_pipeline",
    },
    "campaign_manager": {
        "module": "agents.campaign_manager",
        "port": int(os.environ.get("CAMPAIGN_PORT", "8182")),
        "description": "Campaign lifecycle manager with ad/lead pipeline integration",
    },
    "custom_code_builder": {
        "module": "agents.custom_code_builder",
        "port": int(os.environ.get("CODEBUILDER_PORT", "8183")),
        "description": "Custom code builder replacing FreeCode — multi-language, framework-aware",
    },
    "automations": {
        "module": "agents.automations",
        "port": int(os.environ.get("AUTOMATION_PORT", "8184")),
        "description": "Intelligent automations and cron workflows (10 pre-configured)",
    },
}


def register_all():
    """Register all Phase 6 modules with the FreeAI router."""
    registered = []
    for name, info in MODULES.items():
        mod = __import__(info["module"], fromlist=["app"])
        if hasattr(mod, "app"):
            registered.append({
                "name": name,
                "port": info["port"],
                "status": "registered",
                "description": info["description"],
            })
    return registered


def print_status():
    """Print status of all Phase 6 modules."""
    print("\n=== FreeAI Phase 6 — Agent Modules Status ===\n")
    print(f"{'Module':<25} {'Port':<8} {'Description'}")
    print("-" * 70)
    for name, info in MODULES.items():
        mod = __import__(info["module"], fromlist=["app"])
        status = "ok" if hasattr(mod, "app") else "missing"
        print(f"  {name:<23} :{info['port']:<6} [{status}] {info['description']}")
    print("\n--- Builder Agents (5) ---")
    try:
        from agents.builder_agents import BUILDER_AGENTS, BUSINESS_TYPES
        for name, info in BUILDER_AGENTS.items():
            print(f"  {name}: {info['description']} (model: {info['model']})")
        print(f"\nBusiness templates ({len(BUSINESS_TYPES)}):")
        for bt, info in BUSINESS_TYPES.items():
            print(f"  {bt}: {info['description']} → builders: {', '.join(info['builders'])}")
    except Exception as e:
        print(f"  Error loading builder agents: {e}")

    print("\n--- Pipeline Agents (3) ---")
    try:
        from agents.pipeline_agents import PIPELINE_AGENTS, AD_FORMATS, LEAD_SOURCES
        for name, info in PIPELINE_AGENTS.items():
            print(f"  {name}: {info['description']} (model: {info['model']})")
        print(f"\nAd formats ({len(AD_FORMATS)}): {', '.join(AD_FORMATS.keys())}")
        print(f"Lead sources ({len(LEAD_SOURCES)}): {', '.join(LEAD_SOURCES.keys())}")
    except Exception as e:
        print(f"  Error loading pipeline agents: {e}")

    print("\n--- Campaign Manager ---")
    try:
        from agents.campaign_manager import CAMPAIGN_TYPES, LIFECYCLE_STATES
        print(f"  Campaign types ({len(CAMPAIGN_TYPES)}): {', '.join(CAMPAIGN_TYPES.keys())}")
        print(f"  Lifecycle states: {' → '.join(LIFECYCLE_STATES)}")
    except Exception as e:
        print(f"  Error loading campaign manager: {e}")

    print("\n--- Custom Code Builder ---")
    try:
        from agents.custom_code_builder import LANGUAGES
        print(f"  Supported languages ({len(LANGUAGES)}): {', '.join(LANGUAGES.keys())}")
    except Exception as e:
        print(f"  Error loading code builder: {e}")

    print("\n--- Automations & Cron (10 workflows) ---")
    try:
        from agents.automations import WORKFLOW_TEMPLATES
        for wf_id, wf in WORKFLOW_TEMPLATES.items():
            print(f"  {wf_id}: {wf['name']} ({wf['schedule']})")
    except Exception as e:
        print(f"  Error loading automations: {e}")

    print("\n--- Business Workflow Templates (7) ---")
    try:
        from workflow.workflows.business_templates import BUSINESS_WORKFLOWS
        for bt, info in BUSINESS_WORKFLOWS.items():
            print(f"  {bt}: {info['name']} — builders: {', '.join(info['builders'])}")
    except Exception as e:
        print(f"  Error loading business templates: {e}")

    print("\n=== End Phase 6 Status ===\n")


if __name__ == "__main__":
    print_status()
