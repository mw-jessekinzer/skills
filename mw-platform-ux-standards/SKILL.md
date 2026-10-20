---
name: mw-platform-ux-standards
description: "MW Platform UX Standards: the UX rules for the Midwestern Platform (internal.buildmidwestern.com) and any Midwestern SaaS or internal tool. Covers how screens work rather than how they look: flows and fidelity, layout structure, full state coverage (loading, empty, error, partial, disabled), worst-case data stress tests, interaction patterns (direct manipulation, forms, overlays, undo, posting), accessibility and responsive behavior. Use whenever designing, prototyping, reviewing, specifying or building any platform page, feature, flow, form, table, dashboard or component, whenever someone asks to simplify a flow, find edge cases, stress test or break a UI, expand states, write a handoff or acceptance criteria, or review a PR for UX. Pair it with the MW Platform Design System v4 skill (mw-platform-design-system-v4), which owns visuals (color, type, icons, components); this skill owns behavior and structure. Trigger even when only one page is named, like Daily Log or Dashboard."
---

# MW Platform UX Standards

How Midwestern's platform should behave. These are the platform's UX standards. The `mw-platform-design-system-v4` skill decides what things look like; this skill decides how they work, what states they have and how they hold up under real data. When the two disagree, MW Platform Design System v4 wins on visuals and this skill wins on behavior. Defer to the design system unless something is broken; when it's broken, fix it and record the fix.

Built from four practices Midwestern uses on platform work: wireframe prototyping, layout structure (better-layout), state expansion (ui-state-expander) and adversarial data testing (break-ui), plus the patterns proven in the platform redesign.

## Core principles

1. **Simplest path first.** One page beats a modal for anything longer than four fields. Remove steps, toggles and duplicate previews before adding features. If two controls do the same job, keep one.
2. **A screen is a state machine, not a poster.** Every data region designs Ready, Loading, Empty, Error and Partial. Undesigned states get invented by whoever builds them.
3. **Real data, not kind data.** Design and test against the worst realistic values: long names, unbreakable URLs, one-letter names, zero, one, 1,000+, missing fields, non-Latin text, emoji.
4. **Structure through space.** Group with spacing first, background second, lines last. Gaps between groups are at least 2x gaps within them. Reading order follows importance.
5. **Never a dead end.** Every empty state offers the next action, every error offers Retry, every disabled control says why, every destructive change offers Undo or a confirm.
6. **Direct manipulation has a keyboard twin.** Anything you can drag, you can also do with keys or exact fields.
7. **Say what happened and what to do next.** Inline for fixable form problems, toasts for confirmations and undo, alerts for persistent page conditions.
8. **Respect the person's context.** Things belong to the object they're about (a blocker belongs to its project, not the day). Ask for information once and reuse it.

## Workflow

1. **Frame the job.** Who uses it, the one task they came to do, what data can fail or be missing, what they must recover from. Ask only what isn't already known.
2. **Map the flow** before screens: entry points, steps, decisions, exits, and what happens on refresh or back. See `references/prototyping.md`.
3. **Lay out by importance** with the rules in `references/layout.md`.
4. **Expand every state** with `references/states.md`. List missing states first when reviewing.
5. **Break it** with `references/stress-testing.md`: build a worst-case fixture next to the demo data, put both behind a dev-only toggle, check 320px, the real container width, 200% zoom, dark mode.
6. **Specify interactions** with `references/interaction.md`: triggers, keyboard paths, validation, feedback, undo.
7. **Hand off** with acceptance criteria per state and per worst case (format below).

## Platform rules (proven in the redesign)

- **Disabled with a reason.** Use `aria-disabled="true"` plus a reason; the control stays focusable, shows a Tooltip on hover and focus, and announces the reason on click. Use plain `disabled` only when the reason is obvious from context.
- **Gate the commit, not the work.** If something must happen first (post an earlier day), let people keep working and block only the final action, with an Alert that links to the fix.
- **Validate on submit, guide to the field.** Mark every invalid field, focus the first one, and clear each error as soon as it's fixed. Never disable a submit button just because fields are empty; let the click explain.
- **Undo beats confirm** for reversible changes (removing a time block, a to do, a blocker): act immediately, toast with Undo. Use an AlertDialog only when the change can't be undone.
- **Save as you go.** Drafts persist without a Save button. After posting, edits mark the item "Changes Not Posted" and the primary becomes Update Post.
- **One primary action per view.** Put it where the work ends (the summary card), not repeated per section.
- **Data the user can't edit is read-only, not disabled.** Viewing a teammate's day renders text, not locked inputs, and hides personal tools (their To Do).
- **Carry over, don't recreate.** Unfinished to dos and open blockers carry to the next day with a visible "From Yesterday" or "Carried from Wednesday" marker and a one-click resolve.
- **Category color lives inside the element** (swatch or badge), never as a colored side stripe.
- **Search fields:** leading icon, text starts after it, filters what's on screen live, and a filtered-to-empty state offers to clear the search.

## Review output

When asked for a review, report findings grouped by principle in a table: **Severity** (High blocks content or an action; Medium harms hierarchy, states or adaptability; Low is polish), **Location** (`file:line` or screen and component), **Before**, **After**, **Why**. Consolidate a repeated issue into one row. Then list **Missing States**, then **Worst Cases That Broke** (value, what happened, fix), then **What Held Up**. End with a verdict: Block (any High), Needs Changes, or Approve.

## Handoff output

For each screen: purpose in one sentence, layout (regions in reading order), data model, interactions with keyboard equivalents, validation rules, every state with its copy, worst-case behavior per field (wrap, truncate, clamp, never truncate numbers), accessibility notes, and acceptance criteria written as checkable statements.

## Self-check

1. The main task takes the fewest steps possible; no modal holds a long task
2. Every data region has Ready, Loading, Empty, Error and Partial states with copy and an action
3. Worst-case fixture exists and was checked at 320px, real container width, widest layout, 200% zoom and dark mode
4. Every disabled control explains itself; every destructive action has Undo or a confirm
5. Every drag interaction has a keyboard and exact-input path
6. Forms validate on submit, focus the first invalid field and clear errors as they're fixed
7. Grouping uses space before lines; reading order matches importance; logical properties for direction-dependent layout
8. Focus is visible, every input has a label, status changes are announced, nothing relies on color alone
9. Copy follows MW Platform Design System v4 content rules (Title Case labels, sentence case bodies, no em dashes)
10. Nothing duplicates: one primary action, one place for each piece of information
