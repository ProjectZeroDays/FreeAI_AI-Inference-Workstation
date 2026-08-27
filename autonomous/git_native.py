"""Git-native runs (ROADMAP 16)."""
import subprocess, pathlib

def git_init_run(workspace: pathlib.Path, spec: str):
    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "freeai@local"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.name", "FreeAI"], cwd=workspace, check=True)
    (workspace / ".gitignore").write_text("*.pyc\n__pycache__/\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", f"init: {spec[:72]}"], cwd=workspace, check=True)

def git_commit_phase(workspace: pathlib.Path, phase: str):
    subprocess.run(["git", "add", "."], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", phase], cwd=workspace, check=False)

def export_branch_archive(workspace: pathlib.Path, out_tar: pathlib.Path):
    subprocess.run(["git", "archive", "--format=tar.gz", "-o", str(out_tar), "HEAD"], cwd=workspace, check=True)
    return out_tar
