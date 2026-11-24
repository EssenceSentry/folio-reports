import shutil
import subprocess
from pathlib import Path

import pytest

from folio_reports.core import build, new

pytestmark = pytest.mark.skipif(
    shutil.which("pandoc") is None, reason="requires Pandoc"
)


def _plot(row: str, scale: str = 'min="-10" max="30" reference="0"') -> str:
    return (
        f'::::: {{.intervalplot label="Change in R&D" stub="Period" {scale}}}\n'
        f'::: {{.row label="A & B" {row}}}\n:::\n:::::\n'
    )


def test_interval_plot_maps_signed_values_and_preserves_precision(
    tmp_path: Path,
) -> None:
    project = new("brief", tmp_path / "book")
    (project / "report.md").write_text(_plot('low="-10" value="+2.00" high="30"'))
    tex = build(project, project / "proof.tex").read_text()
    assert r"\FolioRangeTitle{Change in R\&D}" in tex
    assert r"\FolioRangeReference{0.250000}{0}" in tex
    assert r"\FolioRangeAxis{-10}{30}" in tex
    assert r"\FolioRangeMark{0.000000}{0.300000}{1.000000}" in tex
    assert r"A \& B" in tex
    assert "+2.00" in tex


def test_interval_plot_allows_ties_without_a_reference(tmp_path: Path) -> None:
    project = new("brief", tmp_path / "book")
    (project / "report.md").write_text(
        _plot('low="3" value="3" high="3"', 'min="1" max="5"')
    )
    body = (
        build(project, project / "proof.tex").read_text().split(r"\begin{document}")[1]
    )
    assert r"\FolioRangeMark{0.500000}{0.500000}{0.500000}" in body
    assert r"\FolioRangeReference" not in body


@pytest.mark.parametrize(
    ("content", "error"),
    [
        (_plot('value="2" low="3" high="4"'), "low <= value <= high"),
        (_plot('value="2" low="-11" high="4"'), "outside its axis"),
        (_plot('value="2" low="1" high="nan"'), "finite number"),
        (_plot('value="2" low="1" high="4"', 'min="5" max="5"'), "max must exceed min"),
        (
            _plot('value="2" low="1" high="4"', 'min="0" max="5" reference="-1"'),
            "Reference outside its axis",
        ),
        ('::: {.intervalplot label="X" min="0" max="5"}\n:::', "at least one .row"),
        (
            '::: {.intervalplot label="X" min="0" max="5"}\nText.\n:::',
            "expects .row",
        ),
        (
            _plot('value="2" low="1" high="4"').replace("\n:::\n", "\nText.\n:::\n"),
            "empty body",
        ),
    ],
)
def test_interval_plot_rejects_bad_inputs(
    tmp_path: Path, capfd: pytest.CaptureFixture[str], content: str, error: str
) -> None:
    project = new("brief", tmp_path / "book")
    (project / "report.md").write_text(content)
    with pytest.raises(subprocess.CalledProcessError):
        build(project, project / "proof.tex")
    assert error in capfd.readouterr().err


@pytest.mark.parametrize(("count", "marked"), [(4, True), (100, False)])
def test_sparse_trends_mark_individual_observations(
    tmp_path: Path, count: int, marked: bool
) -> None:
    project = new("brief", tmp_path / "book")
    values = ",".join(str(i) for i in range(count))
    (project / "report.md").write_text(
        f'::: {{.trend label="Visits" min="0" max="100" values="{values}" '
        'start="First" end="Last"}\n:::\n'
    )
    tex = build(project, project / "proof.tex").read_text()
    body = tex.split(r"\begin{document}")[1]
    assert (r"\FolioTrendPoints" in body) == marked


def test_interval_plot_accepts_wide_finite_scales(tmp_path: Path) -> None:
    project = new("brief", tmp_path / "book")
    (project / "report.md").write_text(
        _plot('low="-1e308" value="0" high="1e308"', 'min="-1e308" max="1e308"')
    )
    tex = build(project, project / "proof.tex").read_text()
    assert r"\FolioRangeMark{0.000000}{0.500000}{1.000000}" in tex


def test_heatmap_final_cell_stops_at_the_table_rule(tmp_path: Path) -> None:
    project = new("brief", tmp_path / "book")
    (project / "report.md").write_text(
        '::::: {.heatmap label="Visits" columns="Mon|Tue" min="0" max="10"}\n'
        '::: {.row label="Week 1" values="0,10"}\n:::\n:::::\n'
    )
    tex = build(project, project / "proof.tex").read_text()
    # Retain the default right padding under the final cell's color overhang.
    assert r"*{2}{>{\centering\arraybackslash}X}}\toprule" in tex


def test_interval_plot_preserves_distinct_large_integer_coordinates(
    tmp_path: Path,
) -> None:
    project = new("brief", tmp_path / "book")
    (project / "report.md").write_text(
        _plot(
            'low="9007199254740992" value="9007199254740993" high="9007199254740994"',
            'min="9007199254740992" max="9007199254740994"',
        )
    )
    tex = build(project, project / "proof.tex").read_text()
    assert r"\FolioRangeMark{0.000000}{0.500000}{1.000000}" in tex
