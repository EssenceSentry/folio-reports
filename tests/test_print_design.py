"""Measure component positions in the typeset PDF."""

import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree

import pytest

from folio_reports import build, new

pytestmark = pytest.mark.skipif(
    not all(shutil.which(tool) for tool in ("pandoc", "tectonic", "pdftotext")),
    reason="Layout measurement requires the PDF toolchain and Poppler",
)


def _bounding_boxes(pdf: Path) -> ElementTree.Element:
    result = subprocess.run(  # noqa: S603 - fixed argv and generated PDF
        ["pdftotext", "-bbox", str(pdf), "-"],  # noqa: S607 - Poppler on PATH
        capture_output=True,
        check=True,
    )
    # Poppler generated this XHTML from the local fixture.
    return ElementTree.fromstring(result.stdout)  # noqa: S314


def test_metric_value_leaves_room_for_its_description(tmp_path: Path) -> None:
    project = new("brief", tmp_path / "brief")
    (project / "report.md").write_text(
        '::: {.metric value="123,456.78"}\nMeasured revenue.\n:::\n'
    )
    pdf = build(project)
    page = _bounding_boxes(pdf)
    words = {word.text: word for word in page.findall(".//{*}word")}
    assert float(words["123,456.78"].attrib["xMax"]) + 6 < float(
        words["Measured"].attrib["xMin"]
    )


def test_table_and_note_share_the_selected_measure(tmp_path: Path) -> None:
    project = new("brief", tmp_path / "tables")
    (project / "report.md").write_text(
        '::: {.table-layout widths="1,1"}\n\n'
        "| Label | Full |\n|:---|---:|\n| North | 8 |\n\n:::\n\n"
        '::: {.table-layout widths="1,1" width="50%"}\n\n'
        "| Label | Half |\n|:---|---:|\n| South | 8 |\n\n" + "Note " * 36 + "\n\n:::\n"
    )
    words = _bounding_boxes(build(project)).findall(".//{*}word")
    cells = {word.text: word for word in words}
    left = float(cells["North"].attrib["xMin"])
    full = float(cells["Full"].attrib["xMax"]) - left
    half = float(cells["Half"].attrib["xMax"]) - left
    assert half / full == pytest.approx(0.5, abs=0.01)
    notes = [word for word in words if word.text == "Note"]
    assert len(notes) == 36
    assert max(float(word.attrib["xMax"]) for word in notes) <= left + half + 1
