#!/usr/bin/env python3.10
"""
Script to use with The Juggernaut Method™ weightlifting program to calculate new
working maxes.

Significant changes done to this script should be reflected on:
https://gist.github.com/izzygomez/86be40a6c7e5efcc97e613f1d08b9c5b
"""

from enum import Enum
import re
import sys
import textwrap


if sys.version_info < (3, 10):
    print("Error: This script requires at least Python 3.10 to run.")
    sys.exit(1)


class Lift(Enum):
    BENCH = 1
    SQUAT = 2
    PRESS = 3
    DEAD = 4


class WorkingMaxUpdateMethod(Enum):
    BIG_INCREMENT = 1
    SMALL_INCREMENT = 2
    STAY_SAME = 3
    FORCE_PERCENTAGE_DIFF = 4


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


def diff_to_string(diff):
    # See https://stackoverflow.com/a/8885688 for formatting syntax
    return "{:.2f}".format((diff - 1.0) * 100) + "%"


def update_method_to_increment_string(update_method):
    match update_method:
        case WorkingMaxUpdateMethod.BIG_INCREMENT:
            return "big-increment"
        case WorkingMaxUpdateMethod.SMALL_INCREMENT:
            return "small-increment"
        case _:
            return "ERROR"


def round_to_base(x, base=2.5, prec=2):
    """Round to nearest multiple of base.

    Args:
        x: Number to round.
        base: Base to round to.
        prec: Precision to round to. Defaults to 2.
    """
    return round(base * round(float(x) / base), prec)


def wrap_text_with_new_lines(paragraphs, max_line_len):
    """Wrap paragraphs of text with new lines using textwrap.

    Args:
        paragraphs: List of paragraphs to wrap. Each paragraph is a string.
                    Strings should not contain "^" character; see note below.
        max_line_len: Max line length to wrap to.

    Note: this function was created using ChatGPT so might be a bit convoluted,
    but the general idea is to extract ANSI codes (i.e. color codes) from the
    paragraphs, wrap the paragraphs, then reinsert the ANSI codes. This is done
    since textwrap doesn't handle ANSI codes well (i.e. it doesn't know that the
    codes shouldn't be counted towards the max line length), so we temporarily
    replace the ANSI codes with a placeholder character "^" before wrapping the
    text. This is why the paragraphs should not contain the "^" character.
    """
    blank_char = " "
    wrapped_paragraphs = []

    for i in range(len(paragraphs)):
        paragraph = paragraphs[i]

        # Extract ANSI codes and replace them with placeholder "^"
        ansi_codes = []
        clean_paragraph = ""
        j = 0
        while j < len(paragraph):
            match = re.match(r"\033\[[0-9;]*[m]", paragraph[j:])
            if match:
                ansi_codes.append(match.group())
                clean_paragraph += "^"
                j += len(match.group())
            else:
                clean_paragraph += paragraph[j]
                j += 1

        # First line is special case since we don't want indentation.
        if i == 0:
            wrapped_text = textwrap.fill(clean_paragraph, width=max_line_len)
        else:  # Subsequent lines should use indentation
            wrapped_text = textwrap.fill(
                clean_paragraph,
                width=max_line_len,
                initial_indent=blank_char * 2,  # indent bullet points
                subsequent_indent=blank_char * 4,  # further indent when wrapped
            )

        # Reinsert the ANSI codes sequentially
        final_text = ""
        ansi_index = 0
        for char in wrapped_text:
            if char == "^":
                final_text += ansi_codes[ansi_index]
                ansi_index += 1
            else:
                final_text += char

        wrapped_paragraphs.append(final_text)

    return "\n".join(wrapped_paragraphs)


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

    # As a general rule of thumb, we want the new working max to stay at least
    # 5% below the projected max. We therefore calculate the ratio between the
    # projected max & the big/small working maxes & ensure the percentage
    # difference is not less than 5%. If both are less than 5% — i.e. neither
    # increment option will yield a sufficiently small working max relative to
    # the projected max - we first optimistically check if we can keep the
    # working max the same. If not, then we calculate the new working max by
    # forcing a 5% difference to the projected max (& round to nearest
    # multiple of small_increment).
    big_percentage_diff = projected_max / big_working_max
    small_percentage_diff = projected_max / small_working_max
    current_percentage_diff = projected_max / working_max
    if big_percentage_diff >= 1.05:
        new_working_max = big_working_max
        update_method = WorkingMaxUpdateMethod.BIG_INCREMENT
        chosen_increment = big_increment
        diff_string = diff_to_string(big_percentage_diff)
    elif small_percentage_diff >= 1.05:
        new_working_max = small_working_max
        update_method = WorkingMaxUpdateMethod.SMALL_INCREMENT
        chosen_increment = small_increment
        diff_string = diff_to_string(small_percentage_diff)
    elif current_percentage_diff >= 1.05:
        new_working_max = working_max
        update_method = WorkingMaxUpdateMethod.STAY_SAME
        chosen_increment = None
        diff_string = diff_to_string(current_percentage_diff)
    else:
        new_working_max = round_to_base(projected_max / 1.05, small_increment)
        # There is an edge case here where the new working max when forced to be
        # rounded to nearest multiple of small_increment is the same as the old
        # working max. This is equivalent to STAY_SAME, so we set update_method
        # accordingly.
        if new_working_max == working_max:
            update_method = WorkingMaxUpdateMethod.STAY_SAME
        else:
            update_method = WorkingMaxUpdateMethod.FORCE_PERCENTAGE_DIFF
        chosen_increment = None
        diff_string = diff_to_string(projected_max / new_working_max)

    # Prints
    paragraphs = []

    paragraphs.append(f"{format.BOLD}{lift_to_string(lift)}:{format.END}")
    paragraphs.append(
        f"• New working max is "
        f"{format.GREEN}{format.BOLD}{new_working_max:0.2f} lbs{format.END}."
    )

    if update_method == WorkingMaxUpdateMethod.STAY_SAME:
        paragraphs.append(
            f"• Both increment options were insufficient when updating the "
            f"{format.RED}{working_max:0.2f} lb{format.END} old working max "
            f"(with {format.CYAN}{extra_reps} extra reps{format.END}) to "
            f"stay >=5% under projected max, but the old working max stays "
            f"within bounds, so keeping it the same."
        )
    elif update_method == WorkingMaxUpdateMethod.FORCE_PERCENTAGE_DIFF:
        paragraphs.append(
            f"• Both increment options were insufficient when updating the "
            f"{format.RED}{working_max:0.2f} lb{format.END} old working max "
            f"(with {format.CYAN}{extra_reps} extra reps{format.END}) to "
            f"stay >=5% under projected max, & old working max does not stay "
            f"within bounds, so setting new working max to be ~5% under "
            f"(rounded to nearest "
            f"{format.CYAN}{small_increment:0.2f} lbs{format.END})."
        )
    else:
        paragraphs.append(
            f"• We used the "
            f"{format.CYAN}{chosen_increment:0.2f} lbs{format.END} "
            f"{update_method_to_increment_string(update_method)} to increase "
            f"the {format.RED}{working_max:0.2f} lb{format.END} old working "
            f"max (with {format.CYAN}{extra_reps} extra reps{format.END}), "
            f"i.e. did {format.CYAN}{reps_performed} reps{format.END} "
            f"on last set when attempting {format.CYAN}{standard_reps} "
            f"reps{format.END} of {format.CYAN}{last_set_weight} "
            f"lbs{format.END}."
        )

    paragraphs.append(
        f"• The percentage difference between the new "
        f"{format.GREEN}{new_working_max:0.2f} lbs{format.END} working max & "
        f"the {format.PURPLE}{projected_max:0.2f} lbs{format.END} projected "
        f"max is {format.BOLD}{diff_string}{format.END}."
    )

    print(wrap_text_with_new_lines(paragraphs, max_line_len=100), "\n")


def calculate_current_maxes():
    standard_reps = 5

    calc_bench = True
    calc_squat = True
    calc_press = True
    calc_dead = True

    if calc_bench:
        bench_working_max = 235
        bench_reps_performed = 7
        bench_last_set_weight = 200
        calculate_new_working_max(
            Lift.BENCH,
            standard_reps,
            bench_working_max,
            bench_reps_performed,
            bench_last_set_weight,
        )

    if calc_squat:
        squat_working_max = 362.5
        squat_reps_performed = 5
        squat_last_set_weight = 315
        calculate_new_working_max(
            Lift.SQUAT,
            standard_reps,
            squat_working_max,
            squat_reps_performed,
            squat_last_set_weight,
        )

    if calc_press:
        press_working_max = 123.75
        press_reps_performed = 8
        press_last_set_weight = 105
        calculate_new_working_max(
            Lift.PRESS,
            standard_reps,
            press_working_max,
            press_reps_performed,
            press_last_set_weight,
        )

    if calc_dead:
        dead_working_max = 397.5
        dead_reps_performed = 7
        dead_last_set_weight = 340
        calculate_new_working_max(
            Lift.DEAD,
            standard_reps,
            dead_working_max,
            dead_reps_performed,
            dead_last_set_weight,
        )


if __name__ == "__main__":
    calculate_current_maxes()
