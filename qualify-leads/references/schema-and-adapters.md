# Canonical schema, source adapters, and work files

## Run folder

```
1_Projects/Lead Triage/<YYYY-MM-DD> <Source label> Lead Qualification/
  00 - Summary.md
  <YYYY-MM-DD> <Source label> Leads.csv
  <YYYY-MM-DD> hubspot-import.csv
  cost-ledger.csv
  Packets/<Company> - Lead Packet.md
  work/   (every intermediate file below)
```

Nothing else in the vault changes except one bullet in `1_Projects/Lead Triage/00 - readme.md` and the vendor rows appended to `1_Projects/Lead Triage/vendor-ledger.csv`.

## Work files

| File | Written by | Schema |
|---|---|---|
| `work/run.json` | `normalize.py`, `ledger.py`, `label.py --freeze-tier1` | as_of, source label, counts, date profile, caps, balances, tier1_frozen |
| `work/00-run-log.md` | every script, plus the runner | "Counts" lines from scripts; the runner adds "## Rulings", "## Commands" (every vendor and CRM call), "## Notes" |
| `work/01-canonical.csv`, `work/01-dupes.csv` | `normalize.py` | below |
| `work/02-pass1.csv`, `work/02-companies.csv`, `work/02-batch-*.csv`, `work/02-prior-companies.csv` | `classify.py` | columns printed at the top of `classify.py` |
| `work/03-research-companies-<batch>.csv`, `work/03-research-people-<batch>.csv` | research workers | `research-brief.md` |
| `work/03-triage-<batch>.csv` | triage workers | `research-brief.md` |
| `work/04-crm-companies.csv`, `work/04-crm-contacts.csv` | `hubspot-analyst` | `qualify-again.md` |
| `work/overrides.csv` | adjudicator and reviewer | `qualify-again.md` |
| `work/05-qualified.csv`, `work/05-company-rollup.csv`, `work/05-changes.csv` | `label.py` | columns at the top of `label.py` |
| `work/06-tier1.csv` (then `06-tier1-candidates.csv`) | `label.py` | columns at the top of `label.py`, including `packet_file` and scaled budget projections |
| `work/06-enrich-skipped.csv` | the runner (`append_row.py skip`) | `company_key_final, reason`: Tier 1 companies deliberately not enriched |
| `work/07-committee-<company>.csv`, `work/07-crm-committee.csv` | enrichment workers, `hubspot-analyst` | `enrichment-playbook.md` |
| `work/07-bounceban.csv` | the runner, after the one bulk call (`append_row.py bounceban`) | `email, bounceban_result, score, bulk_id` |
| `work/08-summary.json`, `work/08-committee-status.csv` | `assemble.py` | read them, don't hand-edit |
| `work/09-review.md` | reviewer | `quality-gates.md` |

Batch names tie outputs to inputs: `02-batch-deep-1.csv` must come back as `03-research-companies-deep-1.csv` plus `03-research-people-deep-1.csv`; `02-batch-triage-1.csv` as `03-triage-triage-1.csv`; `02-batch-keep-1.csv` as `03-research-companies-keep-1.csv` plus people. `checks.py` gate 1 compares the key sets.

## Canonical lead row (`work/01-canonical.csv`)

One row per person per run; company-only records are a row with no person. Repeat touches by one person merge into one row (merge key: LinkedIn URL, then email, then name plus company key; company-only rows merge on company key). The kept `lead_id` is the earliest touch, `touch_date` the newest, `touch_count` the sum, and every merge is a line in `01-dupes.csv`. Source rows in the window always equal canonical rows plus merged rows.

Overlapping inputs (two exports, overlapping Baserow pages) repeat a record id: the first copy is kept and the repeats are logged in `01-dupes.csv` as "repeat of the same record id" (not counted as merges). Two CSV inputs that share a file name get the parent folder name in their lead ids so they never collide.

Options on every adapter: `--since` / `--until` take a date (whole day) or a full timestamp (`2026-09-25T19:41:04Z`, compared on `touch_ts`); `--exclude-prior <run folder> [...]` skips lead ids already in those runs (new since last run; counted in `run.json` as `excluded_prior`; the flag needs at least one folder, and a run where every row is excluded or outside the window stops with a clear message and writes nothing); `--test-run` marks the run so later `--prior-dir` scans ignore it (folders named "... test run ..." are ignored too).

| Field | Notes |
|---|---|
| `lead_id` | `<source_system>:<record id>`; stable across reruns; first column of every row-level file |
| `source_type` | `rb2b_visit`, `social_engagement`, `campaign_list`, `other_list` |
| `source_system`, `source_record_id`, `source_file`, `source_detail` | RB2B: page path. Social: engagement summary. Campaign: the campaign name |
| `touch_type` | `page_view`, `reaction`, `comment`, `reply`, `form_fill`, `event_registration`, `event_attended`, `content_download`, `list_member`. Declared by the adapter, never guessed |
| `touch_date`, `touch_ts`, `touch_date_basis` | `touch_ts` is the full UTC timestamp when the source has one; basis `event_time`, `observed` (seen by our scraper), `post_date`, `list_added`, `unknown` |
| `email_origin` | `person_supplied` only for form fills, event registrations, and attendance lists; `source_matched` when a vendor matched it; `none` |
| `is_company_only`, `full_name`, `first_name`, `last_name`, `title_raw`, `headline`, `linkedin_url`, `email_raw` | |
| `company_name_raw`, `company_domain_hint`, `company_website_raw`, `company_key` | the key is `name:<normalized name>` when a company name exists, else a work-email domain, else the website domain. Names fold accents (Café is cafe) and keep non-Latin scripts as written (华为 stays 华为). Across the file: one name on two work-email or website domains splits into `name:<name>@<domain>` keys (Acme at acme.com and acme.io are two companies), and a row of that name with no domain stays on `name:<name>` with a `key_note`. One name on one domain keeps every row, with or without an email, on `name:<name>`. Different names are never merged: two names on one work-email domain (CV and CV Christian Vision, or "Acme Robotics" with a stale oldco.com address) each get a `key_note`. Key notes become the company's `collision` for the adjudicator, and gate 4 needs a `collision_resolved` fact for them. Research replaces the key with a verified domain (`company_key_final`) |
| `employee_count_raw`, `industry_raw` | kept for reference only; never used for a label |
| `referrer_raw`, `pages_all`, `engagement_counts`, `comment_text`, `crm_hint`, `rb2b_lead_type`, `past_company`, `touches_json` | source context |

`classify.py` derives the source channel (by referrer host, never substring), intent level and phrase, title group, email type, and hard codes. No model sets intent.

## Adapters

### RB2B from Baserow (default for RB2B)

The live table is `1171339` (database 535262). **Pull it as JSON through the API with `baserow.sh`, never as a Baserow CSV export**: the CSV export mixes DD/MM and ISO dates and flattens page detail, and the csv adapter refuses one with a message saying so. The Downloads export is stale; use the table.

```bash
# sandbox disabled; read only; repeat N until "next" is null
~/.claude/scripts/baserow.sh rows 1171339 --size 200 --page N --raw > "<run>/work/00-raw-baserow-pN.json"
python3 scripts/normalize.py --run "<run>" --adapter rb2b-baserow --input "<run>"/work/00-raw-baserow-p*.json \
  --since YYYY-MM-DD --until YYYY-MM-DD --source-label "RB2B 30-Day"
```

Check rows pulled against the first page's `count` before normalizing. Known collection holes: nothing before 2026-09-02, nothing 2026-09-11 to 09-15, and Jul 15 to 21 in older exports. Report the actual date range and zero-row days that `normalize.py` prints, never the requested window. Ignored on purpose: `Visit Count` (always 1), the `Hot page` tag (it double counts the direct-placement page), `Estimated Revenue`, `Industry`.

### RB2B direct export

`--adapter rb2b-export --input ~/Downloads/filtered_custom_report_*.csv`. Pages come from the `RecentPageUrls` JSON array; the highest-intent page sets intent. Still one page view per row in practice.

### LinkedIn engagement (exec-analytics)

JK exports the Leads list from the exec-analytics app (List tab, Export CSV): `leads-list-YYYY-MM-DD.csv` with `name, title, company, tag, outreachStatus, linkedinUrl, listAddedAt, distinctExecs, distinctPosts, reactions, comments, replies, firstSeenAt, lastSeenAt, heatTier`.

`--adapter social --input leads-list-2026-09-28.csv --source-label "LinkedIn Engagement"`.

- Lead ids are `exec_analytics:<LinkedIn slug>`; a row with no LinkedIn URL gets `<export file name>-row<N>`, so two exports never collide on row numbers.
- `tag` and `heatTier` are the app's own fit tiers. This skill ignores them and re-scores every person (JK ruling 2026-09-28).
- A company ending in `(past)` is a former employer: the row gets no company and lands in Insufficient data until research finds a current role.
- Social rows carry no email (`email_origin = none`), so they reach Qualified only after research or enrichment finds a qualifying work email.
- Follower and connection counts are never evidence.
- Touch dates are scraper batch dates, so `normalize.py` does not profile zero-row days for social runs; say "scraper batch dates" in the summary's caveats.
- The export has no company size. A company name in `large-companies.txt` (JPMorgan Chase, Deloitte, and similar) sends that company to knowledge triage first, which confirms it and drops it before any deep research.

### Campaign or any other CSV

`--adapter csv --input list.csv --touch-type <type> --campaign "<name>" [--map "title=Job Title,company=Org"] [--date-format dmy|mdy]`.

Before running, ask JK one question if it is not already stated: "How did people get on this list?" The answer sets `--touch-type` for the whole file: `form_fill`, `event_registration`, `event_attended`, `content_download`, or `list_member` (bought, scraped, or unknown). The first three mean the person typed the email (`email_origin = person_supplied`).

Slash dates: the adapter infers day-first or month-first from values over 12 and says which. It stops with a clear message when the date column is ambiguous (every part 12 or less) or mixes formats (ISO with slash, or day-first with month-first); rerun with `--date-format dmy` or `--date-format mdy`. Two-digit years ("9/25/26") always stop the run, flag or not: the adapter never guesses the century, so re-export with four-digit years. Header aliases cover the usual HubSpot and event exports; the adapter prints the mapping it chose and keeps unmapped columns in `touches_json`. A HubSpot export with `Record ID` gets `lead_id = hubspot:<id>`; the CRM stage still runs because owners and deals are not on a contact export.

## Intent (fixed tables, no model)

RB2B pages (`page-intent.csv`): `/contact` and `/survey` High; services, work, industry, and global-talent pages Medium; homepage, about, insights, privacy Low; careers None (job-seeker hint). An ad landing page (`/`, `/services/recruiting/direct-placement`, `/industry/enterprise`) reached from a paid referrer is Low and reads "Arrived from Facebook (likely an ad) at the homepage". RB2B carries no UTMs, so every paid-source phrase says "likely an ad" and never asserts a click on an ad. The ad-verification scanner (`connect.themediatrust.com`) is None: "Ad-verification scanner, not a person". `/survey` is the Configure a team quiz, and RB2B only proves the visit, so its phrase says so.

Social: a comment asking about hiring, help, or pricing is High (only when comment text exists); any comment Medium; 3+ reactions across 2+ posts Medium; a reaction Low.

Campaign: form fill High ("Filled out a form for <campaign>"); attended ("Attended <campaign>"), registered ("Registered for <campaign>"), downloaded ("Downloaded <campaign>") Medium; list member None.

Intent never changes a Verdict. It orders rows inside an Action bucket and appears in packets as "How this account reached us".
