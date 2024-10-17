import argparse

import pandas as pd
from tabulate import tabulate

"""
Prints "HR Intensities for Standard Marathon Training Workouts" table from
"Advanced Marathoning" book by Pfitzinger & Douglas (Page 17, Table 1.2). Usage
described by `python pfitz_hr_ranges.py --help`.

Dependencies: `pip install pandas tabulate`
"""


def print_pfitz_hr_ranges(max_hr: int, resting_hr: int, table_type: str):
    hr_reserve = max_hr - resting_hr
    workouts_to_hr = {
        0: {
            "name": "V̇O2 max (5k pace)",
            "maximal_hr": [93, 95],
            "hr_reserve": [91, 94],
        },
        1: {
            "name": "Lactate threshold",
            "maximal_hr": [82, 91],
            "hr_reserve": [76, 88],
        },
        2: {"name": "Marathon Pace", "maximal_hr": [82, 88], "hr_reserve": [76, 84]},
        3: {
            "name": "Long / medium-long",
            "maximal_hr": [75, 84],
            "hr_reserve": [66, 78],
        },
        4: {"name": "General aerobic", "maximal_hr": [72, 81], "hr_reserve": [62, 75]},
        5: {"name": "Recovery", "maximal_hr": [0, 76], "hr_reserve": [0, 68]},
    }

    col1 = "Workouts"
    col2 = "Maximal HR ranges"
    col3 = "HR reserve ranges"
    table_data = {col1: [], col2: [], col3: []}

    for i in range(len(workouts_to_hr)):
        workout = workouts_to_hr[i]

        max_low = workout["maximal_hr"][0]
        max_high = workout["maximal_hr"][1]
        maximal_hr_s = f"{max_low}-{max_high}% => {max_hr*max_low/100:.1f}-{max_hr*max_high/100:.1f} ♥ BPM"

        res_low = workout["hr_reserve"][0]
        res_high = workout["hr_reserve"][1]
        hr_reserve_s = f"{res_low}-{res_high}% => {hr_reserve*res_low/100 + resting_hr:.1f}-{hr_reserve*res_high/100 + resting_hr:.1f} ♥ BPM"

        table_data[col1].append(workout["name"])
        table_data[col2].append(maximal_hr_s)
        table_data[col3].append(hr_reserve_s)

    df = pd.DataFrame(table_data)

    print("HR Intensities for Standard Marathon Training Workouts\n")
    print(
        f"Calculated with following values: max HR = {max_hr}, resting HR = {resting_hr}, HR reserve = max HR - resting HR = {hr_reserve}\n"
    )
    print(tabulate(df, headers="keys", tablefmt=table_type, showindex=False))


if __name__ == "__main__":
    default_max_hr = 194
    default_resting_hr = 50
    default_table_type = "plain"

    parser = argparse.ArgumentParser(
        description="A script to print out HR intensities table for Pfitz Advanced Marathon training programs"
    )
    parser.add_argument(
        "-m", "--max", type=int, help="Maximum HR", default=default_max_hr
    )
    parser.add_argument(
        "-r", "--resting", type=int, help="Resting HR", default=default_resting_hr
    )
    parser.add_argument(
        "-t",
        "--table",
        type=str,
        choices=["grid", "pipe", "html", "plain"],
        help="Table type from {grid, pipe, html, plain}",
    )

    args = parser.parse_args()
    max_hr = args.max
    resting_hr = args.resting
    table_type = args.table

    print_pfitz_hr_ranges(max_hr, resting_hr, table_type)
