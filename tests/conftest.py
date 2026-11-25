import shutil
from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def legacy_report(tmp_path: Path) -> Callable[[str], Path]:
    archive = Path(__file__).resolve().parents[1] / "examples/legacy/templates"

    def copy_report(layout: str) -> Path:
        project = tmp_path / layout
        shutil.copytree(archive / "common", project)
        shutil.copytree(archive / layout, project, dirs_exist_ok=True)
        return project

    return copy_report
