import shutil
from pathlib import Path

import pytest

from folio_reports import build, new


@pytest.mark.parametrize("layout", ["brief", "research"])
@pytest.mark.skipif(
    shutil.which("pandoc") is None, reason="Pandoc is optional for API tests"
)
def test_shipped_templates_export_latex(tmp_path: Path, layout: str) -> None:
    project = new(layout, tmp_path / layout)
    tex = build(project, project / "manuscript.tex").read_text()
    assert r"\documentclass" in tex
    assert r"\begin{document}" in tex
    if layout == "brief":
        assert r"\begin{FolioMetric}{18}" in tex
    else:
        assert "Wilson" in tex
        assert "missed-transfers.pdf" in tex


@pytest.mark.parametrize("layout", ["brief", "research", "specimen"])
@pytest.mark.skipif(
    not all(shutil.which(tool) for tool in ("pandoc", "tectonic")),
    reason="PDF integration requires both external typesetting tools",
)
def test_shipped_templates_typeset(tmp_path: Path, layout: str) -> None:
    pdf = build(new(layout, tmp_path / layout)).read_bytes()
    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")


def test_tex_export_preserves_layout(tmp_path: Path) -> None:
    project = new("brief", tmp_path / "brief")
    with pytest.raises(ValueError, match="template"):
        build(project, project / "style.tex")
