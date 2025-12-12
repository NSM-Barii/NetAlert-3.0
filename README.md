# 🎯 YODA - Voice Activated IDS
file:///var/mobile/Library/SMS/Attachments/87/07/367BB9D7-8143-4EBF-B154-813FD5017BCB/Image%2012-12-25%20at%201.55%E2%80%AFAM.png
> **Formerly NetAlert-3.0**

YODA is a voice-activated **Intrusion Detection System** designed for real-time LAN monitoring. The core feature is **voice control** - use natural language commands to manage your network, including kicking devices off your network, querying the number of active devices, and requesting detailed node information. All data is visualized through a hacker-themed dashboard with live network monitoring and Matrix-style effects.

**🤖 AI-Powered (Coming Soon)** - Integrating AI for intelligent threat detection and anomaly analysis. Contributions welcome!

---

## Features

- Real-time device discovery via ARP scanning
- Hacker-themed web dashboard with Matrix effects
- Live monitoring of IP, MAC, hostname, vendor info
- Voice commands for network management
- Online/Offline tracking for all network nodes

---

## Quick Start

1. **Clone and navigate**
   ```bash
   cd nsm_modules
   ```

2. **Setup virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Install mpg123 (required for voice commands)**
   ```bash
   # Debian/Ubuntu
   sudo apt install mpg123

   # Arch
   sudo pacman -S mpg123
   ```

5. **Run YODA**
   ```bash
   sudo venv/bin/python nsm_main.py
   ```

6. **Access the dashboard**
   - The program will prompt you for:
     - **Interface** (e.g., `eth0`, `wlan0`)
     - **Subnet** (e.g., `192.168.1.0/24`)
     - **Mode** (choose **GUI**)
   - Open your browser to the URL displayed in terminal (typically `http://localhost:8000/yoda.html`)

---

## Usage

- **Auto-refresh**: Dashboard updates every 2 seconds (configurable)
- **Search & Filter**: Find nodes by IP, hostname, vendor, or MAC
- **Inspect Nodes**: Click INSPECT to view detailed device information
- **Emergency Lockdown**: Visual alert system (future: actual network blocking)

---

## Contributing

Contributions are welcome, especially for:
- AI integration for threat detection
- Automated blocking/prevention features
- Enhanced voice commands
- Port scanning integration

Submit PRs to [github.com/nsm-barii/netalert-3.0](https://github.com/nsm-barii/netalert-3.0)

---

**Built by NSM Barii** | [GitHub](https://github.com/nsm-barii/netalert-3.0) | Contributions Welcome
