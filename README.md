# Folio Reports

Write the finding in Markdown. Give the person reading it a PDF they can take into a meeting, annotate, or print. Folio supplies the typography, figure captions, tables, and page furniture. You own the text and the LaTeX in each project.

[Open the decision brief](examples/decision-brief.pdf) · [Open the research report](examples/research-report.pdf)

![A one-page decision brief and both pages of a research report on the same transit pilot.](examples/report-previews.webp)

## Choose a starting point

| If your reader needs to… | Start with |
|---|---|
| Approve a change, understand its size, and know who acts next | **Brief.** A compact sans-serif headline, a prominent metric, and a short action table. |
| Inspect a result, follow the method, and judge its limits | **Research.** A serif title, numbered sections, vector figures, equations, and a bibliography. |

Both examples use the same synthetic transit observations. The brief proposes a 90-second hold. The report shows why a particular departure warrants a trial and what the counts can establish.

## Make your first report

Install [Pandoc](https://pandoc.org/installing.html) and [Tectonic](https://tectonic-typesetting.github.io/), then install the CLI from this checkout with Python 3.12 or newer.

```sh
uv tool install --editable .
folio-reports new brief my-brief
folio-reports build my-brief
```

Open `my-brief/report.pdf`. Edit `my-brief/report.md` and run the build again. For the longer format, use `folio-reports new research my-study`. Tectonic downloads its TeX packages on the first build.

## Make it yours

- Change the title, subtitle, authors and date at the top of `report.md`. The body accepts Markdown tables, math, footnotes, citations, local figures, and raw LaTeX.
- Set margins, paper size and Pandoc options in `folio.yaml`. Edit `layout.tex` for the title treatment and accent color, or `style.tex` for the typefaces and shared styling.
- Give a designer editable LaTeX with `folio-reports build my-brief -o my-brief/manuscript.tex`. Keep figures beside the source when sharing it.
- Build a generated project directly with `pandoc --defaults=folio.yaml report.md -o report.pdf` from its directory.

[Authoring guide](docs/getting-started.md) · [Template sources](src/folio_reports/templates) · [Development](DEVELOPMENT.md)
