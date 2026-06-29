"""
Template script to calculate new working maxes for The Juggernaut Method™
weightlifting program.

Usage instructions:
- Copy this file `cp my_maxes.template.py my_maxes.py`.
  - `my_maxes.py` is git-ignored.
- Edit `my_maxes.py` to have non-zero values for lift variables.
- Run `python my_maxes.py` to calculate new working maxes.

This template file should not contain any actual values. Requires Python 3.10+.
"""

from juggernaut import Lift, calculate_new_working_max


def calculate_current_maxes():
    # Standard reps per wave: 10, 8, 5, 3
    standard_reps = 3

    calc_bench = True
    calc_squat = True
    calc_press = True
    calc_dead = True

    if calc_bench:
        bench_working_max = 0
        bench_reps_performed = 0
        bench_last_set_weight = 0
        calculate_new_working_max(
            Lift.BENCH,
            standard_reps,
            bench_working_max,
            bench_reps_performed,
            bench_last_set_weight,
        )

    if calc_squat:
        squat_working_max = 0
        squat_reps_performed = 0
        squat_last_set_weight = 0
        calculate_new_working_max(
            Lift.SQUAT,
            standard_reps,
            squat_working_max,
            squat_reps_performed,
            squat_last_set_weight,
        )

    if calc_press:
        press_working_max = 0
        press_reps_performed = 0
        press_last_set_weight = 0
        calculate_new_working_max(
            Lift.PRESS,
            standard_reps,
            press_working_max,
            press_reps_performed,
            press_last_set_weight,
        )

    if calc_dead:
        dead_working_max = 0
        dead_reps_performed = 0
        dead_last_set_weight = 0
        calculate_new_working_max(
            Lift.DEAD,
            standard_reps,
            dead_working_max,
            dead_reps_performed,
            dead_last_set_weight,
        )


if __name__ == "__main__":
    # TODO: delete this print statement.
    print(
        "This template script should not be run directly. Run `python my_maxes.py` instead."
    )
    # TODO: uncomment this line.
    # calculate_current_maxes()
