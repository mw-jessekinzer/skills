# Converting v2 to v4

Contents: 1. Workflow · 2. Rule reversals · 3. Token map · 4. Component map · 5. Pattern map · 6. Icon map · 7. Find and fix list · 8. Conversion report

v2 is the `mw-saas-system` skill: `.mw-` CSS classes, `--mw-` tokens, `data-theme` attributes, zero radius, sentence case, blue overlines, an 8pt spacing scale, and ShadCN on Radix as a fallback. Platform pages built with it convert to v4 using this file.

---

## 1. Workflow

1. **Inventory.** List every section, component and state on the v2 page. Note data, copy, actions and behavior. Behavior and content are preserved; only the system changes.
2. **Identify the pattern** (dashboard, list, detail, settings, form) and rebuild the frame from `patterns.md`: Sidebar shell, inset header with breadcrumb, page header.
3. **Map components** with §4. Replace each `.mw-` element with the v4 component and the right variant. Don't port v2 CSS.
4. **Map tokens** with §3. Every color, font and size becomes a token or Tailwind class.
5. **Rewrite copy** per §2 and `content.md`: Title Case labels, sentence case prose, overlines removed or converted.
6. **Swap icons** with §6 to Phosphor Light.
7. **Add missing states** (empty, loading, error) that v2 skipped.
8. **Run the §7 find and fix list**, then the SKILL.md self-check, in light and dark mode.
9. **Write the conversion report** (§8).

Convert a page completely. Never ship a page that mixes v2 and v4 pieces.

---

## 2. Rule reversals

| v2 rule | v4 rule |
|---|---|
| `border-radius: 0` everywhere | Mira radius (`--radius: 0.45rem`), pills where Mira uses them |
| Sentence case for all text | Title Case for UI labels and headings; sentence case for prose |
| Headings always weight 400 | Mira weights; page and section titles Medium |
| Blue overline above every page title | No eyebrows. Breadcrumb carries context |
| Two-row page header with brand bar | Sidebar shell + inset header + page header |
| Light background `#F6F7FE`, surface `#E8E9F4` | White background, Zinc muted surfaces |
| Dark mode accent switches to green | Dark primary is MW Blue 700. Green is not a product color |
| Green KPI highlight | `foreground` metric; `text-success` only for genuinely positive values |
| 8pt spacing tokens, generous whitespace | Tailwind 4px scale, Mira's compact density |
| Comfortable default, opt-in compact density | Mira is compact by default; no density modes |
| System mono for code | DM Mono for code only |
| Icons: unspecified / Carbon | Phosphor Light only |
| `data-theme="dark"` | `.dark` class on `<html>` via next-themes |
| ShadCN fallback on Radix with `asChild` | Base UI components with the `render` prop |
| Buttons 40px, 16px text | Mira sizing |
| Secondary button is black filled | Secondary is Zinc; filled black buttons no longer exist |

---

## 3. Token map

| v2 token | v4 replacement |
|---|---|
| `--mw-color-background` | `bg-background` |
| `--mw-color-foreground` | `text-foreground` (light: MW Black) |
| `--mw-color-inverse` | `text-primary-foreground` on blue; otherwise rethink (no inverse surfaces) |
| `--mw-color-surface` (`#E8E9F4`) | `bg-muted` (inset blocks) or `bg-card` (containers) |
| `--mw-color-blue` | `bg-primary` / `text-link` / `mw-blue-600` |
| `--mw-color-navy` | `mw-blue-700` (hover, dark primary) |
| `--mw-color-green` | Remove. Use `primary` for highlights or `success` for positive values |
| `--mw-color-muted` (`#666`) | `text-muted-foreground` |
| `--mw-color-muted-light` | `bg-muted` |
| `--mw-color-gray-light` / `--mw-color-disabled` | Component `disabled` states (opacity handled by Mira) |
| `--mw-color-danger` / `--mw-color-destructive` | `destructive` |
| `--mw-color-success` | `success` (same `#407E0B` in light) |
| `rgba(1,3,19,0.15)` borders | `border-border` |
| `rgba(1,3,19,0.08)` row dividers | Table defaults (`border-b`) |
| `--mw-font-primary` | `font-sans` (TT Hoves) |
| `--mw-font-mono` | `font-mono` (DM Mono), code only |
| `--mw-text-hero/display/h1` | Rarely needed in product. Page Title is `text-xl font-medium` |
| `--mw-text-h2` (page title in v2 header) | `text-xl font-medium` |
| `--mw-text-h4/h5` (card titles) | `CardTitle` |
| `--mw-text-body` (16px) | `text-sm` (14px) for body; Mira sizes inside components |
| `--mw-text-body-sm` (14px) | `text-sm` or `text-xs` for descriptions |
| `--mw-text-caption` (12px) | `text-xs` |
| `--mw-spacing-5/6/7` (8/12/16) | `gap-2` / `gap-3` / `gap-4` |
| `--mw-spacing-9/10` (24/32) component padding | Mira component padding (don't set) |
| `--mw-spacing-12+` page padding | `p-4` to `p-6` |
| `--mw-radius: 0` | Delete. Mira radius applies |

---

## 4. Component map

| v2 | v4 | Notes |
|---|---|---|
| `.mw-btn--primary` | `Button` (default) | One per section |
| `.mw-btn--secondary` (black) | `Button variant="secondary"` or `"outline"` | Visual change: black fill goes away |
| `.mw-btn--ghost` | `Button variant="ghost"` | |
| `.mw-btn--destructive` | `Button variant="destructive"` + `AlertDialog` | Confirmation now required |
| `.mw-card` | `Card` with header/content/footer parts | |
| `.mw-card--kpi` | `Card` KPI composition (`components.md` §5) | Green value becomes foreground |
| `.mw-input` | `Field` + `Input` | Filled Mira input |
| `.mw-input-label` | `FieldLabel` | Title Case |
| Textarea | `Textarea` | |
| Select (native) | `Select` (or `NativeSelect` if native behavior was intentional) | |
| Search input | `InputGroup` with `MagnifyingGlass` | |
| `.mw-checkbox` | `Checkbox` | Mira square |
| Radio | `RadioGroup` | |
| `.mw-toggle` | `Switch` | Pill |
| Slider | `Slider` | |
| Number input | `Input type="number"` in `InputGroup` | |
| File upload | File upload composition (`components.md` §10) | |
| Date input | Date Picker (`Popover` + `Calendar`) | |
| Form field wrapper | `Field` / `FieldGroup` | |
| `.mw-modal` | `Dialog` | |
| Tooltip | `Tooltip` | |
| Popover / dropdown menu | `Popover` / `DropdownMenu` | Surface colored |
| `.mw-toast` | Sonner `toast()` | |
| `.mw-alert` (inline notification) | `Alert` | |
| Loading spinner / inline loading | `Spinner` | |
| `.mw-skeleton` | `Skeleton` | |
| Progress bar | `Progress` | |
| Step indicator | Stepper composition | |
| `.mw-tabs` (underline) | `Tabs` (Mira segmented) | Visual change |
| Breadcrumb | `Breadcrumb` | Moves into the inset header |
| Pagination | `Pagination` | |
| `.mw-shell` (topbar + sidebar) | `Sidebar` shell | Top bar removed |
| `.mw-nav-item` | `SidebarMenuButton` | No blue left border |
| Overflow menu | `DropdownMenu` + ghost icon `Button` with `DotsThree` | |
| Link variants | `Button variant="link"` or `text-link` anchor | |
| `.mw-badge--default` | `Badge variant="outline"` | |
| `.mw-badge--blue` | `Badge` (default) | |
| `.mw-badge--green` | `Badge` default, or success badge if it meant success | |
| `.mw-tag` | `Badge variant="secondary"` | |
| `.mw-tile` | `Card` or `Item` | |
| Accordion | `Accordion` | |
| `.mw-code` / `.mw-code-block` | Code treatment (`components.md` §9) | DM Mono |
| `.mw-switcher` (content switcher) | `ToggleGroup` (views) or `Tabs` (panels) | |
| `.mw-empty` | `Empty` | Add an action |
| `.mw-table` | `Table` / Data Table | Title Case headers, right-aligned numbers |
| `.mw-chart` | shadcn `Chart` with `chart-1..5` | Single-hue blue |

## 5. Pattern map

| v2 pattern | v4 pattern |
|---|---|
| Two-row page header (brand bar + overline + H1) | Sidebar header carries the logo; inset header carries breadcrumb; page header carries the title |
| Header metadata "Updated Month D, YYYY" | Page description line or a `text-xs text-muted-foreground` note near the data it describes |
| `.mw-shell__content` gray surface | `SidebarInset` with `bg-background`; cards provide structure |

---

## 6. Icon map

Map by meaning to Phosphor (Light). Common translations from Carbon (v2/v3) and Lucide (shadcn defaults):

| Meaning | Carbon | Lucide | Phosphor |
|---|---|---|---|
| Add | `Add` | `Plus` | `Plus` |
| Close | `Close` | `X` | `X` |
| Search | `Search` | `Search` | `MagnifyingGlass` |
| Settings | `Settings` | `Settings` | `Gear` |
| Menu | `Menu` | `Menu` | `List` |
| Overflow | `OverflowMenuVertical` / `Horizontal` | `MoreVertical` / `MoreHorizontal` | `DotsThreeVertical` / `DotsThree` |
| Chevron | `ChevronDown/Right` | `ChevronDown/Right` | `CaretDown` / `CaretRight` |
| Arrow | `ArrowRight` | `ArrowRight` | `ArrowRight` |
| External link | `Launch` | `ExternalLink` | `ArrowSquareOut` |
| Edit | `Edit` | `Pencil` | `PencilSimple` |
| Delete | `TrashCan` | `Trash2` | `Trash` |
| Copy | `Copy` | `Copy` | `Copy` |
| Check | `Checkmark` | `Check` | `Check` |
| Info | `Information` | `Info` | `Info` |
| Warning | `Warning` | `AlertTriangle` | `Warning` |
| Error | `WarningAlt` / `ErrorFilled` | `AlertCircle` | `WarningCircle` |
| Success | `CheckmarkOutline` | `CheckCircle` | `CheckCircle` |
| User | `User` | `User` | `User` |
| Team | `Group` | `Users` | `Users` |
| Home | `Home` | `Home` | `House` |
| Dashboard | `Dashboard` | `LayoutDashboard` | `SquaresFour` |
| Calendar | `Calendar` | `Calendar` | `Calendar` |
| Time | `Time` | `Clock` | `Clock` |
| Filter | `Filter` | `Filter` | `Funnel` |
| Sort | `ArrowsVertical` | `ArrowUpDown` | `ArrowsDownUp` |
| Download | `Download` | `Download` | `DownloadSimple` |
| Upload | `Upload` | `Upload` | `UploadSimple` |
| Document | `Document` | `FileText` | `FileText` |
| Notification | `Notification` | `Bell` | `Bell` |
| Sign out | `Logout` | `LogOut` | `SignOut` |
| Chart | `ChartBar` | `BarChart3` | `ChartBar` |
| Link | `Link` | `Link` | `Link` |
| Lock | `Locked` | `Lock` | `Lock` |
| Eye / reveal | `View` / `ViewOff` | `Eye` / `EyeOff` | `Eye` / `EyeSlash` |
| Loading | `InProgress` | `Loader2` | use `Spinner` component |

For anything not listed, search Phosphor by meaning, not by the old name.

---

## 7. Find and fix list

Search the converted code for each; every hit must be resolved.

| Search for | Fix |
|---|---|
| `mw-` classes, `--mw-color`, `--mw-text`, `--mw-spacing` | Replace with v4 components, tokens, Tailwind |
| `data-theme` | `.dark` class via next-themes |
| `rounded-none`, `border-radius: 0` | Delete |
| `#F6F7FE`, `#E8E9F4`, `#666666`, `#A9A9A9`, `#C7FA50`, any raw hex | Tokens |
| `uppercase`, `tracking-wide`, `tracking-wider`, `tracking-widest` | Remove; Title Case text |
| `font-mono` | Keep only on code snippets |
| `asChild` | `render` prop |
| `lucide-react`, `@carbon/icons-react` | Phosphor |
| `DM_Sans`, `'DM Sans'` as a primary font | TT Hoves |
| `font-weight: 300` / `font-light` | Remove; never Light |
| `.overline` | Remove or move context to breadcrumb |

---

## 8. Conversion report

After converting, give a short report:
- Pattern used and shell structure
- Components swapped, with any visual changes worth noticing (secondary buttons, tabs, radius)
- Copy changes (case updates, rewritten labels)
- States added (empty, loading, error)
- Anything that had no clean v4 equivalent and how it was handled
- Open questions for the design team


## Remove side accents
v2 used colored left rules ("spines") on alerts, cards and tree nodes. v4 removes every one of them.
- Search for `border-l-`, `border-s-`, `border-inline-start`, `border-left`, and `box-shadow` values with `inset` and a horizontal offset.
- Replace with a uniform 1px `border`. If the color carried meaning (department, project, status), move it into a swatch, `Badge` or the icon color inside the element.
- Alerts use the `Alert` component's own variants; never add a colored edge.
