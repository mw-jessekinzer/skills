# MW Platform Design System v4 Foundations

Contents: 1. Color · 2. Typography · 3. Icons · 4. Logos · 5. Radius, spacing, elevation · 6. Dark mode · 7. Setup checklist

Everything here is expressed as shadcn tokens and Tailwind classes. Use the token, never the raw value. Raw values appear only so humans can verify them.

---

## 1. Color

### Brand primitives

| Name | Hex | Token | Use |
|---|---|---|---|
| MW Blue | `#2237F1` | `--mw-blue-600` | Primary actions, selection, focus of attention |
| MW Black | `#010313` | `--mw-black` | Light mode text (via `foreground`) |
| MW White | `#F6F7FE` | `--mw-white` | Text on blue fills (via `primary-foreground`) |

MW Green (`#C7FA50`) is a brand accent for marketing. It is **not** part of the v4 product palette and never stands in for success.

### MW blue ramp

Hue is locked to MW blue so every step reads as the same blue. 600 is the brand color exactly. Lightness steps follow the preset's blue ramp, so contrast behaves the way Mira expects.

| Step | Hex | Tailwind class | Typical use |
|---|---|---|---|
| 50 | `#F0F5FF` | `mw-blue-50` | Selected row tint, subtle info background (light) |
| 100 | `#DEE8FF` | `mw-blue-100` | Hover on selected items (light) |
| 200 | `#C6D8FF` | `mw-blue-200` | Range fills, progress track tint |
| 300 | `#A4BFFF` | `mw-blue-300` | Chart 1, link text in dark mode |
| 400 | `#749AFF` | `mw-blue-400` | Chart 2, icons on dark surfaces |
| 500 | `#436DFD` | `mw-blue-500` | Chart 3, dark mode sidebar primary |
| 600 | `#2237F1` | `mw-blue-600` | **Light mode primary**, chart 4, link text in light mode |
| 700 | `#1B2ECB` | `mw-blue-700` | **Dark mode primary**, chart 5, primary hover in light |
| 800 | `#1527A7` | `mw-blue-800` | Pressed states |
| 900 | `#0F1F7F` | `mw-blue-900` | Deep tints on dark surfaces |
| 950 | `#081554` | `mw-blue-950` | Selected row tint, subtle info background (dark) |

700 is the successor to v2's "Navy" (`#1A2CD1`), and is visually almost identical.

Contrast checks: 600 with MW White text is 6.8:1. 700 with MW White text is 8.6:1. 300 on the dark background is 10.9:1. 500 with white text is only 4.1:1, so never put small text on 500 fills.

### Semantic tokens

Use these through Tailwind: `bg-primary`, `text-muted-foreground`, `border-border`, `text-success`, and so on.

| Token | Light | Dark | Notes |
|---|---|---|---|
| `background` | white | Zinc 950 | Page |
| `foreground` | MW Black | Zinc 50 | Primary text |
| `card` / `card-foreground` | white / MW Black | Zinc 900 / Zinc 50 | Cards |
| `popover` / `popover-foreground` | white / MW Black | Zinc 900 / Zinc 50 | Menus, popovers, selects. Menus always match surface |
| `primary` / `primary-foreground` | Blue 600 / MW White | Blue 700 / MW White | Primary buttons, checked controls, active states |
| `secondary` / `secondary-foreground` | Zinc 100 / MW Black | Zinc 800 / Zinc 50 | Secondary buttons, segmented controls |
| `muted` / `muted-foreground` | Zinc 100 / Zinc 500 | Zinc 800 / Zinc 400 | Input fills, helper text, descriptions |
| `accent` / `accent-foreground` | Zinc 100 / MW Black | Zinc 800 / Zinc 50 | Hover and highlighted menu items (Mira "subtle" accent) |
| `destructive` | Mira red | Mira red (dark) | Delete and irreversible actions only |
| `success` / `success-foreground` | `#407E0B` / white | `#67BF22` / MW Black | Positive values, completed states. **v4 addition** |
| `link` | Blue 600 | Blue 300 | Inline text links and blue text. **v4 addition** |
| `border` / `input` | Zinc 200 | white 10% / 15% | Hairlines and control borders |
| `ring` | Zinc 400 | Zinc 500 | Focus rings (Mira neutral ring) |
| `chart-1` to `chart-5` | Blue 300 to 700 | Blue 300 to 700 | Single-hue blue charts |
| `sidebar-*` | Mira values, MW black text, Blue 600 primary | Mira values, Blue 500 primary | Shell sidebar |

**Warning** has no dedicated token yet. Until one is decided, warnings use the foreground color with a `Warning` icon (icon led, no fill), the same approach v2 used. Do not invent an amber.

### Color rules

- Blue means "act here" or "this is selected". Primary buttons, checked checkboxes and radios, on switches, active nav item icon, sliders, progress, focused selections, links.
- One `default` (blue) button per view or per card section. Everything else is `secondary`, `outline` or `ghost`.
- Never fill a large surface with blue: no blue cards, banners, headers or page sections. Badges, buttons and chips can be blue.
- Body text is never blue. Blue text is for links and occasional inline emphasis only, always via `text-link` so it flips correctly in dark mode. Never `text-primary` on a dark background.
- Positive numbers use `text-success`, negative numbers use `text-destructive` or stay `foreground` with a minus sign. Color is never the only signal: pair with a sign, icon or label.
- Charts are single-hue blue using `chart-1` through `chart-5`. For more than five series, rethink the chart before adding colors.
- No gradients and no glows on UI. (Photographic or illustrative media inside a card is fine.)

---

## 2. Typography

### Families

| Role | Family | Tailwind | Notes |
|---|---|---|---|
| All UI text | TT Hoves | `font-sans` (default) | Replaces the preset's DM Sans everywhere, including headings |
| Fallback | DM Sans | (in the stack) | Only loads if TT Hoves fails. Never set it directly |
| Code | DM Mono | `font-mono` | Code snippets, env var keys, API paths, CLI commands. Nothing else |

TT Hoves weights: Regular (400), Medium (500), Bold (700). **Never Light.** Regular and Medium ship with the skill; the Bold file is still to be added (see `assets/setup/fonts.ts`).

### Sizes and weights: defer to Mira

Mira's generated components set their own text sizes and weights (compact: roughly 12 to 14px for control, label and description text, medium weight for card titles). Do not change them. The table below only covers page-level text that sits outside components, sized to sit comfortably above Mira's components.

| Style | Tailwind | Size | Weight | Use |
|---|---|---|---|---|
| Page Title | `text-xl font-medium` | 20px | Medium | One per page, in the page header |
| Section Heading | `text-base font-medium` | 16px | Medium | Groups of cards or form sections |
| Card Title | (Mira `CardTitle`) | Mira | Mira | Do not override |
| Body | `text-sm` | 14px | Regular | Paragraphs, table cells |
| Small | `text-xs` | 12px | Regular | Descriptions, helper text, captions, metadata |
| Metric | `text-2xl font-medium num` or `text-3xl num` | 24 to 30px | Medium | KPI values in cards |

Rules:
- 12px (`text-xs`) is the floor. Never go smaller.
- Line height comes from Tailwind defaults and Mira. Don't hand-tune it.
- Bold (700) is rare: inline emphasis inside body text only. Headings use Medium at most.
- Numbers that align or update (tables, metrics, currency, timers) use the `num` utility: `tabular-nums` plus `0.04em` letter spacing. TT Hoves' tabular figures are drawn tighter than its default figures (zeros touch in "8:00" without the tracking), so never use `tabular-nums` alone. Apply `num` to the number itself, not to surrounding words. Never switch to mono for numbers.
- Case rules live in `content.md`. Short version: Title Case for labels and headings, sentence case for prose, never all caps.

---

## 3. Icons

- Library: **Phosphor Icons**, `@phosphor-icons/react`. The preset already uses Phosphor; v4 sets **Light at 16px** globally via `IconContext` (see `assets/setup/providers.tsx`). The only exception is 12px icons, which use Regular.
- In server components, `@phosphor-icons/react/ssr` icons ignore context, so pass `weight="light"` explicitly.
- Sizes are a fixed scale. Never use 14px.

| Size | Weight | Where |
|---|---|---|
| 16px (`size-4`) | Light | **Default.** Every button (including `sm` and icon buttons), input, select, menu, tab, sidebar item, alert, toast and inline status icon |
| 12px (`size-3`) | **Regular** | Badges and breadcrumb separators only. Light strokes are too thin at 12px |
| 24 to 32px | Light | Standalone icons in empty states and large media slots |

- Mira's generated components shrink some icons to 14px (`size-3.5`, often on `sm` buttons). Change those to `size-4`.
- 12px icons import the Regular weight explicitly: `<Check size={12} weight="regular" />`.
- Never mix sizes within one list or toolbar.
- Color: icons inherit text color. Use `text-muted-foreground` for decorative icons, `currentColor` inside buttons. No blue icons except on active or selected items.
- Never mix in Lucide, Carbon or other sets. When converting, map icons using the table in `migration-v2-to-v4.md`.
- Icon-only buttons always get an `aria-label` and usually a `Tooltip`.

---

## 4. Logos

Assets in `assets/logos/` use `currentColor`, so they follow `foreground` in both modes.

| File | Use |
|---|---|
| `mw-icon.svg` | Default. The sidebar header mark, favicons, compact spaces |
| `mw-logo.svg` | Horizontal wordmark. Sign-in screens, external or client-facing surfaces |
| `mw-logo-stacked.svg` | Square layouts only |

Rules: inline the SVG, set `color` on the parent, never hardcode a fill, never stretch, never place on a blue fill. In the sidebar the icon sits in the `SidebarHeader` beside the product name "Midwestern Platform" (see `patterns.md`).

---

## 5. Radius, spacing, elevation

- **Radius:** `--radius: 0.45rem` (Mira "Small"). Components derive `rounded-sm/md/lg` from it. Use the derived classes; never hardcode radius and never set `rounded-none` to imitate v2.
- **Pills:** badges, switches and avatars are fully rounded because Mira makes them so. Leave them.
- **Spacing:** Tailwind's 4px scale, as Mira uses it. Inside components, never change Mira's padding or gaps. For page layout use: page padding `p-4` to `p-6`, gap between cards `gap-4`, gap between page sections `gap-6`, form field stack `gap-4` (or Mira's `FieldGroup` defaults).
- **Density:** Mira is already compact. There is no separate compact mode in v4; don't shrink further.
- **Elevation:** Mira relies on borders and rings, not shadows. Cards stay flat with their default border. Overlays (dialogs, popovers, menus) keep Mira's shadow. Don't add shadows elsewhere.
- **Layout widths:** Forms and settings max out around `max-w-2xl`. Data pages run full width. Dialogs use Mira's defaults.

---

## 6. Dark mode

- Strategy: `class` on `<html>` via `next-themes`. Light is the default.
- Dark mode structure (surfaces, borders, muted text) is Mira's Zinc dark. Only blue, success and link differ.
- Primary shifts from Blue 600 to Blue 700 so white text keeps contrast on fills.
- Blue as text on dark surfaces uses `text-link` (Blue 300). Never Blue 600 text on dark.
- Test every screen in both modes before handing back.

---

## 7. Setup checklist (new project)

1. `pnpm dlx shadcn@latest init --preset b1a0Rv7GV --template next`
2. In the shadcn create panel or `components.json`, confirm menus are set to the default (surface) style, not Inverted/Translucent. If components were already generated as inverted, see `components.md` §Menus.
3. Apply `assets/mw-platform-design-system-v4-theme.css` to `app/globals.css` as its header comment describes.
4. Copy `assets/fonts/` to `app/fonts/`, add `assets/setup/fonts.ts` and `providers.tsx`, and update `app/layout.tsx` per `layout.example.tsx`. Remove the preset's DM Sans import.
5. `pnpm add next-themes` (and `@phosphor-icons/react` if the preset didn't add it).
6. Add components as needed: `pnpm dlx shadcn@latest add sidebar card table ...`
7. Search the repo for `DM_Sans`, `uppercase`, `lucide-react` and `font-mono`; resolve every hit against these rules.
