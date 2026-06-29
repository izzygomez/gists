"""
Script to use with The Juggernaut Method™ weightlifting program to calculate new
working maxes.

Requires Python 3.10+.
"""

from enum import Enum
import re
import textwrap


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


class style:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    BOLD = "\033[1m"
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
    return f"{(diff - 1.0) * 100:.2f}%"


def format_signed(val):
    if val >= 0:
        return f"{style.GREEN}+{val}{style.END}"
    else:
        return f"{style.RED}{val}{style.END}"


def round_down_to_base(x, base=2.5, prec=2):
    """Round down to the nearest multiple of base.

    Args:
        x: Number to round.
        base: Base to round down to. Defaults to 2.5.
        prec: Decimal precision of result. Defaults to 2.
    """
    return round(base * round(float(x) // base), prec)


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
    wrapped_paragraphs = []

    for i, paragraph in enumerate(paragraphs):
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
                initial_indent=" " * 2,  # indent bullet points
                subsequent_indent=" " * 4,  # further indent when wrapped
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
        reps_performed: Reps in last AMAP set in the realization phase.
        last_set_weight: Weight in last AMAP set in the realization phase.
    """
    # Note: choosing to use Epley formula since it's a bit more optimistic (i.e.
    # higher vals) than Brzycki, but this can be adjusted later if needed.
    projected_max = calc_1rm_epley(last_set_weight, reps_performed)

    # cap extra reps to at most 10
    # TODO: it's not clear how this should behave if
    # reps_performed < standard_reps or reps_performed == 0. Investigate & fix.
    extra_reps = min(reps_performed - standard_reps, 10)

    if lift == Lift.BENCH or lift == Lift.PRESS:
        big_increment = 2.5
        small_increment = 1.25
    else:  # lift == Lift.SQUAT or lift == Lift.DEAD
        big_increment = 5.0
        small_increment = 2.5

    big_wm = working_max + extra_reps * big_increment
    small_wm = working_max + extra_reps * small_increment

    # As a general rule of thumb, we want the new working max to stay at least
    # 5% below the projected max. We therefore calculate the ratio between the
    # projected max & the big/small working maxes & ensure the percentage
    # difference is not less than 5%. If both are less than 5% — i.e. neither
    # increment option will yield a sufficiently small working max relative to
    # the projected max - we first optimistically check if we can keep the
    # working max the same. If not, then we calculate the new working max by
    # forcing a 5% difference to the projected max (& round to nearest
    # multiple of small_increment).
    big_percentage_diff = projected_max / big_wm
    small_percentage_diff = projected_max / small_wm
    current_percentage_diff = projected_max / working_max
    if big_percentage_diff >= 1.05:
        new_wm = big_wm
        update_method = WorkingMaxUpdateMethod.BIG_INCREMENT
        diff_str = diff_to_string(big_percentage_diff)
    elif small_percentage_diff >= 1.05:
        new_wm = small_wm
        update_method = WorkingMaxUpdateMethod.SMALL_INCREMENT
        diff_str = diff_to_string(small_percentage_diff)
    elif current_percentage_diff >= 1.05:
        new_wm = working_max
        update_method = WorkingMaxUpdateMethod.STAY_SAME
        diff_str = diff_to_string(current_percentage_diff)
    else:
        new_wm = round_down_to_base(projected_max / 1.05, small_increment)
        # There is an edge case here where the new working max when forced to be
        # rounded to nearest multiple of small_increment is the same as the old
        # working max. This is equivalent to STAY_SAME, so we set update_method
        # accordingly.
        if new_wm == working_max:
            update_method = WorkingMaxUpdateMethod.STAY_SAME
        else:
            update_method = WorkingMaxUpdateMethod.FORCE_PERCENTAGE_DIFF
        diff_str = diff_to_string(projected_max / new_wm)

    # Prints
    paragraphs = []

    paragraphs.append(f"{style.BOLD}{lift_to_string(lift)}:{style.END}")

    old_wm_str = f"{style.RED}{working_max:0.2f} lbs{style.END}"
    new_wm_str = f"{style.GREEN}{style.BOLD}{new_wm:0.2f} lbs{style.END}"
    if update_method == WorkingMaxUpdateMethod.STAY_SAME:
        paragraphs.append(f"• Working max stays the same at {old_wm_str}.")
    elif update_method == WorkingMaxUpdateMethod.FORCE_PERCENTAGE_DIFF:
        paragraphs.append(
            f"• Decreasing working max from {old_wm_str} to {new_wm_str}."
        )
    else:
        paragraphs.append(
            f"• Increasing working max from {old_wm_str} to {new_wm_str}."
        )

    paragraphs.append(
        f"• Did {style.CYAN}{reps_performed} reps{style.END} on last AMAP "
        f"set of {style.CYAN}{standard_reps}x{last_set_weight} lbs{style.END} "
        f"({format_signed(extra_reps)})."
    )
    paragraphs.append(
        f"• New {new_wm_str} working max is {style.BOLD}{diff_str}{style.END} "
        f"below the {style.PURPLE}{projected_max:0.2f} lbs{style.END} "
        f"projected max."
    )

    print(wrap_text_with_new_lines(paragraphs, max_line_len=100), "\n")
