# Validation Artifact Templates

Two artifacts come out of a validation run:

1. The validation findings doc (new file in the ICP project's `working/` folder).
2. The sharpened sales questions doc (append to an existing file if present; create if not).

Both write through the Obsidian MCP. Path prefix is `Main/` (the server is rooted at the `Vaults/` parent).

---

## 1. Validation findings doc

**Location:** `Main/1_Projects/ICP Research/<vertical>/working/06-hubspot-validation.md`

If a prior phase already used `06-`, increment (07-, 08-, ...). Default is `06-` to match the shipped precedent.

**Frontmatter:**

```yaml
---
date: <YYYY-MM-DD>
tags:
  - icp-research
  - <vertical-slug>
  - sales-validation
type: icp-research-artifact
status: draft
phase: 6
project: "[[ICP Research <vertical>]]"
---
```

**Body structure (use these section names verbatim; the order matters):**

```markdown
# HubSpot Validation: <vertical>

<one-paragraph opener: how many sub-agents, how many deals enriched, how many in target industries, breakdown by win/loss/no-go/active. Call out the engagement-log state in the opener if empty. Confidence framing.>

## Bottom line
<numbered list, 3 to 6 items. Top-level findings only. Include the vertical-agnostic framing here if it emerges from the data; do not bury it. Each item is a sentence or two, evidence-grounded.>

## Confirmed (with evidence)
<bullets. Each confirmed claim from the draft ICP gets a bullet with the deal evidence that confirms it. Company names and deal amounts, not generic patterns. Distinguish wins (direct validation), losses (contrastive validation), and active deals (forward signal).>

## Refinements to the draft ICP
<numbered list. Concrete, evidence-backed changes the human reviewer should consider. Each refinement names the evidence (specific deals, IDs, amounts, contacts). Refinement categories to cover when the data supports them:
  1. Size band (floor / ceiling / sweet spot)
  2. Gate adjustments (tightening or loosening hard exclusions)
  3. New tiers (e.g. a partner-channel segment)
  4. Trigger taxonomy (replace vague triggers with named, evidence-backed ones)
  5. Buyer-title hierarchy (who lands, who blocks)
  6. Service-line segmentation (if a different service line wins different deals)
  7. Exclusions to add (companies the data shows are structurally non-fit)
>

## Surprises and open questions
<bullets. Anomalies, outliers, single-data-point findings that need a human read. Do NOT put the vertical-agnostic finding here; that goes in Bottom line.>

## Active pipeline reality check
<short section. Top N active deals, their amounts and verticals. Explicit call-out if zero target-vertical deals are in the active pipeline. The point is to make the sales meeting honest about starting state.>

## Data hygiene flag
<REQUIRED. Even if engagements exist, state what was found. If the log is empty, state it explicitly and say where the qualitative "why won / lost" must now come from. Include any proxy-deal flags, domain mismatches, or other data-quality issues spotted during enrichment.>

## Confidence summary
<bulleted by tier:
- **[HIGH]**: claims with multiple repeat-account evidence or structural proof
- **[MEDIUM]**: claims with directional but limited evidence (small n, single data point patterns)
- **[LOW]**: claims with one weak data point
- **[UNKNOWN, sales meeting required]**: claims that need qualitative input that CRM cannot provide>
```

---

## 2. Sharpened sales questions doc

**Location:** `Main/1_Projects/ICP Research/<vertical>/Questions for Sales.md`

(Or wherever the prior phases placed it. Search the project folder first.)

**Behavior: append-if-exists, create-if-not.**

- **If the file exists:** append a new section. Do not overwrite. Do not modify existing question numbering. Use a dated section header.
- **If the file does not exist:** create it with frontmatter, a short purpose paragraph, then the HubSpot-grounded section.

**Append section template (use this header verbatim, including the date):**

```markdown
---

## Sharpened by HubSpot deal history (added <YYYY-MM-DD>)
Specific deals to bring to the meeting. Each one is grounded in actual CRM data.

<N>. **<Short title for the question or finding.>** <Context paragraph naming specific companies, deal IDs or amounts, contact titles, and what the CRM data shows.> <The question to ask sales, usually about the "why" the CRM cannot answer.>

<continue numbering from where the existing doc left off, or start at 1 if creating new>
```

**Question categories to generate from the validation findings (one or two questions per category when the evidence supports them):**

1. **The real wins in the target vertical.** Name the specific companies, deal counts, amounts, and buyer titles. Ask sales what made them land.
2. **The losses in the target vertical.** Name the specific lost deals, contact title, amount. Ask sales whether wrong-door routing or something structural killed it.
3. **Active target-vertical deals.** Name the specific active deals if any, with amounts and contact titles. Ask sales what they actually are (engineering vs. marketing vs. IT, etc.).
4. **The biggest recent loss in any vertical.** Name it, with amount and contact title. Ask what killed it and whether the pattern is structural.
5. **The vertical-agnostic question.** If wins cluster across verticals, ask explicitly whether the target-vertical push should narrow or broaden.
6. **The active pipeline reality.** Name the top active deals (vertical, amount). Ask whether the target-vertical push starts from a fresh pipeline by design or by default.
7. **Partner-channel segment (if visible in data).** Name the companies and the recurring buyer. Ask whether this is a deliberate channel to formalize.
8. **Data hygiene as a separate question.** If the engagement log is empty, ask separately how to close that gap going forward. Frame as process improvement, not as part of the ICP question.

**Frontmatter for new file (use only if creating fresh):**

```yaml
---
date: <YYYY-MM-DD>
tags:
  - icp-research
  - <vertical-slug>
  - sales-enablement
type: sales-questions
project: "[[ICP Research <vertical>]]"
---
```

---

## 3. ICP refinement application: gated, not automatic

`outputs/draft-icp-hypothesis.md` is **not** auto-edited by this skill.

The flow is:

1. Skill writes the validation doc with `## Refinements to the draft ICP`.
2. Skill stops and surfaces the refinements list to the human.
3. Human reviews, accepts or rejects each refinement.
4. **Only on explicit go** does the skill (or a follow-up) edit the hypothesis doc.

When the go comes, edit the hypothesis through the Obsidian MCP (`mcp__obsidian__edit_note` or `mcp__obsidian__write_note` with the existing content preserved). Preserve frontmatter. Add a dated note in the hypothesis doc explaining what changed and link back to the validation doc with a path-qualified wikilink:

```
[[1_Projects/ICP Research/<vertical>/working/06-hubspot-validation|06-hubspot-validation]]
```
