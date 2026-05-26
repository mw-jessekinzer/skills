# README Template (copied to project README.md)

When scaffolding, write this to `Main/1_Projects/ICP Research/<vertical>/README.md` via the Obsidian MCP. The `status:` and `phase:` frontmatter fields are the resume markers: update them at every gate.

`status:` values, in order: `intake`, `plan-pending-approval`, `enriching`, `enrichment-review`, `patterns-pending-approval`, `rubric-and-draft`, `draft-pending-review`, `complete`.

```markdown
---
date: <YYYY-MM-DD>
tags:
  - icp-research
  - <vertical-slug>
type: icp-research-readme
status: intake
phase: 0
project: "[[ICP Research <vertical>]]"
---

# ICP Research: <vertical>

Research-backed Draft ICP Hypothesis for the <vertical> vertical, built from an AE account list. This is a draft for human review, not a final ICP.

## Where this stands
- **Current phase:** 0 (Intake)
- **Waiting on:** JK to drop `inputs/accounts.csv` and fill `inputs/context.md`, then say "go".

## How to use this folder
- `inputs/` holds the raw account list and JK's context. Claude reads, never rewrites, these.
- `working/` holds intermediate research artifacts (Phases 0 to 5). Every claim there carries a confidence label and sources.
- `outputs/` holds the Draft ICP Hypothesis only, written after Gate 4.

## The flow
0. Intake summary and clarifying questions
1. Research plan (Gate 1)
2. Account enrichment (Gate 2)
3. Buying committee analysis
4. Pattern analysis (Gate 3)
5. Fit scoring rubric
6. Draft ICP Hypothesis (Gate 4)

## Artifacts
- [[1_Projects/ICP Research/<vertical>/working/00-intake-summary|00-intake-summary]]
- [[1_Projects/ICP Research/<vertical>/working/01-research-plan|01-research-plan]]
- [[1_Projects/ICP Research/<vertical>/working/02-enriched-accounts|02-enriched-accounts]]
- [[1_Projects/ICP Research/<vertical>/working/03-buying-committee|03-buying-committee]]
- [[1_Projects/ICP Research/<vertical>/working/04-patterns|04-patterns]]
- [[1_Projects/ICP Research/<vertical>/working/05-fit-rubric|05-fit-rubric]]
- [[1_Projects/ICP Research/<vertical>/outputs/draft-icp-hypothesis|draft-icp-hypothesis]]
```

**Use path-qualified wikilinks** (full vault path plus a clean display alias, as above) for every cross-reference between ICP artifacts. Artifact filenames repeat across verticals (every project has a `00-intake-summary`, etc.), so a bare `[[00-intake-summary]]` is ambiguous once a second vertical exists. The path qualifier resolves it; the alias keeps it readable. Links are dangling until each phase creates the note, which Obsidian handles fine.
