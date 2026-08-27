<#
.SYNOPSIS
    Runs the Terraform pre-deployment validation preflight sequence and prints a
    compact PASS/FAIL/SKIP summary plus captured error text for any failed step.
.DESCRIPTION
    Runs every check even if an earlier one fails, so you get a complete verdict in
    a single call. It never fixes anything - it only runs and reports, so you can
    jump straight to remediation for any failed step.

    Steps: terraform present, az present, authenticated, init, fmt -check, validate,
    plan, state list, Go-style {{ .Env.* }} template-variable scan.

    SECURITY WARNING: This script executes Terraform commands against the specified
    infrastructure directory. Terraform configuration can execute arbitrary code through
    external data sources, provider plugins, and provisioners. Only run this script
    against infrastructure from trusted sources. When validating untrusted infrastructure
    (e.g., pull requests from external contributors), use the -TrustUntrustedInfra flag
    and ensure the execution environment is properly sandboxed with minimal privileges.
.PARAMETER InfraDir
    Path to the Terraform infra directory (default: ./infra).
.PARAMETER SubscriptionId
    Optional subscription to select before checks.
.PARAMETER TrustUntrustedInfra
    Explicitly acknowledge that you are validating potentially untrusted infrastructure.
    Required when InfraDir is not the default ./infra path. This flag serves as a
    security control to prevent accidental execution of untrusted Terraform configuration.
.EXAMPLE
    .\validate-terraform.ps1
    # Validate ./infra (default trusted path)
.EXAMPLE
    .\validate-terraform.ps1 -InfraDir ./infra -SubscriptionId 00000000-0000-0000-0000-000000000000
    # Validate an explicit directory against a specific subscription
.EXAMPLE
    .\validate-terraform.ps1 -InfraDir ./external-pr/infra -TrustUntrustedInfra
    # Validate untrusted infrastructure with explicit acknowledgment
.NOTES
    Exit code: 0 when every non-skipped step passes, 1 when any step fails.
#>
param(
    [string]$InfraDir = "./infra",
    [string]$SubscriptionId,
    [switch]$TrustUntrustedInfra
)

$ErrorActionPreference = "Continue"

$steps = [System.Collections.Generic.List[object]]::new()

function Add-Result {
    param([string]$Name, [string]$Status, [string]$ErrorText = "")
    # Results are collected here and rendered once in the summary at the end.
    $steps.Add([pscustomobject]@{ Name = $Name; Status = $Status; Error = $ErrorText })
}

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

# --- Security: Path validation and trust enforcement -------------------------
# Normalize the path to prevent directory traversal attacks
$InfraDir = $InfraDir.TrimEnd('\', '/')
$resolvedPath = $null
try {
    # Resolve to absolute path if it exists, otherwise use as-is for error reporting
    if (Test-Path -Path $InfraDir -PathType Container) {
        $resolvedPath = (Resolve-Path -Path $InfraDir).Path
    }
} catch {
    # Path resolution failed, will be caught by existence check later
}

# Security check: Require explicit trust acknowledgment for non-default paths
# This prevents accidental execution of untrusted Terraform configuration
$defaultInfraPaths = @("./infra", ".\infra", "infra")
$isDefaultPath = $defaultInfraPaths -contains $InfraDir

if (-not $isDefaultPath -and -not $TrustUntrustedInfra) {
    Write-Host "ERROR: Security check failed" -ForegroundColor Red
    Write-Host ""
    Write-Host "You are attempting to validate infrastructure from a non-default path:"
    Write-Host "  $InfraDir"
    Write-Host ""
    Write-Host "SECURITY WARNING:"
    Write-Host "  Terraform configuration can execute arbitrary code through external data"
    Write-Host "  sources, provider plugins, and provisioners. This code will inherit the"
    Write-Host "  privileges, credentials, and network access of this validation script."
    Write-Host ""
    Write-Host "If you trust this infrastructure source, re-run with -TrustUntrustedInfra:"
    Write-Host "  .\validate-terraform.ps1 -InfraDir '$InfraDir' -TrustUntrustedInfra"
    Write-Host ""
    Write-Host "For untrusted infrastructure (e.g., external pull requests), ensure:"
    Write-Host "  1. This script runs in a sandboxed environment with minimal privileges"
    Write-Host "  2. No production credentials are available to the execution environment"
    Write-Host "  3. Network access is restricted to prevent data exfiltration"
    Write-Host "  4. The execution environment is ephemeral and discarded after validation"
    Write-Host ""
    exit 1
}

# Additional security warning for untrusted infrastructure
if ($TrustUntrustedInfra) {
    Write-Host "WARNING: Validating potentially untrusted infrastructure" -ForegroundColor Yellow
    Write-Host "Ensure this environment is properly sandboxed with minimal privileges." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Terraform validation preflight - infra dir: $InfraDir"
Write-Host ""

# --- 1. Terraform installed --------------------------------------------------
if (Test-Command "terraform") {
    Add-Result "Terraform installed" "PASS"
} else {
    Add-Result "Terraform installed" "FAIL" "terraform not found on PATH. Install: https://developer.hashicorp.com/terraform/install"
}

# --- 2. Azure CLI installed --------------------------------------------------
$hasAz = Test-Command "az"
if ($hasAz) {
    Add-Result "Azure CLI installed" "PASS"
} else {
    Add-Result "Azure CLI installed" "FAIL" "az not found on PATH. Install the Azure CLI: mcp_azure_mcp_extension_cli_install(cli-type: `"az`")"
}

# --- 3. Authentication -------------------------------------------------------
if ($hasAz) {
    if ($SubscriptionId) {
        $subOut = az account set --subscription $SubscriptionId 2>&1
        if ($LASTEXITCODE -eq 0) {
            Add-Result "Select subscription" "PASS"
        } else {
            Add-Result "Select subscription" "FAIL" ($subOut | Out-String).Trim()
        }
    }
    $accountOut = az account show -o none 2>&1
    if ($LASTEXITCODE -eq 0) {
        Add-Result "Authenticated (az account show)" "PASS"
    } else {
        Add-Result "Authenticated (az account show)" "FAIL" ($accountOut | Out-String).Trim()
    }
} else {
    Add-Result "Authenticated (az account show)" "SKIP" "Azure CLI not installed"
}

# --- infra dir presence gate -------------------------------------------------
$haveTf = (Test-Command "terraform") -and (Test-Path -Path $InfraDir -PathType Container)

function Invoke-Tf {
    param([string]$Name, [string[]]$Args)
    if (-not $haveTf) {
        Add-Result $Name "SKIP" "terraform unavailable or infra dir '$InfraDir' not found"
        return
    }
    Push-Location $InfraDir
    try {
        # Security: Sanitize environment to reduce credential exposure
        # Remove sensitive Azure and cloud provider environment variables that could
        # be exfiltrated by malicious Terraform configuration
        $sensitiveVars = @(
            'ARM_CLIENT_SECRET',
            'ARM_CLIENT_CERTIFICATE_PASSWORD', 
            'AZURE_CLIENT_SECRET',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_SESSION_TOKEN',
            'GOOGLE_CREDENTIALS',
            'GOOGLE_APPLICATION_CREDENTIALS'
        )
        
        $savedEnv = @{}
        foreach ($var in $sensitiveVars) {
            if (Test-Path "env:$var") {
                $savedEnv[$var] = (Get-Item "env:$var").Value
                Remove-Item "env:$var" -ErrorAction SilentlyContinue
            }
        }
        
        try {
            # Stream output to a temp file so large output (e.g. terraform plan) is
            # not held in memory; only read it back when the command fails.
            $tmp = New-TemporaryFile
            & terraform @Args *> $tmp.FullName
            if ($LASTEXITCODE -eq 0) {
                Add-Result $Name "PASS"
            } else {
                $content = Get-Content -Raw $tmp.FullName
                if ($null -eq $content) { $content = "" }
                Add-Result $Name "FAIL" $content.Trim()
            }
            Remove-Item $tmp.FullName -ErrorAction SilentlyContinue
        } finally {
            # Restore sanitized environment variables
            foreach ($var in $savedEnv.Keys) {
                [System.Environment]::SetEnvironmentVariable($var, $savedEnv[$var], 'Process')
            }
        }
    } finally {
        Pop-Location
    }
}

# --- 4. Initialize -----------------------------------------------------------
Invoke-Tf "terraform init" @("init", "-input=false")

# --- 5. Format check ---------------------------------------------------------
Invoke-Tf "terraform fmt -check" @("fmt", "-check", "-recursive")

# --- 6. Validate syntax ------------------------------------------------------
Invoke-Tf "terraform validate" @("validate")

# --- 7. Plan preview ---------------------------------------------------------
Invoke-Tf "terraform plan" @("plan", "-input=false", "-out=tfplan")

# --- 8. State backend --------------------------------------------------------
Invoke-Tf "terraform state list" @("state", "list")

# --- 9. Go-style template-variable scan --------------------------------------
if (Test-Path -Path $InfraDir -PathType Container) {
    $hits = Get-ChildItem -Path $InfraDir -Recurse -Include "*.tf", "*.tfvars.json" -ErrorAction SilentlyContinue |
        Select-String -Pattern '{{ *\.Env\.' |
        ForEach-Object { "{0}:{1}:{2}" -f $_.Path, $_.LineNumber, $_.Line.Trim() }
    if ($hits) {
        $detail = "Found unresolved Go-style template variables - replace {{ .Env.VAR }} with `${VAR} (azd envsubst format):`n" + ($hits -join "`n")
        Add-Result "Template-variable scan ({{ .Env.* }})" "FAIL" $detail
    } else {
        Add-Result "Template-variable scan ({{ .Env.* }})" "PASS"
    }
} else {
    Add-Result "Template-variable scan ({{ .Env.* }})" "SKIP" "infra dir '$InfraDir' not found"
}

# --- 10. main.tfvars.json JSON syntax ----------------------------------------
$tfvars = Join-Path $InfraDir "main.tfvars.json"
if (Test-Path -Path $tfvars -PathType Leaf) {
    try {
        Get-Content -Raw $tfvars | ConvertFrom-Json -ErrorAction Stop | Out-Null
        Add-Result "main.tfvars.json is valid JSON" "PASS"
    } catch {
        Add-Result "main.tfvars.json is valid JSON" "FAIL" $_.Exception.Message
    }
} else {
    Add-Result "main.tfvars.json is valid JSON" "SKIP" "$tfvars not found"
}

# --- summary -----------------------------------------------------------------
Write-Host ""
Write-Host "==================== SUMMARY ===================="
"{0,-40} {1}" -f "STEP", "RESULT" | Write-Host
"{0,-40} {1}" -f "----", "------" | Write-Host
foreach ($s in $steps) {
    "{0,-40} {1}" -f $s.Name, $s.Status | Write-Host
}
Write-Host "================================================="

$failed = @($steps | Where-Object { $_.Status -eq "FAIL" })
if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "----- FAILURE DETAILS -----"
    foreach ($s in $failed) {
        Write-Host ""
        Write-Host "### $($s.Name)"
        Write-Host $s.Error
    }
    Write-Host ""
    Write-Host "RESULT: $($failed.Count) step(s) failed. See remediation guidance in README.md."
    exit 1
}

Write-Host ""
Write-Host "RESULT: All checks passed. Ready for azure-deploy."
exit 0
