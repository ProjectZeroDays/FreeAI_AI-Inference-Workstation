# Security Considerations for Terraform Validation Scripts

## Overview

The `validate-terraform.ps1` and `validate-terraform.sh` scripts execute Terraform commands against infrastructure-as-code directories. Due to the nature of Terraform, these scripts can execute arbitrary code embedded in Terraform configuration files.

## Security Risk

**Terraform configuration can execute arbitrary code** through multiple mechanisms:

1. **External Data Sources**: The `external` data source can invoke arbitrary programs
2. **Provider Plugins**: Providers are executable binaries that run during `terraform init` and `terraform plan`
3. **Local-exec Provisioners**: Can execute shell commands (though less common in validation scenarios)
4. **Provider Configuration**: Some providers execute code during initialization

Any code executed through these mechanisms inherits:
- The operating system privileges of the validation script
- All environment variables (including credentials)
- Network access available to the execution environment
- Filesystem access permissions

## Threat Model

### Attack Scenario
An attacker submits a pull request containing malicious Terraform configuration to a repository. When a CI/CD pipeline runs the validation script against this untrusted code:

1. The malicious configuration uses an `external` data source to execute a script
2. The script exfiltrates credentials from environment variables (e.g., `ARM_CLIENT_SECRET`, `AWS_SECRET_ACCESS_KEY`)
3. The script sends these credentials to an attacker-controlled server
4. The attacker gains access to cloud resources

### Impact
- **Credential Theft**: Cloud provider credentials can be exfiltrated
- **Privilege Escalation**: Execution with CI/CD job privileges
- **Data Exfiltration**: Access to secrets, source code, and infrastructure state
- **Supply Chain Attack**: Compromise of deployment pipeline

## Implemented Mitigations

### 1. Explicit Trust Requirement

**PowerShell**: The `-TrustUntrustedInfra` flag must be explicitly provided when validating non-default paths.

**Bash**: The `TRUST_UNTRUSTED_INFRA=1` environment variable must be set when validating non-default paths.

This prevents accidental execution of untrusted infrastructure and forces operators to consciously acknowledge the security risk.

### 2. Environment Variable Sanitization

Before executing Terraform commands, the scripts temporarily remove sensitive environment variables:

- `ARM_CLIENT_SECRET` (Azure service principal secret)
- `ARM_CLIENT_CERTIFICATE_PASSWORD` (Azure certificate password)
- `AZURE_CLIENT_SECRET` (Azure client secret)
- `AWS_SECRET_ACCESS_KEY` (AWS secret key)
- `AWS_SESSION_TOKEN` (AWS session token)
- `GOOGLE_CREDENTIALS` (GCP credentials JSON)
- `GOOGLE_APPLICATION_CREDENTIALS` (GCP credentials file path)

These variables are restored after Terraform execution completes.

**Note**: This mitigation is defense-in-depth and does not prevent all attacks. Terraform still has access to:
- Azure CLI credentials (via `az` command)
- AWS CLI credentials (via `aws` command)
- Filesystem access to credential files
- Network access to metadata services (e.g., Azure IMDS, AWS EC2 metadata)

### 3. Path Normalization

Input paths are normalized to prevent directory traversal attacks (e.g., `../../etc/passwd`).

### 4. Security Warnings

The scripts display prominent warnings when validating untrusted infrastructure, reminding operators to use proper sandboxing.

## Recommended Security Controls

When validating untrusted infrastructure (e.g., external pull requests), implement these additional controls:

### 1. Sandboxed Execution Environment

Run validation in an isolated environment:
- **Containers**: Use Docker or similar with minimal privileges
- **Virtual Machines**: Ephemeral VMs that are destroyed after validation
- **Serverless**: AWS Lambda, Azure Functions, or similar with restricted IAM roles

### 2. Minimal Credentials

Provide only the minimum credentials required for validation:
- Use read-only service principals/roles
- Limit scope to non-production subscriptions/accounts
- Use short-lived credentials that expire quickly
- Avoid providing credentials for production environments

### 3. Network Isolation

Restrict network access from the validation environment:
- Block outbound internet access except to required Terraform registries
- Use private endpoints for cloud provider APIs
- Monitor and log all network connections
- Use egress filtering to prevent data exfiltration

### 4. Filesystem Isolation

Limit filesystem access:
- Mount only the infrastructure directory (read-only if possible)
- Do not mount sensitive directories (e.g., `/home`, `/root`)
- Use temporary directories that are wiped after execution

### 5. Monitoring and Logging

Implement comprehensive monitoring:
- Log all Terraform executions and their output
- Monitor for suspicious network connections
- Alert on credential access attempts
- Track execution time and resource usage

### 6. Code Review

For high-security environments:
- Require manual code review before automated validation
- Use static analysis tools to detect suspicious Terraform patterns
- Implement approval workflows for external contributions

## Example: Secure CI/CD Configuration

### GitHub Actions Example

```yaml
name: Validate Terraform (Untrusted)

on:
  pull_request_target:  # Use pull_request_target for external PRs

jobs:
  validate:
    runs-on: ubuntu-latest
    
    # Use a separate environment with minimal permissions
    environment: terraform-validation-sandbox
    
    permissions:
      contents: read
      pull-requests: write
    
    steps:
      - name: Checkout PR code
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
      
      # Do NOT provide production credentials
      # Use a read-only service principal with minimal scope
      - name: Azure Login (Read-Only)
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_VALIDATION_READONLY_CREDS }}
      
      - name: Validate Terraform
        run: |
          # Explicitly acknowledge untrusted infrastructure
          TRUST_UNTRUSTED_INFRA=1 \
          ./scripts/validate-terraform.sh ./infra
        
      - name: Comment on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            // Post validation results as PR comment
```

### Azure DevOps Example

```yaml
trigger: none  # Manual trigger only for untrusted code

pool:
  vmImage: 'ubuntu-latest'

steps:
- checkout: self
  clean: true

- task: AzureCLI@2
  displayName: 'Validate Terraform'
  inputs:
    azureSubscription: 'terraform-validation-readonly'  # Read-only service connection
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      # Run in isolated environment with explicit trust flag
      TRUST_UNTRUSTED_INFRA=1 \
      ./scripts/validate-terraform.sh ./infra
```

## Residual Risk

Even with all mitigations in place, some risk remains:

1. **Managed Identity/IAM Role Access**: If the execution environment uses managed identities or IAM roles, Terraform can access these through metadata services
2. **Filesystem Access**: Terraform can read files accessible to the execution user
3. **Network Access**: If internet access is required for provider downloads, data exfiltration is possible
4. **Denial of Service**: Malicious configuration can consume excessive resources

## Conclusion

These scripts implement defense-in-depth security controls but **cannot completely prevent code execution** - that is inherent to Terraform's design. The security model relies on:

1. **Explicit acknowledgment** of risk when validating untrusted infrastructure
2. **Environment-level controls** (sandboxing, minimal credentials, network isolation)
3. **Operational controls** (monitoring, code review, approval workflows)

Always treat validation of untrusted infrastructure as a potentially hostile operation and implement appropriate environmental controls.
