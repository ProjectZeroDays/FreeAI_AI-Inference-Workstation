---
description: Build cross-platform release artifacts (binaries, .deb/.rpm/.pkg/.dmg/.msi/.AppImage/.zip/.tar.gz, install/run scripts, Docker/k8s/Terraform manifests, SHA-256 checksums) and upload to a GitHub Release. Requires an existing tag.
agent: maintainer
model: anthropic/claude-sonnet-4-5-20250929
subtask: true
---

Load the `release-assets` skill and prepare a build proposal for the release
named by `$ARGUMENTS`.

`$ARGUMENTS`:
- (empty)              → use the most recent tag (`git describe --tags --abbrev=0`).
- `vX.Y.Z`             → build assets for that tag (must already exist).
- `--targets <list>`   → comma-separated subset of `windows-x64,linux-x64,
                         linux-arm64,darwin-x64,darwin-arm64,android,ios`.
- `--skip-mobile`      → omit Android/iOS targets.
- `--no-upload`        → build only; do NOT run §5 (GitHub Release upload).

Always run §0 (gate: tag exists, working tree clean, health green) and §3
(toolchain probe) before proposing. Print the §6 PROPOSED MATRIX block and
**WAIT** for the user to reply `build all` / `build <subset>` before any build,
and a separate `upload` confirmation before §5. Never sign Android/iOS assets
in-session — print the steps and stop. Never publish to npm/PyPI/crates.io.