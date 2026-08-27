# Failure Patterns

Use this reference only when deciding whether a failed function deserves more decompiler attempts.

## Good Candidate For r2dec

- Ghidra found a real function and assembly is coherent.
- Failure says `Overlapping input varnodes`, `Cannot properly adjust input varnodes`, or another simplification/dataflow problem.
- Function contains normal calls, branches, stack setup, or recognizable math/FPU helper logic.

## Bad Candidate For More High-Level Decompilers

- Entry or startup stub jumps into uninitialized/generated memory.
- Assembly includes `PUSHAD`, `POPAD`, `MOVSD.REP`, `MOVSB.REP`, self-copying, unpacking loops, or XOR-copy loops.
- Failure is in `Unwind@...` or exception handler data.
- Disassembly is dominated by invalid instructions, I/O port instructions, impossible far jumps, `iretd`, or dense nonsense control flow.

## Next Steps After Classification

- `recovered-pseudocode`: integrate the generated `*.r2dec.c` as the missing C-like representation.
- `pseudo-only-low-confidence`: preserve `pdc` output but do not treat it as accurate source.
- `packed-or-loader-stub`: unpack or emulate if the stub matters; otherwise document it as loader code.
- `unwind-or-bad-code-fragment`: correct function boundaries or mark as data/unwind metadata.
- `manual-assembly-required`: use the copied Ghidra assembly and inspect manually.
