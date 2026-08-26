"""Sandboxed code execution (ROADMAP 3)."""
import subprocess, os, pathlib

WORKSPACE_ROOT = pathlib.Path(__file__).parent.parent / "workspaces"

def run_sandboxed(cmd: list, cwd: str, timeout=60, network_off=False):
    """Run cmd inside gVisor-style sandbox if available, else plain subprocess with guards."""
    # Try bubblewrap (bwrap) if present, else nspawn, else plain
    if network_off and shutil.which("bwrap"):
        cmd = ["bwrap", "--ro-bind", "/", "/", "--unshare-net", "--chdir", cwd, "--"] + cmd
    elif shutil.which("systemd-nspawn") and network_off:
        cmd = ["systemd-nspawn", "-D", cwd, "--private-network"] + cmd
    # Path guard: cwd must be inside WORKSPACE_ROOT
    if not pathlib.Path(cwd).resolve().is_relative_to(WORKSPACE_ROOT.resolve()):
        raise ValueError("cwd outside workspace")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)

import shutil
