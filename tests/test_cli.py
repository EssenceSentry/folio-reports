import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from folio_reports import __version__
from folio_reports.cli import main


def test_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    project = str(tmp_path / "case")
    assert main(["new", "brief", project]) == 0
    assert main(["new", "brief", project]) == 2
    assert "exists" in capsys.readouterr().err.lower()
    with patch("folio_reports.cli.build", return_value=tmp_path / "report.pdf"):
        assert main(["build", project]) == 0
    assert "report.pdf" in capsys.readouterr().out


def test_compiler_failure(capsys: pytest.CaptureFixture[str]) -> None:
    with patch(
        "folio_reports.cli.build",
        side_effect=subprocess.CalledProcessError(1, ["pandoc"]),
    ):
        assert main(["build"]) == 2
    assert "error" in capsys.readouterr().err


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out
