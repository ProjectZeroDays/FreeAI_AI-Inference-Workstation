---
name: release-assets
description: Build and publish cross-platform release artifacts for a project — native binaries (Windows x64, Linux x64+arm64, macOS x64+arm64), Android APK/AAB, iOS IPA, .deb/.rpm/.pkg/.dmg/.msi/.AppImage/.zip/.tar.gz packages, install/run scripts (sh/ps1/bat), Docker/k8s/Terraform/Cloud-Run/Lambda deploy manifests, and SHA-256 checksums — then upload to a GitHub Release. Pairs with the `release` skill. Use when the user says "build binaries", "package for release", "cross-compile", "make a .deb/.rpm/.dmg", "ship install scripts", "upload release assets", "package for Android/iOS/Windows/macOS/Linux".
---

# Release assets — build matrix, package, and publish

This skill produces **artifacts** for a release the `release` skill has *already*
cut (the tag exists). It is read-only until the user confirms the target matrix;
after that it runs builds, signs what it can, computes checksums, and uploads to
a GitHub Release.

## 0. Stop conditions (gate before any build)

- The release tag **must** already exist (`git tag --list "v<version>"`).
  If it doesn't: hand off to the `release` skill first.
- The repo's health gate (`repo-maintenance` skill) must be green on the tagged
  commit. Check out the tag (`git checkout v<version>`) before building.
- Build tools for each requested target must be installed. Probe upfront and
  FAIL FAST with the exact install command, rather than half-building then
  dying.
- Never publish while the working tree is dirty: `git status --porcelain` must
  be empty (excluding the build output dir, which is gitignored).

## 1. Discover the project's native build surface

Don't assume. Smell the repo:

| file                          | stack            | build command                        | artifact                                  |
|-------------------------------|------------------|--------------------------------------|-------------------------------------------|
| `package.json` "bin"          | Node CLI         | `pkg`/`@yao-pkg/pkg`/`bun build --compile` | `.exe`/ELF/Mach-O per target            |
| `src/main.rs` + `Cargo.toml`  | Rust             | `cargo build --release --target`     | ELF/Mach-O/PE in `target/<triple>/release/` |
| `cmd/`/`main.go` + `go.mod`   | Go               | `GOOS=… GOARCH=… go build -ldflags`  | single binary                              |
| `*.csproj` w/ `<OutputType>Exe` | .NET           | `dotnet publish -c Release -r <rid> --self-contained` | `publish/` dir                |
| `CMakeLists.txt`              | C/C++            | `cmake --build` per triple (needs a toolchain file for cross) | binary              |
| `Makefile`/`make`             | C/C++            | `make` per target triplet            | binary                                     |
| `pyproject.toml` w/ `[gui]`/`[cli]` | Python      | `pyoxidizer`/`pyinstaller --onefile --target-architecture` | `.exe`/ELF/Mach-O   |
| `build.gradle(.kts)` w/ plugins | Android        | `./gradlew :app:assembleRelease`     | `app-release.aab` + `app-arm64-v8a-release.apk` |
| `*.xcodeproj`/`Package.swift` | iOS/macOS native | `xcodebuild archive -scheme …`       | `.ipa` (needs signing + provisioning)     |
| `Web/` + `Web.csproj`        | .NET MAUI        | `dotnet maui-blazor -t:Publish`      | Android app                                |
| `package.json` "main"         | Web/bundled JS    | `vite build`/`next build`/`webpack` | `dist/` (deploy, not binary)              |

Table rows that don't apply → skip. Don't run `pkg` on a web-only `package.json`.

## 2. The cross-platform matrix (one place to edit)

Define the matrix once. Below is the default; the user may pass `--targets
linux-x64,darwin-arm64` to shrink it.

### Native binaries (single-platform CLI/server)
| OS      | arch   | build command (Rust example)                      | artifact                              | packaging                  |
|---------|--------|---------------------------------------------------|---------------------------------------|----------------------------|
| Windows | x64    | `cargo build --release --target x86_64-pc-windows-msvc` | `agent-toolkit-v<ver>-x86_64-pc-windows-msvc.exe` | `.zip`             |
| Linux   | x64    | `cargo build --release --target x86_64-unknown-linux-gnu` | `agent-toolkit-v<ver>-linux-x64` | `.tar.gz`, `.deb`, `.rpm`, `.AppImage` |
| Linux   | arm64  | `cargo build --release --target aarch64-unknown-linux-gnu` | `…-linux-arm64` | `.tar.gz`, `.deb` (arm64), `.rpm` (arm64) |
| macOS   | x64    | `cargo build --release --target x86_64-apple-darwin` | `agent-toolkit-v<ver>-darwin-x64` | `.tar.gz`                |
| macOS   | arm64  | `cargo build --release --target aarch64-apple-darwin` | `…-darwin-arm64`  | `.tar.gz`, `.pkg` (universal carve via `lipo`) |

For Go: replace `cargo build` with `GOOS=linux GOARCH=arm64 go build -ldflags="-s -w -X main.version=v<ver>"`.
For Node (`pkg`): replace with `npx @yao-pkg/pkg . --targets node20-linux-x64,node20-win-x64,...`.

### Mobile
| target       | build command                                                              | artifact        | signing required              |
|--------------|----------------------------------------------------------------------------|-----------------|-------------------------------|
| Android apk  | `./gradlew :app:assembleRelease`                                          | `app-release.apk`(per-ABI)  | `keytool`/`apksigner`        |
| Android aab  | `./gradlew :app:bundleRelease`                                            | `app-release.aab`| Play upload signing          |
| iOS ipa      | `xcodebuild archive -scheme App -archivePath App.xcarchive … && xcodebuild -exportArchive` | `App.ipa`     | Apple Developer cert/profile |

For mobile, **never** auto-run signing. Print the signing command and have the
user run it; you won't have their keystore password.

### Install/run/deploy scripts (generated, not bespoke)
| purpose                | filename                       | format   | source uses                                    |
|------------------------|--------------------------------|----------|------------------------------------------------|
| bootstrapping (Linux)  | `install.sh`                   | POSIX sh | downloads correct per-OS asset via `uname -sm` |
| bootstrapping (Win)    | `install.ps1`                  | PS5+     | `Invoke-WebRequest` per arch                   |
| bootstrapping (Win legacy) | `install.bat`              | cmd.exe  | falls back where PS unavailable                |
| launch                 | `run.sh`, `run.cmd`            | sh/cmd   | honours `AGENT_TOOLKIT_HOME` env var          |
| Docker image           | `Dockerfile` + `docker-compose.yml` | OCI | multi-stage + ` artifacts/<tri ple> ...` COPY |
| K8s                    | `deploy/k8s.yaml`              | manifest | Deployment + Service + ConfigMap for env      |
| Terraform              | `deploy/terraform/main.tf`     | HCL      | `kubernetes_*`/`aws_*`/`cloudflare_*` blocks  |
| Cloud Run              | `deploy/cloudrun.service.yaml` | Knative  | `gcloud run deploy` ready                     |
| Lambda                 | `deploy/lambda.zip`            | zip      | `lambda.Function` SAM/CDK ready               |
| systemd unit           | `deploy/agent-toolkit.service` | INI      | `systemctl enable --now` ready                |

The install script hashes the asset's expected SHA-256 and refuses to install on
hash mismatch. Generate the script **after** the asset list is final in §4.

### Compressed archives
- Windows assets → `.zip` (deflate).
- macOS/Linux assets → `.tar.gz`.
- Universal macOS binary → `lipo -create x86_64 aarch64 -output universal`
  **before** archiving, then archive.
- Never tar already-tarred content; pick one level.

## 3. Toolchain probe (run before builds, halt early)

```
# Rust: rustup target list --installed
rustup target add aarch64-unknown-linux-gnu x86_64-pc-windows-msvc ... --toolchain stable
# Go: just use the right GOOS/GOARCH — no install needed if Go >=1.21
# Node: npx @yao-pkg/pkg --help (auto-fetches build tools)
# .deb: dpkg-deb --version
# .rpm: rpmbuild --version
# .dmg: hdiutil (macOS only) — Linux uses `genisoimage`
# .AppImage: linuxdeploy + appimagetool
# Android: ANDROID_HOME + ./gradlew --version
# iOS: xcodebuild -version (macOS host only)
```

For each absent tool, print the one-line install command (per OS) and stop.
Don't try three fallback toolchains.

## 4. Build, hash, sign — sequence per target

```
# 1) Build the per-target binary into builds/<triple>/<artifact>
#    - isolate output to `builds/` (gitignored) so the working tree stays clean.
# 2) Strip (Linux/macOS): `strip --strip-debug builds/<triple>/<binary>` to shrink.
# 3) Package per §2 table (.zip / .tar.gz / .deb / .rpm / .pkg / .dmg / .AppImage).
# 4) Compute SHA-256 of every final asset:
#       sha256sum builds/<triple>/*.zip builds/<dist>/*.deb ... > dist/SHA256SUMS.txt
# 5) Sign where configured (GPG/codesign/sigstore). If signing isn't set up,
#    OMIT signing rather than producing an unsigned "signature" file.
# 6) Generate install/run/deploy scripts (templates in ../references/) and add
#    their SHA-256 to SHA256SUMS too.
```

`.deb` build (Linux):
```
mkdir -p dist/agent-toolkit_<ver>_<arch>/{DEBIAN,usr/bin,usr/share/doc/agent-toolkit}
cp builds/<triple>/<binary> dist/agent-toolkit_<ver>_<arch>/usr/bin/agent-toolkit
cat > dist/agent-toolkit_<ver>_<arch>/DEBIAN/control <<EOF
Package: agent-toolkit
Version: <ver>
Architecture: <arch>
Maintainer: <name> <email>
Description: opencode orchestration toolkit
Depends: libc6 (>= 2.31)
EOF
dpkg-deb --build --root-owner-group dist/agent-toolkit_<ver>_<arch>
```

`.rpm` build:
```
rpmbuild -bb agent-toolkit.spec --target <arch> --define "_topdir $PWD/dist/rpm"
  (the spec %install copies the binary to /usr/bin; postinst symlinks.)
```

`.AppImage` (Linux portable):
```
linuxdeploy --appdir AppDir --executable builds/<triple>/<binary> \
  --desktop-file res/agent-toolkit.desktop --icon-file res/icon.png
appimagetool AppDir dist/agent-toolkit-<ver>-<arch>.AppImage
```

`.dmg` (macOS, host must be macOS):
```
hdiutil create -volname agent-toolkit -srcfolder dist/stage -fs HFS+ -format UDZO \
  dist/agent-toolkit-<ver>-darwin.dmg
  # host Linux uses `genisoimage` -> produces an ISO; not a real DMG. Tell the user.
```

`.pkg` (macOS, universal):
```
pkgbuild --root dist/stage --identifier com.example.agent-toolkit \
  --version <ver> dist/agent-toolkit-<ver>.pkg
```

`.msi` (Windows, host ideally Windows or via Wix on Linux via Wine — flaky):
```
candle.exe agent-toolkit.wxs -o dist/agent-toolkit.wixobj
light.exe dist/agent-toolkit.wixobj -o dist/agent-toolkit-<ver>-x64.msi
```

### Android assembly
```
./gradlew :app:assembleRelease           # produces app-arm64-v8a-release.apk etc.
./gradlew :app:bundleRelease             # produces app-release.aab (Play upload)
  # signing config: gradle property `android.injected.signing.*` OR
  # leave unsigned and print "run: apksigner sign --ks <key> <apk>"
```

### iOS archive
```
xcodebuild archive -scheme agent-toolkit -archivePath dist/App.xcarchive \
  -destination "generic/iOS"
xcodebuild -exportArchive -archivePath dist/App.xcarchive \
  -exportOptionsPlist res/ExportOptions.plist -exportPath dist/
  # ExportOptions.plist pins `method`: "app-store" / "development" / "ad-hoc".
  # You don't have the cert/profile — print the steps and stop.
```

## 5. Upload to GitHub Release

Once the matrix is built and SHA256SUMS.txt is generated:

```
gh release create v<ver> dist/* dist/SHA256SUMS.txt \
  --title "v<ver>" \
  --notes-file <path-to-the-changelog-section> \
  --verify-tag
```

Caveats:
- Use the `gh` CLI's `--verify-tag` so the upload fails if the tag doesn't
  exist (defense against uploading assets against the wrong tag).
- 4GB per-file GitHub Release limit — if an artifact exceeds it, surface it and
  suggest Google Drive / S3 + a release-noted link instead of forcing it.
- Don't publish to npm/PyPI/Helm/crates.io inside this skill — those are
  registry-specific publish flows that belong to user-confirmed prompts in
  `release` skill §3 step 6, not here.

## 6. Proposed output to the user

```
RELEASE ASSETS — v<ver>
PROPOSED MATRIX:
  binaries:    windows-x64, linux-x64, linux-arm64, darwin-x64, darwin-arm64
  packages:    .zip (win), .tar.gz (*nix), .deb (linux-{x64,arm64}), .rpm (linux-{x64,arm64}),
               .AppImage (linux-x64), .pkg (darwin-universal), .dmg (darwin-universal)
  mobile:      (none — no Android/iOS build files detected)
  scripts:     install.sh, install.ps1, install.bat, run.sh, run.cmd
  deploy:      Dockerfile, docker-compose.yml, deploy/k8s.yaml, deploy/terraform/main.tf,
               deploy/agent-toolkit.service
  checksums:   dist/SHA256SUMS.txt
  upload-to:   gh release v<ver>

TOOLCHAIN:
  present:  rustc/stable, dpkg-deb, rpmbuild, linuxdeploy, hdiutil (host is macOS)
  missing:  appimagetool (install: `wget .../appimagetool-x86_64.AppImage`)

CONFIRM? reply `build all`, or pick a subset (`build linux-x64,darwin-arm64`),
or `--skip-mobile`. After build: reply `upload` to push to gh release v<ver>.
```

## 7. Hard limits

- Never cross-compile if you cannot verify the toolchain; halt at §3.
- Never sign Android/iOS binaries in this skill — print the steps and stop.
- Never overwrite an existing asset on an existing release without explicit
  user confirmation. (`gh release upload --clobber` exists; refuse to use it
  unprompted.)
- Never publish to registries (npm/PyPI/crates.io/Helm). Those do not belong
  in a GitHub-Release-asset upload.
- Never commit the `builds/` or `dist/` directories; both must be gitignored
  before any build (verify in §0).