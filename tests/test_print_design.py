"""Check the printed geometry of the metric when its value needs more room."""

import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree

import pytest

from folio_reports import build, new


@pytest.mark.skipif(
    not all(shutil.which(tool) for tool in ("pandoc", "tectonic", "pdftotext")),
    reason="Layout measurement requires the PDF toolchain and Poppler",
)
def test_metric_value_leaves_room_for_its_description(tmp_path: Path) -> None:
    project = new("brief", tmp_path / "brief")
    (project / "report.md").write_text(
        '::: {.metric value="123,456.78"}\nMeasured revenue.\n:::\n'
    )
    pdf = build(project)
    result = subprocess.run(  # noqa: S603 - fixed argv and generated PDF
        ["pdftotext", "-bbox", str(pdf), "-"],  # noqa: S607 - Poppler on PATH
        capture_output=True,
        check=True,
    )
    # Poppler generated this XHTML from the local fixture.
    page = ElementTree.fromstring(result.stdout)  # noqa: S314
    words = {word.text: word for word in page.findall(".//{*}word")}
    assert float(words["123,456.78"].attrib["xMax"]) + 6 < float(
        words["Measured"].attrib["xMin"]
    )
