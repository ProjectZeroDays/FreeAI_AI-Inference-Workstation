"""Sandboxed workspace for autonomous runs.

All file operations are rooted at WORKSPACES_DIR/<run_id>/ and every
path is resolved against that root — traversal outside it is rejected.
"""
import os

WORKSPACES_DIR = os.environ.get(
    "WORKSPACES_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "workspaces"))

MAX_FILE_BYTES = int(os.environ.get("MAX_FILE_BYTES", 512 * 1024))

# Files the engine itself owns — never listed as project output.
_INTERNAL_FILES = {"_run.json"}


class Workspace:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.root = os.path.join(WORKSPACES_DIR, run_id)

    def init(self):
        os.makedirs(self.root, exist_ok=True)
        return self.root

    def resolve(self, rel_path: str) -> str:
        """Resolve a workspace-relative path; block traversal."""
        raw = rel_path or ""
        if raw.startswith(("/", "\\")) or ":" in raw:
            raise ValueError(f"unsafe path: {rel_path!r}")
        clean = raw.replace("\\", "/").lstrip("/")
        if not clean or clean.startswith("..") or "/../" in f"/{clean}":
            raise ValueError(f"unsafe path: {rel_path!r}")
        full = os.path.abspath(os.path.join(self.root, clean))
        root = os.path.abspath(self.root)
        if not full.startswith(root + os.sep):
            raise ValueError(f"unsafe path: {rel_path!r}")
        return full

    def write_file(self, rel_path: str, content: str) -> int:
        full = self.resolve(rel_path)
        data = content.encode("utf-8")
        if len(data) > MAX_FILE_BYTES:
            raise ValueError(f"file too large: {rel_path} "
                             f"({len(data)} > {MAX_FILE_BYTES})")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        return len(data)

    def read_file(self, rel_path: str) -> str:
        with open(self.resolve(rel_path), encoding="utf-8",
                  errors="replace") as f:
            return f.read()

    def list_files(self) -> list:
        files = []
        for base, _dirs, names in os.walk(self.root):
            for name in names:
                if name in _INTERNAL_FILES or name.endswith(".tar.gz"):
                    continue  # engine-owned state + packaged artifacts
                full = os.path.join(base, name)
                rel = os.path.relpath(full, self.root).replace("\\", "/")
                files.append({"path": rel,
                              "bytes": os.path.getsize(full)})
        return sorted(files, key=lambda f: f["path"])

    def artifact_path(self) -> str:
        return os.path.join(self.root, "_artifact.tar.gz")
