import shutil
import subprocess
from pathlib import Path

import pytest

from folio_reports.core import STYLES, build, new

pytestmark = pytest.mark.skipif(
    shutil.which("pandoc") is None, reason="requires Pandoc"
)


@pytest.mark.parametrize("style", STYLES)
def test_style_override_embeds_the_selected_design(tmp_path: Path, style: str) -> None:
    project = new("specimen", tmp_path / "book", style="signal")
    original = (project / "folio.yaml").read_bytes()
    tex = build(project, project / "proof.tex", style=style).read_text()
    style_marker = (project / "styles" / f"{style}.tex").read_text().splitlines()[0]
    assert style_marker in tex
    assert r"\begin{FolioColumns}" in tex
    assert r"\FolioTrend{Evening visits per week}" in tex
    assert r"\FolioHeatTitle{Evening arrivals by day}" in tex
    assert (project / "folio.yaml").read_bytes() == original


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
    project = new("brief", tmp_path / "book")
    (project / "report.md").write_text(markdown)
    with pytest.raises(subprocess.CalledProcessError):
        build(project, project / "report.tex")
    assert message in capfd.readouterr().err


def test_author_metadata_and_cover_survive_style(tmp_path: Path) -> None:
    project = new("brief", tmp_path / "book")
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


def test_new_cli_style_and_legacy_build(tmp_path: Path) -> None:
    from folio_reports.cli import main

    project = tmp_path / "example"
    assert main(["new", "brief", str(project), "--style", "gazette"]) == 0
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
