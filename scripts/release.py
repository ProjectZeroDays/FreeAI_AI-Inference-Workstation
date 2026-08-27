#!/usr/bin/env python3
"""Release automation for FreeAI Unified AI Stack.

Reads current version from VERSION, bumps it, generates changelog from git,
creates annotated tag, builds release artifacts via package.py, and publishes
a GitHub release with changelog.

Usage:
    python scripts/release.py bump --type patch       # 1.2.0 -> 1.2.1
    python scripts/release.py bump --type minor       # 1.2.0 -> 1.3.0
    python scripts/release.py bump --type major       # 1.2.0 -> 2.0.0
    python scripts/release.py run                     # full pipeline (bump+tag+release)
    python scripts/release.py tag                     # tag only (VERSION must match changelog)
    python scripts/release.py status                  # show current version and pending tag
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "config" / "VERSION"
CHANGELOG = ROOT / "CHANGELOG.md"
SCRIPTS_DIR = ROOT / "scripts"


def run(cmd, check=True, **kwargs):
    r = subprocess.run(cmd, shell=True, check=check, text=True, capture_output=True, **kwargs)
    return r.stdout.strip()


def get_current_version():
    v = VERSION_FILE.read_text().strip()
    m = re.match(r"^\d+\.\d+\.\d+$", v)
    if not m:
        print(f"ERROR: VERSION file contains invalid semver: {v!r}", file=sys.stderr)
        sys.exit(1)
    return v


def parse_version(v):
    return tuple(int(x) for x in v.split("."))


def format_version(t):
    return ".".join(str(x) for x in t)


def bump_version(current, bump_type):
    t = parse_version(current)
    if bump_type == "major":
        new = (t[0] + 1, 0, 0)
    elif bump_type == "minor":
        new = (t[0], t[1] + 1, 0)
    elif bump_type == "patch":
        new = (t[0], t[1], t[2] + 1)
    else:
        print(f"ERROR: unknown bump type {bump_type!r}", file=sys.stderr)
        sys.exit(1)
    return format_version(new)


def get_unreleased_commits():
    current = get_current_version()
    tag = f"v{current}"
    try:
        run(f"git rev-parse {tag}", check=False)
        range_spec = f"{tag}..HEAD"
    except subprocess.CalledProcessError:
        range_spec = "HEAD"
    try:
        return run(f"git log --oneline {range_spec}")
    except subprocess.CalledProcessError:
        return ""


def generate_changelog_entry(new_version):
    commits = get_unreleased_commits()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = f"\n\n## {new_version} - {today}\n"
    if commits:
        header += "\n### Commits\n"
        for line in commits.splitlines()[:50]:
            header += f"- {line}\n"
    else:
        header += "\n(no unreleased commits)\n"
    return header


def update_changelog(new_version):
    entry = generate_changelog_entry(new_version)
    if CHANGELOG.exists():
        content = CHANGELOG.read_text()
        # Insert after the first heading (## X.Y.Z) if it exists, otherwise prepend
        match = re.search(r"^## \d+\.\d+\.\d+", content, re.MULTILINE)
        if match:
            content = content[: match.end()] + entry + content[match.end() :]
        else:
            content = entry + "\n" + content
    else:
        content = f"# Changelog\n{entry}"
    CHANGELOG.write_text(content)
    print(f"Updated {CHANGELOG}")


def create_tag(version):
    tag = f"v{version}"
    try:
        run(f"git rev-parse refs/tags/{tag}", check=False)
        print(f"Tag {tag} already exists — skipping")
        return tag
    except subprocess.CalledProcessError:
        pass
    run(f'git tag -a "{tag}" -m "Release {tag}"')
    print(f"Created tag {tag}")
    return tag


def push_tag(tag):
    run(f"git push origin {tag}")
    print(f"Pushed tag {tag}")


def get_git_user():
    try:
        name = run("git config user.name") or "freeai-release-bot"
        email = run("git config user.email") or "actions@users.noreply.github.com"
    except subprocess.CalledProcessError:
        name, email = "freeai-release-bot", "actions@users.noreply.github.com"
    return name, email


def save_release_state(version, tag, artifacts_dir):
    state = ROOT / ".runs" / "release-state.json"
    state.parent.mkdir(exist_ok=True)
    import json
    state.write_text(json.dumps({
        "version": version,
        "tag": tag,
        "artifacts_dir": str(artifacts_dir),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2))
    print(f"Wrote release state to {state}")


def cmd_bump(args):
    current = get_current_version()
    new = bump_version(current, args.type)
    VERSION_FILE.write_text(new + "\n")
    print(f"Bumped {current} -> {new}")
    update_changelog(new)


def cmd_tag(args):
    version = get_current_version()
    tag = create_tag(version)
    if not args.no_push:
        push_tag(tag)
    return version, tag


def cmd_run(args):
    name, email = get_git_user()
    subprocess.run(
        f'git config user.name "{name}" && git config user.email "{email}"',
        shell=True,
    )

    version = get_current_version()
    if args.bump:
        version = bump_version(version, args.bump)
        VERSION_FILE.write_text(version + "\n")
        print(f"Bumped {get_current_version()} -> {version}")
        update_changelog(version)

    tag = create_tag(version)

    artifacts_dir = ROOT / "dist"
    artifacts_dir.mkdir(exist_ok=True)

    pkg_result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "package.py"), "--output", str(artifacts_dir)],
        capture_output=True,
        text=True,
    )
    if pkg_result.returncode != 0:
        print(f"package.py failed:\n{pkg_result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(pkg_result.stdout)

    # Generate checksums for all artifacts
    checksums = []
    for f in sorted(artifacts_dir.glob("*")):
        if f.is_file():
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            checksums.append(f"{h}  {f.name}")
            print(f"  {h}  {f.name}")
    (artifacts_dir / "sha256sums.txt").write_text("\n".join(checksums) + "\n")

    save_release_state(version, tag, artifacts_dir)
    print(f"\nRelease {version} ready in {artifacts_dir}")
    print(f"Next: git push origin {tag}  (or run with --push)")
    if args.push:
        push_tag(tag)


def cmd_status(args):
    version = get_current_version()
    tag = f"v{version}"
    try:
        run(f"git rev-parse refs/tags/{tag}", check=False)
        tag_status = "tagged"
    except subprocess.CalledProcessError:
        tag_status = "not tagged"
    commits = get_unreleased_commits()
    print(f"Version: {version}")
    print(f"Tag:     {tag} ({tag_status})")
    print(f"Commits: {len(commits.splitlines()) if commits else 0} unreleased")
    if commits:
        for line in commits.splitlines()[:10]:
            print(f"  {line}")


def main():
    parser = argparse.ArgumentParser(description="FreeAI release automation")
    sub = parser.add_subparsers(dest="command", required=True)

    p_bump = sub.add_parser("bump", help="Bump version and update changelog")
    p_bump.add_argument("--type", required=True, choices=["major", "minor", "patch"])

    p_tag = sub.add_parser("tag", help="Create and push git tag for current VERSION")
    p_tag.add_argument("--no-push", action="store_true", help="Skip git push")

    p_run = sub.add_parser("run", help="Full release: bump (optional) + tag + build + checksum")
    p_run.add_argument("--bump", choices=["major", "minor", "patch"], help="Bump before releasing")
    p_run.add_argument("--push", action="store_true", help="Push tag to origin")

    p_status = sub.add_parser("status", help="Show current version and tag status")

    args = parser.parse_args()
    {"bump": cmd_bump, "tag": cmd_tag, "run": cmd_run, "status": cmd_status}[args.command](args)


if __name__ == "__main__":
    main()
