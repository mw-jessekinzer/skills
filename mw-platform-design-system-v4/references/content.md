# MW Platform Design System v4 Content

Applies to the Midwestern Platform and internal product UI only. Marketing and brand output follow the brand guidelines (sentence case everywhere). Both are correct in their own context.

---

## 1. Case

### Title Case
Use for short UI labels that name things:
- Page titles, section headings, card titles, dialog and sheet titles
- Buttons and links that act as buttons ("Save Changes", "View Full Report")
- Navigation items and sidebar group labels ("Daily Log", "Big Board", "Overview")
- Tabs, segmented controls, menu items, select options
- Form field labels and legends ("Street Address", "Public Email")
- Table column headers, badges, tags, stat labels ("Upcoming", "Auto-Save Plan")
- Toast and alert titles ("Profile Saved")
- Empty state titles ("No Team Members")

Title Case style: capitalize every word except articles, short conjunctions and short prepositions (a, an, the, and, but, or, for, of, to, in, on, at, by, with) unless they're the first or last word. "Scan to Connect Your Mobile Device", "Add Members to Your Workspace".

### Sentence case
Use for anything that reads as a sentence:
- Card and page descriptions, helper text, field descriptions
- Body copy, empty state explanations, alert and toast bodies
- Error messages, tooltips longer than a label, confirmation dialog descriptions
- Placeholders with example content ("Brief description of the issue")

### Never all caps
No `uppercase` class, no typed caps, no wide letter-spaced eyebrows. Mira examples ship labels like "UPCOMING", "RETIREMENT", "VALUE", "OPEN / CLOSE"; convert them to Title Case ("Upcoming", "Retirement", "Value") at normal tracking, and remove any `tracking-wide`/`tracking-wider` that came with them.

Exceptions: true acronyms and product names keep their own form (API, URL, PDF, MW, EBU, Leapsome, iOS). Ticker symbols and codes inside code snippets stay as written.

---

## 2. Voice

Clear, warm and direct, in line with Midwestern's Code of Service (Delivery Excellence, Service From a H.E.A.R.T. of Care, Surprise & Delight):
- Say what happened and what to do next. Short sentences.
- Address the user as "you". Use "we" for Midwestern sparingly.
- No blame in errors ("We couldn't save your changes", not "You entered an invalid value").
- Moments of delight belong in empty states, completions and milestones, never in errors or destructive confirmations.

## 3. Buttons and actions

- Start with a verb: Create, Save, Invite, Export, Delete, Submit.
- Be specific: "Invite Members" beats "Submit". "Delete Project" beats "Confirm".
- Destructive confirm buttons repeat the action from the title.
- Avoid "Click Here", "OK", "Yes/No".

## 4. Errors and validation

- Field errors: what's wrong and how to fix it, sentence case, no trailing period for fragments ("Enter an email address like name@midwestern.com").
- Page or region errors: what failed, why if known, and a Retry action.
- Never show raw error codes alone; put them in a details disclosure if needed.

## 5. Empty states

Title (Title Case) + one sentence (sentence case) + action. "No Daily Logs Yet" / "Log your first day to start tracking your hours and highlights." / "Create Log".

## 6. Numbers, dates and times

- The `num` utility (tabular figures plus tracking) for anything that aligns or updates.
- Currency: `$1,250.00` in tables, `$1.2K` style abbreviations only in compact KPI contexts.
- Dates: "Oct 7, 2026" in UI, "October 7, 2026" in headings and descriptions, relative ("2h ago", "Yesterday") for recent activity with the full date in a tooltip.
- Times: "9:00 AM". Durations: "3h 48m".
- Percentages: no space ("31%"). Deltas carry a sign ("+42%", "-6.50").

## 7. Punctuation

- No periods on labels, titles, buttons or single-fragment helper text. Full sentences in descriptions and bodies take periods.
- No em dashes in UI copy. Use a period, comma or colon.
- Use the ellipsis character only for truncation and in-progress states ("Saving…").
