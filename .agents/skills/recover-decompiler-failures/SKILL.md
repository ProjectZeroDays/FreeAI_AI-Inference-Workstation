---
name: recover-decompiler-failures
description: Use when Ghidra, decompile_failures.tsv, failed decompilation, packed stubs, bad function boundaries, unwind fragments, overlapping varnodes, or native binary reverse engineering needs fallback recovery with radare2/r2dec/assembly classification.
---

# Recover Decompiler Failures

## Core Rule

Treat a decompiler failure as a triage problem, not as proof the code is unrecoverable. First recover what another tool can emit; then classify the rest as packed/loader stub, unwind/bad-code fragment, bad boundary, or manual assembly.

## Workflow

1. Confirm the failing targets:
   - For Ghidra exports, scan `decompile_failures.tsv` and `summary.txt`.
   - Check duplicate library hashes before rerunning identical failures.
2. Run the bundled script:
   ```bash
   python3 /root/.codex/skills/recover-decompiler-failures/scripts/recover_decompiler_failures.py \
     <ghidra-decompiled-root> \
     --out <output-dir> \
     --install-r2dec
   ```
3. Read `<output-dir>/recovery-report.tsv` and `<output-dir>/recovery-report.md`.
4. Use recovered `*.r2dec.c` when classification is `recovered-pseudocode`.
5. Use `*.radare2-pdc.txt` only as low-confidence pseudo-code unless the control flow is coherent.
6. For `packed-or-loader-stub` and `unwind-or-bad-code-fragment`, keep assembly as source of truth unless the user asks for manual unpacking or boundary cleanup.

## Tool Choices

- Prefer Ghidra output when it exists.
- Use `r2dec` (`pdd`) for overlapping varnodes, bad Ghidra simplification, and ordinary function-boundary issues.
- Use radare2 `pdc` as a fallback when `r2dec` cannot emit C.
- Use assembly for packed startup/decompression stubs, invalid-instruction-heavy fragments, and exception unwind fragments.
- Do not waste time repeatedly decompiling byte-identical DLLs. Reuse results and record the reuse.

## Scripts

- `scripts/recover_decompiler_failures.py`: scans Ghidra export folders or a single failure set, runs radare2/r2dec fallbacks, copies relevant assembly, dedupes identical binaries, and writes reports. Run `--help` for flags.

## Common Failure Meaning

- `Exception while decompiling ... timeout` on entry stubs with `PUSHAD`, `POPAD`, `MOVS*.REP`, jumps to empty/uninitialized regions: likely packed/loader/decompression stub.
- `Unwind@...`, invalid opcodes, privileged I/O instructions, or nonsensical dense control flow: likely unwind table or data misidentified as code.
- `Overlapping input varnodes` or `Cannot properly adjust input varnodes` on otherwise coherent functions: try `r2dec`; this is the best alternative-decompiler case.
- Zero functions discovered in a PE DLL is not a failure by itself; preserve metadata/import/export/string indexes.
