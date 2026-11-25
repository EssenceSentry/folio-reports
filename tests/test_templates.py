import shutil
from pathlib import Path

import pytest

from folio_reports import build, new


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="Requires Pandoc")
def test_shipped_template_exports_latex(tmp_path: Path) -> None:
    project = new(tmp_path / "outlook")
    tex = build(project, project / "manuscript.tex").read_text()
    assert r"\documentclass" in tex
    assert r"\begin{document}" in tex
    assert r"\begin{FolioReadingColumns}" in tex
    assert r"\begin{FolioMetricRail}" in tex
    assert "cover.jpg" in tex


@pytest.mark.skipif(
    not all(shutil.which(tool) for tool in ("pandoc", "tectonic")),
    reason="PDF integration requires both external typesetting tools",
)
def test_shipped_template_typesets(tmp_path: Path) -> None:
    pdf = build(new(tmp_path / "report")).read_bytes()
    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")


def test_tex_export_preserves_layout(tmp_path: Path) -> None:
    project = new(tmp_path / "report")
    with pytest.raises(ValueError, match="template"):
        build(project, project / "style.tex")
