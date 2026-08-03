<p align="center">
  <img src="banner.gif" alt="Yoda" width="100%"/>
</p>

# Yoda

A passive RF **detection appliance** for a fixed location.

Yoda sits in one place and runs 24/7. Instead of just listing every Bluetooth and WiFi device it sees, it **learns what "normal" looks like there** — how many access points, clients, and BLE devices are usually around — and then **alerts you when reality drifts from that baseline or when it sees an attack** (Bluetooth jamming, WiFi deauth). Alerts reach you three ways: **spoken out loud** (TTS), **pushed to your phone** (ntfy), and shown on a **live web dashboard**.

The idea is simple: you shouldn't have to stare at a screen. Yoda watches the airspace, stays quiet while things are normal, and speaks up only when something changes.

```bash
sudo venv/bin/python main.py
```

A CLI walks you through every setting before it launches. For an unattended / boot-time install, use `--headless` to skip the prompts.

---

## What it watches

**Bluetooth / BLE**
- Nearby devices with vendor + manufacturer lookup and per-device RSSI
- Flags unstable devices (randomized / rotating MACs)
- **Jamming detection** — a sudden, sustained drop in visible devices
- Learns the typical device count and reacts to abnormal swings

**WiFi — Access Points**
- Passive channel-hopping across 2.4GHz and 5GHz
- SSID, BSSID, channel, vendor, RSSI, and live client count per AP
- Learns the typical AP count **per hour of day** and alerts on deviation

**WiFi — Clients**
- Tracks clients associating with nearby APs (vendor + RSSI)
- Three-state presence: online → idle → offline
- Learns the typical client count and alerts on deviation
- **Deauth detection** — flags deauthentication frames (a common WiFi attack)

---

## Web Dashboard

A single-page dashboard (served locally) polls the program once a second:

- Live counts (BLE / APs / clients) and the current drop / unstable scores
- A **jam banner** that flashes red the moment Bluetooth jamming is detected
- A BLE table (MAC, name, vendor, RSSI, state)
- A WiFi table where each **AP expands to reveal its clients** underneath — each client showing vendor, RSSI, and presence state

```
http://localhost:8080
```

Pass `--obs` to **obfuscate** the dashboard: MACs keep their vendor prefix but hide the unique half (`a4:83:e7:xx:xx:xx`) and SSIDs are masked. Handy for screenshots / screen-sharing. Your phone notifications still get the real values.

---

## Detection Model

Yoda doesn't alert on "a new device appeared" — in a normal neighborhood that happens constantly. It alerts on **deviation from a learned baseline**.

- Each metric (BLE count, WiFi AP count, WiFi client count) is tracked with an **asymmetric EWMA**:
  - adapts **slowly** when the count drops (`α = 0.01`) — so sustained jamming can't quietly become the new "normal"
  - adapts **faster** when the count rises (`α = 0.05`) — so it recovers cleanly afterward
- WiFi baselines are kept **per hour of day** — 3pm and 3am aren't the same airspace.
- An alert won't re-fire until the metric recovers below **half** the threshold (hysteresis, no flapping).
- During a confirmed jam the baseline **freezes** and only slow-thaws after 20 minutes.

---

## Voice Announcements

Yoda speaks (offline, via [piper](https://github.com/rhasspy/piper)):

- **Attacks** — "Bluetooth jamming attack detected", "WiFi deauthentication attack on channel N"
- **Status watchdog** — an area summary on an interval: quiet when calm (every 30 min by default), urgent during a jam (every 3 min). Both intervals are configurable (`--calm`, `--jam`).

---

## Push Notifications (ntfy)

Alerts route to your phone via [ntfy.sh](https://ntfy.sh) — install the app and subscribe to your topic, no account needed.

Notifications are **off by default and opt-in.** ntfy topics are public and unauthenticated — anyone who knows a topic name can read *and* post to it — so Yoda ships with no default topic. Choose your own long, hard-to-guess name; alerts only start sending once you set one.

BLE and WiFi alerts use **separate topics** so you can route them independently. The `-ntfy` flag is a shortcut that points **both** at the same topic:

```bash
# quick start — BLE and WiFi alerts to one topic
sudo venv/bin/python main.py -ntfy my-topic-a9f3k2
```

To send BLE and WiFi to **different** topics, skip `-ntfy` and set `ntfy_ble_path` / `ntfy_wifi_path` separately in the interactive setup.

Yoda is deliberately quiet — it pushes **threats and drift**, not routine chatter. Recoveries are sent at low priority so good news doesn't buzz your phone.

| Event | Priority |
|---|---|
| WiFi deauth attack | max |
| BLE jamming / drop rising | max |
| BLE instability rising | max |
| WiFi AP count spiked / dropped | max |
| WiFi client count spiked / dropped | max |
| **Hourly status summary** | low *(high if jammed)* |
| Any "recovered / back to baseline" | default |
| New BLE device *(opt-in: `verbose`)* | low |
| Client left / returned *(opt-in: `notify_client_events`)* | default |

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

On launch, an interactive CLI walks you through every setting (interface, ntfy topics, thresholds, …), each pre-filled with a default — just hit Enter to accept. Any flag you pass becomes the **default shown in that prompt**, so you can pass it and press Enter, or type over it. Nothing you don't pass is touched.

For a 24/7 / systemd install, add `--headless` to skip the prompts entirely and run on flags + defaults.

```
sudo venv/bin/python main.py
sudo venv/bin/python main.py -i wlan1
sudo venv/bin/python main.py -i wlan1 -ntfy my-topic-a9f3k2
sudo venv/bin/python main.py --headless -i wlan1 -ntfy my-topic-a9f3k2 --bu 30 --bd 40
sudo venv/bin/python main.py --help
```

| Flag | Description | Default |
|---|---|---|
| `-i` | Monitor mode interface | `wlan1` |
| `-ntfy` | ntfy topic — sets **both** the BLE and WiFi topics | off |
| `--bu` | BLE unstable device threshold % | 25 |
| `--bd` | BLE drop score threshold % | 35 |
| `--calm` | Voice status announcement interval when calm (minutes) | 30 |
| `--jam` | Voice announcement interval during a jam (minutes) | 3 |
| `--obs` | Obfuscate MACs and SSIDs on the dashboard | off |
| `--headless` | Skip interactive setup — flags + defaults only | off |
| `--help` / `-h` | Show help and exit | — |

---

## Files

```
src/main.py          — entry point, CLI arg parsing, startup
src/nsm_cli.py       — interactive setup + welcome screen
src/nsm_server.py    — web dashboard HTTP server + /data JSON
src/nsm_monitor.py   — BLE + WiFi capture (bleak / tshark)
src/nsm_detector.py  — detection engine, notifications, TTS, background threads
src/nsm_database.py  — vendor lookup + device logging
src/nsm_vars.py      — shared state and variables
gui/index.html       — dashboard front-end
rust/                — (WIP) libpcap WiFi capture engine, lower latency
```

---

Made by NSM Barii
