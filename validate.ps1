# FreeAI stack offline validator (Windows / PowerShell 5.1+).
# Mirrors validate.sh: structure, JSON, python syntax, quant sanity.
# Usage: .\validate.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$fail = 0

function Check($ok, $msg) {
  if ($ok) { Write-Host "OK   $msg" } else { Write-Host "FAIL $msg"; $script:fail = 1 }
}

Write-Host "== structure =="
foreach ($d in @("router","agents","workflow","autonomous","dashboard","ui",
                 "models","registry","manifest","hardware","k8s","docs","tests")) {
  Check (Test-Path $d) "dir $d/"
}
foreach ($f in @("install.sh","start.sh","validate.sh","supervisor.sh",
                 "docker-compose.yml","freeai.py","requirements.txt",
                 "config\config.json","registry\registry.json","VERSION")) {
  Check (Test-Path $f) "file $f"
}

Write-Host "== json =="
Get-ChildItem -Recurse -Filter *.json | Where-Object { $_.FullName -notmatch '\\\.git\\' } | ForEach-Object {
  try { Get-Content $_.FullName -Raw | ConvertFrom-Json | Out-Null; Write-Host "OK   $($_.Name)" }
  catch { Write-Host "FAIL $($_.Name): $_"; $fail = 1 }
}

Write-Host "== python =="
$pyFiles = Get-ChildItem -Recurse -Filter *.py | Where-Object { $_.FullName -notmatch '\\\.git\\' }
$pyList = ($pyFiles | ForEach-Object { $_.FullName }) -join " "
if ($pyList) {
  python -m py_compile $pyFiles.FullName 2>$null
  Check ($LASTEXITCODE -eq 0) "py_compile all"
}

Write-Host "== quant sanity =="
Get-ChildItem models -Filter *.gguf -ErrorAction SilentlyContinue | ForEach-Object {
  if ($_.Name -notmatch 'Q[4-6]_K|Q8_0|BF16|F16|IQ4') {
    Write-Host "WARN $($_.Name): aggressive quant hurts coherence"
  }
}

Write-Host ""
if ($fail -eq 0) { Write-Host "VALIDATION PASSED" } else { Write-Host "VALIDATION FAILED"; exit 1 }
