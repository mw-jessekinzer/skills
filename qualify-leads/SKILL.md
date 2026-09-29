---
name: qualify-leads
description: Use when JK hands over a lead list to qualify, tier, or enrich (RB2B visitors or a Baserow table id, an exec-analytics LinkedIn engager export, an event or campaign list, any CSV) and wants consistent verdicts, Tier 1 committees, lead packets, or a HubSpot import. Triggers "qualify these leads", "tier the RB2B visitors", "who should sales call". Not for a single lead (lead-capture), Baserow adds, hiring intent alone (hirebase), vertical ICP research, or any CRM write.
---

# Qualify leads

**Core rule: workers supply facts, scripts supply labels.** Opus workers return typed facts; `scripts/label.py` computes Verdict, Action, strength, reasons, and rank. Fix a wrong label by adding a fact row to `work/overrides.csv` and rerunning `label.py`. Never type a label.

`<skill>` = `~/.claude/skills/qualify-leads`. Run scripts as `PYTHONDONTWRITEBYTECODE=1 python3 <skill>/scripts/<name>.py`. Run folder: `1_Projects/Lead Triage/<YYYY-MM-DD> <Source label> Lead Qualification/`.

## Dispatch rules

- Opus for judgment (research, triage, adjudication, enrichment, review); Sonnet for mechanics (`hubspot-analyst` CRM lookup, summary note). **Pass `model` on every Agent call.**
- At most 3 workers at once. Every brief says: sequential, no sub-agents or forks, write row by row with `append_row.py`.
- Vendor scripts and job board fetches need Bash with the sandbox disabled.
- **Read only** outside the run folder. No HubSpot or Baserow writes, ever. Log every vendor and CRM command under `## Commands` in `work/00-run-log.md`.

## Stages

| Stage | Who | Do | Check before moving on |
|---|---|---|---|
| S0 Intake | you, `normalize.py` | adapter per `references/schema-and-adapters.md` (Baserow as JSON through the API, never a CSV export); `--since` takes a timestamp, `--exclude-prior <run>` skips leads already handled, `--test-run` for tests; at most one question to JK | rows pulled = API count; report the real date range and gaps |
| S1 Qualify | `classify.py --prior-dir "1_Projects/Lead Triage"` | batches in `work/02-batch-*` | over 60 deep-research companies: ask JK |
| S2 Research | Opus, briefs in `references/research-brief.md` | deep and triage batches; then `classify.py keeps` and the keep batches | `checks.py gate --run <run> --stage S2 1 2` |
| S3 CRM | `hubspot-analyst`, Sonnet | `label.py`, then the brief in `references/qualify-again.md` | `checks.py gate --run <run> --stage S3 1` |
| S4 Qualify again | `label.py`, one Opus adjudicator | flagged rows become override facts; `label.py` | `checks.py gate --run <run> --stage S4 1 2` |
| S5 Tier 1 | you, `label.py --freeze-tier1 [--tier1-max N]` | read `work/06-tier1.csv` (default 8 companies, projections scaled to the caps) | over the Tier 1 size in Contact now, or `ledger.py check` fails: ask JK; companies you skip go in `work/06-enrich-skipped.csv` with a reason |
| S6 Enrich | Opus, one per Tier 1 company | `references/enrichment-playbook.md`; workers never run `assemble.py`; one BounceBan bulk call per run, by you, after all workers; committee CRM pass | `ledger.py check` before each company; `checks.py gate --run <run> --stage S6 1 4` |
| S7 Relabel | `label.py` | read `work/05-changes.csv` | post-freeze upgrades go in the summary, no packet |
| S8 Assemble | `assemble.py` once, then Sonnet | summary from `work/08-summary.json` per `references/output-spec.md`; readme bullet; `ledger.py summary` and `close` | final rows = canonical rows |
| S9 Gates | `checks.py all`, Opus reviewer | `references/quality-gates.md`; fixes as overrides, rerun S7 to S9, max 2 loops; humanizer on summary and packets | ALL GATES PASS |

## Stop and ask JK

- Over 60 companies need deep research, or more Contact now companies than the Tier 1 size.
- `ledger.py check` exits 2. Caps per run (on this run's own ledger spend): Deepline 10 credits, Hirebase 25, MoltSets 60 tokens. Change them only with JK's approval: `ledger.py caps --run <run> --deepline N --approved-by "JK"`. Report spent per vendor, what is left, cost to finish, and a recommendation.
- A CSV where nobody knows how people got on the list, or whose dates are ambiguous (`--date-format`).

## Outputs

`00 - Summary.md`; `<date> <Source label> Leads.csv` (UTF-8 BOM); `<date> hubspot-import.csv` (new contacts only; owner = the company's active HubSpot owner, else Jesse Kinzer; JK imports it); `Packets/<packet_file from 06-tier1.csv>` (no connection notes); `cost-ledger.csv`; `work/`. Plus a readme bullet and `vendor-ledger.csv` rows.

## References

- `label-spec.md`: every labeling rule, JK's rulings, calibration cases.
- `schema-and-adapters.md`, `research-brief.md`, `qualify-again.md` (CRM and adjudicator briefs), `enrichment-playbook.md` (vendor order, commands, pricing), `packet-template.md`, `output-spec.md` (summary writer brief), `quality-gates.md` (reviewer brief, common mistakes).
- Editable tables: `reason-codes.csv`, `page-intent.csv`, `referrer-hosts.csv`, `exclusions.csv`, `tech-roles.txt`, `large-companies.txt`.
- Tests: `python3 -m unittest discover -s <skill>/tests`.
