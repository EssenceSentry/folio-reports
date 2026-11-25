"""Create a self-contained report project and typeset it with Pandoc."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
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
        Start with a title and an empty manuscript body. Omit example assets.
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
            shutil.copy2(_TEMPLATES / "outlook" / "layout.tex", staged)
            (staged / "report.md").write_text(
                _blank_manuscript(title, author), encoding="utf-8"
            )
        else:
            shutil.copytree(_TEMPLATES / "outlook", staged, dirs_exist_ok=True)
        # A reader sees the entire report at once. Concurrent generators publish
        # nonempty directories, so a later rename cannot overwrite a winner.
        staged.rename(directory)
    return directory


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
        command = [
            "pandoc",
            "--defaults=folio.yaml",
            "report.md",
            "--output",
            str(rendered),
        ]
        if style is not None:
            command.append(f"--metadata=folio-style-preview:{style}")
        # Resolve bibliography and figures from the project, wherever the caller is.
        subprocess.run(command, cwd=project, check=True)  # noqa: S603 - fixed argv, no shell
        rendered.replace(target)
    return target
