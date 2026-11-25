import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from folio_reports import build, new

pytestmark = pytest.mark.skipif(
    shutil.which("pandoc") is None, reason="requires Pandoc"
)


@pytest.mark.parametrize("style", ["classic", "fieldnotes", "signal", "swiss"])
def test_style_override_embeds_the_selected_design(
    legacy_report: Callable[[str], Path], style: str
) -> None:
    project = legacy_report("specimen")
    original = (project / "folio.yaml").read_bytes()
    tex = build(project, project / "proof.tex", style=style).read_text()
    style_marker = (project / "styles" / f"{style}.tex").read_text().splitlines()[0]
    assert style_marker in tex
    assert r"\begin{FolioColumns}" in tex
    assert r"\FolioTrend{Evening visits per week}" in tex
    assert r"\FolioHeatTitle{Evening arrivals by day}" in tex
    assert (project / "folio.yaml").read_bytes() == original


def test_reference_labels_keep_their_original_link_targets(
    legacy_report: Callable[[str], Path],
) -> None:
    project = legacy_report("specimen")
    tex = " ".join(build(project, project / "proof.tex").read_text().split())
    doi = "10.1080/01621459.1927.10502953"
    assert rf"\href{{https://doi.org/{doi}}}{{DOI {doi}}}" in tex
    assert r"\href{https://pubmed.ncbi.nlm.nih.gov/9595617/}{PubMed 9595617}" in tex


@pytest.mark.parametrize(
    ("markdown", "message"),
    [
        (
            '::: {.interval label="Visits" low="25" value="12" high="14"}\n:::',
            "low <= value",
        ),
        ("::: {.metric}\nReaders.\n:::", "value attribute"),
        (
            '::: {.trend min="0" max="10" values="1,,3"}\n:::',
            "finite number",
        ),
        ("::: {.comparison}\nOne paragraph.\n:::", "two .column"),
        ("::: {.flow}\nA paragraph.\n:::", "ordered list"),
        ('::: {.bar label="Percent" value="1000"}\n:::', "between 0 and 100"),
        (
            '::: {.distribution min="0" max="10" summary="1,2,7,5,9"}\n:::',
            "ordered",
        ),
    ],
)
def test_component_errors_identify_the_input(
    tmp_path: Path, markdown: str, message: str, capfd: pytest.CaptureFixture[str]
) -> None:
    project = new(tmp_path / "book")
    (project / "report.md").write_text(markdown)
    with pytest.raises(subprocess.CalledProcessError):
        build(project, project / "report.tex")
    assert message in capfd.readouterr().err


def test_author_metadata_and_cover_survive_style(tmp_path: Path) -> None:
    project = new(tmp_path / "book")
    (project / "report.md").write_text(
        "---\ntitle: A handoff\nfolio-cover: true\n"
        "header-includes:\n  - '\\newcommand{\\AReader}{First}'\n"
        "  - '\\newcommand{\\AnotherReader}{Second}'\n---\n"
        '::: {.note title="R&D at 50%"}\nText with **emphasis**.\n:::\n'
    )
    tex = build(project, project / "proof.tex").read_text()
    assert r"\let\FolioInnerTitle" in tex
    assert r"\newcommand{\AReader}{First}" in tex
    assert r"\newcommand{\AnotherReader}{Second}" in tex
    assert r"R\&D at 50\%" in tex


def test_cli_can_preview_an_existing_project(
    legacy_report: Callable[[str], Path], tmp_path: Path
) -> None:
    from folio_reports.cli import main

    project = legacy_report("brief")
    assert (
        main(
            [
                "build",
                str(project),
                "--style",
                "ledger",
                "-o",
                str(project / "proof.tex"),
            ]
        )
        == 0
    )
    plain = tmp_path / "legacy"
    plain.mkdir()
    (plain / "folio.yaml").write_text("from: markdown\nto: latex\nstandalone: true\n")
    (plain / "report.md").write_text("An existing report.")
    assert "An existing report." in build(plain, plain / "legacy.tex").read_text()


def test_table_layout_preserves_column_alignment_and_caption(tmp_path: Path) -> None:
    project = new(tmp_path / "book")
    (project / "report.md").write_text(
        '::: {.table-layout widths="1,3"}\n\n'
        "| Period | Visits |\n|:---|---:|\n| Morning | 16 |\n\n"
        ": Counts by period\n\n:::\n"
    )
    body = (
        build(project, project / "proof.tex").read_text().split(r"\begin{document}")[1]
    )
    assert "0.25" in body
    assert "0.75" in body
    assert r"\raggedleft" in body
    assert "Counts by period" in body


@pytest.mark.parametrize("widths", ["0,2", "1", "1,nan", "1,2,3"])
def test_table_layout_rejects_invalid_widths(tmp_path: Path, widths: str) -> None:
    project = new(tmp_path / "book")
    (project / "report.md").write_text(
        f'::: {{.table-layout widths="{widths}"}}\n\n'
        "| A | B |\n|---|---:|\n| Morning | 16 |\n\n:::\n"
    )
    with pytest.raises(subprocess.CalledProcessError):
        build(project, project / "proof.tex")


def test_compact_table_keeps_note_with_selected_measure(tmp_path: Path) -> None:
    project = new(tmp_path / "book")
    (project / "report.md").write_text(
        '::: {.table-layout widths="1,2" width="75%"}\n\n'
        "| Period | Visits |\n|---|---:|\n| Morning | 16 |\n\n"
        "The count includes **return visits**.\n\n:::\n"
    )
    body = (
        build(project, project / "proof.tex").read_text().split(r"\begin{document}")[1]
    )
    assert r"\begin{FolioTable}{0.750000}" in body
    assert body.index(r"\begin{FolioTableNote}") < body.index(r"\textbf{return visits}")
    assert body.index(r"\end{FolioTableNote}") < body.index(r"\end{FolioTable}")


@pytest.mark.parametrize("width", ["0%", "125%", "wide"])
def test_invalid_table_measure(tmp_path: Path, width: str) -> None:
    project = new(tmp_path / "book")
    (project / "report.md").write_text(
        f'::: {{.table-layout widths="1,1" width="{width}"}}\n\n'
        "| A | B |\n|---|---:|\n| Morning | 16 |\n\n:::\n"
    )
    with pytest.raises(subprocess.CalledProcessError):
        build(project, project / "proof.tex")
