# FreeAI Workstation — Verified Parts List

As-shipped build (see [BUILD-SHEET.md](../docs/BUILD-SHEET.md)). Every part
below is the exact SKU in the running box; MPN/ASIN where confirmed.

| Category | Part | MPN / SKU | Store ref | Est. USD |
|---|---|---|---|---|
| CPU | Intel Core i9-14900KF (8P+16E, 32 threads, 6.0 GHz TVB Max) | `BX8071514900KF` | Amazon / Newegg / MC | $530–590 |
| Cooler | EKWB EK-AIO 360 D-RGB (360 mm AIO) | `3831109811402` | Amazon / EKWB | $140–170 |
| Motherboard | MSI Z790 Tomahawk WiFi DDR5 (LGA1700, ATX) | `Z790 Tomahawk WiFi` | Amazon / Newegg / MC | $210–260 |
| GPU | MSI GeForce RTX 4090 Gaming X Trio 24G (DLSS 3) | `G4090GXT24` / `912-V510-014` | Amazon | $1,600–1,850 |
| RAM | TeamGroup Delta RGB 128GB (4×32GB) DDR5-6000 | `FF3D532G6000HC38ADC01` (4×32 kit) | Amazon / Newegg | $380–450 |
| OS SSD | MSI Spatium M480 Pro 2TB Gen4 NVMe (PCIe 4.0) | `S78-440L730-P83` | Amazon / MC | $140–170 |
| Models SSD | MSI Spatium M480 Pro 2TB Gen4 NVMe (2nd drive) | `S78-440L730-P83` | Amazon / MC | $140–170 |
| PSU | ABS 1000W Gold ATX 3.0 (ATX 3.0, PCIe 5.0 12VHPWR) | `ABS-1000G-ATX30` | Newegg | $140–180 |
| Case | Deepcool CH510 ATX (mesh front, 17.13×9.06×18.55 in) | `R-CH510-BKNNE1-G-1` | Amazon / Newegg | $80–110 |
| Network | On-board Wi-Fi 6E + BT 5.3 (Z790 Tomahawk) | — | — | incl. |

**Budget: roughly $3,400–3,800** before taxes/peripherals (4090 dominates).

Notes:

- **Windows 11 Pro ships on the box** — the FreeAI stack targets
  **Ubuntu 24.04 LTS**. Dual-boot or wipe per
  [FIRST-BOOT-GUIDE.md](../docs/FIRST-BOOT-GUIDE.md); the installer
  expects Ubuntu + NVIDIA driver 580+ (CUDA 13.0).
- **RAM**: 4×32 DDR5-6000 runs via XMP/EXPO. Z790 Tomahawk needs BIOS
  with 14th-gen support (ships ready on recent stock; update if POST
  shows no CPU). Use slots A2/B2 first for 2-stick, then fill A1/B1.
- **Storage split**: NVMe1 (OS + hot Q6_K roster) / NVMe2 (RAG +
  cold models + logs) — keeps model swaps off the OS disk.
- **PSU**: ATX 3.0 native 12VHPWR handles the 4090's 450 W transients
  without an adapter; 1000 W leaves ~400 W headroom for the 253 W
  PL2 14900KF burst.
- **Thermals**: 360 mm AIO is mandatory for 24/7 14900KF PL2; CH510
  mesh front + 2× front intake keeps the Gaming X Trio's 3.5-slot
  cooler fed. Wired Ethernet strongly preferred for noVNC + streaming.
- **Alternatives**: RTX 6000 Ada (48 GB, ECC) or Blackwell 96 GB drop
  into the same board/PSU if you outgrow 24 GB — see BUILD-SHEET
  GPU tier table.

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
