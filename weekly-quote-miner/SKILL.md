---
name: weekly-quote-miner
description: Scheduled weekly job that mines the past week's Airspeed call transcripts for quotable client praise about Midwestern Interactive and posts a graded digest to #client-quotes. Use when the scheduled Friday run fires or JK says "run the quote miner".
---

# Weekly Quote Miner

Mines Airspeed call transcripts for verbatim client praise about Midwestern Interactive (buildmidwestern.com) and posts a digest to the private Slack channel **#client-quotes (channel_id: C0BHGFLHYMB)**.

Origin: MAR-172. This replaced a retired custom Slack bot; see `/Users/jk/Documents/GitHub/client_quote_slack_bot/REPLACEMENT-GUIDE.md`.

## Procedure

### 1. Collect calls
- Load tools via ToolSearch: `mcp__airspeed__list_calls`, `mcp__airspeed__get_call_info`.
- Date range: the 7 days ending today (run `date` to compute; use UTC ISO 8601 for `start_time_from`).
- Call `list_calls` with `limit: 100` and `start_time_from`. **Paginate with the cursor until exhausted** — a week can exceed 100 calls.
- Keep calls where: `status.code == "completed"` AND `duration >= 300` seconds.
- **Skip** calls tagged `Cold Call` or `Initial Call - SDR` (they never contain testimonials — verified in pilot run 1, 2026-07-15).

### 2. Extract quotes
Process calls in batches of ~3 via parallel general-purpose subagents (Agent tool) so transcripts stay out of the main context. Each subagent: load `mcp__airspeed__get_call_info` via ToolSearch, fetch each call, read `transcript_turns`, and apply these rules:

- Internal = any participant with a buildmidwestern.com email. Extract ONLY from external participants. Match `party_id` in transcript turns to the participants list `id`.
- **Skip recruiting screens entirely**: calls where the external person is a job candidate being interviewed (Midwestern staffs placements for clients like Glue). Flag as skipped.
- Extract statements where an external person praises Midwestern: team, people, work quality, process, speed, results, or the experience of working with them.
- EXCLUDE: generic politeness ("sounds good", "thanks"), buying interest ("I'd love to work together"), praise of non-Midwestern things, and anything said by internal staff.
- Quote must be VERBATIM from the transcript. Mark suspected transcription garbles with [sic?]. Watch for diarization swaps (speaker attribution errors are common on short calls; sanity-check that the speaker is really external).
- Grade: **A** = usable in marketing as-is, **B** = usable with light trim, **C** = weak/borderline.
- Carry a context flag when the surrounding call complicates use (e.g., praise inside a pricing renegotiation or complaint call).
- Return the **sales owner** with every candidate: the internal (buildmidwestern.com) participant on the call (primary one if several). Their approval gates any use of the quote.

### 3. Post the digest
Load `mcp__plugin_slack_slack__slack_send_message` via ToolSearch. Post ONE message to channel_id `C0BHGFLHYMB` in EXACTLY this layout (JK-approved format, 2026-07-15). Slack markdown: `**bold**`, `_italic_`, `> blockquote`; NO headers (#) and NO tables — they don't render.

```
📣 **Client quotes this week** · Jul 8–14 · 5 found across 11 calls

🟢 **A tier**

> Quote text, plain (not bold), no surrounding quotation marks.

**Speaker Name**, role, Company · Call title · Jul 9 · Sales owner: **Rep Name**

🟡 **B tier**

> Quote text.

**Speaker Name**, Company · Call title · Jul 9 · Sales owner: **Rep Name** · _one-line caveat_

> Quote with a serious caveat.

**Speaker Name**, Company · Call title · Jul 9 · Sales owner: **Rep Name** · ⚠️ _flag - e.g. said during a pricing renegotiation_

⚠️ _These are unapproved candidates pulled from call transcripts - nothing here is logged or cleared for use. Sales owners: 👍 react to approve your quote, or reply in thread to kill it. Approved quotes still need client permission before public use._

_Skipped: N cold/SDR calls + N recruiting screens · Next run: Friday 9:15am_
```

Rules:
- Tiers describe QUOTE QUALITY ONLY, never approval status: 🟢 **A tier** = strong as-is, 🟡 **B tier** = needs a trim or carries a caveat. Omit an empty section. Omit C-tier unless there are no A/B at all.
- **Sales owner** = the internal (buildmidwestern.com) participant on that call - the subagents must return this with each candidate. Plain bold name, no @-mention (don't ping; reps see it when they check the channel).
- The disclaimer block is MANDATORY on every digest, verbatim as above. Sales approval happens via 👍 reaction in the channel; the miner never logs quotes anywhere.
- Quote text goes in a `>` blockquote, plain weight. Bold ONLY speaker names, rep names, and section labels.
- One blank line between every element. Caveats/flags live inline on the attribution line in italics, never as a separate "Context:" line unless genuinely needed for the decision.
- Keep the [sic?] garble marker inside the blockquote where applicable.
- Zero candidates → post one line: "📣 Client quotes this week · <range> · none found (N calls scanned, M mined)." Always post; silence looks like breakage.

### 4. Log
Append one summary line to `/Users/jk/.claude/skills/weekly-quote-miner/run.log` is handled by the runner script; just print a run summary (calls scanned/mined/skipped, candidates by grade, message link) as your final output.

## Boundaries
- Do NOT write to any Google Sheet, Linear, or the Obsidian vault.
- Do NOT post anywhere except C0BHGFLHYMB.
- Permission to use a quote publicly is asked by a human at use time — the miner only surfaces candidates.
