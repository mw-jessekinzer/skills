# Baserow Lead Capture — V0 Schema

Field lists below re-read from the live base on 2026-08-26. Two linked tables in database
`535262`, built from Baserow's CRM template and trimmed down. Companies is the parent;
Contacts hang off it.

Confirm with `~/.claude/scripts/baserow.sh schema <table_id>` at the start of a session.
This file goes stale the moment JK edits a field, and he edits fields.

## How to reach Baserow

Over the REST API, using `~/.claude/scripts/baserow.sh`. The Baserow MCP server is gone —
`mcp-remote` kept dropping its connection mid-task. The script reads a database token from
the macOS Keychain (`baserow-api-key`) and needs Bash with the sandbox disabled, since both
the Keychain read and its temp auth file are blocked inside the sandbox. Run the script with
no arguments for the command list.

Note that the MCP endpoint key and a database token are two different credentials. The MCP
key returns `401 ERROR_TOKEN_DOES_NOT_EXIST` against the REST API.

What the database token can and cannot do:

| Operation | Works with a database token? |
|-----------|------------------------------|
| Read schema, including exact select option strings and ids | Yes — verified |
| Read / create / update / delete rows | Yes — verified |
| Set a link field (`{"Company": [5]}`) | Yes — verified |
| Add a new field to a table | Per Baserow's OpenAPI spec, yes. Untested — do not try it without asking JK first |
| Edit or delete an existing field | **No** — JWT auth only |
| Create or delete a table | **No** — JWT auth only |
| Create a view | **No** — JWT auth only |

Structural edits are JK's job in the UI; data is this skill's job over the API.

---

## Table 1 — Companies (`1156883`)

`Name` is the primary field, so it is the row label everywhere.

| Field | Baserow type | Notes |
|-------|--------------|-------|
| Name | Single line text | Primary. Verified legal or trading name. |
| Industry | Single select | PropTech; FinTech; Automotive; Cloud Infra & Software; Faith and Flourishing; Sports; Logistics; Legacy Enterprise; Small Business |
| Website | URL | Full URL including scheme. The de-duplication key. |
| Contacts | Link to table → Contacts | Reverse side of `Contacts.Company`. |
| Notes | Long text | Company context, displaced Intent Proof URLs, anything that needs prose. |
| Size | Single select | 1 - 10; 11 - 50; 51 - 100; 101 - 500; 501 - 1000; 1K+ |
| Intent Signals | Multiple select | Hiring; Completed Funding Round |
| Intent Proof | URL | The single URL proving the intent signal. Holds one value. |
| Stage | Multiple select | Warm Up; Watching |
| In CRM | Multiple select | Yes; No |

Since the 2026-08-25 version of this file, `Address` has been removed and `Stage`, `In CRM`,
`Legacy Enterprise`, and `Small Business` have been added. `Stage` and `In CRM` are the
prospecting fields the `baserow-prospect-add` skill writes; that skill treats `In CRM` as
mandatory on every row.

`Industry` carries one known rough edge: `Automotive` is a leftover from the Baserow
template rather than a deliberate vertical. It does not block capture. Do not add options
without asking — it is a field edit, and those are JWT-only.

---

## Table 2 — Contacts (`1156884`)

`Name` is the primary field.

| Field | Baserow type | Notes |
|-------|--------------|-------|
| Name | Single line text | Primary. |
| Title | Single line text | Verified current title only. |
| Company | Link to table → Companies | Always set. Create the company row first. |
| Email | Email | Only if supplied or publicly published. Never a guessed pattern. |
| Phone | Phone number | Rarely available. Leave blank. |
| LinkedIn | URL | Full profile URL. Never guessed. |
| Company name | Rollup | `min(lookup('Company','Name'))`. **Read-only — never write to it.** |
| Notes | Long text | Dated prose: what happened, the source URL, the next step. |

**There is no `Status` field on Contacts as of 2026-08-26.** The V0 spec called for one
(`New`; `Working`; `Passed to Sales`; `Not a Fit`) and this file used to list it, but the
live table does not have it and a write to it fails with
`ERROR_REQUEST_BODY_VALIDATION`. Anything downstream that assumes `Status` — the Inbox view
below included — needs JK to add the field in the UI first.

### Notes format

A convention, not a constraint. Newest entry on top, one per encounter:

```
2026-08-25 — Commented on Ryan's post about contract-to-hire risk. Source:
https://linkedin.com/posts/... Next: reply to the comment, no pitch.
```

---

## Deliberately not in V0

Dropped from the original spreadsheet spec, each for a reason:

- `Owner` — single user, so assignment is noise.
- `ICP Fit` and `Likely Need` — both are properties of the company, not the person, and
  both invite a confident-sounding guess on thin evidence. Revisit when there is enough
  volume that triage actually costs time.
- `Lead Source`, `Source URL`, `Lead Signal`, `Next Step`, `Date Added` — collapsed into
  `Contacts.Notes` as prose. Nine fields with five blanks kills the capture habit faster
  than prose does.
- `HubSpot Company ID` / `HubSpot Contact ID` — nothing syncs yet, so the placeholders
  would sit empty.
- A date field. There is no `Created on` or `Date Added` field on either table, which
  means **an Inbox view cannot sort by newest.** Adding a `Created on` field fixes it and
  costs nothing at capture time, since Baserow fills it automatically.

---

## Views

View creation is JWT-only, so none of these can be built over the API. JK builds them once
in the UI.

- **Inbox** — Contacts grid. Blocked until a `Status` field exists. Filter: `Status` is not
  `Passed to Sales`, and `Status` is not `Not a Fit`. That one filter catches `New`, `Working`, and blank, so nothing hides.
  This is the daily working view.
- **Capture form** — Contacts form view. Expose in this order: `Name`, `Company`, `Title`,
  `LinkedIn`, `Notes`. Leave `Status` off the form so there is nothing to decide on submit.
  If the `Company` form field offers row creation, enable it; if not, the form captures
  the person and the company gets attached afterward.
- **By Company** — Companies grid, default view. Expanding a row shows its linked contacts.

---

## HubSpot mapping — parked, not active

Real values from the live Midwestern portal, not defaults. The `lifecyclestage` picklist
is customized there, so the generic stage names do not apply. Kept here because it was
expensive to establish, not because anything uses it yet.

| Intent | HubSpot property | Value |
|--------|------------------|-------|
| Ready to hand off | `hs_lead_status` | `New Marketing Lead` |
| Ready to hand off | `lead_generated_by` | `Marketing` |
| Handed off | `lifecyclestage` | `subscriber` (label: "Contacted") |
| Nurture | `lifecyclestage` | `51571792` (label: "Marketing Cultivation") |
| Closed out | `hs_lead_status` | `UNQUALIFIED` |

`lead_generated_by = Marketing` is the only attribution signal that holds up in this
portal, so it gets set on every contact if and when a push is built.

Nothing syncs automatically. The push would be a separate, deliberate step.
