---
name: typography
description: Set or review typography for reports, editorial layouts, PDFs, and reading interfaces. Use for type selection, scale, whitespace, table measure, mixed-script composition, or proofing the rendered result.
---

# Typography

Start where the reader will spend time. In a report, that is usually an interior page with a paragraph, a heading and a table. In a monitor, it may be a row of labels and values. Work with the real text, numbers, language, typefaces and output size. Keep the author’s intended voice. An audit of an existing publication should produce corrections within its design unless the owner asks for a redesign.

**Choose the work the page needs.** Each reference stands on its own.

| When the question is… | Use |
|---|---|
| Which face, size or spacing makes this readable? How should figures, lists, quotations, code and multilingual text be set? | [Text, fonts and tables](references/text-and-tables.md) |
| Why does this page feel empty, crowded or unbalanced? How should a spread, its margins, columns or type scale work? | [Page composition and scale](references/page-and-scale.md) |
| How does the typography hold up across viewport sizes, zoom, color schemes or font loading? | [Reading on screens](references/web.md) |
| How do I inspect a PDF, prepare a press proof, or adapt this to slides or email? | [Proofs and delivery](references/proofs-and-media.md) |
| Which source supports this recommendation, or where did the sources disagree? | [Source coverage and design choices](references/sources.md) |

**Set and compare.** Choose face, size, line length and leading together. Read a full paragraph, follow one number to both its row and column labels, and scan the headings at a glance. Give related material a common edge and less space within the group than between groups. Compare the same content at the same physical size across alternatives. Tune the smallest change that makes the reading task easier. Keep values, significant digits, code, names, links and the meaning of the copy intact.

**Proof and report.** Distinguish what the source declares, what the engine selected, what you saw in a render, and what survived final export or physical printing. For a review, lead with the few fixes that affect reading most. Give each a location, the observation or measurement, its consequence and a specific correction. Flag every material loss of content, legibility, access or delivery. Mention a deliberate feature an editor might otherwise undo. If one choice genuinely depends on taste, show it on the same passage. Mark unverified properties explicitly.

**Working in Folio.** Use `folio-reports build PROJECT -o PROOF.pdf` to inspect a manuscript. In a generated project, `style.tex` controls shared typography, `layout.tex` sets the page geometry and hierarchy, and `folio.yaml` sets Pandoc options. Start a table in Markdown. Use `.table-layout` so its columns have relative widths and its explanatory note follows the same measure. [Worked table](references/text-and-tables.md#fit-a-table-to-its-content)

Use the bundled tools to compare [type scales](scripts/type_scale.py), measure [a region of a PDF](scripts/proof_pdf.py), inspect [press and export details](scripts/preflight_pdf.py), check [color contrast](scripts/contrast.py), or measure [live browser text](assets/measure-browser.js). The relevant reference explains how to run and interpret each tool. A clean tool report still needs a reader’s eye.
