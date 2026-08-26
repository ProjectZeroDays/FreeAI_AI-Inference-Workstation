# FreeAI Workstation — Build Guide

Physical assembly + OS install for the always-on AI workstation.
Software stack provisioning is automated by `install-stack.sh` —
you only touch a terminal once Ubuntu is on the machine.

Parts: see [PARTS-LIST.md](PARTS-LIST.md).

---

## 0. Prep (15 min)

- Clear, well-lit table; cardboard from the case box as a mat
- Philips #2 screwdriver (magnetic tip helps)
- Anti-static: touch bare metal of the case periodically; avoid carpet
- Keep small screws sorted: M2 (M.2/SSD), 6-32 (PSU), standoffs are
  usually pre-installed in the CH510

## 1. Motherboard out-of-case build

Do CPU/RAM/M.2/AIO mount with the board on its foam tray.

### 1.1 CPU (LGA1700 — i9-14900KF)

1. Lift the LGA1700 socket lever, open the retention plate (Hynix
   ILM — don't overtighten later).
2. Align the gold triangle (socket corner and CPU corner match);
   drop in — **never slide** the pins-side LGA socket.
3. Close plate, press lever down under its catch. Check the triangle
   is still aligned after closing.

### 1.2 RAM (TeamGroup Delta RGB 4×32GB DDR5-6000)

1. Open latches on all four slots; populate **A2 and B2 first** (2nd
   and 4th from CPU) for initial POST, then fill A1/B1.
2. Align the notch; push both ends until they click flat and latches
   snap. Delta RGB height (46 mm) clears the EKWB AIO tubes.
3. Dual-channel is automatic with 4 sticks — no slot choice penalty
   after all four are in.

### 1.3 M.2 SSDs (2× MSI Spatium M480 Pro 2TB)

1. Both drives go heatsink-down per the Tomahawk's Shield Frozr
   heatsinks: remove heatsink screw, slot at ~30°, lay flat, replace
   heatsink and torque the screw (don't overtighten the SSD itself).
2. Recommended: top slot M2_1 (CPU-direct, PCIe 4.0 x4) → OS,
   M2_2 (chipset, PCIe 4.0 x4) → models. Either order works
   electrically; CPU-direct is slightly lower latency for the OS.

### 1.4 CPU cooler (EKWB 360 mm AIO)

1. Mount the LGA1700 backplate + standoffs per EKWB manual (1700
   hole spacing — not 1200).
2. Apply paste: one 4–5 mm dot center-CPU (NT-H2 or EKWB paste).
3. Radiator goes **top-mount** in the CH510 (360 mm fits top or
   front; top as exhaust is quietest with this case). Tubes toward
   the front if front-mounted, toward the rear if top-mounted.
4. Connect pump tach to `CPU_FAN` (or `AIO_PUMP` if present) and
   radiator fans to `CPU_FAN`/`SYS_FAN` — BIOS expects a fan on
   `CPU_FAN` or POST warns.
5. RGB: Delta RAM + EKWB block via JRAINBOW headers (optional).

## 2. Case prep (Deepcool CH510)

1. Remove both side panels (thumbscrews).
2. Standoffs: CH510 ships with ATX standoffs pre-installed — verify
   9 positions against the Z790 Tomahawk's holes.
3. I/O shield is integrated on this MSI board — nothing to snap in.

## 3. Motherboard into case

Lower at an angle, rear I/O first into the case cutout, then set the
standoff holes over the brass posts. Screw all 9 (hand-snug, then
quarter-turn). Don't forget the center standoff — it aligns the board.

## 4. PSU + cabling (ABS 1000W Gold ATX 3.0)

1. Slide ABS 1000W fan-side **down** (CH510 bottom vent — pulls cool
   air from beneath).
2. Connect:
   - 24-pin ATX → motherboard right edge
   - 2× 8-pin EPS (CPU) → top-left `CPU_PWR1` + `CPU_PWR2` — both
     populated for 14900KF PL2; do not confuse with PCIe
   - Native 12VHPWR (16-pin) → RTX 4090 Gaming X Trio — one cable
     direct from PSU (ATX 3.0, no adapter needed); seat firmly until
     the latch clicks — a half-seated 12VHPWR is the #1 "GPU not
     detected" cause
3. Front-panel: USB-C/USB3 headers bottom edge; HD_AUDIO bottom-left;
   power sw pins bottom-right (polarity doesn't matter for switches).

## 5. GPU install (MSI RTX 4090 Gaming X Trio — 3.5 slots)

1. Remove three expansion-slot covers adjacent to the top PCIe x16 slot
   (card is 3.5 slots wide).
2. Seat firmly until the PCIe latch clicks; the Gaming X Trio's
   support bracket screws to the case slots — install it.
3. Plug the native 12VHPWR; check the sense pins are fully seated
   (no gap at the shroud).
4. Verify the card doesn't sag — the included anti-sag arm is
   recommended even with the bracket.

## 6. Fans

- CH510 stock: 1× rear 120 mm exhaust + front mesh (add 2× 120/140 mm
  front intake if not included — front mesh is the main GPU intake)
- Radiator fans: as exhaust if top-mounted, intake if front-mounted
- All PWM fans → `SYS_FAN` headers; set `DC/PWM = PWM` in BIOS later

## 7. First boot checklist (monitor + keyboard needed, last time)

1. Power on → POST, fans spin, DRAM debug LED cycles then
   boots to "no bootable device" — that's expected.
2. Enter BIOS (Del):
   - Enable **XMP** profile → DDR5-6000 (JEDEC 4800 leaves ~20%
     memory bandwidth on the table; 4×32 at 6000 may train at
     5600–6000 depending on IMC — XMP is the target)
   - `Settings > PCIe subsystem`: leave Resizable BAR **on**
     (helps llama.cpp host transfers)
   - `Settings > Advanced > Power Management`: Restore AC power
     loss → **Power On** (24/7 box auto-restarts after outages)
   - Fan curves: AIO pump 100% (if on AIO_PUMP header), chassis
     fans ~40% below 60°C, ramp to 80% by 75°C
3. F10 save & exit.

## 8. Ubuntu Server 24.04 LTS

1. On another PC: flash ubuntu-24.04.x-live-server-amd64.iso to USB
   (Rufus / balenaEtcher). Desktop ISO also works.
2. Boot from USB (F11 boot menu on MSI). Install:
   - Whole disk (use the 2 TB OS NVMe), LVM default is fine;
     leave the 2nd NVMe untouched for `/srv` later
   - Hostname `freeai` (or `center`)
   - **Install OpenSSH server** ✔
   - Skip snaps you don't need
3. Reboot, pull USB. Log in via LAN: `ssh user@<ip>` (find IP from
   router, or `ip a` on a temporary monitor session).

> Windows 11 Pro note: the box ships with Windows on NVMe1.
> Shrink or wipe that partition during Ubuntu install, or install
> Ubuntu to the 2nd NVMe and dual-boot — either works. The stack
> targets Linux + NVIDIA.

## 9. Provision the stack

```bash
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/ProjectZeroDays/FreeAI_Ubuntu-AI-Inference-Workstation.git ~/FreeAI
cd ~/FreeAI
sudo ./hardware/install-stack.sh              # drivers→CUDA→docker→stack→systemd
sudo reboot                                   # only if driver was freshly installed
```

Then verify:

```bash
nvidia-smi                                    # expect: RTX 4090, 24564 MiB
curl -s localhost:8030/api/status | python3 -m json.tool | head -20
python3 freeai.py status
```

Dashboard at `http://<ip>:8030` should show GPU util/temp/power/clock
and all core services UP (sample telemetry if `SAMPLE_TELEMETRY=1`).

## 10. Remote access (choose one)

- **Desktop profile** (recommended): `docker compose --profile desktop up -d`
  (XFCE + TigerVNC :5901 + noVNC :6080) → `http://<ip>:6080`
- **Tailscale** (simplest private mesh): `curl -fsSL https://tailscale.com/install.sh | sh`
  → `sudo tailscale up` — every device on your tailnet reaches
  dashboard/router privately.
- **Cloudflare Tunnel**: `ENABLE_CLOUDFLARED=1 sudo ./hardware/install-stack.sh`
  installs `cloudflared`; then
  `cloudflared tunnel login && cloudflared tunnel create freeai &&
  cloudflared tunnel route dns freeai <subdomain>` and point the config
  at `http://localhost:8030`.

Only ports **22, 8030, 8050** are opened by UFW by default; add
`ENABLE_DESKTOP_PORTS=1` for 5901/6080. Router (:8010) and llama.cpp
(:9001) stay localhost/tailnet-only by design.
