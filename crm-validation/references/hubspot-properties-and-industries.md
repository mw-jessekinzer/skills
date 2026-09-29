# HubSpot Property + Industry Quick Reference

Property names and industry codes the validation workflow leans on. Sourced from working runs; refresh against `search_properties` when in doubt.

---

## Property discovery: how to find what you need

HubSpot accounts customize properties heavily. Do not assume a property exists. Use the discovery tool first:

```
mcp__hubspot__search_properties
  objectType: "0-3"  # 0-3 = deal, 0-2 = company, 0-1 = contact
  query: "industry"  # or "won", "lost", "employees", etc.
```

Search by keyword, read back the property names that match, then build filters from those names. The names below are what the workflow typically lands on, but verify in your tenant.

---

## Deal properties (objectType `0-3`)

Core fields for bucketing and analysis:

| Property | What it holds | Notes |
|---|---|---|
| `dealname` | Deal title | Parse for service-line prefix and company hint |
| `amount` | Deal value (USD) | String in API; cast to number for analysis |
| `dealstage` | Stage ID (per pipeline) | Internal ID, not label; map via pipeline definition |
| `pipeline` | Pipeline ID | Multiple pipelines coexist; bucket by this |
| `hs_is_closed_won` | Boolean (string `"true"`/`"false"`) | Most reliable cross-pipeline win marker |
| `closedate` | Close date | ISO; use for recency analysis |
| `createdate` | Creation date | ISO |
| `dealtype` | Deal type | New business vs. existing |
| `closed_lost_reason` | Lost-reason text | Often empty in practice; verify before relying |
| `closed_won_reason` | Won-reason text | Same caveat |
| `num_associated_contacts` | Contact count | Cheap signal for committee size |

---

## Company properties (objectType `0-2`)

| Property | What it holds | Notes |
|---|---|---|
| `name` | Company name | Verify against `domain` for proxy-deal detection |
| `domain` | Company domain | Cross-check contact email domain |
| `industry` | Industry code | UPPER_SNAKE_CASE enum (see codes below) |
| `hs_industry_group` | Broader industry grouping | Use when `industry` is too granular |
| `numberofemployees` | Headcount | Often stale; sanity-check against LinkedIn for ICP-critical accounts |
| `annualrevenue` | Revenue | Frequently empty; do not rely |
| `num_associated_deals` | Deal count on this company | Filter universe with this `> 0` |
| `lifecyclestage` | Lifecycle stage | Customer / lead / etc. |
| `hs_lead_status` | Lead status | Custom values vary by tenant |

---

## Contact properties (objectType `0-1`)

| Property | What it holds | Notes |
|---|---|---|
| `firstname`, `lastname` | Name |  |
| `email` | Email | Check domain against company domain to flag proxy deals |
| `jobtitle` | Job title | Primary buying-committee signal |
| `hs_lead_status` | Lead status | Custom values |

---

## Engagement objects

| Object | objectType | What it holds |
|---|---|---|
| Note | `0-46` | Free-text rep notes attached to a deal |
| Call | `0-48` | Logged call summaries |
| Email | `0-49` | Logged email threads |

Pull these via `get_crm_objects` with the associated deal ID. If counts come back zero across the sampled deals, the engagement log is empty: flag it and shift the "why won / lost" question to the live sales conversation.

---

## Industry codes (UPPER_SNAKE_CASE)

The `industry` property accepts an enumerated value, not free text. Filtering with the human-readable label returns nothing.

**Tech + adjacent (most common targets):**
- `COMPUTER_SOFTWARE`
- `INFORMATION_TECHNOLOGY_AND_SERVICES`
- `INTERNET`
- `COMPUTER_HARDWARE`
- `COMPUTER_NETWORKING`
- `SEMICONDUCTORS`

**Real estate / construction / built environment:**
- `REAL_ESTATE`
- `CONSTRUCTION`
- `COMMERCIAL_REAL_ESTATE`
- `ARCHITECTURE_AND_PLANNING`
- `CIVIL_ENGINEERING`
- `BUILDING_MATERIALS`

**Financial services / fintech:**
- `FINANCIAL_SERVICES`
- `BANKING`
- `INSURANCE`
- `INVESTMENT_MANAGEMENT`
- `VENTURE_CAPITAL_AND_PRIVATE_EQUITY`

**Marketing / media:**
- `MARKETING_AND_ADVERTISING`
- `ONLINE_MEDIA`
- `PUBLISHING`

**Other recurring:**
- `HEALTH_WELLNESS_AND_FITNESS`
- `HOSPITAL_AND_HEALTH_CARE`
- `MANAGEMENT_CONSULTING`
- `NONPROFIT_ORGANIZATION_MANAGEMENT`
- `EDUCATION_MANAGEMENT`

If the target vertical's exact code is unclear, pull a sample of `companies` (5 to 10) you know are in that vertical and read their `industry` values back. Build the filter list from real data.

---

## Service-line prefix parsing (Midwestern-specific)

When the CRM lacks a structured service-line field, deal-name prefixes are the fallback. Midwestern's convention:

| Prefix in `dealname` | Service line |
|---|---|
| `Embedded` | Embedded Teams |
| `Direct Placement` | Recruiting / Direct Placement |
| `Scoped` | Scoped Projects |
| `Marketing Site` | Marketing / web work |

Treat parsed values as inferences, not facts. Tune the list for your org if you are not at Midwestern.

---

## Quick filter snippets

**Companies in target industries with deal history:**

```
search_crm_objects (objectType: "0-2")
  filterGroups:
    [{ filters: [
        { propertyName: "industry", operator: "IN", values: ["REAL_ESTATE","COMPUTER_SOFTWARE","INTERNET"] },
        { propertyName: "num_associated_deals", operator: "GT", value: "0" }
      ]}]
  properties: ["name","domain","industry","hs_industry_group","numberofemployees","num_associated_deals"]
  limit: 200
  chatInsights: { userIntent: "...", satisfaction: "neutral" }
```

**Deals associated with a set of company IDs:**

```
search_crm_objects (objectType: "0-3")
  filterGroups:
    [{ filters: [
        { propertyName: "associations.company", operator: "IN", values: ["<companyId1>","<companyId2>",...] }
      ]}]
  properties: ["dealname","amount","dealstage","pipeline","hs_is_closed_won","closedate","createdate","dealtype"]
  limit: 500
  chatInsights: { ... }
```

**Pre-flight access check (no data pulled):**

```
mcp__hubspot__get_user_details
```

Verify the response shows read scopes on `DEAL`, `COMPANY`, `CONTACT`, `NOTE`, `CALL`, `EMAIL`. If any are missing, stop and tell the user before pulling data.
