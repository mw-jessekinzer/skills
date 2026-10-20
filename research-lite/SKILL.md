---
name: research-lite
description: Lightweight middle-ground research — runs the research-lite workflow (2 parallel search agents, 1 verifier) then synthesizes a final answer. Use when the user types /research-lite, or asks for quick multi-source research that's deeper than a plain answer but lighter than /deep-research. Pass the research question as args.
---

# research-lite

A thin entry point to the `research-lite` workflow. Use this when the user wants real, multi-source research without the full `deep-research` fan-out and adversarial pipeline.

## What it runs

The workflow (`.claude/workflows/research-lite.js`) does:
1. **Search (parallel):** two Sonnet agents — one on the landscape/breadth, one on evidence/depth. Both must cite real source URLs and must not speculate from memory.
2. **Verify:** one agent independently re-searches the load-bearing claims, marks each solid / shaky / contradicted / unverifiable, and flags contradictions + gaps.
3. **Synthesis:** the workflow returns structured data to you (the main agent) to write the final answer.

## Steps

1. **Get the question.** Use the skill args as the research question. If no question was provided, ask the user for one before running anything.

2. **Run the workflow.** Invoke the `Workflow` tool:
   ```
   Workflow({ name: "research-lite", args: "<the research question>" })
   ```
   This requires no extra opt-in — invoking this skill is the opt-in.

3. **Synthesize.** When the workflow returns `{ question, landscape, evidence, verification }`:
   - Lead with the answer to the question.
   - Build it from claims the verifier marked **solid**.
   - Explicitly flag anything **shaky / contradicted / unverifiable**, plus open gaps. Don't bury the uncertainty.
   - Keep it dense and scannable per the user's communication style (headers, bullets, bold).

4. **Offer to save.** Per the vault rules, ask whether to save the result to the Obsidian vault and where, before writing any note. Default to answering in-thread unless the user wants it saved.

## Notes

- This is the lighter sibling of `/deep-research`. If the question is broad or high-stakes enough to warrant adversarial fact-checking and a fully cited report, suggest `deep-research` instead.
- The workflow sets the agents to Sonnet but cannot pass thinking-effort through workflow agent calls. If the user needs high-thinking research subagents specifically, dispatch the agents manually instead of using the workflow.
