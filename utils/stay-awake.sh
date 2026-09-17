#!/bin/bash

# stay-awake.sh
# Prevents your Mac from sleeping, using `caffeinate`.

DURATION="" # total seconds passed to caffeinate (empty = indefinite)
DURATION_DISPLAY="indefinitely"
INPUT_FORM="" # how -t was written: SEC | MIN:SEC | HR:MIN:SEC

usage() {
    cat <<'EOF'
Usage: stay-awake.sh [-t DURATION] [-h]

  -t DURATION  Stay awake for a fixed time, then exit. DURATION is one of:
                 SECONDS   a positive integer, e.g. 9000
                 MM:SS     minutes:seconds, e.g. 2:30   (SS is 00-59)
                 HH:MM:SS  hours:minutes:seconds, e.g. 2:30:00 (MM, SS 00-59)
               Omit -t to stay awake indefinitely.
  -h, --help   Show this help.

Flags passed to caffeinate, as `-disu -w <pid of this script>`:
    -d  display won't sleep
    -i  system won't idle sleep
    -s  system won't sleep on AC power
    -u  keeps screensaver/lock from triggering
    -w  stop if this script dies (e.g. if `kill -9 <pid>` is used)

This script keeps its own timer instead of using caffeinate's `-t` flag.
EOF
}

# Parse a -t value into total seconds. Accepts:
#   SECONDS    one integer, e.g. 9000
#   MM:SS      e.g. 2:30      (SS is 00-59; MM is not capped, so 90:00 is valid)
#   HH:MM:SS   e.g. 2:30:00   (MM and SS are 00-59; HH is not capped)
# Sets globals DURATION (integer seconds) and INPUT_FORM (SEC|MIN:SEC|HR:MIN:SEC).
# `10#` forces base 10 so a leading zero (e.g. 08) is not read as octal.
# Returns 1 for a bad format, 2 for a zero duration.
parse_duration() {
    local raw=$1 h m s
    if [[ $raw =~ ^[0-9]+$ ]]; then
        DURATION=$((10#$raw))
        INPUT_FORM="SEC"
    elif [[ $raw =~ ^([0-9]+):([0-5]?[0-9])$ ]]; then
        m=$((10#${BASH_REMATCH[1]}))
        s=$((10#${BASH_REMATCH[2]}))
        DURATION=$((m * 60 + s))
        INPUT_FORM="MIN:SEC"
    elif [[ $raw =~ ^([0-9]+):([0-5]?[0-9]):([0-5]?[0-9])$ ]]; then
        h=$((10#${BASH_REMATCH[1]}))
        m=$((10#${BASH_REMATCH[2]}))
        s=$((10#${BASH_REMATCH[3]}))
        DURATION=$((h * 3600 + m * 60 + s))
        INPUT_FORM="HR:MIN:SEC"
    else
        return 1
    fi
    [ "$DURATION" -gt 0 ] || return 2
    return 0
}

# Render seconds as words (e.g. "2hr 30min"), at the granularity of INPUT_FORM.
# Zero-valued fields are dropped. MM:SS keeps minutes uncapped (90:00 -> 90min);
# a bare seconds value and HH:MM:SS both carry up into hr/min/sec.
format_duration() {
    local total=$1 form=$2 h=0 m=0 s=0 out=""
    if [ "$form" = "MIN:SEC" ]; then
        m=$((total / 60))
        s=$((total % 60))
    else
        h=$((total / 3600))
        m=$((total % 3600 / 60))
        s=$((total % 60))
    fi
    [ "$h" -gt 0 ] && out="${h}hr"
    [ "$m" -gt 0 ] && out="${out:+$out }${m}min"
    [ "$s" -gt 0 ] && out="${out:+$out }${s}sec"
    printf '%s' "$out"
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
        parse_duration "$OPTARG"
        case $? in
        1)
            echo "Error: -t must be SECONDS, MM:SS, or HH:MM:SS with MM and SS 00-59, got '$OPTARG'" >&2
            usage >&2
            exit 1
            ;;
        2)
            echo "Error: -t duration must be more than 0, got '$OPTARG'" >&2
            exit 1
            ;;
        esac
        DURATION_DISPLAY="for $(format_duration "$DURATION" "$INPUT_FORM")"
        # Echo the raw seconds only for a bare seconds input, and only once it
        # was regrouped into larger units (>= 60s); below that it is redundant.
        if [ "$INPUT_FORM" = "SEC" ] && [ "$DURATION" -ge 60 ]; then
            DURATION_DISPLAY="$DURATION_DISPLAY (i.e. $DURATION seconds)"
        fi
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
    trap - SIGINT SIGTERM SIGHUP       # avoid re-entry
    kill "$CAFFEINATE_PID" 2>/dev/null # explicitly stop caffeinate (SIGTERM-safe)
    print_footer "Stopped after" "$((SECONDS - START))"
    exit 0
}
trap cleanup SIGINT SIGTERM SIGHUP

# Banner
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🍵 stay-awake.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Keeping your Mac awake $DURATION_DISPLAY"
echo ""
echo "  Running: caffeinate -disu -w $$"
echo "    -d  display won't sleep"
echo "    -i  system won't idle sleep"
echo "    -s  system won't sleep on AC power"
echo "    -u  keeps screensaver/lock from triggering"
echo "    -w  stops caffeinate if stay-awake.sh dies"
echo "        (e.g. \`kill -9 $$\`)"
echo ""
echo "  Press Ctrl+C to stop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Background caffeinate so we can show a live counter.
# Not using caffeinate's -t: it is not strictly wall-clock time, because macOS
# defers the timer it exits on to save power, so it always runs long (up to 60s).
caffeinate -disu -w $$ &
CAFFEINATE_PID=$!

# Live counter. This loop, not caffeinate, decides when the time is up.
ELAPSED=0
REASON=""
while :; do
    ELAPSED=$((SECONDS - START))
    if [ -n "$DURATION" ] && [ "$ELAPSED" -gt "$DURATION" ]; then
        ELAPSED=$DURATION # never display or report past the target
    fi
    printf "\r  ⏱  Running for: %s" "$(format_time "$ELAPSED")"

    if [ -n "$DURATION" ] && [ "$ELAPSED" -ge "$DURATION" ]; then
        REASON="done"
        break
    fi
    # caffeinate should outlive the target; if it is gone, something killed it.
    if ! kill -0 "$CAFFEINATE_PID" 2>/dev/null; then
        REASON="early"
        break
    fi
    sleep 1
done

kill "$CAFFEINATE_PID" 2>/dev/null # release the assertions

if [ "$REASON" = "done" ]; then
    print_footer "Done — ran for" "$ELAPSED"
else
    print_footer "Stopped early, caffeinate exited — ran for" "$ELAPSED"
fi
