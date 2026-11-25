"""Report Poppler's font, page and text evidence for a local PDF."""

import argparse
import json
import math
import os
import shutil
import statistics
import subprocess
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


def poppler(name, *arguments):
    """Run an installed Poppler executable and return its standard output."""
    binary = shutil.which(name)
    if binary is None:
        raise ValueError(f"Poppler executable {name} is missing from PATH")
    return subprocess.run(  # noqa: S603 - resolved Poppler binary, separate arguments
        [binary, *arguments],
        capture_output=True,
        check=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "LC_ALL": "C"},
    ).stdout


def region_arg(value):
    """Parse a page rectangle in PDF points measured from the top left."""
    try:
        x0, y0, x1, y1 = map(float, value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError("use x0,top,x1,bottom in points") from error
    if not all(map(math.isfinite, (x0, y0, x1, y1))) or x1 <= x0 or y1 <= y0:
        raise argparse.ArgumentTypeError("supply a finite rectangle with positive area")
    return x0, y0, x1, y1


def measure_page(page, area, show_lines):
    """Measure whole lines, keeping the columns separated by Poppler."""
    boxes, lengths, spacings, samples = [], [], [], []
    for block in page.findall(".//{*}block"):
        previous_top = None
        for line in block.findall("{*}line"):
            box = tuple(
                float(line.attrib[key]) for key in ("xMin", "yMin", "xMax", "yMax")
            )
            if area and not (
                area[0] <= box[0]
                and area[1] <= box[1]
                and box[2] <= area[2]
                and box[3] <= area[3]
            ):
                previous_top = None
                continue
            words = [word.text or "" for word in line.findall("{*}word")]
            if not words:
                continue
            sample = " ".join(words)
            lengths.append(len(sample))
            boxes.append(box)
            if show_lines:
                samples.append(sample)
            if previous_top is not None and box[1] > previous_top:
                spacings.append(box[1] - previous_top)
            previous_top = box[1]
    return {
        "lines": len(boxes),
        "characters_per_line": {
            "min": min(lengths),
            "median": statistics.median(lengths),
            "max": max(lengths),
        }
        if lengths
        else None,
        "ink_bounds_pt": [
            min(b[0] for b in boxes),
            min(b[1] for b in boxes),
            max(b[2] for b in boxes),
            max(b[3] for b in boxes),
        ]
        if boxes
        else None,
        "median_within_block_line_pitch_pt": round(statistics.median(spacings), 2)
        if spacings
        else None,
        **({"text_lines": samples} if show_lines else {}),
    }


def font_runs(pdf, first, last):
    """Count text runs per Poppler font family and nominal size for sampled pages."""
    xml = poppler(
        "pdftohtml",
        "-xml",
        "-i",
        "-zoom",
        "1",
        "-stdout",
        "-f",
        str(first),
        "-l",
        str(last),
        str(pdf),
    )
    tree = ET.fromstring(xml)  # noqa: S314 - XML is produced by local Poppler
    fonts = {
        f.get("id"): (f.get("family"), f.get("size")) for f in tree.iter("fontspec")
    }
    counts = Counter(
        fonts[t.get("font")] for t in tree.iter("text") if t.get("font") in fonts
    )
    return [
        {"family": family, "size_pt_approx": size, "runs": count}
        for (family, size), count in counts.most_common()
    ]


def main():
    """Print measured evidence as JSON, reporting missing optional tools explicitly."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--page", type=int, help="one 1-based page (default: first 20)")
    parser.add_argument(
        "--region", type=region_arg, help="x0,top,x1,bottom in PDF points"
    )
    parser.add_argument(
        "--show-lines",
        action="store_true",
        help="include local text for identifying roles",
    )
    args = parser.parse_args()
    pdf = args.pdf.resolve()
    if not pdf.is_file() or (args.page is not None and args.page < 1):
        parser.error("supply an existing file and a positive page number")
    first, last = (args.page, args.page) if args.page else (1, 20)
    try:
        xml = poppler(
            "pdftotext",
            "-bbox-layout",
            "-enc",
            "UTF-8",
            "-f",
            str(first),
            "-l",
            str(last),
            str(pdf),
            "-",
        )
        tree = ET.fromstring(xml)  # noqa: S314 - XML is produced by local Poppler
        pages = [
            {"page": i, **measure_page(p, args.region, args.show_lines)}
            for i, p in enumerate(tree.findall(".//{*}page"), first)
        ]
        if not pages:
            raise ValueError("the selected page range is empty")
        result = {"file": str(pdf), "pages": pages, "region_pt": args.region}
        for name, field, options in (
            ("pdfinfo", "document_info", ["-box", "-f", str(first), "-l", str(last)]),
            ("pdffonts", "embedded_fonts", []),
        ):
            result[field] = (
                poppler(name, *options, str(pdf)).strip()
                if shutil.which(name)
                else f"unavailable: {name}"
            )
        result["sample_font_runs"] = (
            font_runs(pdf, first, last)
            if shutil.which("pdftohtml")
            else "unavailable: pdftohtml"
        )
    except (ValueError, ET.ParseError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{getattr(error, 'stderr', None) or error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
