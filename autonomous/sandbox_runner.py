"""OS-level sandbox runner (ROADMAP 16)."""
import subprocess, pathlib, os

def run_sandboxed(cmd, cwd, network_off=False):
    """Try bwrap ? nspawn ? plain subprocess."""
    cwd = pathlib.Path(cwd)
    if network_off and shutil.which("bwrap"):
        cmd = ["bwrap", "--ro-bind", "/", "/", "--unshare-net", "--chdir", str(cwd), "--"] + cmd
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)

import shutil
