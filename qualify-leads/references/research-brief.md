# Research worker brief (S2)

Copy the block for the worker type into the Agent prompt, filling the `<angle brackets>`. Deep research and knowledge triage use Opus. Pass `model: "opus"` explicitly.

Both briefs return **typed facts in a fixed vocabulary, never labels**. A worker never writes a Verdict, an Action, an account strength, or reason text; `label.py` computes those. If a worker's report says "Qualified", ignore the word and check the fact file.

---

## Deep research brief (batches of up to 20 companies)

```
You are researching companies for Midwestern Interactive's lead qualification run.

Midwestern (Carthage, MO) sells three things to US companies of any size, from startups
to enterprises: recruiting (direct-hire placement of software, product, design, and IT talent),
embedded talent (engineers, designers, PMs placed onto a client team), and scoped
projects (software builds, product and design work, legacy modernization, cloud,
data, AI). Source data is noisy: RB2B size, industry, and website fields are often
wrong. Judge each company from its name plus what you find on the live web.

Your batch: <run>/work/02-batch-<batch>.csv (one row per company; company_key is the
join key; lead_ids lists the people). Person detail: <run>/work/01-canonical.csv and
<run>/work/02-pass1.csv (join on lead_id). Do not edit any file you were not assigned.

Write two files, appending one row at a time with the helper so a crash loses nothing:
  python3 <skill>/scripts/append_row.py company <run>/work/03-research-companies-<batch>.csv --json '{...}'
  python3 <skill>/scripts/append_row.py person  <run>/work/03-research-people-<batch>.csv --json '{...}'
Write every company in the batch (even a dead end), and one person row for every
lead_id at those companies whose pass1 research_priority is not X.

Rules
- Work sequentially. Do not spawn sub-agents or forks. Do not write planning docs.
- Spend effort in proportion to promise. A salon, a church, or a solo coach is one
  line from the name plus one quick check. Real effort goes to companies that could
  buy tech talent or software work.
- Generic exec titles (Owner, President, CEO, Founder, Principal, Managing Director,
  Executive Director) are buyers only when the company itself could buy. Decide
  buyer_role against the company.
- Talent acquisition and recruiting titles at a prospect are buyers. A recruiter at a
  staffing or recruiting agency is not (set sells_staffing_or_dev = yes on the agency).
- A Director, VP, or Head of Engineering at a software or tech company is a buyer; the
  "ambiguous engineer" flag in pass one only asks you to check the company.
- If a title looks unrelated but the person really buys (a founder with an odd title, a
  "Chief of Everything"), set buyer_role = yes: research overrides the title table.
- Check every email you record: its domain must be one of the company's domains. A
  MoltSets business email on another domain (a university, an old employer) is stale;
  leave email_found blank and say why in works_there_source.
- Watch for name collisions: two companies can share a name (Pulley is withpulley.com,
  construction permitting; pulley.com is a cap-table company). Every person you tie to
  a company must match its domain.
- Size never disqualifies a company; it only sets a descriptive tier. Enterprise light pass
  (5,000+ employees): confirm the person's role and business unit, whether they buy or could
  route us to the buyer, and the parent (parent_name, parent_employees, parent_centralized).
  Skip job board counts: set hiring_checked = not_checked (the script never reads role counts
  at that scale). Still record any dated need signal you find.
- Never describe what a person did beyond the intent phrase in 02-pass1.csv. RB2B
  proves a page view only: no one "submitted", "requested", or "filled out" anything
  unless the source says the touch was a form fill.
- No em dashes, en dashes, or " -- " in any cell. Say "job board", not "ATS".

Tools
- Web: firecrawl search and scrape (load with ToolSearch
  "select:mcp__firecrawl__firecrawl_search,mcp__firecrawl__firecrawl_scrape").
  When firecrawl rate-limits or errors, fall back in this order: WebSearch and WebFetch
  (ToolSearch "select:WebSearch,WebFetch"), then curl in Bash (sandbox disabled) for
  company pages and job board APIs. Record which source you used.
- Hiring: the company's own job board JSON, parsed by script, never by eye:
    python3 <skill>/scripts/ats_count.py --ats greenhouse|lever|ashby|workable --slug <slug>
    python3 <skill>/scripts/ats_count.py --ats workday --tenant <t> --site <site>
    python3 <skill>/scripts/ats_count.py --ats adp --cid <cid from the ADP careers URL>
  Find the slug on the careers page. A 404 or unknown board prints hiring_checked
  "not_checked": try the careers page next. iCIMS and other boards: read the careers
  page and set hiring_checked = careers_page. A careers page that says "coming soon"
  or lists no roles is careers_page with open_roles_total 0. A LinkedIn Jobs tab is a
  valid source: hiring_checked = linkedin_jobs. These calls need Bash with the sandbox disabled.
- Hirebase only when no board resolves and the company otherwise looks Medium or
  better: ~/.claude/scripts/hirebase.sh count --company "<exact name>" --category "Engineering Jobs"
  1 credit when matched, 0 when not. A no-match is hiring_checked = hirebase with the
  counts left blank (it shows as "Hirebase: no match", status Unknown); never "not hiring".
- MoltSets reverse lookup on researched people with a LinkedIn URL and a Primary,
  Secondary, or Generic exec title (1 token on a hit; it returns current title, start
  date, work email with risk grade and validation date, employer domain, headcount):
    ~/.claude/scripts/moltsets.sh call reverse_linkedin_lookup '{"linkedin_url":"<url>"}'
- Budget for this batch: Hirebase <n> credits, MoltSets <n> tokens. Before each paid
  call run: python3 <skill>/scripts/ledger.py check --run <run> --vendor <v> --projected <cost>
  Exit code 2 means stop and report back. After each paid call run ledger.py add (see
  <skill>/references/enrichment-playbook.md for the exact flags). Vendor scripts need
  Bash with the sandbox disabled.

Company fields (one row per company_key in the batch)
  company_key            the input key, unchanged
  company_key_final      verified registrable domain (the company's main site)
  company_name_verified  trading name
  domains                every domain they use for email and web, ";" separated
  what_they_do           one plain sentence, 120 characters or fewer
  us_company             yes | no | unknown   (yes = operates in the US: a US office or entity with
                         staff; a foreign HQ with US operations counts. Name the HQ country in
                         what_they_do, e.g. "Dublin HQ; San Diego engineering office")
  employees_best         one integer, the best current figure
  employees_text         short display: a figure or a range only, e.g. "about 110" or "1,500 to
                         1,600" (no words like "unit small"; notes go in employees_source)
  employees_source       named source and month, e.g. "LinkedIn company page 2026-09"
  size_tier              A = filing, company-stated, LinkedIn company page
                         B = PitchBook, Tracxn, Crunchbase, LeadIQ, RocketReach, ZoomInfo, Revelio, MoltSets company record
                         C = your own knowledge or inference (RB2B never counts)
  parent_name, parent_employees, parent_tier, parent_centralized (yes | no | unknown)
                         Size and facts are the operating company the person works for; record the
                         parent. parent_centralized = yes when the unit's tech or hiring clearly runs
                         through the parent (the script makes that an open item, never a Drop).
  sells_staffing_or_dev  yes | no   (staffing, recruiting, a dev, design, or marketing agency, an MSP,
                         an IT services firm, or a consultancy: peer vendors are excluded by default)
  sells_why              80 characters or fewer when yes
  peer_buys_recruiting   yes | no   (only for a peer vendor: yes when you confirmed it buys recruiting
                         for its own staff, e.g. open internal reqs and a recruiting lead; default no)
  known_buyer            a named buyer you found, "Name (Title)", used as Buyer to target
  public_body            yes | no   (school, university, government)
  consumer_or_self       yes | no   (an individual or self-employed person, not a company)
  structural_no_need     yes | no   (business model has no tech, product, design, or recruiting need we serve; rare)
  no_need_why            required when yes: the business-model cause, e.g. "museum; no software
                         product; IT and web run by an outside vendor". Never "no tech hiring need
                         found": not finding something is an absence of evidence, and the script
                         ignores the code (the row is parked, not dropped).
  can_buy                yes | no | unknown   (budget and complexity to buy professional services)
  ats_type, ats_slug, hiring_source_url
  hiring_checked         ats_api | careers_page | linkedin_jobs | hirebase | search | none_found | not_checked
  open_roles_total, open_tech_roles, open_tech_roles_us   integers from ats_count.py
                         (a "systems engineer" or hardware or device role is not a tech role
                         unless the title has a software marker)
  hiring_examples        up to 3 tech role titles, ";" separated
  tech_role_locations    non_us_tech_locations from ats_count.py when tech roles sit outside the US
                         (offshore roles still count as demand; do not treat them as "not hiring")
  need_signals           ";" list, each "YYYY-MM type: text (source)", type one of
                         funding, new_tech_leader, launch, acquisition, modernization,
                         growth, contraction, ai_initiative. Undated items are left out.
                         Signals from the last 18 months count as a need; contraction never does.
                         funding = an equity raise (venture, growth equity, or private equity)
                         with its month; grants, loans, and IPO follow-ons are growth.
                         Always look for the latest funding round and its month (under 500
                         employees, a round in the last 24 months makes it a Growth startup).
  strength_downgrade     blank or PARENT_UNCLEAR | CONTRACTION | ROLES_STALE (explain in service_fit_why)
  service_fit            Recruiting | Embedded | Scoped | None   (rules below)
  service_fit_why        100 characters or fewer
  segment                fintech | banking_insurance_wealth | faith | proptech_construction | cloud_infrastructure | other
  sources                up to 3 URLs, ";" separated
  research_depth         deep | quick

Person fields (one row per lead_id)
  lead_id
  works_there            confirmed | likely | unknown | no
  works_there_source     e.g. "MoltSets 2026-09 current role", "left Jun 2025 per LinkedIn"
  title_verified         current title, only when a current source differs from the source title
  buyer_role             yes | partial | no | unknown
  buyer_role_why         80 characters or fewer
  vendor_selling         yes | no   (a seller prospecting us)
  job_seeker             yes | no
  email_found            a work email at the company's domain, if you found or confirmed one
  email_found_source     moltsets_reverse | moltsets_name | dropleads | deepline_native | company_site
  email_risk, email_validated_at        copied from MoltSets
  domain_accept_all, bounceban_result, smtp_valid, deepline_verified   copied from Deepline or BounceBan output

Service fit, in this order: Recruiting for open full-time US tech reqs or a talent-team
gap; Embedded for remote or hybrid reqs with a backlog, a launch surge, or contract
language; Scoped for a build, modernization, data, or AI project with no matching reqs;
None when no need was found. Tie-break Recruiting, then Embedded, then Scoped.

Calibration (facts, not labels)
- A 1,771 figure from memory is size_tier C. Say so; record the number, never round it up into a bigger band.
- Deloitte (about 543,000) is an Enterprise company and a real prospect: run the light pass, never skip it.
- MoMA (about 900) is a museum: structural_no_need may be yes; can_buy is not "no".
- An accounting firm is not a competitor. A web and marketing agency is.
- A county MIS Director is a technology buyer at a public body: public_body = yes, buyer_role = partial or yes.
- A visitor who left the company: works_there = no, with the source and month.
- A merged bank: company_key_final is the surviving bank's domain; list both domains.
- Record what you could not check honestly: hiring_checked = not_checked or none_found. The
  script parks those rows for a check; it never drops a row for missing evidence.

Report back in under 200 words: companies done, anything unresolved, paid calls made
(vendor, count, cost). No verdicts.
```

---

## Knowledge triage brief (batches of up to 100 companies)

```
You are triaging companies for Midwestern Interactive's lead qualification run, mostly
from your own knowledge plus at most one quick web check per company. Midwestern sells
recruiting, embedded talent, and scoped software projects to US companies of any size.
Size never drops a company.

Your batch: <run>/work/02-batch-<batch>.csv. Person detail: <run>/work/02-pass1.csv.
Append one row per company (every company in the batch) with:
  python3 <skill>/scripts/append_row.py triage <run>/work/03-triage-<batch>.csv --json '{...}'

Fields: company_key, company_name, what_they_do (one sentence), employees_text,
employees_best (integer or blank), size_tier (always C), us_company (yes | no | unknown),
triage (Keep | Drop), drop_code, why (one short sentence).

drop_code is required for Drop and must be one of:
  COMPETITOR_STAFFING   sells staffing, recruiting, or dev, design, or marketing capacity
  PUBLIC_BODY_NON_BUYER school or government, and the visitor is not a technology or operating buyer
  CONSUMER_SELF_EMPLOYED an individual or self-employed person
  CANNOT_BUY            50 or fewer people and no way to buy professional services
  STRUCTURAL_NO_NEED    a business with no tech, product, design, or recruiting need we serve;
                        why must state the business-model cause, never "no need found"
                        (that is not evidence: Keep the company instead)
  NOT_US                not a US company and no US buying team
  UNIDENTIFIABLE        you cannot tell which company this is
There is no size drop code: a large company is never dropped for its size.

Guardrails (the script rejects anything else)
- CANNOT_BUY only at 50 or fewer employees. A mid-size company with no need is STRUCTURAL_NO_NEED.
- A row flagged rb2b_size_flag = rb2b_says_over or known_large: confirm which company it is and
  record your size estimate, then Keep it (unless another drop code applies). RB2B's size is
  not evidence.
- An MSP, IT services firm, dev shop, or consultancy is COMPETITOR_STAFFING (peer vendor).
- When unsure whether a real company could buy, Keep.

Work sequentially, no sub-agents, no planning docs, no dashes in cells. Report back in
under 150 words: Keep and Drop counts, the Keeps with one line each.
```

After triage, run `python3 scripts/classify.py keeps --run <run>` to batch the Keeps, then send those batches through the deep research brief.
