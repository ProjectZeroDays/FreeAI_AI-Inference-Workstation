# Red Team Test Campaign Framework

> **Classification:** INTERNAL USE ONLY  
> **Authorization:** Red team testing against owned infrastructure  
> **Version:** 1.0.0

---

## 1. Campaign Architecture Overview

### Test Matrix Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMPAIGN OVERVIEW                           │
├─────────────┬─────────────┬─────────────┬───────────────────────┤
│   Variant A │   Variant B │   Variant C │   Control (Baseline)  │
│   (60%)     │   (25%)     │   (15%)     │   (100% reference)    │
├─────────────┴─────────────┴─────────────┴───────────────────────┤
│                    AUDIENCE SEGMENTS                            │
├──────────────┬───────────────┬───────────────┬──────────────────┤
│ Segment 1    │ Segment 2     │ Segment 3     │ Segment 4        │
│ (Tech)       │ (Exec)        │ (Ops)         │ (Mixed)          │
│ 30% budget   │ 25% budget    │ 25% budget    │ 20% budget       │
└──────────────┴───────────────┴───────────────┴──────────────────┘
```

### Campaign ID Convention

```
CAMP-YYYYMMDD-XXXX
Example: CAMP-20260831-001
```

---

## 2. A/B Test Framework

### 2.1 Standard A/B Test

**Purpose:** Compare two variants against each other and a baseline.

```json
{
  "campaign_id": "CAMP-20260831-001",
  "type": "ab_test",
  "title": "Phishing Template Effectiveness",
  "variants": [
    {
      "id": "variant_a",
      "name": "Urgency-Based",
      "weight": 50,
      "payload": {
        "subject": "URGENT: Password Expiration Notice",
        "body_template": "your_password_expires_in_24_hours",
        "cta_text": "Reset Now",
        "urgency_indicators": ["countdown_timer", "red_alert"]
      }
    },
    {
      "id": "variant_b",
      "name": "Authority-Based",
      "weight": 50,
      "payload": {
        "subject": "IT Department: Security Update Required",
        "body_template": "mandatory_security_update",
        "cta_text": "Apply Update",
        "authority_indicators": ["IT_logo", "official_reference_number"]
      }
    }
  ],
  "control": {
    "name": "Baseline_Neutral",
    "payload": {
      "subject": "System Notification",
      "body_template": "standard_notification"
    }
  },
  "audience": {
    "segment": "all_employees",
    "sample_size": 500,
    "min_confidence": 0.95
  },
  "metrics": ["open_rate", "click_rate", "credential_submission"],
  "duration_hours": 48,
  "budget": {
    "total": 1000,
    "currency": "test_credits",
    "per_variant": 500
  }
}
```

### 2.2 A/B/n Test (Multi-Variant)

**Purpose:** Test multiple variants simultaneously.

```json
{
  "campaign_id": "CAMP-20260831-002",
  "type": "abn_test",
  "title": "Email Header Analysis",
  "variants": [
    {
      "id": "v1",
      "name": "Spoofed_From",
      "weight": 25,
      "header_modifications": {
        "from": "admin@company.com",
        "reply_to": "helpdesk@company.com"
      }
    },
    {
      "id": "v2",
      "name": "Spoofed_ReplyTo",
      "weight": 25,
      "header_modifications": {
        "from": "it-support@gmail.com",
        "reply_to": "help@company.com"
      }
    },
    {
      "id": "v3",
      "name": "Subdomain_Spoof",
      "weight": 25,
      "header_modifications": {
        "from": "it-company.com (looks like company.com)"
      }
    },
    {
      "id": "v4",
      "name": "Control",
      "weight": 25,
      "header_modifications": {}
    }
  ],
  "metrics": ["open_rate", "hover_time", "report_rate"],
  "duration_hours": 24
}
```

---

## 3. Audience Segmentation

### 3.1 Role-Based Segments

| Segment | Criteria | Budget % | Campaign Type |
|---------|----------|----------|---------------|
| **C-Level Executives** | Title contains CEO, CTO, CFO, VP | 15% | Executive impersonation |
| **IT Personnel** | Department = IT, Title = Admin, SysAdmin | 20% | Technical pretexting |
| **Finance** | Department = Finance, Accounting | 15% | Invoice/fraud themed |
| **HR** | Department = Human Resources | 10% | Policy/document themed |
| **Engineering** | Title contains Eng, Dev, Architect | 20% | GitHub/Jira themed |
| **General Staff** | All others | 20% | Mixed templates |

### 3.2 Behavioral Segments

```json
{
  "segments": [
    {
      "id": "high_risk",
      "criteria": ["clicks_phishing_simulations", "fails_mfa_challenge"],
      "weight": 40,
      "description": "Users with prior phishing susceptibility"
    },
    {
      "id": "medium_risk",
      "criteria": ["opens_emails", "low_click_history"],
      "weight": 35,
      "description": "Regular email users, moderate caution"
    },
    {
      "id": "low_risk",
      "criteria": ["reports_suspicious_emails", "mfa_compliant"],
      "weight": 25,
      "description": "Security-aware users"
    }
  ]
}
```

### 3.3 Department-Specific Templates

```
Department    → Template Type          → Urgency    → Sender Spoof
─────────────────────────────────────────────────────────────────────
Finance       → Invoice/Fraud          → High       → Vendor/CFO
HR            → Policy/Compliance      → Medium     → HR Director
IT            → Technical Alert        → Medium     → SysAdmin
Executive     → Board/Legal            → High       → Legal/CFO
Engineering   → Code/Deployment        → Low        → Tech Lead
```

---

## 4. Budget Allocation Strategies

### 4.1 Equal Split (Baseline)

```
Campaign Budget: $10,000
├── Variant A: $3,333 (33.3%)
├── Variant B: $3,333 (33.3%)
├── Variant C: $3,334 (33.4%)
└── Control:   $0 (reference only)
```

### 4.2 Gradient Split (Prioritized)

```
Campaign Budget: $10,000
├── Variant A (Primary): $5,000 (50%)
├── Variant B (Secondary): $3,000 (30%)
├── Variant C (Tertiary): $1,500 (15%)
└── Reserve (Contingency): $500 (5%)
```

### 4.3 Dynamic Allocation (Adaptive)

```python
# Payouts adjusted based on real-time performance
class DynamicBudgetAllocator:
    def __init__(self, total_budget, variants):
        self.budget = total_budget
        self.variants = variants
        self.spent = {v.id: 0 for v in variants}
        self.performance = {v.id: 0 for v in variants}
    
    def allocate_next(self):
        """ Allocate to best-performing variant with exploration """
        for variant in self.variants:
            # Upper Confidence Bound (UCB) algorithm
            ucb = (self.performance[variant.id] / max(self.spent[variant.id], 1)) + \
                  math.sqrt(2 * math.log(sum(self.spent.values())) / max(self.spent[variant.id], 1))
            
            if self.spent[variant.id] < variant.max_allocation:
                return variant
        return None
```

### 4.4 Segment-Based Budget

```
Total Budget: $15,000

Segment Allocation:
├── Executive (High-value targets): $4,500 (30%)
│   └── Variant A: $2,250 | Variant B: $2,250
├── IT Staff (Security awareness): $3,750 (25%)
│   └── Variant A: $1,875 | Variant B: $1,875
├── Finance (High-risk department): $3,750 (25%)
│   └── Variant A: $1,875 | Variant B: $1,875
├── Engineering (Technical users): $2,250 (15%)
│   └── Variant A: $1,125 | Variant B: $1,125
└── General Staff: $750 (5%)
    └── Variant A: $375 | Variant B: $375
```

---

## 5. Campaign Templates

### 5.1 Phishing Simulation

```json
{
  "campaign_template": "phishing_simulation",
  "variants": {
    "subject_lines": [
      "Your package is waiting - {company_name}",
      "Action Required: Verify your account",
      "Meeting invitation: {random_topic}",
      "Invoice #{invoice_number} attached"
    ],
    "pretext_scenarios": [
      "IT security alert",
      "HR policy update",
      "Benefit enrollment",
      "Vendor payment",
      "Login verification"
    ],
    "landing_pages": [
      "microsoft_login.html",
      "google_workspace.html",
      "adobe_sign.html",
      "dropbox_share.html"
    ]
  },
  "success_metrics": {
    "primary": "credential_submission_rate",
    "secondary": ["open_rate", "click_rate", "time_to_submit"],
    "avoidance": ["mark_as_phishing", "report_to_it"]
  }
}
```

### 5.2 USB Drop Test

```json
{
  "campaign_template": "usb_drop",
  "variants": {
    "labels": [
      "Q4_Budget_2026.xlsx",
      "Confidential_Merger_Docs.pdf",
      "Employee_Salaries_2026.csv",
      "IT_Security_Policy.docx",
      "Layoff_List_Dec2026.txt"
    ],
    "placement_zones": [
      "parking_lot",
      "lobby",
      "cafeteria",
      "elevator",
      "printer_room"
    ],
    "payload_types": [
      "autorun.inf",
      "shortcut_with_icon",
      "emotet_stager",
      "payloadless_macro"
    ]
  },
  "success_metrics": {
    "primary": "insertion_rate",
    "secondary": ["boot_rate", "payload_execution"],
    "detection": ["reported_to_security"]
  }
}
```

### 5.3 Wi-Fi Rogue Access Point

```json
{
  "campaign_template": "rogue_ap",
  "variants": {
    "ssid_options": [
      "{company_name}_Guest",
      "{company_name}_Secure",
      "{company_name}_IT",
      "Free_Office_WiFi",
      "Corporate_VPN_Test"
    ],
    "encryption": ["open", "wep_fake", "wpa2_enterprise_fake"],
    "passthrough": ["login_page", "certificate_warning", "mfa_challenge"]
  },
  "success_metrics": {
    "primary": "device_connection_rate",
    "secondary": ["authentication_attempts", "data_exfiltration_volume"],
    "duration_seconds": 3600
  }
}
```

### 5.4 Social Engineering (Phone)

```json
{
  "campaign_template": "vishing",
  "variants": {
    "caller_identities": [
      "IT Helpdesk",
      "Security Team",
      "Vendor Support",
      "Executive Assistant",
      "HR Representative"
    ],
    "pretexts": [
      "password_reset",
      "account_lockout",
      "malware_infection",
      "verify_transaction",
      "update_directory"
    ],
    "urgency_levels": ["low", "medium", "high", "critical"]
  },
  "success_metrics": {
    "primary": "information_obtained_rate",
    "secondary": ["call_duration", "compliance_score"],
    " Ethical guardrails": ["no_threats", "no_personal_data", "immediate_debrief"]
  }
}
```

---

## 6. Test Execution Workflow

### 6.1 Pre-Campaign Checklist

```
□ Authorization verified (ROE documented)
□ Target scope confirmed (owned infrastructure only)
□ Legal/compliance review completed
□ Rollback plan documented
□ Notification sent to SOC (to avoid real incident)
□ Monitoring dashboard configured
□ Response team on standby
```

### 6.2 Execution Steps

```
1. CAMPAIGN INIT
   ├─ Generate campaign ID
   ├─ Distribute variants across audience segments
   ├─ Set budget allocation
   └─ Start timestamp

2. MONITOR (Real-time)
   ├─ Track engagement metrics
   ├─ Watch for escalation triggers
   ├─ Log all interactions
   └─ Alert on anomalies

3. EVALUATE (Post-campaign)
   ├─ Calculate success rates per variant
   ├─ Statistical significance testing
   ├─ Segment analysis
   └─ Lessons learned report

4. CLEANUP
   ├─ Remove test infrastructure
   ├─ Revoke test credentials
   ├─ Archive campaign data
   └─ Update defensive posture
```

### 6.3 Escalation Triggers

```python
ESCALATION_CONDITIONS = {
    "real_user_reported": True,        # Someone reported to real security
    "legal_impact": True,              # Potential legal/regulatory issue
    "data_leak": True,                 # Sensitive data accessed
    "system_disruption": True,         # Service impacted
    "duration_exceeded": 4,            # Hours beyond planned duration
    "budget_exceeded": True            # Cost overrun
}
```

---

## 7. Reporting Framework

### 7.1 Campaign Report Template

```markdown
# Campaign Report: {campaign_id}

## Executive Summary
- **Objective:** {description}
- **Duration:** {start} to {end}
- **Total Audience:** {N} users
- **Overall Success Rate:** {X}%

## Variant Performance

| Variant | Sent | Open | Click | Submit | Rate |
|---------|------|------|-------|--------|------|
| A       | 500  | 312  | 187   | 45     | 9.0% |
| B       | 500  | 298  | 156   | 32     | 6.4% |
| Control | 500  | 189  | 67    | 8      | 1.6% |

## Segment Analysis
- Executive: 12.3% success (highest)
- IT Staff: 3.1% success (lowest)
- Finance: 8.7% success

## Key Findings
1. {finding}
2. {finding}

## Recommendations
1. {recommendation}
2. {recommendation}
```

### 7.2 Metrics Dashboard

```
Real-Time Metrics:
┌─────────────────────────────────────────────┐
│  Campaign: CAMP-20260831-001                │
│  Status: ACTIVE | Time Remaining: 14:23     │
├─────────────────────────────────────────────┤
│  Variant A: ████████░░ 78% budget used      │
│  Variant B: ████░░░░░░ 42% budget used      │
│  Variant C: ██░░░░░░░░ 21% budget used      │
├─────────────────────────────────────────────┤
│  Overall Open Rate: 64.2%                   │
│  Click Rate: 38.7%                          │
│  Submission Rate: 9.3%                      │
│  Report Rate: 2.1%                          │
└─────────────────────────────────────────────┘
```

---

## 8. Ethical Guardrails

### Mandatory Rules

1. **Authorization:** Written ROE required for all campaigns
2. **Scope:** Only test infrastructure you own or have explicit permission
3. **Disclosure:** Notify internal security before campaigns begin
4. **Data Handling:** No production data exfiltration in phishing tests
5. **Time Limits:** Hard stop at campaign duration
6. **Escape Hatch:** Immediate halt on any escalation trigger

### Test-Only Infrastructure

```
RECOMMENDED TEST ENVIRONMENTS:
├── Isolated VLAN with no production access
├── Mock Active Directory (test domain only)
├── Fake email server (not production Exchange)
├── Simulation landing pages (no credential storage)
└── Test credit system (no real payment data)
```

---

## 9. Implementation Scripts

### 9.1 Campaign Generator

```python
#!/usr/bin/env python3
"""
Red Team Campaign Generator
Usage: python campaign_gen.py --type phishing --variants 3 --audience exec
"""

import json
import uuid
from datetime import datetime

class CampaignGenerator:
    def __init__(self):
        self.campaign_id = f"CAMP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:3].upper()}"
    
    def generate_ab_test(self, variants, audience_size, budget):
        """Generate A/B test campaign config"""
        per_variant = budget // len(variants)
        
        return {
            "campaign_id": self.campaign_id,
            "type": "ab_test",
            "created": datetime.now().isoformat(),
            "variants": [
                {
                    "id": f"variant_{i}",
                    "weight": 100 // len(variants),
                    "budget": per_variant,
                    "audience": audience_size // len(variants)
                }
                for i in range(len(variants))
            ],
            "metrics": ["open_rate", "click_rate", "conversion_rate"]
        }
    
    def generate_segment_split(self, segments):
        """Generate audience segment configuration"""
        total = sum(s.get("budget_pct", 20) for s in segments)
        
        return {
            "segments": [
                {
                    **s,
                    "adjusted_pct": (s["budget_pct"] / total) * 100
                }
                for s in segments
            ]
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, choices=["phishing", "vishing", "usb_drop"])
    parser.add_argument("--variants", type=int, default=2)
    parser.add_argument("--audience", default="all")
    args = parser.parse_args()
    
    gen = CampaignGenerator()
    campaign = gen.generate_ab_test(args.variants, 1000, 5000)
    print(json.dumps(campaign, indent=2))
```

### 9.2 Budget Allocator

```python
#!/usr/bin/env python3
"""
Dynamic Budget Allocator for Red Team Campaigns
"""

import math

class BudgetAllocator:
    def __init__(self, total_budget, num_variants):
        self.total = total_budget
        self.variants = [f"V{i}" for i in range(num_variants)]
        self.budget = {v: total_budget / num_variants for v in self.variants}
        self.spent = {v: 0 for v in self.variants}
        self.conversions = {v: 0 for v in self.variants}
    
    def allocate_next(self, exploration_factor=0.1):
        """ Allocate budget using UCB1 algorithm """
        total_spent = sum(self.spent.values())
        
        ucb_scores = {}
        for v in self.variants:
            if self.spent[v] == 0:
                ucb_scores[v] = float('inf')  # Explore untested variants
            else:
                avg_reward = self.conversions[v] / self.spent[v]
                exploration = exploration_factor * math.sqrt(
                    math.log(total_spent + 1) / self.spent[v]
                )
                ucb_scores[v] = avg_reward + exploration
        
        # Pick highest UCB with remaining budget
        best_variant = max(ucb_scores, key=ucb_scores.get)
        
        if self.budget[best_variant] > 0:
            allocation = min(100, self.budget[best_variant])
            self.budget[best_variant] -= allocation
            return best_variant, allocation
        
        return None, 0
    
    def record_result(self, variant, success=False):
        """ Record a campaign result """
        self.spent[variant] += 1
        if success:
            self.conversions[variant] += 1
    
    def get_stats(self):
        """ Get current performance stats """
        return {
            v: {
                "spent": self.spent[v],
                "conversions": self.conversions[v],
                "rate": self.conversions[v] / max(self.spent[v], 1),
                "budget_remaining": self.budget[v]
            }
            for v in self.variants
        }
```

---

## 10. Quick Reference

### Campaign Types

| Type | Use Case | Duration | Complexity |
|------|----------|----------|------------|
| **Phishing Sim** | Email security awareness | 24-72h | Low |
| **USB Drop** | Physical security testing | 4-8h | Medium |
| **Rogue AP** | Network security testing | 1-4h | Medium |
| **Vishing** | Social engineering testing | 2-4h | High |
| **Tailgating** | Physical access testing | 1-2h | Medium |

### Statistically Significant Sample Sizes

| Expected Conversion | Sample Size (95% conf) |
|---------------------|------------------------|
| 1% | 15,000+ |
| 5% | 3,000+ |
| 10% | 1,500+ |
| 20% | 800+ |
| 50% | 400+ |

---

*Document Version: 1.0.0*  
*Last Updated: 2026-08-31*  
*Author: Red Team Campaign Framework*
