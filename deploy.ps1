# Remote SSH deploy: copy the repo to a Linux host and provision it.
# Usage:
#   .\deploy.ps1 -Hostname 1.2.3.4 [-Port 22] [-User root] [-TargetDir /opt/tokugawa] [-NoStart]
param(
  [Parameter(Mandatory=$true)][string]$Hostname,
  [int]$Port = 22,
  [string]$User = "root",
  [string]$TargetDir = "/opt/tokugawa",
  [switch]$NoStart
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$bundle = Join-Path $env:TEMP "tokugawa-deploy-$stamp.tar.gz"

Write-Host "[deploy] packing repo (excluding venv/models/git)..."
tar --exclude='./.git' --exclude='./venv' --exclude='./.venv-vllm' `
    --exclude='./llama.cpp' --exclude='./models/*.gguf' `
    --exclude='./workspaces' --exclude='./backups' `
    -czf $bundle -C $root .

$size = "{0:N1}" -f ((Get-Item $bundle).Length / 1MB)
Write-Host "[deploy] bundle: $bundle ($size MB)"

Write-Host "[deploy] uploading to ${User}@${Hostname}:${TargetDir} ..."
ssh -p $Port "$User@$Hostname" "mkdir -p $TargetDir"
scp -P $Port $bundle "${User}@${Hostname}:$TargetDir/bundle.tar.gz"
ssh -p $Port "$User@$Hostname" "cd $TargetDir && tar -xzf bundle.tar.gz && rm bundle.tar.gz"

$envFlag = ""
if ($NoStart) { $envFlag = "NO_START=1" }
Write-Host "[deploy] provisioning (this builds llama.cpp; ~10-30 min)..."
ssh -t -p $Port "$User@$Hostname" "cd $TargetDir/hardware && $envFlag ./install-stack.sh"

Write-Host ""
Write-Host "[deploy] done. Verify:"
Write-Host "  ssh -p $Port ${User}@${Hostname} 'python3 $TargetDir/tokugawa.py status'"
Write-Host "  dashboard: http://${Hostname}:8030"
