---
name: pm
description: Use when JK logs a moment for the PM Coverage Experiment — a friction point where a dedicated PM would have helped, or a moment the team ran clean without a PM. Trigger on "/pm ...", "log a pm gap", "pm gap moment", "no-PM friction", "pm win". Appends a dated row to the PM Gap Log in the Obsidian vault. Do NOT use for general project-management tasks, ticket creation, or the continuity-system build.
metadata:
  author: JK
  version: 1.0.0
---

# PM Gap Logger (`/pm`)

Captures a single moment for the July **PM Coverage Experiment** and appends it to the log. The experiment runs the Experience team without a dedicated PM and documents **both sides** — where a PM would have helped, and where the team self-sustained — to build a dollar-amount case for dedicated PM time.

**Core principle: keep the evidence two-sided.** Friction entries are worthless without self-sustained entries to weigh against them. Never editorialize toward "we need a PM." Record what happened.

**The one file this skill writes (absolute path):**
`/Users/jk/Documents/Vaults/Main/1_Projects/PM Coverage Experiment/01 - PM Gap Log.md`

(Vault-relative: `1_Projects/PM Coverage Experiment/01 - PM Gap Log.md`. The file is written directly; Obsidian re-indexes filesystem writes automatically.)

---

## Step 1 — Read the input

Everything after `/pm` is the moment to log, in JK's words. Examples:
- `/pm couldn't ship the LP, nobody owned the creative brief, ~30 min chasing it`
- `/pm self-sustained: Cole ran the content calendar all week, no PM input, zero slippage`

If `/pm` is invoked with no text, ask: "What happened? (the moment you want logged)" and wait.

---

## Step 2 — Classify the entry

Set **Type** to one of:
- **`friction`** — a PM would have helped: something couldn't get done, got dropped, needed chasing, lost context, or cost prep/redirect time.
- **`self-sustained`** — the team handled it without a PM: ran clean, someone stepped up, no slippage.

Decide from the text. Signals like "couldn't," "had to chase," "no one owned," "lost time," "context gap" → friction. Signals like "ran clean," "handled it," "no PM needed," "self-sustained," "no slippage" → self-sustained. If genuinely ambiguous, ask one short question, then proceed.

---

## Step 3 — Estimate time lost (friction only)

- If JK stated a duration ("~30 min", "an hour"), use it.
- If not but it's reasonably inferable, estimate and mark it (e.g. `~20 min (est)`).
- If not inferable, leave `—` and don't invent one.
- For `self-sustained` rows, time lost is `—` (optionally note time *saved* in Notes).

**$ est:** only fill if the log has a PM loaded rate set (read the file; look for `PM loaded rate: $N/hr`). If a rate is present, compute `time × rate` and round. If the rate is still a blank placeholder, leave `—`.

---

## Step 4 — Write a tight summary

Compress the input into one clear factual clause for the **What happened** column — JK's voice, no fluff, no spin. Put any extra context (who, which ticket, which client) in **Notes**. Keep cell contents free of unescaped `|` pipes (replace with `/` or "and").

---

## Step 5 — Append the row (read-then-edit)

Get today's date: `date +%Y-%m-%d` (Bash).

Build the row:
`| <date> | <type> | <what happened> | <time lost or —> | <$ est or —> | <notes or —> |`

**Append with read-then-edit — do NOT use blind append** (it breaks markdown tables):

1. `Read` the log file at the absolute path above.
2. Find the **last table line** (the most recent data row, or the `|---|...|` separator if only the header exists).
3. `Edit` the file: replace that exact last line with itself + newline + the new row.
   - old: `<last table line>`
   - new: `<last table line>\n<new row>`

This keeps every row on its own line regardless of trailing-newline state.

---

## Step 6 — Confirm

One line back to JK, e.g.:
> Logged (**friction**, ~30 min): couldn't ship the LP, no creative-brief owner. — PM Gap Log

If it's easy, add a running tally: "That's N friction / M self-sustained entries so far." (Count the rows by Type from the file you just read.)

---

## Notes

- This skill only ever appends to the log. It never rewrites prior rows or edits the readme.
- If the log file is missing, tell JK it isn't at the expected path (the [[PM Coverage Experiment]] project may have moved) rather than recreating it.
- Don't pull in the continuity-system work — that's a separate project ([[Continuity System]]).
