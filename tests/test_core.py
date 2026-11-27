import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from folio_reports.core import build, layout_warnings, new


def test_new_is_self_contained(tmp_path: Path) -> None:
    dest = tmp_path / "nested" / "report"
    new(dest)
    for name in ["report.md", "folio.yaml", "style.tex", "layout.tex"]:
        assert (dest / name).is_file()
    (dest / "report.md").write_text("my edits")
    with pytest.raises(FileExistsError):
        new(dest)
    assert (dest / "report.md").read_text() == "my edits"


def test_missing_source(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"report\.md"):
        build(tmp_path)


def test_failed_build_preserves_existing_pdf(tmp_path: Path) -> None:
    new(tmp_path / "case")
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
    new(project)

    def render(
        args: list[str], *, cwd: Path, check: bool, **_: object
    ) -> subprocess.CompletedProcess[str]:
        assert cwd == project
        if args[0] == "pandoc":
            assert check
            Path(args[args.index("--output") + 1]).write_text("% LaTeX")
        else:
            outdir = Path(next(a for a in args if a.startswith("--outdir="))[9:])
            (outdir / "review.pdf").write_bytes(b"%PDF-example")
            (outdir / "review.log").write_text(
                "Package Folio Warning: A list is cut by floated exhibit 2.\n\n"
            )
        return subprocess.CompletedProcess(args, 0, "", "")

    with patch("folio_reports.core.subprocess.run", side_effect=render):
        output = build(project, tmp_path / "outputs" / "review.pdf")
    assert output.read_bytes().startswith(b"%PDF")


def test_reject_nondocument_output(tmp_path: Path) -> None:
    new(tmp_path / "case")
    with pytest.raises(ValueError, match="PDF"):
        build(tmp_path / "case", tmp_path / "case" / "report.md")


def test_blank_project_keeps_design_and_omits_example_content(tmp_path: Path) -> None:
    example = new(tmp_path / "example")
    project = new(tmp_path / "draft", blank=True)
    resources = [
        "layout.tex",
        "cover.jpg",
        "folio.yaml",
        "blocks.lua",
        "compose.lua",
        "style.tex",
        "components.tex",
    ]
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
    assert "folio-cover-image: cover.jpg" in metadata
    assert not body.strip()


@pytest.mark.parametrize(("title", "author"), [("   ", None), (None, "")])
def test_empty_manuscript_metadata_leaves_no_project(
    tmp_path: Path, title: str | None, author: str | None
) -> None:
    with pytest.raises(ValueError, match="must contain"):
        new(tmp_path / "draft", title=title, author=author)
    assert not (tmp_path / "draft").exists()


def test_engine_failure_is_reported_and_raised(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    project = new(tmp_path / "case")

    def render(args: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        if args[0] == "pandoc":
            Path(args[args.index("--output") + 1]).write_text("% LaTeX")
            return subprocess.CompletedProcess(args, 0, "", "")
        return subprocess.CompletedProcess(args, 1, "", "! Display equation is wide")

    with (
        patch("folio_reports.core.subprocess.run", side_effect=render),
        pytest.raises(subprocess.CalledProcessError),
    ):
        build(project)
    assert "Display equation is wide" in capsys.readouterr().err


def test_layout_warnings_name_each_fault_once() -> None:
    log = (
        "Underfull \\hbox (badness 10000) in paragraph at lines 3--9\n"
        "[]\\TU/SourceSansPro-Regular.otf(0)/m/n/11 One large new flight\n\n"
        "Underfull \\hbox (badness 10000) in paragraph at lines 3--9\n"
        "[]\\TU/SourceSansPro-Regular.otf(0)/m/n/11 One large new flight\n\n"
        "Overfull \\hbox (12.5pt too wide) in paragraph at lines 20--21\n"
        "\\TU/lmtt/m/n/11 a_long_identifier\n\n"
        "Overfull \\hbox (0.2pt too wide) in paragraph at lines 30--31\nfine\n\n"
        "Overfull \\vbox (19.0pt too high) has occurred while \\output is active\n"
        "Package Folio Warning: A list is cut by floated exhibit 3 (page 22) and is t\n"
        "oo tall to move past it.\n\n"
    )
    assert layout_warnings(log) == [
        "loose line (badness 10000); reword or shorten near: One large new flight",
        "line 12.5pt too wide near: a_long_identifier",
        "a column or page is 19.0pt too tall",
        "A list is cut by floated exhibit 3 (page 22) and is too tall to move past it.",
    ]
