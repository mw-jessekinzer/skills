---
name: midwestern-design-system
description: Apply Midwestern brand guidelines to any output — HTML/CSS components, copy, data visualizations, presentations, or documents. Use whenever the task requires on-brand visual design or producing content that represents the Midwestern brand.
---

# Midwestern Design System

## Overview

This skill encodes Midwestern's complete brand system: colors, typography, voice, component patterns, and more. Apply it whenever producing anything that represents Midwestern externally or internally.

**Keywords**: Midwestern brand, on-brand, style guide, brand colors, typography, brand voice, design system, components

---

## 1. Colors

### Brand Philosophy

Midwestern uses a minimal, high-contrast palette: black and white as the foundation, with blue as the primary accent and green as a secondary accent. This keeps things clean and flexible for impactful design.

### Base Palette

| Token | Hex | Use |
|---|---|---|
| `--white` | `#F6F7FE` | Light mode backgrounds, primary surface |
| `--black` | `#010313` | Light mode typography, dark mode backgrounds |
| `--blue` | `#2237F1` | Primary accent color — CTAs, interactive elements |
| `--green` | `#C7FA50` | Secondary accent — used very sparingly |

### Semantic Tokens

| Token | Value | Use |
|---|---|---|
| `--background` | `#F6F7FE` | Page/surface backgrounds |
| `--foreground` | `#010313` | Primary text and UI elements |
| `--inverse` | `#F6F7FE` | Text on dark/foreground surfaces |
| `--more-muted` | `#666666` | Muted text, subtle borders, dividers |

### The 60–30–10 Rule

**Light mode applications:**
- 60% White (`#F6F7FE`) — Background surfaces
- 25% Black (`#010313`) — Typography, UI elements
- 10% Blue (`#2237F1`) — Accents, interactive elements
- 5% Green (`#C7FA50`) — Secondary accents (sparingly)

**Dark mode applications:**
- 60% Black (`#010313`) — Background surfaces
- 25% White (`#F6F7FE`) — Typography, UI elements
- 10% Blue (`#2237F1`) — Accents, interactive elements
- 5% Green (`#C7FA50`) — Secondary accents (sparingly)

### CSS Custom Properties

```css
:root {
  --white:      #F6F7FE;
  --black:      #010313;
  --blue:       #2237F1;
  --green:      #C7FA50;

  /* Semantic */
  --background:  #F6F7FE;  /* light mode default */
  --foreground:  #010313;
  --inverse:     #F6F7FE;  /* text on dark surfaces */
  --more-muted:  #666666;  /* muted text / borders */
}

/* Dark mode override */
[data-theme="dark"] {
  --background: #010313;
  --foreground: #F6F7FE;
  --inverse:    #010313;
}
```

### Color Usage Rules

- **Never** use blue or green as a background color for large surfaces — reserve them for accents only
- **Always** use white text (`--inverse`) on blue or black backgrounds
- **Always** use black text (`--black`) on white or green backgrounds
- Green (`#C7FA50`) is the rarest color — if it appears frequently, pull back

---

## 2. Typography

### Typeface

Midwestern uses a single typeface across all applications: **TT Hoves**. Available in Regular, Medium, and Bold weights. Do not use Light. 

```css
--font-primary: 'TT Hoves', sans-serif;
```

### Core Rules

- **Sentence case always** — never title case or all-caps (e.g. "This is headline text", not "This Is Headline Text")
- **All text in TT Hoves** — no mixing in other typefaces
- **Blue (`#2237F1`) for overlines, CTAs, and hierarchy labels** — never for body copy
- **Regular weight** for long-form body paragraphs and for headings and UI
- Use bold and Medium sparingly. These are used to define a solid hierarchy within body copy and subheadings. Never for H1 headings.
- **On dark (#010313) backgrounds, body copy may be set to 60% opacity** (`rgba(246,247,254,0.6)`) to create hierarchy contrast with full-white headings. Use this when the heading needs to dominate and the body should recede. Never apply opacity to headings — only body copy. Full white body copy is also valid.

---

### Type Scale

#### Display — attention-grabbing hero titles, LH 1.2

| Style | Size | Letter Spacing | Line Height |
|---|---|---|---|
| Display XL | 128px | 0 | 1.2 |
| Display Large | 96px | 0 | 1.2 |
| Display Medium | 88px | 0 | 1.2 |

#### Heading — section and content titles, LH 1.2

| Style | Size | Letter Spacing | Line Height |
|---|---|---|---|
| Heading XL | 72px | -1px | 1.2 |
| Heading Large | 60px | -1px | 1.2 |
| Heading Medium | 48px | -1px | 1.2 |
| Heading Small | 40px | 0 | 1.2 |
| Heading XS | 36px | 0 | 1.2 |

#### Body — running text blocks, LH 1.5

| Style | Size | Letter Spacing | Line Height |
|---|---|---|---|
| Body XL | 40px | 0 | 1.5 |
| Body Large | 24px | 0 | 1.5 |
| Body Medium | 20px | 0 | 1.5 |
| Body Small | 16px | 0 | 1.5 |

#### Extras

| Style | Size | Letter Spacing | Line Height |
|---|---|---|---|
| Overline / Badge | 60px | -1px | 1.2 |
| CTA | 40px | -1px | 1.2 |
| Link | 16px | 0 | normal |
| Caption | 14px | 0 | 1.5 |
| Legal | 12px | 0 | 1.5 |

---

### Hierarchy in Practice

The type hierarchy follows a 60px base-unit proportional system:

- **Overline** (1.5× body) — small label above a headline, rendered in blue
- **Headline** (3.5× body) — primary attention grab, largest text on the page
- **Subheadline** (1.5× body) — supporting title below headline
- **Body Copy** — TT Hoves Regular, -1px LS, 1.75× line height
- **CTA** (1× body) — rendered in blue (`--highlight: #2237F1`), same size as body

### CSS Quick Reference

```css
/* Display */
.display-xl    { font-family: 'TT Hoves', sans-serif; font-size: 128px; font-weight: 400; line-height: 1.2; letter-spacing: 0; }
.display-large { font-family: 'TT Hoves', sans-serif; font-size: 96px;  font-weight: 400; line-height: 1.2; letter-spacing: 0; }

/* Headings */
.heading-xl     { font-family: 'TT Hoves', sans-serif; font-size: 72px; font-weight: 400; line-height: 1.2; letter-spacing: -1px; }
.heading-large  { font-family: 'TT Hoves', sans-serif; font-size: 60px; font-weight: 400; line-height: 1.2; letter-spacing: -1px; }
.heading-medium { font-family: 'TT Hoves', sans-serif; font-size: 48px; font-weight: 400; line-height: 1.2; letter-spacing: -1px; }
.heading-small  { font-family: 'TT Hoves', sans-serif; font-size: 40px; font-weight: 400; line-height: 1.2; letter-spacing: 0; }
.heading-xs     { font-family: 'TT Hoves', sans-serif; font-size: 36px; font-weight: 400; line-height: 1.2; letter-spacing: 0; }

/* Body */
.body-xl     { font-family: 'TT Hoves', sans-serif; font-size: 40px; font-weight: 400; line-height: 1.5; letter-spacing: 0; }
.body-large  { font-family: 'TT Hoves', sans-serif; font-size: 24px; font-weight: 400; line-height: 1.5; letter-spacing: 0; }
.body-medium { font-family: 'TT Hoves', sans-serif; font-size: 20px; font-weight: 400; line-height: 1.5; letter-spacing: 0; }
.body-small  { font-family: 'TT Hoves', sans-serif; font-size: 16px; font-weight: 400; line-height: 1.5; letter-spacing: 0; }

/* Extras */
.overline { font-family: 'TT Hoves', sans-serif; font-size: 60px; font-weight: 400; line-height: 1.2; letter-spacing: -1px; color: #2237F1; }
.cta      { font-family: 'TT Hoves', sans-serif; font-size: 40px; font-weight: 400; line-height: 1.2; letter-spacing: -1px; color: #2237F1; }
.caption  { font-family: 'TT Hoves', sans-serif; font-size: 14px; font-weight: 400; line-height: 1.5; }
.legal    { font-family: 'TT Hoves', sans-serif; font-size: 12px; font-weight: 400; line-height: 1.5; }
.link     { font-family: 'TT Hoves', sans-serif; font-size: 16px; font-weight: 400; color: #2237F1; }

/* Dark background body opacity variant */
.body-muted { color: rgba(246, 247, 254, 0.6); } /* use on body copy on #010313 backgrounds only */
```

---

## 3. Border Radius

**Always 0. Midwestern uses sharp corners on all elements — no exceptions.**

```css
* { border-radius: 0; }
```

This applies to: buttons, cards, inputs, modals, badges, images, containers, chips — everything. Never round any corner unless explicitly overriding for a specific technical reason (e.g. a circle avatar).

---

## 4. Spacing

### System

Midwestern uses an **8pt grid system**. Base unit is 8px (token `5`). All spacing, padding, margin, and gap values must come from this scale — never use arbitrary values.

### Scale

| Token | px | Multiple | Common use |
|---|---|---|---|
| `--0` | 0px | 0 | No spacing |
| `--1` | 1px | 0.125 | Hairlines, borders |
| `--2` | 2px | 0.25 | Fine borders |
| `--3` | 4px | 0.5 | Tight internal gaps |
| `--4` | 6px | 0.75 | Small icon padding |
| `--5` | 8px | **1 (Base)** | Default tight gap |
| `--6` | 12px | 1.5 | Compact padding |
| `--7` | 16px | 2 | Small padding, inline gaps |
| `--8` | 20px | 2.5 | Button padding (y-axis) |
| `--9` | 24px | 3 | Component internal padding |
| `--10` | 32px | 4 | Section element gaps |
| `--11` | 40px | 5 | Generous padding |
| `--12` | 48px | 6 | Section padding, page insets |
| `--13` | 56px | 7 | Large section gaps |
| `--14` | 64px | 8 | Page-level padding, hero spacing |

### CSS Custom Properties

```css
:root {
  --0:  0px;
  --1:  1px;
  --2:  2px;
  --3:  4px;
  --4:  6px;
  --5:  8px;   /* base unit */
  --6:  12px;
  --7:  16px;
  --8:  20px;
  --9:  24px;
  --10: 32px;
  --11: 40px;
  --12: 48px;
  --13: 56px;
  --14: 64px;
}
```

### Usage Rules

- **Only use tokens from this scale** — never hardcode arbitrary px values like `10px`, `15px`, `18px`
- **8px is the default minimum** comfortable spacing between distinct UI elements
- **Page-level padding** uses `--12` (48px) or `--14` (64px)
- **Component internal padding** uses `--9` (24px) or `--10` (32px)
- **Tight inline gaps** (icon + label, badge spacing) use `--5` (8px) or `--6` (12px)

---

## 5. Deck / Presentation Rules

### Background
Decks are always **dark mode** — full `#010313` background on every slide. No light slides.

### Slide Anatomy

Every slide follows the same structure:

**Top-left — Slide title**
- Section label: 20px TT Hoves, `rgba(246,247,254,0.5)` — sits just above the title
- Title: 60px TT Hoves Regular, white `#F6F7FE`, tracking -1px

**Bottom — Footer bar (present on every slide)**
- Thin top border: `1px rgba(246,247,254,0.4)`
- Left: slide number · deck name · section name at 50% opacity — all TT Hoves, 16px
- Right: Midwestern logo mark

**Content area — full bleed between title and footer**

### Colors in Decks

- **Primary text**: white `#F6F7FE`
- **Secondary / muted text**: `rgba(246,247,254,0.5)` — 50% opacity white
- **Descriptive body text**: `rgba(246,247,254,0.6)` — 60% opacity white
- **Accent highlight** (key numbers, callout values): green `#C7FA50`
- **Accent blocks** (image backgrounds, feature panels): blue `#2237F1`
- **Step/numbered badges**: green `#C7FA50` fill, black `#010313` text
- **Label chips**: `rgba(246,247,254,0.1)` semi-transparent fill, white text

### Cards & Containers
- Borders: `0.75px solid rgba(246,247,254,0.5)`
- No border-radius — sharp corners always
- Internal padding: 40px

### Typography in Decks
- Everything is TT Hoves — Regular for body/headings and supporting text, Medium for emphasis
- No DM Mono, DM Sans, Space Grotesk, or any other typeface

### Layout Patterns

**Card grid** — the most common layout. Equal-width cards side by side (2, 3, or 4 columns), each with: small label chip top-left, title, supporting text, optional illustration or stat at bottom. Cards use `0.75px border rgba(246,247,254,0.5)`.

**Numbered row groups** — content grouped into rows (01/02/03), each row separated by a thin `rgba(246,247,254,0.6)` horizontal line. Large muted number (48px, 50% opacity) anchors left, cards or tiles fill the right.

**Split layout** — left column has title + body text, right area has the primary content (cards, diagrams, charts). Common ratio is roughly 40/60 or 30/70.

**Stat + diagram** — large percentage or number (60px) on the left with a category label, dashed connector line leading to a diagram or chart filling the right side.

**Timeline / Gantt** — horizontal phase bars on a vertical dashed-line grid. Blue bars = primary/active phases, white = completed, grey = future/secondary. Labels above bars.

**Blue full-bleed content block** — blue (`#2237F1`) fills a large content area (not the whole slide) for process diagrams or featured visuals. White TT Hoves text sits on top.

### Illustration Style
Midwestern uses a **line art / technical drawing** style — thin white strokes, minimal fill, geometric shapes. Precise, clean, organized. Used as the lower-half visual in cards and as full diagram slides. No gradients, no 3D renders, no drop shadows.

---

## How to Apply This Skill

**For HTML/CSS components**: Reference the color tokens above. Default to light mode (white background, black text). Use blue for interactive/accent elements. Use green only for the rarest highlights.

**For dark mode**: Swap `--background` to `#010313` and `--foreground` to `#F6F7FE`. Keep blue and green accent usage the same.

**For data viz / charts**: Use white background, black for primary data, blue for the highlighted/key series, green only for the single most important callout value.

**For typography**: Always TT Hoves. Sentence case only. Use Display/Heading styles for titles (LH 1.2), Body styles for paragraphs (LH 1.5). Color overlines, CTAs, and links in blue (`#2237F1`). Never use headings in all-caps or title case.

**For border radius**: Always 0. No rounded corners on anything.

**For spacing**: Only use values from the spacing scale. Reference tokens (`--5` through `--14`) rather than hardcoding px values. Page padding = `--12`/`--14`. Component padding = `--9`/`--10`. Tight gaps = `--5`/`--6`.
