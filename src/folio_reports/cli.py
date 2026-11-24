"""Command-line entry point for report authors."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from folio_reports import __version__
from folio_reports.core import LAYOUTS, build, new


def main(argv: Sequence[str] | None = None) -> int:
    """Create a report project or render its source.

    Parameters
    ----------
    argv : Sequence[str] or None
        Arguments without the program name. Defaults to the process arguments.

    Returns
    -------
    int
        Zero on success or two on a project or toolchain error.
    """
    parser = argparse.ArgumentParser(prog="folio-reports", description=__doc__)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("new", help="copy an editable report starter")
    create.add_argument("layout", choices=LAYOUTS)
    create.add_argument("directory", type=Path)
    render = commands.add_parser("build", help="typeset the PDF or export LaTeX")
    render.add_argument("directory", type=Path, default=Path.cwd(), nargs="?")
    render.add_argument("-o", "--output", type=Path, help="output .pdf or .tex path")
    args = parser.parse_args(argv)
    try:
        if args.command == "new":
            result = new(args.layout, args.directory)
        else:
            result = build(args.directory, args.output)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(result)
    return 0
