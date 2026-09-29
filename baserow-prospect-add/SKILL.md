---
name: baserow-prospect-add
description: Use when JK pastes a company website, careers board, or LinkedIn profile and wants it added to the Baserow prospecting table — "add this company to baserow", "add them as a warm up company", "new prospect", "put this contact in", "pull the hubspot contacts in too". Also use when refreshing or correcting a company or contact row that already exists in that table. Do NOT use for HubSpot-only work, ICP research, or general company research with no Baserow write.
metadata:
  author: JK
  version: 2.1.0
---

# Baserow Prospect Add

Adds a company and its contacts to JK's Baserow prospecting table, enriched from the same sources every time so rows are comparable to each other.

**Core principle: a row is a handoff to a salesperson, not a bookmark.** Every field either carries a verified fact or says plainly that the fact is missing. Never write a guess as though it were verified, and never leave the reader wondering where a number came from.

## Reaching Baserow

Use the REST client at `~/.claude/scripts/baserow.sh`. The Baserow MCP server was removed because `mcp-remote` dropped its connection mid-task; the script talks straight to `https://api.baserow.io/api/` with a database token pulled from the macOS Keychain (`baserow-api-key`), falling back to `$BASEROW_API_KEY`.

**Every call needs Bash with the sandbox disabled.** The Keychain read and the temp file that carries the auth header are both blocked inside the sandbox, and the failure surfaces as `mktemp failed`, not as a permissions message.

```bash
~/.claude/scripts/baserow.sh check 1156883 1156884      # confirm the token still has access
~/.claude/scripts/baserow.sh schema <table_id>          # fields, types, exact select options
~/.claude/scripts/baserow.sh schema <table_id> --raw    # full JSON, including select option ids
~/.claude/scripts/baserow.sh rows <table_id> --search "Acme"
~/.claude/scripts/baserow.sh rows <table_id> --filters '<filter tree JSON>'
~/.claude/scripts/baserow.sh row <table_id> <row_id>
~/.claude/scripts/baserow.sh create <table_id> '<json>'
~/.claude/scripts/baserow.sh update <table_id> <row_id> '<json>'
~/.claude/scripts/baserow.sh batch-create <table_id> '<json array>'
~/.claude/scripts/baserow.sh batch-update <table_id> '<json array>'   # each item carries its "id"
~/.claude/scripts/baserow.sh delete <table_id> <row_id> --yes
```

Any JSON argument also accepts `@path/to/file.json`, which is the sane way to pass a long Notes field without fighting shell quoting. Writes use `user_field_names`, so bodies are keyed by field name: `{"Name":"Acme","Industry":"PropTech","Stage":["Warm Up"],"Contacts":[42]}`. Single and multiple selects take the exact option string, link-row fields take an array of row ids.

The script exits non-zero and prints the HTTP status plus Baserow's error body on failure, so a rejected write is loud rather than silent. Pipe output through `jq` to keep responses small.

## The two tables (database 535262)

| Table | ID | Primary field |
|---|---|---|
| Companies | `1156883` | Name |
| Contacts | `1156884` | Name |

**Companies fields.** `Name` (text), `Website` (url), `Industry` (single select), `Size` (single select), `Intent Signals` (multi select), `Intent Proof` (url), `Stage` (multi select), `In CRM` (multi select), `Notes` (long text), `Contacts` (link to Contacts).

**Contacts fields.** `Name` (text), `Title` (text), `Company` (link to Companies), `Email`, `Phone`, `LinkedIn` (url), `Notes` (long text). `Company name` is a rollup — never write to it.

**Exact option strings** (Baserow rejects near-misses):

- Industry: `PropTech` · `FinTech` · `Automotive` · `Cloud Infra & Software` · `Faith and Flourishing` · `Sports` · `Logistics` · `Legacy Enterprise` · `Small Business`
- Size: `1 - 10` · `11 - 50` · `51 - 100` · `101 - 500` · `501 - 1000` · `1K+` (note the spaces around the hyphens)
- Intent Signals: `Hiring` · `Completed Funding Round`
- Stage: `Warm Up` · `Watching`
- In CRM: `Yes` · `No`

Run `schema` on both tables at the start of a run anyway — JK adds options, and a stale option string now fails the write outright: `ERROR_REQUEST_BODY_VALIDATION`, "The provided select option value '51-100' is not a valid select option." That is a feature. A near-miss can no longer sneak through as a blank field.

**Filters are the exception, and they fail quietly.** A filter tree matches select fields by option *id*, not by name, and a name in the `value` slot returns zero rows with a 200 status instead of an error. Get the ids from `schema <table_id> --raw` and read a zero-row result as suspect until you have checked them:

```bash
~/.claude/scripts/baserow.sh schema 1156883 --raw | jq -r '.[] | select(.name=="Stage") | .select_options[] | "\(.id) \(.value)"'
~/.claude/scripts/baserow.sh rows 1156883 --filters '{"filter_type":"AND","filters":[{"field":"Stage","type":"multiple_select_has","value":"7395425"}],"groups":[]}'
```

For finding one company, `--search` is simpler and matches on text, so prefer it over a filter tree.

## Workflow

1. **Check Baserow first.** `rows 1156883 --search "<company name>"`. A hit means this is an update, not an add — see Updating below.
2. **Check HubSpot.** `search_crm_objects` on `COMPANY` with the domain as query. If a record exists, also pull its contacts: `search_crm_objects` on `CONTACT` with `filterGroups: [{associatedWith: [{objectType: "companies", operator: "EQUAL", objectIdValues: [<id>]}]}]`, properties including `jobtitle`, `email`, `mobilephone`, `phone`, `lifecyclestage`, `hubspot_owner_id`, `notes_last_contacted`. Resolve the owner id with `search_owners`.
3. **STOP if the company is already owned in HubSpot.** Report the owner, lifecycle stage, last-touch date, and contact count, then wait. JK decides whether the company belongs in the prospecting table at all. Do not write any row before he answers.
4. **Read the careers board and the website, and run the discontinuity check.** See Enrichment sources for which URL forms actually return data, and Discontinuity check for the one search that decides whether the facts on file still describe this company.
5. **Ask before spending TheirStack credits.** The balance runs low and a failed call still costs a round trip. Say what the call will buy (headcount, funding total, 180-day posting volume) and what it costs, then wait.
6. **Ask which Stage.** `Warm Up` or `Watching`. Ask every time, even when JK's message said "warm up" — confirm rather than infer, it is one word of friction.
7. **Write the company row** with `create 1156883`, read the `id` off the response, then write the contact rows with `Company: [<company row id>]`. Link by row id, not by name; two rows can share a name. Several contacts go in one `batch-create` call.
8. **Report in the terminal.** Row IDs, the facts written, and an explicit list of what could not be verified. Nothing gets written to the vault.

## Enrichment sources

| Source | Call | Gotcha |
|---|---|---|
| Ashby careers board | WebFetch `https://api.ashbyhq.com/posting-api/job-board/<board-slug>` | The human-facing `jobs.ashbyhq.com/<slug>` page is JavaScript-rendered and fetches empty. The posting API returns clean JSON with titles, locations, and departments. |
| TheirStack | `search_jobs` with `company_domain_or: ["<domain>"]`, `posted_at_max_age_days: 180`, `include_total_results: true`, **`limit: 1`** | Credits are charged per job returned, so `limit: 1` costs one credit and still returns the full `company_object`: `employee_count`, `total_funding_usd`, `funding_stage`, `linkedin_url`, `city`, `num_jobs_last_30_days`. `metadata.total_results` gives the 180-day posting count. A larger limit blows past the token cap and lands in a temp file. |
| Workday careers board | `curl -s -X POST 'https://<tenant>.wd5.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs' -H 'Content-Type: application/json' -d '{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}'` | Same trap as Ashby: the human-facing board is JavaScript-rendered and WebFetch returns an empty page. The JSON endpoint returns `total` plus a `jobPostings` array of title, `locationsText`, and `postedOn` (a relative age like "Posted 23 Days Ago", which caps at "30+ Days Ago"). This needs Bash because WebFetch cannot POST. The tenant and site come straight out of the pasted URL: `23andme.wd5.myworkdayjobs.com/23` means tenant `23andme`, site `23`. Pipe through `python3 -c` or `jq` to list roles without dumping the whole payload. Other subdomains exist (`wd1`, `wd3`, `wd5`, …) — use whichever the pasted URL uses. |
| Company website | WebFetch the homepage | Marketing pages carry customer logos, funding claims, and product framing. They rarely state headcount or HQ. |
| LinkedIn profile | WebFetch the profile URL | Returns partial data; titles are often missing behind the sign-in wall. When the fetched name disagrees with the URL slug, confirm with WebSearch and record both. |

## Field rules

**Size** maps from employee count: 174 → `101 - 500`, 64 → `51 - 100`. When headcount is unknown, leave Size blank and say so in Notes rather than eyeballing it.

**Industry** takes the closest option and flags the compromise in Notes. An insurtech AI company became `FinTech`; a user-research SaaS became `Cloud Infra & Software`. Both rows say in Notes that the label is approximate and why. Never invent an option.

**Intent Signals.** Tag `Hiring` when there are live roles. Tag `Completed Funding Round` **only for a dated round inside the last 6 months** — a large total raised with no round date does not qualify, and Notes should say why the tag was withheld.

**Intent Proof** points at the live roles a salesperson can actually open: the careers board or ATS URL. When JK's pasted link is a marketing page that only links onward to the board, use the board and record both URLs in Notes.

**In CRM** is `Yes` or `No` based on step 2, never left blank.

## Discontinuity check

Run one search on the company name plus the current year before writing the row. If the results or the company's own site mention **bankruptcy, Chapter 11, acquisition, merger, spin-off, take-private, rename, domain change, mass layoff, or nonprofit conversion**, the company on file is not the company that exists today, and the row has to say so.

When that fires:

- **The discontinuity paragraph goes second in Notes**, immediately after what the company does, before funding or hiring. Give the sequence with dates and dollar figures, name the acquirer or new parent, and say in one sentence what kind of buyer this now is.
- **Every pre-event number is suspect.** Headcount, funding total, and revenue on file may describe the old entity. Leave `Size` blank rather than banding from a pre-event figure, and say in Notes which figures predate the event.
- **An acquisition price is not a funding round.** No `Completed Funding Round` tag for a purchase price, a debt facility, or a bankruptcy sale, however large and however recent.
- **A `.org` domain, a renamed entity, or a careers board on a different name is the tell.** Chase it rather than assuming a typo. The pasted URL is what JK saw; the entity behind it may have a different name, and the row's `Name` should be the entity that exists now.

Worked example: `23andme.org` is not a typo for `.com`. 23andMe filed Chapter 11 in March 2025, Anne Wojcicki's nonprofit TTAM Research Institute bought the assets for $305M over Regeneron's $256M, and the surviving entity is 23andMe Research Institute, a nonprofit public benefit corporation. Every headcount figure in circulation predates that, so Size stayed blank.

## Notes format

Notes are prose written for another person to read, not compressed shorthand. Open with the date and how the company arrived (`2026-08-26: Added by JK as a Warm Up target.`), then short paragraphs covering: what the company does and who it sells to; any discontinuity in its recent history, second and before anything else, whenever the check above fired; funding and investors; the hiring signal with counts, locations, and named roles; careers board and company LinkedIn URLs; CRM status including owner and last-touch date; and any field compromise with its reasoning.

State the provenance of every number in the sentence that uses it — "59 postings in the last 180 days (TheirStack)" — and name contradictions instead of resolving them silently. When a company's own job copy claims under 150 people and the data says 174, write both.

## Contacts

Add the contact JK pastes, plus every HubSpot contact already associated with the company, in the same pass. Those are already his records and cost nothing to fetch.

Two recurring traps:

- **A phone number repeated across every contact at a company is the main line, not a direct dial.** Put mobiles in `Phone`, leave `Phone` empty when the shared number is all there is, and record that number in Notes as the company line.
- **A LinkedIn slug that disagrees with the profile name usually means a name change.** File the current name, keep the slug JK gave in the `LinkedIn` field, and note the mismatch so nobody thinks it is the wrong person.

Copy HubSpot job titles verbatim even when they read like LinkedIn headlines, and flag in Notes that the title needs confirming rather than cleaning it up into something the CRM does not say.

## Updating an existing row

Never create a second row for a company already in the table. `update <table_id> <row_id>` on the existing row: refresh stale fields, append a new dated entry to the end of Notes rather than replacing what is there, and add contacts that are missing. A `PATCH` only touches the keys you send, so omitted fields are safe — but Notes is replaced wholesale by whatever you send, so read the current Notes with `row` first and send the old text plus the new entry. Say in the report which fields changed and which were left alone.

## Common mistakes

- Writing the row before JK answers the HubSpot-owner question or the Stage question.
- Reading a zero-row filter result as "not in the table" when the filter matched a select option by name instead of by id.
- Linking a contact to a company by name when a row id is available.
- Sending a Notes update without the existing Notes text, which replaces the row's history instead of appending to it.
- Running the script through sandboxed Bash and reading `mktemp failed` as a Baserow problem.
- Calling TheirStack with the default `limit: 25`, which costs 25 credits and overflows into a temp file.
- Fetching `jobs.ashbyhq.com/<slug>` or the human-facing Workday board instead of the JSON endpoint, and concluding the company has no open roles.
- Banding `Size` from a headcount figure that predates a bankruptcy, layoff, or acquisition.
- Reading an odd domain, a renamed entity, or a mismatched careers board as sloppiness rather than as a discontinuity worth one search.
- Compressing Notes into fragments. The conversation gets compressed; the row does not.
