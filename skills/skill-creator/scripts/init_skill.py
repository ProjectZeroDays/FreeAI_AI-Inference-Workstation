#!/usr/bin/env python3
"""Initialize a new skill directory with scaffold files."""
import argparse
import os
import sys


SKILL_TEMPLATE = """---
name: {name}
description: TODO: Describe what this skill does and when to trigger it.
---

# {title}

TODO: Write skill instructions here.

## Usage

TODO: Add usage examples.

## References

TODO: List any reference files and when to read them.
"""


def init_skill(name: str, path: str = "skills") -> str:
    """Create skill directory scaffold. Returns created path."""
    skill_dir = os.path.join(path, name)
    os.makedirs(os.path.join(skill_dir, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(skill_dir, "references"), exist_ok=True)
    os.makedirs(os.path.join(skill_dir, "assets"), exist_ok=True)

    # Write SKILL.md
    title = " ".join(word.capitalize() for word in name.split("-"))
    skill_md = SKILL_TEMPLATE.format(name=name, title=title)
    skill_path = os.path.join(skill_dir, "SKILL.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(skill_md)

    # Remove empty example dirs if not needed
    for subdir in ["scripts", "references", "assets"]:
        subdir_path = os.path.join(skill_dir, subdir)
        if not os.listdir(subdir_path):
            os.rmdir(subdir_path)

    print(f"Created skill: {skill_dir}")
    print(f"  SKILL.md: {skill_path}")
    return skill_dir


def main():
    parser = argparse.ArgumentParser(description="Initialize a new skill")
    parser.add_argument("name", help="Skill name (kebab-case)")
    parser.add_argument("--path", default="skills", help="Parent directory (default: skills)")
    args = parser.parse_args()

    if not all(c.isalnum() or c == "-" for c in args.name) or args.name.startswith("-"):
        print("Error: Skill name must be kebab-case (letters, numbers, hyphens only)")
        sys.exit(1)

    init_skill(args.name, args.path)


if __name__ == "__main__":
    main()
