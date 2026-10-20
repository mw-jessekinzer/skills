# Layout Structure

Layout communicates before a word is read. Position, spacing and alignment carry hierarchy on their own. Express every change in the project's existing styling system (Tailwind in the platform); never add a second styling approach. Visual tokens, radius and component anatomy come from MW Platform Design System v4.

## Principles

1. **Group with space, not lines.** Space first, background shapes second, separator lines last. The gap between groups is at least 2x the gap within a group (8px within, 16px+ between).
2. **Controls look like controls.** A background, border or consistent placement zone. Never style a control like adjacent static text.
3. **Align to shared edges.** Pick edges and stick to them. One spacing step per level of subordination (16px default). Indent a section's body to its title's text edge, not to its icon or swatch.
4. **Order by importance.** Most important content near the top and leading edge. Think leading and trailing, not left and right.
5. **Hint at hidden content.** A horizontal scroller lets the next item or block peek 16 to 32px past the edge; collapsed content has a visible disclosure control.
6. **Breathing room between targets.** About 12px between bordered controls, 24px clearance around borderless text and icon controls, unless a density system says otherwise and hit areas don't overlap.
7. **Inset buttons from edges.** Full-width buttons sit inside layout margins (16px on mobile).
8. **Content bleeds, controls float.** Backgrounds and media may reach the viewport edge; text and controls stay inside margins and safe areas.
9. **Hold structure until it breaks.** Breakpoints come from content. Keep the expanded layout as long as it fits; collapse late; prefer container queries for components.
10. **Plan for growth and clipping.** No fixed widths or heights on text containers; rows wrap; translated strings can grow a lot. Never park the primary action where resizing clips it.

## Platform layouts

- **Work page with a summary** (Daily Log): main column for the work, a 20rem side column (24rem at 1440+) for totals, the single primary action and supporting lists. One column below 1024px, side content after the main content.
- **Dashboard**: one question per card; three-up grid collapsing to one column below 768px.
- **List page**: toolbar (search, filters, view options) above the table; bulk actions replace filters when rows are selected.
- **Wide visuals** (time tracks, org charts, tables): their own horizontal scroll container with a sensible min width; the page body never scrolls sideways.

## Logical properties

Use `padding-inline-start`, `margin-inline-end`, `inset-inline-start` for direction-dependent layout. Keep physical left and right for genuinely physical geometry, such as a time axis that always runs left to right (set `direction: ltr` on that element).

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Separator line where space would do | Remove the line, double the gap between groups |
| `margin-left` in a localizable layout | `margin-inline-start` |
| Scroller that looks complete | Let the next item peek past the edge |
| Adjacent controls merge | Increase the gap using the spacing scale |
| Breakpoints at 768/1024 because they're defaults | Break where content stops fitting |
| Fixed-width text container | `max-width` plus wrapping |
| Primary action at the clip-prone bottom of a pane | Sticky positioning or stable chrome |
| Card actions squeezing the title on mobile | Wrap actions below the title under 640px |
