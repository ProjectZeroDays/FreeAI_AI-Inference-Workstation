# Center AI Workstation v1 — Build Guide

Physical assembly + OS install for the always-on AI workstation.
Software stack provisioning is automated by `install-stack.sh` —
you only touch a terminal once Ubuntu is on the machine.

Parts: see [parts-list.md](parts-list.md).

---

## 0. Prep (15 min)

- Clear, well-lit table; cardboard from the case box as a mat
- Philips #2 screwdriver (magnetic tip helps)
- Anti-static: touch bare metal of the case periodically; avoid carpet
- Keep small screws sorted: M2 (M.2/SSD), 6-32 (PSU), 6-32 coarse +
  standoffs are usually pre-installed

## 1. Motherboard out-of-case build

Do CPU/RAM/M.2/cooler with the board on its foam tray.

### 1.1 CPU
1. Lift the AM5 socket lever, open the retention plate.
2. Align the gold triangle (socket corner and CPU corner match);
   drop in — **never slide** the pins-side LGA socket.
3. Close plate, press lever down under its catch.

### 1.2 RAM (F5-6000J3040G32GX2-FX5)
1. Open both latches on slots **A2 and B2** (2nd and 4th from CPU).
2. Align the notch; push both ends until they click flat.
   Dual-channel requires A2+B2 — single-stick or wrong slots halve
   memory bandwidth.

### 1.3 M.2 SSDs
1. Both drives go heatsink-down per the board's quick-screw design:
   unscrew the standoff, slot at ~30°, lay flat, torque the screw.
2. Recommended: Samsung 990 EVO → CPU-adjacent M2_1 (OS),
   SN850X → M2_2 (models). Either order works electrically here.

### 1.4 CPU cooler (NH-D15S)
1. Mount the AM5 backplate behind the board (it ships attached to
   Noctua's bracket — check orientation per manual).
2. Apply paste: one 4–5mm dot center-CPU (NT-H2 included, or the
   pre-applied NT-H1 strip if you kept it).
3. Tower goes **vertical, fins front-to-back**, fan blowing toward
   the rear exhaust position. Offset design clears tall RAM.
4. Connect fan cable to `CPU_FAN` header (required or POST warns).

## 2. Case prep

1. Remove both tempered/acrylic side panels.
2. Standoffs: North/Meshify ship with ATX standoffs pre-installed —
   verify 9 positions against the board's holes.
3. I/O shield is integrated on this ASUS board — nothing to snap in.

## 3. Motherboard into case

Lower at an angle, rear I/O first into the case cutout, then set the
standoff holes over the brass posts. Screw all 9 (hand-snug, then
quarter-turn).

## 4. PSU + cabling

1. Slide RM850x fan-side **down** (or up in North's basement — either
   works; fan-down pulls cool air from beneath).
2. Connect:
   - 24-pin ATX → motherboard right edge
   - 8-pin EPS (CPU) → top-left `ATX_12V` — do not confuse with PCIe
   - PCIe 12VHPWR/8-pin ×? → GPU later (card uses 1×16-pin adapter or
     3×8-pin depending on GIGABYTE revision; use the native 12VHPWR
     cable Corsair includes)
3. Front-panel: USB-C/USB3 headers bottom edge; HD_AUDIO bottom-left;
   power sw pins bottom-right (polarity doesn't matter for switches).

## 5. GPU install

1. Remove two expansion-slot covers adjacent to the top slot.
2. Seat GV-N407TSGAMING OC-16GD until latch clicks.
3. Screw bracket; attach the anti-sag arm to the far end.
4. Plug the 16-pin power firmly — a half-seated 12VHPWR is the #1
   "GPU not detected" cause.

## 6. Fans

- 2× NF-A14 front intake (North: behind the walnut front)
- Rear 140mm exhaust (case-included fan acceptable)
- All PWM fans → case fan headers; set `DC/PWM = PWM` in BIOS later

## 7. First boot checklist (monitor + keyboard needed, last time)

1. Power on → POST beeps silent, fans spin, DRAM debug LED cycles then
   boots to "no bootable device" — that's expected.
2. Enter BIOS (Del):
   - Enable **EXPO** profile → DDR5-6000 CL30 (leaving JEDEC leaves
     ~20% memory bandwidth on the table)
   - `Advanced > PCI subsystem`: leave Re-Size BAR **on** (default;
     helps llama.cpp host transfers)
   - Restore AC power loss → **Power On** (24/7 box auto-restarts
     after outages)
   - Fan curves: chassis fans ~40% below 60°C
3. F10 save & exit.

## 8. Ubuntu Server 24.04 LTS

1. On another PC: flash ubuntu-24.04.x-live-server-amd64.iso to USB
   (Rufus / balenaEtcher).
2. Boot from USB (F8 boot menu). Install:
   - Whole disk (use the 1TB 990 EVO), LVM default is fine
   - Profile name + hostname (`center`)
   - **Install OpenSSH server** ✔
   - Skip snaps you don't need
3. Reboot, pull USB. Log in via LAN: `ssh user@<ip>` (find IP from
   router, or `ip a` on a temporary monitor session).

## 9. Provision the stack

```bash
sudo apt-get update && sudo apt-get install -y git
git clone <your-fork-url> ~/unified-ai-stack    # or scp the folder over
cd ~/unified-ai-stack/hardware
sudo ./install-stack.sh                          # drivers→CUDA→docker→stack→systemd
sudo reboot                                      # only if driver was freshly installed
```

Then verify:

```bash
nvidia-smi                                       # driver OK
curl -s localhost:8010/health                    # router
curl -s localhost:8030/api/status | head         # dashboard telemetry
python3 tokugawa.py status
```

## 10. Remote access (choose one)

- **Tailscale** (simplest): `curl -fsSL https://tailscale.com/install.sh | sh`
  → `sudo tailscale up` — every device on your tailnet reaches
  dashboard/router privately.
- **Cloudflare Tunnel**: `install-stack.sh` installs `cloudflared` when
  run with `ENABLE_CLOUDFLARED=1`; then
  `cloudflared tunnel login && cloudflared tunnel create center &&
  cloudflared tunnel route dns center <subdomain>` and point the config
  at `http://localhost:8030`.

Only ports **22, 8030, 8050** are opened by UFW; router (:8010) and
llama.cpp (:9001) stay localhost/tailnet-only by design.
