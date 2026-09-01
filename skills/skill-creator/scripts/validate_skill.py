#!/usr/bin/env python3
"""Validate a skill directory for correct structure and content."""
import argparse
import os
import re
import sys


def validate_skill(skill_path: str) -> list[str]:
    """Validate skill directory. Returns list of errors (empty = valid)."""
    errors = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(skill_md):
        errors.append("Missing SKILL.md")
        return errors

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Check frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        errors.append("Missing YAML frontmatter (must start with ---)")
        return errors

    fm = fm_match.group(1)
    if "name:" not in fm:
        errors.append("Frontmatter missing 'name' field")
    if "description:" not in fm:
        errors.append("Frontmatter missing 'description' field")

    # Check body exists (content after frontmatter)
    body = content[fm_match.end():].strip()
    if len(body) < 50:
        errors.append("SKILL.md body too short (< 50 chars)")

    # Check line count
    line_count = len(content.splitlines())
    if line_count > 500:
        errors.append(f"SKILL.md too long ({line_count} lines, max 500)")

    # Check no forbidden files
    forbidden = ["README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md"]
    for fname in forbidden:
        fpath = os.path.join(skill_path, fname)
        if os.path.isfile(fpath):
            errors.append(f"Found forbidden file: {fname}")

    # Check directory structure
    valid_dirs = {"scripts", "references", "assets", ".git", ".gitignore"}
    for item in os.listdir(skill_path):
        item_path = os.path.join(skill_path, item)
        if os.path.isdir(item_path) and item not in valid_dirs:
            errors.append(f"Unexpected directory: {item}/")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate a skill")
    parser.add_argument("path", help="Path to skill directory")
    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: {args.path} is not a directory")
        sys.exit(1)

    errors = validate_skill(args.path)
    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"Valid: {args.path}")
        sys.exit(0)


if __name__ == "__main__":
    main()
