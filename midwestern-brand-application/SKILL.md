---
name: midwestern-brand-application
description: "Automatically apply Midwestern Interactive brand standards to any visual or client-facing output created in Claude — HTML artifacts, PDFs, documents, decks, and any other branded content. Triggers on any request to create or generate something visual or client-facing: artifact, HTML, landing page, one-pager, dashboard, document, PDF, deck, slides, presentation, pitch deck, proposal, SOW, case study, email template, social post, marketing asset, or any deliverable. Also triggers on: 'on-brand', 'Midwestern brand', 'MW style', 'design system', 'brand colors'. Does NOT trigger for general business questions, strategy discussions, or non-visual content."
---

# Midwestern Brand Application

Automatically applies Midwestern Interactive brand standards to any visual or
client-facing output. Employees do not need to ask for branded output — it is
always on.

New format types can be added by dropping a new `mw-[format].md` file into
`references/formats/` and reinstalling the skill.

---

## Instructions

Before generating any output:
1. Read `references/foundation.md` — applies to all output types without exception
2. Read `references/patterns.md` — structural layout patterns that extend Foundation, applies to all visual output
3. Identify the output type from the request
4. Check `references/formats/` for a matching format file using the naming convention below
5. If a matching format file exists, read it and apply it after Foundation and Patterns. Where files conflict, format files take precedence for that output type only.
6. If no matching format file exists, proceed with Foundation + Patterns only and apply best judgment using established brand tokens

---

## Reference files

### Foundation (always read first)
`references/foundation.md`

### Patterns (always read second)
`references/patterns.md`

Structural layout and composition patterns that extend Foundation — page headers, section structure, and reusable compositions. Applies to all visual output.

### Format files (read only the one that matches)
Located in `references/formats/`, named `mw-[format].md`

**Naming convention — map the request to a format slug:**
- Deck, slides, presentation → `mw-decks.md`
- Proposal, SOW, statement of work → `mw-proposals.md`
- Case study, client story → `mw-case-study.md`
- Email, newsletter → `mw-email.md`
- Social post, marketing asset → `mw-social.md`
- Any other format → normalize to lowercase hyphenated slug and check for a match

---

## Routing logic

| Output type                          | Files to read                          |
|--------------------------------------|----------------------------------------|
| HTML, artifact, dashboard, document  | Foundation only                        |
| Deck, slides, presentation           | Foundation + `mw-decks.md`             |
| Proposal, SOW                        | Foundation + `mw-proposals.md`         |
| Case study                           | Foundation + `mw-case-study.md`        |
| Email template                       | Foundation + `mw-email.md`             |
| Social / marketing asset             | Foundation + `mw-social.md`            |

---

## Logo usage

Three logo assets are bundled in `assets/logos/`. All use `currentColor` so they automatically inherit `--mw-color-foreground` — dark on light backgrounds, light on dark backgrounds.

| File | Use when |
|------|----------|
| `mw-icon.svg` | Default for all output — products, websites, internal assets, artifacts |
| `mw-logo.svg` | External/client-facing output when horizontal layout fits |
| `mw-logo-stacked.svg` | External/client-facing output when a square or stacked layout is needed |

**Rules:**
- Always use `mw-icon.svg` by default unless the output is explicitly client-facing
- Only use `mw-logo.svg` or `mw-logo-stacked.svg` when the user requests it or the output is a client deliverable
- Set the parent element's `color` to `var(--mw-color-foreground)` so the logo responds to light/dark mode automatically
- Never hardcode a fill color on the SVG — always rely on `currentColor`
- Never stretch or distort the logo — always maintain the original aspect ratio
- Never place the logo on a blue or green background

---

## Default behavior
- Light mode is the default unless the user explicitly requests dark mode
- Border radius is always 0 — no exceptions
- ShadCN UI is the component fallback for anything not defined in Foundation — always styled to Midwestern brand tokens
- Never use fonts, colors, or components outside what the reference files define
- Run the self-check validation list from Foundation before presenting any output
