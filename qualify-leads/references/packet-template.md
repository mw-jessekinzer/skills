# Lead packet template

One packet per Tier 1 company that is not in `work/06-enrich-skipped.csv`. Save it as `<run>/Packets/<packet_file>`, using the exact `packet_file` value from `work/06-tier1.csv` (the company name with path characters such as "/" and ":" removed; the gates match on it).

Target: one screen plus the committee table, about 250 to 450 words of prose. Small on purpose.

**Never include:** connection notes, LinkedIn messages, email drafts, DMs, call scripts, a numeric score. If JK asks for a message in a given run, that is a separate one-off request.

**Facts come from the work files, not memory:** headcount, roles, and CRM text from `work/05-qualified.csv` and the research rows; committee emails and **email status copied from `python3 <skill>/scripts/committee_status.py --run <run> --company <company_key_final>`** (read only). That is the same string the CSV and `08-committee-status.csv` carry: the visitor's status comes from the visitor's CSV row, and a committee member already in HubSpot reads "From HubSpot". Packet workers never run `assemble.py`; the orchestrator runs it once after all packets, and gate 4 compares every packet email and status with it.

**Copy rules:** brand voice from the Marketing Hub's Messaging Patterns note. No "brokers", "staffing firm", "staffing partner", or "outsource". No em dashes, en dashes, or " -- ". No contrast flips ("didn't X; it Y"), no "isn't X, it's Y", no validation openers. Quote "How this account reached us" verbatim from the `What they did` column; RB2B proves a page view only, so never write "submitted", "requested", or "filled out" unless the touch was a form fill. Use the proof points from the Hub's Proof Points note as written: full-time roles recruited in under 3 weeks (under 15 business days); embedded talent placed onto a team in under 2 weeks (under 10 business days).

## Template

```markdown
---
tags:
  - lead-triage
  - lead-packet
date: YYYY-MM-DD
type: reference
status: ready
project: "[[1_Projects/Lead Triage/00 - readme|Lead Triage]]"
summary: <one sentence: who they are, why now, and the action>
---

# <Company>, lead packet

For [[<Owner>]] as of YYYY-MM-DD. Action: <Contact now | Account play>.
(When there is no active HubSpot owner: "Owner: Jesse Kinzer until assigned; segment owner <name>.")

## Overview
<2 to 3 sentences: what they do, domain, HQ, headcount with its source and month.>
How this account reached us: <What they did, verbatim>, <touch date>.
<The CRM status sentence from the CSV.>

## Open roles
<N open, M tech, K in the US, counted YYYY-MM-DD from <job board URL>.>
- <Role>, <location>, posted YYYY-MM-DD   (up to 7 tech roles)

## Funding
<Latest dated round: amount, lead investor, month. "No round found" is fine. Mark anything unconfirmed as unconfirmed.>

## Buying committee
| Order | Name | Title | Role in decision | Email | Email status | LinkedIn |
|---|---|---|---|---|---|---|
| 1 | <name> | <title> | <role> | <email or blank> | <status from 08-committee-status.csv> | <url> |

## Angle
- <Lead service and why, citing the hiring or need evidence>
- <A second fit, if any>
- <One proof point where it fits>

## Watch-outs
- <CRM ownership to fix, people who may have left, name collisions, onsite rules, anything unconfirmed>
- <Copy the CSV's Watch-outs cell when it has one, e.g. tech roles all outside the US, so the fit may be embedded global talent.>
- Don't mention the website visit. (RB2B rows only.)

## Sources
- <up to 5 URLs>
```

## Filled example (Pulley, from the 2026-09-27 follow-on, trimmed)

```markdown
# Pulley, lead packet

For [[Jonathan Gonzalez]] as of 2026-09-25. Action: Contact now.

## Overview
Pulley (withpulley.com) runs AI-assisted construction permitting for builders and developers from San Francisco. About 100 employees per Tracxn (May 2026).
How this account reached us: Viewed the homepage from LinkedIn, 2026-09-08.
HubSpot company record, unowned, subscriber stage; this person is a HubSpot contact owned by Jonathan Gonzalez.

## Open roles
23 open, 7 tech, 7 in the US, counted 2026-09-25 from the Ashby job board.
- Staff AI Engineer, San Francisco, posted 2026-09-21
- Senior Software Engineer, San Francisco, posted 2026-07-28

## Buying committee
| Order | Name | Title | Role in decision | Email | Email status | LinkedIn |
|---|---|---|---|---|---|---|
| 1 | Charlie Jacobson | Co-Founder and CEO | Economic buyer (the visitor) | charlie@withpulley.com | Verified | linkedin.com/in/charliejacobson |
| 2 | Michellie McDonald-O'Brien | Talent and People Ops Lead | Talent owner | michellie@withpulley.com | Verified | linkedin.com/in/michellie |

## Angle
- Recruiting first: seven US tech reqs at once, including a Senior Technical Recruiter, points to a talent team stretched thin.
- Full-time roles recruited in under 3 weeks is the proof point to lead with.

## Watch-outs
- The company record is unowned; the contact belongs to Jonathan Gonzalez. Claim the company record before outreach.
- pulley.com is a different company (cap tables). Check the domain on every contact.
- Don't mention the website visit.
```
