"""Create a self-contained report project and typeset it with Pandoc."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

LAYOUTS = ("brief", "research", "specimen")
STYLES = {
    "classic": "Original Folio typography tailored to each starter.",
    "swiss": "Asymmetric grotesk headlines and a strong red rule.",
    "gazette": "A centered newspaper masthead and double rules.",
    "blueprint": "Cobalt drafting marks and monospaced annotations.",
    "fieldnotes": "Olive field-journal typography and an inset title.",
    "ledger": "A compact financial statement with ruled section labels.",
    "gallery": "Aubergine exhibition typography with generous open space.",
    "signal": "A high-contrast banner for operational decisions.",
    "monograph": "Quiet book typography, centered titles and small capitals.",
    "dispatch": "A navy correspondence header and a split title block.",
}
_TEMPLATES = Path(__file__).with_name("templates")


def new(layout: str, directory: Path, *, style: str = "classic") -> Path:
    """Create a report with editable content, fonts, page layout and examples.

    Parameters
    ----------
    layout : str
        A brief, research report or component specimen.
    directory : Path
        New project directory. An existing directory is never reused.
    style : str
        Persistent visual style for the project.

    Returns
    -------
    Path
        Absolute path to the project.
    """
    if layout not in LAYOUTS:
        raise ValueError(
            f"Unknown layout {layout!r}. Choose from {', '.join(LAYOUTS)}."
        )
    if style not in STYLES:
        raise ValueError(f"Unknown style {style!r}. Choose from {', '.join(STYLES)}.")
    directory = directory.absolute()
    if directory.exists() or directory.is_symlink():
        raise FileExistsError(f"Destination already exists: {directory}")
    directory.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=directory.parent) as temporary:
        staged = Path(temporary) / "project"
        shutil.copytree(_TEMPLATES / "common", staged)
        shutil.copytree(_TEMPLATES / layout, staged, dirs_exist_ok=True)
        defaults = staged / "folio.yaml"
        defaults.write_text(
            defaults.read_text().replace(
                "folio-style: classic", f"folio-style: {style}"
            )
        )
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
        Override the project style for this build only.

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
        style not in STYLES or not (project / "styles" / f"{style}.tex").is_file()
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
