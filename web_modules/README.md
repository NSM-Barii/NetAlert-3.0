# DISCLAMER - WHILE ALL PYTHON MODULES ARE MADE BY ME (NSM BARII), ALL HTML MODULES ARE CREATED WITH AI
![alt text](image-1.png)
# NetAlert Dashboard (WebSocket Edition) 

A real-time network status dashboard for **NetAlert 3.0**, supporting both HTTP polling and WebSocket live updates.

---

## 📌 Features

### Core Dashboard
- **GitHub Link** in header → `nsm-barii/netalert-3.0`
- **Condensed width** (~1024px) for balanced view
- Auto-sort **online** nodes → top, **offline** → bottom
- **Search bar** (matches IP, host, vendor, MAC)
- **Status filter** dropdown (`All`, `Online`, `Offline`)
- Summary display: **Online count / Total count**

### Visual Theme
- Hybrid **modern / retro hacker / cyberpunk purple**
- Dark gradient background with subtle animated grid
- Monospace typography
- Gradient headers + soft glow
- Animated status dots (online = pulse, offline = fade)
- Custom purple tooltips with:
  - IP
  - Host
  - MAC
  - Vendor
  - Last Seen

### Performance
- **Performance Mode** toggle (disables animations/glow for speed)
- Debounced search (120ms)
- Prevents overlapping fetches during auto-refresh
- Supports **local file load** & **HTTP fetch**

### Reactive Updates
- **Diff-aware updating** — only changes/new rows are updated
- Detects:
  - **New devices**
  - **Status changes**
- Highlight animations:
  - New device → green glow
  - Status change → amber glow
- Toast notifications for changes
- Optional beep toggle

### WebSocket Mode
- **WebSocket controls**:
  - Enter URL
  - Connect / Disconnect
  - Status LED
  - "Use WebSocket mode" toggle
- Auto-pauses polling when WS is active
- Accepts:
  - Full snapshots: `{ summary, nodes }` (array or IP-keyed object)
  - Incremental single device updates
- Integrates with all reactive + visual features

---

## ⚙️ Setup & Usage

### 1. Prepare JSON Data
Ensure your NetAlert 3.0 Python backend outputs a valid `nodes.json` file in:
```
~/Documents/nsm_tools/.data/netalert3/nodes.json
```

### 2. Create a Symlink
From your dashboard project directory, symlink the `nodes.json` file:
```bash
ln -s ~/Documents/nsm_tools/.data/netalert3/nodes.json ./nodes.json
```

### 3. Run a Local HTTP Server
From the same directory containing `nodes.json`, run:
```bash
python3 -m http.server 8080
```
This will make `nodes.json` available at:
```
http://localhost:8080/nodes.json
```

### 4. Load Data in Dashboard
- Open `netalert_dashboard_ws.html` in your browser
- In the **HTTP Fetch** field, enter:
```
/nodes.json
```
- Click **Fetch** to load the latest data

### 5. WebSocket Mode (Optional)
If your backend sends live updates:
1. Enter your WebSocket server URL in the **WebSocket URL** field (e.g., `ws://localhost:9000`).
2. Click **Connect** and enable **Use WebSocket Mode**.
3. Dashboard will update instantly on device changes.

---

## 📸 Screenshot
*(Add screenshot here)*

---

## 📝 License
MIT License — see LICENSE for details.
