# Setting up Midwestern in Claude Design

This skill does not feed Claude Design. Claude Design keeps its own design system object (Settings > Design systems), so the same rules have to be loaded there once. Whoever sets it up should be the person who owns the brand, and should check the first exports by eye.

## Upload

1. Logos: `assets/logos/mw-logo.svg`, `mw-icon.svg`, `mw-logo-stacked.svg`.
2. Fonts: the three files in `assets/fonts/dm-sans/`. Do not upload TT Hoves: the license bars putting the font file on third-party servers.
3. Examples: PDFs of the templates, printed from Chrome (`deck.html`, `one-pager.html`, `proposal.html`, `case-study.html`, `report.html`). Claude Design extracts color, type and layout from real examples better than from descriptions.
4. Rules: paste `references/style.md` and `references/brand.md` as the written guidance.

## Say in the setup prompt

- Font of record: DM Sans, Regular only. TT Hoves is the brand font on design machines; DM Sans is its approved stand-in. Ignore any "missing brand fonts" warning about TT Hoves.
- Colors: `#010313`, `#F6F7FE`, `#FFFFFF` (print paper), `#2237F1`, `#C7FA50`, muted `#666666`. Radius 0, flat color, nothing floats.
- Decks are dark by default; blue means the decision or next step only (the closing ask, a recommendation to approve); no blue on near-black.
- Documents follow the 4-column Letter grid with titles at the top and 0.5pt lines in tables only.

## Admin

- Team and Enterprise: an owner turns on design systems under Organization settings > Artifacts, then flips the system to "Published" so it becomes the org default. Enterprise can limit who publishes.
- Presentations may route to Claude Slides, which has its own setting under Organization settings > Artifacts.
- Claude Design has no version history. Keep this skill folder as the source of truth and re-upload when it changes.
