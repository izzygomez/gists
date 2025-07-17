"""
Sum multiple time values provided as command line arguments.

Accepts time strings in various formats:
- Seconds only: "45"
- Minutes:seconds: "13:45"
- Hours:minutes:seconds: "1:22:57"

Outputs the total time in H:MM:SS format.

Usage:
    python time_sum.py <time1> <time2> [time3] ...
    python time_sum.py 13 13:14 1:22:57

Examples:
    python time_sum.py 30 45        # 30s + 45s = 0:01:15
    python time_sum.py 5:30 2:45    # 5m30s + 2m45s = 0:08:15
    python time_sum.py 1:30:00 45:30 15  # 1h30m + 45m30s + 15s = 2:15:45

Any changes done to this script should be reflected on:
TODO insert link here
"""

import sys
from datetime import timedelta


def parse_time_string(s):
    parts = list(map(int, s.split(":")))
    if len(parts) == 1:
        return timedelta(seconds=parts[0])
    elif len(parts) == 2:
        return timedelta(minutes=parts[0], seconds=parts[1])
    elif len(parts) == 3:
        return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
    else:
        raise ValueError(f"Invalid time string: {s}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python sum_times.py 13 13:14 1:22:57")
        sys.exit(1)

    total = timedelta()
    for time_str in sys.argv[1:]:
        total += parse_time_string(time_str)

    # Format output as H:MM:SS (no leading zeros)
    total_seconds = int(total.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    print(f"{hours}:{minutes:02}:{seconds:02}")


if __name__ == "__main__":
    main()
