import shutil
from pathlib import Path

import pytest

from folio_reports import build, new


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="Requires Pandoc")
def test_new_report_floats_native_tables_whole_inside_the_columns(
    tmp_path: Path,
) -> None:
    project = new(tmp_path / "report", blank=True)
    paragraph = "A report needs a comfortable measure for continuous reading. " * 9
    (project / "report.md").write_text(
        "# Results\n\n"
        + paragraph
        + "\n\n| Measure | Value |\n|:---|---:|\n| Observations | 100 |\n\n"
        + paragraph
    )
    body = (
        build(project, project / "proof.tex").read_text().split(r"\begin{document}")[1]
    )
    first = body.index(r"\begin{FolioReadingColumns}")
    whole = body.index(r"\begin{FolioWhole}")
    table = body.index(r"\begin{longtable}")
    # The table floats whole, so one run of columns carries the text past it.
    assert first < whole < table < body.index(r"\end{FolioWhole}")
    assert body.index(r"\end{FolioWhole}") < body.index(r"\end{FolioReadingColumns}")
    assert body.count(r"\begin{FolioReadingColumns}") == 1
    assert not (project / "styles").exists()


def test_breakable_table_stays_in_place_between_column_runs(tmp_path: Path) -> None:
    project = new(tmp_path / "report", blank=True)
    paragraph = "A report needs a comfortable measure for continuous reading. " * 9
    (project / "report.md").write_text(
        "# Results\n\n"
        + paragraph
        + '\n\n::: {.table-layout .breakable widths="60,40"}\n\n'
        + "| Measure | Value |\n|:---|---:|\n| Observations | 100 |\n\n:::\n\n"
        + paragraph
    )
    body = (
        build(project, project / "proof.tex").read_text().split(r"\begin{document}")[1]
    )
    first = body.index(r"\begin{FolioReadingColumns}")
    table = body.index(r"\begin{longtable}")
    assert r"\begin{FolioWhole}" not in body
    assert first < body.index(r"\end{FolioReadingColumns}") < table
    assert table < body.index(r"\begin{FolioReadingColumns}", first + 1)
