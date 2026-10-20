# Interaction Patterns

## Direct manipulation (tracks, timelines, boards, charts)

- **Pick, then act.** A brush or tool selection (radio group of chips) followed by a drag reads clearly and avoids mode confusion. Keep the selected brush visible.
- **Snap** to a meaningful unit (15 minutes for time) and store at a finer one (5 minutes) so exact edits and timers stay precise.
- **Show the result while dragging**: live preview plus a floating label with the exact value ("2:00 PM – 4:00 PM · 2:00").
- **Click versus drag**: under 4px of movement is a click. A click on an item opens its exact editor; a click on empty space adds a sensible default (one hour).
- **Edges resize, body paints.** Resize handles are at least 10px wide with a grip visible on hover and focus.
- **No impossible states.** Model data so conflicts can't exist (time as slots, later paint wins) rather than warning about them after the fact.
- **Keyboard twin.** Focusable items: arrow keys move the end, Shift plus arrows moves the start, Enter opens the exact editor, Delete removes. Plus an "Enter Times" path with plain fields.
- **Undo** via a visible button and Cmd/Ctrl+Z (outside text fields), with a history of at least 50 steps.
- **Touch**: `touch-action: pan-y` on horizontal tracks so vertical scrolling still works; the track gets its own horizontal scroll with a min width below 1024px.

## Forms

- Labels above fields, one column, optional fields marked "(Optional)".
- A field becomes optional when something else satisfies it (What Got Done is optional when a done To Do is tagged to that project); show that in the label.
- Validate on submit and on blur for format errors. Focus the first invalid field. Clear an error the moment it's fixed, without a re-render that steals focus.
- Typing never triggers a full re-render. Save drafts in the background.

## Overlays

- **Dialog** for short focused tasks (up to four fields) and confirmations that show a preview (Post Day shows exactly what will post).
- **Sheet** for reviewing or editing something while keeping page context (Review unposted days).
- **No modal for the main task.** If the page exists to do the task, do it on the page.
- Focus moves into the overlay, is trapped while open, and returns to the trigger on close. Escape closes.

## Feedback

- **Toast** (top right, 4 seconds, close button) confirms completed actions and offers Undo. Persistent toasts only for things the person must resolve.
- **Inline error** for anything fixable in a form.
- **Alert** for page conditions (earlier days unposted) with the fixing action inside it.
- **Live region** announcements for changes that happen without navigation (timer started, to do marked done and added to a project's YTB).

## Lists you check off

- Enter adds and keeps focus in the add field.
- Checking moves the item to the bottom with a line-through, focus stays on its checkbox.
- Item actions (tag a project, remove) in a trailing menu; removal gets Undo.
- Unfinished items carry forward with a visible marker.

## Read-only views

- Render text instead of disabled inputs.
- Hide personal tools that don't apply to the viewer.
- Say whose data it is in the header and in empty states.

## Posting and publishing flows

- Gate only the commit. Explain the gate in an Alert with the fix inside it.
- Preview exactly what will be shared in the confirm step.
- After publishing, edits mark the item changed and the primary becomes Update.
- Offer a copy-as-text option for where the content goes next (Copy YTB for Slack), with a fallback dialog if the clipboard is blocked.
