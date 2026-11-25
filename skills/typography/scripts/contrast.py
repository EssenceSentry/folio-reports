"""Measure WCAG contrast and the supplementary APCA-W3 0.0.98G Lc for sRGB colors."""

import argparse
import json
import math


def parse_color(text):
    """Accept CSS hex in short or long form, including an alpha channel."""
    value = text.removeprefix("#")
    if len(value) in (3, 4):
        value = "".join(c * 2 for c in value)
    if len(value) not in (6, 8) or any(
        c not in "0123456789abcdefABCDEF" for c in value
    ):
        raise argparse.ArgumentTypeError(
            "use a hexadecimal sRGB color, e.g. '#243549' or '#fff8'"
        )
    return (
        tuple(int(value[i : i + 2], 16) / 255 for i in range(0, 8, 2))
        if len(value) == 8
        else (*(int(value[i : i + 2], 16) / 255 for i in range(0, 6, 2)), 1.0)
    )


def composite(top, bottom):
    """Composite sRGB channels over an opaque backing color."""
    return tuple(top[i] * top[3] + bottom[i] * (1 - top[3]) for i in range(3))


def luminance(color):
    """Calculate WCAG 2 relative luminance from sRGB."""
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in color
    ]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722), strict=True))


def apca_y(color):
    """Calculate luminance with the APCA black soft clamp."""
    y = sum(
        a**2.4 * b
        for a, b in zip(color, (0.2126729, 0.7151522, 0.0721750), strict=True)
    )
    return y if y > 0.022 else y + (0.022 - y) ** 1.414


def lightness_contrast(ink, paper):
    """Calculate signed APCA Lc, retaining light-on-dark polarity."""
    fg, bg = apca_y(ink), apca_y(paper)
    if abs(fg - bg) < 0.0005:
        return 0.0
    if bg > fg:
        value = (bg**0.56 - fg**0.57) * 1.14
        return 0.0 if value < 0.1 else (value - 0.027) * 100
    value = (bg**0.65 - fg**0.62) * 1.14
    return 0.0 if value > -0.1 else (value + 0.027) * 100


def main():
    """Report contrast for the specified colors, size, and weight."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("foreground", type=parse_color)
    parser.add_argument("background", type=parse_color)
    parser.add_argument("--canvas", type=parse_color, default=parse_color("#fff"))
    parser.add_argument("--size", type=float, default=16, help="CSS pixels")
    parser.add_argument("--weight", type=float, default=400, help="CSS font weight")
    args = parser.parse_args()
    if (
        args.canvas[3] != 1
        or not math.isfinite(args.size)
        or args.size <= 0
        or not 1 <= args.weight <= 1000
    ):
        parser.error(
            "use an opaque canvas, positive finite size, and weight from 1 to 1000"
        )
    bg = composite(args.background, args.canvas)
    fg = composite(args.foreground, bg)
    values = sorted((luminance(fg) + 0.05, luminance(bg) + 0.05))
    ratio = values[1] / values[0]
    large = args.size >= 24 or (args.size >= 14 * 96 / 72 and args.weight >= 700)
    print(
        json.dumps(
            {
                "wcag_ratio": ratio,
                "large_text": large,
                "AA": ratio >= (3 if large else 4.5),
                "AAA": ratio >= (4.5 if large else 7),
                "apca_lc": round(lightness_contrast(fg, bg), 1),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
