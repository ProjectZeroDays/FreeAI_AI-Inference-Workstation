#!/usr/bin/env python3
"""Merge provider configs from mimocode/ clients into config/providers-merged.json.

Reads per-client providers JSON files from mimocode/ and merges them into a
single canonical registry. Last-write-wins per-provider; source list is tracked
so the dashboard can show provenance.

Usage:
    python scripts/sync_providers.py           # merge and write
    python scripts/sync_providers.py --dry-run  # print diff only
    python scripts/sync_providers.py --sources  # list detected sources
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIMOCODE_DIR = ROOT / "mimocode"
CONFIG_DIR = ROOT / "config"
OUTPUT_PATH = CONFIG_DIR / "providers-merged.json"

# Ordered list of provider sources to scan (first = highest priority for conflicts)
SOURCE_PATTERNS = [
    "mimocode-providers.json",
    "opencode-providers.json",
    "openclaw-providers.json",
    "jcode-providers.json",
    "hermes-providers.json",
    "mimocode-desktop-providers.json",
    "opencode-desktop-providers.json",
    "openclaw-desktop-providers.json",
    "jcode-terminal-providers.json",
    "hermes-desktop-providers.json",
]


def find_source_files() -> list[Path]:
    """Return list of mimocode/ JSON files that look like provider registries."""
    found = []
    if not MIMOCODE_DIR.exists():
        return found
    for pattern in SOURCE_PATTERNS:
        p = MIMOCODE_DIR / pattern
        if p.exists():
            found.append(p)
    # Also pick up any other *-providers.json files we might have missed
    for p in sorted(MIMOCODE_DIR.glob("*-providers.json")):
        if p not in found:
            found.append(p)
    return found


def load_providers(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  SKIP {path.name}: {exc}", file=sys.stderr)
        return {}
    return data.get("providers", {})


def normalise_provider(raw: dict) -> dict:
    """Normalise a provider entry to a common schema."""
    out = {
        "type": raw.get("type", "primary"),
        "base_url": raw.get("base_url", raw.get("baseUrl", "")),
        "models": raw.get("models", []),
        "auth": raw.get("auth", "env:" + raw.get("api_key_env", raw.get("key_env", "UNKNOWN"))),
        "enabled": raw.get("enabled", True),
    }
    # Handle legacy "name" field
    if "name" in raw and not out["base_url"]:
        out["display_name"] = raw["name"]
    if raw.get("fallback"):
        out["fallback"] = True
    return out


def merge_providers(sources: list[tuple[str, dict]]) -> dict:
    merged = {}
    for source_name, providers in sources:
        for pname, pdata in providers.items():
            if pname not in merged:
                merged[pname] = {"_sources": [source_name]}
            else:
                merged[pname]["_sources"].append(source_name)
            # Deep-merge: new data wins on scalar fields, models list is unionised
            norm = normalise_provider(pdata if isinstance(pdata, dict) else {})
            for k, v in norm.items():
                if k == "models":
                    existing = set(merged[pname].get("models", []))
                    existing.update(v)
                    merged[pname]["models"] = sorted(existing)
                else:
                    merged[pname][k] = v
    # Strip internal _sources key from final output
    for pname in merged:
        merged[pname].pop("_sources", None)
    return merged


def main():
    parser = argparse.ArgumentParser(description="Sync providers from mimocode/ into merged registry")
    parser.add_argument("--dry-run", action="store_true", help="Print diff without writing")
    parser.add_argument("--sources", action="store_true", help="List detected source files")
    args = parser.parse_args()

    source_files = find_source_files()
    if args.sources:
        for p in source_files:
            providers = load_providers(p)
            print(f"{p.name}: {len(providers)} providers")
        return

    if not source_files:
        print("No mimocode provider sources found.", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {len(source_files)} source file(s)...")
    sources = []
    for p in source_files:
        providers = load_providers(p)
        if providers:
            sources.append((p.name, providers))
            print(f"  {p.name}: {len(providers)} providers")

    merged = merge_providers(sources)
    print(f"Merged registry: {len(merged)} unique providers")

    # Show new/conflicting providers
    existing = {}
    if OUTPUT_PATH.exists():
        try:
            existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")).get("providers", {})
        except (json.JSONDecodeError, OSError):
            pass

    new_names = set(merged) - set(existing)
    changed_names = {n for n in set(merged) & set(existing)
                     if merged[n].get("base_url") != existing[n].get("base_url")
                     or set(merged[n].get("models", [])) != set(existing[n].get("models", []))}

    if new_names:
        print(f"  New providers: {', '.join(sorted(new_names)[:20])}"
              + ("" if len(new_names) <= 20 else f"  (+{len(new_names)-20} more)"))
    if changed_names:
        print(f"  Updated providers: {', '.join(sorted(changed_names)[:20])}"
              + ("" if len(changed_names) <= 20 else f"  (+{len(changed_names)-20} more)"))

    if args.dry_run:
        print("\n[dry-run] Would write to:", OUTPUT_PATH)
        return

    payload = {
        "_comment": "Auto-merged provider registry from mimocode/ sources. Do not edit by hand.",
        "merged_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sources": [s[0] for s in sources],
        "providers": merged,
    }
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}  ({len(merged)} providers)")


if __name__ == "__main__":
    main()
