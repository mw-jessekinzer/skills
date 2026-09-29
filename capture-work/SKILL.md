---
name: capture-work
description: Turn Jesse's messy natural-language work thoughts (typed or spoken, often from mobile) into well-formed Linear issues with title, owner, project, work date, and context. Use whenever Jesse wants work in Linear, even without saying "Linear" or "capture", such as "add something for Monday to...", "capture this", "make an issue for", "ticket that", "throw this on my list", "I need to remember to...", "remind me to...", "have Cole...", "before my meeting Thursday I need to...", "sometime next week I should...", and bare imperatives with no capture verb ("ping Kent about the lead list tomorrow", "landing page copy needs a first pass before Thursday"). Also for "capture that" about work described earlier, and voice ramble with several tasks. NOT for questions about existing work, rescheduling or closing existing issues, musing with no commitment ("I wonder if we should ever..."), summarizing pasted content, or discussions about designing this skill or the AI PM system, unless Jesse explicitly says to capture.
---

# Capture Work (v0)

Turn a quick, messy work thought into a useful Linear issue with as little friction as possible. Jesse provides the thought; you provide the structure. Optimize for successful capture over perfect metadata. This is a dogfooding version; its rules are working assumptions that will be refined from real usage.

## What is and isn't a capture

The description in the frontmatter governs triggering. A few boundaries deserve a sentence of explanation because they're where false positives come from:

- **Musing vs. commitment.** "We should probably rethink referrals someday" is thinking out loud. "Put something in for next week to rethink the referral program" is a capture. The difference is a commitment marker: a time, a directive verb, or an explicit ask. When it's ambiguous, don't create anything; you may offer once ("Want me to capture that?") and then let it go.
- **Existing work.** Moving, closing, or commenting on an issue that already exists is not capture. Do it directly with Linear tools; never create a new issue for it.
- **Meta-conversation.** Jesse will spend a lot of time talking *about* this skill, and those conversations contain example phrases verbatim. Don't capture from a design discussion unless he says to.

## Fast path

Most captures should complete with one write and one read against Linear. Use the workspace snapshot below to resolve team, project, people, and labels without lookups. Reach for a Linear search only in the specific cases called out later (recruiting ambiguity, duplicate suspicion, an unrecognized name that sounds like a teammate).

1. Identify the actual work. Is it one task or several independent ones?
2. Resolve fields from the snapshot: project → team → assignee → date → priority → labels.
3. Write a title and description.
4. Create the issue with `Linear:save_issue`.
5. Read the returned record. Build the receipt from what came back, not from what you sent.
6. Return a short receipt.

If `save_issue` errors on a metadata field (project, label, state), retry once with only team, title, assignee, description, and dueDate. A capture that lands with thin metadata beats one that fails.

## Workspace snapshot

Snapshot taken 2026-09-05. Names below are safe to pass directly to `save_issue`. If something Jesse says doesn't match anything here, that's a cue to look it up or leave the field blank, not to invent an entity.

### Teams

- **Marketing** (MAR): default for Jesse's work
- **AI Council** (AIC): AI workflow documentation and AI standard work
- **Recruiting BU** (RBU): recruiting business-unit buildout (positioning, playbooks, KPIs, ops)

Team follows project. Resolve the project first; if it lives on another team, use that team. With no project, default to Marketing.

### People

- **Jesse Kinzer** (jk): default assignee for everything
- **Cole Simmons**: design, social, content calendars, Founder Pack, SLT social
- **Oscar Gonzalez**: case studies, events
- **Nikia Wade**: leads the Referral Program (Q3)
- **Kenny Johnson**: guest user

"Kent" is not a Linear user. When a name doesn't resolve, keep it in the title or description as spoken and assign Jesse. Only run `Linear:list_users` when the name sounds like a teammate you don't recognize and assignment actually matters.

### Active projects and mapping hints

Marketing team:

- **AI Project Manager**: this system; capture skill, PM skills, dogfooding notes
- **Lead Capture & Sales Handoff**: lead flow, lead record, RB2B, website forms, booked meetings, sales handoff rules, sales feedback loop (target 2026-09-30)
- **LinkedIn → Leads**: Apify LinkedIn engagement pipeline, warm prospects to sales, LinkedIn lead automation
- **SEO**: organic search, AI visibility, service pages, GSC, article fixes
- **Recruiting GTM Strategy**: recruiting *marketing*: competitive research, pitch, campaigns (see ambiguity note below)
- **Referral Program (Q3)**: anything referral program
- **Executive Dinner Marketing Support**: dinner program landing pages, creative, post-event attribution
- **Q3 - Gloo Hackathon**
- **Q3 (overflow) - Vertical Buildout**: vertical / ICP buildout
- **Sales-Driven Content Pipeline**: content requested by or for sales
- **Paid Media | Build & Learn**: paid ads
- **Q3 - Enable the network**, **Q3 - Define the Social Funnel**, **SLT Social Strategy**, **Founder Pack - The Blueprint**, **FP - Podcast Guest 5**: Cole-led social and content work
- **New ClosedWon Client Annimations**: client announcement animations (auto-fed from Slack)
- **Case Study: Gloo — Project Manager / Scope Alignment**, **Case Study: Gloo — Delivery Consultant / Operating Model**, **Case Study: Gloo — Scrum Master / Delivery Metrics & Progress Visibility**, **Case Study - Jessup University**, **Case Study - ABS**: pick by client and offering; if no client is named, leave project blank
- **Victory Beyond the Cup**: planned, purpose unclear; only use if named

AI Council team:

- **AI Workflow Library**: documenting an AI workflow, "add a workflow ticket", AI standard material

Recruiting BU team (these show Backlog status but are actively worked):

- **P1 Positioning & Service Catalog**: recruiting positioning, service messaging (contract-to-hire, managed sourcing, retained search), recruiting landing page copy
- **P4 Sales Enablement & Growth**: recruiting pitch deck, competitive analysis
- **P2 Delivery Playbook**, **P3 Customer Success Playbook**, **P5 KPIs, Scorecard & Continuous Improvement**, **P6 Operations, Technology & Scaling**: only when clearly named or obviously matching

Don't route new work to Backlog-only Marketing projects (SLT Content Calendar, Founder Pack Content Calendar, MW Content Calendar, Q1/Q2 Website Improvements, Offerings Process Decks, Experience Sprint Board) or to completed ones unless Jesse names them.

**Recruiting ambiguity.** "Contract-to-hire" and other service messaging recently landed in RBU / P1, while competitive research and pitch work sits in Marketing / Recruiting GTM Strategy. For recruiting captures, one `Linear:list_issues` query on the topic is worth the round trip: pick whichever project has the most recent related activity, and name the choice in the receipt so a correction is one tap.

### Labels

Marketing topical labels you may apply: Strategy, Copy, Website, Design, Design-Support, AI, automation, Social, Paid Ad, Deck, PM Help, Needs-Refinement, Gloo, MW Corporate, Brazil 2026, SLT, tweak, Problem, Bug, Feature, Improvement.

Never apply scheduling or calendar labels during capture: Today, This month, Next Month, June, July, August, September, 09W1 through 09W5, Migrated. They belong to the content calendar or are legacy.

AI Council uses grouped labels (Dept, Frequency, Reuse, Saves, Setup, Rank) that classify workflows. Don't guess these; leave them for refinement.

Recruiting BU has its own small set (Positioning, Phase 1, Marketing). Apply only when obvious.

### Statuses

Marketing: Triage, Backlog, Todo, In Progress, Blocked, In Review, Done, Duplicate, Canceled.

v0 convention: an issue with a work date goes to **Todo**; an issue without one goes to **Backlog**. If a team lacks the state, omit `state` and accept the default.

## Field rules

### Title

Rewrite spoken language into a clear action that begins with a verb and makes the outcome obvious at a glance.

Good: *Review contract-to-hire landing page*, *Draft referral program positioning*, *Evaluate Vector vs. RB2B*, *Send Kent the lead list*.

Avoid: *Look at this*, *Landing page thing*, *Follow up*, *Reminder*, *Work on LinkedIn*.

### Assignee

Default to Jesse. Assign someone else only when Jesse uses a directive that puts the work on them: "have Cole...", "Cole should...", "assign this to Cole", "Cole needs to...". Mentions are not assignments: "ask Cole about...", "talk to Cole", "send Cole the..." are Jesse's tasks that involve Cole.

Assigning another person puts work in their queue from a voice note, so when you do it, say so plainly in the receipt. Don't @mention anyone in descriptions (mentions notify); use plain names.

### Project

Evidence order: Jesse names it → his wording strongly maps to a snapshot hint → a single Linear search clearly matches → otherwise leave blank. Never pick a project to make the metadata look complete. A blank project is correct more often than a wrong one.

### Dates

**v0 convention: Linear Due Date is the day Jesse intends to work on the issue, not an external deadline.** When a real deadline exists and differs from the work date, record it in the description on its own line, exactly in this form so it stays findable:

`**Hard deadline:** 2026-09-11 (Fri) — review meeting at 2 PM`

Resolve relative dates from today's date in Jesse's timezone (Central). Resolve literally; don't shift weekend dates.

| Jesse says | Work date | Also record |
|---|---|---|
| today | today | |
| tomorrow | today + 1 | |
| Monday (any weekday) | next occurrence strictly after today | |
| next Monday | that weekday of next calendar week (Mon–Sun) | |
| this week | Friday of this week; if today is Fri or later, treat as "next week" | |
| early next week | Monday of next week | |
| mid next week | Wednesday of next week | |
| end of / later next week | Friday of next week | |
| next week / sometime next week | Monday of next week (surfaces at weekly planning; Plan My Day can redistribute) | |
| before Friday / by Friday | last business day before that day | Hard deadline: that day |
| before my meeting Thursday | business day before | Hard deadline: meeting day, time if given |
| end of month / by end of month | last business day of the month | Hard deadline: last day of month |
| later this month, next month, eventually, someday, Q4 | no due date | Put the phrase in the description under Timing |
| a specific date | that date | |

Time of day ("first thing", "after lunch", "by 2 PM") can't live in the date field. Keep it in the description.

### Priority

**Default: leave priority unset.** Linear's "No priority" is a useful triage signal, and this workspace already has nearly everything marked High or Urgent, which makes priority meaningless. Set a priority only when the evidence is in what Jesse said:

- **Urgent (1):** explicit urgent/P0 language, a same-day blocker, "drop everything"
- **High (2):** "important", "critical", a meeting or dependency within a few days, work tied to a named current priority
- **Medium (3):** Jesse asks for it or says "normal priority"
- **Low (4):** "nice to have", "someday", "low priority", exploratory

Never infer High from the topic alone.

### Labels

Apply zero to two existing topical labels, and only when they'd help find or plan the work. Don't add a label because its word appeared in the sentence. When in doubt, none.

### Description

Preserve why Future Jesse cares. For a small obvious task, one or two sentences. For meaningful work:

- **Context:** why this exists
- **Outcome:** what should result
- **Constraints:** deadline, meeting, person, decision, dependency, link, or condition mentioned
- **Timing:** only when the date field couldn't hold it
- **Hard deadline:** the structured line above, when applicable

If your interpretation involved real judgment (heavy rewrite, ambiguous project), add one line `Captured from: "<cleaned original phrasing>"` so the original intent survives. Skip it for trivial tasks.

Don't write a mini-PRD. Don't invent context Jesse didn't supply.

## Judgment calls

### One issue or several

Several independent actions → several issues. "Monday I need to review the analytics dashboard, send Kent the lead list, and start the referral page copy" is three.

One outcome with several steps → one issue, unless the steps clearly need separate owners, dates, or tracking. Don't fragment.

### Capturing from earlier in the conversation

"Capture that" or "ticket that" refers to something upthread. Find the most recent concrete action Jesse committed to or asked for. If more than one candidate exists, take the most recent and name it in the receipt so he can redirect.

### Voice transcripts

Expect missing punctuation, filler words, run-ons, and misheard proper nouns ("RB to B", "coal" for Cole, "vector" for Vector). Match against the snapshot phonetically and generously for projects and teammates. Don't "correct" an unknown name to a Linear user unless the phonetic match is obvious; otherwise keep the spelling as transcribed. If the intent verb arrives at the end of a long ramble, it still counts.

### Clarify vs. capture with Needs-Refinement

Clarifying on mobile is expensive; Jesse may be walking into a meeting. Use this boundary:

- **Recognizable subject, fuzzy action** ("we need to rethink how referrals work, put something in for next week") → capture it, apply `Needs-Refinement`, and put your one question in the receipt where it doesn't block.
- **No recognizable subject** ("have Cole take care of that thing") → don't create anything; ask one concise question.

Never ask about optional metadata. Omit it instead.

### Duplicates

Search only when both are true: the capture points at a specific existing project or entity, *and* the phrasing suggests continuation ("still need to", "that thing", "again", "follow up on", "the X issue"). Then run one `Linear:list_issues` query with two or three keywords, assignee `me`, excluding Done. If a result is clearly the same work, don't create a new issue; report the existing one and offer to update its date or add a note. If the match is weak, create the issue. Never run more than one duplicate query.

## Write and verify

Call `Linear:save_issue` with `team`, `title`, `assignee`, `description`, and whichever of `project`, `dueDate`, `priority`, `state`, `addLabels` you have evidence for. Then use the returned record (identifier, URL, applied fields) for the receipt. If a field didn't apply, say so rather than implying it did.

## Receipt

Keep it short. Include the identifier, the title, and the fields most likely to need a one-tap correction.

**Created:** MAR-1190 · Review contract-to-hire landing page
Recruiting BU / P1 Positioning · Mon Sep 7 · no priority

If you assigned someone else, made an ambiguous project choice, or resolved a vague date, add one line naming the assumption. If you applied Needs-Refinement, add your one question. For multiple issues, one line each.

Don't repeat the description unless asked.

## Corrections are product feedback

When Jesse corrects a title, project, date, priority, label, or assignee, fix the issue first. Then add a one-line comment on **MAR-1181** (Build and dogfood Capture Work Skill v0.1) using `Linear:save_comment`:

`Correction · <field> · captured "<what you did>" → Jesse wanted "<what he changed it to>" · <his phrasing if useful>`

This keeps the evidence in Linear across conversations. Don't generalize a single correction into a new rule on the spot; the pattern gets proposed as a skill update once it repeats.

## Guardrails

- Retrieve before guessing, but only where this skill says a lookup is worth it. Speed is part of correctness here.
- Never create a team, project, label, or user during capture.
- Never invent dates, people, meetings, dependencies, or business context.
- Never modify unrelated existing issues.
- Keep capture additive and reversible.
- Preserve uncertainty instead of manufacturing precision.
- Rely on the returned Linear record, never on intended input, before claiming success.

## Open decisions carried into v0

These are conventions, not settled design. Apply them consistently so the dogfooding evidence is clean.

- Due Date means planned work date; hard deadlines live in a structured description line. Plan My Day and Triage will need a queryable deadline eventually.
- Dated issues go to Todo, undated to Backlog. Linear's Triage state is an alternative inbox that hasn't been evaluated.
- "Sometime next week" resolves to Monday. If Monday pileups appear, revisit.
- Priority is unset by default. If Jesse finds himself adding priority to most captures by hand, revisit.
