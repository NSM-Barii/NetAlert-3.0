#!/bin/bash

echo "[YODA Audio Uninstaller]"

# Stop and disable service
systemctl --user stop yoda-audio 2>/dev/null
systemctl --user disable yoda-audio 2>/dev/null
echo "[+] Stopped and disabled service"

# Remove binaries
sudo rm -f /usr/local/bin/yoda-audio
sudo rm -f /usr/local/bin/yoda-audio-daemon
echo "[+] Removed binaries"

# Remove systemd service
rm -f ~/.config/systemd/user/yoda-audio.service
systemctl --user daemon-reload
echo "[+] Removed systemd service"

# Remove queue directory
rm -rf ~/.yoda-audio
echo "[+] Removed queue directory"

echo ""
echo "[SUCCESS] YODA Audio uninstalled!"
