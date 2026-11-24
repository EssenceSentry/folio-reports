# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11", "pypdf>=5"]
# ///
"""Render the printable style catalog and component specimen from shipped projects."""

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


def main() -> None:
    """Compile every style and make a contact sheet from the actual page headers."""
    gallery = PdfWriter()
    gallery.add_metadata({"/Title": "Folio Reports · Ten visual styles"})
    sheet = Image.new("RGB", (1040, 5 * 230 + 20), "#ECEBE6")
    drawing = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=20)
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
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
            thumb = project / "thumbnail"
            # Rasterize our generated PDF to a fixed local thumbnail.
            subprocess.run(  # noqa: S603 - fixed arguments and generated paths
                [  # noqa: S607 - command supplied by Poppler
                    "pdftoppm",
                    "-r",
                    "100",
                    "-f",
                    "1",
                    "-l",
                    "1",
                    "-singlefile",
                    "-png",
                    str(pdf),
                    str(thumb),
                ],
                check=True,
            )
            with Image.open(thumb.with_suffix(".png")) as page:
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
                drawing.rounded_rectangle(
                    (x, y, x + 494, y + 216), radius=5, fill="white"
                )
                sheet.paste(header, (x + (494 - header.width) // 2, y + 45))
                drawing.text((x + 20, y + 10), style.title(), fill="#303C3D", font=font)
        gallery.write(OUTPUT / "style-lookbook.pdf")
        sheet.save(OUTPUT / "style-previews.webp", quality=91, method=6)
        project = new("specimen", root / "specimen", style="fieldnotes")
        build(project, OUTPUT / "component-specimen.pdf")


if __name__ == "__main__":
    main()
