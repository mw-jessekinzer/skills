# Decks

## Defaults

- 1920 x 1080 slides, one `<section class="slide">` each, built from `templates/deck.html`.
- **Dark by default** (`#010313`), matching the Figma Slide Library. Use the light variant (add `deck--light` to `<body>`) only when the user asks for it or the deck will be printed.
- Up to 2 blue slides (`slide--blue`), only for the decision or next step: the closing ask, and a statement slide only if it is the recommendation you want approved. Key statements otherwise stay dark.
- Green (`#C7FA50`) marks one thing on a dark slide at most: the key bar, the key phase, or one number. Many slides have none. On light slides the key bar is near-black and blue is kept for the ask; on blue slides the accent is off-white.
- Every slide but the title carries the footer: logo, deck name (set once in `--deck-name`), slide number (counts itself).

## Anatomy

- Head row (top 312px): muted kicker (24px) and title (72px) across columns 1 to 9. Title 8 words or fewer, 2 lines at most, stating the point.
- Main row (the rest, down to 152px above the bottom): the layout's content on the 12 columns.
- Content starts at the same height on every slide, so the deck reads as one system when flipped. Only `slide--number`, the statement's source line and `slide--closing` anchor to the bottom.
- Side margins are 96px (ruling 2026-09-30; the Figma library uses 56px).

## Layout catalog

Pick one layout per slide by what the content is. If nothing fits, the content is probably two slides.

| Layout | Use when | Word budget |
|---|---|---|
| `slide--title` | First slide only | Kicker 8, title 10, 2 or 3 meta items |
| `slide--section` | Opening a part, when the deck has 3 or more parts | Title 5, optional line 15 |
| `slide--statement` | One sentence carries the argument. Dark; `slide--blue` only if it is the decision you ask for | 12 |
| `slide--number` | One number is the message | Title 8 (states what the number means, never repeats it), numeral 4 characters, context 30 |
| `slide--numbers` | 2 to 4 different facts that belong together (never boxed) | Each numeral 5 characters, label 8 |
| `slide--two` | Two options, before and after, two audiences | Each column: heading 5, text 35 |
| `slide--steps` | A process in order, 3 to 5 steps | Step title 4, text 14 |
| `slide--timeline` | Phases with dates, drawn to scale, 2 to 5 phases | Phase name 3, weeks label 4 |
| `slide--table` | Real rows and columns: team, prices, comparisons | 6 rows by 4 columns, cells 6 words |
| `slide--chart` | Comparing amounts, 2 to 6 bars | Label 4, title states the finding |
| `slide--quote` | One real client quote, once per deck at most | 25 |
| `slide--image` | You have a real image (product screen, team, site) | Title 7, text 30 |
| `slide--closing` (blue) | The ask and the contact. The ask (the action you want the reader to take) is draft content: write it for client decks. The contact is a Midwestern fact: the user's, or "Placeholder: name, email, phone" at body size. Internal decks end on their last content slide unless the user named the decision | Ask 8, follow-up 25 |

Figure budgets count digits and separators only; a currency sign and a K, M or % suffix do not count ("$193K" counts 3). "Under" goes in `<span class="fig-pre">` before the numeral; never "<", "~" or "+".

Total reading text on any slide: 40 words or fewer (tables excepted). If it does not fit, cut words first, then split the slide. Never shrink type, never add a column to squeeze text in.

**Fit test.** Trimming words to fit a slot is editing. Padding two points into three, or cutting a real fourth option so a 3-column layout works, is distortion. Choose the layout that matches the real count. An explicit slide count is a user fact. Meet at least its lower bound with true or draft content (a statement slide with the key takeaway, or a plan slide with draft specifics). Go below it only when every candidate slide would repeat another; then say so in the first line of the handover and name the slide that would complete it. Never add a slide that restates another, never write body text that restates its heading, and never put the same claim on more than two slides.

A typical 8-slide pitch, when the content is there: title, statement, number, steps, timeline or table, numbers, (quote if real), closing.

## Build steps

1. Copy `templates/deck.html`. Set `<title>` and `--deck-name`.
2. Write the story first as one line per slide. Pick a layout for each line from the catalog.
3. Delete the slides you do not need; copy a slide to reuse its layout. Keep slides in story order.
4. Fill slots inside their budgets. Keep the SLOT comments' limits; delete the comments at the end if you like.
5. Render or open it. Any slide with a red frame spills: cut copy.
6. Export: Chrome > Print > Save as PDF (the page size is set to the slide), margins None, background graphics on. In Claude Code: headless Chrome `--print-to-pdf`.

## PowerPoint and Google Slides builds

Same grid, same layouts, same rules. Convert the pixel values:

| | PowerPoint 13.33 x 7.5 in | Google Slides widescreen 10 x 5.625 in |
|---|---|---|
| Factor | px / 2 = pt | px x 0.375 = pt |
| Margins (side, top, bottom) | 48, 44, 76 pt | 36, 33, 57 pt |
| Gutter | 16 pt | 12 pt |
| Footer / label / body / lead | 10 / 12 / 16 / 22 pt | 7.5 / 9 / 12 / 16.5 pt |
| Title / display / big number | 36 / 60 / 140 pt | 27 / 45 / 105 pt |
| Lines | 0.5 pt | 0.5 pt |

- Font: TT Hoves if the person building or presenting has it installed; otherwise DM Sans (built into Google Slides and Docs; install it from Google Fonts for PowerPoint). See `fonts.md`.
- Background fill `#010313`, text `#F6F7FE`, muted text `#999A9E` (the flat equivalent of 62% off-white).
- python-pptx: set every shape's fill and line explicitly (`shape.line.fill.background()` removes the default outline); never use default theme shapes, which bring outlines and fills. Place the logo as the SVG or a PNG exported from it, never a screenshot with a background.
- Google Slides: set the theme fonts and colors once in the master, then build from blank layouts; do not use the built-in themes.
