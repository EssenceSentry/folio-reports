import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from folio_reports import __version__
from folio_reports.cli import main


def test_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    project = str(tmp_path / "case")
    assert main(["new", project]) == 0
    assert main(["new", project]) == 2
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


def test_cli_blank_flag(tmp_path: Path) -> None:
    project = tmp_path / "new report"
    assert main(["new", str(project), "--blank"]) == 0
    assert not (project / "references.bib").exists()


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="TeX export requires Pandoc")
def test_cli_personal_manuscript_renders_metadata(tmp_path: Path) -> None:
    project = tmp_path / "draft"
    assert (
        main(
            [
                "new",
                str(project),
                "--title",
                "Q4: 8% & #5",
                "--author",
                'Zoë "Z" García',
            ]
        )
        == 0
    )
    output = tmp_path / "proof.tex"
    assert main(["build", str(project), "-o", str(output)]) == 0
    tex = output.read_text()
    assert r"\title{Q4: 8\% \& \#5}" in tex
    assert "García" in tex
    assert "Alder Junction" not in tex
