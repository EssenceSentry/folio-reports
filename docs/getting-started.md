# Author a report

## Create and render

Install Pandoc, Tectonic and Python 3.12 or newer. From the Folio Reports checkout, run `uv tool install --editable .`. Create an editable copy of a starter and render it.

```sh
folio-reports new research transfer-study
folio-reports build transfer-study
```

Both commands print their output path. The default output is `transfer-study/report.pdf`. To publish a copy elsewhere, pass `-o path/to/finding.pdf`. An explicit output path is relative to the shell's working directory. A failed build keeps the previous PDF.

## Write for your reader

For a brief, lead with the action someone can authorize. Use the large number only when you can name what it counts, its denominator, and any assumption behind it. In a research report, put the first figure beside the finding it supports. Use the following sections for the population, method, and practical limits.

The YAML at the top of `report.md` holds the title, subtitle, author and date. Pandoc also accepts multiple authors. To cite a source, put its record in a BibTeX file, set `bibliography: references.bib` in the YAML, and use `[@key]` in the text. Add a captioned image with `![Caption](figure.pdf){width=90%}`. PDF works well for vector plots. PNG and JPEG suit raster images. Replace the sample figure and CSV with your own analysis outputs.

For a short metric with a unit or percentage, use a fenced block. The text on the right supports ordinary Markdown emphasis and links.

````markdown
::: {.metric value="18"}
**Potentially recoverable transfers** among 100 observed rider connections.
:::
````

Use a top-level heading for each section. Both templates paginate automatically. The research example uses a deliberate `\newpage` before its methods. Delete that line for continuous flow. For a longer study, add `table-of-contents: true` to `folio.yaml`. Set `papersize: letter` under `variables` for US Letter.

## Edit the design or hand off the source

The two templates share `style.tex` for body typography, table spacing, captions, and footers. `layout.tex` controls the accent, title and section styles. Both files are copied into each new report. The included TeX Gyre Pagella and Heros font settings resolve from the TeX distribution.

```sh
folio-reports build transfer-study -o transfer-study/manuscript.tex
```

The exported TeX includes the preamble, body, and formatted references. Keep its images in the same relative locations when compiling it with Tectonic. The editable report directory can also be shared in full.

The research example includes the four aggregate observations in `transfers.csv`. To regenerate its vector plot, run `uv run examples/redraw.py transfer-study` from the Folio checkout. It computes the 95% Wilson intervals from the counts. The illustrative 90-second observation threshold describes a possible intervention, not an estimated treatment effect.

## Call Folio from Python

```python
from pathlib import Path
from folio_reports import new, build

project = new("brief", Path("service-review"))
pdf = build(project)
```
