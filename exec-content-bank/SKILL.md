---
name: exec-content-bank
description: Use when JK wants LinkedIn or Instagram content ideas, a post idea bank, hooks, lead magnets, or a thought-leadership content plan for any person at Midwestern (the CEO, an SLT member, another leader, or JK himself), especially when the ideas should be mined from real sources like the vault, meetings, Granola, Slack, sales calls, or the person's own LinkedIn. Also use when extending or refreshing an existing content bank.
---

# Exec Content Bank

## Overview

Build a large, sourced bank of LinkedIn and Instagram ideas for one person, using Hormozi's method: give away useful knowledge their audience needs, keep giving, and let them ask to pay. Every idea traces to a real source, so nothing is invented.

The skill is person-agnostic. Everything specific to the person (audience, niche, voice, channels, home folder, existing ideas) goes into a **person profile** that you build first. The worker briefs in `references/worker-briefs.md` read only from that profile.

You are the orchestrator. Parallel workers each mine one source into their own research file. An Opus worker synthesizes, and a separate Sonnet worker reviews. Keep raw research out of your context.

## Before dispatch

1. **Look for existing work first.** Search the vault for the person's name together with "content idea bank", "post ideas", "personal brand", "through-line", or "swipe file". If a bank built by this skill exists (it has a `.build/` folder), use "Extending a bank" below. Other idea lists and drafts become `{EXISTING}` in the profile.
2. **Build the person profile.** Fill each field from the vault. Every brief uses these fields.

   | Field | Where to look | Default when nothing is found |
   |---|---|---|
   | Name, title | `job-title` in `People/<Name>.md`, then the Slack profile title | Ask JK |
   | Audience | The person's own positioning notes (niche, through-line, bridge) | Midwestern's buyers, from the Hub's service-line ICPs. Confirm with JK, because the person's expertise (for example, sales leadership) may point to a different audience |
   | Niche and through-line | The same positioning notes | "None defined yet" |
   | Bridge to Midwestern | A bridge note, or the ICPs | How this audience's problems lead to Scoped, Embedded, or Recruiting |
   | Channels | Positioning notes, or the accounts that actually exist | LinkedIn and Instagram |
   | Voice | A profile or voice note for the person (search `4_References/` and `People/`) | Derive it from the LinkedIn audit and meetings |
   | Home folder | An existing personal-brand or project folder for the person | `1_Projects/<Name> Content Ideas/` |
   | LinkedIn URL, Instagram handle | The vault, or the tab JK has open | Ask JK |
   | Slack ID | `slack_search_users` | Skip the Slack brief |
   | Social owner | `1_Projects/Social Team Ownership & Lanes/`, and the Hub's Executive Social roster | Ask JK |

   Ask JK when:
   - a value is missing,
   - two sources disagree (for example, the Slack title differs from the People note), or
   - a title conflicts with what the meetings show (for example, a "Sales Manager" title for someone who sits on the SLT).

   Put all the questions into one AskUserQuestion. Never guess a title or an audience. If the person is JK himself, still ask him, and phrase each question as a decision about his own account.

   Some sources can come back thin: a niche audience that rarely appears on sales calls, or a person with few meetings. Keep the brief anyway, and tell JK to expect fewer results from it. If no LinkedIn URL is available, hold the LinkedIn brief until JK gives one. Do not skip it.
3. **Preflight every source with one cheap call each,** in parallel:
   - Granola: `get_account_info`
   - Slack: `slack_search_users`
   - Airspeed MCP: if it is down, the REST fallback in the sales-call brief works.
   - Mail: `list_zapier_connections` with `selected_api: "GoogleMailV2CLIAPI"`, or any Gmail MCP.
   - Browser: `ego-browser nodejs -e 'console.log((await listTaskSpaces()).length)'`, run with `dangerouslyDisableSandbox: true`. Inside the sandbox the call fails with "Failed to connect to ego_cli bootstrap". The LinkedIn and Instagram workers need the same flag.

   Tell JK in one line which sources are missing. A missing source is a gap to report. It is not a reason to stop.
4. **Set up the home folder.**
   - A new folder gets `00 - readme.md` (what it is, where to start, sources mined, work log) and a `Research/` subfolder.
   - If the home folder already exists (such as a personal-brand folder), put the bank in a `Content Idea Bank/` subfolder with its own readme. Do not scatter files in the parent folder.
   - Update the work log after each phase.

## Phases

| Phase | Workers (model) | Output |
|---|---|---|
| 1. Research, all in parallel | LinkedIn audit, Vault, Meetings voice, Sales calls, Slack (all `sonnet`). Add Instagram only when the channels include it and a handle exists. Add Email only when a mail connector exists | `Research/01` to `07` |
| 2. Synthesis | one `opus` worker | `.build/` data, `01 - Content Idea Bank.md`, `Exports/*.csv` |
| 3. Review | one `sonnet` worker, independent of synthesis | fixes in `.build/`, rebuilt outputs |
| 4. Verify and close | you | readme log, memory, report |

Pass `model` on every Agent call. Named agent types inherit the parent model otherwise.

## Extending a bank

Use this path for a narrow request, such as "add about 15 ideas on X from Slack". Do not run the full Phase 1 for it.

1. Dispatch research only for the named source and time window. Write to a new research file (for example `Research/05b - Slack Mining (<topic>, <dates>).md`). Never overwrite the existing research files.
2. Write the new idea blocks into `.build/ideas.txt`, yourself or with one `sonnet` worker. Use `opus` synthesis only for a large refresh (50 or more ideas, or new pillars).
3. Append the new blocks at the end of the matching pillar, just before the next `#P` line. IDs come from position, so this is the only safe place. Never reorder or delete existing blocks: posts may already be scheduled by ID.
4. Run one `sonnet` review scoped to the new keys. Then run `build`, and confirm that the existing IDs still map to the same topics.

## The generator

`scripts/build_bank.py` renders the note and both CSVs from `.build/config.json`, `.build/ideas.txt`, and `.build/prose.md`, so the markdown and the CSVs cannot drift apart. In `config.json`:
- `"channels": ["linkedin"]` drops the Instagram column and the Instagram CTAs.
- `audience_label` names the audience in the pillar table.
- `project_link` points the frontmatter at the folder's readme. Use the full path (for example `[[1_Personal Social Brand/Content Idea Bank/00 - readme]]`), because many folders have a note named "00 - readme".

The build exits 1 on dashes, banned words, bad lead magnet references, or schema errors. It warns on trope patterns and stage-mix drift.

```bash
python3 ~/.claude/skills/exec-content-bank/scripts/build_bank.py init  "<home>" --exec "<Full Name>"
python3 ~/.claude/skills/exec-content-bank/scripts/build_bank.py build "<home>"
```

The data lives in the home folder's `.build/` directory. It is hidden from Obsidian, and it survives the session. Never hand-edit the rendered tables: Obsidian may reformat them, and the next build overwrites them.

## Phase 4: verify before reporting

- Run `build` yourself. It must exit 0. Read every WARN line.
- Read the Top 20 and 10 random rows. Check that the hooks match the profile's voice, that the ideas serve the profile's audience, and that every Source is specific.
- Log the results in the readme. Save or update a project memory with the Write tool (Bash cannot write to the memory folder).
- Report in plain language: counts, what was verified, source gaps, the items that need the person or client permission, and at most one decision for JK.

## Guardrails (put these in every brief)

- Proof points only in the exact wording of the `[[Proof Points]]` note. Find the note by search, because notes move.
- Hooks are written as the person, in the person's voice. Claims about Midwestern follow `[[Messaging Patterns]]`.
- Never write "broker". Do not frame Midwestern as an agency, a vendor, a staffing firm, or an outsourcer.
- No client names in hooks. Anonymize them and add "(needs client OK to name)".
- Attribute a quote only when the transcript names the speaker. Otherwise mark it "(confirm speaker)".
- Nothing from any DO NOT POST list: HR, compensation, pricing and fees, departures, M&A, legal, medical, negative client feedback.
- No em dashes or en dashes. No contrast-flip hooks. The humanizer runs in review.

## Common mistakes

| Mistake | Fix |
|---|---|
| Assuming the audience is tech buyers | Build the profile first. A person with their own niche gets their niche's audience |
| Missing the person's existing ideas and drafts | Search for them in step 1 and pass them to every worker as `{EXISTING}` |
| Picking meetings from a People note for someone who attends almost every meeting | Use the meetings brief's topic-based selection |
| Hardcoding vault paths in briefs (Proof Points was not where a brief said) | Tell workers to find files by search and the Hub Index |
| Finding a missing source (such as email) only after dispatch | Preflight every source first |
| Keeping the generator in the session scratchpad, which is lost when the session ends | Use `scripts/build_bank.py`, with the data in the home folder's `.build/` |
| Crediting "Speaker A" quotes to the person | Apply the speaker rule. The reviewer checks quotes against the original transcripts |
| Letting the synthesis worker grade its own copy | A separate reviewer runs the humanizer and the three-question test |
| Posting podcast promos as content | Turn each episode into a standalone lesson post |
| Renumbering ideas after the bank is shared | Append new ideas at the end of a pillar, because IDs come from order |
