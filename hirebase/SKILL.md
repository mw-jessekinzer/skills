---
name: hirebase
description: Query the Hirebase Jobs API for hiring-intent data on named accounts — open engineering role counts, posting recency, and cold/warm/hot intent scoring. Use when enriching an account list with hiring signal, checking whether a company is actively hiring engineers, comparing hiring-intent coverage against TheirStack, or answering "is this account hiring right now". Triggers on "hiring intent", "are they hiring", "enrich this account list", "engineering hiring signal", "hirebase", "job posting data". Do NOT use for recruiting candidates, sourcing people, or job-seeker workflows.
---

# Hirebase — hiring-intent data

Hirebase indexes job postings from 300k+ company career pages and 80+ ATS
platforms (Greenhouse, Lever, Workday, iCIMS), refreshed 12–24 times a day.
For Midwestern, it's a buying signal: an account posting engineering roles has
an engineering capacity gap, which is what Scoped and Embedded sell into.

It sits alongside TheirStack in the hiring-intent layer described in
`0_Marketing GIT/0_Marketing Hub/3_Execution/Tooling/Hiring-Intent Data Layer — Provider Comparison.md`.

## The client

Everything goes through `~/.claude/scripts/hirebase.sh`. Do not hand-roll curl
calls — the script handles key retrieval, keeps the key out of `ps` output,
reports credit usage, and enforces the API's limits.

The key lives in the macOS Keychain as `hirebase-api-key`. Keychain reads fail
silently under the Bash sandbox, so **run this script with
`dangerouslyDisableSandbox: true`**.

```bash
~/.claude/scripts/hirebase.sh quota      # free
~/.claude/scripts/hirebase.sh params     # full parameter reference, free
~/.claude/scripts/hirebase.sh categories # valid job_category / industry values, free
```

## Billing — the thing that governs every decision here

**One credit per job row returned, not per API call.** The plan is 500 credits
a month with `overage-mode: block`, so it hard-stops rather than billing over.

| Call | Cost |
|---|---|
| `limit=50` | 50 credits |
| `limit=1` | 1 credit |
| any query matching zero jobs | 0 credits |
| `quota` | 0 credits |

Consequences that should shape every query you write:

- **Never use `limit=50` to explore.** Use `limit=1` unless you actually need
  the rows. Learning the shape of a response costs the same as one row.
- `total_count` in the response is the full match count regardless of how many
  rows you asked for. **One credit buys both the count and, from the single
  returned row, the most recent posting date.** That pair is the entire intent
  signal, so `count` is the workhorse and it costs 1.
- Companies Hirebase has never indexed return zero rows and cost nothing, so a
  bulk enrich only bills for accounts that actually matched.
- Rate limit is 100 requests/minute. The script sleeps 0.7s between calls in
  `enrich` and `roles`.

Check `quota` before any bulk run. The script prints remaining credits after
every command.

## Commands

### count — 1 credit, the default move

```bash
~/.claude/scripts/hirebase.sh count --company "Acme" --category "Software Engineer Jobs"
```

Returns match count, company count, most recent posting date and days since.
This answers "are they hiring engineers, and how recently" for one credit.

### enrich — 1 credit per matched company

```bash
~/.claude/scripts/hirebase.sh enrich --file accounts.txt --out enriched.csv
```

One company name per line (a CSV works if the name is the first column; `#`
comments and blank lines are skipped). Defaults to `Engineering Jobs`. Outputs
`company, matched_name, eng_open, latest_eng_post, days_since, signal`.

Signal thresholds, all tunable with `--hot-count` / `--hot-days` / `--warm-days`:

- **hot** — 3+ open eng roles and posted within 14 days
- **warm** — 1+ open eng role and posted within 45 days
- **cold** — indexed, but stale or thin
- **no-match** — not in the index at all (see the coverage warning below)
- **error** — the call failed; retry that row

`--with-total` adds all-department open roles for context and doubles the cost.

### roles — 1 credit per row

```bash
~/.claude/scripts/hirebase.sh roles --company "Acme" --category "Engineering Jobs" \
  --limit 25 --since 2026-08-01
```

Pulls actual listings. `--limit` caps at 50 (API limit); total cost is
`limit × pages`. `--since` works client-side: results come back newest-first,
so the script stops paging once a page ends older than the cutoff. Add `--json`
for full records.

### search — raw passthrough

```bash
~/.claude/scripts/hirebase.sh search '{"keywords":["kubernetes"],"industry":"Finance","limit":5}'
```

Accepts `@path/to/body.json`. Use it for anything the wrappers don't cover.

## Limitations that will bite you

**No domain filter.** Hirebase keys companies by name and slug only. An account
list keyed on domain needs a company-name column before it can be enriched.
Name matching is exact (though case-insensitive), so trading-name mismatches
silently return `no-match`.

**Coverage is real but not universal.** Verified 2026-08-26: Plaid returns zero
results under `Plaid`, `plaid`, `Plaid Inc.`, and `Plaid Technologies`, despite
being a well-known fintech that posts constantly. **`no-match` means "not
indexed", not "not hiring."** Never report a no-match as evidence an account
isn't hiring — cross-check against TheirStack or the company's careers page
before drawing a conclusion. Any campaign built on Hirebase data should measure
its own hit rate against the target list first.

**Category tagging is loose.** Verified 2026-08-26: a `Software Engineer Jobs`
query against Stripe returned "Senior Account Executive, AI Sales" and "Product
Manager, Sail Core" in the top three. Categories are AI-assigned and
over-inclusive. For a defensible engineering-capacity signal, combine the
category with `--title` filters, or pull rows with `roles` and filter on
`job_title` yourself. Raw category counts overstate engineering hiring.

**`date_posted` is an exact single day**, not a range. There is no
since/until filter. Get recency from `count`'s latest-posting field, or use
`--since` on `roles`.

**No company-search endpoint.** `/v2/companies/*` returns 404. Jobs search with
a company filter is the only path to company data, though each job carries a
`company_data` block (industries, subindustries, size_range, type, LinkedIn URL,
description summary).

## Hirebase vs TheirStack

Both are job-posting intent sources; they are not redundant, they have
different coverage. TheirStack (MCP: `mcp__theirstack__search_jobs`) bills per
job and per company and supports company-domain filtering, which Hirebase does
not. Hirebase's free zero-match queries and per-row billing make wide, shallow
counting cheap.

Practical split: use **Hirebase `count`/`enrich`** for cheap breadth across a
named list, and **TheirStack** when you need domain-keyed lookups or a second
opinion on a company Hirebase reports as no-match. Never treat either as
complete on its own — the open question in the provider-comparison brief is
coverage of Midwestern's specific small-company targets, and it is still open.

## Reporting rules

When reporting intent findings, always state the credit cost of the run and
separate `no-match` from `cold`. Those mean different things and conflating
them turns a data gap into a false negative about an account.
