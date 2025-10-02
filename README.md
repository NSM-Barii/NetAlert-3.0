# 🚨 NetAlert-3.0

NetAlert-3.0 is a LAN **Intrusion Detection System** (soon to become an Intrusion Prevention System) 🛡️ that continuously monitors your network for connected devices.  
It identifies and displays key details for each device, including:

- 💻 **IP Address**  
- 🏷️ **Hostname**  
- 🔑 **MAC Address**  
- 🏢 **Vendor**  

⚡ **Coming Soon:** automatic open port scanning for each device, giving you deeper visibility into potential security risks.  

All monitoring data is served to a live 🌐 browser-based frontend for easy management and real-time awareness.  

---

## 📂 Directory Structure
```
nsm_modules/     # Backend Python modules
web_modules/     # Frontend files
cpp_modules/     # (Optional) C++ modules
```

---

## ⚙️ How It Works
- **🧵 Background Threads**  
  - **📊 Summary Updater** – Updates stats like total nodes and currently online nodes.  
  - **🔍 ARP Scanner** – Runs interval-based ARP scans to discover all devices on the subnet.  

- **📡 Per-Device Monitoring**  
  - Each discovered device gets its own monitoring thread.  
  - Monitors whether the device is online or offline using repeated ARP checks.  

- **💻 HTTP Server**  
  - Hosts the web frontend.  
  - Dynamically loads `nodes.json` to display live device data.  

---

## ✨ Features
- ⚡ Real-time LAN device discovery using ARP.  
- 📶 Per-device status tracking.  
- 🌐 Web interface for easy viewing of network activity.  
- 🛡️ IDS core ready for future IPS features.  
- 📋 Device information: IP, hostname, MAC, vendor.  
- 🔮 (Planned) Per-device open port scanning.  

---

## 🚀 Setup & Running

1. **Navigate to the backend folder**  
   ```bash
   cd nsm_modules
   ```

2. **Create and activate a virtual environment**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Run the backend + frontend server**  
   ```bash
   sudo .venv/bin/python nsm_main.py
   ```

5. **📝 CLI Startup Prompts**  
   When starting, the program will ask for:  
   - **Interface** (`iface`) – Example: `eth0` or `wlan0`  
   - **Subnet** – Example: `192.168.1.0/24`  
   - **Mode** – Choose **GUI** unless you specifically want to test the unfinished CLI version.  

6. **🌍 Access the Frontend**  
   Once started, the terminal will print a link to open in your browser for the live GUI view.  

---

## 🔗 Optional: Symlink for `nodes.json` in `web_modules`

If you want the frontend in `web_modules` to directly use the live `nodes.json` file from the backend without copying it, create a symbolic link:

```bash
cd web_modules
ln -s ../../.data/netalert3/nodes.json .
```

Alternatively, you can point the frontend to read from:
```
~/Documents/nsm_tools/.data/netalert3/nodes.json (NOT RECOMMENDED)
```

This ensures the web interface always displays the latest device data.

---

## 📦 Requirements
- 🐍 Python 3.x  
- [📡 Scapy](https://scapy.net/)  
- 📄 `requirements.txt` dependencies  
