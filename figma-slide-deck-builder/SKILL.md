---
name: figma-slide-deck-builder
version: "2.1.0"
last_updated: "March 30, 2026"
latest_changes: "v2.1.0 — HTML fallback complete: all 34 Slide Library layouts as verified HTML/CSS templates. Real MW brand assets as data URIs, Phosphor Icons, PDF via browser print, slide grid documented."
description: "Build slide decks using the Midwestern Slide Library and Design System. Trigger whenever the user asks to create a presentation, pitch deck, slide deck, or any multi-slide deliverable — even if they just say 'make me a deck' or 'build slides for this.' Works in two modes: if Figma MCP is connected, builds directly in Figma using published components. If Figma MCP is not available, builds an HTML/CSS presentation with PDF download. Also trigger when the user references the Slide Library, asks to convert content into slides, or wants to populate an existing deck with new content. Always read this skill before creating any slides. Also responds to: 'build a deck', 'make slides', 'presentation for [client]', 'pitch deck', 'populate this deck', 'add a slide'."
---

# Midwestern Slide Deck Builder

This skill builds complete slide decks styled to the Midwestern Design System. It supports two rendering paths depending on the user's environment — detect which one to use before doing anything else.

---

## Step 0: Detect environment

Check if you have access to Figma MCP tools (specifically `Figma:use_figma` or `Figma:whoami`).

- **Figma MCP available** → Follow the **Figma path**. Read `references/workflow.md` and `references/slide-library-catalog.md`.
- **Figma MCP not available** → Follow the **HTML fallback path**. Read `references/html-fallback.md` and `references/slide-library-catalog.md` (for layout selection logic — ignore the component keys).

Both paths use the same layout catalog and visual language. The difference is the output medium, not the design decisions.

**Both paths follow the same build sequence:**
1. **Outline first** — Study the source content, map every slide to a layout, and present a complete deck outline to the user. Include layout name, rough content, and visual elements for each slide. **Do not start building until the user approves the outline.**
2. **Build slide-by-slide** — Import/create one slide at a time. Fully populate and adjust each slide before moving to the next. Do not batch-import all slides first.

---

## Quick reference

### Figma path
Build slides directly in Figma using published Slide Library components and DS tokens.

| Key | Value |
|---|---|
| MW Design System | `eTyygHuvSaHUWA4kS4iaZn` |
| Slide Library | `9ZnOiRVkBQUbB1zRKcgkjF` |
| Workspace plan key | `team::929068967373356657` |

### Slide grid (both paths)
All slides align to the same canonical grid: **12 columns** (32px gutters, 56px offset) × **6 rows** (0px gutters, 56px offset). Content area is 1808px wide. See `workflow.md § 1.3` for Figma implementation or `html-fallback.md § Slide grid` for CSS.

### HTML fallback path
Build slides as a single-file HTML/CSS presentation with:
- Two view modes: scroll (all slides stacked) or presentation (one slide at a time with arrow nav)
- PDF export via browser print with @media print styles
- MW Design System tokens as CSS custom properties
- SVG decorative elements with corrected stroke widths for screen rendering

---

## When to read reference files

| Situation | Read this |
|---|---|
| **Figma path**: starting a new deck | `references/workflow.md` |
| **HTML path**: starting a new deck | `references/html-fallback.md` |
| Choosing which layout to use for a slide | `references/slide-library-catalog.md` |
| Running into Figma errors or unexpected behavior | `references/gotchas.md` |
| Need to bind DS tokens to Figma elements | `references/workflow.md` § Token Binding |
| Modifying Figma vector paths (charts, curves) | `references/gotchas.md` § Vector Path Editing |
| Styling a chart, graph, or data viz slide | `references/gotchas.md` § Data Visualization Styling (Figma) or `references/html-fallback.md` § Data Visualization (HTML) |

---

## Changelog

**v2.1.0 — March 30, 2026**

- Real MW mark (filled M) and full wordmark (M + "midwestern") as inline SVG data URIs — zero font dependency
- Phosphor Icons (light + regular) via CDN for all icon needs
- All 34 Slide Library layouts now have verified HTML/CSS templates (16 verified against Figma design context, 18 additional based on screenshots and variant documentation)
- PDF export switched to browser print with `@media print` — killed CDN-dependent html2pdf.js
- Presentation mode fixed: opacity-based slide switching instead of display
- Footer corrected: page number + title + section (muted), border color #666
- Slide grid documented: 12-column / 6-row canonical grid (both Figma and CSS)
- Reusable patterns extracted: Title Block, Cover Graphic, Social Icons Row
- Documented Claude artifact preview CDN limitation

**v2.0.0 — March 30, 2026**

- Dual-path architecture: Figma MCP detection with HTML/CSS fallback
- HTML fallback: all 34 layouts as HTML/CSS templates with MW tokens
- HTML fallback: scroll + presentation view modes with keyboard nav
- HTML fallback: PDF download via html2pdf.js with @media print fallback
- HTML fallback: SVG decorative elements (Cover Graphics, MW Mark, line art) with corrected stroke widths
- HTML fallback: data visualization styling in CSS

**v1.1.0 — March 30, 2026**

- Added data visualization styling rules (color hierarchy, shape/fill rules, Figma API bindings)
- Re-queried all keys from MW workspace Figma files: 34 slide component keys, 6 variable keys, 3 text style keys, Cover Graphic set key, and MW Mark component key
- Updated MW Design System and Slide Library file keys to MW workspace
- Removed unused library keys (lk-) from quick reference
- Added version and changelog tracking

**v1.0.0 — Initial release**

- Core workflow: file creation, component import, content population, token binding, cleanup
- Slide library catalog: 34 layouts with component keys and content-to-layout decision tree
- Gotchas: font handling (TT Hoves → DM Sans swap), instance overrides, batch import limits, vector path editing
- MW slide visual language rules
