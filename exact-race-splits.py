"""
Get precise average splits (min/mi) to complete various race distances in a
given time.

Usage:
    python exact-race-splits.py -t <time> -d <distance> 

Significant changes done to this script should be reflected on:
TODO
"""

import argparse
import re


def valid_time_format(value):
    pattern = re.compile(r"^(?:(\d{1,2}):)?([0-5]?\d):([0-5]?\d)$")
    if not pattern.match(value):
        raise argparse.ArgumentTypeError(
            f"Invalid time format: '{value}'. Expected 'HH:MM:SS' or 'MM:SS'."
        )
    return value


def _distance_to_miles(distance: str) -> float:
    # 1 mile is exactly 1,609.344 metres [1].
    # Therefore, 1 mile / 1.609344 =  0.621371192 mile/km
    # The half marathon distance is exactly 21.0975 km [2].
    # Marathon is obviously exactly double that [3].
    # [1] https://en.wikipedia.org/wiki/Mile
    # [2] https://en.wikipedia.org/wiki/Half_marathon
    # [3] https://en.wikipedia.org/wiki/Marathon
    miles_per_km = 0.621371192
    distance_to_miles = {
        "5k": 5 * miles_per_km,  # 3.10685596
        "10k": 10 * miles_per_km,  # 6.21371192
        "15k": 15 * miles_per_km,  # 9.32056788
        "10M": 10,
        "HM": 21.0975 * miles_per_km,  # 13.10937872322
        "FM": 42.195 * miles_per_km,  # 26.21875744644
    }
    return distance_to_miles[distance]


def _distance_to_string(distance: str) -> str:
    distance_to_string = {
        "5k": "5k",
        "10k": "10k",
        "15k": "15k",
        "10M": "10 mile",
        "HM": "half marathon",
        "FM": "marathon",
    }
    return distance_to_string[distance]


def print_precise_splits(time: str, distance: str):
    """
    Assumes inputs are well-formed & valid.
    """
    time_split = time.split(":")
    total_seconds = int(time_split[-1])
    time_str = "_"
    if len(time_split) == 3:
        total_seconds += int(time_split[0]) * 3600 + int(time_split[1]) * 60
        time_str = (
            f"{int(time_split[0])}hr {int(time_split[1])}min {int(time_split[2])}sec"
        )
    elif len(time_split) == 2:
        total_seconds += int(time_split[0]) * 60
        time_str = f"{time_split[0]}min {time_split[1]}sec"

    distance_miles = _distance_to_miles(distance)
    pace_seconds = total_seconds / distance_miles
    pace_minutes = pace_seconds // 60
    pace_seconds = pace_seconds % 60
    # print(
    #     f"debug:\n{distance_miles=}\n{total_seconds=}\n"
    #     f"{pace_minutes=}\n{pace_seconds=}\n"
    # )  # debug

    print(
        "You must run an average split of "
        f"{int(pace_minutes)} min {pace_seconds:.2f} sec per mile "
        f"to run a {_distance_to_string(distance)} race in {time_str}."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A script to print out precise average splits for various race distances in given time."
    )
    parser.add_argument(
        "-t",
        "--time",
        type=valid_time_format,
        help='Goal time ("HH:MM:SS" or "MM:SS")',
        required=True,
    )
    parser.add_argument(
        "-d",
        "--distance",
        type=str,
        choices=["5k", "10k", "15k", "10M", "HM", "FM"],
        help="Race distance (5k, 10k, 15k, 10M, HM, FM)",
        required=True,
    )

    args = parser.parse_args()
    print_precise_splits(args.time, args.distance)
