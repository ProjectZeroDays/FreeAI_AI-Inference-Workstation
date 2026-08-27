---
name: cloud-operations
description: Manage cloud infrastructure operations for the QUANTUM C2 framework including cloud enumeration, cloud exploitation, and data/info/target systems analysis. Use when working with cloud security assessments, AWS/Azure/GCP enumeration, cloud vulnerability scanning, and cloud-native attack path analysis.
---

# Cloud Operations

This skill covers cloud infrastructure operations for authorized security assessments and penetration testing within the QUANTUM C2 framework.

## Cloud Enumeration

### AWS Enumeration
- IAM role discovery and permission analysis
- S3 bucket enumeration and access testing
- EC2 instance discovery and metadata probing
- Lambda function enumeration
- Security group and NACL analysis
- CloudTrail log analysis

### Azure Enumeration
- Entra ID (Azure AD) discovery
- Resource group and subscription enumeration
- Storage account access testing
- VM and container instance discovery
- Key Vault enumeration
- Activity Log analysis

### GCP Enumeration
- Project and folder discovery
- IAM policy analysis
- Storage bucket enumeration
- Compute instance discovery
- Cloud SQL enumeration
- Audit log analysis

## Cloud Exploitation

### Common Attack Vectors
- Privilege escalation via misconfigured IAM roles
- Cross-service trust relationship exploitation
- Instance metadata service (IMDSv1) SSRF
- Storage bucket privilege escalation
- Container escape via privileged containers
- Serverless function injection

### Credential Access
- Cloud provider SDK credential harvesting
- Instance profile credential extraction
- Environment variable enumeration
- Secret manager access

## Data/Info/Target Systems

### Cloud Asset Inventory
- Resource tagging analysis
- Service dependency mapping
- Data classification and sensitivity labeling
- Access pattern analysis
- Compliance posture assessment

## Settings Panels

The following settings panels are available:
- `c2-beacon-settings` - C2 beacon configuration
- `c2-channels-settings` - C2 channel configuration
- `c2-encrypt-settings` - Encryption settings

## Navigation
Cloud operations pages are accessible via:
- Cloud Enumeration
- Cloud Exploitation
- Data / Info / Target Systems
