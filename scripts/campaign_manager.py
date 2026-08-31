#!/usr/bin/env python3
"""
Red Team Campaign Manager
A/B Testing, Multi-Variant, Audience Segmentation, Budget Allocation
"""

import json
import uuid
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class CampaignType(Enum):
    AB_TEST = "ab_test"
    ABN_TEST = "abn_test"
    PHISHING_SIM = "phishing_simulation"
    USB_DROP = "usb_drop"
    ROGUE_AP = "rogue_ap"
    VISHING = "vishing"

class AudienceSegment(Enum):
    C_LEVEL = "c_level"
    IT_STAFF = "it_staff"
    FINANCE = "finance"
    HR = "hr"
    ENGINEERING = "engineering"
    GENERAL = "general"

@dataclass
class CampaignVariant:
    id: str
    name: str
    weight: int  # Percentage (0-100)
    budget: float
    payload: Dict[str, Any]
    max_allocation: float = float('inf')

@dataclass
class AudienceSegmentConfig:
    segment: AudienceSegment
    criteria: List[str]
    budget_percentage: float
    sample_size: int
    template_override: Optional[Dict] = None

@dataclass
class CampaignMetrics:
    campaign_id: str
    variant_id: str
    sent: int = 0
    opened: int = 0
    clicked: int = 0
    converted: int = 0
    reported: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    @property
    def open_rate(self) -> float:
        return (self.opened / self.sent * 100) if self.sent > 0 else 0

    @property
    def click_rate(self) -> float:
        return (self.clicked / self.opened * 100) if self.opened > 0 else 0

    @property
    def conversion_rate(self) -> float:
        return (self.converted / self.clicked * 100) if self.clicked > 0 else 0

    @property
    def report_rate(self) -> float:
        return (self.reported / self.sent * 100) if self.sent > 0 else 0


class CampaignGenerator:
    """Generate campaign configurations for testing"""
    
    TEMPLATES = {
        "phishing": {
            "subjects": [
                "URGENT: {action} Required",
                "Your {service} Account Needs Verification",
                "Security Alert: {action} Immediately",
                "Invoice #{number} Attached - {action}",
                "Meeting Invitation: {topic}"
            ],
            "pretexts": [
                "IT Security Alert",
                "HR Policy Update",
                "Benefit Enrollment Reminder",
                "Vendor Payment Notice",
                "Login Verification Failed"
            ],
            "landing_pages": [
                "microsoft_login.html",
                "google_workspace.html",
                "adobe_sign.html",
                "dropbox_share.html",
                "slack_verify.html"
            ]
        },
        "vishing": {
            "caller_identities": [
                "IT Helpdesk",
                "Security Operations",
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
            ]
        },
        "usb_drop": {
            "labels": [
                "Q4_Budget_{year}.xlsx",
                "Confidential_Merger_Docs.pdf",
                "Employee_Salaries_{year}.csv",
                "IT_Security_Policy.docx",
                "Layoff_List_{month}.txt"
            ],
            "payloads": [
                "autorun.inf",
                "shortcut_with_icon",
                "emotet_stager",
                "payloadless_macro"
            ]
        }
    }

    def __init__(self):
        self.campaign_counter = 0
        self.generated_campaigns = []

    def generate_campaign_id(self) -> str:
        """Generate unique campaign ID"""
        self.campaign_counter += 1
        date_str = datetime.now().strftime('%Y%m%d')
        return f"CAMP-{date_str}-{self.campaign_counter:03d}"

    def generate_ab_test(self, 
                        name: str,
                        variants: List[Dict],
                        audience_size: int,
                        budget: float,
                        duration_hours: int = 48) -> Dict:
        """Generate A/B test campaign"""
        
        campaign = {
            "campaign_id": self.generate_campaign_id(),
            "type": CampaignType.AB_TEST.value,
            "title": name,
            "created": datetime.now().isoformat(),
            "status": "draft",
            "duration_hours": duration_hours,
            "variants": [],
            "audience": {
                "total_size": audience_size,
                "segments": []
            },
            "budget": {
                "total": budget,
                "currency": "test_credits",
                "allocated": 0
            },
            "metrics": {
                "primary": "conversion_rate",
                "secondary": ["open_rate", "click_rate", "report_rate"],
                "target_confidence": 0.95,
                "minimum_sample_size": self._calculate_min_sample(audience_size)
            }
        }
        
        per_variant_budget = budget / len(variants)
        
        for i, variant_config in enumerate(variants):
            variant = CampaignVariant(
                id=f"variant_{i+1}",
                name=variant_config.get("name", f"Variant {i+1}"),
                weight=variant_config.get("weight", 100 // len(variants)),
                budget=per_variant_budget,
                payload=variant_config.get("payload", {})
            )
            campaign["variants"].append(asdict(variant))
            campaign["budget"]["allocated"] += per_variant_budget
        
        return campaign

    def generate_abn_test(self,
                         name: str,
                         variants: List[Dict],
                         segments: List[Dict],
                         total_budget: float) -> Dict:
        """Generate A/B/n test with audience segmentation"""
        
        campaign = {
            "campaign_id": self.generate_campaign_id(),
            "type": CampaignType.ABN_TEST.value,
            "title": name,
            "created": datetime.now().isoformat(),
            "status": "draft",
            "variants": [],
            "audience_segments": segments,
            "budget": {
                "total": total_budget,
                "allocation_strategy": "gradient",
                "distribution": {}
            },
            "metrics": {
                "comparison_method": "chi_square",
                "significance_level": 0.05
            }
        }
        
        total_weight = sum(v.get("weight", 1) for v in variants)
        
        for variant in variants:
            weight_pct = (variant.get("weight", 1) / total_weight) * 100
            budget_share = (variant.get("weight", 1) / total_weight) * total_budget
            
            campaign["variants"].append({
                "id": variant.get("id", f"v_{len(campaign['variants'])+1}"),
                "name": variant.get("name", f"Variant {len(campaign['variants'])+1}"),
                "weight": weight_pct,
                "budget_allocation": budget_share,
                "payload": variant.get("payload", {})
            })
        
        # Calculate segment distribution
        for segment in segments:
            segment_budget = (segment.get("budget_pct", 20) / 100) * total_budget
            campaign["budget"]["distribution"][segment["name"]] = {
                "budget": segment_budget,
                "variants": {v["id"]: segment_budget / len(variants) for v in variants}
            }
        
        return campaign

    def _calculate_min_sample(self, population_size: int, 
                             expected_conversion: float = 0.05,
                             confidence: float = 0.95,
                             mcp: float = 0.05) -> int:
        """Calculate minimum sample size for statistical significance"""
        z = 1.96 if confidence == 0.95 else 2.576
        p = expected_conversion
        margin = mcp
        
        n = (z ** 2 * p * (1 - p)) / (margin ** 2)
        return int(min(n, population_size))

    def generate_phishing_template(self, company: str, target_segment: str) -> Dict:
        """Generate phishing email template"""
        
        template = self.TEMPLATES["phishing"]
        
        return {
            "company": company,
            "target_segment": target_segment,
            "subject_line": self._format_subject(template["subjects"][0], company),
            "body_template": self._generate_body(target_segment),
            "cta_text": self._get_cta(target_segment),
            "landing_page": template["landing_pages"][0],
            "headers": {
                "from": self._get_sender(target_segment),
                "reply_to": "noreply@company.com"
            },
            "tracking": {
                "pixel_url": "https://tracking.test/pixel?id={campaign_id}&v={variant}",
                "link_rewrite": True
            }
        }

    def _format_subject(self, template: str, company: str) -> str:
        """Format subject line with variables"""
        return template.format(
            action="Verify",
            service="Microsoft 365",
            number=f"{uuid.uuid4().hex[:8].upper()}",
            topic="Quarterly Review"
        )

    def _generate_body(self, segment: str) -> str:
        """Generate email body based on segment"""
        bodies = {
            "c_level": "Executive summary indicates urgent action required...",
            "it_staff": "Security scan detected potential vulnerability...",
            "finance": "Invoice payment pending approval...",
            "hr": "New benefits enrollment period opening...",
            "engineering": "Code deployment requires verification...",
            "general": "System notification requires your attention..."
        }
        return bodies.get(segment, bodies["general"])

    def _get_cta(self, segment: str) -> str:
        """Get call-to-action based on segment"""
        ctas = {
            "c_level": "Review Documents",
            "it_staff": "View Security Alert",
            "finance": "Process Payment",
            "hr": "Complete Enrollment",
            "engineering": "Verify Deployment",
            "general": "Take Action"
        }
        return ctas.get(segment, "Take Action")

    def _get_sender(self, segment: str) -> str:
        """Get spoofed sender based on segment"""
        senders = {
            "c_level": "cfo@company.com",
            "it_staff": "it-support@company.com",
            "finance": "accounts@vendor.com",
            "hr": "hr-department@company.com",
            "engineering": "tech-lead@company.com",
            "general": "noreply@company.com"
        }
        return senders.get(segment, "noreply@company.com")


class BudgetAllocator:
    """Dynamic budget allocator using UCB1 algorithm"""
    
    def __init__(self, total_budget: float, num_variants: int, 
                 exploration_factor: float = 0.1):
        self.total_budget = total_budget
        self.variants = [f"V{i}" for i in range(num_variants)]
        self.budget = {v: total_budget / num_variants for v in self.variants}
        self.spent = {v: 0.0 for v in self.variants}
        self.conversions = {v: 0 for v in self.variants}
        self.exploration_factor = exploration_factor
    
    def allocate_next(self) -> Optional[tuple]:
        """Allocate budget using UCB1 for multi-armed bandit"""
        total_spent = sum(self.spent.values())
        
        if total_spent == 0:
            # Initial exploration - distribute equally
            variant = min(self.budget, key=self.budget.get)
            allocation = self.budget[variant]
            self.budget[variant] = 0
            return variant, allocation
        
        ucb_scores = {}
        for v in self.variants:
            if self.spent[v] == 0:
                ucb_scores[v] = float('inf')
            else:
                avg_reward = self.conversions[v] / self.spent[v]
                exploration = self.exploration_factor * math.sqrt(
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
    
    def record_result(self, variant: str, success: bool = False):
        """Record a campaign result"""
        self.spent[variant] += 1
        if success:
            self.conversions[variant] += 1
    
    def get_stats(self) -> Dict:
        """Get current performance statistics"""
        return {
            v: {
                "budget_spent": self.spent[v],
                "conversions": self.conversions[v],
                "conversion_rate": (self.conversions[v] / self.spent[v] * 100) if self.spent[v] > 0 else 0,
                "budget_remaining": self.budget[v],
                "ucb_score": self._calculate_ucb(v)
            }
            for v in self.variants
        }
    
    def _calculate_ucb(self, variant: str) -> float:
        """Calculate UCB score for a variant"""
        total_spent = sum(self.spent.values())
        if self.spent[variant] == 0:
            return float('inf')
        avg_reward = self.conversions[variant] / self.spent[variant]
        exploration = self.exploration_factor * math.sqrt(
            math.log(total_spent + 1) / self.spent[variant]
        )
        return avg_reward + exploration

    def redistribute_budget(self, winner_variant: str, preserve_exploration: bool = True):
        """Redistribute remaining budget toward best performer"""
        remaining = sum(self.budget.values())
        if remaining <= 0:
            return
        
        if winner_variant in self.budget:
            # Give 70% to winner, distribute rest based on performance
            self.budget[winner_variant] += remaining * 0.7
            
            if preserve_exploration:
                # Keep 30% for exploration
                other_budget = remaining * 0.3
                for v in self.variants:
                    if v != winner_variant and self.budget[v] > 0:
                        self.budget[v] += other_budget * (self.conversions[v] / max(sum(self.conversions.values()), 1))


class SegmentAnalyzer:
    """Analyze audience segments for campaign optimization"""
    
    def __init__(self):
        self.segments = {}
    
    def add_segment(self, config: AudienceSegmentConfig):
        """Add audience segment configuration"""
        self.segments[config.segment.value] = {
            "criteria": config.criteria,
            "budget_pct": config.budget_percentage,
            "sample_size": config.sample_size,
            "template_override": config.template_override
        }
    
    def calculate_optimal_distribution(self, total_budget: float) -> Dict:
        """Calculate optimal budget distribution across segments"""
        total_pct = sum(s["budget_pct"] for s in self.segments.values())
        
        distribution = {}
        for segment, config in self.segments.items():
            adjusted_pct = (config["budget_pct"] / total_pct) * 100
            budget = (adjusted_pct / 100) * total_budget
            distribution[segment] = {
                "percentage": adjusted_pct,
                "budget": budget,
                "sample_size": config["sample_size"]
            }
        
        return distribution
    
    def analyze_performance(self, segment_data: Dict) -> Dict:
        """Analyze performance by segment"""
        results = {}
        for segment, metrics in segment_data.items():
            results[segment] = {
                "open_rate": metrics.get("opened", 0) / max(metrics.get("sent", 1), 1) * 100,
                "click_rate": metrics.get("clicked", 0) / max(metrics.get("opened", 1), 1) * 100,
                "conversion_rate": metrics.get("converted", 0) / max(metrics.get("clicked", 1), 1) * 100,
                "efficiency_score": self._calculate_efficiency(metrics)
            }
        return results
    
    def _calculate_efficiency(self, metrics: Dict) -> float:
        """Calculate efficiency score (conversions per dollar spent)"""
        cost_per_send = metrics.get("cost_per_send", 0.01)
        sent = metrics.get("sent", 0)
        converted = metrics.get("converted", 0)
        
        if sent == 0:
            return 0
        return converted / (sent * cost_per_send)


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Red Team Campaign Manager")
    parser.add_argument("--command", required=True, 
                       choices=["generate", "allocate", "analyze"],
                       help="Command to execute")
    parser.add_argument("--type", choices=["ab", "abn", "phishing"],
                       help="Campaign type")
    parser.add_argument("--variants", type=int, default=2,
                       help="Number of variants")
    parser.add_argument("--budget", type=float, default=1000,
                       help="Total budget")
    parser.add_argument("--audience", type=int, default=500,
                       help="Audience size")
    parser.add_argument("--output", help="Output file")
    
    args = parser.parse_args()
    
    generator = CampaignGenerator()
    
    if args.command == "generate":
        if args.type == "ab":
            campaign = generator.generate_ab_test(
                name=f"Test Campaign {args.variants}V",
                variants=[{"name": f"Variant {i+1}", "weight": 100//args.variants} 
                         for i in range(args.variants)],
                audience_size=args.audience,
                budget=args.budget
            )
        elif args.type == "phishing":
            campaign = generator.generate_phishing_template(
                company="TestCorp",
                target_segment="it_staff"
            )
        else:
            print("Unknown campaign type")
            exit(1)
        
        output = json.dumps(campaign, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Campaign saved to {args.output}")
        else:
            print(output)
    
    elif args.command == "allocate":
        allocator = BudgetAllocator(args.budget, args.variants)
        stats = allocator.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.command == "analyze":
        analyzer = SegmentAnalyzer()
        distribution = analyzer.calculate_optimal_distribution(args.budget)
        print(json.dumps(distribution, indent=2))
