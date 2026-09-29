---
name: lead-capture
description: Use when JK passes a lead to be captured into the Baserow lead-capture tables — a name, company, URL, form response, referral note, LinkedIn interaction, RB2B website visit, or a screenshot of any of those. Researches public facts, finds or creates the company, writes the contact row linked to it, and reports what was written. Triggers on "capture this lead", "log this lead", "add this to Baserow", "new lead", "here's a lead", "who is this", or a bare name/company/URL pasted with capture intent. Do NOT use for bulk cold-prospect list building, hiring-intent scoring, ICP research runs, or anything that writes to HubSpot.
---

# Lead Capture

Turn a sparse, messy lead signal into clean rows in Baserow. Company first, contacts
grouped under it.

This exists to build the habit of capturing leads consistently. Speed matters more than
completeness. A row with four verified fields beats a row with nine fields where five
were guessed.

## Config

| Setting | Value |
|---------|-------|
| Database ID | `535262` |
| Companies table ID | `1156883` |
| Contacts table ID | `1156884` |

Every read and write goes through `~/.claude/scripts/baserow.sh`, a thin client over
Baserow's REST API. It replaced the Baserow MCP server, which dropped connections
mid-task. Run it with no arguments for the command list, and note that it needs Bash with
the sandbox disabled — the Keychain token read is blocked otherwise.

It covers row create/read/update/delete and schema read, which is everything this skill
needs. It cannot create tables, edit fields, or create views — if a field appears to be
missing, tell JK rather than working around it.

Field definitions and controlled values live in `references/baserow-schema.md`. Read it
before the first write of a session.

## The loop

1. JK pastes whatever he has.
2. Resolve identity. If the company or person cannot be uniquely identified from what
   was given, ask one concise clarifying question. One, not a list.
3. Research public sources for the missing fields. Company site, LinkedIn, the source
   page itself.
4. Find or create the company row.
5. Create the contact row linked to it. Skip this for company-only leads.
6. Report back: what was written, what was left blank, and what needs review.

## Find or create the company

Always check before creating. Duplicate companies break the grouping, which is the whole
point of this structure.

Run `baserow.sh rows 1156883 --search "<company name>"`, then again with the bare domain.
Match in this order:

1. Normalized domain — strip scheme, `www.`, path, and trailing slash. `Acme.com/careers`
   and `https://www.acme.com` are the same company.
2. Exact name, case-insensitive.
3. Name minus the legal suffix (Inc, LLC, Ltd, Co, Corp).

On a match, update the existing row rather than creating a second one. Only fill fields
that are currently blank. Never overwrite a value JK set by hand.

No match means create the company, then create the contact.

## Find or create the contact

Same discipline. Match on email first, then LinkedIn URL, then name plus company. A
person who surfaces from a second source gets their existing row updated and the new
signal appended to their Notes with its date — not a duplicate row.

## Where the signal goes

There is no dedicated Lead Source, Source URL, Lead Signal, or Next Step field. This is
deliberate for V0: fewer fields means fewer blanks to stare at, and prose holds a messy
signal better than a picklist that has to be maintained.

**Company-level intent** goes in the two structured fields. `Intent Signals` is a
multi-select (`Hiring`, `Completed Funding Round`) and `Intent Proof` is the single URL
that proves it. `Intent Proof` holds one URL, so a newer, stronger proof replaces an
older one — move the displaced URL into `Companies.Notes` with its date rather than
losing it.

**Person-level signal** goes in `Contacts.Notes` as dated prose. Lead with the date, then
what happened, then the next step. One entry per encounter, newest at the top:

```
2026-08-25 — Commented on Ryan's post about contract-to-hire risk. Source:
https://linkedin.com/posts/... Next: reply to the comment, no pitch.
```

That format is a convention, not a schema. Keep it readable over strict.

## Status

`Contacts.Status` is the only workflow field, and it is what makes the Inbox view work.
Set it honestly:

- `New` — captured, not yet looked at by a human
- `Working` — JK is actively doing something with it
- `Passed to Sales` — handed off
- `Not a Fit` — closed out

Default every new capture to `New`. Never set `Working` or `Passed to Sales` on JK's
behalf; those are his calls to make. If identity, fit, or source is materially uncertain,
still use `New` and say so plainly in the report and in Notes.

## Non-negotiables

- **Never invent a company, title, email, LinkedIn URL, industry, or source.** Leave
  fields blank when unknown. A blank is honest; a plausible guess is a landmine that
  reads as verified six weeks later.
- **Never infer an email pattern.** `first.last@company.com` is a guess, not a fact. An
  email goes in only when JK supplied it or an authoritative public source publishes it.
- **Preserve the original signal URL.** The post, form, or thread is the evidence. Do not
  replace it with a homepage.
- **Never write to `Company name`.** It is a rollup field, computed from the link. Baserow
  will reject the write.
- **Never contact the lead** and never write to HubSpot from this skill.

## Writing the rows

Get the real date from the environment context, never from memory.

Link fields take an array of row IDs: `{"Company": [42]}`.

Multi-selects take an array of option values: `{"Intent Signals": ["Hiring"]}`. Only the
options that already exist are valid — a new option needs a field edit, which this skill
cannot do.

`Industry` and `Size` are single selects. Fill them only when public sources make the
answer obvious. Both are nice-to-have; neither is worth a research detour.

## Reporting back

After writing, give JK:

- One line per row written or updated, with the Baserow row ID.
- Every field left blank and why.
- Anything uncertain, and what would resolve it.

Keep it short. Do not restate the whole row back to him.

## When Baserow is unreachable

The base can change under you — tables get renamed, fields get added. Every failure prints
the HTTP status and Baserow's own error body, so read that before guessing:

- `401 ERROR_TOKEN_DOES_NOT_EXIST` — the token is missing, revoked, or the Keychain entry
  is gone. Ask JK to re-add it; do not try to work around it.
- `404` on a table id — the table was renamed or deleted, or the token lost access to it.
  `baserow.sh check 1156883 1156884` confirms which tables the token can still reach. The
  ids above may be stale.
- `400 ERROR_REQUEST_BODY_VALIDATION` — usually a select option string that does not match
  exactly, or a write to a field that does not exist. Re-read the schema.
- `mktemp failed` — the call ran through the sandbox. Re-run it with the sandbox disabled.

If a write genuinely fails, do not silently drop the lead and do not claim it was saved.
Report the failure, output the row as a TSV block so it can be pasted manually, and say
plainly that the row still needs to be written.

## Out of scope

Bulk list building, cold prospecting, hiring-intent scoring, ICP research across a
vertical, and any write to HubSpot. The HubSpot push is a separate, deliberate step; the
mapping is parked in `references/baserow-schema.md` but nothing syncs from here.
