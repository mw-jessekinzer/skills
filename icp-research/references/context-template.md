# Context Template (copied to inputs/context.md)

When scaffolding, write this to `Main/1_Projects/ICP Research/<vertical>/inputs/context.md` via the Obsidian MCP. Replace `<vertical>` and `<vertical-slug>` and set today's date. Leave the answer lines for JK to fill.

```markdown
---
date: <YYYY-MM-DD>
tags:
  - icp-research
  - <vertical-slug>
type: icp-research-context
project: "[[ICP Research <vertical>]]"
---

# Context: <vertical>

Fill in what you know. Leave blanks rather than guessing. Optional fields can stay empty. Claude reads this before researching.

## Vertical
<what vertical is this account list for>

## Service line emphasis
<Embedded Teams / Scoped Projects / Recruiting / all>

## Known closed-won examples (optional)
<company names plus a one-line why-they-fit, if any>

## Known bad-fit examples (optional)
<company names plus a one-line why-they-failed, if any>

## Must-include account types (optional)
<traits or categories that should always count as in-scope>

## Must-exclude account types (optional)
<traits or categories that disqualify an account>

## HubSpot or sales data (optional)
<paste relevant deal status, closed-won/lost, sales notes, or engagement history>

## Anything else Claude should know
<company stage, recent shifts, constraints, sales intuition to test>
```
