#!/bin/bash

# stay-awake.sh
# Prevents your Mac from sleeping using caffeinate

DURATION=""
DURATION_DISPLAY="indefinitely"

# Parse optional -t flag
while getopts "t:" opt; do
    case $opt in
    t)
        DURATION=$OPTARG
        DURATION_DISPLAY="for ${DURATION} seconds"
        ;;
    *)
        echo "Usage: $0 [-t duration_in_seconds]"
        exit 1
        ;;
    esac
done

# Print explanation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🍵 stay-awake.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Keeping your Mac awake $DURATION_DISPLAY"
echo ""
if [ -n "$DURATION" ]; then
    echo "  Running: caffeinate -d -i -s -t $DURATION"
else
    echo "  Running: caffeinate -d -i -s"
fi
echo "    -d  display won't sleep"
echo "    -i  system won't idle sleep"
echo "    -s  system won't sleep on AC power"
echo ""
echo "  Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Format seconds into hh:mm:ss
format_time() {
    local total=$1
    printf "%02d:%02d:%02d" $((total / 3600)) $((total % 3600 / 60)) $((total % 60))
}

# Cleanup on exit
cleanup() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ caffeinate stopped after: $(format_time $((SECONDS - START)))"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start caffeinate in background
if [ -n "$DURATION" ]; then
    caffeinate -d -i -s -t "$DURATION" &
else
    caffeinate -d -i -s &
fi
CAFFEINATE_PID=$!

# Live counter
START=$SECONDS
while kill -0 $CAFFEINATE_PID 2>/dev/null; do
    ELAPSED=$((SECONDS - START))
    printf "\r  ⏱  Running for: %s" "$(format_time $ELAPSED)"
    sleep 1
done

# If caffeinate exited on its own (e.g. -t expired)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Done! Ran for: $(format_time $((SECONDS - START)))"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
