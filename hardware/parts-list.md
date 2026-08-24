# Center AI Workstation v1 — Verified Parts List

Every part number below was verified against current retail listings
(Amazon ASIN shown where confirmed; MicroCenter stocks most items
in-store — search the MPN at microcenter.com or the aisle system).

Prices are typical bands as of writing and float constantly — treat
them as budget estimates, not quotes.

| Category | Part | MPN / SKU | Store ref | Est. USD |
|---|---|---|---|---|
| CPU | AMD Ryzen 9 7900 (12c/24t, boxed w/ Wraith) | `100-100000904` | Amazon/MC search MPN | $280–330 |
| Cooler | Noctua NH-D15S (AM5 SecuFirm2 included) | `NH-D15S` | Amazon/MC | $100–110 |
| Motherboard | ASUS TUF Gaming B650-PLUS WIFI | `TUF GAMING B650-PLUS WIFI` | Amazon/MC | $190–220 |
| GPU | GIGABYTE RTX 4070 Ti SUPER Gaming OC 16G | `GV-N407TSGAMING OC-16GD` | Amazon ASIN `B0CSJVCD3Y` | $800–900 |
| RAM | G.Skill Flare X5 64GB (2×32) DDR5-6000 **CL30** EXPO | `F5-6000J3040G32GX2-FX5` | Amazon/MC | $200–230 |
| OS SSD | Samsung 990 EVO 1TB Gen4 NVMe | `MZ-V9E1T0B/AM` (alt: 990 EVO Plus `MZ-V9S1T0B/AM`) | Amazon/MC | $70–95 |
| Models SSD | WD Black SN850X 2TB Gen4 NVMe | `WDS200T2X0E` | Amazon ASIN `B0B7CMZ3QH` | $140–170 |
| PSU | Corsair RM850x 850W 80+ Gold (modular) | `CP-9020200-NA` | Amazon/MC | $130–150 |
| Case | Fractal Design North (charcoal/walnut) | `FD-C-NOR1C-01` | Amazon/MC | $130–140 |
| Case alt | Fractal Meshify 2 Compact (more airflow) | `FD-MES2C-001` | Amazon/MC | $90–110 |
| Fans | Noctua NF-A14 PWM ×2 (front intake) | `NF-A14 PWM` | Amazon/MC | $23 ea |
| Paste | Noctua NT-H2 (incl. cleaner) | `NT-H2-3.5G` | Amazon/MC | $11 |

**Budget: roughly $2,300–2,600** before taxes/peripherals.

Notes:

- The B650-PLUS WIFI runs the second M.2 at Gen4 x4 — perfect for the
  SN850X models drive. First slot also Gen4 x4; either order works.
- NH-D15S clears the top PCIe slot on this board; the GIGABYTE card's
  backplate + anti-sag bracket fit the North/Meshify without mods.
- RM850x leaves ~350W headroom (7900 = 88W TDP, 4070 Ti Super = 285W).
- If you want headroom for a second GPU later, step up to the RM1000x
  (`CP-9020196-NA`).

## Coherence checklist (carried into the stack config)

The workstation ships with these already applied in
`llama/launch-llama.sh`:

1. `--jinja` — use the GGUF's embedded chat template (Qwen3/DeepSeek
   reasoning models degrade into tag-soup/repetition loops without it)
2. Q4_K/Q6_K quantizations only — our downloader pins those
3. Fresh llama.cpp master built from source (`./install.sh` does this),
   so tokenizer/template handling matches current model cards
4. No speculative decoding by default — add a draft model later via
   `LLAMA_EXTRA_ARGS="--model-draft ..."` only after validating output
