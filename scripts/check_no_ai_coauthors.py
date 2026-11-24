"""Reject commit messages that credit an AI assistant as a co-author.

Runs as a commit-msg hook on the message file, or over a range of commits:

    python scripts/check_no_ai_coauthors.py .git/COMMIT_EDITMSG
    python scripts/check_no_ai_coauthors.py --range origin/main..HEAD
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

AI_CREDIT = re.compile(
    r"^\s*co-authored-by:.*\b(claude|anthropic|copilot|openai|chatgpt|codex|gemini)\b"
    r"|generated with \[?claude",
    re.IGNORECASE,
)


def offending_lines(message: str) -> list[str]:
    """Return the lines of a commit message that credit an AI assistant.

    Parameters
    ----------
    message : str
        A full commit message.

    Returns
    -------
    list[str]
        The offending lines, stripped; empty when the message is clean.
    """
    return [line.strip() for line in message.splitlines() if AI_CREDIT.search(line)]


def range_messages(revision_range: str) -> dict[str, str]:
    """Read the message of every commit in a revision range.

    Parameters
    ----------
    revision_range : str
        A git revision range such as ``origin/main..HEAD``.

    Returns
    -------
    dict[str, str]
        Commit messages keyed by abbreviated commit hash.
    """
    output = subprocess.run(
        ["git", "log", "--format=%H%x00%B%x01", revision_range],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    messages: dict[str, str] = {}
    for record in output.split("\x01"):
        if "\x00" in record:
            commit, body = record.strip("\n").split("\x00", 1)
            messages[commit[:12]] = body
    return messages


def main(argv: list[str] | None = None) -> int:
    """Check one message file or a range of commits.

    Parameters
    ----------
    argv : list[str] or None
        Arguments without the program name; ``None`` reads ``sys.argv``.

    Returns
    -------
    int
        0 when no message credits an AI assistant, 1 otherwise.
    """
    parser = argparse.ArgumentParser(description="Reject AI co-author credits.")
    parser.add_argument("message_file", nargs="?", type=Path)
    parser.add_argument("--range", dest="revision_range")
    args = parser.parse_args(argv)
    if args.revision_range:
        messages = range_messages(args.revision_range)
    elif args.message_file:
        text = args.message_file.read_text(encoding="utf-8")
        messages = {str(args.message_file): text}
    else:
        parser.error("give a commit message file or --range")
    found = {
        source: lines
        for source, message in messages.items()
        if (lines := offending_lines(message))
    }
    for source, lines in found.items():
        for line in lines:
            print(f"{source}: {line}", file=sys.stderr)
    if found:
        print("Remove AI co-author credits from these messages.", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
