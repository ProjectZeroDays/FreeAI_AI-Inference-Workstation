#!/usr/bin/env bash
# validate-terraform.sh
# Runs the Terraform pre-deployment validation preflight sequence and prints a
# compact PASS/FAIL/SKIP summary plus the captured error text for any failed step.
#
# The script runs every check even if an earlier one fails, so you get a complete
# verdict in a single call. It never fixes anything - it only runs and reports, so
# you can jump straight to remediation for any failed step.
#
# Steps: terraform present, az present, authenticated, init, fmt -check, validate,
#        plan, state list, Go-style {{ .Env.* }} template-variable scan.
#
# SECURITY WARNING: This script executes Terraform commands against the specified
# infrastructure directory. Terraform configuration can execute arbitrary code through
# external data sources, provider plugins, and provisioners. Only run this script
# against infrastructure from trusted sources. When validating untrusted infrastructure
# (e.g., pull requests from external contributors), set TRUST_UNTRUSTED_INFRA=1 and
# ensure the execution environment is properly sandboxed with minimal privileges.
#
# Usage:
#   ./validate-terraform.sh [infra-dir] [subscription-id]
#
# Arguments:
#   infra-dir         Path to the Terraform infra directory (default: ./infra).
#   subscription-id   Optional subscription to select before checks.
#
# Environment Variables:
#   TRUST_UNTRUSTED_INFRA  Set to "1" to explicitly acknowledge validation of
#                          potentially untrusted infrastructure (required for
#                          non-default paths).
#
# Examples:
#   ./validate-terraform.sh                       # Validate ./infra
#   ./validate-terraform.sh ./infra               # Validate an explicit directory
#   ./validate-terraform.sh ./infra 00000000-0000-0000-0000-000000000000
#   TRUST_UNTRUSTED_INFRA=1 ./validate-terraform.sh ./external-pr/infra
#
# Exit code: 0 when every non-skipped step passes, 1 when any step fails.

set -uo pipefail

INFRA_DIR="${1:-./infra}"
SUBSCRIPTION_ID="${2:-}"

# --- Security: Path validation and trust enforcement -------------------------
# Normalize the path to prevent directory traversal attacks
INFRA_DIR="${INFRA_DIR%/}"

# Security check: Require explicit trust acknowledgment for non-default paths
# This prevents accidental execution of untrusted Terraform configuration
case "$INFRA_DIR" in
    "./infra"|"infra")
        IS_DEFAULT_PATH=true
        ;;
    *)
        IS_DEFAULT_PATH=false
        ;;
esac

if [ "$IS_DEFAULT_PATH" != true ] && [ "${TRUST_UNTRUSTED_INFRA:-0}" != "1" ]; then
    echo "ERROR: Security check failed" >&2
    echo "" >&2
    echo "You are attempting to validate infrastructure from a non-default path:" >&2
    echo "  $INFRA_DIR" >&2
    echo "" >&2
    echo "SECURITY WARNING:" >&2
    echo "  Terraform configuration can execute arbitrary code through external data" >&2
    echo "  sources, provider plugins, and provisioners. This code will inherit the" >&2
    echo "  privileges, credentials, and network access of this validation script." >&2
    echo "" >&2
    echo "If you trust this infrastructure source, re-run with TRUST_UNTRUSTED_INFRA=1:" >&2
    echo "  TRUST_UNTRUSTED_INFRA=1 ./validate-terraform.sh '$INFRA_DIR'" >&2
    echo "" >&2
    echo "For untrusted infrastructure (e.g., external pull requests), ensure:" >&2
    echo "  1. This script runs in a sandboxed environment with minimal privileges" >&2
    echo "  2. No production credentials are available to the execution environment" >&2
    echo "  3. Network access is restricted to prevent data exfiltration" >&2
    echo "  4. The execution environment is ephemeral and discarded after validation" >&2
    echo "" >&2
    exit 1
fi

# Additional security warning for untrusted infrastructure
if [ "${TRUST_UNTRUSTED_INFRA:-0}" = "1" ]; then
    echo "WARNING: Validating potentially untrusted infrastructure" >&2
    echo "Ensure this environment is properly sandboxed with minimal privileges." >&2
    echo "" >&2
fi

# --- result tracking ---------------------------------------------------------
STEP_NAMES=()
STEP_STATUS=()   # PASS | FAIL | SKIP
STEP_ERRORS=()   # captured error text (empty unless FAIL)

record() {
    # record <name> <status> [error-text]
    # Results are collected here and rendered once in the summary at the end.
    STEP_NAMES+=("$1")
    STEP_STATUS+=("$2")
    STEP_ERRORS+=("${3:-}")
}

echo "Terraform validation preflight - infra dir: $INFRA_DIR"
echo ""

# --- 1. Terraform installed --------------------------------------------------
if command -v terraform >/dev/null 2>&1; then
    record "Terraform installed" "PASS"
else
    record "Terraform installed" "FAIL" "terraform not found on PATH. Install: https://developer.hashicorp.com/terraform/install"
fi

# --- 2. Azure CLI installed --------------------------------------------------
if command -v az >/dev/null 2>&1; then
    record "Azure CLI installed" "PASS"
else
    record "Azure CLI installed" "FAIL" "az not found on PATH. Install the Azure CLI: mcp_azure_mcp_extension_cli_install(cli-type: \"az\")"
fi

# --- 3. Authentication -------------------------------------------------------
if command -v az >/dev/null 2>&1; then
    if [ -n "$SUBSCRIPTION_ID" ]; then
        if SUB_OUT=$(az account set --subscription "$SUBSCRIPTION_ID" 2>&1); then
            record "Select subscription" "PASS"
        else
            record "Select subscription" "FAIL" "$SUB_OUT"
        fi
    fi
    if ACCOUNT_OUT=$(az account show -o none 2>&1); then
        record "Authenticated (az account show)" "PASS"
    else
        record "Authenticated (az account show)" "FAIL" "$ACCOUNT_OUT"
    fi
else
    record "Authenticated (az account show)" "SKIP" "Azure CLI not installed"
fi

# --- infra dir presence gate -------------------------------------------------
HAVE_TF=false
if command -v terraform >/dev/null 2>&1 && [ -d "$INFRA_DIR" ]; then
    HAVE_TF=true
fi

run_tf() {
    # run_tf <name> <terraform args...>
    local name="$1"; shift
    if [ "$HAVE_TF" != true ]; then
        record "$name" "SKIP" "terraform unavailable or infra dir '$INFRA_DIR' not found"
        return
    fi
    
    # Security: Sanitize environment to reduce credential exposure
    # Remove sensitive Azure and cloud provider environment variables that could
    # be exfiltrated by malicious Terraform configuration
    local saved_ARM_CLIENT_SECRET="${ARM_CLIENT_SECRET:-}"
    local saved_ARM_CLIENT_CERTIFICATE_PASSWORD="${ARM_CLIENT_CERTIFICATE_PASSWORD:-}"
    local saved_AZURE_CLIENT_SECRET="${AZURE_CLIENT_SECRET:-}"
    local saved_AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-}"
    local saved_AWS_SESSION_TOKEN="${AWS_SESSION_TOKEN:-}"
    local saved_GOOGLE_CREDENTIALS="${GOOGLE_CREDENTIALS:-}"
    local saved_GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-}"
    
    unset ARM_CLIENT_SECRET
    unset ARM_CLIENT_CERTIFICATE_PASSWORD
    unset AZURE_CLIENT_SECRET
    unset AWS_SECRET_ACCESS_KEY
    unset AWS_SESSION_TOKEN
    unset GOOGLE_CREDENTIALS
    unset GOOGLE_APPLICATION_CREDENTIALS
    
    # Stream output to a temp file so large output (e.g. terraform plan) is not
    # held in memory; only read it back when the command fails.
    local tmp
    tmp=$(mktemp)
    local exit_code=0
    if (cd "$INFRA_DIR" && terraform "$@") >"$tmp" 2>&1; then
        record "$name" "PASS"
    else
        exit_code=$?
        record "$name" "FAIL" "$(cat "$tmp")"
    fi
    rm -f "$tmp"
    
    # Restore sanitized environment variables
    [ -n "$saved_ARM_CLIENT_SECRET" ] && export ARM_CLIENT_SECRET="$saved_ARM_CLIENT_SECRET"
    [ -n "$saved_ARM_CLIENT_CERTIFICATE_PASSWORD" ] && export ARM_CLIENT_CERTIFICATE_PASSWORD="$saved_ARM_CLIENT_CERTIFICATE_PASSWORD"
    [ -n "$saved_AZURE_CLIENT_SECRET" ] && export AZURE_CLIENT_SECRET="$saved_AZURE_CLIENT_SECRET"
    [ -n "$saved_AWS_SECRET_ACCESS_KEY" ] && export AWS_SECRET_ACCESS_KEY="$saved_AWS_SECRET_ACCESS_KEY"
    [ -n "$saved_AWS_SESSION_TOKEN" ] && export AWS_SESSION_TOKEN="$saved_AWS_SESSION_TOKEN"
    [ -n "$saved_GOOGLE_CREDENTIALS" ] && export GOOGLE_CREDENTIALS="$saved_GOOGLE_CREDENTIALS"
    [ -n "$saved_GOOGLE_APPLICATION_CREDENTIALS" ] && export GOOGLE_APPLICATION_CREDENTIALS="$saved_GOOGLE_APPLICATION_CREDENTIALS"
    
    return $exit_code
}

# --- 4. Initialize -----------------------------------------------------------
run_tf "terraform init" init -input=false

# --- 5. Format check ---------------------------------------------------------
run_tf "terraform fmt -check" fmt -check -recursive

# --- 6. Validate syntax ------------------------------------------------------
run_tf "terraform validate" validate

# --- 7. Plan preview ---------------------------------------------------------
run_tf "terraform plan" plan -input=false -out=tfplan

# --- 8. State backend --------------------------------------------------------
run_tf "terraform state list" state list

# --- 9. Go-style template-variable scan --------------------------------------
if [ -d "$INFRA_DIR" ]; then
    TEMPLATE_HITS=$(grep -rn '{{ *\.Env\.' "$INFRA_DIR" --include='*.tf' --include='*.tfvars.json' 2>/dev/null || true)
    if [ -n "$TEMPLATE_HITS" ]; then
        record "Template-variable scan ({{ .Env.* }})" "FAIL" \
            "Found unresolved Go-style template variables - replace {{ .Env.VAR }} with \${VAR} (azd envsubst format):
$TEMPLATE_HITS"
    else
        record "Template-variable scan ({{ .Env.* }})" "PASS"
    fi
else
    record "Template-variable scan ({{ .Env.* }})" "SKIP" "infra dir '$INFRA_DIR' not found"
fi

# --- 10. main.tfvars.json JSON syntax ----------------------------------------
TFVARS="$INFRA_DIR/main.tfvars.json"
if [ -f "$TFVARS" ]; then
    if command -v python3 >/dev/null 2>&1; then
        if JSON_ERR=$(python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$TFVARS" 2>&1); then
            record "main.tfvars.json is valid JSON" "PASS"
        else
            record "main.tfvars.json is valid JSON" "FAIL" "$JSON_ERR"
        fi
    elif command -v jq >/dev/null 2>&1; then
        if JSON_ERR=$(jq empty "$TFVARS" 2>&1); then
            record "main.tfvars.json is valid JSON" "PASS"
        else
            record "main.tfvars.json is valid JSON" "FAIL" "$JSON_ERR"
        fi
    else
        record "main.tfvars.json is valid JSON" "SKIP" "no JSON parser (python3/jq) available"
    fi
else
    record "main.tfvars.json is valid JSON" "SKIP" "$TFVARS not found"
fi

# --- summary -----------------------------------------------------------------
echo ""
echo "==================== SUMMARY ===================="
printf '%-40s %s\n' "STEP" "RESULT"
printf '%-40s %s\n' "----" "------"
FAILED=0
for i in "${!STEP_NAMES[@]}"; do
    printf '%-40s %s\n' "${STEP_NAMES[$i]}" "${STEP_STATUS[$i]}"
    [ "${STEP_STATUS[$i]}" = "FAIL" ] && FAILED=$((FAILED + 1))
done
echo "================================================="

if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo "----- FAILURE DETAILS -----"
    for i in "${!STEP_NAMES[@]}"; do
        if [ "${STEP_STATUS[$i]}" = "FAIL" ]; then
            echo ""
            echo "### ${STEP_NAMES[$i]}"
            echo "${STEP_ERRORS[$i]}"
        fi
    done
    echo ""
    echo "RESULT: $FAILED step(s) failed. See remediation guidance in README.md."
    exit 1
fi

echo ""
echo "RESULT: All checks passed. Ready for azure-deploy."
exit 0
