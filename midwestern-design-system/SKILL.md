---
name: midwestern-design-system
description: Midwestern brand design for decks, slides, presentations, one-pagers, proposals, SOWs, case studies, reports and documents. On-brand templates, fonts, colors, logos.
---

# Midwestern design system

Use this for anything visual that carries the Midwestern brand: slide decks, one-pagers and leave-behinds, proposals and SOWs, case studies, internal reports, and other documents. It gives you finished templates in one style, Swiss editorial, so the person asking does not need design knowledge. Your job is to pick the right template, fill it with good copy, and check it before you hand it over.

## Load only what the task needs

| Task | Read | Start from |
|---|---|---|
| Any task with copy (all of them) | `references/brand.md` first: "What we sell", voice, the three kinds of content, placeholders | |
| Deck, slides, presentation, pitch | `references/decks.md` | `templates/deck.html` |
| One-pager, leave-behind, handout, service sheet | `references/documents.md` | `templates/one-pager.html` |
| Proposal, SOW, pricing, project plan | `references/documents.md` | `templates/proposal.html` |
| Case study, client story | `references/documents.md` | `templates/case-study.html` |
| Internal report, metrics summary, review | `references/documents.md` | `templates/report.html` |
| Other document (memo, brief, agenda) | `references/documents.md` | closest document template |
| PowerPoint, Google Slides, Google Docs, Word | `decks.md` or `documents.md` (conversion tables at the end), `references/fonts.md` | same layouts |
| Font question or font trouble | `references/fonts.md` | |
| Colors, logo, voice, what to call things | `references/brand.md` | |
| Unsure whether something is on-style | `references/style.md` (rules and the avoid list) | |
| Setting up Claude Design | `references/claude-design.md` | |

Do not read every file. The templates already carry the styles; you only need the reference for the medium you are building. `templates/mw.css` holds the same CSS as the templates and is only needed when no template fits.

## Build rules

1. **Start from a template.** Copy the template file and fill it. Never write a Midwestern deck or document from a blank page, and never restyle a template.
2. **Pick a layout per slide or page from the catalog.** Choose by what the content is (one number, a process, a comparison), not by what looks full.
3. **One idea per slide, one section per page.** Titles go at the top and state the point.
4. **Stay inside the word budget in each SLOT comment.** When copy does not fit, cut words first, then split into two slides or pages. Never shrink type, tighten spacing, or add columns to make it fit.
5. **Never go below the minimum size.** Documents: 10.5px for any content. Slides: 24px for any content. The footer is the only smaller text.
6. **Use the markers.** SLOT = replace the text. REPEAT = copy or delete the whole block within its count. OPTIONAL = delete the block cleanly if you have nothing true to put in it. DATA = change the number in the style attribute and retype the printed value.
7. **Only real content, in three kinds.** **User facts** (anything in the request: client, team size, price, dates, results) are real: use them, never replace them with a Placeholder. **Draft content** (phases, deliverables, features, approach, team roles, a story consistent with the user facts, recommendations, a milestone split of a sample price) is yours to write plainly and list in the handover as draft to confirm. **Midwestern facts** (proof points, company figures, terms on a real price, named people, contacts, quotes, client names, guarantees, response times) are never invented. Sample status follows the number. The proof points, typical delivery windows and never guarantees, written "in under" or "typically": embedded talent placed onto a team **in under 2 weeks (under 10 business days)**; recruiting, client-facing, **"fill a role in under 20 days"** (internal form: full-time roles in under 3 weeks, under 15 business days). A missing Midwestern fact is "Placeholder: what is missing" at body or label size on one line, never in a title, statement, display or lead slot; if a title would have to be a Placeholder, delete the slide or block or ask. Sample numbers are marked in the footer name (", sample data") and the first kicker where they appear, nowhere else. Notes for the user go in the handover, never on the page. Never invent a number to fill a page. A sample breakdown of user totals is allowed only when the user said sample data is acceptable; label it on the block itself ("Detail, sample split" in the kicker or a caption "Sample split of September totals") and list it in the handover. The ask (the action you want the reader to take) is draft content: write it for client decks and one-pagers. The contact is a Midwestern fact: use the user's or write "Placeholder: name, email, phone" at body size. Internal decks end on their last content slide unless the user named the decision.
8. **Check the page does not spill.** Open or render the file. A red frame on a page or slide means its content overflows: cut copy until no frame shows.
9. **Say each fact once, never by deleting substance.** A number or claim appears at most twice in a piece. The headline states the outcome in words; the figure carries the number, with its qualifier and unit, and its label says what was measured. That pairing is one mention, and it is the default for covers, one-pagers and case studies ("Full-time engineers hired before the roadmap slips" over a figure "Under 20 days", labelled "typical time to fill a role"). A figure row and a chart on one page never show the same numbers: turn the repeat into a rate. If deleting a repeat would leave a page without its figure, table or chart, reword the headline instead. Never pad; never go below an explicit count without saying so.
10. **Titles state the finding.** "Design roles take longest to fill", not "By role family". Replace every sample title in the template.

## The style in brief

Swiss editorial: type on a strict grid, a lot of designed white space, flush-left ragged-right text, one weight, one accent with one meaning. Hierarchy comes from size and space, never from boxes, lines or bold.

- **Grid.** Documents: US Letter, 4 columns of 164px, 16px gutters, 56px margins. Slides: 1920 x 1080, 12 columns, 32px gutters, 96px sides. Everything starts on a column line.
- **Type.** Short fixed scales (documents 8.5 to 80px, slides 20 to 280px), Regular weight only, sentence case, tabular figures.
- **Color.** Documents on white paper `#FFFFFF`; decks dark `#010313` by default. Blue `#2237F1` means the decision or next step, nothing else (the ask, the closing slide, the investment page; a cover field is the one exception). The key bar in a chart is near-black on paper, green on dark. Green `#C7FA50` is one highlight on a dark slide, at most. Never blue on near-black.
- **Lines.** 0.5pt, only in real tables and one chart axis.
- **Color pages.** A document gets at most 1 dark and 2 blue pages; a deck at most 2 blue slides. They carry the most important content.
- **Numbers.** A big numeral only when the number is the message; its unit small and muted beside it.
- **Logo.** The inline wordmark in `currentColor`: top right on covers, bottom left in footers, never on blue or green.

Never produce: card grids of bordered boxes, rounded corners, gradients, shadows, blur, emoji or icon-in-circle rows, pill badges, centered layouts, boxes around blocks, lines between every row, rules heavier than 0.5pt, blue overlines on headings, stock-photo placeholders, KPI tiles, decorative shapes, bold, ALL CAPS or Title Case. The full list with fixes is in `references/style.md`.

## Fonts

- Stack everywhere: `'TT Hoves', 'DM Sans', 'Helvetica Neue', Arial, sans-serif`.
- TT Hoves is the brand font and loads only from the viewer's installed copy (`local()`). Never embed, bundle, upload or ask for the TT Hoves file: the license forbids it.
- DM Sans is the approved fallback, loaded from Google Fonts in HTML and bundled in `assets/fonts/dm-sans/` for offline, PDF and sandbox use. The templates tune it to TT Hoves widths so layouts do not reflow. Never edit the MW FONTS block; for offline use, copy the font beside the HTML (see Delivering).
- **Never refuse DM Sans, and never substitute any other font.**
- PPTX, Google Slides, Docs, Word: set TT Hoves only if the user has it installed; otherwise DM Sans (built into Google Slides and Docs).

## Delivering

- **claude.ai artifact:** output the filled template as a single HTML artifact. Nothing to do for fonts: Google Fonts loads DM Sans. For a PDF, tell the user: open the file in Chrome, Print, Save as PDF, margins None, background graphics on.
- **Any render in a sandbox, Claude Code or Cowork (HTML to PDF or PNG):** first copy `assets/fonts/dm-sans/DMSans-Variable.ttf` into a `fonts/` folder next to the HTML (the sandbox may have no network). Then render with headless Chrome, look at the result, and hand over.
- **Before handover:** delete the SLOT, REPEAT, OPTIONAL and DATA comments.
- **Say what you did not fill:** every Placeholder, sample number, and missing image, plus the draft content to confirm.

## Self-check before you present

Run every line. Fix and re-check anything that fails.

- [ ] Built from a template; every slide or page uses a catalog layout.
- [ ] Font stack is `'TT Hoves', 'DM Sans', 'Helvetica Neue', Arial, sans-serif`; the MW FONTS block is untouched; no TT Hoves file is embedded or linked.
- [ ] No banned style: no boxes, cards, pills, icons, rounded corners, shadows, gradients, centered blocks, lines between rows, rules over 0.5pt, decorative shapes.
- [ ] Regular weight only; no bold, no italic.
- [ ] Nothing below the minimum size (documents 10.5px, slides 24px; footer excepted), and no inline font-size overrides.
- [ ] Every block starts on a grid column (`at-N` / `w-N` classes, no pixel nudges or inline margins).
- [ ] No red spill frame on any page or slide; no page ends with 1 or 2 stray lines; PDF page count equals frame count.
- [ ] Sentence case on every title, heading and label. Titles at the top, stating the point.
- [ ] Blue used for one meaning; no blue on near-black; green at most once per dark slide; color pages within their limit.
- [ ] Logo present (cover and footers), in `currentColor`, not on blue or green.
- [ ] Proof points in their approved form ("under 20 days" for client-facing recruiting), never as a guarantee; user facts used, not replaced; no invented Midwestern facts; sample data in the footer name and first kicker only; "Midwestern", never "MWI"; website `midwestern.com`.
- [ ] Every Placeholder is at body or label size on one line; none in a title, statement, display or lead slot.
- [ ] Every document page carries a figure, table, chart or real rows, or is a deliberate cover or statement page; no page ends above the midline with an empty tail.
- [ ] No contrast framing ("X, not Y", "rather than") and no parentheses in titles or display type.
- [ ] No number or claim appears more than twice; no figure repeats the title or the chart; no two slides say the same thing.
- [ ] No title is a topic label; each title could be the only line a reader sees.
- [ ] One logo per page; nothing pinned to the page foot with a void above it; no notes to the user on the page.
- [ ] Every SLOT filled, no leftover template sample text (Larkspur Freight, Priya Natarajan, sample titles), unused OPTIONAL blocks deleted.
