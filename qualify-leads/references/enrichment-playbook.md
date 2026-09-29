# Enrichment playbook (S6): Tier 1 companies and buying committees

Goal: for each Tier 1 company, 3 to 5 named, current people with a qualifying work email, the hiring and funding facts a rep needs, and a small packet. Cheapest route first; free sources do most of the work.

All vendor commands run in Bash **with the sandbox disabled** (Keychain reads and `~/.npm` are blocked otherwise). Credentials only through the existing clients: `~/.claude/scripts/baserow.sh`, `hirebase.sh`, `moltsets.sh`, and the `deepline` CLI. No writes anywhere except the run folder.

## Budget caps and the stop-and-ask rule

Per run (JK 2026-09-28): **Deepline 10 credits, Hirebase 25 credits, MoltSets 60 tokens** (about 25 for research-stage visitor checks, 35 for committees; the split can flex).

Caps are enforced on **this run's own ledger spend**, never on vendor balances: the org accounts are shared with other runs, so balance readings are informational (gate 8 warns on drift, never fails). Change a cap only with JK's approval, from the command line; the change is logged in the run log:

```bash
python3 scripts/ledger.py caps --run "<run>" --deepline 2 --moltsets 10 --approved-by "JK"
```

```bash
# run start and run end (informational)
deepline billing balance --json            # then: ledger.py balance --vendor deepline --when start --value <n>
~/.claude/scripts/hirebase.sh quota        # then: ledger.py balance --vendor hirebase --when start --value <n>
# MoltSets: tokens_remaining is in every response's metadata; record the first one as start

# before each company (S6) or batch (S2)
python3 scripts/ledger.py check --run "<run>" --vendor deepline --projected 1.25   # or the Tier 1 row's projection
python3 scripts/ledger.py check --run "<run>" --vendor moltsets --projected 7.5
# exit code 2 = STOP: finish nothing new, and ask JK with spent per vendor,
# what is left undone, projected cost to finish, and a recommendation

# after EVERY paid or possibly paid call, before the next one
python3 scripts/ledger.py add --run "<run>" --stage S6 --vendor deepline \
  --endpoint dropleads_email_finder --company withpulley.com --person "Chad Ackerman" \
  --input "Chad Ackerman at withpulley.com" --charged 0.26 --result hit --useful yes
```

A timeout or error is logged as charged at list price until a balance proves otherwise. `useful = yes` means the output changed a fact that reached the CSV or a packet (a verified email, a confirmed current role, a role count). At run end: `ledger.py summary`, then `ledger.py close --run-name "<folder name>" --vendor-ledger "1_Projects/Lead Triage/vendor-ledger.csv"`. Planning estimate per company: MoltSets 7.5 tokens, Deepline 1.25 credits, so the default caps fit a full Tier 1 of 8 exactly (8 x 7.5 = 60, 8 x 1.25 = 10). Observed: Deepline 5.70 for 5 accounts (1.14 each), 1.24 for Pulley, 1.18 for 2 companies in the test run; MoltSets 4 tokens for 2 companies (committee search now starts with Deepline's free search).

## Vendor order per job

| Job | Order | Stop when |
|---|---|---|
| Hiring | 1. Job board JSON via `ats_count.py` (free). 2. Careers page (free). 3. Hirebase `count` only if no board resolves and the company is Medium or better. | a board is parsed, or Hirebase no-match (= Unknown, never "not hiring") |
| Company facts | company site, LinkedIn company page via search, SEC filings, press (firecrawl); the MoltSets company block that comes free with a reverse lookup | a tier A or B headcount and a dated need signal, or clear absence |
| Committee discovery | 1. Deepline `company_titles` (free). 2. Deepline `dropleads_search_people` (free). 3. Leadership page, job posts' "reports to" lines. 4. MoltSets `search_people` by domain (1 token, trial-limited). 5. Deepline `deepline_native_search_contact` (0.56 per hit) only for a required seat nobody else filled. | 3 to 5 named, current people |
| Identity check | MoltSets `reverse_linkedin_lookup` per candidate (1 token on a hit); the returned `company.website_url` must be one of the company's domains and the role current | each person confirmed or dropped |
| Work email | 1. MoltSets business email from the reverse lookup (risk A, validated in 90 days, on a company domain). 2. MoltSets `search_business_email_by_name` with `company_domain` (a hint, not a filter: check the returned domain). 3. Deepline `dropleads_email_finder` (0.26, billed on `valid` only). 4. Deepline `deepline_native_enrich_contact` by LinkedIn (0.98 on a match), top 2 buyers only. | a qualifying address, or all four missed |
| Catch-all | workers record accept-all addresses with `bounceban_result = pending`. After every worker finishes, the orchestrator sends ONE Deepline `bounceban_verify_bulk` for the whole run (every pending address, plus 1 or 2 known-good addresses per domain as calibration; ledger result `pending`), reads the results, and appends them to `work/07-bounceban.csv` with `append_row.py bounceban`; `bounceban_verify_single` only for stragglers | every accept-all address has a result |
| Employment doubt | Deepline `deepline_native_search_contact` with `included_names` (0.56 on a hit, free on a miss) | current or gone |

Never used: TheirStack (dropped; its MCP returns 401), Deepline plays, waterfalls (`prebuilt/name-and-domain-to-email-waterfall-batch` cannot be priced up front), monitors, any HubSpot or CRM provider inside Deepline.

## Exact commands

```bash
# Job boards (free; parse with the script, never by eye)
python3 scripts/ats_count.py --ats greenhouse --slug <slug>
python3 scripts/ats_count.py --ats lever --slug <slug>
python3 scripts/ats_count.py --ats ashby --slug <slug>
python3 scripts/ats_count.py --ats workday --tenant <tenant> --site <site>
python3 scripts/ats_count.py --ats workable --slug <slug>        # apply.workable.com/<slug>
python3 scripts/ats_count.py --ats adp --cid <cid>               # cid= in the ADP careers URL
# iCIMS: no public JSON endpoint; read the careers page (hiring_checked = careers_page)
# a 404 or wrong slug prints hiring_checked "not_checked"; move to the careers page

# Hirebase (1 credit per matched call with limit 1, 0 on no-match; hard monthly block at 500)
~/.claude/scripts/hirebase.sh quota
~/.claude/scripts/hirebase.sh count --company "<exact name>" --category "Engineering Jobs"

# MoltSets (charged only when data is found; tokens_remaining in every response)
~/.claude/scripts/moltsets.sh call reverse_linkedin_lookup '{"linkedin_url":"https://www.linkedin.com/in/<slug>/"}'
~/.claude/scripts/moltsets.sh call search_people '{"company_domain":"<domain>","limit":5}'
~/.claude/scripts/moltsets.sh call search_people '{"company_domain":"<domain>","title":"<title>","limit":5}'
~/.claude/scripts/moltsets.sh call search_business_email_by_name '{"name":"<First Last>","company_domain":"<domain>"}'
~/.claude/scripts/moltsets.sh call reverse_email_lookup '{"emails":["<a@domain>","<b@domain>"]}'
~/.claude/scripts/moltsets.sh call search_linkedin_profile '{"name":"<First Last>","company":"<Company>"}'

# Deepline (run bare, no pipes; preflight alone first; prefix parallel calls with DEEPLINE_SKIP_SELF_UPDATE=1)
deepline preflight --json
deepline billing balance --json
deepline tools execute company_titles --input '{"domain":"<domain>"}' --json
deepline tools execute dropleads_search_people --input '{"filters":{"companyDomains":["<domain>"],"jobTitles":["Chief Technology Officer","VP of Engineering"]},"pagination":{"page":1,"limit":25}}' --json
deepline tools execute deepline_native_search_contact --input '{"domain":"<domain>","included_names":["<First Last>"],"page_size":1}' --json
deepline tools execute deepline_native_search_contact --input '{"domain":"<domain>","title_lists":[{"name":"cto","titles":["Chief Technology Officer"]}],"page_size":1}' --json
deepline tools execute dropleads_email_finder --input '{"first_name":"<First>","last_name":"<Last>","company_domain":"<domain>"}' --json
deepline tools execute deepline_native_enrich_contact --input '{"linkedin":"https://www.linkedin.com/in/<slug>"}' --json
deepline tools execute bounceban_verify_bulk --input '{"emails":["<a@domain>","<b@domain>"],"name":"<run-id>-catchall"}' --json
deepline tools execute bounceban_get_bulk_status --input '{"id":"<bulk id>"}' --json
deepline tools execute bounceban_get_bulk_emails --input '{"id":"<bulk id>","emails":["<a@domain>"]}' --json
deepline tools execute bounceban_verify_single --input '{"email":"<a@domain>"}' --json
```

If `deepline` misbehaves, run `deepline doctor --json` and repair with `deepline skills` before spending.

## Pricing facts (observed)

| Vendor | Call | Cost |
|---|---|---|
| Deepline | `company_titles`, `dropleads_search_people`, BounceBan status and email reads, catch-all and not-found email-finder results, native search misses | free |
| Deepline | `dropleads_email_finder` | 0.26 on `valid`; **a 60 s timeout still billed 0.26** |
| Deepline | `deepline_native_search_contact` | 0.56 per result returned |
| Deepline | `deepline_native_enrich_contact` | 0.98 on a match |
| Deepline | `bounceban_verify_bulk`, `bounceban_verify_single` | about 0.06 per email |
| Deepline | credit value | about $0.10 |
| Hirebase | any call | 1 credit per job row returned; `limit=1` count = 1 if matched, 0 if not |
| MoltSets | enrichment endpoints | only when data is found; `reverse_linkedin_lookup` 1 token; `reverse_email_lookup` 1 per address with data |
| MoltSets | `search_people` | 1 token per call, trial-limited (5 results per call, 100 total). When `search_trial.results_remaining` is under 10, skip it and use the free Deepline roster |

Observed yields (2026-09-25): 0.71 Deepline credits per verified buyer; 6 of 9 Dropleads finds were catch-all; BounceBan split 7 catch-alls into 3 deliverable and 4 undeliverable. Dropleads can be stale (it listed Lincoln's former CIO). BounceBan calibration: two known-good Pulley addresses scored 97 before the rest were trusted.

## Where each vendor field goes

| Output | Committee column |
|---|---|
| MoltSets `business_email_risk_score`, `business_email_validated_at` | `email_risk`, `email_validated_at` |
| MoltSets `company.website_url` | `employer_domain` |
| BounceBan `is_accept_all`, `result` | `domain_accept_all` (yes/no), `bounceban_result` |
| Dropleads email finder `status = valid` on a normal domain | `smtp_valid = yes` |
| Deepline native enrich `verified=true, status=safe` | `deepline_verified = yes` |

Copy vendor values verbatim; `assemble.py` and `committee_status.py` compute the email status from them.

MoltSets parameter note: `search_business_email_by_name` takes `company_domain` (or `company`), never `domain` (HTTP 422); the example comment inside `moltsets.sh` still shows `domain` and is wrong.

## Enrichment worker brief (one Opus worker per company, at most 3 at once)

```
Enrich one Tier 1 account for Midwestern Interactive: <company name> (<company_key_final>),
domains <domains>. Action: <Contact now | Account play>. Facts so far:
<paste the company row from 03-research-companies-*.csv and the lead rows from 05-qualified.csv>.

Work sequentially, no sub-agents, no planning docs. Vendor calls need Bash with the sandbox
disabled. Follow <skill>/references/enrichment-playbook.md for vendor order and commands.
Before the first paid call: python3 <skill>/scripts/ledger.py check --run <run> --vendor <v> --projected <cost>;
exit code 2 means stop and report. After every paid call: ledger.py add (flags in the playbook).
Budget for this company: Deepline <n> credits, MoltSets <n> tokens.

1. Re-pull the job board (ats_count.py) for current counts, titles, locations, dates, and
   any "reports to" lines. Find the latest dated funding round.
2. Build a committee of 3 to 5 current people: economic buyer, technical buyer, talent
   owner, 1 or 2 hiring managers for the open reqs. For a Contact now company the visitor
   is person one. Confirm each person's employer domain is one of the company's domains;
   a person whose MoltSets or Deepline employer is another company is dropped, even with
   the same company name.
3. Find each person's work email in the playbook order and record the verification
   fields verbatim. Do NOT call BounceBan: record every accept-all address with
   bounceban_result = pending. The orchestrator verifies all of them in one bulk call
   after every worker is done.
4. Append one row per person:
     python3 <skill>/scripts/append_row.py committee <run>/work/07-committee-<slug>.csv --json '{...}'
   Fields: company_key_final, order, full_name, first_name, last_name, title,
   role_in_decision (Economic buyer | Technical buyer | Talent owner | Hiring manager |
   Influencer, plus "(the visitor)" when it is the visitor), priority (First call |
   Second wave | Third wave | Influencer), email, email_source, email_risk,
   email_validated_at, domain_accept_all, bounceban_result, smtp_valid, deepline_verified,
   employer_domain, works_there (confirmed | likely | unknown | no), works_there_source,
   linkedin_url, lead_id (only for the visitor), notes.
5. If a company fact changed (headcount, roles, a new signal), append an override row:
     python3 <skill>/scripts/append_row.py override <run>/work/overrides.csv --json '{"level":"company",...}'
6. Write the packet from <skill>/references/packet-template.md to
   <run>/Packets/<packet_file from 06-tier1.csv>. No connection notes, no message drafts.
   Take every Email status from:
     python3 <skill>/scripts/committee_status.py --run <run> --company <company_key_final>
   (read only; never run assemble.py, the orchestrator runs it once after all packets).
   A pending catch-all shows "Catch-all, unconfirmed" until the bulk check lands; the
   orchestrator updates those cells after it. Brand voice from the Marketing Hub's
   Messaging Patterns note: no "brokers", no "staffing firm", no "outsource", no em or en
   dashes. Call a person who reacted or commented on LinkedIn what they did ("reacted to
   a Midwestern exec post"), never "the visitor".
   Then run: python3 <skill>/scripts/checks.py lint "<run>/Packets/<packet_file>"

Report back in under 150 words: people found with email status, paid calls and cost,
anything unresolved.
```

`<slug>` is `company_key_final` lowercased with anything other than letters, digits, dots, and hyphens replaced by `_` (the same rule as `label.slug`).

## After all enrichment workers finish (orchestrator)

1. Collect every committee row with `bounceban_result = pending` across companies and send one `bounceban_verify_bulk` (ledger it with result `pending`), then read the results with `bounceban_get_bulk_emails` (free) and append each to `work/07-bounceban.csv` with `append_row.py bounceban`. `assemble.py` and `committee_status.py` apply those results over the committee rows.
2. Run the committee CRM pass (`qualify-again.md`).
3. Run `assemble.py` once, update any packet Email status cells that changed (the `committee_status.py` output is the source), then `checks.py gate --run <run> --stage S6 1 4`.
4. A Tier 1 company left unenriched on purpose goes in `work/06-enrich-skipped.csv` with the reason (`append_row.py skip`).
