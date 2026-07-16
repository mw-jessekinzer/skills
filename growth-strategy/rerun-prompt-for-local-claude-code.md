# Prompt: Q3 Growth Strategy Rebuild (run in Claude Code with full local context)

Copy everything below the line into Claude Code on a machine with access to Granola, HubSpot, Slack, and internal marketing docs.

---

Act as an expert B2B growth marketing consultant. I'm the Director of Marketing at Midwestern (buildmidwestern.com), a ~120-person software development / talent partner agency in Joplin, MO. Current positioning: "Talent partner for the AI era of work" — Embedded Teams, Scoped Projects, and Recruiting/Direct Hire, US-led with global sourcing.

## The assignment

Build our complete growth marketing strategy for Q3 (August 1 – October 31, 2026). Our goals:

1. **Double marketing-sourced pipeline** created in the quarter (Q2 baseline was roughly $363K from LinkedIn + Website/Inbound — verify this yourself in HubSpot).
2. **Double closed-won pipeline** for the whole team (Q2 baseline roughly $539K — verify).
3. **Extremely qualified leads only.** We do not want MQL volume. We want hand-raisers from ICP-fit accounts. Judge every recommendation by pipeline dollars and deal quality, not lead counts.

A prior consulting pass (without access to our internal data) produced these conclusions — treat them as hypotheses to confirm, sharpen, or overturn with the data you have that it didn't:

- ~95% of our pipeline is relationship/referral/customer-upgrade sourced; marketing-sourced deals average ~$22K vs ~$127K for relationship deals, and none have closed-won this year.
- Doubling won pipeline in-quarter must come from the ~$4.85M of open pipeline, customer expansion (our #1 winning source), and referrals — not from new top-of-funnel (deals take 90–170 days).
- Recommended play stack: (1) systematize the referral program with partner fees and give-first cadences, (2) ship two qualification-by-design lead magnets — a "Build vs. Buy vs. Embed" interactive cost calculator and a "Custom Software Partner Evaluation Scorecard", (3) run the podcast as a guest-as-prospect engine (guest list = target account list), (4) ABM-style signal-based outbound on 2 focus verticals with LinkedIn Thought Leader Ads air cover, (5) founder/exec LinkedIn content, (6) mid-funnel repair (case studies, loss analysis, expansion campaign, <1-hour hand-raiser response SLA), (7) optional executive dinner pilot.

## What we're already doing (don't re-propose as new)

- A referral program has launched
- We produce a podcast
- We've verticalized and started account-based-marketing-style work on our website

## How to work — Phase 1: mine internal context FIRST (this is why we're re-running the exercise)

Before any external research, build the ground truth the prior pass couldn't:

1. **Granola meeting transcripts** — this is the highest-value source. Query sales calls and marketing meetings from the last 2 quarters and extract: (a) why we actually win and lose deals — real objections, pricing pushback, competitors named, who ghosted and when; (b) which verticals and buyer titles actually show up in deals; (c) what prospects say brought them to us (true attribution, in their words); (d) internal strategy discussions about the verticals, podcast, referral program, and pipeline goals so your strategy matches decisions already made.
2. **HubSpot** — re-pull the pipeline baseline yourself: pipeline created by month and by `deal_source` for Q1/Q2/Q3-to-date, closed-won and closed-lost by source, average deal size by source, stage-by-stage conversion, and time-in-stage. Do a loss analysis on this year's closed-lost deals (~25 deals / ~$2.2M as of mid-July). Also look at contacts/companies: what does our actual won-deal ICP look like (industry, size, title)?
3. **Marketing docs and Slack** — find the vertical list and ABM account lists, podcast performance and guest history, referral program terms, brand/positioning docs, current content calendar, and any budget constraints. Confirm which 2 verticals should lead Q3, or tell me exactly what decision is blocking that.

## Phase 2: external research with subagents

Spawn parallel Sonnet subagents (background, web-enabled) to research: (a) current best-evidence B2B demand gen strategies for high-ACV tech services firms — prioritize Gartner, 6sense, Hinge Research Institute, HockeyStack, Refine Labs/HIRO thinking; (b) proven lead magnet examples that produce qualified B2B leads for agencies/consultancies (interactive calculators, assessments, vendor scorecards, benchmark research — with real examples, conversion benchmarks, and URLs); (c) anything competitive our named competitors are doing (Toptal, Crema, Atomic Object, WillowTree/TELUS, BairesDev, Bottle Rocket). Skip this phase where the prior pass's findings (summarized above) are already sufficient — spend your effort where internal data changes the picture.

## Phase 3: synthesize the strategy

Produce a single strategy document containing:

1. **Executive summary** — the core argument in plain English
2. **Verified baseline** — the real numbers from HubSpot, plus what the meeting transcripts revealed that the CRM doesn't show
3. **Win/loss truth** — the actual reasons we win and lose, quoted or paraphrased from real calls, and what marketing should build in response
4. **Q3 targets with the math** — how the doubling goals decompose across plays, with per-play pipeline contribution estimates
5. **The play stack** — prioritized, each with owner, effort, cost, expected in-quarter contribution, and a kill/scale rule. Keep what the prior plan got right, replace what the internal data disproves, and say explicitly where you changed the prior plan and why.
6. **Lead magnet specs** — for each recommended magnet: concept, inputs/questions, gating approach, distribution plan, and what makes it self-qualifying
7. **What we will NOT do**, with one-line reasons
8. **Measurement** — hand-raiser definition, weekly dashboard metrics, self-reported attribution setup, response-time SLA
9. **90-day calendar** (August build → September distribute → October compound)
10. **Decisions needed from leadership** — only ones the data genuinely can't resolve

## Ground rules

- Real data over benchmarks; when you use an external benchmark, flag that it's directional and usually SaaS-derived.
- Quote real evidence from our own meetings/CRM for every major claim — that's the point of this re-run.
- No MQL scoring, no generic gated ebooks, no community builds, no broad cold email, max 2 verticals.
- If something important is genuinely ambiguous after checking the data (e.g., vertical selection), ask me — otherwise proceed and state your assumptions.
- Deliverable: save the strategy as a markdown doc, and give me a plain-English summary of the 5 most impactful moves at the end.
