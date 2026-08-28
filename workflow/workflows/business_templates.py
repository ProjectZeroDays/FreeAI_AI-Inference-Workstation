#!/usr/bin/env python3
"""Business workflow templates — pre-configured pipelines for common business types.

Business types:
  salon, clinic, auto_shop, restaurant, consulting, ecommerce, fitness

Each template defines a complete workflow combining builder agents,
pipeline agents, campaign management, and automations.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ── Business workflow templates ───────────────────────────────────────
BUSINESS_WORKFLOWS = {
    "salon": {
        "name": "Hair Salon",
        "description": "Complete business system for a hair/beauty salon",
        "builders": {
            "website": {"spec": "Modern salon website with service menu, pricing gallery, team bios, online booking CTA, and customer reviews",
                        "stack": "static_html"},
            "appointment_chatbot": {"spec": "Salon booking chatbot: service selection (haircut, color, treatment), stylist matching, time slot picker, SMS reminders, cancellation policy",
                                    "stack": "python_fastapi"},
        },
        "pipelines": {
            "ad_campaign": {
                "product": "Salon services",
                "target_audience": "Women 25-55, local area, interested in beauty",
                "platforms": ["facebook_feed", "google_search", "instagram"],
                "brand_voice": "warm, professional, welcoming",
            },
            "lead_collection": {
                "source": "web_scrape",
                "params": {"query": "salon clients looking for new stylist near me",
                           "location": "local_5mi"},
            },
        },
        "campaigns": [
            {"name": "Summer Glow Campaign", "type": "seasonal", "budget": 2000,
             "channels": ["facebook", "email", "google"]},
            {"name": "New Client Special", "type": "lead_gen", "budget": 1000,
             "channels": ["google", "facebook"]},
        ],
        "automations": [
            {"workflow": "daily_lead_enrichment", "enabled": True},
            {"workflow": "customer_followup_sequence", "enabled": True,
             "params": {"template": "post_visit_thankyou"}},
            {"workflow": "social_media_scheduler", "enabled": True,
             "params": {"platforms": ["instagram", "facebook"]}},
        ],
    },
    "clinic": {
        "name": "Medical Clinic",
        "description": "HIPAA-aware clinic management system",
        "builders": {
            "website": {"spec": "Medical clinic website: services, doctor profiles, insurance accepted, patient portal, appointment request, health blog",
                        "stack": "nextjs"},
            "appointment_chatbot": {"spec": "Clinic scheduling: specialty selection, doctor preference, insurance check, pre-visit questionnaire, reminder SMS, cancellation",
                                    "stack": "python_fastapi"},
            "crm": {"spec": "Patient CRM: contact management, appointment history, treatment plans, follow-up scheduling, HIPAA-compliant notes",
                    "stack": "python_fastapi"},
        },
        "pipelines": {
            "ad_campaign": {
                "product": "Clinic services",
                "target_audience": "Local residents 30-65, needing primary care or specialty",
                "platforms": ["google_search", "facebook_feed", "linkedin_sponsor"],
                "brand_voice": "trustworthy, compassionate, professional",
            },
            "lead_collection": {
                "source": "web_scrape",
                "params": {"query": "best clinic near me", "filters": ["high_rating", "accepting_new_patients"]},
            },
        },
        "campaigns": [
            {"name": "Open Enrollment Health Check", "type": "seasonal", "budget": 5000,
             "channels": ["google", "email", "mail"]},
            {"name": "New Patient Welcome", "type": "retention", "budget": 1500,
             "channels": ["email", "sms"]},
        ],
        "automations": [
            {"workflow": "daily_lead_enrichment", "enabled": True},
            {"workflow": "customer_followup_sequence", "enabled": True,
             "params": {"template": "post_visit_followup"}},
            {"workflow": "weekly_campaign_report", "enabled": True},
            {"workflow": "data_backup_sync", "enabled": True},
        ],
    },
    "auto_shop": {
        "name": "Auto Repair Shop",
        "description": "Complete auto shop business system",
        "builders": {
            "website": {"spec": "Auto shop website: services (oil change, brakes, tires, engine), pricing estimates, vehicle make/model lookup, hours, location map, reviews",
                        "stack": "nextjs"},
            "appointment_chatbot": {"spec": "Auto shop booking: service type, vehicle info (make/model/year), preferred time, reminder, service history lookup",
                                    "stack": "python_fastapi"},
            "crm": {"spec": "Auto shop CRM: customer vehicles, service history, maintenance reminders, parts inventory, estimates, invoices",
                    "stack": "python_fastapi"},
        },
        "pipelines": {
            "ad_campaign": {
                "product": "Auto repair services",
                "target_audience": "Car owners 25-65, local area, vehicle maintenance needs",
                "platforms": ["google_search", "facebook_feed", "youtube_prejoin"],
                "brand_voice": "reliable, transparent, friendly",
            },
            "lead_collection": {
                "source": "web_scrape",
                "params": {"query": "auto repair near me", "filters": ["new_customer"]},
            },
        },
        "campaigns": [
            {"name": "Oil Change Special", "type": "seasonal", "budget": 1500,
             "channels": ["google", "facebook", "email"]},
            {"name": "Winter Safety Check", "type": "seasonal", "budget": 2000,
             "channels": ["google", "email", "direct_mail"]},
        ],
        "automations": [
            {"workflow": "daily_lead_enrichment", "enabled": True},
            {"workflow": "customer_followup_sequence", "enabled": True,
             "params": {"template": "service_reminder"}},
            {"workflow": "ad_rotation_scheduler", "enabled": True},
        ],
    },
    "restaurant": {
        "name": "Restaurant",
        "description": "Restaurant website + reservation system",
        "builders": {
            "website": {"spec": "Restaurant website: menu with photos, hours, location, online ordering, reservations, events, reviews, catering info",
                        "stack": "astro"},
            "appointment_chatbot": {"spec": "Restaurant reservation bot: party size, date/time, seating preference, special requests, waitlist, confirmation",
                                    "stack": "python_fastapi"},
        },
        "pipelines": {
            "ad_campaign": {
                "product": "Restaurant dining",
                "target_audience": "Foodies 25-50, local area, dining out enthusiasts",
                "platforms": ["facebook_feed", "google_search", "instagram"],
                "brand_voice": "appetizing, warm, inviting",
            },
            "lead_collection": {
                "source": "web_scrape",
                "params": {"query": "best restaurants near me", "filters": ["new_openings"]},
            },
        },
        "campaigns": [
            {"name": "Weekend Brunch Launch", "type": "product_launch", "budget": 1000,
             "channels": ["instagram", "facebook", "email"]},
            {"name": "Lunch Special Series", "type": "seasonal", "budget": 800,
             "channels": ["google", "email"]},
        ],
        "automations": [
            {"workflow": "social_media_scheduler", "enabled": True,
             "params": {"platforms": ["instagram", "twitter"]}},
            {"workflow": "customer_followup_sequence", "enabled": True,
             "params": {"template": "post_visit_review"}},
        ],
    },
    "consulting": {
        "name": "Consulting Firm",
        "description": "Professional consulting business system",
        "builders": {
            "website": {"spec": "Consulting firm site: about/services, case studies, team bios, blog, testimonials, contact/booking",
                        "stack": "nextjs"},
            "crm": {"spec": "Consulting CRM: client management, project tracking, proposal generation, invoice tracking, time tracking",
                    "stack": "python_fastapi"},
            "customer_service_chatbot": {"spec": "Consulting chatbot: FAQ about services, book consultation, resource library, quote request",
                                         "stack": "streamlit"},
        },
        "pipelines": {
            "ad_campaign": {
                "product": "Consulting services",
                "target_audience": "Business decision makers, C-suite, startup founders",
                "platforms": ["linkedin_sponsor", "google_search", "email_campaign"],
                "brand_voice": "authoritative, insightful, results-driven",
            },
            "lead_collection": {
                "source": "linkedin",
                "params": {"title_keywords": ["CEO", "Director", "VP"],
                           "industry": "target_industry", "seniority": "decision_maker"},
            },
        },
        "campaigns": [
            {"name": "Q1 Business Growth Package", "type": "product_launch", "budget": 3000,
             "channels": ["linkedin", "email", "webinar"]},
            {"name": "Client Retention Program", "type": "retention", "budget": 1000,
             "channels": ["email", "phone"]},
        ],
        "automations": [
            {"workflow": "daily_lead_enrichment", "enabled": True},
            {"workflow": "weekly_campaign_report", "enabled": True},
            {"workflow": "customer_followup_sequence", "enabled": True,
             "params": {"template": "nurturing_sequence"}},
            {"workflow": "competitor_monitor", "enabled": True},
        ],
    },
    "ecommerce": {
        "name": "E-Commerce Store",
        "description": "Full e-commerce platform with support chatbot",
        "builders": {
            "fullstack_app": {"spec": "E-commerce platform: product catalog, cart, checkout (Stripe), user accounts, order tracking, reviews, Wishlist, admin dashboard",
                              "stack": "python_fastapi"},
            "customer_service_chatbot": {"spec": "E-commerce support bot: order status lookup, return/exchange help, product recommendations, FAQ, shipping info",
                                         "stack": "streamlit"},
        },
        "pipelines": {
            "ad_campaign": {
                "product": "E-commerce products",
                "target_audience": "Online shoppers, interest-based segments",
                "platforms": ["google_search", "facebook_feed", "youtube_prejoin", "email_campaign"],
                "brand_voice": "exciting, trustworthy, urgent",
            },
            "lead_collection": {
                "source": "web_scrape",
                "params": {"query": "best deals on product_category",
                           "filters": ["high_intent"]},
            },
        },
        "campaigns": [
            {"name": "Black Friday Sale", "type": "seasonal", "budget": 10000,
             "channels": ["google", "facebook", "email", "sms"]},
            {"name": "New Collection Launch", "type": "product_launch", "budget": 3000,
             "channels": ["instagram", "email", "influencer"]},
        ],
        "automations": [
            {"workflow": "daily_lead_enrichment", "enabled": True},
            {"workflow": "ad_rotation_scheduler", "enabled": True},
            {"workflow": "customer_followup_sequence", "enabled": True,
             "params": {"template": "abandoned_cart"}},
            {"workflow": "social_media_scheduler", "enabled": True},
            {"workflow": "real_time_alert_monitor", "enabled": True},
        ],
    },
    "fitness": {
        "name": "Fitness Studio",
        "description": "Gym/fitness studio with class booking and membership",
        "builders": {
            "website": {"spec": "Fitness studio site: class schedule, membership plans, trainer profiles, transformations, class booking, contact",
                        "stack": "nextjs"},
            "appointment_chatbot": {"spec": "Fitness booking: class selection, trainer preference, time slot, trial class, cancellation, waitlist",
                                    "stack": "python_fastapi"},
            "crm": {"spec": "Fitness CRM: membership management, attendance tracking, progress notes, renewal reminders, class capacity",
                    "stack": "python_fastapi"},
        },
        "pipelines": {
            "ad_campaign": {
                "product": "Fitness membership and classes",
                "target_audience": "Health-conscious 20-45, local area",
                "platforms": ["facebook_feed", "instagram", "google_search", "youtube_prejoin"],
                "brand_voice": "energetic, motivating, supportive",
            },
            "lead_collection": {
                "source": "web_scrape",
                "params": {"query": "best gym near me", "filters": ["new_members"]},
            },
        },
        "campaigns": [
            {"name": "New Year Resolution Push", "type": "seasonal", "budget": 5000,
             "channels": ["facebook", "instagram", "google"]},
            {"name": "Summer Shred Challenge", "type": "seasonal", "budget": 3000,
             "channels": ["instagram", "email", "sms"]},
        ],
        "automations": [
            {"workflow": "daily_lead_enrichment", "enabled": True},
            {"workflow": "customer_followup_sequence", "enabled": True,
             "params": {"template": "trial_to_member"}},
            {"workflow": "social_media_scheduler", "enabled": True,
             "params": {"platforms": ["instagram", "facebook"]}},
        ],
    },
}


def get_workflow(business_type):
    """Get a business workflow template."""
    return BUSINESS_WORKFLOWS.get(business_type)


def list_workflows():
    """List all business workflow templates."""
    return {k: {"name": v["name"], "description": v["description"],
                "builders": list(v["builders"].keys()),
                "campaigns": len(v["campaigns"]),
                "automations": len(v["automations"])}
            for k, v in BUSINESS_WORKFLOWS.items()}


def generate_business_workflow(business_type, custom_specs=None):
    """Generate a complete business workflow from template."""
    template = BUSINESS_WORKFLOWS.get(business_type)
    if not template:
        return {"error": f"Unknown business type: {business_type}"}

    result = {"business_type": business_type, "template": template["name"], "status": "generated"}

    # Apply custom specs if provided
    if custom_specs:
        for section, specs in custom_specs.items():
            if section in result and isinstance(result[section], dict):
                result[section].update(specs)

    # Save to workspace
    ws_dir = ROOT / "workspaces" / "business_workflows" / business_type
    ws_dir.mkdir(parents=True, exist_ok=True)
    (ws_dir / "workflow.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (ws_dir / "README.md").write_text(
        f"# {template['name']} Workflow\n\n"
        f"{template['description']}\n\n"
        f"## Builders\n" + "\n".join(f"- {k}: {v['spec']}" for k, v in template["builders"].items()) + "\n\n"
        f"## Campaigns\n" + "\n".join(f"- {c['name']} ({c['type']}): ${c['budget']}" for c in template["campaigns"]) + "\n\n"
        f"## Automations\n" + "\n".join(f"- {a['workflow']}" for a in template["automations"]) + "\n",
        encoding="utf-8",
    )

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: business_templates.py [list|generate <business_type>]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "list":
        for name, wf in list_workflows().items():
            print(f"  {name}: {wf['name']} — builders: {', '.join(wf['builders'])}")
    elif cmd == "generate" and len(sys.argv) > 2:
        result = generate_business_workflow(sys.argv[2])
        print(json.dumps(result, indent=2)[:2000])
    else:
        print("Unknown command. Use: list or generate <business_type>")
