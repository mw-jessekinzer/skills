# Quality gates (S9)

Nothing goes to JK until gates 1 to 8 pass (`python3 scripts/checks.py all --run <run>`), gate 9's review is done, and gate 10's copy pass is clean. Run single gates mid-run with `checks.py gate --run <run> --stage <S2|S3|S4|S6|S8> <n> ...`: gate 1 then checks only what should exist by that stage (batches at S2, CRM rows at S3, labels at S4, committees and packets at S6, the final CSV at S8). Useful stage checks: S2 gates 1 and 2; S3 gate 1; S4 gates 1 and 2; S6 gates 1 and 4.

## Automated (checks.py)

| Gate | What it proves | Typical fix |
|---|---|---|
| 1 Counts | canonical ids unique; source rows = canonical + merged; pass1, qualified, and final CSV cover the same lead ids; every batch file came back with the same company keys; every researched company's people have person rows; every triage Keep was researched; every researched company without a company code (and its people) was checked in HubSpot; Tier 1 is within its size (`tier1_max`, default 8), and each Tier 1 company has a committee file and a packet unless it is listed in `06-enrich-skipped.csv` (reported as a warning, not a failure) | rerun the missing batch or CRM rows; `classify.py keeps` |
| 2 Vocabulary | every label cell is an allowed value; every reason code exists; `CANNOT_BUY` never over 50 people; `OVER_2000` only with a tier A or B figure of 2,000+ or an estimate of 5,000+; no Qualified row on a tier C size; no Drop that rests on missing evidence (only a hard disqualifier or a confirmed absence of need may Drop); no `TINY_NO_BUDGET` without a tier A or B headcount and a job list that was read; research and triage files use the allowed values; need signals are dated; overrides name real fields | correct the worker file or add an override |
| 3 Lint | no em dash, en dash, or " -- " in any CSV cell, the summary, or a packet; no "broker", "staffing firm", "staffing partner", "outsource"; no internal jargon in CSV cells (DQ, ICP gate, pass1, ATS); no contrast-flip tropes; cells within length | fix the worker text (an override, or the packet) |
| 4 Domain match | every committee and import email is on the company's domains; every committee member's employer domain matches; packet emails and statuses match `08-committee-status.csv` (the same strings as the CSV, visitor status included); any name collision has a `collision_resolved` override | drop or replace the person; write the resolution |
| 5 CRM applied | the CSV's CRM status equals what the HubSpot facts produce; a HubSpot contact email at the company domain shows as the Email with status From HubSpot | rerun `label.py` and `assemble.py` |
| 6 Intent | "What they did" is the template phrase; submitted, filled out, requested, signed up, registered, interested in appear only on form fills or registrations (CSV and packets); "verified" only beside a qualifying email | fix the packet wording |
| 7 Determinism | `label.py` twice on the same inputs gives identical files, and `05-qualified.csv` is current | rerun `label.py`; a real diff is a bug in the script |
| 8 Budget and no writes | this run's ledger totals within its caps (the only hard budget check); vendor balances are shared across runs, so balance drift is a warning only; the run log and ledger contain no write command (`baserow.sh create/update/delete`, any `manage_*` HubSpot tool, Deepline HubSpot providers) | stop and tell JK |

## Gate 9: independent review (Opus, fresh context)

Dispatch one reviewer with `model: "opus"` that did not work on this run. Brief:

```
Review a finished lead qualification run before it goes to JK. Read, do not rewrite.
Run folder: <run>. Read 00 - Summary.md, every row of the final CSV that is not Drop,
min(20, number of Drop rows) random Drop rows (seed 7; all of them when there are 20 or
fewer), and every packet
in Packets/. Check them against work/03-*.csv, work/04-*.csv, work/07-*.csv, and the
sources they cite.

Check, and list each finding with the lead_id or file and the evidence:
1. Intent overstated anywhere (RB2B is one page view; nobody submitted anything unless
   the touch was a form fill).
2. A size read from a keyword instead of a number, or RB2B's size used as evidence.
3. A person who has left the company, or a person tied to the wrong company (same name,
   different domain; check every committee member's employer domain).
4. A HubSpot fact not applied (owner, open deal, customer, a HubSpot email).
5. A generic or wrong reason (a museum called "can't buy", an accounting firm called a
   competitor, a mid-size company called tiny).
6. Numbers in packets that differ from the CSV or the work files.
7. An Action a salesperson would find wrong (a strong account buried, a weak one pushed).
8. Dashes, "brokers", "staffing firm", "outsource", contrast-flip phrasing, connection
   notes or message drafts in packets.
9. Anything the summary claims that the files do not support.

Write findings to <run>/work/09-review.md as a table: finding, lead_id or file, evidence,
suggested FACT fix (level, key, field, new value). Never suggest editing a label directly.
Report back in under 200 words.
```

Apply each accepted finding as an `overrides.csv` fact row (or a packet edit), then rerun `label.py`, `assemble.py`, and `checks.py all`. At most 2 review loops; after that, report what is still open.

## Common mistakes the gates exist for

| Mistake | Instead |
|---|---|
| Editing a Verdict or Action cell, or a label in code | Add a fact row to `overrides.csv`, rerun `label.py` |
| "Over 2,000" from a keyword, or RB2B's size | A tier A or B number of 2,000+, or an estimate of 5,000+ |
| Dropping a row because hiring or size was never checked | The script parks it; check the fact and rerun |
| Calling a page view a submission | Quote `What they did`; RB2B proves a visit only |
| Joining files by company name or row position | Join on `lead_id` and `company_key`; gate 1 checks key sets |
| Trusting a same-name company | Every contact's email and employer domain must be on the company's domains |
| Workers that fork, or 4+ at once | Sequential workers, 3 at a time, row-by-row writes with `append_row.py` |
| Paying before checking | `ledger.py check` before, `ledger.py add` after every paid call |

## Gate 10: copy pass

Run the humanizer skill on `00 - Summary.md` and every packet. Then grep for JK's tropes and dashes:

```bash
python3 scripts/checks.py lint "<run>/00 - Summary.md" "<run>"/Packets/*.md
```
