import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from folio_reports.core import build, new


@pytest.mark.parametrize("layout", ["brief", "research"])
def test_new_is_self_contained(tmp_path: Path, layout: str) -> None:
    dest = tmp_path / "nested" / "report"
    new(layout, dest)
    for name in ["report.md", "folio.yaml", "style.tex", "layout.tex"]:
        assert (dest / name).is_file()
    (dest / "report.md").write_text("my edits")
    with pytest.raises(FileExistsError):
        new(layout, dest)
    assert (dest / "report.md").read_text() == "my edits"


def test_unknown_layout(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown"):
        new("invalid", tmp_path / "project")


def test_missing_source(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"report\.md"):
        build(tmp_path)


def test_failed_build_preserves_existing_pdf(tmp_path: Path) -> None:
    new("brief", tmp_path / "case")
    output = tmp_path / "case" / "report.pdf"
    output.write_bytes(b"old")
    with (
        patch(
            "folio_reports.core.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, ["pandoc"]),
        ),
        pytest.raises(subprocess.CalledProcessError),
    ):
        build(tmp_path / "case")
    assert output.read_bytes() == b"old"


def test_build_works_outside_report_directory(tmp_path: Path) -> None:
    project = tmp_path / "source files"
    new("brief", project)

    def render(args: list[str], *, cwd: Path, check: bool) -> None:
        assert cwd == project
        assert check
        Path(args[args.index("--output") + 1]).write_bytes(b"%PDF-example")

    with patch("folio_reports.core.subprocess.run", side_effect=render):
        output = build(project, tmp_path / "outputs" / "review.pdf")
    assert output.read_bytes().startswith(b"%PDF")


def test_reject_nondocument_output(tmp_path: Path) -> None:
    new("research", tmp_path / "case")
    with pytest.raises(ValueError, match="PDF"):
        build(tmp_path / "case", tmp_path / "case" / "report.md")


@pytest.mark.parametrize("layout", ["brief", "research", "specimen"])
def test_blank_project_keeps_design_and_omits_example_content(
    tmp_path: Path, layout: str
) -> None:
    example = new(layout, tmp_path / "example", style="gazette")
    project = new(layout, tmp_path / "draft", blank=True, style="gazette")
    resources = [
        "layout.tex",
        "folio.yaml",
        "blocks.lua",
        "style.tex",
        "components.tex",
    ]
    resources.extend(
        str(path.relative_to(example)) for path in (example / "styles").glob("*.tex")
    )
    assert {
        str(path.relative_to(project)): path.read_bytes()
        for path in project.rglob("*")
        if path.is_file() and path.name != "report.md"
    } == {name: (example / name).read_bytes() for name in resources}
    metadata, body = (
        (project / "report.md").read_text().removeprefix("---\n").split("\n---")
    )
    assert "Untitled report" in metadata
    assert "author:" not in metadata
    assert not body.strip()


@pytest.mark.parametrize(("title", "author"), [("   ", None), (None, "")])
def test_empty_manuscript_metadata_leaves_no_project(
    tmp_path: Path, title: str | None, author: str | None
) -> None:
    with pytest.raises(ValueError, match="must contain"):
        new("brief", tmp_path / "draft", title=title, author=author)
    assert not (tmp_path / "draft").exists()
