"""Create a self-contained report project and typeset it with Pandoc."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

_TEMPLATES = Path(__file__).with_name("templates")


def _blank_manuscript(title: str | None, author: str | None) -> str:
    metadata = {"title": "Untitled report" if title is None else title}
    if author is not None:
        metadata["author"] = author
    lines = ["---"]
    for key, value in metadata.items():
        if not value.strip():
            raise ValueError(f"The {key} must contain text.")
        # JSON-quoted strings are valid YAML scalars, including colons and quotes.
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    # A blank report opens on the illustrated cover, like the worked example.
    lines.append("folio-cover-image: cover.jpg")
    return "\n".join([*lines, "---", "", ""])


def new(
    directory: Path,
    *,
    blank: bool = False,
    title: str | None = None,
    author: str | None = None,
) -> Path:
    """Create an editable report project from a worked example or a blank manuscript.

    Parameters
    ----------
    directory : Path
        New project directory. An existing directory is never reused.
    blank : bool
        Start with a title, the cover and an empty manuscript body.
    title : str or None
        Title for a blank manuscript. Providing a title selects the blank starter.
        Defaults to "Untitled report" for a blank manuscript.
    author : str or None
        Optional byline for a blank manuscript. Providing an author also selects
        the blank starter.

    Returns
    -------
    Path
        Absolute path to the project.
    """
    directory = directory.absolute()
    if directory.exists() or directory.is_symlink():
        raise FileExistsError(f"Destination already exists: {directory}")
    directory.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=directory.parent) as temporary:
        staged = Path(temporary) / "project"
        shutil.copytree(_TEMPLATES / "common", staged)
        if blank or title is not None or author is not None:
            for name in ("layout.tex", "cover.jpg"):
                shutil.copy2(_TEMPLATES / "outlook" / name, staged)
            (staged / "report.md").write_text(
                _blank_manuscript(title, author), encoding="utf-8"
            )
        else:
            shutil.copytree(_TEMPLATES / "outlook", staged, dirs_exist_ok=True)
        # A reader sees the entire report at once. Concurrent generators publish
        # nonempty directories, so a later rename cannot overwrite a winner.
        staged.rename(directory)
    return directory


def _typeset(source: Path, project: Path) -> None:
    """Typeset a LaTeX file beside itself and print the layout faults in its log."""
    # Typeset the LaTeX here, not inside Pandoc, to keep the engine's log.
    typeset = [
        "tectonic",
        "--keep-logs",
        "--chatter=minimal",
        f"--outdir={source.parent}",
        "-Z",
        f"search-path={project}",
        str(source),
    ]
    done = subprocess.run(  # noqa: S603 - fixed argv, no shell
        typeset, cwd=project, check=False, capture_output=True, text=True
    )
    if done.returncode:
        # The engine's own account of an error is the useful one.
        sys.stderr.write(done.stdout + done.stderr)
        raise subprocess.CalledProcessError(done.returncode, typeset)
    log = source.with_suffix(".log")
    if log.is_file():
        for message in layout_warnings(log.read_text(errors="replace")):
            print(f"warning: {message}", file=sys.stderr)


def build(
    directory: Path, output: Path | None = None, *, style: str | None = None
) -> Path:
    """Render a PDF or export its standalone LaTeX source.

    Parameters
    ----------
    directory : Path
        A project containing report.md and folio.yaml.
    output : Path or None
        Output PDF or TeX file. Defaults to report.pdf beside the source.
        An explicit relative path resolves from the caller's working directory.
    style : str or None
        Preview a style from an older project's local styles directory.

    Returns
    -------
    Path
        Absolute path to the completed file.
    """
    project = directory.resolve()
    for required in ("report.md", "folio.yaml"):
        if not (project / required).is_file():
            raise FileNotFoundError(f"Missing {required} in {project}")
    if style is not None and (
        re.fullmatch(r"[a-z][a-z0-9-]*", style) is None
        or not (project / "styles" / f"{style}.tex").is_file()
    ):
        raise ValueError(
            f"Style {style!r} is unavailable in this project's styles directory."
        )
    target = output.resolve() if output is not None else project / "report.pdf"
    if target.suffix not in {".pdf", ".tex"}:
        raise ValueError("Choose a PDF (.pdf) or LaTeX (.tex) output file.")
    if target in {
        project / name
        for name in ("style.tex", "layout.tex", "components.tex", "east-room.tex")
    } or target.is_relative_to(project / "styles"):
        raise ValueError("Choose an export filename other than the project templates.")
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=target.parent) as temporary:
        rendered = Path(temporary) / target.name
        source = rendered.with_suffix(".tex")
        command = [
            "pandoc",
            "--defaults=folio.yaml",
            "report.md",
            "--output",
            str(source),
        ]
        if style is not None:
            command.append(f"--metadata=folio-style-preview:{style}")
        # Resolve bibliography and figures from the project, wherever the caller is.
        subprocess.run(command, cwd=project, check=True)  # noqa: S603 - fixed argv, no shell
        if target.suffix == ".pdf":
            _typeset(source, project)
        rendered.replace(target)
    return target


_FONT = re.compile(r"\\[A-Za-z0-9]+/[^ ]* ")
_LOOSE = re.compile(
    r"Underfull \\hbox \(badness (\d+)\) in paragraph at lines \d+--\d+\n([^\n]*)"
)
_WIDE = re.compile(
    r"Overfull \\hbox \(([\d.]+)pt too wide\) in paragraph at lines \d+--\d+\n([^\n]*)"
)
_TALL = re.compile(r"Overfull \\vbox \(([\d.]+)pt too high\)")
_FOLIO = re.compile(r"Package Folio Warning: (.*?)\n\n", re.DOTALL)


def _words(line: str) -> str:
    """Return the words of a line as the TeX log prints it."""
    text = _FONT.sub("", line).replace("[]", "").replace("\\-", "").replace("|", "")
    return " ".join(text.split())


def layout_warnings(log: str) -> list[str]:
    """Collect the layout faults an author should fix from a TeX log.

    Parameters
    ----------
    log : str
        Text of the engine's log for one build.

    Returns
    -------
    list of str
        One message for each loose justified line, line or page that overflows,
        and warning raised by the Folio templates, in the order they first occur.
        A fault repeated across the engine's passes is reported once.
    """
    found: list[str] = []
    for badness, line in _LOOSE.findall(log):
        found.append(
            f"loose line (badness {badness}); reword or shorten near: {_words(line)}"
        )
    for excess, line in _WIDE.findall(log):
        if float(excess) >= 1:
            found.append(f"line {excess}pt too wide near: {_words(line)}")
    found.extend(
        f"a column or page is {excess}pt too tall"
        for excess in _TALL.findall(log)
        if float(excess) >= 1
    )
    for message in _FOLIO.findall(log):
        # The log wraps at a fixed width and marks each continued line of a warning.
        text = re.sub(r"\n\(Folio\)\s+", " ", message).replace("\n", "")
        found.append(text)
    return list(dict.fromkeys(found))
