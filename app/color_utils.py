"""Pure, testable color utilities. RGB distance follows SRS Sections 2.7 and 4.3."""
import math
import re


def validate_rgb(*components):
    if len(components) != 3:
        raise ValueError("Enter exactly three RGB integers.")
    values = []
    for component in components:
        if isinstance(component, bool) or not re.fullmatch(r"[+-]?\d+", str(component).strip(), re.ASCII):
            raise ValueError("RGB components must be integers from 0 through 255.")
        value = int(component)
        if not 0 <= value <= 255:
            raise ValueError("RGB components must be integers from 0 through 255.")
        values.append(value)
    return tuple(values)


def hex_to_rgb(value):
    normalized = value.strip().removeprefix("#")
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", normalized):
        raise ValueError("Enter exactly 6 hexadecimal digits, optionally beginning with #.")
    return tuple(int(normalized[index:index + 2], 16) for index in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*validate_rgb(*rgb))


def rgb_distance(first, second):
    return math.sqrt(sum((left - right) ** 2 for left, right in zip(first, second)))


def rank_closest(source_rgb, paints, count):
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("Number of results must be a positive integer.")
    ranked = [(paint, rgb_distance(source_rgb, paint.rgb)) for paint in paints]
    return sorted(ranked, key=lambda pair: (pair[1], pair[0].id))[:count]


def format_timing(milliseconds):
    # Preserve tiny nonzero measurements instead of rounding them to fake zeroes.
    return f"{milliseconds:.4f}" if milliseconds >= 0.0001 else f"{milliseconds:.3g}"
