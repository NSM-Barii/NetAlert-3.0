# LAN Device Monitor

This project is a LAN monitoring tool that discovers devices on your subnet in real time, tracks their online/offline status, and serves the data to a web-based frontend.

---

## Directory Structure
```
nsm_modules/     # Backend Python modules
web_modules/     # Frontend files
cpp_modules/     # (Optional) C++ modules
```

---

## How It Works
- **Background Threads**
  - **Summary Updater** – Updates stats like total nodes and currently online nodes.
  - **ARP Scanner** – Runs interval-based ARP scans to discover all devices on the subnet.

- **Per-Device Monitoring**
  - Each discovered device gets its own monitoring thread.
  - Monitors whether the device is online or offline using repeated ARP checks.

- **HTTP Server**
  - Hosts the web frontend.
  - Dynamically loads `nodes.json` to display live device data.

---

## Features
- Real-time LAN device discovery using ARP.
- Per-device status tracking.
- Web interface for easy viewing of network activity.

---

## Setup & Running

1. **Navigate to the backend folder**:
   ```bash
   cd nsm_modules
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Run the backend + frontend server**:
   ```bash
   sudo .venv/bin/python nsm_main.py
   ```

5. **CLI Startup Prompts**
   When starting, the program will ask for:
   - **Interface** (`iface`) – Example: `eth0` or `wlan0`
   - **Subnet** – Example: `192.168.1.0/24`
   - **Mode** – Choose **GUI** unless you specifically want to test the unfinished CLI version.

6. **Access the Frontend**
   Once started, the terminal will print a link to open in your browser for the live GUI view.

---

## Requirements
- Python 3.x
- [Scapy](https://scapy.net/)
- `requirements.txt` dependencies
