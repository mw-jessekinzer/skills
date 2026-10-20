# Fonts

## The rule

- **TT Hoves** is the brand font. **DM Sans** is the approved fallback. Both are on-brand.
- Stack, everywhere: `'TT Hoves', 'DM Sans', 'Helvetica Neue', Arial, sans-serif`.
- **Never refuse DM Sans.** If TT Hoves is not available, build in DM Sans and say nothing more than "set in DM Sans, the approved fallback".
- **Never substitute any other font** (Inter, Roboto, Montserrat, system-ui, Space Grotesk, a mono). Helvetica Neue and Arial are last-resort system fallbacks in the stack, not choices.
- Regular (400) for everything. Medium (500) is the only other weight that exists in the system, and only when a tool forces a second weight. Never Bold.

## Why TT Hoves is never bundled

The TT Hoves desktop license covers fonts installed on licensed machines. It bars delivering the font through `@font-face` from a file and bars sharing the font file. So:

- Do not copy, embed, base64-encode, upload or link a TT Hoves file in anything you make, and do not ask the user for it.
- The templates load TT Hoves with `local()` only, which uses the copy installed on a design machine. On any other machine, DM Sans takes over automatically.

## How each surface gets its font

| Surface | TT Hoves | DM Sans |
|---|---|---|
| HTML artifact, claude.ai or Claude Code | Used if installed on the viewer's machine (`local()`) | Loaded from Google Fonts (`fonts.gstatic.com`, allowed in artifacts) |
| HTML file opened or rendered offline (sandbox, Claude Code, Cowork) | Same | Copy `assets/fonts/dm-sans/DMSans-Variable.ttf` into a `fonts/` folder next to the HTML. The MW FONTS block already looks there; never edit the block. |
| PDF or PNG from HTML (Chrome) | Embedded by Chrome if installed on the machine that prints | Google Fonts when online; otherwise the `fonts/` copy above. Copy it before every sandbox render. |
| PDF from Python (reportlab) | Never | Register `assets/fonts/dm-sans/DMSans-Regular.ttf` (and `DMSans-Medium.ttf`) |
| PPTX / DOCX (python-pptx, python-docx) | Set the font name "TT Hoves" only if the user says they and their audience have it | Otherwise set "DM Sans". Office files do not embed fonts from these libraries. |
| Google Slides / Docs | Not available | Built in: pick DM Sans |
| Figma | Local only; the Plugin API cannot load it | Build in DM Sans; a designer swaps to TT Hoves locally |
| Claude Design | Not uploaded (license) | Upload the DM Sans files; see `claude-design.md` |

## DM Sans tuned to TT Hoves

DM Sans at its automatic optical size sets 6 to 7% wider than TT Hoves at text sizes and about 4% narrower at display sizes, so a layout built on one font reflows on the other. The templates fix this:

- `font-variation-settings: "opsz" 32` on `html` pins DM Sans to one optical size at every size.
- `size-adjust: 99%` on the DM Sans `@font-face`.

Measured in Chrome, that puts DM Sans text within 1% of TT Hoves widths from 10 to 120px. Big numerals run up to 10% narrower at 280px. Budgets are set on TT Hoves, so DM Sans never overflows. TT Hoves ignores both settings. Keep the MW FONTS block exactly as it is in the templates.

For reportlab or Office files (static DM Sans, no optical axis), DM Sans runs about 6% wider: budget 10% fewer words per line, or add -0.03em tracking (-3%) on text under 24pt.

## reportlab snippet

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
FONTS = "<skill>/assets/fonts/dm-sans/"
pdfmetrics.registerFont(TTFont("DMSans", FONTS + "DMSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("DMSans-Medium", FONTS + "DMSans-Medium.ttf"))
```

## Files

`assets/fonts/dm-sans/`: `DMSans-Variable.ttf` (from the google/fonts repository), `DMSans-Regular.ttf` and `DMSans-Medium.ttf` (static cuts from the googlefonts/dm-fonts source repository), `OFL.txt` (SIL Open Font License; the fonts may be bundled and shared).
