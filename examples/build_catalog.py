# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Build the Outlook sample and render its pages for the README."""

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from folio_reports import build, new

OUTPUT = Path(__file__).resolve().parent


def render_pages(pdf: Path, destination: Path) -> None:
    """Render every page at the same scale and save it as WebP."""
    destination.mkdir()
    stem = destination.parent / "page"
    subprocess.run(  # noqa: S603 - generated paths are passed directly to Poppler
        [  # noqa: S607 - command supplied by Poppler
            "pdftoppm",
            "-r",
            "132",
            "-png",
            str(pdf),
            str(stem),
        ],
        check=True,
    )
    for index, raster in enumerate(sorted(stem.parent.glob("page-*.png")), start=1):
        with Image.open(raster) as page:
            page.save(destination / f"page-{index}.webp", quality=92, method=6)


def main() -> None:
    """Update the example after its PDF and all page images render."""
    with TemporaryDirectory(dir=OUTPUT) as temporary:
        root = Path(temporary)
        pdf = build(new(root / "report"), root / "outlook-report.pdf")
        pages = root / "outlook-pages"
        render_pages(pdf, pages)
        published_pages = OUTPUT / pages.name
        published_pages.mkdir(exist_ok=True)
        for page in pages.iterdir():
            page.replace(published_pages / page.name)
        pdf.replace(OUTPUT / pdf.name)


if __name__ == "__main__":
    main()
