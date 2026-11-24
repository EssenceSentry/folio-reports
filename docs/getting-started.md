# Author a report

## Create and render

Install Pandoc, Tectonic, uv and Python 3.12 or newer. Install the Folio Reports CLI from GitHub, then start your own research report with its title and byline.

```sh
uv tool install git+https://github.com/EssenceSentry/folio-reports.git
folio-reports new research transfer-study --title "Morning transfers: pilot results" --author "Service Planning"
folio-reports build transfer-study
```

Open `transfer-study/report.md` and write below the closing `---`. The title and byline remain editable in the YAML at the top. Either `--title` or `--author` starts a clean manuscript and leaves out the example figures, data and bibliography. Use `--blank` on its own to start with “Untitled report”. All three layouts support these options and keep their styles and components.

To explore a worked example, run `folio-reports new research transfer-example` and build that directory. The `brief` starter demonstrates a short decision memo and `specimen` showcases the component library.

Both `new` and `build` print their output path. The default output is `transfer-study/report.pdf`. To publish a copy elsewhere, pass `-o path/to/finding.pdf`. An explicit output path is relative to the shell's working directory. A failed build keeps the previous PDF.

## Preview the same report in another style

Run `folio-reports styles` for the names and visual descriptions. Choose a default when you create a project, or pass a temporary choice when you build.

```sh
folio-reports new research ridership --style ledger
folio-reports build ridership --style gazette -o gazette-proof.pdf
```

The saved choice is `metadata.folio-style` in `folio.yaml`. The files in `styles/` travel with your project and can be edited directly. The most recent style layer takes precedence over the shared typography. A project created with the first version of Folio still builds using its original files. To use the new styles in such a report, generate a fresh project and copy your manuscript, figures and bibliography into it. Bring across your own layout changes selectively.

For a separate title page, set `folio-cover: true` in the manuscript's YAML. Add `table-of-contents: true` to the top level of `folio.yaml` for navigation in a long report. The `specimen` starter uses a compact page for its component sheets. The other starters default to A4.

## Write for your reader

For a brief, lead with the action someone can authorize. Use the large number only when you can name what it counts, its denominator, and any assumption behind it. In a research report, put the first figure beside the finding it supports. Use the following sections for the population, method, and practical limits.

Use the YAML at the top of `report.md` for the title, subtitle, author and date. Pandoc also accepts multiple authors. To cite a source, put its record in a BibTeX file, set `bibliography: references.bib` in the YAML, and use `[@key]` in the text. Add a captioned image with `![Caption](figure.pdf){width=90%}`. PDF works well for vector plots. PNG and JPEG suit raster images. Put your own figures beside the manuscript or refer to them by a project-relative path.

For a short metric with a unit or percentage, use a fenced block. The text on the right supports ordinary Markdown emphasis and links.

````markdown
::: {.metric value="18"}
**Potentially recoverable transfers** among 100 observed rider connections.
:::
````

Use a top-level heading for each section. All three layouts paginate automatically. The research example uses a deliberate `\newpage` before its methods. Delete that line for continuous flow. For a longer study, add `table-of-contents: true` to `folio.yaml`. Set `papersize: letter` under `variables` for US Letter.

## Edit the design or hand off the source

The starters share `style.tex` for body typography, table spacing, captions, and footers. `layout.tex` controls the accent, title and section styles. Both files are copied into each new report. The included TeX Gyre Pagella and Heros font settings resolve from the TeX distribution.

```sh
folio-reports build transfer-study -o transfer-study/manuscript.tex
```

The exported TeX includes the preamble, body, and formatted references. Keep its images in the same relative locations when compiling it with Tectonic. The editable report directory can also be shared in full.

The research example includes the four aggregate observations in `transfers.csv`. To regenerate its vector plot, run `uv run examples/redraw.py transfer-example` from the Folio checkout. It computes the 95% Wilson intervals from the counts. The 90-second threshold identifies visits where a hold might have helped. Estimating its effect requires a trial.

## Call Folio from Python

```python
from pathlib import Path
from folio_reports import new, build

project = new("brief", Path("service-review"), title="Review of the pilot")
pdf = build(project)
```
