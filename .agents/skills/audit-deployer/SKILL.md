---
name: audit-deployer
description: Autonomous deployment and reporting of Red/Blue/Purple Team audits. Orchestrates the full audit lifecycle from targeting to final reporting.
---

# Autonomous Audit Deployer

This skill manages professional security assessments.

## Audit Lifecycle
1. **Target Definition**: Define the scope and objectives of the audit.
2. **Team Selection**: Deploy the appropriate team (Red for breach, Blue for defense, Purple for collaboration).
3. **Execution**: Trigger the `autonomous-red-teaming` or `autonomous-blue-ops` skills.
4. **Evidence Collection**: Use `pegasus-forensics` and `pegasus-loot-mgr` to gather proof of success/failure.
5. **Automated Reporting**: Use `reporting-auditing` to generate the final classified report.
