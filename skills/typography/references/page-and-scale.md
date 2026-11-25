# Page composition and scale

**Construct from both directions.** The text gives you a comfortable line and leading. The page gives you a physical size, binding, reading distance and material to place. Put an actual heading, two paragraphs, a figure or table, its caption and a note on the page. Adjust the text and the block until both work. Keep the reader’s entry point and the direction of reading visible at thumbnail size.

## Margins, fields and empty space

A4 suits office printing and halves at the same aspect ratio. A 2:3 page is a useful book starting point. A golden-ratio or custom format can fit a narrower book or an image-led spread. Choose a format the intended printer, device or binding can deliver.

For a 2:3 facing-page book, try an inner margin of one ninth of page width, an outer margin of two ninths, a top margin of one ninth of height and a bottom margin of two ninths. In a single unit those margins are **2 / 3 / 4 / 6**. A **1 / 1 / 2 / 3** construction gives a different text block. Mirror facing pages and allow for binding loss in the gutter. A single-sided report or a slide has a different reading geometry. An ample foot can ground a page. The available text measure and a printed spread decide the final proportions.

Draw only the alignments the content uses. A metadata column beside a title needs one decisive secondary edge. For a series with many different tables, diagrams and pull quotes, a modular grid of 8–32 fields gives more choices. A six-by-six construction can accommodate halves, thirds and groups of six. Reuse a few divisions across pages. Try gutters around two ems and adjust until the eye returns to the correct column. Align table notes and captions with the objects they explain. A table can occupy seven eighths of the prose width and still clearly belong to the page.

In an asymmetric spread, concentrate the main visual weight on an axis. Leave space opposite it and place a smaller element where it leads the eye onward. Look for a clear entry, a second place to look and an identifiable edge shared by both. If the layout feels inert, cover the ornaments and see whether the type, positions and empty regions still describe a reading order. Symmetry can give a title page, dedication or chapter opener ceremony. On a screen, preserve the relationships when columns collapse and check intermediate widths. Halving fields is one useful construction.

## Rhythm and type scale

Use body leading as the baseline unit when readers scan adjacent columns or facing pages. At 10/14 pt, 30 lines occupy 420 pt. A figure with a caption can occupy a whole number of those lines so the prose resumes in alignment. Half steps can help headings and compact captions. Let an opener or full-page figure interrupt the rhythm deliberately. Read both columns after a proof change. Forcing a caption or a wrapped heading into an undersized line box can obscure its meaning.

Choose the few roles that actually occur. Compare a classical sequence such as 10, 12, 14, 18, 24, 36 or 48 pt with modular steps. Ratios near **1.125–1.2** suit dense instruments and modest book headings. Try **1.25** for documentation, **1.333** for stronger editorial contrast and **1.5–1.618** for a short display-led piece. Two related scales can separate display and data annotation. Hierarchy also comes from weight, placement, spacing and face. Prune unused levels. Test the smallest annotation and the longest headline.

Run commands from the folder containing `SKILL.md`. The calculator holds the body constant when comparing ratios, uses gentler steps below it, and can snap leading to full or half grid units. It prints a role spec or JSON. With `--medium web` it can also export CSS or Tailwind v4 theme variables.

```sh
python3 scripts/type_scale.py --medium print --base 11 --leading 1.3 --ratios 1.2,1.25 --up 3
python3 scripts/type_scale.py --medium web --base 16 --base-max 18 --ratios 1.25 --ratio-max 1.333 --format css
```

For web CSS the reference root is 16 px. Generated rem bounds and intercept preserve a contribution from the reader’s font size. Match the stylesheet to the real root and test zoom. Use unitless leading for free-flowing text when a grid adds no value. If aligning different faces to a strict baseline, measure ascent and descent in the rendered face. Identical line boxes can place the ink differently. Test custom `--grid`, `--ratio-down` and viewport settings on the actual text before committing them.

The export maps the available steps to h1–h6 and includes tracking suggestions for display sizes. Read the actual pair before tightening a heading. Preserve the semantic heading order even if two levels share a size. The JSON is a role spec with numeric endpoints. CSS and Tailwind v4 exports include the variables and heading rules.

For a page that requires aligned baselines, obtain the body face’s ascent and descent in the same font and coordinate system. In a canvas configured to the loaded face at 100 px, subtract `fontBoundingBoxDescent` from `fontBoundingBoxAscent` and divide by 200. For example, `--grid 24 --k 0.36 --format css --medium web` emits an opt-in `.type-baseline` offset. Apply it only to a leaf text block whose layout edge already starts on a grid line. Measure again for other faces. Fluid line heights interpolate between the computed endpoints. For a strict grid across widths use fixed sizes or resnap at each breakpoint and check actual baselines.
