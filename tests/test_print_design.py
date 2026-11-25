"""Measure component positions in the typeset PDF."""

import shutil
import subprocess
from collections.abc import Callable
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
    project = new(tmp_path / "brief")
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
    project = new(tmp_path / "tables")
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


@pytest.mark.parametrize("style", ["fieldnotes", "monograph"])
def test_specimen_folio_uses_the_final_page_geometry(
    legacy_report: Callable[[str], Path], style: str
) -> None:
    project = legacy_report("specimen")
    (project / "report.md").write_text("Report text.")
    page = _bounding_boxes(build(project, style=style)).find(".//{*}page")
    assert page is not None
    width = float(page.attrib["width"])
    folio = page.find(".//{*}word[.='1']")
    assert folio is not None
    left, right = (float(folio.attrib[edge]) for edge in ("xMin", "xMax"))
    if style == "monograph":
        assert (left + right) / 2 == pytest.approx(width / 2, abs=1)
    else:
        assert right == pytest.approx(width - 18 * 72 / 25.4, abs=1)


def test_related_decision_is_closer_than_a_new_risk_panel(tmp_path: Path) -> None:
    project = new(tmp_path / "spacing", blank=True)
    (project / "report.md").write_text(
        "::::: {.comparison}\n"
        '::: {.column title="First option"}\nOptionEnd\n:::\n'
        '::: {.column title="Second option"}\nOtherEnd\n:::\n'
        ":::::\n\n"
        '::: {.decision title="DecisionLabel"}\nDecision body.\n:::\n\n'
        '::: {.milestone when="Milestone"}\nCalendarEnd\n:::\n\n'
        '::: {.risk title="RiskLabel"}\nRisk body.\n:::\n'
    )
    words = {
        word.text: word
        for word in _bounding_boxes(build(project)).findall(".//{*}word")
    }
    decision_gap = float(words["DecisionLabel"].attrib["yMin"]) - float(
        words["OptionEnd"].attrib["yMax"]
    )
    risk_gap = float(words["RiskLabel"].attrib["yMin"]) - float(
        words["CalendarEnd"].attrib["yMax"]
    )
    assert 0 < decision_gap < risk_gap


@pytest.mark.parametrize(("layout", "value"), [("research", "30"), ("specimen", "48%")])
def test_worked_tables_run_to_the_right_folio_edge(
    legacy_report: Callable[[str], Path], layout: str, value: str
) -> None:
    page = _bounding_boxes(build(legacy_report(layout))).findall(".//{*}page")[1]
    words = page.findall(".//{*}word")
    cell = next(word for word in words if word.text == value)
    folio = max(
        (word for word in words if word.text == "2"),
        key=lambda word: float(word.attrib["xMax"]),
    )
    assert float(cell.attrib["xMax"]) == pytest.approx(
        float(folio.attrib["xMax"]), abs=1
    )


def test_outlook_cover_and_evidence_use_the_page_grid(tmp_path: Path) -> None:
    pages = _bounding_boxes(build(new(tmp_path / "outlook"))).findall(".//{*}page")
    assert len(pages) == 6
    assert pages[0].find(".//{*}word[.='Classification']") is not None
    table = pages[3].find(".//{*}word[.='6.0%']")
    assert table is not None
    assert float(table.attrib["xMax"]) == pytest.approx(560, abs=1)
    note = pages[4].find(".//{*}word[.='calibration']")
    assert note is not None
    assert float(note.attrib["yMin"]) > 680


def test_new_manuscript_flows_in_two_columns_above_a_native_table(
    tmp_path: Path,
) -> None:
    project = new(tmp_path / "draft", blank=True)
    paragraph = " Ordinary paragraphs should use a comfortable reading measure." * 8
    (project / "report.md").write_text(
        "Firstcolumn."
        + paragraph
        + "\n\nSecondcolumn."
        + paragraph
        + "\n\n| Label | Middle | Right |\n|:---|---:|---:|\n| Result | 12 | 79 |\n"
    )
    page = _bounding_boxes(build(project)).find(".//{*}page")
    assert page is not None
    words = {word.text: word.attrib for word in page.findall(".//{*}word")}
    assert float(words["Firstcolumn."]["xMin"]) == pytest.approx(59, abs=1)
    assert float(words["Secondcolumn."]["xMin"]) == pytest.approx(318.5, abs=1)
    assert float(words["79"]["xMax"]) == pytest.approx(560, abs=1)


@pytest.mark.skipif(shutil.which("pdftohtml") is None, reason="Requires Poppler XML")
def test_data_page_figure_caption_uses_light_text(tmp_path: Path) -> None:
    project = new(tmp_path / "outlook")
    (project / "report.md").write_text(
        "::::: {.data-page}\n\n"
        '::: {.exhibit title="Diagnostic"}\n\n'
        "![Diagnostic caption.](cover.jpg){width=45%}\n\n"
        ":::\n\n:::::\n"
    )
    result = subprocess.run(  # noqa: S603 - fixed argv and generated PDF
        ["pdftohtml", "-xml", "-i", "-stdout", str(build(project))],  # noqa: S607
        capture_output=True,
        check=True,
    )
    page = ElementTree.fromstring(result.stdout)  # noqa: S314 - local Poppler XML
    caption = page.find(".//text[.='Diagnostic caption.']")
    assert caption is not None
    font = page.find(f".//fontspec[@id='{caption.attrib['font']}']")
    assert font is not None
    assert min(bytes.fromhex(font.attrib["color"][1:])) >= 175


@pytest.mark.skipif(
    shutil.which("pdfinfo") is None, reason="Requires Poppler destinations"
)
def test_outlook_keeps_stacked_headings_with_the_opening_text(tmp_path: Path) -> None:
    project = new(tmp_path / "outlook", blank=True)
    (project / "report.md").write_text(
        "Previous section.\n\n"
        "\\vspace*{520bp}\n\n"
        "# Separating the Plan's Pull from Advertiser Cost\n\n"
        "## Replay setup\n\n"
        "Opening passage on a new method with enough words for several lines at "
        "the normal measure. The section introduces the method and explains its use.\n"
    )
    pdf = build(project)
    pages = _bounding_boxes(pdf).findall(".//{*}page")
    assert len(pages) == 2
    markers = {"Separating", "Replay", "Opening"}
    assert markers.isdisjoint(word.text for word in pages[0].iterfind(".//{*}word"))
    assert markers <= {word.text for word in pages[1].iterfind(".//{*}word")}
    pdfinfo = shutil.which("pdfinfo")
    assert pdfinfo is not None
    destinations = subprocess.check_output(  # noqa: S603 - generated PDF with fixed arguments
        [pdfinfo, "-dests", str(pdf)], text=True
    )
    heading = next(
        line
        for line in destinations.splitlines()
        if '"section.1"' in line
        or '"section*.1"' in line
        or '"separating-the-plans-pull-from-advertiser-cost"' in line
    )
    assert heading.split()[0] == "2"


def test_keep_together_keeps_the_lead_and_last_list_item_on_one_page(
    tmp_path: Path,
) -> None:
    project = new(tmp_path / "outlook", blank=True)
    (project / "report.md").write_text(
        "Previous section.\n\n"
        "\\vspace*{580bp}\n\n"
        "::: {.keep-together}\n\n"
        "Criteria for the review.\n\n"
        + "\n".join(f"- Rule {i}." for i in range(1, 8))
        + "\n- Final criterion.\n\n:::\n"
    )
    pages = _bounding_boxes(build(project)).findall(".//{*}page")
    assert len(pages) == 2
    assert pages[0].find(".//{*}word[.='Criteria']") is None
    assert pages[1].find(".//{*}word[.='Criteria']") is not None
    assert pages[1].find(".//{*}word[.='Final']") is not None
