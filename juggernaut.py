"""
Script to use with Juggernaut workout method to calculate new working maxes

Significant changes done to this script should be reflected on:
https://gist.github.com/izzygomez/86be40a6c7e5efcc97e613f1d08b9c5b
"""

from enum import Enum


class Lift(Enum):
    BENCH = 1
    SQUAT = 2
    PRESS = 3
    DEAD = 4


# From https://stackoverflow.com/a/17303428
class format:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def lift_to_string(lift):
    match lift:
        case Lift.BENCH:
            return "Bench Press"
        case Lift.SQUAT:
            return "Squat"
        case Lift.PRESS:
            return "Shoulder Press"
        case Lift.DEAD:
            return "Deadlift"


# Good resources on topic of 1RM:
#  - https://en.wikipedia.org/wiki/One-repetition_maximum
#  - https://observablehq.com/@mourner/one-rep-max-formulas-showdown
#  - https://www.athlegan.com/calculate-1rm


def calc_1rm_epley(weight, reps):
    return weight * (1 + (reps / 30.0))


def calc_1rm_brzycki(weight, reps):
    return weight * (36.0 / (37 - reps))


def calculate_new_working_max(
    lift, standard_reps, working_max, reps_performed, last_set_weight
):
    """Calculate new working max.

    Args:
        lift: Enum indicating lift.
        standard_reps: Standard reps in current wave that was just completed.
        working_max: Working max in current wave that was just completed.
        reps_performed: Reps performed in last AMAP set in the Realization phase.
        last_set_weight: Weight used in last AMAP set in the Realization phase.
    """
    # Note: choosing to use Epley formula since it's a bit more optimistic (i.e.
    # higher vals) than Brzycki, but this can be adjusted later if needed.
    projected_max = calc_1rm_epley(last_set_weight, reps_performed)

    # cap extra reps to at most 10
    extra_reps = min(reps_performed - standard_reps, 10)
    # TODO: figure out what to do if extra_reps < 0, i.e. failed last set

    if lift == Lift.BENCH or lift == Lift.PRESS:
        big_increment = 2.5
        small_increment = 1.25
    elif lift == Lift.SQUAT or lift == Lift.DEAD:
        big_increment = 5.0
        small_increment = 2.5
    else:
        print("Invalid `lift` passed into calculate_new_working_max")
        return

    big_working_max = working_max + extra_reps * big_increment
    small_working_max = working_max + extra_reps * small_increment

    # As a general rule of thumb, we want the new working max to stay 5-10%
    # below the project max. We therefore calculate the ratio between the
    # projected max & the big working max & ensure the percentage difference is
    # not less than 5%.
    big_percentage_diff = projected_max / big_working_max
    small_percentage_diff = projected_max / small_working_max
    # see https://stackoverflow.com/a/8885688 for formatting syntax
    big_diff_string = "{:.2f}".format((big_percentage_diff - 1.0) * 100) + "%"
    small_diff_string = "{:.2f}".format((small_percentage_diff - 1.0) * 100) + "%"
    if big_percentage_diff >= 1.05:
        new_working_max = big_working_max
        chosen_increment = big_increment
        chosen_increment_string = "big"
        diff_string = big_diff_string
    else:
        new_working_max = small_working_max
        chosen_increment = small_increment
        chosen_increment_string = "small"
        diff_string = small_diff_string

    # printssss
    print("%s%s:%s" % (format.BOLD, lift_to_string(lift), format.END))
    print(
        "• New working max is %s%s%.2f lbs%s."
        % (format.GREEN, format.BOLD, new_working_max, format.END)
    )
    print(
        "• We used the %s%.2f lbs%s %s-increment to increase the %s%.2f lb%s old working max with %s%d%s extra reps."
        % (
            format.CYAN,
            chosen_increment,
            format.END,
            chosen_increment_string,
            format.RED,
            working_max,
            format.END,
            format.CYAN,
            extra_reps,
            format.END,
        )
    )
    print(
        "\t• i.e. did %d reps on last set attempt of %d lbs for %d reps."
        % (reps_performed, last_set_weight, standard_reps)
    )
    print(
        "• The percentage difference between the new %s%d%s working max & the %s%0.2f%s projected max is %s%s%s.\n"
        % (
            format.GREEN,
            new_working_max,
            format.END,
            format.PURPLE,
            projected_max,
            format.END,
            format.BOLD,
            diff_string,
            format.END,
        )
    )


# Calculate new working maxes
standard_reps = 8

bench_working_max = 220
bench_reps_performed = None
bench_last_set_weight = None

squat_working_max = 315
squat_reps_performed = None
squat_last_set_weight = None

press_working_max = 108
press_reps_performed = None
press_last_set_weight = None

dead_working_max = 342
dead_reps_performed = None
dead_last_set_weight = None


calculate_new_working_max(
    Lift.BENCH,
    standard_reps,
    bench_working_max,
    bench_reps_performed,
    bench_last_set_weight,
)
calculate_new_working_max(
    Lift.SQUAT,
    standard_reps,
    squat_working_max,
    squat_reps_performed,
    squat_last_set_weight,
)
calculate_new_working_max(
    Lift.PRESS,
    standard_reps,
    press_working_max,
    press_reps_performed,
    press_last_set_weight,
)
calculate_new_working_max(
    Lift.DEAD,
    standard_reps,
    dead_working_max,
    dead_reps_performed,
    dead_last_set_weight,
)
