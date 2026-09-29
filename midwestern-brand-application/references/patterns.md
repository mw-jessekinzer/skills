---
name: midwestern-patterns
version: 1.0.0
description: "Reusable layout and composition patterns for Midwestern Interactive branded output. These are structural decisions — not brand primitives. Read alongside foundation.md for any HTML artifact, dashboard, internal tool, or document."
---

# Midwestern Patterns

Reusable layout and composition patterns. These are structural decisions that have been made deliberately and should be applied consistently. They are not design tokens — see `foundation.md` for those.

Read `foundation.md` first. This file extends it.

---

## 1. Page header

Every internal tool, dashboard, or document page uses this two-row header structure. Do not invent alternatives.

### Structure

**Row 1 — brand bar:** MW icon mark left-aligned, page metadata (date, last updated, etc.) right-aligned. Nothing else on this row.

**Row 2 — page title:** Blue overline (section/context label) above the H1 page title. Full width — no competing element to the right.

The two rows are separated by a consistent gap. A 1px hairline border at `rgba(1,3,19,0.15)` runs below the entire header block. Bottom margin separates the header from the first content section.

### Logo usage in the header

Always use `mw-icon.svg` for internal tools and dashboards. Set `color: var(--mw-color-foreground)` on the parent so the mark inherits correctly via `currentColor`. Render the icon at `width: 32px`.

Never use the horizontal wordmark (`mw-logo.svg`) or stacked wordmark (`mw-logo-stacked.svg`) in internal page headers — those are for external/client-facing output only.

### CSS

```css
.header {
  display: flex;
  flex-direction: column;
  gap: var(--mw-spacing-7);
  border-bottom: 1px solid rgba(1,3,19,0.15);
  padding-bottom: var(--mw-spacing-8);
  margin-bottom: var(--mw-spacing-9);
}

/* Row 1 */
.header-brand {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-logo {
  color: var(--mw-color-foreground);
  display: flex;
  align-items: center;
}
.header-logo svg {
  width: 32px;
  height: auto;
  display: block;
}
.header-date {
  font-size: var(--mw-text-body-sm);
  color: var(--mw-color-muted);
}
.header-date strong {
  color: var(--mw-color-foreground);
  font-weight: var(--mw-font-weight-medium);
}

/* Row 2 */
.header-title .overline {
  font-size: var(--mw-text-body-sm);
  color: var(--mw-color-blue);
  letter-spacing: 0.02em;
  margin-bottom: var(--mw-spacing-3);
}
.header-title h1 {
  font-size: var(--mw-text-h2);
  font-weight: var(--mw-font-weight-regular);
  line-height: var(--mw-line-height-display);
  letter-spacing: -1px;
}
```

### HTML

```html
<div class="header">
  <!-- Row 1: brand + metadata -->
  <div class="header-brand">
    <div class="header-logo">
      <svg width="282" height="150" viewBox="0 0 282 150" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M218.994 0.133175L111.936 106.318V150H155.932L218.994 87.4519V150H281.25V17.5348L263.705 0.133175H218.994Z" fill="currentColor"/>
        <path d="M160.417 0H107.013L0 106.141V149.822H43.9957L178.125 17.5348L160.417 0Z" fill="currentColor"/>
      </svg>
    </div>
    <div class="header-date">Updated <strong>Month D, YYYY</strong></div>
  </div>
  <!-- Row 2: page title -->
  <div class="header-title">
    <div class="overline">Section label</div>
    <h1>Page title</h1>
  </div>
</div>
```

### Rules

- Always two rows. Never collapse into a single row.
- Row 1 metadata is date/last-updated only. Do not add navigation, actions, or avatars to row 1 without explicit instruction.
- Row 2 always has both the overline and the H1. Never omit the overline.
- Overline text is the section or context label (e.g. "Design operations", "Client delivery"). Always in blue.
- H1 is the specific page title. Always sentence case, regular weight.
- The `mw-icon.svg` SVG must be inlined — do not use an `<img>` tag.

---

<!-- Future patterns go here. Examples: empty states, section dividers, data card layouts, modal shells. -->
