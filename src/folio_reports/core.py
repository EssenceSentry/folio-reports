"""Create a self-contained report project and typeset it with Pandoc."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

LAYOUTS = ("brief", "research")
_TEMPLATES = Path(__file__).with_name("templates")


def new(layout: str, directory: Path) -> Path:
    """Create a report with editable content, fonts, page layout and examples.

    Parameters
    ----------
    layout : str
        Either "brief" or "research".
    directory : Path
        New project directory. An existing directory is never reused.

    Returns
    -------
    Path
        Absolute path to the project.
    """
    if layout not in LAYOUTS:
        raise ValueError(
            f"Unknown layout {layout!r}. Choose from {', '.join(LAYOUTS)}."
        )
    directory = directory.absolute()
    if directory.exists() or directory.is_symlink():
        raise FileExistsError(f"Destination already exists: {directory}")
    directory.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=directory.parent) as temporary:
        staged = Path(temporary) / "project"
        shutil.copytree(_TEMPLATES / "common", staged)
        shutil.copytree(_TEMPLATES / layout, staged, dirs_exist_ok=True)
        # A reader sees the entire report at once. Concurrent generators publish
        # nonempty directories, so a later rename cannot overwrite a winner.
        staged.rename(directory)
    return directory


def build(directory: Path, output: Path | None = None) -> Path:
    """Render a PDF or export its standalone LaTeX source.

    Parameters
    ----------
    directory : Path
        A project containing report.md and folio.yaml.
    output : Path or None
        Output PDF or TeX file. Defaults to report.pdf beside the source.
        An explicit relative path resolves from the caller's working directory.

    Returns
    -------
    Path
        Absolute path to the completed file.
    """
    project = directory.resolve()
    for required in ("report.md", "folio.yaml"):
        if not (project / required).is_file():
            raise FileNotFoundError(f"Missing {required} in {project}")
    target = output.resolve() if output is not None else project / "report.pdf"
    if target.suffix not in {".pdf", ".tex"}:
        raise ValueError("Choose a PDF (.pdf) or LaTeX (.tex) output file.")
    if target.suffix == ".tex" and target in {
        project / "style.tex",
        project / "layout.tex",
    }:
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
        # Resolve bibliography and figures from the project, wherever the caller is.
        subprocess.run(command, cwd=project, check=True)  # noqa: S603 - fixed argv, no shell
        rendered.replace(target)
    return target
