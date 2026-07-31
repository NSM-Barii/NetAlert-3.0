<p align="center">
  <img src="banner.gif" alt="Yoda" width="100%"/>
</p>

# Yoda

Passive RF monitoring for home. Tracks BLE devices, WiFi access points, and clients in your area in real time — with push notifications and jamming detection.

Just run it — a CLI will walk you through all settings before launching the TUI.

```bash
sudo venv/bin/python main.py
```

---

## What it monitors

**Bluetooth / BLE**
- Discovers nearby devices with vendor and manufacturer lookup
- Tracks signal strength (RSSI) per device
- Detects unstable devices (randomized/rotating MACs)
- Jamming detection via asymmetric EWMA drop score
- New max / min device count alerts

**WiFi — Access Points**
- Passive channel-hopping scan across 2.4GHz and 5GHz
- SSID, BSSID, channel, vendor, client count per AP
- New AP alerts

**WiFi — Clients**
- Tracks clients associating with nearby APs
- Three-state presence: online → idle → offline
- Session duration tracking
- Alerts when clients leave and return

---

## TUI

Four tabs — live dashboard, BLE device table, WiFi AP table, WiFi tree (APs with clients nested underneath).

```
┌─────────────────────────────────────────────────────────┐
│  BLE: 12  |  APs: 8  |  Clients: 3                     │
├─────────────────────────────────────────────────────────┤
│  Dashboard │ BLE Devices │ WiFi APs │ WiFi Tree         │
├──────────────────────┬──────────────────────────────────┤
│  Bluetooth/BLE       │  WiFi                            │
│                      │                                  │
│  live feed...        │  live feed...                    │
└──────────────────────┴──────────────────────────────────┘
```

---

## Push Notifications (ntfy)

Alerts route to your phone via [ntfy.sh](https://ntfy.sh) — install the ntfy app and subscribe to your topic, no account needed.

Notifications are **off by default and opt-in.** ntfy topics are public and unauthenticated — anyone who knows a topic name can read *and* post to it — so Yoda ships with no default topic. Choose your own long, hard-to-guess name; alerts only start sending once you set one.

BLE and WiFi alerts use **separate topics** so you can route them independently. The `-ntfy` flag is a shortcut that points **both** at the same topic:

```bash
# quick start — BLE and WiFi alerts to one topic
sudo venv/bin/python main.py -ntfy my-topic-a9f3k2
```

To send BLE and WiFi to **different** topics, skip `-ntfy` and set `ntfy_ble_path` / `ntfy_wifi_path` separately in the interactive setup prompt.

| Event | Priority |
|---|---|
| New BLE device | low |
| Unstable BLE device | max |
| BLE drop score rising | max |
| BLE instability alert | max |
| New WiFi AP | max |
| New client | max |
| Client left | max |
| Client returned | default |

---

## Jamming Detection

Yoda tracks a rolling average of visible BLE devices using an asymmetric EWMA:
- Average adapts **slowly** when count drops (`α = 0.01`) — sustained jamming doesn't let the baseline self-correct
- Average adapts **faster** when count rises (`α = 0.05`) — recovers cleanly after jamming stops

When the drop score or unstable device ratio exceeds your configured threshold, an alert fires. It won't re-fire until the metric recovers below half the threshold.

---

## Install

**BlueZ (Bluetooth):**
```bash
sudo apt update && sudo apt install bluez bluez-tools bluez-firmware -y
sudo systemctl enable bluetooth && sudo systemctl start bluetooth
systemctl status bluetooth
```

**tshark (Wi-Fi packet capture):**
```bash
sudo apt install tshark -y
```
> During install, select **Yes** when asked to allow non-superusers to capture packets, or run with `sudo`.

**Yoda:**
```bash
git clone https://github.com/nsm-barii/yoda
cd yoda/src
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Requires a wireless adapter that supports monitor mode.

---

## Usage

On launch, an interactive CLI walks you through every setting (interface, ntfy topics, thresholds, …), each pre-filled with a default — just hit Enter to accept.

Flags are optional shortcuts: any flag you pass becomes the **default shown in that prompt**, so you can pass it and press Enter, or still type over it. Nothing you don't pass is touched.

```
sudo venv/bin/python main.py
sudo venv/bin/python main.py -i wlan1
sudo venv/bin/python main.py -i wlan1 -ntfy my-topic-a9f3k2
sudo venv/bin/python main.py -i wlan1 -ntfy my-topic-a9f3k2 --bu 30 --bd 40
sudo venv/bin/python main.py --help
```

| Flag | Description | Default |
|---|---|---|
| `-i` | Monitor mode interface | `wlan1` |
| `-ntfy` | ntfy topic — sets **both** the BLE and WiFi topics | off |
| `--bu` | BLE unstable device threshold % | 25 |
| `--bd` | BLE drop score threshold % | 25 |
| `--obs` | Obfuscate MACs and SSIDs in the TUI | off |
| `--help` / `-h` | Show help and exit | — |

---

## Files

```
main.py          — entry point, CLI arg parsing
nsm_tui.py       — Textual TUI + CLI setup flow
nsm_monitor.py   — BLE and WiFi monitor logic
nsm_database.py  — vendor lookup, notifications, EWMA
nsm_vars.py      — shared state and variables
```

---

Made by NSM Barii
