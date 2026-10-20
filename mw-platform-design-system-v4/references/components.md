# MW Platform Design System v4 Components

Contents: 1. Ground rules · 2. Base UI notes · 3. Actions · 4. Forms · 5. Data display · 6. Navigation · 7. Overlays and menus · 8. Feedback and states · 9. Code · 10. Missing components

---

## 1. Ground rules

- Every component comes from the generated Mira set in `@/components/ui/*`. Add with `pnpm dlx shadcn@latest add <name>`.
- Never edit sizes, padding, radius or font sizes inside a component file. If something looks wrong, fix the token or the usage, not the component.
- Allowed edits to component files: replacing inverted menu classes with surface classes (§7), removing `uppercase`/wide `tracking-*` classes, removing `font-mono` from non-code elements, swapping any non-Phosphor icon, and changing 14px icon sizes (`size-3.5`) to 16px (`size-4`).
- Compose with the component's own parts (`CardHeader`, `CardTitle`, `FieldLabel`, ...) rather than rebuilding anatomy from `div`s.
- Use component variants before custom classes. A custom class that recreates a variant is a bug.

## 2. Base UI notes

The preset uses **Base UI**, not Radix. This matters when reading older shadcn examples or converting v2 code:

- Composition uses the **`render` prop**, not `asChild`. Example: `<Button render={<Link href="/settings" />}>Settings</Button>`, `<DropdownMenuTrigger render={<Button variant="ghost" size="icon" />}>`.
- Prop names can differ from Radix (open state, side and alignment props, value change callbacks). Check the generated component file or the shadcn docs for the Base UI variant before guessing.
- Radix-only examples copied from the web must be adapted, not pasted.

---

## 3. Actions

### Button
| Variant | Use |
|---|---|
| `default` (MW blue) | The single primary action of a view or card section: Save, Create, Submit, Deploy |
| `secondary` | Supporting actions next to a primary, or neutral actions in toolbars |
| `outline` | Secondary actions where a visible boundary helps: Cancel, Download PDF, Attach File, Details |
| `ghost` | Low emphasis: icon buttons in toolbars and card headers, table row actions |
| `destructive` | Delete or irreversible actions. Always confirmed by an `AlertDialog` |
| `link` | Inline navigation inside text |

- Sizes: Mira defaults. `size="icon"` for icon-only buttons, which always get `aria-label` and usually a `Tooltip`.
- Footer order: secondary actions left of the primary; primary is rightmost. Cancel is `outline` or `ghost`.
- Leading or trailing icons are fine (`Plus` on Create, `ArrowRight` on Continue). Don't put icons on every button.
- Labels are Title Case verbs: "Save Changes", "Invite Members", "Create Codespace".
- Loading: keep the label, add `Spinner` and set `disabled`.

### Button Group
Joined related actions (split buttons, segmented actions). Don't use it to align unrelated buttons.

### Toggle / Toggle Group
On/off formatting or view switches (list vs grid, Day/Week/Month). For switching content panels use `Tabs`.

---

## 4. Forms

### Field (and FieldGroup, FieldLabel, FieldDescription, FieldError, FieldSet, FieldLegend)
Wrap every control in `Field`. Every control has a visible `FieldLabel` unless the context makes it obvious (search boxes), in which case use `aria-label`. Descriptions go under the control in `FieldDescription`; errors replace or follow the description in `FieldError`.

### Input / Input Group
Mira inputs are filled (muted background) with a light border. Use `InputGroup` for prefixes and suffixes ($, units, search icon, copy button). Placeholders show an example, never the label.

### Textarea
Same treatment as Input. Give it a sensible minimum height; don't auto-grow beyond the viewport.

### Select / Native Select / Combobox
- `Select` (Base UI) for 2 to ~15 options.
- `Combobox` or `Command` in a `Popover` when the list is long or searchable.
- `NativeSelect` only where a native picker is better (mobile-heavy forms).
- Placeholder reads "Select a Topic" style: Title Case, starts with Select or Choose.

### Checkbox
Open decision: Mira's square checkbox ships today; a round checkbox was also proposed. Until it's settled, use the generated Mira checkbox and don't restyle it per page.
Mira square checkbox with the small radius. Checked state is MW blue. Use for multi-select and single opt-ins. Labels sit to the right and are clickable.

### Radio Group
One choice from a short list. For visual choices with descriptions (Bank Transfer vs PayPal), use radio cards: the `RadioGroup` item inside a bordered container, selected border in primary.

### Switch
Pill, MW blue when on. Immediate effect settings only (no Save button needed). If the change needs Save, use a Checkbox instead.

### Slider
Ranges and continuous values. Always show the current value next to or above it, with min and max labels when the range isn't obvious.

### Input OTP
Verification codes only.

### Calendar / Date Picker
`Calendar` inside a `Popover` triggered by an outline button that shows the selected date. Selected day uses primary.

### Label
Only when `Field` doesn't fit. Title Case.

---

## 5. Data display

### Card
Anatomy: `CardHeader` (`CardTitle`, `CardDescription`, optional `CardAction` top right), `CardContent`, optional `CardFooter`.
- Card titles are Title Case; descriptions are sentence case, one line ideally.
- `CardAction` holds a ghost icon button, a small outline button ("View All") or a badge. One item.
- Cards never get colored backgrounds. Nested surfaces inside a card use `bg-muted` (Mira's inset blocks, like stat groups).
- KPI card: `CardDescription` as the metric label, metric in `text-2xl font-medium num`, optional delta as a `Badge` or `text-success`/`text-destructive` small text.

### Table / Data Table
- Simple lists: `Table`. Sorting, filtering, selection or pagination: Data Table (TanStack Table on `Table`).
- Header cells Title Case, `text-muted-foreground`, never uppercase.
- Numbers right-aligned with the `num` utility. Text left-aligned. Status as `Badge`.
- Row actions: a ghost icon button with `DotsThree` opening a `DropdownMenu`, at the row end.
- Selection: checkbox column first. Bulk actions appear in the toolbar when rows are selected.
- Toolbar above the table: search `InputGroup` left, filters next, primary action right.
- Pagination below, right aligned, with row count left.

### Badge
| Variant | Use |
|---|---|
| `default` (blue) | Highlights and "new" or promoted states. Sparingly |
| `secondary` | Neutral status and counts (Pending, Draft, 312) |
| `outline` | Metadata and categories (ETF, Stock, Firefox) |
| `destructive` | Failed, Error, Overdue |
| success | `className="bg-success/15 text-success"` style badge for Completed, Active, Paid. No other custom badge colors |

Badges are short Title Case nouns or adjectives. Never all caps. Badge icons are 12px in Phosphor **Regular** weight.

### Avatar / Avatar Group
Initials fallback always. Group stacks show a "+N" when overflowing.

### Item
Rows with icon, title, description and trailing action or chevron (settings lists, transaction lists). Prefer `Item` over hand-built flex rows.

### Accordion / Collapsible
FAQs and progressive disclosure. Don't hide primary content or required fields in accordions.

### Progress
Determinate progress and goal tracking. Show the value as text nearby.

### Chart
shadcn `Chart` (Recharts) with `chart-1` to `chart-5`. Tooltips and legends from the chart components. Axis text `text-muted-foreground text-xs`. Gridlines from `border`. Bars may keep Mira's small radius.

### Kbd
Keyboard shortcuts in menus and help. Uses TT Hoves, not mono.

### Separator, Scroll Area, Aspect Ratio, Resizable, Carousel
Use as provided. Carousel is rarely right in a platform UI.

---

## 6. Navigation

### Sidebar
The app shell. Details in `patterns.md` §1. Groups with Title Case `SidebarGroupLabel`s, Phosphor Light icons on every top-level item, active item uses Mira's active styling.

### Tabs
Mira tabs are segmented (filled pill on the active tab). Use for switching between sibling views of the same object (General, Billing, Goals). Max ~6 tabs. Title Case. Don't use tabs as primary navigation between unrelated pages; that's the sidebar's job.

### Breadcrumb
In the page header for anything two or more levels deep. Last item is the current page, not a link. Collapse the middle with an ellipsis beyond four levels.

### Pagination
Below tables and lists. Show previous and next plus a few page numbers.

### Navigation Menu / Menubar
Rarely needed inside the platform (the sidebar covers navigation). Don't add a top nav alongside the sidebar.

---

## 7. Overlays and menus

### Menus: match the surface
Dropdown Menu, Context Menu, Select content, Combobox, Command palette and Popover all use `bg-popover text-popover-foreground` with Mira's border, radius and shadow. The preset was configured with "Inverted / Translucent" menus; v4 overrides that.
- Best fix: set Menu to the default style in the shadcn create panel and regenerate.
- If components are already generated: in each menu content component, replace inverted classes (dark background, light text, `backdrop-blur`, translucency on the content surface) with `bg-popover text-popover-foreground`. Keep Mira's sizing, padding and radius.
- Highlighted items use the `accent` token (Mira "Subtle" accent).

### Dropdown Menu
Group items with labels and separators. Destructive items last, `variant="destructive"`, separated. Shortcuts via `DropdownMenuShortcut` or `Kbd`. Items are Title Case.

### Dialog
Focused tasks that need the user's full attention: short forms, confirmations with input. Title Case title, sentence case description, footer with Cancel (outline) and the primary.

### Alert Dialog
Required for every destructive or irreversible action. Title names the action ("Delete Project?"), description states the consequence, confirm button uses `destructive` and repeats the verb ("Delete Project").

### Sheet / Drawer
Side panels for detail views, filters and longer edit forms that should keep page context. Drawer for mobile bottom sheets.

### Popover / Hover Card
Popover for small interactive content (date pickers, quick settings). Hover Card for preview-only content (user cards). Never put required actions in hover cards.

### Tooltip
Short labels for icon buttons and truncated text. One line, no actions, no essential information.

### Command
Command palette (⌘K) and searchable pickers.

---

## 8. Feedback and states

### Sonner (toasts)
Confirmation of completed actions ("Profile Saved"), undo opportunities, background task results. Not for errors the user must fix in a form; those go inline.
- **Position:** upper right, just below the inset header (`<Toaster position="top-right" offset={{ top: 60 }} />`, adjusting the offset to the header height). Newest on top. This is the platform standard.
- **Timing:** confirmations auto-dismiss after 4 seconds (Sonner's default `duration: 4000`). Toasts that need action stay until dismissed or resolved (`duration: Infinity`), like a missing-days warning that clears once the days are logged. Every toast has a close button.

### Alert
Inline, persistent messages within a page or card: info, warning (icon led), destructive. Title in Title Case, body in sentence case. Use the Phosphor `Info`, `Warning` or `WarningCircle` icon.

### Skeleton
Loading placeholders that mirror the final layout. Prefer skeletons over spinners for content regions.

### Spinner
Inline busy indicators: buttons, small refreshes, "Syncing Your Accounts". Always paired with text or an accessible label.

### Empty
Every list, table and data region has an empty state: icon (Phosphor, muted), Title Case title, one sentence of explanation, and the next action as a button. See `patterns.md` §7.

---

## 9. Code

Code snippets are the only place DM Mono appears: env variable keys and values, API endpoints, CLI commands, JSON, IDs meant to be copied.
- Inline: `<code className="font-mono text-xs rounded-sm bg-muted px-1 py-0.5">`.
- Blocks: `bg-muted` container, Mira radius, `font-mono text-xs`, horizontal scroll, copy button (ghost icon, `Copy` icon) top right.
- Secrets are masked by default with a reveal toggle.

---

## 10. Missing components

When v4 doesn't have what's needed:
1. Compose it from shadcn primitives and existing Mira components (most "missing" components are compositions: stat cards, file upload zones, steppers, timelines).
2. Check the shadcn registry and blocks for a Base UI compatible version.
3. Only then build custom, using tokens, Mira radius and spacing, Phosphor Light, and the same anatomy conventions. Document it in this file afterward.

Never pull in another component library (Carbon, MUI, Chakra, Mantine, Ant). v3's Carbon fallback rule is retired.

Common compositions:
- **File upload:** dashed `border-border` zone inside a card, `UploadSimple` icon, Title Case label ("Upload Files"), constraint text in `text-xs text-muted-foreground`, `outline` or `default` "Browse Files" button.
- **Stepper:** numbered circles (`bg-primary` for current and done, `bg-muted` for upcoming) with Title Case step labels, connected by `Separator`.
- **Stat group:** `bg-muted` rounded block inside a card with label (`text-xs text-muted-foreground`, Title Case) over value (`text-lg font-medium num`).


### Platform compositions (built for the Daily Log and Dashboard)
Compose these from existing primitives; don't add a library.
- **Time Track**: a horizontal lane (`bg-muted/45`, 1px `border`, hour gridlines from `border`) with absolutely positioned blocks. Blocks are `button`s filled with a project's categorical color (`--cat-1` to `--cat-5` in the theme, assigned by project order and repeating after five), text in `--bar-ink`, Mira small radius minus 4px. Edge handles are 10px wide hit areas with a 2px grip shown on hover and focus. Axis labels in `text-xs text-muted-foreground`. A 2px `foreground` line marks now. Wrap the track in a horizontal scroll container with a 40rem min width below `lg`.
- **Brush Chips**: a `ToggleGroup` in single mode with `role="radiogroup"`. Each chip is an outline button with a 10px color swatch and the project name, truncated at 15rem with the full name in a tooltip. Selected chip: `primary` border plus `primary` at 8% fill. The Break chip uses Phosphor `Eraser`.
- **Project Swatch**: 10px square, 2px radius, the project's categorical color. The only way category color appears on cards, rows and nodes (never a side stripe).
- **To Do Item**: `Checkbox` + clickable label (wraps, `overflow-wrap:anywhere`) + meta row (project swatch and client name, "From Yesterday" `Badge`) + trailing ghost `DotsThree` menu. Done items: `muted-foreground` with line-through, sorted to the bottom.
- **Blocker Item**: a block with `warning` at 9% fill and a uniform 1px `warning` at 22% border, Phosphor `Flag` in `warning`, text or `Textarea`, and its action on the right (Resolved outline button for carried blockers, ghost `X` for new ones).
- **Project Section**: swatch + project name (`text-sm font-medium`, wraps) + time ranges (`text-xs muted`, `num`) + total on the right (`num`). Body indented to the title edge (1.25rem).
