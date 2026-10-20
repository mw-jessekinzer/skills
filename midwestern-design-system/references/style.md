# The style: Swiss editorial

Every Midwestern deck and document uses one style. It comes from the recruiting packet system JK approved ("F") and the contract-to-hire leave-behind (v4a). Hierarchy comes from size, space and one accent color, never from boxes, lines or weight.

## Rules you can check

**Grid**
- Documents (US Letter, 816 x 1056px at 96 per inch): 4 columns of 164px, 16px gutters, 56px margins top and sides, 88px footer band.
- Slides (1920 x 1080): 12 columns, 32px gutters, 96px side margins, 88px top, content ends 152px above the bottom.
- Every left edge sits on a column line. Use the `at-N` (start column) and `w-N` (span) classes; never nudge with pixels.
- The document hang: labels in column 1, reading text in columns 2 to 3 (about 60 characters a line), a quiet aside in column 4. Slides: title across columns 1 to 9, content on the same 12 columns below.

**Type**
- Documents, 8 sizes: 8.5 footer / 10.5 labels and tables / 11.5 body / 16 lead / 24 quote / 36 page title / 64 display / 80 hero (px).
- Slides, 8 sizes: 20 footer / 24 labels / 32 body / 44 lead / 72 title and quote / 120 display / 280 one big number (px).
- Minimum size: documents 10.5px for any content (8.5px is the footer only); slides 24px for any content (20px is the footer only).
- One weight, Regular (400). Headings are Regular. `strong` renders Regular. No bold, no italic, no underline for emphasis.
- Flush left, ragged right. Nothing centered, nothing justified.
- Tight display type: line-height 1.0 to 1.1 and negative tracking on titles and figures (the tokens do this).
- Tabular figures on every number (set globally).

**Structure**
- Titles at the top of every page and slide, under a small muted kicker. Never at the foot.
- One idea per slide. One section per page; every major section starts a new page.
- Say each fact once. The headline states the outcome in words; the figure carries the number; that is one mention. A figure never restates the title in numbers. A figure row and a chart on the same page never show the same numbers: replace the repeat with a rate. Say-once removes repeats, never substance.
- Titles state the finding. "Design roles take longest to fill" passes; "By role family" fails.
- A big numeral only where the number is the message. Its unit or maximum sits beside it, small and muted; a qualifier ("under") sits before it in `fig-pre`. Never "<", "~" or "+" in a figure.
- A figure is number, unit beside it, label on the next line under the number, all in one column span. Never split a figure's label into another column.
- A title that names a number, share or slice ("a third of meetings") needs that number on the page, as a figure ("3 of 9") or a bar.
- Color pages carry the most important content: in a document, at most 1 dark page and 2 blue pages; in a deck, at most 2 blue slides. The rest is paper (documents) or near-black (decks).

**Lines**
- One weight: 0.5pt (1px on a 1920 slide, which is 0.5pt at 13.33 inches).
- Lines only where data is tabular: honest tables, one chart axis. Nowhere else.

**Space**
- Designed space is good. A page or slide that is 50 to 70% empty is normal.
- Accidental space is not: no 1 or 2 line spill onto a new page, no lone block stranded on a page. A block pushed to the page foot with a void above it counts as stranded: follow the last block at the normal step instead.
- Spacing uses the token steps only (`mt-1` to `mt-9`). Documents: 4, 8, 12, 16, 24, 32, 48, 64, 96px. Slides: 8, 16, 24, 32, 48, 64, 96, 128, 192px.

**Data graphics**
- Bars are drawn to the data on a shared scale (`--v`, `--max`). Spans on a timeline are drawn to their dates (`--start`, `--len`).
- One key bar or span at most, and only the one the title names: near-black on paper, green on a dark slide, off-white on a dark page or a blue page. Everything else in the neutral data color. Blue is never a chart color.
- Label the bars directly; no legends, no gridlines, no 3D, no pie charts.
- A graphic that only repeats a number already printed is decoration. Cut it. A chart with illustrative lengths is never allowed: no real values, no chart.
- Value labels are the number and unit, 6 characters or fewer. Words go in the row label or the caption.
- Bars in one chart share one measure. Never plot a slice of one bar as another stage.

## Styles to avoid, each with the fix

| Avoid | Fix |
|---|---|
| Equal-box card grids as the default layout (3 or 4 bordered boxes in a row) | Pick a layout from the catalog. Parallel items become rows in the hang, or unboxed columns on the grid. |
| Rounded corners of any size | Radius 0. |
| Gradients, glows, color washes | Flat brand colors only. |
| Drop shadows and "elevation" | Nothing floats. Separate with space. |
| Glass, blur, frosted panels | Flat fills. |
| Emoji, icons in circles, icon-per-feature rows | Words. A short label in the column does the job. |
| Pill badges, chips, tags | A muted label in text. |
| Centered-everything layouts, centered hero text with a subtitle and two buttons | Flush left on the grid. The ask is one line of text. |
| Boxes or borders around every block | Space separates blocks. No outlines. |
| Lines between every row of a list or text block | Space between rows. Hairlines only inside real tables. |
| Heavy rules (anything over 0.5pt): 1pt, 2pt, 3pt section rules | 0.5pt, and only in tables and one axis. |
| Column rules between columns | The gutter is the divider. |
| A blue overline or eyebrow on every heading | A muted kicker. Blue keeps its one meaning: the decision or next step. |
| Topic titles ("What we propose", "Two wins this quarter") and body text that restates its heading | A title that states the finding; text that adds something. |
| The same fact on three slides or in three places on a page | Say it once as the figure or headline, once in text if the sentence needs it. |
| A blue field or glyph next to the list or timeline it draws | Delete the field, or put it on a page without that list. |
| Green on more than one thing, green on light pages, green step badges | One green highlight on a dark slide, or none. |
| ALL CAPS or Title Case headings and labels | Sentence case. |
| Stock-photo placeholders and decorative imagery | Use only a real image (product screen, team, site). No image: pick a layout without one. |
| Text walls | Stay inside the word budget of the slot. Split into two slides or pages. |
| KPI tiles with borders or backgrounds | Unboxed figures on the grid: number, then a muted label. |
| Decorative background shapes, blobs, dot grids, random geometry | Empty space. A glyph only if it is drawn about the content (the steps, the phases). |
| More than 2 weights on a page | Regular only. |
| Arbitrary spacing and pixel nudges | Token steps and grid columns only. |
| A dark cover with a giant green numeral | Covers are type on the grid: kicker, title, meta, logo top right. |
| Titles at the foot of the page | Title at the top, always. |
| A full-page quote | One quote at quote size, on a page or slide that also carries the proof. |
| Gray boxes behind content | No fills behind text on paper. |
| Blue shapes or text on near-black | Green for the one highlight on dark; blue gets its own full-bleed slide. |
| A logo on blue or green, or a pasted logo with a white background | Hide the logo on color; use the inline SVG in `currentColor`. |
