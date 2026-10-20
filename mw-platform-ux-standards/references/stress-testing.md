# Stress Testing (Break the UI)

Demo data is chosen, usually without anyone noticing, to make a design look good. Undo that choice one field at a time.

## Hard rules

1. **Plausible or schema-backed, never random.** Each worst-case value is something a real user could produce, or the actual limit from the schema, column or API. No limit found is itself a finding ("unbounded").
2. **Change the data, not the component.** Worst-case data enters through the same boundary as demo data (fixture, mock, props, API stub). Never hand-edit markup to cause a break.
3. **One dataset, many failures.** Spread different failures across the first rows, since that's what's on screen.
4. **The toggle is dev-only.** A segmented control (Demo, Worst Case, One, plus Empty, Loading, Error) fixed at the bottom of the viewport in prototypes, or a `?data=worst&state=error` URL param in the app. Never ships.
5. **Report before fixing** when a break is a design decision (wrap or truncate, hide or show a placeholder).

## Workflow

1. **Map the surface.** Table every rendered value: field, source, type, limit, optional. Include counts, timestamps, badge text, tooltips, avatars and list length.
2. **Build the fixture** from the catalog below, shaped exactly like the demo data. Also cover Empty, One (every count at exactly 1) and Huge (realistic upper bound, 1,000+ for unpaginated lists).
3. **Wire the toggle.**
4. **Break it** at the real container width, 320px, the widest layout, 200% zoom, dark mode, and RTL if supported.
5. **Report**: what broke (Broken, Ugly, Fragile), decisions for the designer, what held up.
6. **Fix on request**, then flip through every state again, Demo included. Keep the fixture as a regression test.

## Platform worst-case catalog

| Kind | Values that break things |
| --- | --- |
| Person names | Aleksandra Wiśniewska-Kowalczyk · Jo · Bartholomew Fitzgerald-Montgomery III · Nguyễn Thị Minh Khai |
| Emails | bartholomew.fitzgerald@northwind-industries-holdings.example.com · jo@mw.co · empty |
| Client : Project | Lutheran Hour Ministries International Partnerships : Daily Reflection Flow Rebuild (Phase 2) · KHA : QA · Fundación Ayuda en Acción Latinoamérica : Donor Portal · Webb City Historical Society & Museum Foundation : Collections Archive Migration |
| URLs in free text | https://staging.northwind-industries-holdings.example.com/api/v2/donors (no break opportunities) |
| Free text | Several paragraphs with bullets, emoji, Spanish and Vietnamese diacritics |
| Counts | 0 · 1 (pluralization) · 1,284 (separators) · 12+ items in a short list |
| Durations | 0:05 · 16:45 in a day · over the 8:00 target · a 5 minute block on a 14 hour track |
| Time ranges | Starting 6:00 AM or earlier · ending 11:45 PM · overlapping entries from older data |
| Allocation | Full time · 62.5% · 0% · not set |
| Dates | Overdue · several unposted days · due today |
| Optional fields | Missing role, missing notes, missing avatar |
| Collections | Six or more projects (categorical colors repeat after five) |

## Failure signatures and fixes

| What you see | Fix |
| --- | --- |
| Avatar, swatch or icon squished | `flex-shrink: 0` on fixed-size boxes |
| Text overflows instead of wrapping | `min-width: 0` on the text column (`minmax(0, 1fr)` in grid) |
| URL or email runs past the edge | `overflow-wrap: anywhere` on that element |
| Trailing action pushed off-screen | `min-width: 0` on the middle, `flex-shrink: 0` on the action |
| Badge wraps onto two lines | `white-space: nowrap; flex-shrink: 0` on the badge |
| Avatar adrift beside a 3-line name | Top-align rows once text can wrap |
| Wrong initials | Grapheme-aware initials (`Intl.Segmenter`), first and last word, skip suffixes like III |
| Orphaned placeholder where a field was | Omit the line or reserve height on purpose |
| "1 members" | `Intl.PluralRules` |
| Jittering or misaligned numbers | `tabular-nums` (the `num` utility) |
| `1284`, `NaN`, `undefined` | `Intl.NumberFormat`, guard nulls |
| Truncated with no way to read it | `title` or Tooltip plus the full value elsewhere |
| Sliver too small to show a label | Hide the label below a width threshold, keep the accessible name and tooltip |
| Card actions crush the title on mobile | Wrap actions below the title under 640px |
| Global input padding overrides an icon inset | Raise the specificity of the icon rule, verify every search field |

## Truncate, wrap or clamp

- **Wrap** what identifies something (names, project titles in sections).
- **Truncate at the end** for secondary metadata, always with a way to see the full value.
- **Truncate in the middle** when items differ at the end (file names, emails on one domain).
- **Clamp** multi-line previews (3 lines) so card heights stay predictable.
- **Never truncate** numbers, amounts, dates or anything people compare.
