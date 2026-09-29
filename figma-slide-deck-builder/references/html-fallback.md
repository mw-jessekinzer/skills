# HTML Fallback: Building slide decks without Figma MCP

Use this workflow when the Figma MCP is not connected. The output is a single-file HTML presentation styled to the Midwestern Design System, with two view modes and PDF export via browser print.

## Build workflow

Before writing any HTML, follow this sequence:

1. **Study the source content** — Read any uploaded documents, text, or briefs the user provides.
2. **Produce an outline** — Map every slide to a layout from `slide-library-catalog.md`. For each slide, specify: the layout name, rough content summary, and any visual elements (images, charts, icons). Present the outline to the user.
3. **Wait for approval** — Do not start building until the user confirms the outline.
4. **Build slide-by-slide** — Write one slide's HTML at a time inside the deck wrapper. Fully populate each slide before writing the next. This makes it easier for the user to review progress and request changes per slide.

---

## Table of contents

1. [CSS Foundation](#1-css-foundation)
2. [HTML Shell](#2-html-shell)
3. [View Modes & Navigation](#3-view-modes--navigation)
4. [PDF Export](#4-pdf-export)
5. [Deck Crawler Footer](#5-deck-crawler-footer)
6. [Brand Assets](#6-brand-assets)
7. [Icons](#7-icons)
8. [Reusable Patterns](#8-reusable-patterns)
9. [Layout Templates](#9-layout-templates)
10. [Data Visualization](#10-data-visualization)
11. [HTML-Specific Gotchas](#11-html-specific-gotchas)

---

## 1. CSS Foundation

Every HTML deck starts with these custom properties. They mirror the MW Design System tokens exactly.

```css
:root {
  /* Colors — Primitives */
  --bg: #010313;
  --fg: #F6F7FE;
  --blue: #2237F1;
  --green: #C7FA50;
  --dark-gray: #333333;
  --med-gray: #666666;
  --muted: #949494;
  --more-muted: #A9A9A9;
  --disabled: #666;

  /* Typography */
  --font: 'DM Sans', sans-serif;

  /* Spacing (8pt grid) */
  --pad: 56px;
}
```

### Base slide styles

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

.slide {
  width: 1920px;
  height: 1080px;
  background: var(--bg);
  color: var(--fg);
  font-family: var(--font);
  font-weight: 400;
  position: relative;
  overflow: hidden;
  padding: var(--pad);
}

.slide * { border-radius: 0; } /* Sharp corners always */
```

### Slide grid

All slides align to a 12-column / 6-row grid. This is the canonical spatial system from the Figma Slide Library — every layout is built on it.

- **12 columns**, 32px gutters, 56px offset (margin), stretch
- **6 rows**, 0px gutters, 56px offset (margin), stretch
- Content area: **1808px wide** (1920 - 56×2)
- Row height: **~161px** each (1080 - 56×2 = 968px / 6)

Common column spans and their widths (approximate):
- 4 columns = **~580px** (card width in 3-col layouts)
- 6 columns = **~888px** (half-width content areas)
- 12 columns = **~1808px** (full-width)

When building layouts in CSS, use this as the underlying spatial reference. The 56px padding, 32px gaps, and column math should be consistent across every slide.

```css
/* Optional: apply as CSS grid when a slide needs column-based layout */
.slide-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  column-gap: 32px;
  row-gap: 0;
  padding: 56px;
  width: 1920px;
  height: 1080px;
}
```

### Typography rules

- **Sentence case always.** Never title case except proper nouns.
- **Font weight 400 (Regular) for almost everything.** The MW system uses size hierarchy, not boldness. Use 500 sparingly for labels. Use 700 only for extreme emphasis on a single word.
- **Line heights:** Display = 1.0–1.1, Heading = 1.2, Body = 1.5.
- **Letter spacing:** -2px for display (128px), -1px for heading sizes (48-96px), 0 for body.

### Type scale (from Figma DS)

| Name | Size | Line height | Letter spacing |
|---|---|---|---|
| Display XL | 128px | 1.1 | -2px |
| Display Large | 96px | 1.1 | -1px |
| Display Medium | 72px | 1.2 | -1px |
| Heading XL | 72px | 1.2 | -1px |
| Heading Large | 60px | 1.2 | -1px |
| Heading Medium | 48px | 1.2 | -1px |
| Heading Small | 36px | 1.2 | 0 |
| Heading XS | 24px | 1.2 | 0 |
| Heading XXS | 20px | 1.2 | 0 |
| Body XL | 24px | 1.5 | 0 |
| Body Large | 20px | 1.5 | 0 |
| Body Medium | 16px | 1.5 | 0 |
| Body Small | 14px | 1.5 | 0 |
| Caption | 12px | 1.4 | 0 |

---

## 2. HTML Shell

The complete outer structure. Every deck uses this wrapper.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{DECK_TITLE}}</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/light/style.css" />
  <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css" />
  <style>
    /* Paste CSS Foundation here */
    /* Paste View Mode styles here */
    /* Paste Layout-specific styles here */
    /* Paste Print styles here */
  </style>
</head>
<body>
  <div class="deck-controls">
    <button id="mode-toggle" onclick="toggleMode()">Presentation mode</button>
    <button onclick="window.print()">Save as PDF</button>
  </div>
  <div class="deck scroll-mode" id="deck">
    <!-- Slides go here -->
  </div>
  <div class="slide-nav" id="slide-nav">
    <button onclick="prevSlide()">←</button>
    <span id="slide-counter">1 / N</span>
    <button onclick="nextSlide()">→</button>
  </div>
  <script>/* Paste View Mode JS here */</script>
</body>
</html>
```

---

## 3. View Modes & Navigation

Two modes: **scroll** (default) and **presentation** (one slide at a time).

### CSS

```css
/* Controls */
.deck-controls { position: fixed; top: 16px; right: 16px; z-index: 1000; display: flex; gap: 8px; }
.deck-controls button { background: var(--bg); color: var(--fg); border: 1px solid var(--more-muted); padding: 8px 16px; font-family: var(--font); font-size: 14px; cursor: pointer; }
.deck-controls button:hover { border-color: var(--fg); }

.slide-nav { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%); z-index: 1000; display: none; align-items: center; gap: 16px; background: rgba(1,3,19,0.85); padding: 8px 20px; border: 1px solid var(--more-muted); }
.slide-nav button { background: none; border: none; color: var(--fg); font-size: 24px; cursor: pointer; }
.slide-nav span { color: var(--muted); font-family: var(--font); font-size: 14px; }

/* Scroll mode (default) */
.deck.scroll-mode { display: flex; flex-direction: column; align-items: center; gap: 40px; padding: 40px 0; }
.deck.scroll-mode .slide { flex-shrink: 0; box-shadow: 0 4px 24px rgba(0,0,0,0.5); }

/* Presentation mode — uses opacity, not display, because inline styles on slides would fight display:none */
.deck.presentation-mode { width: 100vw; height: 100vh; overflow: hidden; position: relative; background: var(--bg); }
.deck.presentation-mode .slide {
  position: absolute !important; top: 50%; left: 50%;
  transform: translate(-50%, -50%) scale(var(--pres-scale, 1)) !important;
  transform-origin: center center !important;
  margin-bottom: 0 !important;
  opacity: 0; pointer-events: none; transition: opacity 0.15s ease;
}
.deck.presentation-mode .slide.active { opacity: 1; pointer-events: auto; }
```

### JavaScript

```javascript
let currentSlide = 0, mode = 'scroll';
const deck = document.getElementById('deck');
const slides = () => deck.querySelectorAll('.slide');
const nav = document.getElementById('slide-nav');
const counter = document.getElementById('slide-counter');

function toggleMode() {
  const s = slides();
  if (mode === 'scroll') {
    mode = 'presentation';
    // Clear scroll-mode inline styles so CSS !important takes over
    s.forEach(sl => { sl.style.transform = ''; sl.style.transformOrigin = ''; sl.style.marginBottom = ''; });
    deck.className = 'deck presentation-mode';
    nav.style.display = 'flex';
    showSlide(currentSlide);
    scalePres();
    document.getElementById('mode-toggle').textContent = 'Scroll mode';
  } else {
    mode = 'scroll';
    s.forEach(sl => sl.classList.remove('active'));
    deck.className = 'deck scroll-mode';
    nav.style.display = 'none';
    scaleScroll();
    document.getElementById('mode-toggle').textContent = 'Presentation mode';
  }
}

function showSlide(i) {
  const s = slides();
  if (i < 0 || i >= s.length) return;
  s.forEach(sl => sl.classList.remove('active'));
  s[i].classList.add('active');
  currentSlide = i;
  counter.textContent = (i+1) + ' / ' + s.length;
}

function prevSlide() { showSlide(currentSlide-1); }
function nextSlide() { showSlide(currentSlide+1); }

document.addEventListener('keydown', e => {
  if (mode !== 'presentation') return;
  if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); nextSlide(); }
  if (e.key === 'ArrowLeft') { e.preventDefault(); prevSlide(); }
  if (e.key === 'Escape') toggleMode();
});

function scalePres() {
  document.documentElement.style.setProperty('--pres-scale', Math.min(innerWidth/1920, innerHeight/1080));
}

function scaleScroll() {
  const s = slides(), scale = Math.min(1920, innerWidth*0.9)/1920;
  s.forEach(sl => {
    sl.style.transform = 'scale('+scale+')';
    sl.style.transformOrigin = 'top center';
    sl.style.marginBottom = -(1080*(1-scale))+'px';
  });
}

addEventListener('resize', () => mode === 'presentation' ? scalePres() : scaleScroll());
addEventListener('load', scaleScroll);
```

**Why opacity instead of display?** Most slides have inline `display:flex` for layout. CSS `display:none` can't override inline styles without `!important`, which would break layout. Opacity doesn't conflict.

---

## 4. PDF Export

**Use browser print, not JavaScript PDF libraries.** CDN-dependent libraries (html2pdf.js, jsPDF) are blocked in the Claude artifact sandbox and unreliable across environments. Browser print with `@media print` is zero-dependency and produces better output.

The "Save as PDF" button calls `window.print()`. Tell the user:
- In Chrome's print dialog: select **"Save as PDF"** as destination
- Under **More Settings**, check **"Background graphics"**
- Scale should auto-detect from `@page` size

### Print CSS

```css
@media print {
  @page { size: 1920px 1080px landscape; margin: 0; }
  html, body {
    width: 1920px; margin: 0; padding: 0;
    background: #010313;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .deck-controls, .slide-nav { display: none !important; }
  .deck { display: block !important; padding: 0 !important; }
  .slide {
    width: 1920px !important; height: 1080px !important;
    transform: none !important; margin: 0 !important;
    box-shadow: none !important; opacity: 1 !important;
    display: block !important; background: #010313 !important;
    page-break-after: always; break-after: page;
    page-break-inside: avoid;
  }
  .slide:last-child { page-break-after: auto; }
  /* Force colors — browsers strip backgrounds by default */
  .cover-graphic { background: #2237F1 !important; }
  .dc { border-top-color: #666 !important; }
}
```

---

## 5. Deck Crawler Footer

Every slide has this footer. Structure matches Figma exactly: page number + presentation title on left, section title in muted, MW mark on right. Border color is `#666` (the `--disabled` token), not `#A9A9A9`.

### CSS

```css
.dc {
  position: absolute; bottom: 0; left: var(--pad); width: 1808px;
  height: 56px; border-top: 1px solid var(--disabled);
  display: flex; align-items: center; justify-content: space-between;
}
.dc-left { display: flex; gap: 20px; align-items: center; font-size: 16px; line-height: 1.5; }
.dc-left span { white-space: nowrap; }
.dc-left .dc-muted { color: var(--muted); }
.dc-mark { color: var(--fg); }
```

### HTML

```html
<div class="dc">
  <div class="dc-left">
    <span>{{PAGE_NUMBER}}</span>
    <span>{{PRESENTATION_TITLE}}</span>
    <span class="dc-muted">{{SECTION_TITLE}}</span>
  </div>
  <div class="dc-mark"><span class="mw-mark"></span></div>
</div>
```

---

## 6. Brand Assets

### MW Mark (M icon — used in footer and standalone)

The real MW mark as a filled SVG data URI. Use everywhere you need the M icon.

```css
.mw-mark {
  display: inline-block;
  width: 25px;
  height: 13px;
  image-rendering: pixelated;
  flex-shrink: 0;
  background-size: 100% 100%;
  background-image: url("data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 25 13%22><path d=%22M 19.466 0.012 L 9.95 9.214 L 9.95 13 L 13.861 13 L 19.466 7.579 L 19.466 13 L 25 13 L 25 1.52 L 23.441 0.012 Z%22 fill=%22rgb(246,247,254)%22></path><path d=%22M 14.259 0 L 9.512 0 L 0 9.199 L 0 12.985 L 3.911 12.985 L 15.833 1.52 Z%22 fill=%22rgb(246,247,254)%22></path></svg>");
}
```

Usage: `<span class="mw-mark"></span>`

### MW Wordmark (full logo: M + "midwestern" text)

The complete wordmark as a single SVG data URI. Vector paths — no font dependency.

```css
.mw-wordmark {
  display: inline-block;
  width: 276px;
  height: 44px;
  flex-shrink: 0;
  background-size: 100% 100%;
  background-repeat: no-repeat;
  background-image: url("data:image/svg+xml,%3Csvg width='276' height='44' viewBox='0 0 276 44' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M80.5312 5.02051V42.9502H62.7051V25.041L44.6484 42.9502H32.0508V30.4424L62.7051 0.0380859H75.5078L80.5312 5.02051ZM185.71 23.6348C190.813 23.6348 194.811 27.6455 194.811 32.9326C194.811 33.481 194.743 33.9185 194.7 34.2441L194.631 34.7578H180.787C181.189 37.3456 183.116 39.1366 185.701 39.1367C187.85 39.1367 189.16 37.8945 189.528 37.1318H194.263L194.271 37.1143C193.869 38.571 191.575 42.9502 185.71 42.9502C180.248 42.9501 176.241 38.9398 176.241 33.293C176.241 27.6459 180.248 23.6348 185.71 23.6348ZM233.963 23.6348C239.066 23.6348 243.063 27.6455 243.063 32.9326C243.063 33.481 242.996 33.9185 242.953 34.2441L242.884 34.7578H229.04C229.442 37.3456 231.369 39.1366 233.954 39.1367C236.103 39.1367 237.413 37.8945 237.781 37.1318H242.516L242.524 37.1143C242.122 38.571 239.828 42.9502 233.963 42.9502C228.501 42.9501 224.494 38.9398 224.494 33.293C224.494 27.6459 228.501 23.6348 233.963 23.6348ZM146.755 42.582H142.748L142.38 40.5762H142.2C141.832 41.0475 141.396 41.4507 140.891 41.7764C140.017 42.359 138.63 42.9413 136.738 42.9414C132.004 42.9414 128.177 39.1111 128.177 33.2842C128.177 27.4572 132.004 23.627 136.738 23.627C138.596 23.627 139.872 24.2435 140.745 24.8262C141.25 25.1517 141.695 25.5543 142.021 25.9912H142.2V17.0625H146.755V42.582ZM203.741 23.627C209.169 23.6272 211.574 27.4575 211.574 29.6426H207.199C207.199 28.5115 205.924 27.2775 203.741 27.2773C201.558 27.2773 200.462 28.3309 200.462 29.4619C200.462 30.3359 201.301 30.9187 203.013 31.1758L206.112 31.6475C209.939 32.2301 211.942 33.978 211.942 37.2939C211.942 40.3531 209.357 42.9414 203.929 42.9414C197.011 42.9412 195.915 38.2026 195.915 36.9258H200.282V36.9346C200.282 37.8429 201.412 39.2998 203.921 39.2998C206.429 39.2997 207.379 38.425 207.379 37.2939C207.379 36.1631 206.865 35.5463 204.828 35.2207L201.917 34.749C198.09 34.132 195.907 32.5639 195.907 29.4619C195.907 26.36 198.639 23.627 203.741 23.627ZM51.0029 5.02051L12.5977 42.8994H0V30.3916L30.6416 0H45.9326L51.0029 5.02051ZM125.813 42.5898H121.259V23.9951H125.813V42.5898ZM155.855 36.2061H156.584L159.683 23.9951H164.785L167.885 36.2061H168.612L171.712 23.9951H176.446L171.712 42.5898H165.702L162.603 30.5586H161.875L158.775 42.5898H152.766L148.03 23.9951H152.757L155.855 36.2061ZM219.399 23.9951H223.586V28.374H219.399V37.3027C219.399 38.1425 219.837 38.5801 220.676 38.5801H223.586V42.5898H219.58C216.481 42.5898 214.845 40.9873 214.845 38.2109V28.3652H211.935V23.9863H214.845V18.708H219.399V23.9951ZM267.841 23.627C272.027 23.627 275.127 26.729 275.127 31.4678V42.5898H270.572V31.8359C270.572 29.4709 268.928 27.8252 266.565 27.8252C264.202 27.8252 262.559 29.4709 262.559 31.8359V42.5898H258.004V23.9951H262.19L262.559 25.8203H262.738C263.064 25.4177 263.5 25.0578 263.979 24.7236C264.818 24.1752 266.094 23.627 267.841 23.627ZM111.241 23.627C115.068 23.627 118.159 26.9085 118.159 31.0986V42.582H113.604V31.459C113.604 29.0939 112.363 27.8174 110.505 27.8174C108.467 27.8176 107.047 29.4197 107.047 31.459V42.582H102.492V31.459C102.492 29.0939 101.25 27.8174 99.3926 27.8174C97.3549 27.8174 95.9336 29.4195 95.9336 31.459V42.582H91.3955V23.9951H95.583L95.9512 25.8203H96.1309C96.4219 25.4176 96.79 25.0578 97.2266 24.7236C97.9543 24.1752 99.0504 23.627 100.506 23.627C102.363 23.627 103.562 24.2864 104.401 24.9033C104.872 25.306 105.274 25.7094 105.6 26.1807H105.779C106.139 25.7094 106.584 25.306 107.089 24.9033C107.962 24.2864 109.307 23.6271 111.241 23.627ZM256.72 28.3652H253.44C251.146 28.3653 249.981 29.5308 249.981 31.8271V42.582H245.427V23.9951H249.263L249.622 25.6318H249.802C250.016 25.3405 250.273 25.0832 250.606 24.8262C251.154 24.4234 251.951 23.9863 253.081 23.9863H256.72V28.3652ZM137.466 27.8252C134.7 27.8252 132.731 29.7968 132.731 33.293C132.732 36.789 134.701 38.7598 137.466 38.7598C140.231 38.7597 142.2 36.7889 142.2 33.293C142.2 29.7968 140.231 27.8252 137.466 27.8252ZM185.71 27.457C182.945 27.4571 181.335 29.2824 180.796 31.6475H190.265C189.862 29.2824 188.296 27.457 185.71 27.457ZM233.963 27.457C231.198 27.4571 229.588 29.2824 229.049 31.6475H238.518C238.115 29.2824 236.548 27.457 233.963 27.457ZM125.993 21.0732H121.079V16.7031H125.993V21.0732Z' fill='%23F6F7FE'/%3E%3C/svg%3E");
}
```

Usage: `<div class="mw-wordmark"></div>`

Scale with inline styles when needed (e.g., title slide uses 172×27):
`<div class="mw-wordmark" style="width:172px; height:27px;"></div>`

---

## 7. Icons

Use **Phosphor Icons** (already in the MW design system) via CDN. Two weights:

- **Phosphor Light** (`ph-light`) — thin stroke, matches MW decorative line-art language. Use for decorative/illustration icons.
- **Phosphor Regular** (`ph`) — standard weight. Use for functional/UI icons and social icons.

### CDN links (add to `<head>`)

```html
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/light/style.css" />
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css" />
```

### Usage

```html
<!-- Decorative (light) -->
<i class="ph-light ph-arrow-up-right" style="font-size:56px;"></i>

<!-- Social icons (regular) -->
<i class="ph ph-linkedin-logo" style="font-size:28px;"></i>
<i class="ph ph-instagram-logo" style="font-size:28px;"></i>
<i class="ph ph-dribbble-logo" style="font-size:28px;"></i>
```

Reference: https://phosphoricons.com/

**Important:** Phosphor icons will NOT render in the Claude artifact preview because CDN requests are sandboxed. They render correctly when the user downloads and opens the HTML file in a real browser. The MW mark and wordmark are inline data URIs, so they always render.

---

## 8. Reusable Patterns

### Title Block

Many slides share a title section at top-left: a muted label (20px) above a heading (60px). Position with absolute at top/left padding.

```css
.slide-title-block {
  position: absolute; top: var(--pad); left: var(--pad);
  width: 1808px; display: flex; flex-direction: column; gap: 4px;
}
.slide-title-block .label { font-size: 20px; line-height: 1.5; color: var(--muted); }
.slide-title-block .heading { font-size: 60px; line-height: 1.2; letter-spacing: -1px; }
```

```html
<div class="slide-title-block">
  <div class="label">{{LABEL}}</div>
  <div class="heading">{{HEADING}}</div>
</div>
```

### Cover Graphic

The decorative graphic on title slides. Blue background, thin white stroke SVG art, white border.

```css
.cover-graphic {
  position: absolute; top: var(--pad); left: var(--pad);
  width: 1808px; height: 484px;
  border: 1px solid var(--fg); overflow: hidden;
  background: var(--blue);
}
```

The default variant is overlapping circles:

```html
<div class="cover-graphic">
  <svg width="100%" height="100%" viewBox="0 0 1808 484" fill="none">
    <circle cx="300" cy="242" r="220" stroke="#F6F7FE" stroke-width="1.5" opacity="0.6"/>
    <circle cx="600" cy="242" r="220" stroke="#F6F7FE" stroke-width="1.5" opacity="0.6"/>
    <circle cx="900" cy="242" r="220" stroke="#F6F7FE" stroke-width="1.5" opacity="0.6"/>
    <circle cx="1200" cy="242" r="220" stroke="#F6F7FE" stroke-width="1.5" opacity="0.6"/>
    <circle cx="1500" cy="242" r="220" stroke="#F6F7FE" stroke-width="1.5" opacity="0.6"/>
    <line x1="0" y1="242" x2="1808" y2="242" stroke="#F6F7FE" stroke-width="1" stroke-dasharray="8 6" opacity="0.5"/>
    <line x1="904" y1="0" x2="904" y2="484" stroke="#F6F7FE" stroke-width="1" stroke-dasharray="8 6" opacity="0.5"/>
  </svg>
</div>
```

For other Cover Graphic variants (Circle Dots, Diamonds, Squares, Logo), generate geometric SVGs following the same rules: stroke-only, no fills, `stroke-width: 1.5`, `opacity: 0.2–0.6`.

### Social Icons Row (for End Slide)

```html
<div style="display:flex; gap:24px; align-items:center;">
  <a href="https://www.midwestern.com/" target="_blank" style="display:flex; align-items:center; justify-content:center; width:48px; height:48px; color:var(--fg); text-decoration:none;">
    <span class="mw-mark" style="width:36px; height:19px;"></span>
  </a>
  <a href="https://www.linkedin.com/company/buildmidwestern/" target="_blank" style="display:flex; align-items:center; justify-content:center; width:48px; height:48px; color:var(--fg); text-decoration:none;">
    <i class="ph ph-linkedin-logo" style="font-size:28px;"></i>
  </a>
  <a href="https://www.instagram.com/buildmidwestern/" target="_blank" style="display:flex; align-items:center; justify-content:center; width:48px; height:48px; color:var(--fg); text-decoration:none;">
    <i class="ph ph-instagram-logo" style="font-size:28px;"></i>
  </a>
  <a href="https://dribbble.com/BuildMidwestern" target="_blank" style="display:flex; align-items:center; justify-content:center; width:48px; height:48px; color:var(--fg); text-decoration:none;">
    <i class="ph ph-dribbble-logo" style="font-size:28px;"></i>
  </a>
</div>
```

---

## 9. Layout Templates

All layouts from the Slide Library, adapted to HTML/CSS. These have been verified against the real Figma design context.

### Title Page / Wide Pane

Cover Graphic pane at top, headline + wordmark at bottom. Headline is Display XL (128px).

```html
<div class="slide">
  <div class="cover-graphic"><!-- SVG variant here --></div>
  <div style="position:absolute; bottom:80px; left:56px; display:flex; flex-direction:column; gap:16px;">
    <div class="mw-wordmark" style="width:172px; height:27px;"></div>
    <div style="font-size:128px; line-height:1.1; max-width:1200px; letter-spacing:-2px;">{{DECK_TITLE}}</div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Entry Page

MW wordmark top-left, large statement text (72px) vertically centered, arrow icon bottom-left. The arrow should use Phosphor Light.

```html
<div class="slide">
  <div style="position:absolute; top:56px; left:56px;">
    <div class="mw-wordmark"></div>
  </div>
  <div style="position:absolute; top:calc(50% - 172px); left:56px; width:1808px; font-size:72px; line-height:1.2; letter-spacing:-1px;">
    {{STATEMENT_TEXT}}
  </div>
  <div style="position:absolute; left:56px; top:904px; width:64px; height:64px; color:var(--fg); display:flex; align-items:center; justify-content:center;">
    <i class="ph-light ph-arrow-up-right" style="font-size:56px;"></i>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Clean + Simple

Title block at top, centered rows with label + value. Labels are 428px wide at 36px muted, values are flex at 48px. Rows have 64px gap, 307px horizontal inset, 16px vertical padding.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:360px; left:56px; width:1808px; display:flex; flex-direction:column; gap:64px;">
    <div style="display:flex; gap:32px; align-items:baseline; padding:16px 307px;">
      <div style="width:428px; flex-shrink:0; font-size:36px; line-height:1.2; color:var(--more-muted);">{{LABEL}}</div>
      <div style="flex:1; font-size:48px; line-height:1.2; letter-spacing:-1px;">{{VALUE}}</div>
    </div>
    <!-- Repeat for each row -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### 2 Column

Title block at top. Two bordered cards (750px tall) side by side. Each card has: tag (20px with muted background), heading (36px), description (24px) at top, and a large stat number (224px) with arrow icon at bottom.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:218px; left:50%; transform:translateX(-50%); width:1808px; height:750px; display:flex; gap:32px;">
    <div style="flex:1; border:1px solid var(--more-muted); padding:40px 40px 0; display:flex; flex-direction:column; justify-content:space-between; overflow:hidden;">
      <div style="display:flex; flex-direction:column; gap:16px; max-width:480px;">
        <div style="display:inline-block; padding:2px 8px; background:rgba(169,169,169,0.24); font-size:20px; line-height:1.5; width:fit-content;">{{TAG}}</div>
        <div style="font-size:36px; line-height:1.2;">{{CARD_HEADING}}</div>
        <div style="font-size:24px; line-height:1.2;">{{CARD_DESCRIPTION}}</div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:flex-end;">
        <div style="font-size:224px; line-height:1.2; letter-spacing:-10px;">{{BIG_NUMBER}}</div>
        <div style="padding-bottom:48px;"><i class="ph-light ph-arrow-up-right" style="font-size:56px;"></i></div>
      </div>
    </div>
    <!-- Repeat for second card -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Content + Bullets

Title block at top (888px wide), then a heading+paragraph section (40px heading + 24px body, 1041px wide), then a 4-column key-value grid (each 428px, heading 40px + description 24px), and a closing statement (40px) with arrow icon anchored at bottom (y=863).

```html
<div class="slide">
  <div style="position:absolute; top:50px; left:56px; width:1808px; display:flex; flex-direction:column; gap:64px;">
    <!-- Title -->
    <div style="display:flex; flex-direction:column; gap:4px; width:888px;">
      <div style="font-size:20px; line-height:1.5; color:var(--muted);">{{SUBTITLE}}</div>
      <div style="font-size:60px; line-height:1.2; letter-spacing:-1px;">{{HEADING}}</div>
    </div>
    <!-- Body section -->
    <div style="width:1041px; display:flex; flex-direction:column; gap:24px; padding-bottom:40px;">
      <div style="font-size:40px; line-height:1.2;">{{SECTION_HEADING}}</div>
      <div style="font-size:24px; line-height:1.5;">{{BODY_TEXT}}</div>
    </div>
    <!-- 4-column key-value grid -->
    <div style="display:flex; gap:32px; width:100%;">
      <div style="width:428px; display:flex; flex-direction:column; gap:24px;">
        <div style="font-size:40px; line-height:1.2;">{{KEY_1}}</div>
        <div style="font-size:24px; line-height:1.5; max-width:400px;">{{VALUE_1}}</div>
      </div>
      <!-- Repeat for keys 2, 3, 4 -->
    </div>
  </div>
  <!-- Closing statement at bottom -->
  <div style="position:absolute; top:863px; left:56px; width:1808px; display:flex; justify-content:space-between; align-items:flex-end;">
    <div style="font-size:40px; line-height:1.2; width:1041px;">{{CLOSING_STATEMENT}}</div>
    <div style="width:64px; height:64px; display:flex; align-items:center; justify-content:center;">
      <i class="ph-light ph-arrow-up-right" style="font-size:56px;"></i>
    </div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Quote

MW mark centered above, italic quote text (72px) centered, attribution below (name 36px + title 24px). Quote is 1299px wide max.

```html
<div class="slide" style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:0; text-align:center;">
  <!-- MW Mark above quote -->
  <div style="margin-bottom:40px;">
    <span class="mw-mark" style="width:71px; height:38px;"></span>
  </div>
  <!-- Quote text — italic -->
  <div style="font-size:72px; line-height:1.2; letter-spacing:-1px; font-style:italic; max-width:1299px; margin-bottom:48px;">
    "{{QUOTE_TEXT}}"
  </div>
  <!-- Attribution -->
  <div style="text-align:center;">
    <div style="font-size:36px; line-height:1.2;">{{PERSON_NAME}}</div>
    <div style="font-size:24px; line-height:1.5;">{{PERSON_TITLE}}</div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Table of Contents

Heading (60px) at top-left. Right side starts at left=823px, width=1041px. Each row is 110px tall, 32px gap between rows. Row structure: number column (121px, border-top, 48px number), section name column (428px, border-top, 48px), sub-items column (flex, muted 20px with page numbers right-aligned).

```html
<div class="slide">
  <!-- Heading top-left -->
  <div style="position:absolute; top:50px; left:56px; font-size:60px; line-height:1.2; letter-spacing:-1px;">{{TOC_TITLE}}</div>
  <!-- TOC rows -->
  <div style="position:absolute; top:56px; left:823px; width:1041px; display:flex; flex-direction:column; gap:32px;">
    <!-- Row -->
    <div style="display:flex; justify-content:space-between; height:110px; padding-bottom:4px;">
      <div style="width:121px; border-top:1px solid var(--fg); padding-top:8px; font-size:48px; line-height:1.2; letter-spacing:-1px; font-feature-settings:'lnum' 1,'tnum' 1;">01</div>
      <div style="width:888px; border-top:1px solid var(--fg); padding-top:8px; display:flex; gap:128px;">
        <div style="width:428px; font-size:48px; line-height:1.2; letter-spacing:-1px;">{{SECTION_NAME}}</div>
        <div style="flex:1; display:flex; flex-direction:column; gap:4px; font-size:20px; line-height:1.5; color:var(--muted);">
          <div style="display:flex; justify-content:space-between;"><span>{{SUB_ITEM}}</span><span style="font-feature-settings:'lnum' 1,'tnum' 1;">{{PAGE}}</span></div>
          <!-- Repeat sub-items -->
        </div>
      </div>
    </div>
    <!-- Repeat rows -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Section Title

Large heading (96px) at top, sub-items (20px muted, 332px wide) anchored at bottom-left with page numbers. Container is 918px tall, justify-content:space-between.

```html
<div class="slide">
  <div style="position:absolute; top:50px; left:56px; width:1808px; height:918px; display:flex; flex-direction:column; justify-content:space-between;">
    <div style="font-size:96px; line-height:1.2;">{{SECTION_NAME}}</div>
    <div style="width:332px; display:flex; flex-direction:column; gap:4px; font-size:20px; line-height:1.5; color:var(--muted);">
      <div style="display:flex; justify-content:space-between;"><span>{{ITEM}}</span><span style="font-feature-settings:'lnum' 1,'tnum' 1;">{{PAGE}}</span></div>
      <!-- Repeat items -->
    </div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### List

Title block at top. Numbered items in vertical stack. Each item: number column (121px, 48px font, border-top), heading + description column (flex, border-top, heading 48px, description 20px muted). Similar structure to TOC rows but full-width.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:218px; left:56px; width:1808px; display:flex; flex-direction:column; gap:24px;">
    <div style="display:flex; gap:32px; border-top:1px solid var(--fg); padding-top:16px;">
      <div style="width:121px; font-size:48px; line-height:1.2; letter-spacing:-1px; color:var(--muted); font-feature-settings:'lnum' 1,'tnum' 1;">01</div>
      <div style="flex:1; display:flex; flex-direction:column; gap:8px;">
        <div style="font-size:48px; line-height:1.2; letter-spacing:-1px;">{{ITEM_HEADING}}</div>
        <div style="font-size:20px; line-height:1.5; color:var(--muted); max-width:800px;">{{ITEM_DESCRIPTION}}</div>
      </div>
    </div>
    <!-- Repeat items -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Graph

Title (60px) + description (24px) at top-left, 735px wide. Chart area below at y=539 (888px wide). SVG chart with green (#C7FA50) growth curve, filled area underneath, and axis labels (12px). Right side at left=1129: heading (36px) + list of callout items with arrow icons (24px).

```html
<div class="slide">
  <!-- Title + description top-left -->
  <div style="position:absolute; top:56px; left:56px; width:735px; display:flex; flex-direction:column; gap:16px;">
    <div style="font-size:60px; line-height:1.2; letter-spacing:-1px;">{{HEADING}}</div>
    <div style="font-size:24px; line-height:1.5;">{{DESCRIPTION}}</div>
  </div>
  <!-- Chart -->
  <div style="position:absolute; top:539px; left:56px; display:flex; flex-direction:column; gap:24px;">
    <div style="font-size:24px; line-height:1.5;">{{CHART_LABEL}}</div>
    <svg width="888" height="347" viewBox="0 0 888 347" fill="none">
      <!-- Grid lines -->
      <line x1="0" y1="82" x2="888" y2="82" stroke="#F6F7FE" stroke-width="1" opacity="0.08"/>
      <line x1="0" y1="164" x2="888" y2="164" stroke="#F6F7FE" stroke-width="1" opacity="0.08"/>
      <line x1="0" y1="246" x2="888" y2="246" stroke="#F6F7FE" stroke-width="1" opacity="0.08"/>
      <!-- Filled area -->
      <path d="M0 316 C60 300 170 20 254 0 C380 5 700 90 888 129 L888 328 L0 328Z" fill="#C7FA50" opacity="0.15"/>
      <!-- Stroke curve -->
      <path d="M0 316 C60 300 170 20 254 0 C380 5 700 90 888 129" stroke="#C7FA50" stroke-width="3" fill="none"/>
      <!-- Axis labels -->
      <text x="0" y="345" fill="#949494" font-family="DM Sans" font-size="12">{{X_START}}</text>
      <text x="444" y="345" fill="#949494" font-family="DM Sans" font-size="12" text-anchor="middle">{{X_MID}}</text>
      <text x="888" y="345" fill="#949494" font-family="DM Sans" font-size="12" text-anchor="end">{{X_END}}</text>
    </svg>
  </div>
  <!-- Right side callouts -->
  <div style="position:absolute; top:600px; left:1129px; width:275px; display:flex; flex-direction:column; gap:24px;">
    <div style="font-size:36px; line-height:1.2;">{{CALLOUT_HEADING}}</div>
    <div style="display:flex; align-items:center; gap:12px; font-size:24px; line-height:1.5;">
      <i class="ph-light ph-arrow-right" style="font-size:20px;"></i> {{CALLOUT_ITEM}}
    </div>
    <!-- Repeat callout items -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Leaps

Title block at top. SVG arc timeline below (1808px × 484px) with stepping dashed arcs getting progressively taller left-to-right. Green dot on first node, white dots on subsequent nodes. Horizontal baseline with arrow at end. Below the arcs: 4-column grid of heading (36px) + description (20px muted, 400px max).

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:217px; left:56px; width:1808px; display:flex; flex-direction:column; gap:40px;">
    <!-- Arc timeline SVG -->
    <svg width="1808" height="484" viewBox="0 0 1808 484" fill="none">
      <!-- Stepped arcs (dashed, progressively taller) -->
      <path d="M9 484 Q 235 320 457 484" stroke="#F6F7FE" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.5" fill="none"/>
      <path d="M9 484 Q 460 167 905 484" stroke="#F6F7FE" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.5" fill="none"/>
      <path d="M9 484 Q 680 9 1353 484" stroke="#F6F7FE" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.5" fill="none"/>
      <!-- Baseline -->
      <line x1="17" y1="484" x2="1790" y2="484" stroke="#F6F7FE" stroke-width="1"/>
      <!-- Arrow at end -->
      <path d="M1770 475 L1790 484 L1770 493" stroke="#F6F7FE" stroke-width="1.5" fill="none"/>
      <!-- Dots -->
      <circle cx="9" cy="484" r="8" fill="none" stroke="#C7FA50" stroke-width="2"/>
      <circle cx="457" cy="484" r="8" fill="#F6F7FE"/>
      <circle cx="905" cy="484" r="8" fill="#F6F7FE"/>
      <circle cx="1353" cy="484" r="8" fill="#F6F7FE"/>
    </svg>
    <!-- Labels below -->
    <div style="display:flex; gap:0; width:1670px;">
      <div style="width:457px; display:flex; flex-direction:column; gap:24px;">
        <div style="font-size:36px; line-height:1.2;">{{PHASE_1_HEADING}}</div>
        <div style="font-size:20px; line-height:1.5; color:var(--muted); max-width:400px;">{{PHASE_1_DESC}}</div>
      </div>
      <div style="width:448px; display:flex; flex-direction:column; gap:24px;">
        <div style="font-size:36px; line-height:1.2;">{{PHASE_2_HEADING}}</div>
        <div style="font-size:20px; line-height:1.5; color:var(--muted); max-width:400px;">{{PHASE_2_DESC}}</div>
      </div>
      <div style="width:448px; display:flex; flex-direction:column; gap:24px;">
        <div style="font-size:36px; line-height:1.2;">{{PHASE_3_HEADING}}</div>
        <div style="font-size:20px; line-height:1.5; color:var(--muted); max-width:400px;">{{PHASE_3_DESC}}</div>
      </div>
      <div style="width:325px; display:flex; flex-direction:column; gap:24px;">
        <div style="font-size:36px; line-height:1.2;">{{PHASE_4_HEADING}}</div>
        <div style="font-size:20px; line-height:1.5; color:var(--muted); max-width:400px;">{{PHASE_4_DESC}}</div>
      </div>
    </div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Photo/Left (and alt)

Title block at top. Two bordered cards (750px tall), left card is an image placeholder (dark gray fill), right card has tag + heading + description at top and content at bottom. Same card structure as 2 Column.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:218px; left:50%; transform:translateX(-50%); width:1808px; height:750px; display:flex; gap:32px;">
    <!-- Photo placeholder -->
    <div style="flex:1; border:1px solid var(--more-muted); background:var(--dark-gray); overflow:hidden;">
      <!-- Replace with <img> if image available -->
    </div>
    <!-- Content card -->
    <div style="flex:1; border:1px solid var(--more-muted); padding:40px 40px 32px; display:flex; flex-direction:column; justify-content:space-between; overflow:hidden;">
      <div style="display:flex; flex-direction:column; gap:24px;">
        <div style="font-size:36px; line-height:1.2; color:var(--more-muted);">{{NUMBER}}</div>
        <div style="font-size:48px; line-height:1.2; letter-spacing:-1px;">{{CARD_HEADING}}</div>
        <div style="font-size:24px; line-height:1.2;">{{CARD_DESCRIPTION}}</div>
      </div>
      <div>
        <ul style="list-style:disc; padding-left:30px; font-size:20px; line-height:1.5; display:flex; flex-direction:column; gap:2px;">
          <li>{{BULLET}}</li>
        </ul>
      </div>
    </div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Team/6, Staff/5, Staff/4

Title block at top. Grid of member cards below. Team/6 = 3×2 grid, Staff/5 = 5×1, Staff/4 = 4×1. Each card: photo placeholder (square, dark gray, bordered), name (20px medium weight), title (20px muted).

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <!-- Team/6: 3 columns, 2 rows -->
  <div style="position:absolute; top:218px; left:56px; width:1808px; display:grid; grid-template-columns:repeat(3, 1fr); gap:32px;">
    <div style="display:flex; flex-direction:column; gap:12px;">
      <div style="aspect-ratio:1; background:var(--dark-gray); border:1px solid var(--more-muted);"></div>
      <div style="font-size:20px; line-height:1.5; font-weight:500;">{{NAME}}</div>
      <div style="font-size:20px; line-height:1.5; color:var(--muted);">{{TITLE}}</div>
    </div>
    <!-- Repeat for each team member -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

For **Staff/5**: `grid-template-columns: repeat(5, 1fr);`
For **Staff/4**: `grid-template-columns: repeat(4, 1fr);`

### Title Page / Big Illustration

Title (128px) on left side (888px wide, vertically centered at top=calc(50%-480px)), MW wordmark below at left=56 top=604. Large decorative illustration (thin white stroke line art) on right starting at left=976, 1245px wide, vertically centered. No cover graphic pane.

```html
<div class="slide">
  <div style="position:absolute; top:calc(50% - 480px); left:56px; width:888px; font-size:128px; line-height:1.2;">{{DECK_TITLE}}</div>
  <div style="position:absolute; top:604px; left:56px;">
    <div class="mw-wordmark" style="width:172px; height:27px;"></div>
  </div>
  <!-- Decorative illustration right side — generate thin-stroke geometric SVG -->
  <div style="position:absolute; top:50%; left:976px; transform:translateY(-50%); width:1245px; height:1603px; overflow:hidden; display:flex; align-items:center; justify-content:center;">
    <svg viewBox="0 0 800 1000" width="80%" fill="none">
      <!-- Generate radial/geometric thin-stroke line art here -->
    </svg>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Bar Chart

Title block at top. 3-4 stepped blue bars aligned to bottom, each bar is a content card (blue fill, dashed right border between bars). Each bar: number (32px, 90% opacity), heading (48px), description (24px). Bars are bottom-aligned at y=379, tallest ~645px. Each bar ~603px wide.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; bottom:56px; left:56px; width:1808px; display:flex; align-items:flex-end;">
    <!-- Bar 1 (shortest) -->
    <div style="width:603px; height:430px; background:var(--blue); border-right:1px dashed var(--fg); padding:56px 64px; display:flex; flex-direction:column; gap:20px;">
      <div style="font-size:32px; opacity:0.9;">01</div>
      <div style="font-size:48px; line-height:1.2; letter-spacing:-1px;">{{BAR_1_HEADING}}</div>
      <div style="font-size:24px; line-height:1.5;">{{BAR_1_DESC}}</div>
    </div>
    <!-- Bar 2 (medium) -->
    <div style="width:602px; height:515px; background:var(--blue); border-right:1px dashed var(--fg); padding:56px 64px; display:flex; flex-direction:column; gap:20px;">
      <div style="font-size:32px; opacity:0.9;">02</div>
      <div style="font-size:48px; line-height:1.2; letter-spacing:-1px;">{{BAR_2_HEADING}}</div>
      <div style="font-size:24px; line-height:1.5;">{{BAR_2_DESC}}</div>
    </div>
    <!-- Bar 3 (tallest) -->
    <div style="width:602px; height:645px; background:var(--blue); padding:56px 64px; display:flex; flex-direction:column; gap:20px;">
      <div style="font-size:32px; opacity:0.9;">03</div>
      <div style="font-size:48px; line-height:1.2; letter-spacing:-1px;">{{BAR_3_HEADING}}</div>
      <div style="font-size:24px; line-height:1.5;">{{BAR_3_DESC}}</div>
    </div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Gantt

Title block at top. Timeline grid below with period labels across the top and task rows. Each row: task label (left, 200px) + colored bar spanning the relevant time columns. Use CSS grid with `grid-template-columns: 200px repeat(N, 1fr)`. Bars use blue fill for primary tasks, foreground at 30% opacity for secondary.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:218px; left:56px; width:1808px; display:flex; flex-direction:column; gap:8px;">
    <!-- Period headers -->
    <div style="display:grid; grid-template-columns:200px repeat(6, 1fr); gap:4px; align-items:center;">
      <span></span>
      <span style="font-size:20px; color:var(--muted);">{{PERIOD_1}}</span>
      <span style="font-size:20px; color:var(--muted);">{{PERIOD_2}}</span>
      <!-- Repeat periods -->
    </div>
    <!-- Task row -->
    <div style="display:grid; grid-template-columns:200px repeat(6, 1fr); gap:4px; align-items:center;">
      <span style="font-size:20px; line-height:1.5;">{{TASK_NAME}}</span>
      <div style="grid-column:2/5; height:36px; background:var(--blue); opacity:0.8;"></div>
    </div>
    <!-- Repeat task rows -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Target

Title block at top. Left side (735px): vertical stack of metric rows. Each row: status icon (32px green square with check) + month label (60px) + bordered progress tile (428×211px) with tag, big number (88px), and arrow icon. Right side (starting left=1020): concentric circles (blue fill, white stroke) with dashed lines connecting from metric tiles to circle rings. Center value (72px) in the innermost ring.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <!-- Left: metric rows -->
  <div style="position:absolute; top:217px; left:56px; width:735px; display:flex; flex-direction:column; gap:40px;">
    <!-- Metric row -->
    <div style="display:flex; gap:186px; align-items:center;">
      <div style="width:121px; display:flex; flex-direction:column; gap:16px;">
        <div style="width:32px; height:32px; background:var(--green); display:flex; align-items:center; justify-content:center;">
          <i class="ph ph-check" style="font-size:18px; color:var(--bg);"></i>
        </div>
        <div style="font-size:60px; line-height:1.2; letter-spacing:-1px;">{{MONTH}}</div>
      </div>
      <div style="width:428px; height:211px; border:1px solid var(--fg); padding:24px; display:flex; flex-direction:column; justify-content:space-between;">
        <div style="display:inline-block; padding:2px 8px; background:rgba(169,169,169,0.24); font-size:20px; width:fit-content;">{{TAG}}</div>
        <div style="display:flex; align-items:flex-end; gap:8px;">
          <div style="font-size:88px; line-height:1.2; flex:1;">{{VALUE}}</div>
          <div style="padding-bottom:20px;"><i class="ph-light ph-arrow-up-right" style="font-size:48px;"></i></div>
        </div>
      </div>
    </div>
    <!-- Repeat rows -->
  </div>
  <!-- Right: concentric circles -->
  <div style="position:absolute; top:180px; left:1020px; width:1300px; height:1300px;">
    <svg width="100%" height="100%" viewBox="0 0 1300 1300" fill="none">
      <circle cx="650" cy="650" r="648" stroke="#F6F7FE" stroke-width="2" fill="none"/>
      <circle cx="650" cy="650" r="407" stroke="#F6F7FE" stroke-width="1.5" fill="var(--blue)" fill-opacity="0.3"/>
      <circle cx="650" cy="650" r="165" stroke="#F6F7FE" stroke-width="1.5" fill="var(--blue)"/>
      <text x="650" y="670" text-anchor="middle" fill="#F6F7FE" font-family="DM Sans" font-size="72" letter-spacing="-1">{{CENTER_VALUE}}</text>
    </svg>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Initiatives

Title block at top. 3-column card grid (same structure as 3 Column/Offer but without the bottom bullet list section). Cards are numbered, with heading + description. Can also use a 2×2 or 2×3 grid for more than 3 initiatives.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:218px; left:50%; transform:translateX(-50%); width:1808px; display:grid; grid-template-columns:repeat(3, 1fr); gap:32px;">
    <div style="border:1px solid var(--more-muted); padding:40px; display:flex; flex-direction:column; gap:24px;">
      <div style="font-size:36px; line-height:1.2; color:var(--more-muted);">01</div>
      <div style="font-size:48px; line-height:1.2; letter-spacing:-1px;">{{INITIATIVE_HEADING}}</div>
      <div style="font-size:24px; line-height:1.2; color:var(--muted);">{{INITIATIVE_DESC}}</div>
    </div>
    <!-- Repeat cards -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

For **Initiatives (alt)**: use `grid-template-columns: repeat(2, 1fr);` for a 2-column layout.

### Product Process

Title block at top. Horizontal flow of numbered steps connected by Phosphor arrow icons. Each step: number (36px muted) + heading (40px) + description (24px muted). Steps use flex row with arrows between.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:350px; left:56px; width:1808px; display:flex; align-items:flex-start; gap:24px;">
    <div style="flex:1; display:flex; flex-direction:column; gap:16px;">
      <div style="font-size:36px; line-height:1.2; color:var(--more-muted);">01</div>
      <div style="font-size:40px; line-height:1.2;">{{STEP_HEADING}}</div>
      <div style="font-size:24px; line-height:1.5; color:var(--muted);">{{STEP_DESC}}</div>
    </div>
    <div style="padding-top:48px; color:var(--muted);"><i class="ph-light ph-arrow-right" style="font-size:32px;"></i></div>
    <!-- Repeat steps with arrows -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Logos / Half Page

Title block at top. Two-column layout: left has heading + description, right has a grid of logo cells. Each cell: bordered, centered image on dark background. Grid is typically 3×2 or 3×3.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:218px; left:56px; width:1808px; display:flex; gap:32px;">
    <!-- Left: content -->
    <div style="width:580px; display:flex; flex-direction:column; gap:24px; padding-top:40px;">
      <div style="font-size:48px; line-height:1.2; letter-spacing:-1px;">{{SECTION_HEADING}}</div>
      <div style="font-size:24px; line-height:1.5; color:var(--muted);">{{DESCRIPTION}}</div>
    </div>
    <!-- Right: logo grid -->
    <div style="flex:1; display:grid; grid-template-columns:repeat(3, 1fr); gap:1px; background:rgba(246,247,254,0.08);">
      <div style="background:var(--bg); display:flex; align-items:center; justify-content:center; padding:32px; aspect-ratio:16/9;">
        <!-- <img> or placeholder -->
      </div>
      <!-- Repeat cells -->
    </div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Logos / Full Page

Full-width logo grid. No side content area — grid spans the full 1808px width. 4 columns, logo cells centered with gray background.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:218px; left:56px; width:1808px; display:grid; grid-template-columns:repeat(4, 1fr); gap:1px; background:rgba(246,247,254,0.08);">
    <div style="background:var(--bg); display:flex; align-items:center; justify-content:center; padding:40px; aspect-ratio:16/9;">
      <!-- <img> or placeholder -->
    </div>
    <!-- Repeat cells -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Bento Box / 4 - Large Right

CSS Grid: 3 columns (1fr 1fr 2fr), 2 rows. Large cell spans right column across both rows. Cells have dark gray background, no border, small gap (12px).

```html
<div class="slide">
  <div style="position:absolute; top:56px; left:56px; width:1808px; height:912px; display:grid; grid-template-columns:1fr 1fr 2fr; grid-template-rows:1fr 1fr; gap:12px;">
    <div style="background:var(--dark-gray); overflow:hidden;"></div>
    <div style="background:var(--dark-gray); overflow:hidden;"></div>
    <div style="background:var(--dark-gray); overflow:hidden; grid-row:1/-1;"></div>
    <div style="background:var(--dark-gray); overflow:hidden;"></div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

For **Bento Box / 4 - Large Left**: swap to `grid-template-columns: 2fr 1fr 1fr;` and put the spanning cell in column 1.

### Bento Box / 6 Rightside

Title area on left, 6-cell grid on right. Left has heading + description. Right is 3×2 grid.

```html
<div class="slide">
  <div style="position:absolute; top:56px; left:56px; width:1808px; height:912px; display:grid; grid-template-columns:1fr 2fr; gap:32px;">
    <!-- Left: content -->
    <div style="display:flex; flex-direction:column; justify-content:center; gap:24px; padding:40px 0;">
      <div style="font-size:60px; line-height:1.2; letter-spacing:-1px;">{{HEADING}}</div>
      <div style="font-size:24px; line-height:1.5; color:var(--muted);">{{DESCRIPTION}}</div>
    </div>
    <!-- Right: 3×2 grid -->
    <div style="display:grid; grid-template-columns:repeat(3, 1fr); grid-template-rows:repeat(2, 1fr); gap:12px;">
      <div style="background:var(--dark-gray); overflow:hidden;"></div>
      <div style="background:var(--dark-gray); overflow:hidden;"></div>
      <div style="background:var(--dark-gray); overflow:hidden;"></div>
      <div style="background:var(--dark-gray); overflow:hidden;"></div>
      <div style="background:var(--dark-gray); overflow:hidden;"></div>
      <div style="background:var(--dark-gray); overflow:hidden;"></div>
    </div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### 3 Column / Arch

Title block at top. Three columns (no border, 64px horizontal padding) with heading (48px) + description (24px) at top. Decorative dashed semi-circle arcs at bottom of each column, connecting white dots. Vertical divider lines between columns. Content starts at y=270, 646px tall.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:270px; left:50%; transform:translateX(-50%); width:1808px; height:646px; display:flex;">
    <div style="flex:1; padding:0 64px 32px; position:relative;">
      <div style="font-size:48px; line-height:1.2; letter-spacing:-1px; margin-bottom:24px;">{{COL_1_HEADING}}</div>
      <div style="font-size:24px; line-height:1.2;">{{COL_1_DESC}}</div>
      <!-- Arch SVG -->
      <svg style="position:absolute; bottom:0; left:0; right:0;" viewBox="0 0 590 221" height="221" fill="none">
        <path d="M0 221 Q 295 0 590 221" stroke="#F6F7FE" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.5" fill="none"/>
        <circle cx="0" cy="221" r="8" fill="#F6F7FE"/>
        <circle cx="590" cy="221" r="8" fill="#F6F7FE"/>
      </svg>
      <!-- Right divider -->
      <div style="position:absolute; right:0; top:0; bottom:0; width:1px; background:var(--fg); opacity:0.3;"></div>
    </div>
    <div style="flex:1; padding:0 64px 32px; position:relative;">
      <div style="font-size:48px; line-height:1.2; letter-spacing:-1px; margin-bottom:24px;">{{COL_2_HEADING}}</div>
      <div style="font-size:24px; line-height:1.2;">{{COL_2_DESC}}</div>
      <svg style="position:absolute; bottom:0; left:0; right:0;" viewBox="0 0 590 221" height="221" fill="none">
        <path d="M0 221 Q 295 0 590 221" stroke="#F6F7FE" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.5" fill="none"/>
        <circle cx="0" cy="221" r="8" fill="#F6F7FE"/>
        <circle cx="590" cy="221" r="8" fill="#F6F7FE"/>
      </svg>
      <div style="position:absolute; right:0; top:0; bottom:0; width:1px; background:var(--fg); opacity:0.3;"></div>
      <div style="position:absolute; left:0; top:0; bottom:0; width:1px; background:var(--fg); opacity:0.3;"></div>
    </div>
    <div style="flex:1; padding:0 64px 32px; position:relative;">
      <div style="font-size:48px; line-height:1.2; letter-spacing:-1px; margin-bottom:24px;">{{COL_3_HEADING}}</div>
      <div style="font-size:24px; line-height:1.2;">{{COL_3_DESC}}</div>
      <svg style="position:absolute; bottom:0; left:0; right:0;" viewBox="0 0 590 221" height="221" fill="none">
        <path d="M0 221 Q 295 0 590 221" stroke="#F6F7FE" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.5" fill="none"/>
        <circle cx="0" cy="221" r="8" fill="#F6F7FE"/>
        <circle cx="590" cy="221" r="8" fill="#F6F7FE"/>
      </svg>
    </div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Bar Chart (alt)

Same as Bar Chart but with different bar proportions or horizontal orientation. Use the same template structure with adjusted heights/widths. The alt version may use 4 bars instead of 3.

### Initiatives (alt)

Same as Initiatives but with a 2-column grid instead of 3:
`grid-template-columns: repeat(2, 1fr);`

### Staff/5

Same as Team/6 but with 5-column single-row grid. Photo placeholders are narrower.

```html
<div class="slide">
  <div class="slide-title-block">
    <div class="label">{{SUBTITLE}}</div>
    <div class="heading">{{HEADING}}</div>
  </div>
  <div style="position:absolute; top:218px; left:56px; width:1808px; display:grid; grid-template-columns:repeat(5, 1fr); gap:20px;">
    <div style="display:flex; flex-direction:column; gap:12px;">
      <div style="aspect-ratio:1; background:var(--dark-gray); border:1px solid var(--more-muted);"></div>
      <div style="font-size:20px; line-height:1.5; font-weight:500;">{{NAME}}</div>
      <div style="font-size:20px; line-height:1.5; color:var(--muted);">{{TITLE}}</div>
    </div>
    <!-- Repeat 5x -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

Note: Staff/5 in Figma uses a 5-column, 5-row grid with 20px gutters and 40px offset. The photo grid aligns to this.

### Staff/4

Same structure as Staff/5 but 4 columns. Photos are larger.

```html
<!-- Same as Staff/5 but with: -->
<div style="... display:grid; grid-template-columns:repeat(4, 1fr); gap:20px;">
```

### Photo/Left (alt)

Same structure as Photo/Left. The alt variant may swap the content card style (e.g., using a tag instead of a number, or different bottom section content). Use the same template with content adjustments as needed.

### Bento Box / 4 - Large Left

Mirror of Bento Box / 4 - Large Right. Large cell spans left column across both rows.

```html
<div class="slide">
  <div style="position:absolute; top:56px; left:56px; width:1808px; height:912px; display:grid; grid-template-columns:2fr 1fr 1fr; grid-template-rows:1fr 1fr; gap:12px;">
    <div style="background:var(--dark-gray); overflow:hidden; grid-row:1/-1;"></div>
    <div style="background:var(--dark-gray); overflow:hidden;"></div>
    <div style="background:var(--dark-gray); overflow:hidden;"></div>
    <div style="background:var(--dark-gray); overflow:hidden;"></div>
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

### Bento Box / Full Masonry

4 columns of stacked 428×491px image placeholders, each column offset vertically for a masonry effect. Column widths are 428px each with ~32px gaps. Columns extend beyond the slide frame and clip. Staggered y-offsets create the masonry feel.

```html
<div class="slide" style="padding:0;">
  <div style="position:absolute; top:0; left:0; width:1920px; height:1080px; overflow:hidden; display:flex; gap:32px; padding-left:56px;">
    <!-- Column 1 (offset -121px) -->
    <div style="width:428px; flex-shrink:0; display:flex; flex-direction:column; gap:32px; margin-top:-121px;">
      <div style="width:428px; height:491px; background:#202020; display:flex; align-items:center; justify-content:center; flex-shrink:0;"></div>
      <div style="width:428px; height:491px; background:#202020; display:flex; align-items:center; justify-content:center; flex-shrink:0;"></div>
      <div style="width:428px; height:491px; background:#202020; display:flex; align-items:center; justify-content:center; flex-shrink:0;"></div>
    </div>
    <!-- Column 2 (offset -254px) -->
    <div style="width:428px; flex-shrink:0; display:flex; flex-direction:column; gap:32px; margin-top:-254px;">
      <div style="width:428px; height:491px; background:#202020; flex-shrink:0;"></div>
      <div style="width:428px; height:491px; background:#202020; flex-shrink:0;"></div>
      <div style="width:428px; height:491px; background:#202020; flex-shrink:0;"></div>
    </div>
    <!-- Column 3 (offset -121px) -->
    <div style="width:428px; flex-shrink:0; display:flex; flex-direction:column; gap:32px; margin-top:-121px;">
      <div style="width:428px; height:491px; background:#202020; flex-shrink:0;"></div>
      <div style="width:428px; height:491px; background:#202020; flex-shrink:0;"></div>
      <div style="width:428px; height:491px; background:#202020; flex-shrink:0;"></div>
    </div>
    <!-- Column 4 (offset -354px) -->
    <div style="width:428px; flex-shrink:0; display:flex; flex-direction:column; gap:32px; margin-top:-354px;">
      <div style="width:428px; height:491px; background:#202020; flex-shrink:0;"></div>
      <div style="width:428px; height:491px; background:#202020; flex-shrink:0;"></div>
      <div style="width:428px; height:491px; background:#202020; flex-shrink:0;"></div>
    </div>
  </div>
</div>
```

Note: No footer on this layout — it's a full-bleed image showcase. Replace placeholders with `<img>` tags or background-image fills.

### End Slide

CTA headline at top-left (72px), contact block at bottom-left (starts at y=802) with label/heading/body stack, social icons row below.

```html
<div class="slide">
  <div style="position:absolute; top:56px; left:56px; font-size:72px; line-height:1.2; letter-spacing:-1px;">{{CTA_HEADLINE}}</div>
  <div style="position:absolute; top:802px; left:56px; display:flex; flex-direction:column; gap:12px;">
    <div style="display:flex; flex-direction:column; gap:4px;">
      <div style="font-size:20px; line-height:1.5; color:var(--more-muted);">{{CONTACT_LABEL}}</div>
      <div style="font-size:60px; line-height:1.2; letter-spacing:-1px;">{{CONTACT_HEADING}}</div>
      <div style="font-size:20px; line-height:1.5;">{{CONTACT_DETAIL}}</div>
    </div>
    <!-- Social icons row (see § Reusable Patterns) -->
  </div>
  <div class="dc"><!-- footer --></div>
</div>
```

---

## 10. Data Visualization

These rules mirror the Figma data viz rules from `gotchas.md`, adapted to CSS.

### Color hierarchy

```css
.mw-chart {
  --chart-bg: var(--bg);
  --chart-primary: var(--fg);
  --chart-highlight: var(--blue);
  --chart-callout: var(--green);
  --chart-secondary: var(--med-gray);
  --chart-grid: rgba(246, 247, 254, 0.08);
  font-family: var(--font);
}
```

### Rules
- **Primary data**: foreground color.
- **Highlight**: blue — one series or element max per chart.
- **Callout**: green — one annotation or standout metric max per chart.
- **Secondary data**: muted or foreground at opacity 0.4.
- **Grid lines**: barely visible, orientation only.
- **Axes/labels**: muted, small type (12–14px).
- **Sharp corners on everything.** No border-radius.
- **No gradients.** Flat solid fills only.
- **Stroke-only decorations** for reference lines and annotations.

---

## 11. HTML-Specific Gotchas

### SVG strokes render thinner in HTML
Minimum `stroke-width: 1.5` for decorative elements, `2` for anything clearly visible. The MW line art should look delicate but not invisible.

### Font fallback
The HTML path uses DM Sans (Google Fonts) since TT Hoves requires a desktop license. Tell the user they can add TT Hoves via `@font-face` if they have the web font files.

### Slide scaling
At 1920×1080, slides are too large for most viewports. The JS scaling system handles this with CSS `transform: scale()` on the container. Text stays sharp because we scale the container, not font sizes.

### Claude artifact preview limitations
The Claude artifact sandbox blocks external CDN requests. This means:
- **Phosphor Icons** won't render in the preview (they require CDN CSS)
- **Google Fonts** may not load
- **MW Mark and Wordmark** always render because they're inline data URIs

Tell the user to **download the HTML file and open it in a browser** for the full experience.

### PDF export via print
`window.print()` gives zero control over print dialog settings (destination, scale, background graphics). The `@media print` CSS handles page size and color forcing, but the user must:
1. Select "Save as PDF" as destination
2. Check "Background graphics" in More Settings
3. Leave scale at default

### Image placeholders
Photo/team/bento layouts have image slots. Use gray placeholder (`background: var(--dark-gray)`) and tell the user to replace `src` attributes or backgrounds manually.

### Presentation mode uses opacity, not display
Most slides have inline `display:flex` or similar for layout. Using `display:none` in presentation mode would require `!important` which breaks layout when the slide is active. Opacity + pointer-events avoids this conflict entirely.
