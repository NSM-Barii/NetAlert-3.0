#!/bin/bash
set -e

# RUNNING THIS --> bash install_yoda_audio.sh

echo "[YODA Audio Installer]"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "[ERROR] Do not run this script with sudo"
    echo "Run as: bash install_yoda_audio.sh"
    exit 1
fi

# Check for audio player
if ! command -v mpg123 &> /dev/null && ! command -v mpv &> /dev/null; then
    echo "[ERROR] Neither mpg123 nor mpv found"
    echo ""
    echo "Install one of these:"
    echo "  Debian/Ubuntu: sudo apt install mpg123"
    echo "  Arch:          sudo pacman -S mpg123"
    echo "  Fedora:        sudo dnf install mpg123"
    echo ""
    exit 1
fi
echo "[+] Audio player found"

# Create queue directory
QUEUE_DIR="$HOME/.yoda-audio"
mkdir -p "$QUEUE_DIR"
chmod 777 "$QUEUE_DIR"
echo "[+] Created queue directory: $QUEUE_DIR"

# Install yoda-audio command
INSTALL_USER="$USER"
sudo tee /usr/local/bin/yoda-audio > /dev/null << EOF
#!/bin/bash
set -e

# Detect real user even when running as root
if [[ \$EUID -eq 0 ]]; then
    REAL_USER=\$(logname 2>/dev/null || who am i | awk '{print \$1}')
    [[ -z "\$REAL_USER" ]] && REAL_USER="$INSTALL_USER"
    QUEUE_DIR=\$(eval echo ~\$REAL_USER)/.yoda-audio
else
    QUEUE_DIR="\$HOME/.yoda-audio"
fi

if [[ \$# -ne 1 ]]; then
    echo "Usage: yoda-audio <audio-file>"
    exit 1
fi

FILE="\$1"

if [[ ! -f "\$FILE" ]]; then
    echo "Error: file not found: \$FILE"
    exit 1
fi

# Create queue dir if needed
mkdir -p "\$QUEUE_DIR"
chmod 777 "\$QUEUE_DIR"

# Copy to queue with timestamp
TS=\$(date +%s%N)
BASENAME=\$(basename "\$FILE")
DEST="\$QUEUE_DIR/\${TS}_\${BASENAME}"

cp "\$FILE" "\$DEST"
chmod 666 "\$DEST"
echo "Queued: \$DEST"
EOF

sudo chmod +x /usr/local/bin/yoda-audio
echo "[+] Installed /usr/local/bin/yoda-audio"

# Install systemd user service
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$USER_SYSTEMD_DIR"

cat > "$USER_SYSTEMD_DIR/yoda-audio.service" << 'EOF'
[Unit]
Description=YODA Audio Player Daemon
After=sound.target

[Service]
Type=simple
ExecStart=/usr/local/bin/yoda-audio-daemon
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

echo "[+] Created systemd user service"

# Install daemon script
sudo tee /usr/local/bin/yoda-audio-daemon > /dev/null << 'EOF'
#!/bin/bash

QUEUE_DIR="$HOME/.yoda-audio"

echo "[YODA Audio Daemon] Starting..."

# Use inotifywait if available, otherwise poll
if command -v inotifywait &> /dev/null; then
    # Event-driven (fast)
    inotifywait -m -e create -e moved_to "$QUEUE_DIR" --format '%f' 2>/dev/null | while read FILE; do
        FILEPATH="$QUEUE_DIR/$FILE"
        if [[ -f "$FILEPATH" ]]; then
            echo "[PLAY] $FILE"
            mpg123 -q "$FILEPATH" 2>/dev/null || mpv --really-quiet "$FILEPATH" 2>/dev/null
            rm -f "$FILEPATH"
        fi
    done
else
    # Polling fallback (slower but works everywhere)
    echo "[WARN] inotifywait not found, using polling mode (install inotify-tools for better performance)"
    while true; do
        for FILE in "$QUEUE_DIR"/*; do
            if [[ -f "$FILE" ]]; then
                echo "[PLAY] $(basename "$FILE")"
                mpg123 -q "$FILE" 2>/dev/null || mpv --really-quiet "$FILE" 2>/dev/null
                rm -f "$FILE"
            fi
        done
        sleep 0.1
    done
fi
EOF

sudo chmod +x /usr/local/bin/yoda-audio-daemon
echo "[+] Installed /usr/local/bin/yoda-audio-daemon"

# Enable and start service for current user
systemctl --user daemon-reload
systemctl --user enable yoda-audio.service
systemctl --user start yoda-audio.service

echo ""
echo "[SUCCESS] YODA Audio installed!"
echo ""
echo "Usage:"
echo "  yoda-audio /path/to/file.mp3"
echo ""
echo "Service status:"
systemctl --user status yoda-audio.service --no-pager
echo ""
echo "To stop:  systemctl --user stop yoda-audio"
echo "To start: systemctl --user start yoda-audio"




[YODA Audio Installer]
[+] Audio player found
[+] Created queue directory: /tmp/yoda-audio
[+] Installed /usr/local/bin/yoda-audio
[+] Created systemd user service
[+] Installed /usr/local/bin/yoda-audio-daemon
Failed to connect to user scope bus via local transport: $DBUS_SESSION_BUS_ADDRESS and $XDG_RUNTIME_DIR not defined (consider using --machine=<user>@.host --user to connect to bus of other user)
                                                                                                                                                                                 
┌──(venv)─(bari㉿laptop)-[~/Documents/nsm_tools/Yoda]
└─$ sudo yoda-audio nsm_modules/output.mp3                                                                                                                       
Queued: /tmp/yoda-audio/1765709696228092337_output.mp3
