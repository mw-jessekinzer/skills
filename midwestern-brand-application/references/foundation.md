---
name: midwestern-design-system
version: 1.1.0
description: "Apply Midwestern Interactive brand guidelines to any visual output — HTML/CSS components, web pages, landing pages, one-pagers, data visualizations, dashboards, documents, or any artifact that needs to look like Midwestern. Triggers on: 'on-brand', 'Midwestern brand', 'MW style', 'design system', 'brand colors', or when producing any visual output for Midwestern. Does NOT trigger for general business questions, strategy discussions, or non-visual content."
---

# Midwestern Design System

This file is the single source of truth for all Midwestern Interactive brand standards. Fetch this file before generating any visual output. Follow every rule here exactly. When in doubt, choose the simpler, sharper, more restrained option.

---

## 1. Colors

### Primitive palette

| Name        | Hex       | CSS custom property       |
|-------------|-----------|---------------------------|
| White       | `#F6F7FE` | `--mw-color-white`        |
| Black       | `#010313` | `--mw-color-black`        |
| Blue        | `#2237F1` | `--mw-color-blue`         |
| Navy        | `#1A2CD1` | `--mw-color-navy`         |
| Green       | `#C7FA50` | `--mw-color-green`        |
| Muted Light | `#E8E9F4` | `--mw-color-muted-light`  |
| Muted       | `#666666` | `--mw-color-muted`        |
| Light Gray  | `#A9A9A9` | `--mw-color-gray-light`   |
| Danger      | `#CC1838` | `--mw-color-danger`       |
| Success     | `#407E0B` | `--mw-color-success`      |

### Semantic tokens

| Token                        | Light mode  | Dark mode   |
|------------------------------|-------------|-------------|
| `--mw-color-background`      | `#F6F7FE`   | `#010313`   |
| `--mw-color-foreground`      | `#010313`   | `#F6F7FE`   |
| `--mw-color-inverse`         | `#F6F7FE`   | `#010313`   |
| `--mw-color-surface`         | `#E8E9F4`   | `#E8E9F4`   |
| `--mw-color-accent`          | `#2237F1`   | `#C7FA50`   |
| `--mw-color-disabled`        | `#A9A9A9`   | `#A9A9A9`   |
| `--mw-color-destructive`     | `#CC1838`   | `#CC1838`   |
| `--mw-color-success`         | `#407E0B`   | `#407E0B`   |

### CSS variable definitions

```css
:root {
  /* Primitives */
  --mw-color-white: #F6F7FE;
  --mw-color-black: #010313;
  --mw-color-blue: #2237F1;
  --mw-color-navy: #1A2CD1;
  --mw-color-green: #C7FA50;
  --mw-color-muted-light: #E8E9F4;
  --mw-color-muted: #666666;
  --mw-color-gray-light: #A9A9A9;
  --mw-color-danger: #CC1838;
  --mw-color-success: #407E0B;

  /* Semantic — light mode defaults */
  --mw-color-background: #F6F7FE;
  --mw-color-foreground: #010313;
  --mw-color-inverse: #F6F7FE;
  --mw-color-surface: #E8E9F4;
  --mw-color-accent: #2237F1;       /* Blue in light mode */
  --mw-color-disabled: #A9A9A9;
  --mw-color-destructive: #CC1838;
}

/* Dark mode — default for all Midwestern branded output */
[data-theme="dark"] {
  --mw-color-background: #010313;
  --mw-color-foreground: #F6F7FE;
  --mw-color-inverse: #010313;
  --mw-color-accent: #C7FA50;       /* Green in dark mode */
}
```

**Light mode is the default for all Midwestern branded output.** Apply `data-theme="light"` to the root element unless the user explicitly requests dark mode.

### 60-30-10 rule

**Dark mode:**
- 60% `#010313` (Black) — backgrounds
- 30% `#F6F7FE` (White) — typography and structural elements
- 10% `#2237F1` (Blue) — accents
- 5% `#C7FA50` (Green) — highlight moments only

**Light mode:**
- 60% `#F6F7FE` (White) — backgrounds
- 30% `#010313` (Black) — typography
- 10% `#2237F1` (Blue) — accents
- 5% `#C7FA50` (Green) — highlight moments only

### Color usage rules

- **Never** use blue or green as a large background fill (full section, full card, hero).
- White text on blue or black backgrounds. Black text on white or green backgrounds.
- Green is the **rarest** color. Reserve it for callout numbers, badges, or single highlight moments — once per screen at most.
- Blue is for interactive elements (links, CTAs, overlines) and small accent areas only.
- Use `--mw-color-muted` for secondary/helper text.
- Use `--mw-color-disabled` for disabled states.
- Use `--mw-color-destructive` for delete or irreversible actions only.
- Never introduce colors outside this palette. The palette is fixed.

---

## 2. Typography

### Font families

| Context            | Family      | CSS custom property  | Fallback stack                            |
|--------------------|-------------|----------------------|-------------------------------------------|
| Web (default)      | TT Hoves    | `--mw-font-primary`  | `'TT Hoves', 'DM Sans', sans-serif`       |
| Web fallback       | DM Sans     | `--mw-font-fallback` | `'DM Sans', sans-serif`                   |
| Code               | System mono | `--mw-font-mono`     | `ui-monospace, 'SF Mono', monospace`      |

**TT Hoves is the primary brand font for all output.** DM Sans is the fallback when TT Hoves cannot be loaded.

#### Loading TT Hoves in HTML artifacts

TT Hoves Regular is bundled in `assets/TT_Hoves_Regular.otf`. In HTML artifacts, declare it via `@font-face` at the top of the `<style>` block. Because the font file is not accessible from a deployed artifact URL, also load DM Sans from Google Fonts as the fallback:

```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700&display=swap" rel="stylesheet">
```

```css
@font-face {
  font-family: 'TT Hoves';
  src: url('assets/TT_Hoves_Regular.otf') format('opentype');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

/* TT Hoves is the primary brand font. DM Sans loads as the fallback. */
:root {
  --mw-font-primary: 'TT Hoves', 'DM Sans', sans-serif;
  --mw-font-fallback: 'DM Sans', sans-serif;
}
```

In environments where `@font-face` src paths resolve (e.g., local dev, Electron, file:// contexts), TT Hoves loads directly. In all other cases, DM Sans is the seamless fallback — no additional code change needed.

### Web type scale

| Token                  | Size  | CSS custom property     | Typical use                  |
|------------------------|-------|-------------------------|------------------------------|
| Hero                   | 64px  | `--mw-text-hero`        | Landing hero headlines       |
| Display                | 48px  | `--mw-text-display`     | Page titles, section heroes  |
| H1                     | 40px  | `--mw-text-h1`          | Primary headings             |
| H2                     | 32px  | `--mw-text-h2`          | Section headings             |
| H3                     | 28px  | `--mw-text-h3`          | Sub-section headings         |
| H4                     | 24px  | `--mw-text-h4`          | Card titles, group labels    |
| H5                     | 20px  | `--mw-text-h5`          | Small headings, overlines    |
| Body Large             | 18px  | `--mw-text-body-lg`     | Lead paragraphs, intros      |
| Body                   | 16px  | `--mw-text-body`        | Default body copy, buttons   |
| Body Small             | 14px  | `--mw-text-body-sm`     | Captions, metadata, helpers  |
| Caption                | 12px  | `--mw-text-caption`     | Fine print, labels           |

### Presentation type scale (reference only)

For slide decks — use with `midwestern-decks.md`.

| Level       | Size   |
|-------------|--------|
| Display XL  | 128px  |
| Hero        | 96px   |
| H1          | 80px   |
| H2          | 60px   |
| H3          | 48px   |
| H4          | 40px   |
| H5          | 32px   |
| Body Large  | 24px   |
| Body        | 20px   |
| Body Small  | 16px   |
| Caption     | 12px   |

### Typography rules

- **Sentence case always.** Never use ALL CAPS or Title Case for headings.
- Headings use **regular weight** (`font-weight: 400`). Non-negotiable.
- Use bold (700) or medium (500) only within body text to create hierarchy — never on headings.
- Blue text is reserved for overlines and CTAs only. Never set a heading or body paragraph in blue.
- On dark backgrounds, body text may use reduced opacity (`rgba(246, 247, 254, 0.6)`) for secondary content. Never reduce opacity on headings.
- Line height: `1.2` for display/heading sizes, `1.5` for body sizes.
- Letter spacing: `-1px` on large headings (H1 and above), `0` on body.

```css
:root {
  --mw-font-primary: 'TT Hoves', 'DM Sans', sans-serif;
  --mw-font-fallback: 'DM Sans', sans-serif;
  --mw-font-mono: ui-monospace, 'SF Mono', monospace;
  --mw-font-weight-regular: 400;
  --mw-font-weight-medium: 500;
  --mw-font-weight-bold: 700;
  --mw-line-height-display: 1.2;
  --mw-line-height-body: 1.5;
  --mw-text-hero: 64px;
  --mw-text-display: 48px;
  --mw-text-h1: 40px;
  --mw-text-h2: 32px;
  --mw-text-h3: 28px;
  --mw-text-h4: 24px;
  --mw-text-h5: 20px;
  --mw-text-body-lg: 18px;
  --mw-text-body: 16px;
  --mw-text-body-sm: 14px;
  --mw-text-caption: 12px;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--mw-font-primary);
  font-weight: var(--mw-font-weight-regular);
  line-height: var(--mw-line-height-display);
}

body {
  font-family: var(--mw-font-primary);
  font-weight: var(--mw-font-weight-regular);
  font-size: var(--mw-text-body);
  line-height: var(--mw-line-height-body);
}

.overline {
  font-size: var(--mw-text-body-sm);
  color: var(--mw-color-blue);
  letter-spacing: 0.02em;
}
```

---

## 3. Spacing

Built on an **8pt grid**. Use only these token values. Never use arbitrary pixel values.

```css
:root {
  --mw-spacing-0:  0px;
  --mw-spacing-1:  1px;
  --mw-spacing-2:  2px;
  --mw-spacing-3:  4px;
  --mw-spacing-4:  6px;
  --mw-spacing-5:  8px;
  --mw-spacing-6:  12px;
  --mw-spacing-7:  16px;
  --mw-spacing-8:  20px;
  --mw-spacing-9:  24px;
  --mw-spacing-10: 32px;
  --mw-spacing-11: 40px;
  --mw-spacing-12: 48px;
  --mw-spacing-13: 56px;
  --mw-spacing-14: 64px;
}
```

| Token              | Value | Typical use                         |
|--------------------|-------|-------------------------------------|
| `--mw-spacing-0`   | 0px   | Reset                               |
| `--mw-spacing-1`   | 1px   | Borders, hairlines                  |
| `--mw-spacing-2`   | 2px   | Tight inline gaps                   |
| `--mw-spacing-3`   | 4px   | Icon-to-text gaps                   |
| `--mw-spacing-4`   | 6px   | Compact internal padding            |
| `--mw-spacing-5`   | 8px   | Tight component gaps                |
| `--mw-spacing-6`   | 12px  | Small gaps, badge padding           |
| `--mw-spacing-7`   | 16px  | Default component internal padding  |
| `--mw-spacing-8`   | 20px  | Medium component padding            |
| `--mw-spacing-9`   | 24px  | Standard component padding          |
| `--mw-spacing-10`  | 32px  | Section internal padding            |
| `--mw-spacing-11`  | 40px  | Large section padding               |
| `--mw-spacing-12`  | 48px  | Page-level padding (small screens)  |
| `--mw-spacing-13`  | 56px  | Page-level padding (medium)         |
| `--mw-spacing-14`  | 64px  | Page-level padding (large screens)  |

**Usage guidance:**
- Page padding: `--mw-spacing-12` to `--mw-spacing-14` depending on viewport
- Component internal padding: `--mw-spacing-9` to `--mw-spacing-10`
- Tight gaps (icon + label, stacked labels): `--mw-spacing-5` to `--mw-spacing-6`
- Maintain generous whitespace — when unsure, add more space, not less

---

## 4. Border radius

```css
* { border-radius: 0; }
--mw-radius: 0px;
```

**Always `0`. No exceptions.** No rounded corners on buttons, cards, inputs, badges, images, or any container. This is a defining characteristic of the Midwestern visual identity.

---

## 5. Breakpoints

```css
:root {
  --mw-viewport-desktop: 1280px;
  --mw-viewport-tablet: 768px;
  --mw-viewport-mobile: 375px;
}
```

---

## 6. Components

### Buttons

Four variants. All buttons: DM Sans Regular, 16px, 40px height, 0 border radius.
Arrow icon rotates to upper-right on hover.

```css
/* Shared base */
.mw-btn {
  font-family: var(--mw-font-primary);
  font-size: var(--mw-text-body);
  font-weight: var(--mw-font-weight-regular);
  line-height: 1;
  height: 40px;
  padding: var(--mw-spacing-5) var(--mw-spacing-7);
  border: 1px solid transparent;
  border-radius: 0;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: var(--mw-spacing-5);
}

/* Primary — blue background, white text */
.mw-btn--primary {
  background-color: var(--mw-color-blue);
  color: var(--mw-color-white);
  border-color: var(--mw-color-blue);
}
.mw-btn--primary:hover {
  background-color: transparent;
  border-color: var(--mw-color-foreground);
  color: var(--mw-color-foreground);
}
.mw-btn--primary:active {
  background-color: var(--mw-color-surface);
  border-color: var(--mw-color-foreground);
  color: var(--mw-color-foreground);
}
.mw-btn--primary:focus {
  outline: 1px solid var(--mw-color-blue);
  outline-offset: 2px;
}
.mw-btn--primary:disabled {
  background-color: var(--mw-color-surface);
  border-color: var(--mw-color-disabled);
  color: var(--mw-color-disabled);
  cursor: not-allowed;
}

/* Secondary — dark background, white text */
.mw-btn--secondary {
  background-color: var(--mw-color-foreground);
  color: var(--mw-color-background);
  border-color: var(--mw-color-foreground);
}
.mw-btn--secondary:hover {
  background-color: transparent;
  border-color: var(--mw-color-foreground);
  color: var(--mw-color-foreground);
}
.mw-btn--secondary:active {
  background-color: var(--mw-color-surface);
  border-color: var(--mw-color-foreground);
  color: var(--mw-color-foreground);
}
.mw-btn--secondary:focus {
  outline: 1px solid var(--mw-color-blue);
  outline-offset: 2px;
}
.mw-btn--secondary:disabled {
  background-color: transparent;
  border-color: var(--mw-color-disabled);
  color: var(--mw-color-disabled);
  cursor: not-allowed;
}

/* Ghost — no border, no background */
.mw-btn--ghost {
  background-color: transparent;
  color: var(--mw-color-foreground);
  border-color: transparent;
}
.mw-btn--ghost:hover {
  background-color: rgba(1, 3, 19, 0.05);
}
[data-theme="dark"] .mw-btn--ghost:hover {
  background-color: rgba(246, 247, 254, 0.08);
}
.mw-btn--ghost:active {
  color: var(--mw-color-muted);
}
.mw-btn--ghost:disabled {
  color: var(--mw-color-disabled);
  cursor: not-allowed;
}

/* Destructive — red background, for high-risk irreversible actions only */
.mw-btn--destructive {
  background-color: var(--mw-color-destructive);
  color: var(--mw-color-white);
  border-color: var(--mw-color-destructive);
}
```

### Cards

```css
/* Standard card */
.mw-card {
  background-color: var(--mw-color-background);
  border: 1px solid rgba(1, 3, 19, 0.15);
  border-radius: 0;
  padding: var(--mw-spacing-10);
  display: flex;
  flex-direction: column;
  gap: var(--mw-spacing-7);
}

[data-theme="dark"] .mw-card {
  border-color: rgba(246, 247, 254, 0.15);
}

/* KPI card — single metric display */
.mw-card--kpi {
  background-color: var(--mw-color-background);
  border: 1px solid rgba(1, 3, 19, 0.15);
  border-radius: 0;
  padding: var(--mw-spacing-10);
  display: flex;
  flex-direction: column;
  gap: var(--mw-spacing-5);
}

.mw-card--kpi .kpi-label {
  font-size: var(--mw-text-body-sm);
  color: var(--mw-color-muted);
}

.mw-card--kpi .kpi-value {
  font-size: var(--mw-text-display);
  font-weight: var(--mw-font-weight-regular);
  line-height: var(--mw-line-height-display);
  color: var(--mw-color-foreground);
}

.mw-card--kpi .kpi-value--highlight {
  color: var(--mw-color-green);
}

[data-theme="dark"] .mw-card--kpi {
  border-color: rgba(246, 247, 254, 0.15);
}
```

### Inputs

```css
.mw-input {
  font-family: var(--mw-font-primary);
  font-size: var(--mw-text-body);
  font-weight: var(--mw-font-weight-regular);
  color: var(--mw-color-foreground);
  background-color: transparent;
  border: 1px solid rgba(1, 3, 19, 0.3);
  border-radius: 0;
  padding: var(--mw-spacing-6) var(--mw-spacing-7);
  width: 100%;
  outline: none;
  transition: border-color 0.15s ease;
}

.mw-input:focus {
  border-color: var(--mw-color-blue);
}

.mw-input::placeholder {
  color: var(--mw-color-muted);
}

.mw-input:disabled {
  color: var(--mw-color-disabled);
  border-color: var(--mw-color-disabled);
  cursor: not-allowed;
}

[data-theme="dark"] .mw-input {
  border-color: rgba(246, 247, 254, 0.3);
}

.mw-input-label {
  font-size: var(--mw-text-body-sm);
  color: var(--mw-color-muted);
  margin-bottom: var(--mw-spacing-3);
  display: block;
}
```

### Badges

```css
.mw-badge {
  display: inline-flex;
  align-items: center;
  font-family: var(--mw-font-primary);
  font-size: var(--mw-text-caption);
  font-weight: var(--mw-font-weight-medium);
  padding: var(--mw-spacing-3) var(--mw-spacing-6);
  border-radius: 0;
  line-height: 1;
}

.mw-badge--default {
  background-color: transparent;
  color: var(--mw-color-foreground);
  border: 1px solid var(--mw-color-muted);
}

.mw-badge--blue {
  background-color: var(--mw-color-blue);
  color: var(--mw-color-white);
  border: 1px solid var(--mw-color-blue);
}

/* Use sparingly — 5% rule applies */
.mw-badge--green {
  background-color: var(--mw-color-green);
  color: var(--mw-color-black);
  border: 1px solid var(--mw-color-green);
}

[data-theme="dark"] .mw-badge--frosted {
  background-color: rgba(246, 247, 254, 0.1);
  color: var(--mw-color-white);
  border: none;
}
```

### Data tables

```css
.mw-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--mw-font-primary);
  font-size: var(--mw-text-body-sm);
}

.mw-table th {
  text-align: left;
  font-weight: var(--mw-font-weight-medium);
  color: var(--mw-color-muted);
  font-size: var(--mw-text-caption);
  padding: var(--mw-spacing-5) var(--mw-spacing-7);
  border-bottom: 1px solid rgba(1, 3, 19, 0.15);
  text-transform: none;
}

.mw-table td {
  padding: var(--mw-spacing-6) var(--mw-spacing-7);
  border-bottom: 1px solid rgba(1, 3, 19, 0.08);
  color: var(--mw-color-foreground);
}

.mw-table tr:last-child td {
  border-bottom: none;
}

[data-theme="dark"] .mw-table th {
  border-bottom-color: rgba(246, 247, 254, 0.15);
}

[data-theme="dark"] .mw-table td {
  border-bottom-color: rgba(246, 247, 254, 0.08);
}
```

---

## 7. Data visualization

```css
.mw-chart {
  --chart-bg: var(--mw-color-background);
  --chart-primary: var(--mw-color-foreground);
  --chart-highlight: var(--mw-color-blue);
  --chart-callout: var(--mw-color-green);
  --chart-secondary: var(--mw-color-muted);
  --chart-grid: rgba(1, 3, 19, 0.08);
  font-family: var(--mw-font-primary);
}

[data-theme="dark"] .mw-chart {
  --chart-grid: rgba(246, 247, 254, 0.08);
}
```

- Background: `--mw-color-background` only. Never a colored background.
- Primary data: foreground color.
- Highlight: blue (`#2237F1`) for the primary data point or series.
- Callout: green (`#C7FA50`) for a single standout metric — once per chart at most.
- Secondary data: muted or foreground at reduced opacity.
- Grid lines: foreground at 8-10% opacity. Never prominent.
- Axes and labels: muted color, caption size.
- Sharp corners on bars, containers, tooltips, legends. No rounded edges.
- No gradients. Flat fills only.

---

## 8. ShadCN component fallback

When a component is needed that is not explicitly defined in this file, use ShadCN UI styled to Midwestern brand tokens. Map MI tokens to ShadCN CSS variables as follows:

```css
:root {
  --background: 240 44% 98%;           /* #F6F7FE */
  --foreground: 237 96% 4%;            /* #010313 */
  --primary: 232 88% 55%;              /* #2237F1 */
  --primary-foreground: 240 44% 98%;   /* #F6F7FE */
  --secondary: 237 96% 4%;             /* #010313 */
  --secondary-foreground: 240 44% 98%;
  --muted: 237 25% 91%;                /* #E8E9F4 */
  --muted-foreground: 0 0% 40%;        /* #666666 */
  --accent: 83 94% 65%;                /* #C7FA50 */
  --accent-foreground: 237 96% 4%;     /* #010313 */
  --destructive: 350 78% 44%;          /* #CC1838 */
  --destructive-foreground: 240 44% 98%;
  --border: 0 0% 66%;                  /* #A9A9A9 */
  --input: 0 0% 66%;
  --ring: 232 88% 55%;                 /* #2237F1 */
  --radius: 0rem;                      /* Always 0 */
}
```

Override ShadCN component defaults:
- `border-radius`: always 0 on every ShadCN component
- Font: always `var(--mw-font-primary)` (TT Hoves / DM Sans fallback), `font-weight: 400`
- Heading weight: always 400, never bold

---

## 9. Do's and don'ts

### Do

- Use semantic tokens (`--mw-color-background`, `--mw-color-foreground`) so dark mode works automatically.
- Apply `data-theme="dark"` by default on all branded output.
- Keep all corners sharp — `border-radius: 0` everywhere.
- Use sentence case for all text.
- Use regular (400) weight for all headings.
- Use the 8pt spacing grid exclusively — no arbitrary values.
- Use TT Hoves for all web-rendered text; DM Sans loads automatically as the fallback.
- Maintain generous whitespace — when unsure, add more space, not less.
- Use blue only for interactive elements, overlines, and small accent areas.
- Use green only for standout numbers, badges, or single callout moments.
- Use 1px solid borders at low opacity for structural dividers.
- Test in both light and dark mode.

### Don't

- Don't round corners. Ever. Not even 2px.
- Don't use blue or green as full-width or full-section backgrounds.
- Don't set headings in bold. Headings are always regular weight.
- Don't use ALL CAPS or Title Case.
- Don't use gradients, drop shadows, or glows.
- Don't use `--mw-font-fallback` (DM Sans) directly — always set `--mw-font-primary` and let the fallback stack handle it.
- Don't use font sizes outside the defined type scale.
- Don't use spacing values outside the defined spacing tokens.
- Don't reduce heading opacity on dark backgrounds (body text only).
- Don't use colored text for body paragraphs — foreground, muted, or reduced-opacity foreground only.
- Don't use more than two accent colors on a single screen.
- Don't introduce additional brand colors. The palette is fixed.
- Don't use `--mw-color-destructive` for anything other than delete or irreversible actions.

---

## 10. Self-check validation list

Before presenting any visual output, verify each item. Fix failures before presenting.

1. `data-theme="light"` is applied to the root element (unless dark mode was explicitly requested)
2. Background matches the correct mode — dark: `#010313`, light: `#F6F7FE`
3. All colors are within the defined palette — no off-token values
4. Font is TT Hoves (or DM Sans fallback) — `--mw-font-primary` applied; no other font families used
5. All headings are `font-weight: 400` — not bold
6. All text is sentence case — no Title Case, no ALL CAPS
7. `border-radius: 0` on every element — no exceptions
8. All spacing values match the token scale — no arbitrary px values
9. No gradients anywhere in the output
10. No drop shadows or glow effects
11. Blue used as accent only — not as a dominant background fill
12. Green used sparingly — once per screen at most
13. ShadCN components (if used) have `--radius: 0rem` and DM Sans applied
14. No more than two accent colors on a single screen
