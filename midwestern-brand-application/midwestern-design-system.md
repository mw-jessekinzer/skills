---
name: midwestern-design-system
version: 1.0.0
description: Apply Midwestern brand guidelines to web components, data visualizations, and documents. Use whenever producing on-brand HTML/CSS output.
---

# Midwestern Design System

This skill defines the complete Midwestern brand system for web development. Follow every rule here when generating HTML, CSS, or component markup. When in doubt, choose the simpler, sharper, more restrained option.

---

## 1. Colors

### Primitive palette

| Name   | Hex       | CSS custom property     |
|--------|-----------|-------------------------|
| White  | `#F6F7FE` | `--mw-color-white`      |
| Black  | `#010313` | `--mw-color-black`      |
| Blue   | `#2237F1` | `--mw-color-blue`       |
| Green  | `#C7FA50` | `--mw-color-green`      |
| Muted  | `#666666` | `--mw-color-muted`      |

### Semantic tokens

| Token                      | Light mode | Dark mode  |
|----------------------------|------------|------------|
| `--mw-color-background`    | `#F6F7FE`  | `#010313`  |
| `--mw-color-foreground`    | `#010313`  | `#F6F7FE`  |
| `--mw-color-inverse`       | `#F6F7FE`  | `#010313`  |

Dark mode is activated via the `[data-theme="dark"]` attribute on the root element:

```css
[data-theme="dark"] {
  --mw-color-background: #010313;
  --mw-color-foreground: #F6F7FE;
  --mw-color-inverse: #010313;
}
```

### 60-30-10 rule

- **60 %** — Background color (white or black depending on mode)
- **30 %** — Foreground text and structural elements (black or white)
- **10 %** — Accent (blue and green combined)

### Usage rules

- **Never** use blue or green as a large background fill (full section, full card, hero). They are accent-only.
- White text on blue or black backgrounds.
- Black text on white or green backgrounds.
- Green is the **rarest** color. Reserve it for callout numbers, badges, or small highlight moments.
- Blue is for interactive elements (links, CTAs, overlines) and small accent blocks.
- Use `--mw-color-muted` (`#666666`) for secondary/helper text and disabled states.

---

## 2. Typography

### Font families

| Context               | Family      | CSS custom property   | Fallback stack               |
|-----------------------|-------------|----------------------|------------------------------|
| Web (default)         | DM Sans     | `--mw-font-primary`  | `'DM Sans', sans-serif`      |
| System / installed    | TT Hoves    | `--mw-font-system`   | `'TT Hoves', sans-serif`     |
| Code                  | System mono | `--mw-font-mono`     | `ui-monospace, 'SF Mono', 'Cascadia Code', monospace` |

Use `--mw-font-primary` (DM Sans) for all web output. Use `--mw-font-system` (TT Hoves) only when the font is confirmed installed (presentations, local tools, Figma exports).

### Web type scale

| Token               | Size   | CSS custom property    | Typical use                  |
|----------------------|--------|------------------------|------------------------------|
| Hero                 | 64 px  | `--mw-text-hero`       | Landing hero headlines       |
| Display              | 48 px  | `--mw-text-display`    | Page titles, section heroes  |
| H1                   | 40 px  | `--mw-text-h1`         | Primary headings             |
| H2                   | 32 px  | `--mw-text-h2`         | Section headings             |
| H3                   | 28 px  | `--mw-text-h3`         | Sub-section headings         |
| H4                   | 24 px  | `--mw-text-h4`         | Card titles, group labels    |
| H5                   | 20 px  | `--mw-text-h5`         | Small headings, overlines    |
| Body Large           | 18 px  | `--mw-text-body-lg`    | Lead paragraphs, intros      |
| Body                 | 16 px  | `--mw-text-body`       | Default body copy            |
| Body Small           | 14 px  | `--mw-text-body-sm`    | Captions, metadata, helpers  |
| Caption              | 12 px  | `--mw-text-caption`    | Fine print, labels           |

### Presentation type scale (reference only)

These are the sizes used in slide decks (roughly 2x the web scale). Included for cross-referencing with the `midwestern-decks` skill.

| Token          | Size    |
|----------------|---------|
| Hero           | 128 px  |
| Display        | 96 px   |
| H1             | 80 px   |
| H2             | 60 px   |
| H3             | 48 px   |
| H4             | 40 px   |
| H5             | 32 px   |
| Body Large     | 24 px   |
| Body           | 20 px   |
| Body Small     | 16 px   |
| Caption        | 12 px   |

### Typography rules

- **Sentence case always.** Never use ALL CAPS or Title Case for headings.
- Headings use **regular weight** (`font-weight: 400`). This is non-negotiable.
- Use **bold (700)** or **medium (500)** sparingly — only within body text to create hierarchy (e.g., a bold label before a description).
- Blue text is reserved for **overlines** and **CTAs** only. Never set a heading or body paragraph in blue.
- On dark backgrounds, body text may use reduced opacity (`rgba(246, 247, 254, 0.6)` or `0.5`) for secondary content. **Never** reduce opacity on headings.
- Line height: `1.2` for display/heading sizes, `1.5` for body sizes.

```css
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

The system is built on an **8 pt grid**. All spacing values are defined as CSS custom properties.

| Token              | Value  | Typical use                        |
|--------------------|--------|------------------------------------|
| `--mw-spacing-0`   | 0 px   | Reset                              |
| `--mw-spacing-1`   | 1 px   | Borders, hairlines                 |
| `--mw-spacing-2`   | 2 px   | Tight inline gaps                  |
| `--mw-spacing-3`   | 4 px   | Icon-to-text gaps                  |
| `--mw-spacing-4`   | 6 px   | Compact internal padding           |
| `--mw-spacing-5`   | 8 px   | Tight component gaps               |
| `--mw-spacing-6`   | 12 px  | Small component gaps, badge padding|
| `--mw-spacing-7`   | 16 px  | Default component internal padding |
| `--mw-spacing-8`   | 20 px  | Medium component padding           |
| `--mw-spacing-9`   | 24 px  | Standard component padding         |
| `--mw-spacing-10`  | 32 px  | Section internal padding           |
| `--mw-spacing-11`  | 40 px  | Large section padding              |
| `--mw-spacing-12`  | 48 px  | Page-level padding (small screens) |
| `--mw-spacing-13`  | 56 px  | Page-level padding (medium)        |
| `--mw-spacing-14`  | 64 px  | Page-level padding (large screens) |

### Usage guidance

- **Page padding**: `--mw-spacing-12` to `--mw-spacing-14` depending on viewport.
- **Component internal padding**: `--mw-spacing-9` to `--mw-spacing-10`.
- **Tight gaps** (between related items, icon + label, stacked labels): `--mw-spacing-5` to `--mw-spacing-6`.

```css
:root {
  --mw-spacing-0: 0px;
  --mw-spacing-1: 1px;
  --mw-spacing-2: 2px;
  --mw-spacing-3: 4px;
  --mw-spacing-4: 6px;
  --mw-spacing-5: 8px;
  --mw-spacing-6: 12px;
  --mw-spacing-7: 16px;
  --mw-spacing-8: 20px;
  --mw-spacing-9: 24px;
  --mw-spacing-10: 32px;
  --mw-spacing-11: 40px;
  --mw-spacing-12: 48px;
  --mw-spacing-13: 56px;
  --mw-spacing-14: 64px;
}
```

---

## 4. Border radius

```css
* { border-radius: 0; }
```

**Always `0`.** No rounded corners anywhere — buttons, cards, inputs, badges, images, containers. No exceptions. This is a defining characteristic of the Midwestern visual identity.

The token `--mw-radius: 0px` exists for consistency but the value must never change.

---

## 5. Components

### Buttons

Three variants: **primary**, **secondary**, **ghost**.

```css
/* Shared base */
.mw-btn {
  font-family: var(--mw-font-primary);
  font-size: var(--mw-text-body-sm);
  font-weight: var(--mw-font-weight-medium);
  line-height: 1;
  padding: var(--mw-spacing-6) var(--mw-spacing-9);
  border: 1px solid transparent;
  border-radius: 0;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

/* Primary — blue background, white text */
.mw-btn--primary {
  background-color: var(--mw-color-blue);
  color: var(--mw-color-white);
  border-color: var(--mw-color-blue);
}
.mw-btn--primary:hover {
  background-color: #1a2bc4;
}

/* Secondary — transparent, border, foreground text */
.mw-btn--secondary {
  background-color: transparent;
  color: var(--mw-color-foreground);
  border-color: var(--mw-color-foreground);
}
.mw-btn--secondary:hover {
  background-color: var(--mw-color-foreground);
  color: var(--mw-color-background);
}

/* Ghost — no border, foreground text */
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
```

### Cards

#### Standard card

```css
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
```

#### KPI card

Used to display a single metric prominently.

```css
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

### Badges / chips

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

/* Default — muted outline */
.mw-badge--default {
  background-color: transparent;
  color: var(--mw-color-foreground);
  border: 1px solid var(--mw-color-muted);
}

/* Blue accent */
.mw-badge--blue {
  background-color: var(--mw-color-blue);
  color: var(--mw-color-white);
  border: 1px solid var(--mw-color-blue);
}

/* Green accent — use sparingly */
.mw-badge--green {
  background-color: var(--mw-color-green);
  color: var(--mw-color-black);
  border: 1px solid var(--mw-color-green);
}

/* Dark-mode chip (frosted) */
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
  text-transform: none; /* sentence case */
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

## 6. Data visualization

When generating charts, graphs, or data visualizations:

- **Background**: white (`#F6F7FE`) or black (`#010313`) depending on mode. Never a colored background.
- **Primary data color**: foreground (black in light mode, white in dark mode).
- **Highlight color**: blue (`#2237F1`) for the primary data point or series being emphasized.
- **Callout color**: green (`#C7FA50`) for a single standout metric or annotation. Use once per chart at most.
- **Secondary data**: muted (`#666666`) or foreground at reduced opacity.
- **Grid lines**: foreground at 8-10 % opacity. Never prominent.
- **Axes and labels**: muted color, `--mw-text-caption` size.
- **Sharp corners on everything**: bars, containers, tooltips, legends. No rounded edges.
- **No gradients**. Flat fills only.

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

---

## 7. Do's and don'ts

### Do

- Use the semantic tokens (`--mw-color-background`, `--mw-color-foreground`) so dark mode works automatically.
- Keep all corners sharp — `border-radius: 0` everywhere.
- Use sentence case for all text.
- Use regular (400) weight for headings.
- Use the 8 pt spacing grid exclusively.
- Use DM Sans for all web-rendered text.
- Maintain generous whitespace — when unsure, add more space, not less.
- Use blue only for interactive elements, overlines, and small accent areas.
- Use green only for standout numbers, badges, or single callout moments.
- Use 1 px solid borders at low opacity for structural dividers.
- Keep UI dense but not cramped — align to the grid and let spacing tokens do the work.
- Test in both light and dark mode.

### Don't

- Don't round corners. Ever. Not even 2 px.
- Don't use blue or green as full-width or full-section backgrounds.
- Don't set headings in bold. Headings are always regular weight.
- Don't use ALL CAPS or Title Case.
- Don't use gradients, drop shadows, or glows.
- Don't mix DM Sans and TT Hoves in the same web page.
- Don't use font sizes outside the defined type scale.
- Don't use spacing values outside the defined spacing tokens.
- Don't reduce heading opacity on dark backgrounds (body text only).
- Don't use colored text for body paragraphs — only foreground, muted, or reduced-opacity foreground.
- Don't use more than two accent colors on a single screen.
- Don't introduce additional brand colors. The palette is five colors. That's it.
