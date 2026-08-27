#!/usr/bin/env python3
"""Recover Ghidra decompiler failures with radare2/r2dec fallbacks."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


BAD_R2DEC_MARKERS = (
    "Error: no data available",
    "Missing plugin",
    "Cannot find function",
    "Please analyze the function/binary first",
)


@dataclass
class Failure:
    target_dir: Path
    failure_file: Path
    binary: Path
    entry: str
    name: str
    status: str
    error: str
    program: str
    asm_file: Path | None
    sha256: str


def run(cmd: list[str], timeout: int) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return proc.returncode, proc.stdout
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", "replace")
        return 124, output + f"\n[TIMEOUT after {timeout}s]\n"


def safe_name(raw: str, max_len: int = 96) -> str:
    raw = raw or "unnamed"
    safe = re.sub(r"[^A-Za-z0-9_.@-]+", "_", raw).strip("_")
    return (safe or "unnamed")[:max_len]


def norm_addr(raw: str) -> str:
    """Normalize and validate a hexadecimal address string.
    
    Args:
        raw: Input string that should represent a hexadecimal address
        
    Returns:
        Normalized address string with '0x' prefix
        
    Raises:
        ValueError: If the input is not a valid hexadecimal address
    """
    raw = raw.strip()
    # Remove 0x prefix if present for validation
    if raw.lower().startswith("0x"):
        hex_part = raw[2:]
    else:
        hex_part = raw
    
    # Validate that the remaining part contains only hexadecimal characters
    # This prevents command injection via radare2's semicolon command separator
    # and shell escape sequences (e.g., "0;!touch /tmp/marker")
    if not hex_part:
        raise ValueError(f"Empty hexadecimal address: {raw!r}")
    
    if not re.match(r'^[0-9a-fA-F]+$', hex_part):
        raise ValueError(f"Invalid hexadecimal address (contains non-hex characters): {raw!r}")
    
    return "0x" + hex_part.lower()


def parse_int_addr(raw: str) -> int | None:
    try:
        return int(norm_addr(raw), 16)
    except ValueError:
        return None


def parse_summary(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(errors="replace").splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            data[key.strip()] = value.strip()
    return data


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_asm(target_dir: Path, entry: str) -> Path | None:
    asm_dir = target_dir / "assembly"
    if not asm_dir.is_dir():
        return None
    needle = entry.lower().replace("0x", "")
    matches = sorted(asm_dir.glob(f"*{needle}*.asm"))
    return matches[0] if matches else None


def scan_failures(root: Path, limit: int | None = None) -> list[Failure]:
    failures: list[Failure] = []
    for failure_file in sorted(root.rglob("decompile_failures.tsv")):
        target_dir = failure_file.parent
        summary = parse_summary(target_dir / "summary.txt")
        binary_text = summary.get("Executable path", "")
        if not binary_text:
            continue
        binary = Path(binary_text)
        if not binary.exists():
            continue
        program = summary.get("Program", binary.name)
        with failure_file.open(newline="", errors="replace") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            for row in reader:
                entry = (row.get("entry") or "").strip()
                if not entry:
                    continue
                
                # Validate that entry is a valid hexadecimal address
                # This prevents command injection attacks via malicious TSV entries
                try:
                    norm_addr(entry)
                except ValueError as e:
                    print(f"warning: skipping invalid entry in {failure_file}: {e}", file=sys.stderr)
                    continue
                
                failures.append(
                    Failure(
                        target_dir=target_dir,
                        failure_file=failure_file,
                        binary=binary,
                        entry=entry,
                        name=(row.get("name") or "").strip(),
                        status=(row.get("status") or "").strip(),
                        error=(row.get("error") or "").strip(),
                        program=program,
                        asm_file=find_asm(target_dir, entry),
                        sha256=sha256(binary),
                    )
                )
                if limit and len(failures) >= limit:
                    return failures
    return failures


def has_r2dec() -> bool:
    if not shutil.which("r2"):
        return False
    rc, out = run(["r2", "-q", "-c", "pdd?", "-c", "q", "/bin/true"], 15)
    return rc == 0 and "Missing plugin" not in out


def install_r2dec() -> None:
    if not shutil.which("r2pm"):
        raise SystemExit("r2pm is not installed; cannot install r2dec automatically")
    for cmd in (["r2pm", "-U"], ["r2pm", "-ci", "r2dec"]):
        rc, out = run(cmd, 600)
        sys.stdout.write(out)
        if rc != 0:
            raise SystemExit(f"command failed: {' '.join(cmd)}")


def write_limited(path: Path, text: str, max_bytes: int) -> bool:
    encoded = text.encode("utf-8", "replace")
    truncated = len(encoded) > max_bytes
    if truncated:
        encoded = encoded[:max_bytes] + b"\n[TRUNCATED]\n"
    path.write_bytes(encoded)
    return truncated


def useful_output(text: str, min_bytes: int = 80) -> bool:
    stripped = text.strip()
    if len(stripped.encode("utf-8", "replace")) < min_bytes:
        return False
    return not any(marker in stripped for marker in BAD_R2DEC_MARKERS)


def radare_cmd(binary: Path, entry: str, command: str) -> list[str]:
    return [
        "r2",
        "-2",
        "-A",
        "-q",
        "-e",
        "scr.color=false",
        "-e",
        "bin.relocs.apply=true",
        "-c",
        f"s {norm_addr(entry)}",
        "-c",
        "af",
        "-c",
        command,
        "-c",
        "q",
        str(binary),
    ]


def classify(failure: Failure, r2dec_ok: bool, pdc_ok: bool, asm_text: str, pdc_text: str) -> str:
    combined = "\n".join([failure.name, failure.status, failure.error, asm_text[:4000], pdc_text[:4000]]).lower()
    packed_stub = (
        "pushad" in combined
        or "popad" in combined
        or "movsd.rep" in combined
        or "movsb.rep" in combined
        or "uninitialized memory" in combined
        or "generated" in combined
    )
    bad_fragment = failure.name.lower().startswith("unwind@") or "invalid" in combined or "iretd" in combined
    if packed_stub:
        return "packed-or-loader-stub"
    if bad_fragment:
        return "unwind-or-bad-code-fragment"
    if r2dec_ok:
        return "recovered-pseudocode"
    if pdc_ok:
        return "pseudo-only-low-confidence"
    return "manual-assembly-required"


def recover_failure(
    failure: Failure,
    out_root: Path,
    timeout: int,
    pdc_timeout: int,
    include_pdc: str,
    max_output_bytes: int,
) -> dict[str, str]:
    rel = failure.target_dir.name
    parent = failure.target_dir.parent.name
    target_slug = safe_name(f"{parent}_{rel}")
    addr_slug = safe_name(norm_addr(failure.entry).replace("0x", "0x"))
    name_slug = safe_name(failure.name)
    out_dir = out_root / target_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    base = f"{addr_slug}_{name_slug}"
    r2dec_path = out_dir / f"{base}.r2dec.c"
    pdc_path = out_dir / f"{base}.radare2-pdc.txt"
    asm_copy = out_dir / f"{base}.ghidra.asm"

    asm_text = ""
    if failure.asm_file and failure.asm_file.exists():
        asm_text = failure.asm_file.read_text(errors="replace")
        asm_copy.write_text(asm_text, encoding="utf-8")

    rc, r2dec_text = run(radare_cmd(failure.binary, failure.entry, "pdd"), timeout)
    r2dec_truncated = write_limited(r2dec_path, r2dec_text, max_output_bytes)
    r2dec_ok = rc == 0 and useful_output(r2dec_text)

    pdc_text = ""
    pdc_ok = False
    pdc_truncated = False
    if include_pdc == "always" or (include_pdc == "auto" and not r2dec_ok):
        pdc_rc, pdc_text = run(radare_cmd(failure.binary, failure.entry, "pdf;pdc"), pdc_timeout)
        pdc_truncated = write_limited(pdc_path, pdc_text, max_output_bytes)
        pdc_ok = pdc_rc == 0 and useful_output(pdc_text)

    classification = classify(failure, r2dec_ok, pdc_ok, asm_text, pdc_text)
    notes: list[str] = []
    if r2dec_truncated or pdc_truncated:
        notes.append("output-truncated")
    if r2dec_ok and classification in {"packed-or-loader-stub", "unwind-or-bad-code-fragment"}:
        notes.append("r2dec-emitted-low-confidence")
    if not r2dec_ok and pdc_ok:
        notes.append("pdc-only")
    if not r2dec_ok and not pdc_ok:
        notes.append("no-high-level-output")

    return {
        "target": str(failure.target_dir),
        "program": failure.program,
        "binary": str(failure.binary),
        "sha256": failure.sha256,
        "entry": norm_addr(failure.entry),
        "name": failure.name,
        "ghidra_status": failure.status,
        "classification": classification,
        "r2dec": str(r2dec_path),
        "radare2_pdc": str(pdc_path) if pdc_path.exists() else "",
        "ghidra_asm": str(asm_copy) if asm_copy.exists() else "",
        "notes": ",".join(notes),
    }


def write_reports(out_root: Path, rows: list[dict[str, str]]) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    fields = [
        "target",
        "program",
        "binary",
        "sha256",
        "entry",
        "name",
        "ghidra_status",
        "classification",
        "r2dec",
        "radare2_pdc",
        "ghidra_asm",
        "notes",
    ]
    report_tsv = out_root / "recovery-report.tsv"
    with report_tsv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1

    lines = ["# Decompiler Failure Recovery", "", "## Counts", ""]
    for key in sorted(counts):
        lines.append(f"- {key}: {counts[key]}")
    lines.extend(["", "## Report", "", f"- TSV: `{report_tsv}`", ""])
    lines.append("## Recovered Pseudocode")
    lines.append("")
    for row in rows:
        if row["classification"] == "recovered-pseudocode":
            lines.append(f"- `{row['program']}` `{row['entry']}` `{row['name']}` -> `{row['r2dec']}`")
    lines.append("")
    lines.append("## Manual/Assembly Cases")
    lines.append("")
    for row in rows:
        if row["classification"] != "recovered-pseudocode":
            lines.append(f"- `{row['program']}` `{row['entry']}` `{row['name']}`: {row['classification']} ({row['notes']})")
    (out_root / "recovery-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decompiled_root", type=Path, help="Root containing Ghidra export folders")
    parser.add_argument("--out", type=Path, default=None, help="Output directory")
    parser.add_argument("--install-r2dec", action="store_true", help="Install r2dec with r2pm if missing")
    parser.add_argument("--timeout", type=int, default=45, help="Seconds for each r2dec pdd run")
    parser.add_argument("--pdc-timeout", type=int, default=20, help="Seconds for each radare2 pdc run")
    parser.add_argument("--include-pdc", choices=("auto", "always", "never"), default="auto")
    parser.add_argument("--max-output-bytes", type=int, default=1_000_000)
    parser.add_argument("--limit", type=int, default=None, help="Limit number of failure rows")
    parser.add_argument("--no-dedupe", action="store_true", help="Do not dedupe identical binary/address/name failures")
    args = parser.parse_args(argv)

    if not shutil.which("r2"):
        raise SystemExit("radare2/r2 is required but was not found in PATH")
    if not has_r2dec():
        if args.install_r2dec:
            install_r2dec()
        else:
            print("warning: r2dec is missing; pdd outputs may be empty. Re-run with --install-r2dec.", file=sys.stderr)

    root = args.decompiled_root.resolve()
    out_root = (args.out or (root.parent / "recovered-decompiler-failures")).resolve()
    failures = scan_failures(root, args.limit)
    rows: list[dict[str, str]] = []
    seen: dict[tuple[str, str, str], dict[str, str]] = {}

    for failure in failures:
        key = (failure.sha256, norm_addr(failure.entry), failure.name)
        if not args.no_dedupe and key in seen:
            row = dict(seen[key])
            row["target"] = str(failure.target_dir)
            row["binary"] = str(failure.binary)
            row["notes"] = ",".join(filter(None, [row.get("notes", ""), "dedupe-reused"]))
            rows.append(row)
            continue
        row = recover_failure(
            failure,
            out_root,
            args.timeout,
            args.pdc_timeout,
            args.include_pdc,
            args.max_output_bytes,
        )
        seen[key] = row
        rows.append(row)

    write_reports(out_root, rows)
    print(f"failures scanned: {len(failures)}")
    print(f"rows written: {len(rows)}")
    print(f"output: {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
