# NTFY Push Notifications - Complete Guide

## What is ntfy?

ntfy is a free push notification service that lets YODA send alerts directly to your phone. No signup, no API keys, just instant notifications.

**Key Features:**
- ✅ Free & open source
- ✅ Works on iOS & Android
- ✅ Supports rich notifications (emojis, buttons, attachments)
- ✅ Self-hostable for unlimited notifications
- ✅ Works from anywhere (not just local network)

---

## Quick Setup

### 1. Install ntfy App

**iPhone:**
- App Store → Search "ntfy"
- Install app

**Android:**
- Play Store → Search "ntfy"
- Install app

### 2. Subscribe to YODA Alerts

1. Open ntfy app
2. Tap "+" to add subscription
3. Enter topic name: `yoda-alerts` (or whatever you choose)
4. Done!

### 3. Test It

```bash
# Send test notification
curl -d "YODA is online!" https://ntfy.sh/yoda-alerts
```

Your phone should buzz with notification.

---

## Self-Hosting (Optional)

### Using Cloudflare Tunnel (Recommended)

**Step 1: Run ntfy server**
```bash
# Using Docker
docker run -d \
  --name ntfy \
  -p 8080:80 \
  binwiederhier/ntfy serve
```

**Step 2: Install cloudflared**
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Step 3: Start tunnel**
```bash
cloudflared tunnel --url http://localhost:8080
```

You'll get a URL like: `https://abc-123-xyz.trycloudflare.com`

**Step 4: Configure YODA**
```python
# In nsm_vars.py
NTFY_SERVER = "https://abc-123-xyz.trycloudflare.com"
NTFY_TOPIC = "yoda-alerts"
```

**Step 5: Add server in ntfy app**
- Open ntfy app
- Settings → Add Server
- Enter: `https://abc-123-xyz.trycloudflare.com`
- Subscribe to `yoda-alerts`

---

## Customization Options

### 1. Priority Levels

Controls how urgently your phone notifies you.

| Priority | Name | Sound | Vibration | Pop-up | Bypass DND |
|----------|------|-------|-----------|--------|------------|
| `1` | `min` | ❌ | ❌ | ❌ | ❌ |
| `2` | `low` | ❌ | ❌ | ❌ | ❌ |
| `3` | `default` | ✅ | ✅ | ❌ | ❌ |
| `4` | `high` | ✅ | ✅ | ✅ | ❌ |
| `5` | `max` | 🚨 ALARM | ✅ | ✅ | ✅ |

**Usage:**
```python
requests.post("https://ntfy.sh/yoda-alerts",
    headers={"Priority": "5"},  # or "max"
    data="CRITICAL ALERT"
)
```

**When to use:**
- Priority 5 (max): Critical attacks (deauth, mass intrusions)
- Priority 4 (high): Important alerts (unknown devices, AP offline)
- Priority 3 (default): Normal events (new device, reconnection)
- Priority 2 (low): Info only (device count updates)
- Priority 1 (min): Debug/verbose logs

---

### 2. Emojis & Tags

Add visual indicators to notifications.

**Security Emojis:**
```python
"Tags": "rotating_light"    # 🚨
"Tags": "warning"           # ⚠️
"Tags": "skull"             # 💀
"Tags": "fire"              # 🔥
"Tags": "lock"              # 🔒
"Tags": "unlock"            # 🔓
"Tags": "shield"            # 🛡️
"Tags": "no_entry"          # ⛔
"Tags": "radioactive"       # ☢️
"Tags": "biohazard"         # ☣️
```

**Network/Tech Emojis:**
```python
"Tags": "computer"          # 💻
"Tags": "satellite"         # 🛰️
"Tags": "signal_strength"   # 📶
"Tags": "wifi"              # 📡
"Tags": "zap"               # ⚡
"Tags": "gear"              # ⚙️
```

**Status Emojis:**
```python
"Tags": "white_check_mark"  # ✅
"Tags": "x"                 # ❌
"Tags": "red_circle"        # 🔴
"Tags": "green_circle"      # 🟢
"Tags": "yellow_circle"     # 🟡
```

**Combine multiple:**
```python
"Tags": "rotating_light,skull,fire"  # 🚨💀🔥
```

**Full emoji list:** https://docs.ntfy.sh/emojis/

---

### 3. Action Buttons

Add up to 3 clickable buttons to notifications.

#### **A) View Button - Opens URL**

```python
# Simple syntax
"Actions": "view, Open Dashboard, https://192.168.1.100:8080"

# Multiple actions (semicolon-separated)
"Actions": "view, Dashboard, https://dash.com; view, Logs, https://logs.com"
```

**Use cases:**
- Open web dashboard
- View attack details
- Open device management page

#### **B) HTTP Button - Trigger API**

```python
# Simple syntax
"Actions": "http, Block Attacker, https://192.168.1.100/api/block?mac=AA:BB:CC"

# With auth
"Actions": "http, Block MAC, https://api.com/block, headers.Authorization=Bearer secret123"

# POST with body
"Actions": "http, Kill Process, https://api.com/kill, method=POST, body={\"pid\":1234}"
```

**Use cases:**
- Block attacker MAC address
- Kill malicious process
- Restart service
- Trigger automation script

#### **C) Broadcast Button - Android Automation**

```python
# Trigger Tasker/MacroDroid actions
"Actions": "broadcast, Take Screenshot, extras.cmd=screenshot"
```

**Use cases (Android only):**
- Take photo when attack detected
- Start screen recording
- Toggle WiFi/VPN
- Launch security app

#### **Combining Actions**

```python
"Actions": "view, Dashboard, https://dash.com; http, Block, https://api/block; broadcast, Alert, extras.sound=alarm"
```

---

### 4. Click Action

URL to open when notification itself is tapped (not a button).

```python
"Click": "https://192.168.1.100:8080/attacks"
"Click": "yoda://open/attack/123"  # Deep link to app
```

---

### 5. Title & Markdown

```python
# Add title (bold)
"Title": "Deauth Attack Detected"

# Enable Markdown formatting
"Markdown": "yes"
# Data: "Attack from **AA:BB:CC** at `192.168.1.50`"
```

---

### 6. Icon & Attachments

```python
# Custom icon
"Icon": "https://yourserver.com/yoda-logo.png"

# Attach file/image
"Attach": "https://yourserver.com/attack-graph.png"
"Filename": "attack.png"

# Or send file directly
with open("attack.pcap", "rb") as f:
    requests.post("https://ntfy.sh/yoda",
        headers={"Filename": "attack.pcap"},
        data=f.read()
    )
```

---

### 7. Scheduled Delivery

```python
# Delay 30 minutes
"X-Delay": "30m"

# Send at specific time
"X-At": "8am"
"X-At": "2026-05-01 09:00"

# Send in duration
"X-In": "2h"
```

---

## YODA Alert Examples

### Critical: Deauth Attack

```python
requests.post("https://ntfy.sh/yoda-alerts",
    headers={
        "Priority": "max",
        "Title": "DEAUTH ATTACK DETECTED",
        "Tags": "rotating_light,skull,warning",
        "Click": "http://192.168.1.100:5000/attacks",
        "Actions": "http, Block Attacker, http://192.168.1.100/api/block?mac=AA:BB:CC, method=POST; view, Dashboard, http://192.168.1.100:5000"
    },
    data="Rate: 80 pkts/sec\nAttacker: AA:BB:CC:DD:EE:FF\nTarget: HomeNetwork"
)
```

**Result:**
- 🚨💀⚠️ MAX priority (alarm sound, bypasses DND)
- Tap notification → opens attacks page
- "Block Attacker" button → calls API to block MAC
- "Dashboard" button → opens main dashboard

---

### High: Unknown Device

```python
requests.post("https://ntfy.sh/yoda-alerts",
    headers={
        "Priority": "high",
        "Title": "Unknown Device Detected",
        "Tags": "computer,warning",
        "Click": "http://192.168.1.100:5000/devices/AA:BB:CC:DD:EE:FF"
    },
    data="MAC: AA:BB:CC:DD:EE:FF\nVendor: Apple Inc\nIP: 192.168.1.105"
)
```

**Result:**
- 💻⚠️ High priority (sound + vibration + pop-up)
- Tap notification → view device details

---

### High: Access Point Offline

```python
requests.post("https://ntfy.sh/yoda-alerts",
    headers={
        "Priority": "high",
        "Title": "Access Point Offline",
        "Tags": "no_entry,wifi",
    },
    data="AP: HomeNetwork (AA:BB:CC:DD:EE:FF)\nOffline for: 15 seconds\nPossible jamming attack"
)
```

**Result:**
- ⛔📡 High priority alert

---

### Default: New Device Max

```python
requests.post("https://ntfy.sh/yoda-alerts",
    headers={
        "Priority": "default",
        "Title": "New Maximum",
        "Tags": "white_check_mark,computer"
    },
    data="WiFi devices: 15 (new max)"
)
```

**Result:**
- ✅💻 Normal notification

---

### Low: Device Reconnected

```python
requests.post("https://ntfy.sh/yoda-alerts",
    headers={
        "Priority": "low",
        "Title": "Device Reconnected",
        "Tags": "green_circle,wifi"
    },
    data="iPhone-John reconnected at 192.168.1.50"
)
```

**Result:**
- 🟢📡 Silent notification (no sound/vibration)

---

## Python Integration

### Basic Function

```python
import requests

def send_ntfy(message, priority="default", title=None, tags=None, click=None, actions=None):
    """Send ntfy notification"""

    headers = {"Priority": priority}

    if title:
        headers["Title"] = title
    if tags:
        headers["Tags"] = tags
    if click:
        headers["Click"] = click
    if actions:
        headers["Actions"] = actions

    try:
        requests.post(
            "https://ntfy.sh/yoda-alerts",
            headers=headers,
            data=message,
            timeout=5
        )
    except Exception as e:
        print(f"ntfy error: {e}")
```

### Usage

```python
# Simple
send_ntfy("YODA online")

# With options
send_ntfy(
    message="Deauth attack - 80 pkts/sec",
    priority="max",
    title="ATTACK DETECTED",
    tags="rotating_light,skull",
    click="http://192.168.1.100:5000"
)
```

---

## Advanced: JSON Format

```python
import requests

requests.post("https://ntfy.sh",
    json={
        "topic": "yoda-alerts",
        "title": "Attack Detected",
        "message": "Deauth attack from AA:BB:CC:DD:EE:FF",
        "priority": 5,
        "tags": ["rotating_light", "skull"],
        "click": "https://dashboard.com",
        "actions": [
            {
                "action": "http",
                "label": "Block Attacker",
                "url": "https://api.com/block",
                "method": "POST",
                "headers": {
                    "Authorization": "Bearer secret"
                },
                "body": '{"mac": "AA:BB:CC:DD:EE:FF"}'
            },
            {
                "action": "view",
                "label": "Dashboard",
                "url": "https://192.168.1.100:5000"
            }
        ]
    }
)
```

---

## Alert Priority Matrix

| Event | Priority | Tags | Example |
|-------|----------|------|---------|
| Deauth Attack | 5 (max) | 🚨💀⚠️ | 80+ pkts/sec detected |
| Mass New Devices | 5 (max) | 🚨💻 | 5+ unknowns in 1 min |
| AP Offline | 4 (high) | ⛔📡 | HomeNetwork down >10s |
| Unknown Device | 4 (high) | 💻⚠️ | New MAC detected |
| Client Count Drop | 4 (high) | ⚠️📉 | 50% drop in clients |
| New Device Max | 3 (default) | ✅💻 | 15 devices (new max) |
| Device Reconnect | 2 (low) | 🟢📡 | iPhone-John back |
| Device Count Update | 1 (min) | 💻 | Current: 12 devices |

---

## Security Best Practices

### 1. Use Random Topic Names

```python
# Bad
NTFY_TOPIC = "yoda-alerts"  # Anyone can guess

# Good
NTFY_TOPIC = "yoda-hf8s9d7f-alerts"  # Random suffix
```

### 2. Self-Host for Sensitive Data

Use Cloudflare Tunnel or Tailscale for private notifications containing:
- MAC addresses
- IP addresses
- Network details
- Attack signatures

### 3. Rate Limiting

Avoid spam by using cooldowns:

```python
import time

last_alert = {}

def send_critical_alert(alert_type, message):
    now = time.time()

    # Don't send same alert type within 60 seconds
    if now - last_alert.get(alert_type, 0) < 60:
        return

    last_alert[alert_type] = now
    send_ntfy(message, priority="max")
```

---

## Troubleshooting

### Notifications Not Arriving

1. Check topic name matches in app and code
2. Test with curl: `curl -d "test" https://ntfy.sh/your-topic`
3. Check phone notification settings (not blocking ntfy)
4. Verify internet connection

### Self-Hosted Not Working

1. Check ntfy server is running: `docker ps`
2. Test locally: `curl http://localhost:8080/health`
3. Verify Cloudflare tunnel is running
4. Check firewall isn't blocking

### Actions Not Working

1. HTTP actions: Verify API endpoint is reachable
2. View actions: Check URL is valid
3. Broadcast actions: Only work on Android with automation apps

---

## Resources

- **Official Docs:** https://docs.ntfy.sh
- **Emoji List:** https://docs.ntfy.sh/emojis/
- **Examples:** https://docs.ntfy.sh/examples/
- **GitHub:** https://github.com/binwiederhier/ntfy

---

## Quick Reference

```python
# Priority levels: 1-5 or min/low/default/high/max
"Priority": "5"

# Tags (emojis): comma-separated
"Tags": "rotating_light,skull,warning"

# Title (bold)
"Title": "Alert Title"

# Click URL (tap notification)
"Click": "https://dashboard.com"

# Action buttons (up to 3, semicolon-separated)
"Actions": "view, Dashboard, https://dash.com; http, Block, https://api/block"

# Icon
"Icon": "https://yoursite.com/icon.png"

# Delay
"X-Delay": "30m"

# Markdown
"Markdown": "yes"
```
