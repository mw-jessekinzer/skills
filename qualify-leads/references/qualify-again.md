# Qualify again (S3 CRM check, S4 relabel and adjudication)

"Qualify again" means: add CRM facts, rerun `label.py`, then resolve the rows the script flags by writing **facts** to `work/overrides.csv`. Labels are never typed by hand.

## S3: HubSpot cross-check (read only)

Dispatch the `hubspot-analyst` agent with `model: "sonnet"`. First build its input list:

```bash
python3 scripts/label.py --run "<run>"       # labels with research facts, before CRM
```

The companies to check are every `company_key_final` in `work/05-qualified.csv` whose company was deep-researched and whose `reason_codes` hold no absolute or company code. The people are every person row at those companies. `checks.py gate --run <run> 1` lists anything missing afterwards.

Brief (fill the brackets):

```
Read-only HubSpot lookup for a lead qualification run. Never create, update, merge,
associate, or delete anything. No manage_* tools.

Companies: <paste company_key_final, company name, domains from 03-research-companies-*.csv>
People: <paste lead_id, full name, email, company_key_final from 05-qualified.csv>

For each company: search COMPANY by every domain in its domains list, then by name as a
secondary check (a name-only hit is match_type = name). Record the company id and name,
owner name and whether that owner is an active user (resolve with search_owners), lifecycle
stage, open deals (count plus one short summary: deal name, amount, stage, close date,
owner), closed-won deals in the last 24 months (count and total amount), last activity date.
For each person: search CONTACT by email, then by name plus the associated company. Record
contact id, email on the record, job title, contact owner and whether active, lifecycle,
lead status.

Write two CSV files with the Write tool, one row per company and one per person,
including misses. Use exactly these header lines and quote any cell that has a comma:
  <run>/work/04-crm-companies.csv
    company_key_final,checked,hs_company_id,hs_company_name,match_type,owner_name,owner_active,lifecycle,open_deals,open_deal_summary,closed_won_24m_count,closed_won_24m_amount,last_activity
  <run>/work/04-crm-contacts.csv
    lead_id,checked,hs_contact_id,match_type,email,job_title,contact_owner,contact_owner_active,lifecycle,lead_status
Values: checked = yes, or no if the lookup failed; match_type = domain | name | none for
companies and email | name | none for people; owner_active and contact_owner_active =
yes | no; open_deals and closed_won_24m_count are integers; dates are YYYY-MM-DD; no dashes
in open_deal_summary.

A failed lookup is checked = no (the quality gate fails until it is redone). Report back in
under 150 words: counts found, open deals, customers, inactive owners.
```

Rules the script applies (so the agent does not): a HubSpot contact email at the company's domain replaces the source email and reads `From HubSpot`; contact owner and company owner stay separate; `customer` needs a closed-won deal in 24 months, because lifecycle alone is unreliable in this portal; the CRM status sentence is written by `label.py` from these fields.

Enrichment adds one more CRM pass, on committee members, before the import file is built: same agent, same rules, contacts searched by email then name, rows written to `work/07-crm-committee.csv` with the header `company_key_final,email,full_name,checked,hs_contact_id,contact_owner,contact_owner_active`.

The agent has no Bash, so it writes files directly. After it finishes, run `python3 scripts/checks.py gate --run <run> 1 2` to confirm the files parse and cover every key.

## S4: relabel, then adjudicate flagged rows

```bash
python3 scripts/label.py --run "<run>"
```

Then send ONE Opus worker (`model: "opus"`) over the flagged rows only:

- a `Generic exec` row whose buyer role is still `unknown`
- a company with a `collision` in `05-company-rollup.csv`: the name was used for another domain in earlier runs, different names in this file share an email domain (same company, or a stale email?), or a no-domain row carries a name that is split across domains (which company?)
- a `STRUCTURAL_NO_NEED ignored` warning: if the business really has no need, write the business-model cause into `no_need_why`; otherwise leave it parked
- a `label_warnings` cell (a rejected triage code, a Keep never researched)
- a Qualified row with Low confidence
- a CRM `possible_match`
- a `GAP_*` code in `reason_codes` on a Review row (hiring not checked or unreadable at a confirmed US company under 2,000): run `ats_count.py` or read the careers page, and record the counts or a dated signal. These are the cheapest upgrades to an Account play. Low priority gap rows are checked only if time allows.

Missing evidence is never a reason to Drop: `label.py` parks those rows in Review or Low priority, and `checks.py` gate 2 fails any Drop that rests on a gap. Offshore-only tech roles count as demand; do not write an override to downgrade them.

The adjudicator writes fact rows, never labels:

```
python3 <skill>/scripts/append_row.py override <run>/work/overrides.csv --json \
  '{"level":"company","key":"name:cyera","field":"employees_best","new_value":"1550","reason":"PitchBook and LeadIQ 2026 show 1,500 to 1,600","source_url":"https://..."}'
```

`level` is `company` (key = `company_key` or `company_key_final`) or `person` (key = `lead_id`). `field` is any company or person fact field from `research-brief.md`, plus `collision_resolved` for a name collision (write what was checked, e.g. "pureins.co in the 09-18 audit was an RB2B website guess; same company"). Every override needs a reason and, when there is one, a source URL. Later rows win.

Then rerun `label.py`. `work/05-changes.csv` lists every label that moved.

### Adjudicator brief (Opus, one worker)

```
Adjudicate flagged rows in a lead qualification run. Facts only: you never write a
Verdict, Action, or reason text. Run folder: <run>. Rows to look at (from
work/05-qualified.csv and work/05-company-rollup.csv): <paste lead_id, company,
primary_code, reason_codes, label_warnings, collision for each flagged row>.
For each: check the one fact in doubt (buyer role against the company, which company
a same-name domain belongs to, the headcount source, the job board, the HubSpot record
name), then append one override row per corrected fact with append_row.py override
(reason and source URL required). For a collision, write collision_resolved with what
you checked. Use the research brief's web fallback order if firecrawl is rate-limited.
Work sequentially, no sub-agents, no dashes in cells. Report back in under 150 words:
facts changed, and anything you could not resolve.
```

## Freeze Tier 1 (S5)

```bash
python3 scripts/label.py --run "<run>" --freeze-tier1 [--tier1-max 4]
```

`--tier1-max` sets the Tier 1 size (default 8, saved in `run.json`); account plays fill the space left after Contact now companies, 5 at most. Each row's `projected_moltsets` and `projected_deepline` are scaled so the whole Tier 1 fits the run's caps, and `packet_file` is the exact packet filename. More Contact now companies than the size, or `ledger.py check` failing on the projection, means stop and ask JK before S6. A company JK or the budget rules out goes in the skip file, which the gates report instead of failing:

```bash
python3 <skill>/scripts/append_row.py skip "<run>/work/06-enrich-skipped.csv" \
  --json '{"company_key_final":"nicoletbank.com","reason":"budget: Deepline cap reached"}'
```
