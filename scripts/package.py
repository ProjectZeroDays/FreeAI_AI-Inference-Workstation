#!/usr/bin/env python3
"""Package builder for FreeAI Unified AI Stack.

Creates a versioned tar.gz source bundle excluding VCS, caches, and runtime
artifacts. Includes VERSION, CHANGELOG.md, and LICENSE. Generates a SHA256
checksum file alongside the archive.

Usage:
    python scripts/package.py                        # bundle to dist/ using VERSION
    python scripts/package.py --version 1.2.0        # override version
    python scripts/package.py --output /tmp/out      # custom output directory
    python scripts/package.py --list                   # show what would be included/excluded
"""
import argparse
import hashlib
import os
import tarfile
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "config" / "VERSION"
DIST_DIR = ROOT / "dist"

# Patterns to exclude from the archive
EXCLUDE_PATTERNS = {
    ".git",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".venv",
    "venv",
    "node_modules",
    "llama.cpp",
    "models",
    "logs",
    "workspaces",
    "backups",
    "dist",
    ".pytest_cache",
    ".runs",
    ".agents",
    ".opencode",
    ".mimocode",
    ".github",
    ".gitignore",
    ".env",
    ".env.*",
    "config/runtime-settings.json",
    "config/presentials.json",
    "config/providers.json",
    "config/browser.json",
    "config/activity_log.jsonl",
    "config/runtime-state.json",
    "config/secrets.enc.yaml",
    "config/llama.env",
    "uploads",
    "site",
    "age.key",
    "*.log",
    "*.err.log",
    "dashboard.err.log",
    "dashboard.log",
    "workflow.json",
}

REQUIRED_FILES = ["VERSION", "CHANGELOG.md", "LICENSE", "README.md"]


def matches_exclude(path_parts):
    for exc in EXCLUDE_PATTERNS:
        if exc.startswith("*"):
            # extension match against the file name
            if path_parts and path_parts[-1].endswith(exc):
                return True
        else:
            if exc in path_parts:
                return True
    return False


def get_version():
    v = VERSION_FILE.read_text().strip()
    import re
    if not re.match(r"^\d+\.\d+\.\d+$", v):
        print(f"ERROR: invalid VERSION: {v!r}", file=sys.stderr)
        sys.exit(1)
    return v


def build_listing(version):
    included, excluded = [], []
    for path in sorted(ROOT.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(ROOT)
        parts = rel.parts
        if matches_exclude(parts):
            excluded.append(str(rel))
            continue
        included.append(str(rel))
    return included, excluded


def cmd_list(args):
    version = args.version or get_version()
    included, excluded = build_listing(version)
    print(f"Version: {version}")
    print(f"Included: {len(included)} files")
    for f in included:
        print(f"  + {f}")
    print(f"Excluded: {len(excluded)} paths")
    for f in excluded:
        print(f"  - {f}")


def cmd_package(args):
    version = args.version or get_version()
    output_dir = Path(args.output) if args.output else DIST_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    included, excluded = build_listing(version)

    if not included:
        print("ERROR: no files selected for packaging", file=sys.stderr)
        sys.exit(1)

    archive_name = f"freeai-workstation-{version}.tar.gz"
    archive_path = output_dir / archive_name

    print(f"Building {archive_name} ({len(included)} files)...")
    with tarfile.open(archive_path, "w:gz") as tar:
        for rel in included:
            full = ROOT / rel
            tar.add(full, arcname=rel)
            print(f"  adding {rel}")

    # Verify required files are present
    with tarfile.open(archive_path, "r:gz") as tar:
        names = tar.getnames()
        for rf in REQUIRED_FILES:
            if rf not in names:
                print(f"WARNING: required file {rf} not in archive", file=sys.stderr)

    # Generate checksum
    h = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_line = f"{h}  {archive_name}\n"
    checksum_path = output_dir / "sha256sums.txt"
    # Append to existing checksums file rather than overwrite
    existing = checksum_path.read_text() if checksum_path.exists() else ""
    checksum_path.write_text(existing.rstrip() + "\n" + checksum_line if existing.strip() else checksum_line)

    size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"\nArchive: {archive_path}")
    print(f"Size:    {size_mb:.2f} MB")
    print(f"SHA256:  {h}")
    print(f"Checksum saved to: {checksum_path}")

    # Print summary
    print(f"\nIncluded: {len(included)} files")
    if excluded:
        print(f"Excluded: {len(excluded)} paths (see --list for details)")


def main():
    parser = argparse.ArgumentParser(description="FreeAI package builder")
    parser.add_argument("--version", help="Override version (default: read from VERSION)")
    parser.add_argument("--output", "-o", help="Output directory (default: dist/)")
    parser.add_argument("--list", action="store_true", help="List files instead of building")
    args = parser.parse_args()

    if args.list:
        cmd_list(args)
    else:
        cmd_package(args)


if __name__ == "__main__":
    main()
