from pathlib import Path

import pytest

from folio_reports.cli import main
from folio_reports.core import build, new


@pytest.mark.parametrize("args", [["styles"], ["new", "research", "sample"]])
def test_retired_starters_are_unavailable(args: list[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2


@pytest.mark.parametrize("style", ["swiss", "../surprise"])
def test_new_project_cannot_preview_a_retired_style(tmp_path: Path, style: str) -> None:
    with pytest.raises(ValueError, match="styles"):
        build(new(tmp_path / "report"), style=style)
