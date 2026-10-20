---
name: mw-platform-design-system-v4
description: MW Platform Design System v4, Midwestern's product design system for the Midwestern Platform (internal.buildmidwestern.com) and any Midwestern SaaS or internal tool UI. Built on shadcn/ui (Mira style, Base UI, Next.js) with Midwestern blue and black, Zinc grays, TT Hoves and Phosphor Light icons. Use this skill whenever building, prototyping, mocking up, reviewing or iterating on platform pages, features, dashboards, admin panels, settings, forms, tables or components for Midwestern's internal products, and whenever converting a page built with the v2 system (mw-saas-system, .mw- classes, --mw- tokens, sharp corners, sentence case) to v4. Also trigger on MW Platform Design System v4, Platform Design System, v4, platform UI, Daily Log, Big Board, platform dashboard, convert to v4, reskin. For platform product UI this supersedes mw-saas-system; marketing and brand output keep using the brand skills.
---

# MW Platform Design System v4

The MW Platform Design System, version 4. It is the shadcn/ui **Mira** style on **Base UI**, re-skinned with Midwestern's brand: MW blue and black, the shadcn **Zinc** grays, **TT Hoves**, and **Phosphor Icons at Light weight**.

Version history, for context when someone says "v2" or "v3":
- v1: the original Figma MWI library
- v2: the `mw-saas-system` skill (sharp corners, sentence case, 8pt tokens, `.mw-` classes)
- v3: Carbon-based update (retired)
- v4: this skill

## Source of truth, in order

1. **The generated preset code.** `pnpm dlx shadcn@latest init --preset b1a0Rv7GV --template next` produces the Mira components. Their structure, sizing, density, shape and dark mode structure are authoritative. Do not re-style component internals.
2. **The v4 theme overrides** in `assets/mw-platform-design-system-v4-theme.css`. They replace the preset's color tokens, fonts and chart colors with Midwestern's.
3. **The rules in `references/`.** Usage, content, patterns, migration.

When these disagree: Mira wins on **sizing, density, spacing, radius, component shape and dark mode structure**. The design system wins on **color, typeface, icons, text case, menu surface and mono usage**.

## Decision log

| Area | v4 decision |
|---|---|
| Base | shadcn/ui, Mira style, Base UI primitives, Next.js template, pnpm |
| Color | MW blue `#2237F1` is primary. MW black `#010313` is light mode text. Zinc grays everywhere else |
| Blue ramp | New 11-step MW blue ramp (50 to 950), 600 = `#2237F1`, built for light and dark |
| Dark mode | Defers to Mira (Zinc dark surfaces), with the MW blue ramp swapped in |
| Success | Its own semantic green, never MW brand green `#C7FA50` |
| Type | TT Hoves for all UI text. Sizes and weights defer to Mira. Never Light weight |
| Mono | DM Mono, strictly for code snippets. Never for numbers, labels or eyebrows |
| Case | Title Case for UI labels and headings. Never all caps. Platform only; marketing keeps brand rules |
| Icons | Phosphor Icons. 16px Light by default; 12px uses Regular (badges, breadcrumb separators); never 14px |
| Logos | MW logo assets in `assets/logos/` |
| Radius | Mira "Small", `--radius: 0.45rem`. v2's zero radius rule is retired for the platform |
| Checkbox | Mira default (square, small radius) |
| Menus | Match the surface (popover token). No inverted or translucent menus |
| Shell | Mira's sidebar pattern (shadcn `Sidebar`) leads |
| Missing components | Compose from shadcn primitives first, then the shadcn registry. No other UI library |
| Side accents | None. No colored left or right borders, side stripes or inset side shadows on cards, rows, alerts or nodes. Category color goes in a small swatch or badge inside the element |
| Disabled controls | Disabled with a reason: `aria-disabled` keeps the control focusable and a Tooltip says why. Plain `disabled` only when the reason is obvious |
| Search fields | `InputGroup` with a leading `MagnifyingGlass`; text starts after the icon. Never let a global input padding rule override the group's inset |
| Toggles | Switches are pills (Mira default) |

## Pick the workflow

**Building something new.** Read `references/foundations.md` and `references/components.md`. Start from the closest pattern in `references/patterns.md`. Write copy using `references/content.md`.

**Iterating on an existing v4 page.** Only change what was asked. Reuse the components and patterns already on the page. Run the self-check before handing back.

**Converting a v2 page to v4.** Read `references/migration-v2-to-v4.md` first and follow its workflow step by step. Then the foundations and components files as needed.

**Reviewing a design or PR for v4 compliance.** Run the self-check below and report each failure with the fix.

## Two output contexts

**Inside the platform codebase (Next.js).** Use the generated shadcn components from `@/components/ui/*`. Never hardcode hex values or arbitrary pixel sizes; use tokens and Tailwind classes. Setup files live in `assets/setup/`.

**Standalone prototypes (HTML artifacts, Claude previews).** Base UI and the component files are not available, so recreate Mira's look with Tailwind classes and the v4 tokens from `assets/mw-platform-design-system-v4-theme.css`. Embed TT Hoves as a base64 `@font-face` when possible, with DM Sans as the fallback. Inline Phosphor Light icons as SVG rather than loading an icon font. Keep the same component anatomy so the prototype maps one to one onto real components.

## Reference files

| File | Read when |
|---|---|
| `references/foundations.md` | Always for new UI. Color tokens, blue ramp, type, icons, radius, spacing, dark mode, setup |
| `references/components.md` | Any time you use a component. Inventory, variants, usage rules, Base UI notes |
| `references/patterns.md` | Building pages: app shell, page header, dashboards, tables, detail, settings, forms, states |
| `references/content.md` | Writing any UI text. Title Case rules, voice, labels, errors, empty states |
| `references/migration-v2-to-v4.md` | Converting anything built with v2 |

Behavior, layout structure, states and stress testing live in the separate MW Platform UX Standards skill (`mw-platform-ux-standards`). Use both: this skill decides how things look, that one decides how they work.

Assets: `assets/mw-platform-design-system-v4-theme.css` (token overrides), `assets/setup/` (fonts, theme and icon providers), `assets/logos/` (MW icon and wordmarks), `assets/fonts/` (TT Hoves).

## Non-negotiables

- Never edit a component's internal sizing or radius to make it "feel more MW". Brand comes through tokens.
- One primary (blue) button per view or card section.
- Blue is for action and selection. Never use blue for large surface fills or body text.
- No all caps anywhere. Remove `uppercase` and wide `tracking` classes that come with Mira examples.
- No monospace outside code snippets. Numbers use `tabular-nums` in TT Hoves.
- Phosphor only: 16px Light by default, 12px Regular in badges. No 14px icons. No Lucide, Carbon or mixed icon sets.
- Menus, popovers and dropdowns use the surface (`bg-popover`), never inverted.
- Light mode is the default. Every screen must also work in dark mode.
- No colored side stripes, side borders or inset side shadows anywhere. Borders are uniform on every side.
- A disabled control that isn't self-explanatory says why (Tooltip on hover, focus and click).

## Self-check before handing back

1. Uses generated shadcn components (or faithful Tailwind recreations in prototypes); no hand-rolled versions of existing components
2. All color comes from tokens; no raw hex except inside the theme file
3. Primary actions are MW blue; at most one per view or card section
4. Text is MW black in light mode via `foreground`; secondary text uses `muted-foreground`
5. Font is TT Hoves; no DM Sans left from the preset except as fallback; no Light weight
6. Mono only inside code snippets (DM Mono)
7. UI labels and headings in Title Case; descriptions and body in sentence case; nothing in all caps
8. Icons are Phosphor: 16px Light by default, 12px Regular in badges, no 14px icons
9. Menus and popovers match the surface
10. Success uses the success token, not MW green
11. App shell uses the shadcn Sidebar pattern
12. Works in light and dark mode; focus rings visible; every input has a label
13. Empty, loading and error states exist for every data region
14. For conversions: nothing from v2 remains (`.mw-` classes, `--mw-` tokens, `rounded-none`, `data-theme`)
15. No colored side stripes or one-sided borders or inset side shadows (search the code for `border-l-`, `border-s-`, `border-inline-start`, `inset Npx 0`)
16. Search fields: placeholder and typed text start after the icon at every page
17. Disabled controls that aren't obvious explain themselves
18. Platform page decisions in `references/patterns.md` §11 are followed (Daily Log, Dashboard, Org Chart)
