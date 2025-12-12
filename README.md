# 🎯 YODA - Voice Activated IDS

> **Formerly NetAlert-3.0**

YODA is a voice-activated **Intrusion Detection System** designed for real-time LAN monitoring. Built with a hacker-themed dashboard and live network visualization, YODA tracks every device on your network and provides instant status updates.

**🤖 AI-Powered (Coming Soon)** - We're working on integrating AI for intelligent threat detection and anomaly analysis. Contributions welcome!

---

## ✨ Features

- 🔍 **Real-time device discovery** via ARP scanning
- 🎨 **Hacker-themed web dashboard** with Matrix effects
- 📊 **Live monitoring** of IP, MAC, hostname, vendor info
- 🗣️ **Voice commands** (hold spacebar to activate)
- 🔴 **Online/Offline tracking** for all network nodes
- ⚡ **No symlinks required** - data served directly from memory
- 🌐 **Cross-platform** support (Linux, macOS, Windows)

---

## 🚀 Quick Start

1. **Clone and navigate**
   ```bash
   cd nsm_modules
   ```

2. **Setup virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Run YODA**
   ```bash
   sudo venv/bin/python nsm_main.py
   ```

5. **Access the dashboard**
   - The program will prompt you for:
     - **Interface** (e.g., `eth0`, `wlan0`)
     - **Subnet** (e.g., `192.168.1.0/24`)
     - **Mode** (choose **GUI**)
   - Open your browser to the URL displayed in terminal (typically `http://localhost:8000/yoda.html`)

---

## 🎮 Usage

- **Auto-refresh**: Dashboard updates every 2 seconds (configurable)
- **Search & Filter**: Find nodes by IP, hostname, vendor, or MAC
- **Voice Commands**: Hold spacebar and say "refresh", "lockdown", or "clear"
- **Inspect Nodes**: Click INSPECT to view detailed device information
- **Emergency Lockdown**: Visual alert system (future: actual network blocking)

---

## 🤝 Contributing

Contributions are **welcome**, especially for:
- 🤖 **AI integration** for threat detection
- 🔒 **Automated blocking/prevention** features
- 🎤 **Enhanced voice commands**
- 📡 **Port scanning integration**

Submit PRs to [github.com/nsm-barii/netalert-3.0](https://github.com/nsm-barii/netalert-3.0)

---

## 📋 Requirements

- Python 3.x
- Scapy
- Rich (for CLI)
- See `requirements.txt` for full dependencies

---

## 📁 Project Structure

```
nsm_modules/     # Backend Python modules
web_modules/     # Frontend (HTML/CSS/JS)
  ├── yoda.html  # Main dashboard
  ├── css/       # Styles
  └── js/        # JavaScript + Matrix effects
```

---

**Built by NSM Barii** | [GitHub](https://github.com/nsm-barii/netalert-3.0) | Contributions Welcome
