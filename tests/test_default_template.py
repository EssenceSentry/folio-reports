import shutil
from pathlib import Path

import pytest

from folio_reports import build, new


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="Requires Pandoc")
def test_new_report_places_prose_in_columns_around_native_tables(
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
    table = body.index(r"\begin{longtable}")
    assert first < body.index(r"\end{FolioReadingColumns}") < table
    assert table < body.index(r"\begin{FolioReadingColumns}", first + 1)
    assert not (project / "styles").exists()
