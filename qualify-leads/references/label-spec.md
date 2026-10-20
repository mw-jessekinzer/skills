# Label spec

`scripts/label.py` implements everything here. Read this to know what a fact does to a label, to brief a worker, or to review output. To change a label, change a fact (in a worker file or `work/overrides.csv`), then rerun `label.py`. Never edit a label cell by hand.

Reason-code wording lives in `reason-codes.csv`. Page intent lives in `page-intent.csv`, referrer channels in `referrer-hosts.csv`, compliance and competitor names in `exclusions.csv`, tech-role titles in `tech-roles.txt`, well-known enterprises (triage first to confirm size and identity, never to drop) in `large-companies.txt`. JK can edit those tables; the scripts read them on every run.

## JK rulings built in (2026-09-28)

- Personal email is a hard fail only when the person typed it (form fill, event registration, attendance list); a vendor-matched personal email caps the row at Possible match.
- TA and recruiting titles at a prospect are buyers; agency and staffing recruiters are excluded.
- Social input (exec-analytics export) is re-scored here; the app's own tiers are ignored.
- Company-only rows top out at Insufficient data; they can still be Account plays.
- Offshore-only tech hiring counts as demand, with a Watch-outs note.
- Need signals count for 18 months.
- Missing evidence parks a row (Review or Low priority); it never drops one.
- HubSpot import: new contacts only; owner is the company's active owner, else Jesse Kinzer.
- JK ruling 2026-10-12 (supersedes the 5,000 cap ruling the same day): no size cap. Enterprise companies stay (Midwestern just landed Deloitte, about 543,000 employees). Size is a descriptive tier: Enterprise 5,000+; Mid-market 500 to 4,999; Growth startup under 500 with a venture round in the last 24 months; Small business under 500 with no recent round. Enterprise reaches Tier 1 only as Contact now; enterprise account plays go to the HubSpot owner, no packet. The thresholds are `ENTERPRISE_MIN`, `MIDMARKET_MIN`, and `STARTUP_FUNDING_MONTHS` in `scripts/common.py`. The retired triage codes `OVER_2000` and `OVER_SIZE_CAP` still load, but such a drop is ignored with a warning.

## Two layers

- **Verdict** (strict ICP): `Qualified`, `Possible match`, `Insufficient data`, `Not qualified`.
- **Action** (what a salesperson does): `Contact now`, `Tell account owner`, `Account play`, `Review`, `Low priority`, `Drop`.

Plus **Account strength** (`Strong`, `Medium`, `Weak`, `None`), which is about the company regardless of the person, and **Confidence** (`High`, `Medium`, `Low`).

## Title group (first match wins)

On `title_verified` when research supplied one, else the source title, else the title parsed from a LinkedIn headline. Commas and slashes are stripped first, so "Director, IT" reads "director it"; both word orders match ("Director of IT", "IT Director", "Engineering Director", "Director of Engineering").

1. `No title`: blank or placeholder (none, n/a, client, unknown).
2. `Excluded title` for an agency, staffing, or third-party recruiter ("Senior Recruiter, Agency"), or an executive, administrative, or personal assistant (so "Executive Assistant to the CEO" never reads as a CEO).
3. `Primary: technology/product`: CTO, CIO, CISO; VP, Head, or Director of Engineering, Technology, IT, Product, Digital, Data, Software Development, Information Systems; Engineering, Technology, Product, or IT Director; Engineering Manager, IT Manager.
4. `Primary: design/creative`.
5. `Primary: recruiting/people`: CHRO, VP, Head, or Director of People, Talent, Talent Acquisition, Recruiting; TA Manager, Recruiting Manager; Head of Recruiting. **TA and recruiting titles at a prospect are buyers.**
6. `Primary: operations/transformation`: VP or Director of Operations, Strategy, Transformation, Procurement, Business Systems.
7. `Secondary influencer`: PM, Product Owner, program manager, architects, staff, principal, lead, or founding engineers, HR manager or generalist, in-house recruiter, technical recruiter, TA specialist, CFO, VP Marketing, Marketing Director.
8. `Generic exec`: Founder, Owner, President, CEO, COO, Managing Director or Partner, Principal, GM, Partner, Executive Director, Chief of Staff, bare VP, any other "Chief ... Officer". Research resolves it: `buyer_role = yes` makes it a buyer; `no` makes it `UNRELATED_TITLE`.
9. `Excluded title`: student, intern, teacher, professor, coordinator, sales rep, account executive, customer support, technician, apprentice, retired, job seeker.
10. `Unrelated title`: everything else. **Research wins over the table:** a row whose research says `buyer_role = yes` never gets `UNRELATED_TITLE`.

The `ambiguous engineer` flag (an individual engineer title with no software marker: mechanical, civil, systems) only routes the company to research. It never changes a label, and it does not fire on engineering leaders (Director, VP, Head, Manager of Engineering).

## Email status (first match wins)

The email checked is, in order: a HubSpot contact email at the company's domain, else the email research found, else the source email. The company's domains come from research; when research recorded none, the source website domain stands in, so a stale employer address still reads `Wrong domain`.

| # | Condition | Status | Qualifies |
|---|---|---|---|
| 1 | no email | `None` | no |
| 2 | personal domain (gmail, yahoo, aol, .rr.com, and the rest in `common.py`) | `Personal` | no |
| 3 | registrable domain not in the company's domains | `Wrong domain` | no |
| 4 | BounceBan undeliverable, or MoltSets risk D to F | `Undeliverable` | no |
| 5 | email came from the HubSpot contact record (visitor or committee member) | `From HubSpot` | yes |
| 6 | the person typed it (form fill, event registration, attendance list) | `Given by the person` | yes |
| 7 | MoltSets risk A validated in the last 90 days; SMTP valid on a normal domain; Deepline native `verified=true`; BounceBan deliverable on a normal domain | `Verified` | yes |
| 8 | accept-all domain and BounceBan deliverable | `Verified, catch-all domain` | yes |
| 9 | accept-all domain, no BounceBan result yet (including `pending`) | `Catch-all, unconfirmed` | no |
| 10 | anything else | `Unverified work email` | no |

A committee member who is the visitor carries the visitor's CSV status, word for word; packets and `08-committee-status.csv` use the same string.

## Company size

Size never drops, disqualifies, or lowers a row. It is a descriptive tier, `company_size`, shown in the CSV's Company size column and in packets.

`size_tier` records source quality only: `A` = filing, company-stated figure, LinkedIn company page count or band; `B` = PitchBook, Tracxn, Crunchbase, LeadIQ, RocketReach, ZoomInfo, Revelio, MoltSets company record; `C` = model knowledge, inference. It feeds Confidence and the `TINY_NO_BUDGET` evidence rule, nothing else.

`company_size` comes from `employees_best` from any source tier (A, B, or C) and the dated need signals:

| Company size | Rule |
|---|---|
| `Enterprise` | `employees_best` 5,000 or more |
| `Mid-market` | 500 to 4,999 |
| `Growth startup` | under 500, and a `funding` need signal dated within 24 months of the run's as-of date |
| `Small business` | under 500, no such funding signal |
| `Unknown` | no `employees_best` |

Size bands (a finer display): `1-10`, `11-50`, `51-200`, `201-500`, `501-1,000`, `1,001-1,999`, `2,000-4,999`, `5,000+`, `Unknown`.

Size belongs to the operating company the person works for. A parent is recorded (`parent_name`, `parent_employees`, `parent_centralized`); when the parent is Enterprise (5,000+ employees, any source tier) and the unit's tech or hiring runs through it (`parent_centralized = yes`), the row gets the `OPEN_PARENT` open item and a one-step strength downgrade. That is a Review, never a Drop.

**Enterprise light pass.** Hiring is not checked at Enterprise scale on purpose: open-role counts never lift an Enterprise company's strength, and the `GAP_HIRING_*` codes never apply to it. An Enterprise row is never a Drop for want of hiring evidence; with no fresh need signal it parks in Low priority.

RB2B's employee field never sets a size; its `5001+` values, and a company name in `large-companies.txt` (for sources with no size field), only send the company to knowledge triage first, to confirm its size and identity. Reason text quotes `employees_best` as a number ("about 120 people"), never the worker's free text.

## Hiring

From job board counts (`ats_count.py`), a careers page, or a LinkedIn Jobs tab (`hiring_checked = linkedin_jobs`). `Hiring tech roles` (1+ US tech role), `Hiring tech roles, none in US`, `Hiring, non-tech only`, `No open roles found` (a board, careers page, or LinkedIn Jobs tab was read and was empty, including a careers page that says "coming soon"), `Not checked`, `Unknown` (no board found, or Hirebase no-match, shown as "Hirebase: no match"; never read as "not hiring"). A Hirebase-only count shows as `N+ (Hirebase, may undercount)`; offshore roles show as `0 (6 outside the US)`.

A "systems engineer" or a hardware or device role is a tech role only with a software marker ("Software Systems Engineer").

**Offshore-only hiring is neutral** (JK 2026-09-28): tech roles outside the US count as hiring demand like US roles. There is no downgrade. The row gets a Watch-outs note: "Open tech roles are all outside the US (India). Fit may be embedded global talent rather than US direct hire."

A **need** is found when there is at least one open tech role (any location) or a dated need signal from the last **18 months**. A `contraction` signal is context, never a need, and signals older than 18 months are not shown in the Need signals column.

## Reason codes

Precedence is the order below; the first code that applies is the primary code and drives "Why this verdict".

- **Absolute** (always Drop): `COMPLIANCE_DNC`, `INTERNAL`.
- **Company** (kills the account): `COMPETITOR_STAFFING`, `NOT_US`, `PUBLIC_BODY_NON_BUYER`, `CONSUMER_SELF_EMPLOYED`, `CANNOT_BUY`, `STRUCTURAL_NO_NEED`, `TINY_NO_BUDGET`. There is no size code.
- **Person**: hard (an excluded audience) `VENDOR_SELLING`, `JOB_SEEKER`, `STUDENT_EDUCATOR`, `EXCLUDED_TITLE`, `PERSONAL_EMAIL_SUBMITTED`; soft (about the buying role only) `NOT_AT_COMPANY`, `UNRELATED_TITLE`. Either kind allows an Account play at a Strong or Medium account; only soft codes are protected by the missing-evidence rule and routed to the owner at a live deal.
- **Insufficient data**: `INS_NO_PERSON`, `INS_NO_COMPANY`, `INS_NO_TITLE`, `INS_US_UNKNOWN` (only when `us_company` is unknown; `no` is `NOT_US`).
- **Possible-match open items**: `OPEN_PARENT`, `OPEN_AUTHORITY`, `OPEN_NEED`, `OPEN_EMPLOYMENT`, `OPEN_EMAIL`, `OPEN_TINY`.
- **Account evidence gaps** (an Action reason, never a Verdict): `GAP_HIRING_NOT_CHECKED` ("Hiring not checked."), `GAP_HIRING_UNREAD` ("Job board not found or not readable, so hiring is unknown."), plus `INS_US_UNKNOWN` reused as a gap. The hiring gaps never apply to an Enterprise company.

Guardrails the script enforces:
- `CANNOT_BUY` is ignored (with a warning) when `employees_best > 50`.
- `TINY_NO_BUDGET` fires only on evidence: under 11 people from a tier A or B source, and a job list that was actually read (job board, careers page, LinkedIn Jobs) with no tech role and no fresh signal. Otherwise a tiny company gets `OPEN_TINY` and stays reviewable.
- A triage Drop with a retired size code (`OVER_2000` or `OVER_SIZE_CAP`, from files written before 2026-10-12) is not a drop: the row gets the warning "triage size drop ignored: size never drops; research it", parks like any Keep never researched, and `classify.py keeps` queues the company for research. Research facts always win over a triage row.
- **Peer vendors are excluded by default**: MSPs, IT services firms, dev shops, and consultancies are `COMPETITOR_STAFFING` (research sets `sells_staffing_or_dev = yes`). The one exception: research confirms the firm buys recruiting for its own staff (`peer_buys_recruiting = yes`) AND the row is that buyer (a recruiting or people title, or `buyer_role = yes`). Named competitors and staffing names from `exclusions.csv` never qualify.
- An accounting firm or a museum is never a competitor. It is `STRUCTURAL_NO_NEED` only when the facts state a business-model cause ("museum; no software product; IT run by an outside vendor"). A reason that rests on not finding anything ("no tech hiring need found", "none found") is an absence of evidence: the code is ignored with a warning and the row is parked (Low priority, or Review for a buyer), never dropped.
- `PUBLIC_BODY_NON_BUYER` does not apply to a technology or operating buyer at a public body.
- `us_company = yes` when the company operates in the US (a US office or entity with staff); a foreign HQ with US operations counts, and research names the HQ country in What the company does.

## Verdict

```
any absolute, company, or person code        -> Not qualified
else any INS_* code                          -> Insufficient data
else any OPEN_* item                         -> Possible match
else                                         -> Qualified
```

Open items: `OPEN_PARENT` (buying may sit with an Enterprise parent), `OPEN_AUTHORITY` (Secondary title, or buyer role partial or unknown), `OPEN_NEED` (no need found), `OPEN_EMPLOYMENT` (not confirmed and no qualifying email), `OPEN_EMAIL` (email does not qualify), `OPEN_TINY` (1 to 10 people).

So Qualified needs: a named buyer, a US company, a need, and a qualifying email. There is no size condition. Company-only rows are never Qualified.

## Account strength

- `None`: any absolute or company code, or the company can't be identified.
- **Enterprise** company: `Medium` when US with a need signal from the last 18 months, else `Weak`. Open-role counts never lift it.
- `Strong`: 11+ people, US, and either 3+ open tech roles (any location) or 1+ with a need signal from the last 18 months.
- `Medium`: US, and at least one open tech role or a fresh need signal.
- `Weak`: everything else.

Then one step down (never up, once) for a big centralized parent, or a worker's `PARENT_UNCLEAR`, `CONTRACTION`, or `ROLES_STALE`. Any other downgrade value (including the retired `ENG_OFFSHORE`) is ignored.

## CRM state

From `04-crm-*.csv`, in this precedence: `possible_match` (name-only match; ownership not trusted, here or in the import), `open_deal`, `customer` (a closed-won deal in 24 months; lifecycle alone does not count), `owned_active`, `owned_inactive`, `unowned`, `not_found`, `not_checked`. The routing owner is the company owner for an open deal or customer, else the active contact owner, else the active company owner.

## Action (first match wins)

1. Any absolute code: `Drop`.
2. CRM `open_deal` or `customer`, and Qualified or Possible match: `Tell account owner`.
3. CRM `open_deal` or `customer`, Not qualified or Insufficient data, and only soft person codes (or none): `Tell account owner` (someone at a live account showed up; the owner should hear).
4. Qualified: `Contact now` (routed to the active HubSpot owner when there is one).
5. Not qualified or Insufficient data, Account strength Strong or Medium, no company code, not an open deal or customer, and the only codes are person codes or `INS_NO_PERSON` / `INS_NO_TITLE`: `Account play`.
6. Possible match: `Review`.
7. **Missing evidence never drops.** Not qualified or Insufficient data, only soft person codes (or none), a company is identified, and the account has an evidence gap (hiring not checked or unreadable with no fresh signal, or US base unknown): `Review` when the only gap is hiring and the company is a confirmed US company; otherwise `Low priority`. Why gets "Account open item: Hiring not checked." and Next step reads "Check hiring at <company> before deciding on an account play."
8. An Enterprise company with only soft person codes (or none), not an open deal or customer: `Low priority` (its hiring is not checked on purpose, so no need found is not a confirmed absence).
9. Insufficient data: `Low priority`.
10. Otherwise: `Drop`.

**Enterprise routing.** An Enterprise company never takes an account play slot. When rules 1 to 10 give an Enterprise row `Account play`, its Action becomes `Tell account owner` and Next step reads "Route to <owner>, the HubSpot owner; enterprise account, no packet." (the active HubSpot company owner), or "Enterprise account: find the owner or AE before any outreach." when there is none. An Enterprise company reaches Tier 1 only through Contact now.

So `Drop` means a hard disqualifier (absolute, company, or hard person code, or an unidentifiable company) or a confirmed absence of need at a company that is not Enterprise (hiring read with no tech roles, no fresh signal, US base known). Size never drops a row. `checks.py` gate 2 fails any other Drop, and any `TINY_NO_BUDGET` without its evidence.

## Confidence

(a) size tier A or B; (b) employment confirmed or a qualifying email; (c) hiring read from a job board, careers page, or LinkedIn Jobs. Person rows: 3 = High, 2 = Medium, else Low. Company-only rows use (a) and (c): 2 = High, 1 = Medium, 0 = Low. A row dropped on a code that needs no research (compliance, internal, excluded title, job seeker, named competitor) is High.

## Sort order and Tier 1

Rows sort by Action, then Account strength, then Verdict, then the rest of the company tuple: tech role bucket, all locations (11+, 6 to 10, 3 to 5, 1 to 2, 0); best intent at the company; age of the freshest need signal; CRM cleanliness (not found or unowned first, active owner last); newest touch; company key; lead id. Strength comes before Verdict so Rank agrees with the Tier 1 order.

Tier 1 = every company whose best Action is Contact now (Enterprise included), plus the top Account plays by the same tuple (never an Enterprise company): 5 at most, and the Tier 1 size in total (`label.py --tier1-max N`, 1 to 8, default 8, saved in `run.json`; above 8 is an error, JK's hard limit). Each Tier 1 row carries a per-company budget projection scaled so the whole list fits the run's caps, and the exact `packet_file` name. When a cap divided by the Tier 1 count falls below the per-company plan (MoltSets 7.5 tokens, Deepline 1.25 credits, set so the default caps fit a full Tier 1 of 8 exactly; observed spend was about 1.1 to 1.2 Deepline credits and 2 MoltSets tokens per company), `label.py` prints a warning and `ledger.py check` repeats it: cut the size, skip companies, or ask JK to raise the cap. More Contact now companies than the size: stop and ask JK which to enrich. A Tier 1 company the runner decides not to enrich (budget, JK's call) goes in `work/06-enrich-skipped.csv` with a reason; the gates report it and the summary lists it. Tier 1 freezes when `label.py --freeze-tier1` runs; later runs write `06-tier1-candidates.csv`, and a company that only reaches Contact now after enrichment is listed as "upgraded after enrichment, no packet built".

## Buyer to target

Contact now: the visitor. Account play: up to 2 current committee members; else a known buyer research named (`known_buyer`, e.g. "Veniamin Veselovsky (Founder)"); else target roles from the service fit.

## Service fit (worker judgment, one value)

- `Recruiting`: open full-time US tech reqs (especially senior or onsite) or a talent-team gap (open recruiter req, one-person TA team).
- `Embedded`: remote or hybrid tech reqs with a backlog or launch surge, contract or C2H language, a named capacity gap, or tech roles hired outside the US (embedded global talent).
- `Scoped`: a build, modernization, data, or AI project signal without matching reqs.
- `None`: no need found.

Tie-break: Recruiting, then Embedded, then Scoped. A second fit goes in the packet's Angle, not the CSV.

## Other fact fields

- `collision_resolved`: a company override written when a name collision was checked. Say what was checked and the answer ("pureins.co in the 09-18 audit was an RB2B website guess; same company"). Gate 4 requires it for any non-Drop company with a collision.
- `tech_role_locations`: where offshore tech roles sit (from `ats_count.py`'s `non_us_tech_locations`), quoted in the Watch-outs note.

## Calibration cases (the golden tests encode these)

| Case | Facts | Labels |
|---|---|---|
| Pulley, Charlie Jacobson | Co-Founder CEO (buyer yes), about 100 (tier B), 7 US tech roles, HubSpot email | Qualified, Contact now, Strong |
| GiveCampus, R. Kulkarni | same shape, HubSpot customer | Qualified, Tell account owner |
| Letter AI, Abby Hunt | VP Marketing (Secondary), open deal, HubSpot holds abby@letter.ai while RB2B had a Gmail | Possible match, Tell account owner, email From HubSpot |
| An accountant at an open-deal account | soft person code | Not qualified, Tell account owner |
| PURE Insurance, John Burnsed | left in 2025; PURE tier A about 1,000 with 6 US tech roles | Not qualified (`NOT_AT_COMPANY`), Account play, Strong |
| Net Health | company-only, about 575, hiring | Insufficient data (`INS_NO_PERSON`), Account play |
| Cyera | 1,771 knowledge estimate (tier C), 9 tech roles | Mid-market; the figure counts whatever its tier; Strong, Account play for a sales visitor; an old triage size drop is ignored with a warning |
| Cyera, sales visitor | 1,550 (tier B), hiring not checked, no signal | Not qualified, `Review` with "Hiring not checked"; with a dated funding signal, Account play |
| Deloitte | about 543,000 (Enterprise) | a buyer with a need and a qualifying email is Contact now and Tier 1; a non-buyer at a Medium account (fresh signal) is `Tell account owner`, routed to the HubSpot owner, no packet; open-role counts never make it Strong |
| A 120-person startup | Series A 20 months ago | Growth startup; Qualified on a tier C size when the buyer, need, and email are there |
| MoMA | about 900, museum | `STRUCTURAL_NO_NEED` only with a business-model cause; "no tech hiring need found" parks it (Review when only hiring is open at a US company); never `CANNOT_BUY` |
| Sensiba | accounting firm | the same rule; never a competitor |
| 44i; a Joplin MSP | web agency; managed IT and dev | `COMPETITOR_STAFFING` (the MSP's confirmed recruiting buyer is the one exception) |
| Chatham County MIS Director | public body, tech buyer, personal email from RB2B | Possible match, never `PUBLIC_BODY_NON_BUYER` |
| Kerri Higgins, MidWestOne | merged into Nicolet (about 1,700); mortgage banker | key merges to Nicolet; `UNRELATED_TITLE`; Account play |
| Sumo Logic, Bamboo Rose | every tech role outside the US | roles count as demand (Strong); Watch-outs note on global talent |
| Lincoln Investment | new CIO/CTO hire 14 months ago, job board unread | signal counts (18-month window): Medium, Account play |
| Rocket Money engineer | unit about 700, parent Rocket Companies runs buying | a buyer gets `OPEN_PARENT` (Review); a non-buyer with hiring unchecked parks in Low priority; never a Drop |
| An 8-person company, hiring not checked | tier A size | Possible match with `OPEN_TINY`; `TINY_NO_BUDGET` needs a job list that was read |
