# Report components

To start with a working example, run `folio-reports new specimen my-components`. Open the generated `report.md` beside its PDF. Every entry below works in a brief, research report or specimen, in any of the ten styles.

## Findings and decisions

A fenced block adds a component. Its body accepts ordinary Markdown paragraphs, links, emphasis and lists. Each of these callouts has a default heading. Override it with `title="..."`.

| Block | Use it for |
|---|---|
| `.summary` | The question, the result and what the reader should do with it |
| `.finding` | A result supported by the evidence on the page |
| `.recommendation` | A proposed action |
| `.decision` | A choice that has been made or needs authorization |
| `.risk` | A possible adverse outcome and how to watch for it |
| `.limitation` | A boundary on what can be inferred |
| `.assumption` | A condition on which the analysis depends |
| `.method` | The procedure that produced the result |
| `.definition` | The meaning of a term or the rule for counting something |
| `.note` | A short practical detail |

````markdown
::: {.finding title="When readers arrive"}
Of 200 recorded visits, **72 began after 18:00**.
:::
````

## Tables and their notes

Use an ordinary Markdown table for a small comparison at its natural width. Wrap it in `.table-layout` to choose its measure. The brief gives four parts of the width to the decision text for every one part given to its label. The research report groups its four columns and explanatory note within seven eighths of the reading column.

````markdown
::: {.table-layout widths="2,1,1" width="75%"}

| **Departure** | **Observed** | **Missed** |
|:--------------|-------------:|-----------:|
| 07:10         |          100 |          8 |
| 08:10         |          100 |         29 |

Counts refer to riders attempting a transfer.
:::
````

Give one positive weight per column. The optional `width` is a percentage of the available line, defaulting to 100%. Markdown controls the alignment of each column. A paragraph below the table becomes a smaller note with the same left and right boundaries. The native table can still carry a caption and continue across pages with repeated headers.

## Numbers, comparisons and charts

| Block | Inputs and visual encoding |
|---|---|
| `.metric` | A short `value` and a Markdown body naming the unit and denominator |
| `.scorecard` | Two to four nested `.measure` blocks with `value`, `label` and an optional short explanation |
| `.comparison` | Two nested `.column` blocks with a `title` and short prose or lists |
| `.bar` | `label` and `value` from 0 to 100. Length encodes the percentage on a common baseline |
| `.interval` | `label`, `low`, `value`, `high` on a 0–100 percent scale. A dot and whiskers show the estimate and bounds |
| `.intervalplot` | A shared numeric axis for several estimates and intervals, with an optional reference and an exact-value table. Each nested `.row` supplies `label`, `low`, `value` and `high` |
| `.trend` | `values` as comma-separated observations, explicit `min` and `max`, a `label` with units, and `start` and `end` labels. Observations are equally spaced. Series of up to twelve observations show a dot at each sample |
| `.distribution` | Five comma-separated values in `summary` giving the lower whisker, first quartile, median, third quartile and upper whisker. Supply axis `min`, `max`, and a descriptive `label` |
| `.heatmap` | Two to six `columns` separated by vertical bars, a `label`, `min`, `max` and optional `stub` heading. Each nested `.row` supplies a label and matching numeric values. Every cell prints its value |

Values and intervals come from the author's analysis. Supply the meaning and level of an interval in its label. Group comparable bars or intervals on the same scale. For unequal time intervals or a model-specific display, include a captioned vector figure from your analysis.

````markdown
::::: {.scorecard}
::: {.measure value="200" label="Observed visits"}
Across four weeks.
:::
::: {.measure value="72" label="Evening visits"}
Arrivals after 18:00.
:::
:::::

::: {.interval label="Evening visits · 95% Wilson interval" low="29.7" value="36" high="42.9"}
:::

::: {.trend label="Visits per week" min="0" max="30" start="Week 1" end="Week 4" values="12,16,20,24"}
:::
````

### Compare estimates on one axis

Use `.intervalplot` for signed differences, counts, percentages or other estimates in a common unit. Set `min` and `max` to cover every interval, and give the units in `label`. The dot marks the estimate. The whiskers and the numeric interval column give its bounds. An optional `reference` draws a dashed mark at the same value in each row. Set `stub` to name the row groups and `interval-label` to describe the bounds.

````markdown
::::: {.intervalplot label="Change in evening share (percentage points)" min="-20" max="50" reference="0" stub="Comparison" interval-label="95% interval"}
::: {.row label="Week 2 vs 1" low="-9.5" value="+8" high="+24.9"}
:::
::: {.row label="Week 4 vs 1" low="+5.2" value="+24" high="+40.6"}
:::
:::::
````

Each row uses author-supplied numbers in the order `low <= value <= high`. Include the interval method and sample sizes in the surrounding prose. The plot keeps the supplied numeric precision in its table and repeats its headers across page breaks.

Use attribute-only blocks for bars, intervals, trends, distribution plots and heatmap rows. Keep scorecards, comparisons and flows short enough to read together on one page. For long comparisons, use a Markdown table or separate sections.

## Workflows and evidence

| Component | Authoring convention |
|---|---|
| `.milestone` | `when="Week 1"` above the event description. Repeat for a timeline |
| `.action` | `owner="Evening supervisor"` above the action and deadline |
| `.flow` | An ordered list of two to four short steps rendered side by side |
| `.check` | `state="open"` or `state="done"` plus the checklist item |
| `.status` | An inline label, for example `[Pending review]{.status}` |
| `.pullquote` | Quoted text with an optional `by="..."` attribution |
| `.source` | Source, measurement window or provenance below the associated evidence |
| `.signature` | `name="Branch manager"` above a brief explanation of what is being signed |

## Report structure and native Markdown

| Feature | How to use it |
|---|---|
| Separate cover | Add `folio-cover: true` to the manuscript's YAML along with title, author, date and optional subtitle |
| Contents | Add `table-of-contents: true` to `folio.yaml` |
| Scene or section divider | Empty `.divider` block with `title="Pilot calendar"` |
| Controlled page turn | Empty `.pagebreak` block. Regular prose and callouts can flow across pages |
| Lettered appendix | Empty `.appendix` block followed by a top-level heading |
| Tables and definitions | Use a Markdown pipe table or Pandoc definition list |
| Figures, photographs and diagrams | `![Caption](figure.pdf){width=90%}`. Use PDF for vectors and PNG or JPEG for photographs and other raster images |
| Equations and code | Use dollar-delimited inline or display math and fenced code with a language name |
| Footnotes and references | Use Markdown footnotes, a BibTeX file in `bibliography`, and citations such as `[@wilson1927]` |

## Rebuild the visual catalog

From the checkout, run `uv run --with-editable . --script examples/build_catalog.py`. The command builds the brief, research report and specimen, then typesets the same brief in all ten styles for the bookmarked lookbook. The page spreads and masthead preview come from those PDFs. The authoring CLI needs Pandoc and Tectonic. The catalog script also uses Poppler's `pdftoppm` and installs its own Python image and PDF dependencies through uv.
