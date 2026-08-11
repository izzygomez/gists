#!/bin/bash

# stay-awake.sh
# Prevents your Mac from sleeping, using `caffeinate`.

DURATION=""
DURATION_DISPLAY="indefinitely"

usage() {
    cat <<'EOF'
Usage: stay-awake.sh [-t seconds] [-h]

  -t seconds   Stay awake for a fixed duration, then exit. Must be a
               positive integer. Omit to stay awake indefinitely.
  -h, --help   Show this help.

Flags passed to caffeinate:
    -d  display won't sleep
    -i  system won't idle sleep
    -s  system won't sleep on AC power
    -u  keeps screensaver/lock from triggering
EOF
}

# Long options: getopts only handles single-char flags, so handle these first.
for arg in "$@"; do
    case $arg in
    --help)
        usage
        exit 0
        ;;
    --) break ;; # conventional end-of-options marker
    --*)
        echo "Error: unknown option '$arg'" >&2
        usage >&2
        exit 1
        ;;
    esac
done

# Leading ':' → silent mode, so we print our own messages for bad input.
while getopts ":t:h" opt; do
    case $opt in
    t)
        DURATION=$OPTARG
        if ! [[ $DURATION =~ ^[0-9]+$ ]] || [ "$DURATION" -eq 0 ]; then
            echo "Error: -t requires a positive integer (seconds), got '$DURATION'" >&2
            exit 1
        fi
        DURATION_DISPLAY="for ${DURATION} seconds"
        ;;
    h)
        usage
        exit 0
        ;;
    :)
        echo "Error: option -$OPTARG requires a value" >&2
        usage >&2
        exit 1
        ;;
    \?)
        echo "Error: unknown option '-$OPTARG'" >&2
        usage >&2
        exit 1
        ;;
    esac
done
shift $((OPTIND - 1))

# Reject any leftover (unrecognized) positional arguments
if [ "$#" -gt 0 ]; then
    echo "Error: unexpected argument '$1'" >&2
    usage >&2
    exit 1
fi

format_time() {
    local total=$1
    printf "%02d:%02d:%02d" $((total / 3600)) $((total % 3600 / 60)) $((total % 60))
}

# Single footer path used by both the signal trap and normal completion.
# $1 = label, $2 = elapsed seconds to display.
print_footer() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ $1: $(format_time "$2")"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

START=$SECONDS # set BEFORE the trap that references it

cleanup() {
    trap - SIGINT SIGTERM              # avoid re-entry
    kill "$CAFFEINATE_PID" 2>/dev/null # explicitly stop caffeinate (SIGTERM-safe)
    print_footer "Stopped after" "$((SECONDS - START))"
    exit 0
}
trap cleanup SIGINT SIGTERM

# Banner
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🍵 stay-awake.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Keeping your Mac awake $DURATION_DISPLAY"
echo ""
if [ -n "$DURATION" ]; then
    echo "  Running: caffeinate -d -i -s -u -t $DURATION"
else
    echo "  Running: caffeinate -d -i -s -u"
fi
echo "    -d  display won't sleep"
echo "    -i  system won't idle sleep"
echo "    -s  system won't sleep on AC power"
echo "    -u  keeps screensaver/lock from triggering"
echo ""
echo "  Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start caffeinate in the background so we can show a live counter.
if [ -n "$DURATION" ]; then
    caffeinate -d -i -s -u -t "$DURATION" &
else
    caffeinate -d -i -s -u &
fi
CAFFEINATE_PID=$!

# Live counter. Track the last displayed value so the footer matches the
# counter exactly, instead of re-reading the clock after the final sleep.
ELAPSED=0
while kill -0 "$CAFFEINATE_PID" 2>/dev/null; do
    ELAPSED=$((SECONDS - START))
    printf "\r  ⏱  Running for: %s" "$(format_time "$ELAPSED")"
    sleep 1
done

# caffeinate exited on its own (e.g. -t expired)
print_footer "Done — ran for" "$ELAPSED"
