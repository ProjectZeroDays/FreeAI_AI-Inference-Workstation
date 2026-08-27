# GPU Benchmark — FreeAI Workstation
# Runs 10 warmup + 10 real inferences and reports tokens/sec, latency, GPU util.
# Usage (Windows PowerShell):  .\scripts\gpu-benchmark.ps1
# Usage (bash):               bash scripts/gpu-benchmark.sh

param(
    [int[]]$Devices = @(),
    [int]$WarmupRuns   = 10,
    [int]$BenchmarkRuns = 10,
    [int]$SeqLen        = 64,
    [int]$BatchSize     = 1,
    [string]$Output     = "scripts/gpu-benchmark-results.json"
)

$ErrorActionPreference = "Continue"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$RESULTS_PATH = Join-Path $ROOT $Output

function Write-Header {
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host "  GPU Benchmark — FreeAI Workstation" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

function Test-NvidiaSmi {
    try {
        $out = nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader,nounits 2>$null
        return $out -ne $null
    } catch { return $false }
}

function Run-TorchBenchmark($deviceId) {
    $success = $false
    $results = @()
    $totalMs = 0.0

    try {
        $code = @'
import torch, time, json, sys
idx = int(sys.argv[1])
iters = int(sys.argv[2])
batch = int(sys.argv[3])
seq   = int(sys.argv[4])
torch.cuda.set_device(idx)
dtypes = [torch.float16] if torch.cuda.is_bf16_supported() else [torch.float32]
times = []
for _ in range(iters):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for __ in range(5):
        a = torch.randn(batch, seq, 512, device=f"cuda:{idx}", dtype=dtypes[0])
        b = torch.randn(512, 512, device=f"cuda:{idx}", dtype=dtypes[0])
        _ = torch.mm(a.reshape(-1, 512), b)
    torch.cuda.synchronize()
    times.append((time.perf_counter() - t0) * 1000)
peak = torch.cuda.max_memory_allocated(idx) / (1024*1024)
print(json.dumps({"avg_ms": round(sum(times)/len(times), 2), "peak_vram_mb": round(peak, 1)}))
'@

        $tmpFile = [System.IO.Path]::GetTempFileName() + ".py"
        $code | Out-File -FilePath $tmpFile -Encoding utf8
        $proc = Start-Process -FilePath (Get-Command python | Select-Object -ExpandProperty Source) `
            -ArgumentList $tmpFile, $deviceId, $BenchmarkRuns, $BatchSize, $SeqLen `
            -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$tmpFile.out" `
            -RedirectStandardError "$tmpFile.err" 2>$null
        Remove-Item $tmpFile -Force -ErrorAction SilentlyContinue
        Remove-Item "$tmpFile.out" -Force -ErrorAction SilentlyContinue
        Remove-Item "$tmpFile.err" -Force -ErrorAction SilentlyContinue
        if (Test-Path "$tmpFile.out") {
            $jsonStr = Get-Content "$tmpFile.out" -Raw -ErrorAction SilentlyContinue
            if ($jsonStr) {
                return $jsonStr | ConvertFrom-Json
            }
        }
        return $null
    } catch {
        return $null
    } finally {
        Remove-Item $tmpFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Header

# Detect GPUs
if (-not (Test-NvidiaSmi)) {
    Write-Host "`nNo NVIDIA GPU detected. Skipping benchmark." -ForegroundColor Yellow
    $result = @{ skipped = $true; reason = "no-gpu" }
    $result | ConvertTo-Json | Out-File -FilePath $RESULTS_PATH -Encoding utf8
    Write-Host "Results → $RESULTS_PATH"
    exit 0
}

$gpuOut = nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader,nounits
$gpus = @()
foreach ($line in $gpuOut.Trim().Split("`n")) {
    $parts = $line.Split(",") | ForEach-Object { $_.Trim() }
    if ($parts.Count -ge 3) {
        $gpus += [PSCustomObject]@{
            index      = [int]$parts[0]
            name       = $parts[1]
            total_vram = [int]$parts[2] * 1024
        }
    }
}

if ($Devices.Count -gt 0) {
    $gpus = $gpus | Where-Object { $Devices -contains $_.index }
}

Write-Host "`nDetected $($gpus.Count) GPU(s):"
foreach ($g in $gpus) {
    Write-Host "  GPU $($g.index): $($g.name) ($($g.total_vram) MB)"
}

# Warmup phase
Write-Host "`n--- Warmup phase ($WarmupRuns runs per GPU) ---"
foreach ($g in $gpus) {
    Write-Host "  Warming GPU $($g.index)..." -NoNewline
    $wr = Run-TorchBenchmark $g.index $WarmupRuns $BatchSize $SeqLen
    if ($wr) {
        Write-Host " done (first-pass avg≈$($wr.avg_ms)ms)"
    } else {
        Write-Host " skipped (torch unavailable)"
    }
}

# Benchmark phase
Write-Host "`n--- Benchmark phase ($BenchmarkRuns runs per GPU) ---"
$allResults = @()
foreach ($g in $gpus) {
    Write-Host "`nGPU $($g.index): $($g.name)" -ForegroundColor Green
    $r = Run-TorchBenchmark $g.index $BenchmarkRuns $BatchSize $SeqLen
    if ($r) {
        Write-Host "  avg_latency_ms : $($r.avg_ms)"
        Write-Host "  peak_vram_mb   : $($r.peak_vram_mb)"
        $op = $BenchmarkRuns * 5 * $BatchSize * $SeqLen * 512  # rough FLOP estimate
        $throughput = if ($r.avg_ms -gt 0) {
            [math]::Round($op / ($r.avg_ms / 1000) / 1e9, 2)
        } else { 0 }
        Write-Host "  est_throughput  : ${throughput} GFLOPS"
        $allResults += [PSCustomObject]@{
            device_index   = $g.index
            device_name    = $g.name
            total_vram_mb  = $g.total_vram
            avg_latency_ms = $r.avg_ms
            peak_vram_mb   = $r.peak_vram_mb
            throughput_gflops = $throughput
        }
    } else {
        Write-Host "  [skip] torch not available"
        $allResults += [PSCustomObject]@{
            device_index    = $g.index
            device_name     = $g.name
            total_vram_mb   = $g.total_vram
            avg_latency_ms  = $null
            peak_vram_mb    = $null
            throughput_gflops = $null
            status          = "skipped-no-torch"
        }
    }
}

# GPU utilization snapshot
$utilOut = nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.cores,power.draw --format=csv,noheader,nounits 2>$null
$utilLines = @()
if ($utilOut) {
    $utilLines = $utilOut.Trim().Split("`n")
}

# Build final JSON
$timestamp = Get-Date -Format "o"
$result = @{
    timestamp        = $timestamp
    gpu_count        = $gpus.Count
    warmup_runs      = $WarmupRuns
    benchmark_runs   = $BenchmarkRuns
    batch_size       = $BatchSize
    seq_len          = $SeqLen
    devices          = $allResults
    utilization_snap = $utilLines
}

$result | ConvertTo-Json -Depth 4 | Out-File -FilePath $RESULTS_PATH -Encoding utf8
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "  Results saved → $RESULTS_PATH" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
