"""
Script to use with Juggernaut workout method to calculate new working maxes

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


# https://en.wikipedia.org/wiki/One-repetition_maximum
def calc_1rm_epley(weight, reps):
    return weight * (1 + (reps / 30.0))


# https://en.wikipedia.org/wiki/One-repetition_maximum
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
    # higher vals) than Brzycki, but this can be adjusted later if increment
    # velocity brings about last set failure in any wave.
    projected_max = calc_1rm_epley(last_set_weight, reps_performed)

    # cap extra reps to at most 10
    extra_reps = min(reps_performed - standard_reps, 10)
    # TODO: figure out what to do if extra_reps < 0

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
    # see https://stackoverflow.com/a/8885688 for formatting syntax
    big_diff_string = "{:.2f}".format((big_percentage_diff - 1) * 100) + "%"
    if big_percentage_diff >= 1.05:
        new_working_max = big_working_max
        chosen_increment = big_increment
    else:
        new_working_max = small_working_max
        chosen_increment = small_increment

    # printssss
    print("%s%s:%s" % (format.BOLD, lift_to_string(lift), format.END))
    print(
        "\tNew working max is %s%s%d lbs%s."
        % (format.GREEN, format.BOLD, new_working_max, format.END)
    )
    print(
        "\tWe used the %s%.2f lbs%s increment to increase the old %s%d%s working max by %s%d%s extra reps."
        % (
            format.CYAN,
            chosen_increment,
            format.END,
            format.RED,
            working_max,
            format.END,
            format.CYAN,
            extra_reps,
            format.END,
        )
    )
    print(
        "\tThe percentage difference between the new %s%d%s working max & the %s%d%s projected max is %s%s%s.\n"
        % (
            format.GREEN,
            new_working_max,
            format.END,
            format.PURPLE,
            projected_max,
            format.END,
            format.BOLD,
            big_diff_string,
            format.END,
        )
    )


# Juggernaut calculations

standard_reps = 10

bench_working_max = 250
bench_reps_performed = 10
bench_last_set_weight = 185

squat_working_max = 325
squat_reps_performed = 12
squat_last_set_weight = 245

press_working_max = 125
press_reps_performed = 8
press_last_set_weight = 95

dead_working_max = 340
dead_reps_performed = 13
dead_last_set_weight = 255

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

"""
# testing 1RM calculations based on last Juggernaut cycle
bench_weight = 220
bench_reps = 4
squat_weight = 280
squat_reps = 6
press_weight = 110
press_reps = 4
dead_weight = 295
dead_reps = 7

print("%s1RM calculations from end of December lifts:%s" % (format.BOLD, format.END))

print("Bench 1RM (based on %dx%d):" % (bench_reps, bench_weight))
print(
    "\tEpley: %.2f\n\tBrzycki: %.2f\n"
    % (
        calc_1rm_epley(bench_weight, bench_reps),
        calc_1rm_brzycki(bench_weight, bench_reps),
    )
)

print("Squat 1RM (based on %dx%d):" % (squat_reps, squat_weight))
print(
    "\tEpley: %.2f\n\tBrzycki: %.2f\n"
    % (
        calc_1rm_epley(squat_weight, squat_reps),
        calc_1rm_brzycki(squat_weight, squat_reps),
    )
)

print("Press 1RM (based on %dx%d):" % (press_reps, press_weight))
print(
    "\tEpley: %.2f\n\tBrzycki: %.2f\n"
    % (
        calc_1rm_epley(press_weight, press_reps),
        calc_1rm_brzycki(press_weight, press_reps),
    )
)

print("Dead 1RM (based on %dx%d):" % (dead_reps, dead_weight))
print(
    "\tEpley: %.2f\n\tBrzycki: %.2f\n"
    % (calc_1rm_epley(dead_weight, dead_reps), calc_1rm_brzycki(dead_weight, dead_reps))
)

bench_weight = 185
bench_reps = 10
squat_weight = 245
squat_reps = 12
press_weight = 95
press_reps = 8
dead_weight = 255
dead_reps = 13

print("%s1RM calculations from end of January lifts:%s" % (format.BOLD, format.END))
print("Bench 1RM (based on %dx%d):" % (bench_reps, bench_weight))
print(
    "\tEpley: %.2f\n\tBrzycki: %.2f\n"
    % (
        calc_1rm_epley(bench_weight, bench_reps),
        calc_1rm_brzycki(bench_weight, bench_reps),
    )
)

print("Squat 1RM (based on %dx%d):" % (squat_reps, squat_weight))
print(
    "\tEpley: %.2f\n\tBrzycki: %.2f\n"
    % (
        calc_1rm_epley(squat_weight, squat_reps),
        calc_1rm_brzycki(squat_weight, squat_reps),
    )
)

print("Press 1RM (based on %dx%d):" % (press_reps, press_weight))
print(
    "\tEpley: %.2f\n\tBrzycki: %.2f\n"
    % (
        calc_1rm_epley(press_weight, press_reps),
        calc_1rm_brzycki(press_weight, press_reps),
    )
)

print("Dead 1RM (based on %dx%d):" % (dead_reps, dead_weight))
print(
    "\tEpley: %.2f\n\tBrzycki: %.2f\n"
    % (calc_1rm_epley(dead_weight, dead_reps), calc_1rm_brzycki(dead_weight, dead_reps))
)
"""
