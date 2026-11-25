# Proofs and delivery

Choose the proof that matches how someone will receive the work. A laptop PDF, a stapled office handout, a bound book and a projected slide can share a manuscript and need different settings. Keep corrected text, notes, data and links intact through the export.

## Read the final PDF

Build through the same route the recipient will use. Open at reading size, zoom in on fragile detail, and scan the sequence as small pages. Inspect a prose page, a dense table, a page break and the final page. Check the actual rendering of fractions, minus signs, superscripts and small caps. For print, fold or bind a physical proof at 100% when the gutter, paper or trim matters. For a screen PDF, also open at laptop fit-width. A typical A4 report is worth trying at 10.5–12 pt body. Test selectable text, copy order, accents, equations, link targets and bookmarks.

Use the small Poppler helper when you know the page, the column or the element. Run from the folder containing `SKILL.md`. Coordinates are PDF points from the top left (72 points to an inch). Start with a whole page, then select a rectangle with complete lines from one role.

```sh
python3 scripts/proof_pdf.py report.pdf --page 2
python3 scripts/proof_pdf.py report.pdf --page 2 --region 85,150,445,350 --show-lines
pdftoppm -f 2 -l 2 -r 120 -singlefile -png report.pdf /tmp/folio-page2
```

`pdftotext` is required for this helper. `pdfinfo` supplies page boxes and document facts, `pdffonts` lists embedding and `pdftohtml` supplies approximate font runs at unit zoom. Isolate prose before interpreting characters per line. An extractor may split a sentence or combine words differently from a reader. Its bounds describe extracted text, excluding rules and figures. Its within-block pitch is measured between line tops. Mixed fonts, headings, superscripts and table cells can all distort the estimate.

Use the [production inspector](../scripts/preflight_pdf.py) when font substitution, output intent, unusual page geometry, press colors or whole-document text metrics matter. Run `python3 -I scripts/preflight_pdf.py report.pdf --pages 20`. It uses qpdf for structure and Ghostscript for glyphs. Each can report independently if the other is unavailable. Compare intended and embedded families, subset and font type, tagging and language, explicit trim and bleed boxes, rotation, approximate margins, size shares, likely body face, full-line measure and character candidates. A dash flag may be a correct identifier. The most common size on a slide or ledger may belong to labels. Inspect the actual role.

**A Folio example.** On page two of the repository’s research example, the four **Observed riders** counts sit on the same right edge. The table and its note have a shorter measure than the paragraph above. The note still belongs visibly to the figures and wraps before reaching the prose edge. The rectangle above gives approximately 350 pt between the outermost extracted text edges. Its median line length is just three characters because the sample contains many numeric cells. Use a paragraph-only rectangle to evaluate reading measure. The fonts are embedded and the text is extractable. The PDF reports `Tagged: no`. If the deliverable requires an accessible screen PDF, the next correction is in export and semantic tagging. [Folio research report](https://github.com/EssenceSentry/folio-reports/blob/b4035bfd3d2f151722fc33a0a902edb4fe84e40c/examples/research-report.pdf)

## Pagination and production

- **Office and book pages.** Check recurring folios, running heads, section openers, first and last lines stranded across breaks, short final words, adjacent hyphens, spacing around displays and floated captions. Use paragraph styles, keep controls, language-aware hyphenation and real breaks. In justified work, inspect word-space extremes, keep consecutive hyphenated lines rare and check the last line of a column. Narrow captions, URLs and display headings usually need their own hyphenation or line-break decisions. Try adjusting the measure or editing a nearby phrase with the author’s approval before tightening an entire page. In a spread, hold recto and verso to the light when backing-up on thin stock matters.
- **Screen PDF.** Verify the title, document language, headings and lists, header associations for data tables, meaningful figure descriptions, decorative artifacts, bookmarks, links and reading order. Inspect the tag tree and traverse the result using the intended reader technology. Test text contrast and zoom. Selectable text and the presence of a tag root establish only a small part of accessibility. Use the requested PDF/UA profile and its validator when conformance is a deliverable.
- **Commercial press.** Obtain the printer’s profile, trim, bleed, binding, stock and output-intent requirements. PDF/X-4 is a common color-managed target. The printer may require PDF/X-1a. Verify the output intent and validate the final export to the requested profile. Embed licensed fonts. Investigate unexpected substitutions, Type 3 body fonts or outlined prose. Keep normal text searchable and vector. Review effective image resolution at printed size, often around 300 ppi for continuous-tone work.
- **Ink and trim.** For ordinary small black press type use the printer’s single black plate, commonly 100% K. Check overprint, trapping and separations on the exported job. Reserve rich black for large solids within the stock’s ink limit. Keep registration black out of artwork. Confirm spot or process color with a physical proof. On uncoated paper, look at counters, hairlines and reversed white type after dot gain. A starting brief might call for 3 mm bleed and 3–5 mm safety, subject to the printer and binding. The helper counts color operators used for fills and strokes. Confirm which actual text or object uses the color. A page box, a color token or a profile name alone cannot certify the printed result.
- **Printing from HTML.** Specify physical page size, margins, body size in pt and leading. Hide controls and navigation, preserve meaningful labels, check note and table breaks, and repeat headings. Include printed link destinations selectively where the reader needs them. Use paged-media support for running heads, folios and distinct opening pages when the receiving renderer supports it. Inspect the exported PDF with its actual fonts.

## Other reading settings

**Slides.** Set a base at the actual viewing distance. Fitting roughly 12–15 lines is a calibration exercise. Put considerably less on a real slide. Keep title, body and attribution distinct, disable text auto-shrink and edit a crowded slide. Check the farthest seat, the projected contrast and fine chart labels in the room’s lighting.

**Email and editable documents.** Choose an available system face, simple spacing and robust fallbacks. Preserve selectable contact information, links and document styles. Open the message or editable file in the recipient’s client and check the plain-text path when it matters.

**Résumés.** Give the decisive experience and dates a clear reading order. Follow a required template or length. Forcing everything into one page by shrinking it can cost legibility. Test a text extraction if an applicant-tracking system is part of delivery, then open the actual PDF. Proof content separately.
