from pathlib import Path

import pytest

from folio_reports.cli import main
from folio_reports.core import STYLES, build, new


def test_styles_are_discoverable(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["styles"]) == 0
    listing = capsys.readouterr().out
    assert len(STYLES) >= 10
    assert all(style in listing for style in STYLES)


def test_style_portability(tmp_path: Path) -> None:
    project = new("specimen", tmp_path / "book", style="swiss")
    assert "folio-style: swiss" in (project / "folio.yaml").read_text()
    assert {path.stem for path in (project / "styles").glob("*.tex")} == set(STYLES)
    assert (project / "components.tex").is_file()


def test_unknown_style(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="style"):
        new("brief", tmp_path / "book", style="../surprise")


def test_legacy_style_override(tmp_path: Path) -> None:
    (tmp_path / "report.md").touch()
    (tmp_path / "folio.yaml").touch()
    with pytest.raises(ValueError, match="styles"):
        build(tmp_path, style="swiss")
