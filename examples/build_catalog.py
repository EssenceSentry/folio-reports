# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11", "pypdf>=5"]
# ///
"""Build the published sample PDFs and their README previews from fresh projects."""

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter

from folio_reports.core import STYLES, build, new

OUTPUT = Path(__file__).resolve().parent


def masthead_end(page) -> float:
    """Locate the opening paragraph so each crop stops below the byline."""
    positions = []

    def locate(text, matrix, text_matrix, _font, size):
        if "A late feeder bus" in text:
            baseline = matrix[5] + text_matrix[5]
            height = float(page.mediabox.height)
            positions.append((height - baseline - size) / height)

    page.extract_text(visitor_text=locate)
    if len(positions) != 1:
        raise ValueError("Could not locate the opening paragraph of the style specimen")
    return float(positions[0])


def raster_page(pdf: Path, page: int, destination: Path) -> Image.Image:
    """Render one PDF page at a consistent scale for the two preview sheets."""
    subprocess.run(  # noqa: S603 - generated paths are passed directly to Poppler
        [  # noqa: S607 - command supplied by Poppler
            "pdftoppm",
            "-r",
            "100",
            "-f",
            str(page),
            "-l",
            str(page),
            "-singlefile",
            "-png",
            str(pdf),
            str(destination),
        ],
        check=True,
    )
    with Image.open(destination.with_suffix(".png")) as image:
        return image.convert("RGB")


def render_examples(root: Path, assets: Path) -> None:
    """Build each worked report and place the brief and research pages side by side."""
    pages = []
    for layout, filename in (
        ("brief", "decision-brief"),
        ("research", "research-report"),
    ):
        project = new(layout, root / layout)
        pdf = build(project, assets / f"{filename}.pdf")
        for number in range(1, len(PdfReader(pdf).pages) + 1):
            page = raster_page(pdf, number, project / f"page-{number}")
            page.thumbnail((420, 595), Image.Resampling.LANCZOS)
            pages.append(page)
    gutter = 26
    sheet = Image.new(
        "RGB",
        (
            sum(page.width + gutter for page in pages) + gutter,
            max(page.height for page in pages) + 2 * gutter,
        ),
        "#E8E7E2",
    )
    x = gutter
    for page in pages:
        sheet.paste(page, (x, gutter))
        x += page.width + gutter
    sheet.save(assets / "report-previews.webp", quality=92, method=6)
    build(
        new("specimen", root / "specimen", style="fieldnotes"),
        assets / "component-specimen.pdf",
    )


def render_styles(root: Path, assets: Path) -> None:
    """Compile the style lookbook and crop each masthead from its actual PDF."""
    gallery = PdfWriter()
    gallery.add_metadata({"/Title": "Folio Reports · Ten visual styles"})
    sheet = Image.new("RGB", (1040, 5 * 230 + 20), "#ECEBE6")
    drawing = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=20)
    for i, style in enumerate(STYLES):
        project = new("brief", root / style, style=style)
        source = project / "report.md"
        source.write_text(
            source.read_text().replace(
                "author: Service Planning", f"author: {style.title()} edition"
            )
        )
        pdf = build(project)
        pages = PdfReader(pdf).pages
        if len(pages) != 1:
            raise ValueError(f"{style} proof no longer fits on one page")
        gallery.append(pdf, outline_item=style.title(), import_outline=False)
        with raster_page(pdf, 1, project / "thumbnail") as page:
            width, height = page.size
            header = page.crop(
                (
                    int(width * 0.122),
                    int(height * 0.070),
                    int(width * 0.878),
                    int(height * masthead_end(pages[0])),
                )
            )
            header.thumbnail((450, 164), Image.Resampling.LANCZOS)
            x, y = 16 + i % 2 * 512, 12 + i // 2 * 230
            drawing.rounded_rectangle((x, y, x + 494, y + 216), radius=5, fill="white")
            sheet.paste(header, (x + (494 - header.width) // 2, y + 45))
            drawing.text((x + 20, y + 10), style.title(), fill="#303C3D", font=font)
    gallery.write(assets / "style-lookbook.pdf")
    sheet.save(assets / "style-previews.webp", quality=91, method=6)


def main() -> None:
    """Replace the published examples after every design has rendered successfully."""
    with TemporaryDirectory(dir=OUTPUT) as temporary:
        root = Path(temporary)
        assets = root / "assets"
        assets.mkdir()
        render_examples(root, assets)
        render_styles(root, assets)
        for asset in assets.iterdir():
            asset.replace(OUTPUT / asset.name)


if __name__ == "__main__":
    main()
