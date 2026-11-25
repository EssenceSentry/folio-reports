"""Compare role-based type scales and export print specs, CSS, Tailwind v4 or JSON."""

import argparse
import json
import math
import sys


def positive(text):
    """Read a positive finite number."""
    value = float(text)
    if not math.isfinite(value) or value <= 0:
        raise argparse.ArgumentTypeError("expected a positive finite number")
    return value


def steps_for(args, ratio):
    """Keep the body fixed while deriving display, text and small-type steps."""
    roles = {
        0: "body",
        -1: "small",
        -2: "label",
        -3: "micro",
        1: "lede",
        2: "subhead",
        3: "heading",
        4: "title",
        5: "display",
        6: "display-large",
    }
    steps = []
    for step in range(-args.down, args.up + 1):
        row = {"step": step, "role": roles[step]}
        for suffix, base, up in (
            ("", args.base, ratio),
            ("_max", args.base_max, args.ratio_max or ratio),
        ):
            if base is None:
                continue
            size = base * (args.ratio_down if step < 0 else up) ** step
            multiplier = (
                args.leading if step <= 0 else max(1.08, args.leading - step * 0.065)
            )
            leading = size * multiplier
            if args.grid:
                unit = args.grid if step <= 0 else args.grid / 2
                leading = (
                    max(math.ceil(1.05 * size / unit), round(leading / unit)) * unit
                )
            row["size" + suffix], row["leading" + suffix] = (
                round(size, 3),
                round(leading, 3),
            )
        relative = row["size"] / args.base
        row["tracking_em"] = next(
            (
                value
                for threshold, value in ((4, -0.03), (2.5, -0.02), (1.6, -0.01))
                if relative >= threshold
            ),
            0.0,
        )
        steps.append(row)
    return steps


def web_value(lo, hi, narrow, wide):
    """Interpolate between two endpoints with zoom-aware rem bounds and intercept."""
    if lo == hi:
        return f"{lo / 16:.5g}rem"
    slope = (hi - lo) / (wide - narrow)
    return (
        f"clamp({min(lo, hi) / 16:.5g}rem, calc({(lo - narrow * slope) / 16:.5g}rem "
        f"+ {slope * 100:.5g}vw), {max(lo, hi) / 16:.5g}rem)"
    )


def emit(scale, args):
    """Print a scale in the requested authoring format."""
    rows = scale["steps"]
    if args.format == "spec":
        unit = "pt" if args.medium == "print" else "px"
        print(f"Ratio {scale['ratio']:g} · size / baseline spacing ({unit})")
        for r in rows:
            wide = (
                f" → {r['size_max']:g}/{r['leading_max']:g}" if "size_max" in r else ""
            )
            print(
                f"{r['role']:14} {r['size']:g}/{r['leading']:g}{wide}"
                f"  tracking {r['tracking_em']:g} em"
            )
        print(
            "Heading roles:",
            ", ".join(f"{name} = {role}" for name, role in scale["headings"].items()),
        )
        return
    tailwind = args.format == "tailwind"
    print("@theme {" if tailwind else ":root {")
    for r in rows:
        size = web_value(r["size"], r.get("size_max", r["size"]), *args.viewports)
        leading = web_value(
            r["leading"], r.get("leading_max", r["leading"]), *args.viewports
        )
        print(f"  --text-{r['role']}: {size};")
        suffix = "--line-height" if tailwind else "-leading"
        print(f"  --text-{r['role']}{suffix}: {leading};")
        tracking = "--letter-spacing" if tailwind else "-tracking"
        print(f"  --text-{r['role']}{tracking}: {r['tracking_em']:g}em;")
    print("}")
    for name, role in scale["headings"].items():
        print(
            f":where({name}) {{ font-size: var(--text-{role}); "
            f"line-height: var(--text-{role}{suffix}); "
            f"letter-spacing: var(--text-{role}{tracking}); }}"
        )
    if args.k is not None:
        print(".type-baseline {")
        print(f"  --grid: {args.grid / 16:g}rem;")
        print(f"  --first-baseline: calc(0.5lh + {args.k:g}em);")
        print("  position: relative;")
        print(
            "  top: calc(round(nearest, var(--first-baseline), var(--grid))"
            " - var(--first-baseline));"
        )
        print("}")


def describe_scale(args, ratio):
    """Associate actual steps with heading levels and flag roles needing a proof."""
    rows = steps_for(args, ratio)
    levels = [row["role"] for row in reversed(rows) if row["step"] > 0]
    if len(levels) == 6:
        levels = levels[1:]
    headings = {f"h{i + 1}": role for i, role in enumerate((levels + ["body"] * 6)[:6])}
    notes = []
    if ratio < 1.15:
        notes.append("Compare adjacent heading levels using weight and spacing.")
    small_floor = 12 if args.medium == "web" else 6
    if rows[0]["size"] < small_floor:
        notes.append(
            f"Proof the smallest text at its intended distance ({rows[0]['size']:g})."
        )
    if any(r.get("size_max", r["size"]) > 2.5 * r["size"] for r in rows):
        notes.append("Proof the widest layout. At least one role grows over 2.5 times.")
    if args.grid and any(r["leading"] > 1.8 * r["size"] for r in rows):
        notes.append("Check loose snapped leading on labels that wrap.")
    for note in notes:
        print(f"Proof note: {note}", file=sys.stderr)
    return {"ratio": ratio, "medium": args.medium, "headings": headings, "steps": rows}


def main():
    """Generate scale alternatives for the author to compare."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--medium", choices=("print", "web"), default="print")
    parser.add_argument(
        "--base", type=positive, help="body size in points or CSS pixels"
    )
    parser.add_argument(
        "--base-max", type=positive, help="body size at the wider web viewport"
    )
    parser.add_argument(
        "--ratios", help="comma-separated ratios to compare, e.g. 1.2,1.25,1.333"
    )
    parser.add_argument(
        "--ratio-max", type=positive, help="optional wide-end web ratio"
    )
    parser.add_argument(
        "--ratio-down", type=positive, help="gentler steps below body size"
    )
    parser.add_argument(
        "--viewports", type=int, nargs=2, default=(375, 1280), metavar=("MIN", "MAX")
    )
    parser.add_argument(
        "--leading", type=positive, help="body line spacing as a multiple of size"
    )
    parser.add_argument(
        "--grid", type=positive, help="baseline unit; display sizes can use half steps"
    )
    parser.add_argument("--up", type=int, choices=range(7), default=4)
    parser.add_argument(
        "--k",
        type=float,
        help="optional (ascent - descent) / 2 per em for baseline CSS",
    )
    parser.add_argument("--down", type=int, choices=range(4), default=2)
    parser.add_argument(
        "--format", choices=("spec", "json", "css", "tailwind"), default="spec"
    )
    args = parser.parse_args()
    web = args.medium == "web"
    args.base = args.base or (18 if web else 11)
    args.leading = args.leading or (1.5 if web else 1.3)
    args.ratio_down = args.ratio_down or (1.125 if web else 1.1)
    if args.viewports[0] <= 0 or args.viewports[1] <= args.viewports[0]:
        parser.error("viewport widths must be positive and increasing")
    if not web and (
        args.base_max or args.ratio_max or args.format in ("css", "tailwind")
    ):
        parser.error("use --medium web for fluid sizes or CSS output")
    if args.ratio_max and not args.base_max:
        parser.error("--ratio-max needs --base-max (which may equal --base)")
    if args.k is not None and (
        not math.isfinite(args.k)
        or not args.grid
        or args.format not in ("css", "tailwind")
    ):
        parser.error(
            "--k needs a finite font metric, --grid, and web CSS or Tailwind output"
        )
    try:
        ratios = (
            [positive(s) for s in args.ratios.split(",")]
            if args.ratios
            else [1.25 if web else 1.2]
        )
    except (ValueError, argparse.ArgumentTypeError):
        parser.error("ratios must be comma-separated positive numbers")
    if min(*ratios, args.ratio_down, args.ratio_max or 2) <= 1:
        parser.error("scale ratios must exceed one")
    if len(ratios) > 1 and args.format in ("css", "tailwind"):
        parser.error("compare in JSON or spec first, then export the selected ratio")
    scales = [describe_scale(args, ratio) for ratio in ratios]
    if args.format == "json":
        print(json.dumps(scales, indent=2))
    else:
        for scale in scales:
            emit(scale, args)


if __name__ == "__main__":
    main()
