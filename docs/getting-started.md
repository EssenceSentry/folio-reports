# Author a report

## Create and render

Install Pandoc, Tectonic, uv and Python 3.12 or newer. Install Folio, then start a report with its title and byline.

```sh
uv tool install git+https://github.com/EssenceSentry/folio-reports.git
folio-reports new model-review --title "Evaluation under a review budget" --author "Model Evaluation"
folio-reports build model-review
```

Write below the closing `---` in `model-review/report.md`. Either `--title` or `--author` starts a blank manuscript. Use `--blank` on its own for “Untitled report”. Create a project with just its directory name to start from the full model evaluation example.

Both commands print their output path. The default PDF is `model-review/report.pdf`. Pass `-o path/to/report.pdf` to write a proof elsewhere. An explicit output path is relative to the shell's working directory. A failed build preserves the previous PDF.

## Compose the pages

Use a top-level Markdown heading for a major section. Folio flows prose, lists and subheadings into two columns. Short introductory passages stay in one narrow column. Major headings, tables, figures and long display equations have the full text width. Put a table next to the passage that explains it and keep its caption close.

Add a captioned figure with `![Caption](figure.pdf)`. Folio places captioned figures in the reading order. PDF suits vector plots. PNG and JPEG suit raster images. Put the images beside the manuscript or refer to them by a project-relative path.

Use a `.keep-together` block for a short list and its lead-in. Use `.reading-columns` when composing the contents of a metric rail or a custom exhibit. You can put short, hand-set equations in that block. For a manuscript whose display math has been fitted to the columns, set `folio-column-math: true` in the YAML. Wrap any wider equation in `.full-width`.

For an illustrated cover, put a portrait image beside `report.md` and set `folio-cover-image: cover.jpg`. Folio crops the image to the page and sets the title, subtitle, byline and date over it. Leave a quiet dark area behind the lettering. Use `folio-cover: true` for a plain separate title page. To add a contents page, set `table-of-contents: true` in `folio.yaml`.

To cite a source, add its record to a BibTeX file, set `bibliography: references.bib` in the manuscript YAML, and cite it with `[@key]`. Folio also supports native Markdown footnotes. [Component reference](components.md)

## Proof and hand off

Read a prose page and an exhibit at actual size. Check where each heading, caption, and list lands when it runs close to the page edge. In tables, follow a value to its column and row labels. Choose relative column widths when labels wrap awkwardly. [Table measures](components.md#tables-and-their-notes)

Folio uses EB Garamond for headings and Source Sans Pro for prose. Edit `layout.tex` to change the page geometry, palette or section styles. Edit `style.tex` for typography and captions. The accompanying template files travel with the project.

```sh
folio-reports build model-review -o model-review/manuscript.tex
```

The exported TeX includes the preamble, body and formatted references. Keep images in the same relative locations when compiling it with Tectonic. A generated project can also build directly with `pandoc --defaults=folio.yaml report.md -o report.pdf` from its directory.

Existing Folio projects continue to use their own settings. To adopt the current template, create a fresh project and copy in your manuscript, figures and bibliography.

## Call Folio from Python

```python
from pathlib import Path

from folio_reports import build, new

project = new(Path("model-review"), title="Evaluation under a review budget")
pdf = build(project)
```
