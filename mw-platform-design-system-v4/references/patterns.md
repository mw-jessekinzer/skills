# MW Platform Design System v4 Patterns

Contents: 1. App shell · 2. Page header · 3. Dashboard · 4. List and table pages · 5. Detail pages · 6. Settings · 7. States · 8. Forms and flows · 9. Responsive · 10. Fast iteration

Patterns are page-level decisions. Components and tokens come from the other references.

---

## 1. App shell (Mira sidebar pattern)

Built from shadcn `Sidebar`. Mira's sidebar pattern leads; v2's top bar and v3's top nav logo placement are retired.

```
SidebarProvider
├── Sidebar (collapsible="icon")
│   ├── SidebarHeader     MW icon + "Midwestern Platform" (product switcher slot if needed)
│   ├── SidebarContent    SidebarGroups with Title Case labels and Phosphor Light icons
│   └── SidebarFooter     User menu (avatar, name, email, DropdownMenu: Profile, Theme, Sign Out)
└── SidebarInset
    ├── header            SidebarTrigger | Separator | Breadcrumb  …  page-level actions (right)
    └── main              page content
```

Rules:
- **SidebarHeader:** the `mw-icon.svg` mark in a small square tile (the `sidebar-primary` token or plain `foreground` mark) beside "Midwestern Platform" and an optional secondary line (team or workspace). When collapsed, only the mark shows.
- **Groups:** two to four groups, each with a `SidebarGroupLabel` in Title Case (Overview, Planning, Account, Support). Never uppercase.
- **Items:** Title Case label, Phosphor Light icon on top-level items. Sub items via `SidebarMenuSub` without icons.
- **Active item:** Mira's active state (accent background, medium weight). Don't add blue bars or borders.
- **Inset header:** sticky, `h-12` to `h-14`, bottom border. Contents: trigger, vertical separator, breadcrumb. Global search or ⌘K can sit on the right with page actions.
- **Header actions (right):** Recent Changes, Notifications, Theme toggle only. Anything already in the sidebar (Feedback, Ask Midwestern) never repeats in the header. No floating action buttons.
- **AI entry points:** Ask Midwestern lives in the sidebar under Stewardship with the Phosphor `Sparkle` icon. `Sparkle` marks AI features everywhere (prompt chips, AI answers); don't use it for anything else.
- **Collapsed state:** icon-only, tooltips on every item.
- **Mobile:** the sidebar becomes a sheet (built into `Sidebar`).
- Starting point: shadcn's sidebar blocks (for example `sidebar-07`, collapsible to icons) adapted to these rules.

## 2. Page header

Sits at the top of `main`, below the inset header.

- Page Title (`text-xl font-medium`, Title Case) on the left.
- Optional one-line description below (`text-sm text-muted-foreground`, sentence case).
- Page actions on the right: at most one `default` button plus secondary or outline buttons, or an overflow `DropdownMenu`.
- No eyebrow above the title. Context comes from the breadcrumb. (v2's blue overline is retired.)
- Tabs for sibling views go directly below the header.

## 3. Dashboard

- Row 1: KPI cards in a responsive grid (`grid gap-4 sm:grid-cols-2 xl:grid-cols-4`). Each card: label, metric, delta, optional sparkline.
- Row 2: one wide chart card (2/3 width) plus a narrower list or breakdown card (1/3).
- Row 3: a recent activity table or list card with "View All".
- Every card answers one question. Title states the subject ("Weekly Hours", "Open Projects"), description states the scope ("Last 6 months").
- Date range or filter controls go in the page header actions, not repeated in each card.
- Starting point: shadcn `dashboard-01` block, re-skinned.

## 4. List and table pages

- Page header with the primary create action ("New Project").
- Toolbar row: search (`InputGroup` with `MagnifyingGlass`), filter controls (`Select`, `ToggleGroup` or a filter `Popover`), view options; selected-row bulk actions replace filters when rows are selected.
- Data Table in a card or directly on the page (pick one per product and stay consistent; default: directly on the page with a border, for width).
- Row click opens the detail page or a `Sheet`. Row actions in a trailing `DotsThree` menu.
- Pagination footer.
- Empty, loading (skeleton rows) and error states for the table region.

## 5. Detail pages

- Header: object name as Page Title, status `Badge` beside it, primary action and overflow menu on the right.
- Optional `Tabs` for sections (Overview, Activity, Settings).
- Two-column layout on wide screens: main content (2/3) and a properties card (1/3) with label/value rows.
- Activity or history as an `Item` list, newest first.

## 6. Settings

- Settings sub-navigation: either a secondary vertical nav inside the page (Profile, Billing, Notifications, Security, Appearance) or `Tabs` for three or fewer sections.
- Each section is a card: title, description, fields, footer with Save (`default`) right aligned and Reset or Cancel (`outline`) left of it.
- Switches save immediately (toast confirms). Fields save with the card's button.
- Danger zone last: a card with a `destructive` outline treatment (icon `WarningCircle` in destructive color), action confirmed by `AlertDialog`.
- Max content width `max-w-3xl`.

## 7. States

Every data region designs all four states.

| State | Treatment |
|---|---|
| Loading | `Skeleton` shaped like the content. Spinner only for small inline refreshes |
| Empty | `Empty`: muted Phosphor icon, Title Case title ("No Codespaces"), one sentence on why and what to do, one action button, optional "Learn More" link |
| Error | `Alert` (destructive) in the region with what failed and a Retry button. Never a blank region |
| Partial / stale | Inline note in `text-xs text-muted-foreground` with last updated time and refresh action |

When a region is empty, its Empty state owns the create actions: hide the card or page header's create button ("New Entry") until the region has content, so the same action never appears twice. First-run empty states sell the next step ("Create Your First Project"). Filtered empty states offer to clear filters.

## 8. Forms and flows

- One column. Labels above fields. Related short fields (City, State, ZIP) may share a row.
- Group with `FieldSet` and `FieldLegend` when a form has distinct sections.
- Required fields are the default; mark optional ones with "(Optional)" after the label.
- Validate on blur and on submit. Errors appear under the field in `FieldError` and the first invalid field receives focus.
- Primary submit at the bottom right of the form or card; Cancel to its left.
- Multi-step flows: stepper composition at top, Back (outline) and Continue (default) at bottom, summary step before final submit.
- Short creation flows (one to four fields) go in a `Dialog`. Longer ones get a page or `Sheet`.

## 9. Responsive

- Breakpoints: Tailwind defaults (`sm` 640, `md` 768, `lg` 1024, `xl` 1280, `2xl` 1536).
- Grids collapse to one column below `md`.
- Tables scroll horizontally inside their container below `lg`; consider a card list on mobile for key tables.
- Page actions collapse into an overflow menu on mobile, keeping the primary visible.

## 10. Fast iteration

When asked to build or change a platform page quickly:
1. Identify the pattern (dashboard, list, detail, settings, form).
2. Start from the matching shadcn block or a previous v4 page; don't start from a blank file.
3. Fill with realistic Midwestern content (projects, clients, embedded designers, hours, reviews), not lorem ipsum or the shadcn demo content.
4. Run the SKILL.md self-check.
5. For changes, touch only what was asked and keep everything else identical.

Platform screens (Dashboard, Daily Log, Big Board and new features) use these patterns. Record page-specific decisions here as they're made.

## 11. Platform page decisions

### Daily Log
- One page, no modal. Header: "Daily Log" + status Badge (Not Started, Draft, Timer Running, Posted, Changes Not Posted, Viewing), date as description, View Day For select on the right only when the person can see more than one day.
- Layout: main column (Your Day card, then Today by Project card) and a 20rem side column (24rem at 1440+) with Day Total, To Do and Yesterday. One column below `lg`.
- Your Day: Brush Chips + Time Track. Card actions: Undo (ghost icon), Templates (outline, menu), Start/Stop Timer (outline). Enter Times (ghost) opens exact times.
- Today by Project is the YTB post: one Project Section per allocated project plus any shared project with time. Each has What Got Done (required when the project has time, optional when a done To Do is tagged to it) and its own blockers. Projects without time still accept blockers.
- To Do replaces Today's Goal. Unfinished items carry to tomorrow with a "From Yesterday" badge. Done items tagged to a project appear in that project's YTB.
- Day Total card owns the page's single primary button (Post Day, or Update Post after edits to a posted day) beside Copy YTB.
- Unposted earlier days: warning `Alert` above the layout with Review. Logging stays open; only posting waits.

### Dashboard
- Open Blockers rows show the project ("Client : Project · Open 3 days"). Report a Blocker goes to the Daily Log.

### Org Chart
- Person nodes use a uniform 1px border; department shows as the swatch chip inside the node. Selected node: `primary` border plus a 1px `primary` ring.

