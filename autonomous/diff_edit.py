"""Diff-based surgical edits (ROADMAP 16) � EDIT_MODE=diff."""
import difflib, pathlib

def apply_diff(root: pathlib.Path, diff_text: str):
    """Apply unified diff to files under root (workspace)."""
    # Minimal: parse --- a/file / +++ b/file headers and hunks
    # For MVP, use `patch -p1` if available
    import subprocess, tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".patch", delete=False) as f:
        f.write(diff_text)
        patch = f.name
    try:
        subprocess.run(["patch", "-p1", "-d", str(root), "-i", patch], check=True, capture_output=True)
        return True
    finally:
        os.unlink(patch)
