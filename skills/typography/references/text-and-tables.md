# Text, fonts and tables

## Set the paragraph

Proof an ordinary paragraph at its intended reading distance using the delivery device or page. Include a long word, punctuation, an italic, a number and a name from the actual manuscript. Start English-language print prose around **10–12 pt**, leading at **120–145%** of point size, and lines of **45–90 characters including spaces**. For sustained, single-column reading, aim initially for 55–75, often near 66. Start narrower for parallel columns, around 40–50. Count complete lines from the proof, leaving aside the short last line of each paragraph. A broad lowercase face fits fewer characters than a narrow face at the same setting.

Read across the longest line and return to the left edge. If you lose your place, narrow the measure or open the leading, one change per proof. If the page looks loose, check the spaces inside paragraphs before reducing the space between sections. A compact face with a large x-height may carry a dense caption at a smaller point size. Confirm in the delivered medium.

Use a first-line indent or a gap to mark paragraphs. For a book, try one em of indent and set the paragraph after a heading or break flush. For a brief, a modest gap often gives faster scanning. Keep long prose on a stable reading edge appropriate to the script. Justification works when the language, hyphenation, column width and composer give even word spaces. Check for rivers, repeated line-end hyphens, a divided last word and bad breaks across pages. Narrow columns and captions often benefit from an even rag. Break display lines at phrases.

## Select faces and establish roles

- Read the body sample in a **text cut**. Compare counters, x-height, character width, punctuation, bold and italic at final size. A display cut can give a title character at a size where its fine strokes hold up. Check optical-size axes and real small caps, italics, weights and numeral features in the files that will ship.
- Try a single family first. Add a companion with a distinct job and compatible proportions, such as sans-serif annotations beside serif prose. A related superfamily is a good proof candidate. Give code its own face if needed. Source Serif, IBM Plex and Charter are useful starting specimens. Check each face’s availability, license for the intended distribution or embedding, language coverage, and behavior with fallback. Preserve diacritics and unfamiliar names.
- Give each structural role a reusable style. A change of alignment, space, weight, size or face can make a level distinct. Keep headings closer to their first paragraph than to the preceding section. Twice as much space above as below is a useful proof to try. Let important headings travel with several lines of text. Use a single, brief signal for emphasis. Reserve underlining for links or an established domain convention.
- Give lists real markers, hanging indents and automatic numbering. Align wrapped lines with their item text. Distinguish block quotations with one clear device, such as an inset or a change of face. Duplicate quotation marks and stacked decoration often add noise. Keep the original wording and attribution.

## Compose the actual characters

Set language-appropriate quotation marks, including an apostrophe for an omitted beginning (’90s). Distinguish a hyphen in a compound, an en dash for a range, a minus sign in a calculation and a prose dash in the chosen house style. Use an ellipsis for an editorial pause. Keep numbers with units, figure and section numbers with labels, and a copyright mark with its date when a break would confuse. Use a single sentence space. Choose a real multiplication sign, prime or ordinal glyph when warranted by meaning and supported by the font. Check paired delimiters and nested quotation. Preserve legal paragraph labels such as `12(c)`.

Keep metric kerning and inspect normal text ligatures where the face supports them. Use modest tracking on short capitals or real small caps, initially around 0.05–0.12 em for Latin text. Keep lowercase prose at its designed spacing. For display type, examine the actual ink at shared edges. An opening quote, a capital A or a large round numeral may need an optical adjustment. A centered badge reads from the cap height or x-height. Check round icons and triangular marks beside text at their actual size.

Protect exact strings before substitutions. Commands, JSON, URLs, filenames, identifiers, quoted data and code must remain copyable with the same characters and whitespace. Choose code fonts with distinct `0/O` and `1/l/I`. Disable discretionary joining that obscures `!=` or `=>`. Use the font’s glyph shaping for ligatures in prose and preserve the original searchable characters.

## Fit a table to its content

Identify the comparison first. Set the values, then the headings, then the width for the row labels. Right-align comparable integers. Align decimals by place where useful and preserve meaningful trailing zeros, units, negative signs and missing values. Use tabular figures for vertical comparisons and lining or oldstyle forms according to their role. Identifiers with leading zeros have their own meaning. A reader should be able to follow a value up to its heading and left to its label without losing the row.

Try content width for a few short numbers and a wider measure for explanatory columns. Reserve enough room for the longest meaningful label and its wrapped lines. Keep unlike groups farther apart than figures within a group. Use light horizontal rules at meaningful boundaries, padding that separates rows, and a quieter note clearly attached to the table. Put the table title above when readers need it to interpret the values. Keep a figure’s explanatory caption close below it. Use a readable caption size and sufficient contrast. Long tables can break between rows with repeated headings and units. Keep short tables and their notes together when they fit.

A Folio decision table may devote four parts to the proposed action for each part given to its label. In this numeric example the entire table occupies three quarters of the reading column. The note wraps within the same width. These are adjustable editorial choices.

```markdown
::: {.table-layout widths="2,1,1" width="75%"}

| **Departure** | **Observed** | **Missed** |
|:--------------|-------------:|-----------:|
| 07:10         |          100 |          8 |
| 08:10         |          100 |         29 |

Counts cover riders attempting a transfer.
:::
```

## International and mixed-script text

Establish language and direction for the document and for distinct runs. The character counts and tracking examples above describe Latin typography. Use local quotation, decimal, grouping, line-break and emphasis conventions. For Arabic check shaping, joining and marks. Check Hebrew or Arabic mixed with numbers and Latin in visual order and copy order. For CJK, verify punctuation placement and permitted line breaks. Thai, Khmer and Lao may need dictionary-based segmentation. Preserve combining marks, emoji sequences and variation selectors. Inspect fallback glyphs, baselines and punctuation next to the primary face. For unfamiliar conventions use a language-specific reference and leave ambiguous text intact. [W3C language layout resources](https://www.w3.org/International/layout)
