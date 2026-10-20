# Documents

Print-first US Letter. Every page is a fixed `<section class="page">` frame (8.5 x 11 in, 816 x 1056px), so what you see on screen is exactly what prints, and overflow is visible (a red frame on screen).

## Pick the template

| Need | Template | Pages | Color pages |
|---|---|---|---|
| Leave-behind, one-pager, service sheet, event handout | `one-pager.html` | 1 | None; the ask line is blue |
| Proposal, SOW, pricing, project plan | `proposal.html` | 4 (cover, summary, plan, investment); add pages by copying one | Blue last page (the decision) |
| Case study, client story | `case-study.html` | 2 (story, results) | Dark results page |
| Internal report, monthly metrics, review | `report.html` | 2 (findings with chart, detail and recommendations) | None |

A document type not listed (brief, memo, agenda, handout): start from the closest template and keep its page frame, head, rows and footer. Never start from a blank page.

## The page model

- **Head at the top of every page**: a muted kicker (what section this is) above the page title (36px, 6 words or fewer, states the point). An aside or result may sit in column 4, bottom-aligned.
- **Standfirst** (16px lead) in columns 2 to 4: the page in one breath.
- **Rows in the hang**: row label in column 1, reading text in columns 2 to 3, aside (note, source, facts, a short quote) in column 4. Space between rows, never lines.
- **Footer inside every page**: logo, document name (set once in `--doc-name`), page number (counts itself). The logo hides itself on blue pages.
- **Covers**: kicker and logo on the first line, the title at 64px (80px `hero` for 2 short lines), meta in columns 3 to 4, an optional blue field with a glyph drawn about the content (the phases). The field is the one approved decorative use of blue and does not count toward the blue-page limit. It never shares a page with the list or timeline it draws. Nodes are evenly spaced, one per phase, each labelled with the phase name in one row; the to-scale timeline lives on the plan page. If the labels do not fit one row, delete the field. The one-pager has no field (ruling 2026-09-30).
- **Say each fact once, never by deleting substance.** The headline states the outcome in words; the figure carries the number. That pairing is one mention. If a figure repeats the chart, replace it with a rate or share. If deleting a repeat would leave a page without its figure, table or chart, reword instead.
- **Kicker and row label differ.** The kicker names the section; the row label names the row. Never the same word.
- **Short content gets fewer pages, not empty tails.** If a page's content ends above the midline and it is not a cover or a color statement page, first restore what a rule removed (a figure, a table, a user fact, draft content), then consider merging it with the page before if both are one section. Restoring a block never means inventing its data. Tell the user when a document comes out shorter than asked. There is no fill quota: placed white space is fine.
- **Titles state the finding** ("Design roles take longest to fill"), never the topic ("By role family").
- **Sections start a new page.** Inside a section, content flows tight. If a section overflows by a little, cut copy; never pull the next section up and never let 1 or 2 lines spill onto a new page. If a section is genuinely long, give it a second page with the same kicker and its own title (never "continued").
- **Color pages** carry the most important content: 1 dark page and 2 blue pages at most. A blue page carries the decision. A results page with no measured before and after leads with the one real delta as a display figure under the title, then the quote, then the ask. A chart with illustrative lengths is never allowed.
- **Nothing pinned to the foot.** The ask, contact and notes follow the last block at `mt-7` or `mt-8`. Only a cover field sits at the bottom. Leftover space falls at the foot of the page, where it reads as designed. Text on them is off-white; muted is off-white at 72%. No blue on the dark page.
- **Contents page**: only for documents of 8 pages or more. Group entries under labels.

## Page-fit budgets

The frames do not grow. Stay inside these and the page fits on the first render.

| Block | Width | Budget |
|---|---|---|
| Page title | cols 1 to 3 | 6 words (14 on a one-pager or case study headline, 2 lines) |
| Standfirst (lead 16px) | cols 2 to 4 | 55 words, 4 lines |
| One row of reading text (11.5px) | cols 2 to 3 | 90 words, about 10 words a line |
| Aside | col 4 | 30 words |
| Table | cols 2 to 4 or 1 to 4 | 8 rows; cells 6 words |
| Chart | cols 2 to 4 | 3 to 8 bars; value labels 6 characters |
| Figure | one column | numeral 5 characters (counts the numeral only; "under" goes in `fig-pre`), label 8 words |
| Whole text page | | head + standfirst + about 300 words of rows |
| One-pager | | about 230 words in total |

When copy runs over: cut words, then cut a row, then move a whole section to its own page. Never reduce the font size, line height or spacing tokens.

## Print and PDF

- In a browser: Print > Save as PDF, paper Letter, margins None, scale 100%, background graphics on. The page size and margins are already set by `@page`.
- In Claude Code or a sandbox with Chrome: `"<chrome>" --headless=new --no-pdf-header-footer --print-to-pdf=out.pdf file:///path/to/file.html`. Wait for fonts: allow a second before printing if the page loads DM Sans from Google.
- Check the PDF: page count equals the number of `section.page` frames, no blank last page, no red frames.
- Name files for the reader: `Midwestern_Proposal_Larkspur-Freight_2026-09.pdf`.

## Google Docs and Word builds

Same grid and rules, set in points:

- Page Letter, margins 0.58 in top and sides (42pt), 0.92 in bottom (66pt).
- Sizes: body 9pt, labels and tables 8pt, lead 12pt, page title 27pt, display 48pt, footer 6.5pt. Line spacing 1.15 for body, 1.0 for titles.
- Font: TT Hoves if installed, otherwise DM Sans (built into Google Docs; install it from Google Fonts for Word).
- Regular weight only. No shading behind paragraphs, no borders on text boxes, table borders 0.5pt horizontal only.
- Use a two-column table with no borders (col 1 about 1.8 in, col 2 the rest) to get the label hang.
