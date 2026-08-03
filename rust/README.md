# yoda-wifi — the WiFi capture engine

A tiny Rust program that reads 802.11 **management frames** off a monitor-mode interface and prints
one JSON line per frame. Python reads those lines and does the detection.

Think of it exactly like `adsb-rx`: the fast, dumb capture engine lives in Rust, the brain lives in
Python, and they talk over a plain stream. Rust doesn't know Python exists — it just prints lines.

```
[ wlan1 monitor ] → yoda-wifi (Rust) → JSON lines → Detector.WiFi (Python) → alerts
```

---

## What it outputs

One line per management frame — the **same shape** as the `ev` dict the tshark path builds, so the
Python side (`Detector.WiFi.consume`) doesn't care which one fed it:

```json
{"sub":12,"src":"aa:bb:cc:dd:ee:ff","dst":"ff:ff:ff:ff:ff:ff","ssid":null,"rssi":null,"channel":null}
```

- `sub` — 802.11 subtype. **12 (0x0c) = deauth**, 8 = beacon.
- `src` / `dst` — transmitter / receiver MAC.
- `ssid` / `rssi` / `channel` — `null` in v1. These are the next fields to add (see the TODO in `main.rs`).

`sub` + `src` + `dst` is already everything you need to detect a **deauth flood**.

---

## Prerequisites

```bash
# libpcap (the capture library this links against)
sudo apt install libpcap-dev

# rust, if you don't have it
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# an interface in monitor mode
sudo ip link set wlan1 down
sudo iw dev wlan1 set type monitor
sudo ip link set wlan1 up
```

## Build & run

```bash
cd yoda/rust
cargo build --release          # binary lands in target/release/yoda-wifi

sudo ./target/release/yoda-wifi wlan1
```

You should see JSON lines scroll by. To watch just deauths:

```bash
sudo ./target/release/yoda-wifi wlan1 | grep '"sub":12'
```

## Feeding it into Python

Pipe stdout straight into the detector — the whole interface is "read a line, `json.loads` it":

```python
import json, subprocess

proc = subprocess.Popen(["sudo", "./target/release/yoda-wifi", "wlan1"],
                        stdout=subprocess.PIPE, text=True)

for line in proc.stdout:                 # one frame per line, in real time
    ev = json.loads(line)                # {"sub":12,"src":...,"dst":...}
    Detector.WiFi.consume(ev)            # same call the tshark path makes
```

(Later you can swap the pipe for a Unix socket so the engine and Python restart independently —
same as `adsb-rx` serving over a port.)

---

## How fast is it, vs scapy and tshark?

The honest answer: the win isn't a magic number, it's **removing work from the hot path**. Here's
what each approach actually does per frame:

| | scapy | tshark | yoda-wifi (Rust) |
|---|---|---|---|
| Language | Python | C (+ a subprocess) | compiled Rust |
| Where filtering happens | userspace (Python sees every frame) | userspace display filter (`-Y`) | **kernel** (BPF `type mgt`) |
| Per-frame work | full Python object build | full dissection of every frame, then text-serialize | read ~22 header bytes, format one line |
| The buffer that caused our lag | none | **dumpcap buffer** (lags on quiet air) | **off** (`immediate_mode`) |
| Drops under load | yes (can't keep up) | no | no |

**What that means in practice:**

- **vs tshark** — same C-speed capture, but yoda-wifi cuts the two things that hurt tshark for
  *detection*: the **dumpcap buffer** (its latency on quiet channels — gone via immediate mode) and
  **dissecting + text-serializing every frame** only to filter in userspace. yoda-wifi filters in the
  **kernel** and touches ~22 bytes per frame. Expect noticeably lower latency and a small fraction of
  the CPU on a busy channel.

- **vs scapy** — not really close. scapy builds a full Python object for every frame and **drops
  packets under load** (it's documented as not built for speed). Rust parsing a fixed 22-byte header
  is orders of magnitude cheaper per frame and won't drop during a flood — which is exactly when you
  need it.

**Rough latency classes** (ballpark, *measure on your own box* — these aren't benchmarks):
- scapy: fine on light traffic, falls behind and drops under a flood.
- tshark: C-fast, but frames can sit in the dumpcap buffer for a beat on a quiet channel.
- yoda-wifi: frame → JSON line in microseconds, no buffer, no drops.

The real point for a **24/7 box**: yoda-wifi sips CPU because the kernel filter means it only wakes for
management frames, and it never falls behind. That's what you want running all the time.

---

## What v1 does *not* do yet (on purpose — kept simple to read)

- **rssi / channel** — live in the radiotap header (`main.rs` currently just skips past it). Parsing
  the radiotap present-flags to pull the dBm signal + channel is the natural next step.
- **ssid** — lives in the beacon frame body as tagged parameters; walk those to read it.
- **output over a socket** instead of stdout — for restart-independence, like adsb-rx.

Each is a small, self-contained addition. Start by reading `main.rs` top to bottom — it's ~4 steps.
