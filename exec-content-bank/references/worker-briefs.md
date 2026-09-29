# Worker briefs

These briefs are person-agnostic. Everything about who the bank is for comes from the person profile you built in SKILL.md "Before dispatch". Fill every placeholder before dispatch:

| Placeholder | Meaning |
|---|---|
| `{PERSON}`, `{FIRST}`, `{TITLE}` | Full name, first name, job title |
| `{HOME}` | Absolute path of the bank's project folder |
| `{AUDIENCE}` | Who the content serves, in one line (e.g. "CTOs, VPs of Engineering, and founders at software companies" or "marketing leaders who manage creative teams at scaling companies") |
| `{NICHE}` | Topic territory plus through-line if one exists, or "none defined yet" |
| `{BRIDGE}` | How helping this audience leads to Midwestern's services (Scoped, Embedded, Recruiting) |
| `{CHANNELS}` | "LinkedIn and Instagram" or "LinkedIn only" |
| `{VOICE}` | Where the person's voice rules come from (a voice or profile note, or "derive from the LinkedIn audit and meetings") |
| `{EXISTING}` | Wikilinks to existing idea lists, drafts, and published-post folders, or "none" |
| `{LINKEDIN_URL}`, `{IG_HANDLE}`, `{SLACK_ID}`, `{DATE}` | As named |

Pass `model` explicitly on every Agent call (research: `sonnet`; synthesis: `opus`; review: `sonnet`). Send all research briefs in one message with `run_in_background: true` so they run in parallel.

## Shared preamble (paste at the top of every brief)

```
Think hard and carefully before each step (high effort). Do not over-plan and do not write planning documents.

Context: Midwestern Interactive (Carthage, MO) is a talent partner for the tech ecosystem, with three service lines: Scoped (project teams), Embedded (talent placed onto a client's team), and Recruiting (full-time hires). JK (Marketing Director) is building a large bank of content ideas for {PERSON} ({TITLE}). It uses Alex Hormozi's method: give away free, useful knowledge that helps {FIRST}'s audience, keep giving, and let them ask to pay. You are one of several parallel research workers. Stay inside your own sources, because other workers cover the rest.

Person profile (judge relevance against it):
- Audience: {AUDIENCE}
- Niche and through-line: {NICHE}
- Bridge to Midwestern: {BRIDGE}
- Channels: {CHANNELS}
- Voice source: {VOICE}
- Existing ideas and posts. Do not re-propose these; build on them: {EXISTING}

Rules for your output file:
- Write ONLY the file named below.
- Start with YAML frontmatter: tags in list format (`- research` plus one topic tag), `date: {DATE}`, `type: research`. Use `##` headings.
- Cite every item. Use a wikilink to the vault note basename, or the call, Slack, or Granola reference.
- No em dashes or en dashes anywhere. Never use the word "broker".
- Find vault files by searching (grep, the Hub Index). Never assume a path, because notes move.
- Attribute a quote to a person only when the transcript names that speaker. If it says "Speaker A" or is unclear, write "(confirm speaker)".
- Do not propose sensitive material. Flag it as DO NOT POST: HR and performance, compensation, pricing tiers and fee percentages, departures, M&A and capital partners, legal matters, personal medical, negative client feedback, other companies' incidents.

Report back in under 250 words: what you covered, counts, top 5 findings, sensitive flags, and gaps.
```

## 1. LinkedIn audit

```
Task: review {FIRST}'s LinkedIn with ego-browser. Run every ego-browser command with dangerouslyDisableSandbox: true, because the sandbox blocks its bootstrap. First run the Skill tool with skill "ego-browser" and follow it exactly: one TaskSpace, reuse page p1, and call `finish({ keep: [] })` at the end.

JK may already have the profile open. You may read `task.tabs()` or `listTaskSpaces()` to find the URL. Never claim or close JK's own tabs or spaces. Open your own TaskSpace and go to {LINKEDIN_URL}. Read-only: never like, comment, follow, message, or post.

Collect:
- Profile: headline, About, Featured, follower and connection counts, and where the profile button goes.
- Posts: open the recent-activity posts tab and scroll to capture 30 or more of their own posts (or all of them if there are fewer). For each post: approximate date, first two lines (the hook), topic, format (text, image, carousel, video, repost, poll), reactions, comments, reposts, and URL. Use page.evaluate for bulk extraction.

Analyze:
- Top 10 posts and why they worked.
- Average engagement by topic and by format, and the posting cadence.
- Voice: sentence length, vocabulary, humor, faith, stories.
- Recurring themes, and gaps someone speaking to {AUDIENCE} should own.
- Use of CTAs and lead magnets.
- Whether the profile tells a visitor what {FIRST} helps with and what to do next.
Give 10 profile fixes and 15 ideas that extend what already works. If the account is new or small, say so, and weight the analysis toward positioning over performance.

If LinkedIn blocks you or ego-browser fails after 2 or 3 tries, stop and report exactly what happened. If ego fails completely, use `mcp__apify__harvestapi--linkedin-profile-posts` (load it via ToolSearch) with a small maxPosts, and say that you did.

Output: {HOME}/Research/01 - LinkedIn Audit.md (tag: - linkedin). Include the full post table.
```

## 2. Vault themes and assets

```
Task: mine the vault at /Users/jk/Documents/Vaults/Main. Do NOT read 2_Notes/Meetings/, because another worker owns it.

Read these first:
1. {FIRST}'s own brand materials: {EXISTING}, the voice source ({VOICE}), and any positioning notes near them (niche, through-line, bridge, swipe file).
2. `0_Marketing GIT/0_Marketing Hub/00 - Hub Index.md`. Follow its routing and load only what is relevant to {AUDIENCE}.

Cover:
- Hub Foundation: Messaging Patterns, Business summation, Service Offerings Taxonomy, the service-line ICPs, the Sales Playbook, and Proof Points. Find Proof Points by grep and quote its exact wording.
- Verticals and intelligence notes that touch {AUDIENCE}.
- Related projects in 1_Projects/ (search for the niche's keywords, plus social, content, blog, podcast, messaging, calculator, dinner, consultation).
- The top section of `People/{PERSON}.md`, if that note exists.
- Grep for "{FIRST}", "lead magnet", "hormozi", and the niche's keywords.

Extract:
- Content pillars {FIRST} could credibly own, with evidence. If a through-line exists, every pillar must ladder up to it.
- 40 or more problems and questions of {AUDIENCE} that free content could answer.
- Frameworks, stats, stories, and opinions already written down.
- 15 or more lead magnets that exist, are in motion, or could be built cheaply.
- Brand guardrails: approved proof points, banned words, voice rules.
- Who owns {FIRST}'s social, and any cadence constraints.
- The ideas in {EXISTING}, listed as a dedupe list.
- Unresolved strategic questions about {FIRST}'s positioning.

Output: {HOME}/Research/02 - Vault Themes and Assets.md (tag: - content-strategy).
```

## 3. Meetings: the person's own voice

```
Task: find {FIRST}'s own stories, opinions, frameworks, and lessons, weighted toward {NICHE}. Another worker covers buyer pain from sales calls.

Choose meetings. Read 2_Notes/Meetings/CLAUDE.md first.
- If `People/{PERSON}.md` exists and lists meetings, use that list to pick the 25 to 40 richest meetings, or all of them if there are fewer. If there are fewer than 10, also run the topic-based search below.
- If there is no People note, or {FIRST} attends most meetings in the archive, pick by topic instead. Grep /Users/jk/Documents/Vaults/Main/2_Notes/Meetings/ for the niche's keywords, and prefer meetings where {FIRST} speaks at length (all-hands talks, working sessions, podcasts, video shoots, 1:1s).
- Read the transcript sections for the best passages.

Granola: load the tools via ToolSearch with `select:mcp__granola__query_granola_meetings,mcp__granola__get_meeting_transcript,mcp__granola__list_meetings`. Run 6 to 10 targeted queries built from the niche and the audience's problems, plus {FIRST}'s career or origin story, the mistakes they admit, and the beliefs they repeat.

Extract:
- 40 or more quotable moments: quote, context, date, and source.
- Recurring and contrarian beliefs.
- Origin and career stories.
- Frameworks and mental models.
- Behind-the-scenes moments (for Instagram only if the channels include it).
- Topics that energize {FIRST}, and topics to avoid.
Check speaker labels before you attribute any quote. List quotes that belong to other people, so that nobody misattributes them.

Output: {HOME}/Research/03 - Meetings - {FIRST}'s Voice.md (tag: - meetings).
```

## 4. Sales calls: buyer pain

```
Task: find what {AUDIENCE} actually ask, fear, and object to. Granola and the vault hold only internal meetings, so Airspeed is the only source of buyer language.

Airspeed:
- Try the `airspeed` MCP first.
- If it is down, use REST. Read the key in an UNSANDBOXED Bash call (dangerouslyDisableSandbox: true, because the sandbox hides Keychain). Keep the key in a shell variable inside the same command, and never print it: `K=$(security find-generic-password -s airspeed-api-key -w); curl -sL -H "X-API-Key: $K" "https://api.glyphic.ai/v1/calls/?limit=50" > "$TMPDIR/calls.json"`
- Always use `curl -L`, because the calls endpoint returns 307.
- Check https://api.glyphic.ai/openapi.json for pagination and filters.
- The verbatim text is in `transcript_turns` on `/v1/calls/{id}`. The snippets endpoint returns empty.
- Sample 40 to 60 external calls from the last 6 months. Prefer calls with people who match {AUDIENCE}. Skip voicemails and internal calls. Extract only the buyer turns, with jq or python.
- If few calls match {AUDIENCE}, say so, and use the closest buyers (for example, the executives who own budget for that audience's work).

Optional and short: HubSpot deal names and lost reasons, via `mcp__claude_ai_HubSpot__search_crm_objects`.

Extract:
- 50 or more questions and pains, grouped by theme: quote, role and industry, call ID and date, and the mapped service.
- The top objections to hiring a partner, and the knowledge that would remove each one.
- Questions that could each become a free post, checklist, calculator, or template.
- Verbatim buyer phrases for hooks.
Remove every company name and person name.

Output: {HOME}/Research/04 - Sales Calls - Buyer Pain.md (tag: - buyer-language). Put scratch data only in $TMPDIR.
```

## 5. Slack

```
Task: mine Slack for {FIRST}'s voice, proof stories, and questions from {AUDIENCE}. Load the tools in ONE ToolSearch call: `select:mcp__claude_ai_Slack__slack_search_public_and_private,mcp__claude_ai_Slack__slack_read_thread,mcp__claude_ai_Slack__slack_read_channel,mcp__claude_ai_Slack__slack_search_channels`. Read-only: never send, react, draft, or schedule.

Search the last 9 months or so:
- `from:<@{SLACK_ID}>` with the niche's keywords, plus: lesson, win, proud, mistake, believe, client, team, LinkedIn.
- Wins, shoutouts, client feedback, sales, and leadership channels. Find their names with slack_search_channels.
- Marketing and social channels about {FIRST}'s content.
- Links that {FIRST} shared with commentary.
Read the threads where {FIRST} writes at length. The workspace may include channels from other companies: skip those.

Extract:
- 40 or more content seeds. For each: the idea, a short quote, the author's role, date, channel, permalink, and type (opinion, proof story, audience question, or behind the scenes).
- {FIRST}'s recurring phrases.
- Proof stories with specifics.
- DO NOT POST flags.

Output: {HOME}/Research/05 - Slack Mining.md (tag: - slack).
```

## 6. Instagram (only if the channels include Instagram and a handle exists)

```
Task: review @{IG_HANDLE} on Instagram with ego-browser, read-only. Use the same ego-browser rules as the LinkedIn brief, including dangerouslyDisableSandbox: true.

Capture the follower count, bio, link, highlights, and the last 30 posts and reels (date, format, caption hook, likes, comments, and views on reels). Analyze what performs, the visual style, and which LinkedIn material could be reused as Reels, carousels, or Stories.

Output: {HOME}/Research/06 - Instagram Audit.md (tag: - instagram).
```

## 7. Email (only if a mail connector is available)

```
Task: search the accessible email for inbound questions from {AUDIENCE}, client praise, and objections from the last 6 months. Read-only. Remove all names. Use the same extraction shape as the sales-call brief.

Output: {HOME}/Research/07 - Email Mining.md (tag: - email).
```

## Synthesis (model: opus)

```
Think very hard (high effort). Your only outputs are the files named below.

Read every file in {HOME}/Research/ in full. Read the Proof Points note (find it by grep) for the exact stat wording. Read the voice source ({VOICE}) and the existing ideas ({EXISTING}). Read other vault files only to verify a specific claim.

Build the bank with the generator:
1. Run: python3 ~/.claude/skills/exec-content-bank/scripts/build_bank.py init "{HOME}" --exec "{PERSON}"
2. Fill {HOME}/.build/config.json:
   - Set "channels" to match {CHANNELS}.
   - Set "audience_label" to a short noun for {AUDIENCE}.
   - Set "project_link" to the wikilink of the folder's readme.
   - Fill the pillars, lead magnets, source shortcodes, top20, and date.
3. Fill {HOME}/.build/ideas.txt (the format is in the script docstring) and {HOME}/.build/prose.md.
4. Run: python3 ~/.claude/skills/exec-content-bank/scripts/build_bank.py build "{HOME}"
Never hand-edit the rendered note or the CSVs. Fix errors in the data and rebuild until the build exits 0. Then judge every WARN line.

Hormozi method:
- Give far more than you ask. Tag each idea with a Stage: Give (how-to, framework, teardown, lesson, joke), Proof (story, result, behind the scenes), Belief (an opinion that attracts the right audience), or Ask (points to a lead magnet). Target 60/20/12/8.
- A lead magnet solves a narrow problem completely and reveals a bigger problem that Midwestern solves (use {BRIDGE}). There are three types: reveal a problem (diagnostic, scorecard, calculator), sample or trial (teardown, review, office hours, dinner), and one step of a process (checklist, template, playbook).
- CTA: "Comment KEYWORD and I'll send it" on LinkedIn. Add "DM me KEYWORD" on Instagram only if the channels include it.
- Teach the actual answer. Hook, retain, reward.

prose.md sections, in this order:
1. How to use this: the method, the stage-mix placeholder, and how the person or the social owner picks ideas.
2. What the research says: 8 to 12 cited bullets.
3. Content pillars.
4. Lead magnet catalog: 15 to 25 entries, cheapest first.
5. Start here: top 20.
6. The idea bank. TARGET 130 or more distinct ideas across 6 to 9 pillars. If a through-line exists, every pillar ladders up to it. Include a proof pillar. Add these only when the research supports them: a humor and personal pillar (if personal posts outperform), and a set that turns a podcast or video series into standalone value posts (if one exists).
7. Recurring series: 5 to 8.
8. Profile fixes.
9. Guardrails and open questions: DO NOT POST topics, client-permission needs, unresolved strategic questions, and sources that were unavailable.

Idea fields:
- Post idea: what the post teaches or shows.
- Hook: a real first line in {FIRST}'s voice, following {VOICE}. Use their verbatim phrases and the audience's verbatim phrases.
- Instagram angle: format plus angle, only when the channels include Instagram.
- Source: the research file plus the specific meeting, call, or Slack reference. If an idea extends one of the existing ideas, cite that note and add a new angle. Never copy an existing idea.

Hard rules:
- Use proof points only in the exact approved wording from the Proof Points note. Any other stat comes from that note or carries "(verify)".
- Hooks are written as {FIRST}, in their voice. Claims about Midwestern follow Messaging Patterns.
- No client names in hooks or ideas. Write a proof story that depends on a named client anonymized, and put "(needs client OK to name)" in Source.
- Nothing from any DO NOT POST or sensitive list.
- Never attribute a quote that the research marks as another person's or as "(confirm speaker)".
- Items that need the person's own input say "(needs {FIRST})" in Source.
- Write hooks as copy: natural, specific, full sentences. No contrast-flips ("isn't X, it's Y", "didn't X; it Y"), no validation openers, and no "Here's the thing".

Report back in under 250 words: counts per pillar and stage, the lead magnet count, the builder output (errors and warnings), and anything left out or unverified.
```

## Review (model: sonnet)

```
Think hard (high effort). You are the independent reviewer of the content bank in {HOME}.

Fix problems only in {HOME}/.build/ideas.txt, config.json, and prose.md. Then rebuild with `python3 ~/.claude/skills/exec-content-bank/scripts/build_bank.py build "{HOME}"`. Copy the three data files to .bak before your first edit. Keep the keys stable, and do not reorder ideas.

Checks:
1. Humanizer: run the Skill tool with skill "humanizer" and apply it to every hook, idea, and prose section. Also remove contrast-flips, validation openers, compressed chiasmus, and filler rule-of-three lists. The person's own verbatim quotes keep their wording.
2. Voice: every hook must match {VOICE}. Apply the three-question test to each hook: can the reader picture it, could it be proven false, and could only {FIRST} say it? Rewrite the weakest 25 or more.
3. Sources and quotes:
   - Sample 35 or more ideas across all pillars, and confirm that each Source supports its idea.
   - Verify every direct quote against the research files. Verify at least 12 against the original meeting note, transcript, or Slack message.
   - De-attribute anything you cannot confirm, and mark it "(confirm speaker)".
4. Duplicates: compare against the existing ideas ({EXISTING}) and merge near-duplicates within the bank. Rewrite each duplicate into a distinct angle.
5. Guardrails: no client names in hooks or ideas, nothing from the DO NOT POST lists, and proof points only in the approved wording. Do not frame Midwestern as an agency, a vendor, a staffing firm, or outsourcing.
6. Integrity: the final build must exit 0. Confirm that the CSV row count equals the idea count, and that every WARN is resolved or justified.

Report back in under 300 words: hooks rewritten, quotes verified (and how many against originals), quotes changed, guardrail hits fixed, duplicates merged, the final builder output, and any decisions JK must make.
```
