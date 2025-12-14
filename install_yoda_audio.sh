cat > /usr/local/bin/yoda-audio << 'EOF'
#!/usr/bin/env bash
set -e

QUEUE="/var/lib/yoda-audio/queue"

if [[ $# -ne 1 ]]; then
    echo "Usage: yoda-audio <audio-file>"
    exit 1
fi

FILE="$1"

if [[ ! -f "$FILE" ]]; then
    echo "Error: file not found: $FILE"
    exit 1
fi

EXT="${FILE##*.}"
if [[ "$EXT" != "mp3" && "$EXT" != "wav" ]]; then
    echo "Error: only mp3 or wav supported"
    exit 1
fi

TS=$(date +%s)
BASENAME=$(basename "$FILE")
DEST="$QUEUE/${TS}_$BASENAME"

cp "$FILE" "$DEST"
echo "Queued: $DEST"
EOF

chmod +x /usr/local/bin/yoda-audio
