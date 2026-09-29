# Common Gotchas (HubSpot ICP Validation)

The traps that bite anyone running this workflow for the first time. Read this once before the run; refer back when something goes sideways.

---

## 1. `chatInsights` is required on every `search_crm_objects` call

Every call to `mcp__hubspot__search_crm_objects` must include a `chatInsights` parameter with `userIntent` and `satisfaction` fields. Missing it returns a validation error with no useful hint about the cause.

**Fix:** include the block on every call.

```json
{
  "chatInsights": {
    "userIntent": "Filter deals in target-industry companies to validate the ICP",
    "satisfaction": "neutral"
  }
}
```

The values are not load-bearing for results; just satisfy the schema.

---

## 2. HubSpot industry values are UPPER_SNAKE_CASE

The `industry` and `hs_industry_group` properties accept enumerated strings, not free text, and not the human-readable label. Searching for `Real Estate` returns nothing. Use `REAL_ESTATE`.

Common codes for tech / RE / construction ICP work:

- `REAL_ESTATE`
- `CONSTRUCTION`
- `COMPUTER_SOFTWARE`
- `INFORMATION_TECHNOLOGY_AND_SERVICES`
- `INTERNET`
- `FINANCIAL_SERVICES`
- `MARKETING_AND_ADVERTISING`

When the target vertical is unclear, query a sample of companies first and read their actual industry values back, then build the filter list.

---

## 3. Large result sets auto-save to a file

When `search_crm_objects` returns a result set bigger than the chat token budget, the MCP writes the JSON to a file under `/tmp/` (or similar) and returns the path instead of the data. Reading the file directly back into context recreates the same overflow.

**Fix:** use `jq` to slice fields out of the saved file. Examples:

```bash
# Just deal IDs, amounts, stages, names
jq '.results[] | {id, name: .properties.dealname, amount: .properties.amount, stage: .properties.dealstage, pipeline: .properties.pipeline}' /tmp/<file>

# Count by pipeline
jq '[.results[].properties.pipeline] | group_by(.) | map({pipeline: .[0], count: length})' /tmp/<file>

# Filter to one pipeline's closed-won deals
jq '.results[] | select(.properties.pipeline == "<id>" and .properties.hs_is_closed_won == "true")' /tmp/<file>
```

Build small, targeted projections; never re-read the full file.

---

## 4. Multiple pipelines coexist; win and loss stages differ per pipeline

A mature HubSpot account usually has more than one deal pipeline live at once. A typical pattern: a default / historical pipeline, an older sales motion (e.g. recruiting), and the current active pipeline. Each has its own stages with different internal IDs, and "closed won" / "closed lost" map to different stage IDs per pipeline.

**Never hardcode stage IDs.** Derive them from the data:

1. Pull a sample of deals across the target population.
2. Group by `pipeline`. Note the count per pipeline.
3. For each pipeline, list distinct `dealstage` values and inspect a couple of deals per stage to identify what "closed won" / "closed lost" / "stalled $0" actually are.
4. Build the bucketing rule from that, not from assumptions.

The most reliable cross-pipeline signal is `hs_is_closed_won` (boolean), combined with `amount` to separate genuine losses from no-go / stalled $0 deals.

---

## 5. The engagement log may be empty

`NOTE`, `CALL`, and `EMAIL` are first-class CRM objects in HubSpot, associated to deals. In well-run accounts they hold the qualitative "why won / lost" detail. In many accounts they hold nothing: sales reps work from memory, or use a separate tool, or skip logging entirely.

If sub-agents enrich deals and find zero engagements across the dataset, that is a real finding, not a bug. Two consequences:

1. The "why won / lost" qualitative layer must come from sales conversation, not from CRM. Flag this in the sharpened sales questions doc.
2. The output validation doc must include an explicit `## Data hygiene flag` section calling out the empty log. Do not bury it; do not skip it because deal names "told us enough."

---

## 6. Deal-name prefix parsing is the practical service-line tag

When the CRM lacks a structured service-line field, deal names are the fallback signal. Midwestern's deal-name convention prefixes the service line:

- `Embedded` (e.g. "Embedded - Senior .NET Engineer")
- `Direct Placement` (e.g. "Direct Placement - Product Engineer")
- `Scoped` (e.g. "Scoped - AI Imaging Pilot")
- `Marketing Site` (e.g. "Marketing Site - Schuber Mitchell")

This is fragile (typos, missing prefixes, mixed conventions across reps), but it is the most consistent signal available. Two rules:

1. Treat parsed service lines as inferences, not verified facts. Confidence: `[MEDIUM]` at best.
2. Tune the prefix list to your own org's deal-naming convention if you are not at Midwestern.

---

## 7. The vertical-agnostic framing is a real, surfaceable finding

When wins cluster across multiple verticals (not just the target one), the underlying winning ICP is broader than the vertical being researched. This emerges naturally when you bucket deals: wins span faith / nonprofit, marketing, automotive, AI, IT services, plus the target.

This is not a "surprise" or a footnote. It is a load-bearing strategic question for the human reviewer. Surface it in the validation doc's `## Bottom line` and again in the sharpened sales questions. Do not bury it under `## Surprises`.

---

## 8. Proxy / referral deals contaminate the signal

A deal can be attached to one company but actually be a referral or proxy for another (a vendor selling to a vendor's end client, a contact whose email domain does not match the associated company). These look like normal records in the data and produce misleading patterns.

Signal: the primary contact's email domain does not match the associated company's domain.

When you spot one, flag it as a data-quality issue, not an ICP signal. Do not drop it from counts; do label it.

---

## 9. Sub-agents must not bypass JK's standing config

Per JK's standing preference, research / enrichment sub-agents run on `model: sonnet` with high thinking effort. The `Agent` tool has no thinking-effort parameter, so the high-effort instruction must be embedded in the sub-agent prompt itself.

The sub-agent brief template in this skill bakes both in. If you write a custom dispatch prompt instead of using the template, you must re-bake them. Silently inheriting the parent model is a violation of the standing config.

---

## 10. `outputs/draft-icp-hypothesis.md` is not auto-edited

The skill's job is to produce a refinement list (with evidence) inside the validation doc. Editing the original ICP hypothesis is a separate, gated action: the human reviewer decides which refinements to accept, then either updates the hypothesis themselves or asks the skill to apply them.

Do not silently rewrite `outputs/draft-icp-hypothesis.md`. The chain is:

1. Skill produces validation doc with `## Refinements to the draft ICP` section.
2. Human reviews.
3. Human approves a subset.
4. Hypothesis is updated as a separate, explicit action.
