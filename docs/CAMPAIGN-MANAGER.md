# Red Team Campaign Manager

A/B testing and multi-variant campaign framework for authorized red team security assessments.

## Overview

This framework provides tools for designing, executing, and analyzing security awareness campaigns including:

- **A/B Tests**: Compare two variants against each other
- **A/B/n Tests**: Compare multiple variants simultaneously
- **Audience Segmentation**: Target different departments/roles
- **Budget Allocation**: Optimal distribution across variants
- **Statistical Analysis**: Determine significance of results

## Quick Start

### Generate a Campaign

```bash
# Generate an A/B test campaign
python scripts/campaign_manager.py --command generate --type ab --variants 2 --budget 1000 --audience 500

# Generate a phishing template
python scripts/campaign_manager.py --command generate --type phishing --variants 2

# Generate an A/B/n test with segments
python scripts/campaign_manager.py --command generate --type abn --variants 4 --budget 2000
```

### Budget Allocation

```bash
# View budget allocation stats
python scripts/campaign_manager.py --command allocate --variants 3 --budget 1000

# Analyze segment distribution
python scripts/campaign_manager.py --command analyze --budget 5000
```

## Configuration

### Campaign Config (`config/campaign-config.json`)

Defines:
- Audience segments and criteria
- Email/SMS/USB templates
- Metrics to track
- Escalation triggers
- Ethical guardrails

### Campaign Examples (`config/campaign-examples.json`)

Pre-built campaign templates:
- Phishing simulation (A/B test)
- Email header spoofing (A/B/n test)
- Executive impersonation
- USB drop test
- Rogue Wi-Fi AP test

## Campaign Types

### 1. Phishing Simulation

Tests email security awareness by sending simulated phishing emails.

**Metrics Tracked:**
- Open rate
- Click rate
- Credential submission
- Report rate

**Best Practices:**
- Use test-only infrastructure
- Never store real credentials
- Provide immediate feedback/debrief
- Set clear time boundaries

### 2. USB Drop Test

Physical security assessment using labeled USB drives.

**Metrics Tracked:**
- Insertion rate
- Boot rate
- Payload execution
- Security report rate

**Safety:**
- Use simulation payloads only
- Monitor with cameras/logging
- Immediate removal after test window

### 3. Rogue Wi-Fi AP

Network security test using rogue access points.

**Metrics Tracked:**
- Device connections
- Authentication attempts
- Time to connect

**Legal:**
- Obtain location permits
- No data retention
- Immediate shutdown capability

### 4. Vishing (Voice Phishing)

Social engineering via phone calls.

**Metrics Tracked:**
- Information obtained
- Call duration
- Compliance score

**Ethical:**
- No threats or coercion
- Immediate debrief
- Opt-out available

## Statistical Analysis

### Sample Size Calculator

```python
from campaign_manager import CampaignGenerator

generator = CampaignGenerator()
min_sample = generator._calculate_min_sample(
    population_size=500,
    expected_conversion=0.05,
    confidence=0.95,
    mcp=0.05
)
print(f"Minimum sample size: {min_sample}")
```

### Budget Allocation (UCB1 Algorithm)

```python
from campaign_manager import BudgetAllocator

allocator = BudgetAllocator(total_budget=1000, num_variants=3)

# Allocate budget using multi-armed bandit
variant, amount = allocator.allocate_next()
print(f"Allocate ${amount} to {variant}")

# Record results
allocator.record_result(variant, success=True)

# Get stats
stats = allocator.get_stats()
print(json.dumps(stats, indent=2))
```

### Segment Analysis

```python
from campaign_manager import SegmentAnalyzer

analyzer = SegmentAnalyzer()
analyzer.add_segment(config)  # Add your segments

# Calculate optimal distribution
distribution = analyzer.calculate_optimal_distribution(total_budget=5000)
print(json.dumps(distribution, indent=2))

# Analyze performance
performance = analyzer.analyze_performance(segment_data)
print(json.dumps(performance, indent=2))
```

## Campaign Execution Workflow

### 1. Pre-Campaign

```
□ Authorization verified (ROE documented)
□ Target scope confirmed
□ Legal/compliance review completed
□ Rollback plan documented
□ SOC notification sent
□ Monitoring configured
□ Response team on standby
```

### 2. Execution

```
1. Generate campaign ID
2. Distribute variants across segments
3. Set budget allocation
4. Start timestamp
5. Monitor real-time metrics
6. Watch for escalation triggers
7. Log all interactions
```

### 3. Post-Campaign

```
1. Calculate success rates per variant
2. Statistical significance testing
3. Segment analysis
4. Generate report
5. Update defensive posture
6. Archive campaign data
```

## Ethical Guardrails

### Mandatory Rules

1. **Authorization**: Written ROE required for all campaigns
2. **Scope**: Only test infrastructure you own or have explicit permission
3. **Disclosure**: Notify internal security before campaigns begin
4. **Data Handling**: No production data exfiltration
5. **Time Limits**: Hard stop at campaign duration
6. **Escape Hatch**: Immediate halt on any escalation trigger

### Escalation Triggers

- Real user reported to security
- Potential legal/regulatory issue
- Sensitive data accessed
- Service impacted
- Duration exceeded
- Budget exceeded

## API Reference

### CampaignGenerator

```python
class CampaignGenerator:
    def generate_ab_test(self, name, variants, audience_size, budget, duration_hours=48) -> Dict
    def generate_abn_test(self, name, variants, segments, total_budget) -> Dict
    def generate_phishing_template(self, company, target_segment) -> Dict
    def generate_campaign_id(self) -> str
```

### BudgetAllocator

```python
class BudgetAllocator:
    def __init__(self, total_budget, num_variants, exploration_factor=0.1)
    def allocate_next(self) -> Optional[tuple]
    def record_result(self, variant, success=False)
    def get_stats(self) -> Dict
    def redistribute_budget(self, winner_variant, preserve_exploration=True)
```

### SegmentAnalyzer

```python
class SegmentAnalyzer:
    def add_segment(self, config: AudienceSegmentConfig)
    def calculate_optimal_distribution(self, total_budget) -> Dict
    def analyze_performance(self, segment_data) -> Dict
```

## Example: Full Campaign

```python
import json
from campaign_manager import CampaignGenerator, BudgetAllocator, SegmentAnalyzer

# Initialize
generator = CampaignGenerator()
allocator = BudgetAllocator(1000, 3)
analyzer = SegmentAnalyzer()

# Generate campaign
campaign = generator.generate_ab_test(
    name="Phishing Test - IT Staff",
    variants=[
        {"name": "Urgency", "weight": 50, "payload": {"subject": "URGENT: Password Expire"}},
        {"name": "Authority", "weight": 50, "payload": {"subject": "IT: Security Update"}}
    ],
    audience_size=100,
    budget=500,
    duration_hours=24
)

# Add segments
from campaign_manager import AudienceSegment, AudienceSegmentConfig
config = AudienceSegmentConfig(
    segment=AudienceSegment.IT_STAFF,
    criteria=["department=IT", "title_contains_admin"],
    budget_percentage=30,
    sample_size=50
)
analyzer.add_segment(config)

# Get stats
stats = allocator.get_stats()

# Output
print(json.dumps(campaign, indent=2))
print(json.dumps(stats, indent=2))
```

## Files

| File | Description |
|------|-------------|
| `scripts/campaign_manager.py` | Main Python module with classes |
| `config/campaign-config.json` | Default configuration |
| `config/campaign-examples.json` | Pre-built campaign templates |
| `docs/redteam-campaign-framework.md` | This documentation |

## License

Internal use only - Red Team authorization required.

## Support

For questions about campaign design or statistical analysis, contact the Red Team lead.
