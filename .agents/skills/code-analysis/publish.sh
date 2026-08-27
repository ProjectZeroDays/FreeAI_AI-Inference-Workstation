#!/usr/bin/env bash
# Publish this skill to ClawHub.
#
# Slug:    wscats/code-analysis-skills
# Version: 1.1.1   (NOTE: pure semver, no leading `v` — ClawHub UI adds the `v` itself)
#
# Usage:
#   ./publish.sh                # publish using defaults below
#   VERSION=1.1.2 ./publish.sh  # override version (no leading `v`)
#
# Prerequisites:
#   - `clawhub` CLI installed and logged in (`clawhub login`).
#   - Run from the repository root (the directory containing skill.yaml).

set -euo pipefail

# ─── Config (override via environment variables if needed) ──────────────────
# NOTE: clawhub slugs must be a single segment (lowercase letters, digits, and
# single hyphens only). The owner handle (e.g. `wscats/`) is taken from your
# logged-in account, not the slug.
SLUG="${SLUG:-code-analysis-skills}"
OWNER="${OWNER:-wscats}"
VERSION="${VERSION:-1.1.1}"
NAME="${NAME:-Code Analysis Skills}"
TAGS="${TAGS:-latest,git,code-analysis,reflection}"
CHANGELOG="${CHANGELOG:-Republish of v1.1.0 with a corrected pure-semver version string. ClawHub UI was rendering vv1.1.0 because the previous publish included a leading v. No code changes vs v1.1.0.}"

# ─── Resolve script directory (the skill folder) ────────────────────────────
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_PATH="${SKILL_PATH:-${SCRIPT_DIR}}"

# ─── Sanity checks ──────────────────────────────────────────────────────────
if ! command -v clawhub >/dev/null 2>&1; then
  echo "❌ 'clawhub' CLI not found in PATH. Install it first:" >&2
  echo "   npm install -g @clawhub/cli   (or follow the official docs)" >&2
  exit 1
fi

if [[ ! -f "${SKILL_PATH}/skill.yaml" ]]; then
  echo "❌ skill.yaml not found at: ${SKILL_PATH}" >&2
  echo "   Run this script from the repository root, or set SKILL_PATH=..." >&2
  exit 1
fi

# ─── Show plan and confirm session ──────────────────────────────────────────
echo "──────────────────────────────────────────────────────────────"
echo " ClawHub publish"
echo "──────────────────────────────────────────────────────────────"
echo "  Owner     : ${OWNER}"
echo "  Slug      : ${SLUG}"
echo "  Version   : ${VERSION}"
echo "  Name      : ${NAME}"
echo "  Tags      : ${TAGS}"
echo "  Path      : ${SKILL_PATH}"
echo "  Changelog : ${CHANGELOG}"
echo "──────────────────────────────────────────────────────────────"

# Verify the user is logged in (non-fatal: clawhub publish will also check).
if ! clawhub whoami >/dev/null 2>&1; then
  echo "⚠️  You don't appear to be logged in. Running 'clawhub login' first..."
  clawhub login
fi

# ─── Publish ────────────────────────────────────────────────────────────────
clawhub publish "${SKILL_PATH}" \
  --slug "${SLUG}" \
  --name "${NAME}" \
  --version "${VERSION}" \
  --tags "${TAGS}" \
  --changelog "${CHANGELOG}"

echo "✅ Published ${SLUG}@${VERSION}"
echo "   View: https://clawhub.ai/${OWNER}/${SLUG}"
