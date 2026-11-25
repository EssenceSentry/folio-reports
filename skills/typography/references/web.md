# Reading on screens

Start with one passage, one link and the densest label or data row. Read them at the reader’s normal font setting and in each supported color scheme. A family in a stylesheet, a computed value, and the glyph actually drawn on screen are different pieces of evidence.

## Reading size and reflow

Leave the root size relative to the reader’s preference. Give components rem or em sizes and flowing text unitless leading. Start sustained reading around 17–20 CSS px at a 16 px default root. These three English-prose specimens from the Practical Typography skill are alternatives worth laying out with the same copy.

| Specimen | Body and leading | Paragraph and measure |
|---|---|---|
| Bookish | 17–18 px at 1.3–1.4 | Serif text, first-line indents, moderate line length |
| Airy | 19–21 px at 1.5–1.6 | Shorter lines and visible space between paragraphs |
| Compact documentation | 15–17 px at 1.35–1.45 | Modest gaps and a wider column. Proof the small end closely. |

Size the column around real lines. A width in `ch` measures the zero glyph. Count a few full lines including spaces or try fitting two or three lowercase alphabets across the column as a rough check. Allow the column to narrow on a phone. Use logical start alignment for running text. Justified text needs the correct language, working hyphenation and enough width to avoid loose word spacing. Balance a short heading if it improves the phrase break. Proof a wrapped title, an unbroken identifier and enlarged error text.

For fluid display type, give `clamp()` relative bounds and a preferred value mixing rem and viewport width. Start with a fixed or gently changing body. Compare endpoints if any role grows more than 2.5×. Set spacing in a consistent direction and give headings room to wrap. To diagnose a claimed baseline grid, place a zero-height inline-block baseline marker in several real lines and measure its position relative to the grid origin. Repeat on lines with inline code, icons and superscripts and in components that span rows. The top of a line box measures a different thing.

## Font delivery and optical checks

Keep weights and styles under one family name with correct descriptors. Deliver the scripts and weights in use, e.g. WOFF2 with appropriate language coverage. Prioritize only the faces needed for the first reading view. Match any preload’s URL, type and cross-origin mode to the font request. Choose `font-display` for the tradeoff between early text and later swap. Proof a cold load, a blocked webfont and fallback with a longer string. Where needed, measure fallback metrics, adjust `size-adjust` or ascent/descent/line-gap overrides, and check for a shifted heading or control.

Use real bold and italic and confirm the variable font contains the requested axes and ranges. When font-display swapping changes line breaks, check the fallback before adding another webfont. Check kerning, suitable ligatures and optical sizing in the rendered face. Set tabular numbers in comparable columns. Avoid global font smoothing or blanket negative tracking. Use tracking on a particular display role only after seeing the actual letter pairs. Inspect cap-height alignment in buttons, the first visible edge of a headline, and the gap between an icon or chevron and its control’s edge.

## Links, contrast and accessibility

Give links in prose a readily visible cue. An underline that clears descenders, with weight and offset tuned to the face, is a reliable choice. As a specimen, try 0.07 em thick at a 0.14 em offset with ink skipping. Keep keyboard focus distinct. Color alone is insufficient for conveying an error, selection or required action. Check hover, focus, visited links, placeholders, muted metadata and validation text in light and dark themes. Evaluate the weakest background beneath text over an image, gradient or translucent layer at each crop.

For WCAG 2.2 text contrast, ordinary text needs 4.5:1 for AA, or 7:1 for AAA. Large text begins at 18 pt regular or 14 pt bold, approximately 24 or 18.67 CSS px, and needs 3:1 for AA or 4.5:1 for AAA. Apply the criterion’s exceptions where appropriate. Keep each color at full precision before judging the threshold. APCA Lc provides a supplementary, polarity-sensitive reading check. Guillot’s working targets range from an absolute Lc of roughly 75–90 for reading text to 45 for sufficiently large headlines. Small or light text deserves more. Examine type and background together before choosing a fix. [WCAG text contrast](https://www.w3.org/TR/WCAG22/#contrast-minimum)

Allow browser zoom and pinch zoom. Test 200% text resizing, reflow at 320 CSS px and author-independent spacing overrides (1.5× line height, 2 em paragraph spacing, 0.12 em letter spacing, 0.16 em word spacing). Look for clipped characters, overlapping controls, lost content or an impossible reading direction. A table that genuinely needs two dimensions can scroll locally. These are resilience tests. For dark mode, compare the actual small text on its background. Try adjusting weight, leading or the brightness of the pair if fine strokes disappear or bright text blooms. Preserve the reader’s contrast and theme settings. [WCAG resize, reflow and text spacing](https://www.w3.org/TR/WCAG22/#reflow)

## Measure the delivered page

Run [the browser probe](../assets/measure-browser.js) through the browser’s evaluation interface on the target page. In Python Playwright with a loaded `page` and the skill folder as the working directory:

```python
from pathlib import Path

probe = Path("assets/measure-browser.js").read_text(encoding="utf-8")
for width in (375, 1280):
    page.set_viewport_size({"width": width, "height": 900})
    for scheme in ("light", "dark"):
        page.emulate_media(color_scheme=scheme)
        evidence = page.evaluate(probe)
        for role in evidence["roles"]:
            print(width, scheme, role["role"], role["sizePx"], role["contrast"])
```

The probe waits for font loading and samples distinct visible text styles. It records computed sizes, weights, likely face, color pairs, links, optical alignment, line and measure estimates, loaded faces, preloads and observable stylesheets. Confirm the rendered font with browser font tools if a missing face would change the verdict. Repeat after opening relevant components. A sample can miss variants of the same role, inaccessible stylesheets, image pixels and states outside the tested page. Verify a representative color pair independently when needed:

```sh
python3 scripts/contrast.py '#38465a' '#fff' --size 16 --weight 400
python3 scripts/contrast.py '#ffffffcc' '#243549' --canvas '#101010'
```
