"""Observable behavior of the standalone typography tools."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "typography" / "scripts"


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed local helper and fixture arguments
        [sys.executable, str(SCRIPTS / name), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def test_scale_compares_ratios_and_respects_the_body_anchor() -> None:
    output = run_script(
        "type_scale.py",
        "--medium",
        "print",
        "--base",
        "11",
        "--ratios",
        "1.2,1.25",
        "--up",
        "2",
        "--format",
        "json",
    )
    scales = json.loads(output.stdout)
    for scale in scales:
        by_step = {row["step"]: row for row in scale["steps"]}
        assert by_step[0]["size"] == 11
        assert by_step[2]["size"] == pytest.approx(11 * scale["ratio"] ** 2, abs=0.01)
        assert by_step[-1]["size"] > 0
        assert by_step[0]["leading"] > by_step[0]["size"]


def test_contrast_accounts_for_alpha_and_light_on_dark() -> None:
    white = json.loads(run_script("contrast.py", "#fff", "#000").stdout)
    translucent = json.loads(run_script("contrast.py", "#ffffff80", "#000").stdout)
    assert white["wcag_ratio"] == 21
    assert 1 < translucent["wcag_ratio"] < white["wcag_ratio"]
    assert white["apca_lc"] < 0


def test_scale_exports_a_fluid_heading_and_an_opt_in_baseline() -> None:
    result = run_script(
        "type_scale.py",
        "--medium",
        "web",
        "--base",
        "16",
        "--base-max",
        "20",
        "--ratios",
        "1.25",
        "--up",
        "2",
        "--format",
        "css",
        "--grid",
        "24",
        "--k",
        "0.36",
    )
    assert "clamp(1rem, calc(" in result.stdout
    assert "1.25rem)" in result.stdout
    assert "--text-subhead-tracking:" in result.stdout
    assert ":where(h1)" in result.stdout
    assert ".type-baseline" in result.stdout


@pytest.mark.skipif(
    not shutil.which("pdftotext"), reason="PDF geometry requires Poppler"
)
def test_pdf_proof_measures_only_selected_page_and_region() -> None:
    proof = json.loads(
        run_script(
            "proof_pdf.py",
            str(ROOT / "examples" / "research-report.pdf"),
            "--page",
            "2",
            "--region",
            "85,150,445,350",
        ).stdout
    )
    assert len(proof["pages"]) == 1
    page = proof["pages"][0]
    assert page["page"] == 2
    assert page["lines"] > 2
    assert page["characters_per_line"]["max"] > 10
    assert page["ink_bounds_pt"][0] >= 85
    assert page["ink_bounds_pt"][2] <= 445


@pytest.mark.skipif(
    not (shutil.which("qpdf") and shutil.which("gs")),
    reason="Production evidence requires qpdf and Ghostscript",
)
def test_production_inspector_reads_real_font_and_page_resources() -> None:
    report = json.loads(
        run_script(
            "preflight_pdf.py", str(ROOT / "examples" / "research-report.pdf")
        ).stdout
    )
    assert report["structure"]["page_count"] == 2
    assert all(font["embedded"] for font in report["structure"]["fonts"])
    assert report["structure"]["fonts"]
    assert report["text"]["body_size_pt"] > 0
    assert report["text"]["body_chars_per_line_median_full_lines"] > 20
