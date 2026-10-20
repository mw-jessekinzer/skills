# State Coverage

A UI is a system of states that change over time, with imperfect data and failures. If a state isn't designed, engineers invent it.

## The six families

- **Data**: loading, first-time empty, empty after filtering, populated, partial, no permission, offline, stale, optimistic, failed fetch, retry success and failure.
- **Interaction**: default, hover, focus, pressed, disabled (with reason), selected, expanded, dragging, in progress, completed, rejected.
- **Form**: placeholder, filled, editing, valid, invalid, required missing, read-only, submitting, submitted, save failed.
- **Content**: short and long content, empty text, very large and small numbers, null values, truncation, overflowing labels, localized expansion.
- **System**: permission denied, not found, timeout, server error, offline, rate limited, maintenance, session expired.
- **Recovery**: retry, undo, restore, draft saved, reconnected, fallback content.

## Platform treatments (MW Platform Design System v4 components)

| State | Treatment |
| --- | --- |
| Loading | `Skeleton` shaped like the content. Spinner only for small inline refreshes, always with a label |
| Empty, first time | `Empty`: muted icon, Title Case title, one sentence on why, one action that starts the work |
| Empty, filtered | Same, but the action clears the filter or search |
| Empty, not yours | Read-only views say whose data it is ("Jo hasn't logged anything today"), no create action |
| Error | Destructive `Alert` inside the region: what failed, that other work is safe, Retry. Never a blank region |
| Partial or stale | `text-xs text-muted-foreground` note with last updated time and a refresh action |
| Disabled | `aria-disabled` plus a reason Tooltip, unless obvious |
| Success | Toast that names the outcome and offers Undo when reversible |

When a region is empty, its Empty state owns the create action; hide the duplicate header button until there's content. Supporting helper text that repeats the empty message is hidden while empty.

## Transitions to define

Loading to content, empty to first item, editing to saving to saved, saved to changed again (Changes Not Posted), failure to retry, filtered-empty to cleared, locked to unlocked (earlier day posted). Each needs a trigger, what moves focus, and what's announced to screen readers.

## Accessibility

Every interactive state is reachable by keyboard with visible focus. Loading, success and errors are announced (live region). Status never relies on color alone. Reading order stays logical in empty and partial states. Respect reduced motion.

## Output when expanding a screen

1. State summary 2. State inventory with triggers 3. State-by-state look, copy and allowed actions 4. Transition logic 5. Missing states (highest value) 6. Implementation notes: variant names, copy, rules engineers need.
