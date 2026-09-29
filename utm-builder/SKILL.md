---
name: utm-builder
description: Use when building a UTM-tagged tracking link for any Midwestern marketing channel — minting a tracking URL for a post, podcast, ad, exec, or campaign, or logging a new UTM. Trigger on "build a UTM link", "create a tracking link", "tag this URL", "mint a UTM", "UTM for [channel]", or "what UTM should I use". Do NOT use for editing the UTM taxonomy wholesale, reporting on or analyzing UTM/campaign performance in HubSpot, or any task that isn't producing a tracking link.
metadata:
  author: Midwestern
  version: 1.0.0
---

# UTM Builder

Builds consistent, taxonomy-compliant UTM links for Midwestern marketing channels and logs each one to the master list.

**Core principle:** the taxonomy is the source of truth. Read it on every run — never cache values, never assume the vocabulary from a previous run still holds.

**Two vault files this skill uses (vault-relative paths):**
- Taxonomy (read): `0_Marketing Hub/4_Performance/Attribution/UTM Taxonomy.md`
- Master list (append): `0_Marketing Hub/4_Performance/Attribution/UTM Master List.md`

The `obsidian` CLI is the primary tool for reading/writing the vault here. If the Obsidian MCP (`mcp__obsidian__read_note` / `write_note`) is connected, it works too (MCP paths need a `Main/` prefix). Prefer the CLI.

---

## Step 0 — Pre-flight

Confirm Obsidian is reachable: run `obsidian vault` (Bash).
- Succeeds → continue silently.
- Fails → stop and tell the user: "Obsidian isn't reachable, and I need it to read the taxonomy and log the link. Make sure Obsidian is running, then try again." Do not proceed.

---

## Step 1 — Gather inputs

Collect these. Ask for any **required** field that's missing; skip optional ones if not relevant.

| Field | Required? | Notes |
|---|---|---|
| Base destination URL | **Yes** | The page/booking the link points to. No default — ask if missing. |
| Channel / where the link will live | **Yes** | e.g. "FounderPack Spotify bio", "Jesse's LinkedIn". Maps to source + medium. |
| Campaign name | **Yes** | The initiative this link is for. |
| Content differentiator | Optional | Exec name, platform variant (spotify/youtube/clips), ad variant, article slug. |
| Paid keyword / audience | Optional | Only for LinkedIn Ads / Meta Ads → `utm_term`. |
| Purpose / notes | Optional | Free text for the log. |

If the channel is ambiguous (e.g. "the podcast" without a platform), ask before continuing.

---

## Step 2 — Read the taxonomy

Read it fresh every time:
```
obsidian read path="0_Marketing Hub/4_Performance/Attribution/UTM Taxonomy.md"
```
(MCP alternative: `mcp__obsidian__read_note` with `Main/0_Marketing Hub/4_Performance/Attribution/UTM Taxonomy.md`.)

If the file is missing, stop and tell the user it isn't at the expected path. From the doc, pull: the `utm_source` vocab table, the `utm_medium` vocab table, and the per-channel lookup table.

---

## Step 3 — Resolve source / medium / content

Map the stated channel to the vocabulary.

- **Clear match** → use those values. (Reuse the conventions: FounderPack → `source=founderpack`, `medium=podcast`, platform in `content`; exec LinkedIn → `source=linkedin`, `medium=social-organic`, `content=exec-firstname-lastname`.)
- **No match / ambiguous** → do NOT invent a value. Present the choice:

  > "'[channel]' isn't in the UTM vocabulary yet. Options:
  > **A — use the closest existing source:** `utm_source=[x]` ([why]).
  > **B — add it as a new source.** Proposed rows:
  >   - `utm_source` table: `[value]` → [maps to]
  >   - per-channel lookup: [row]
  > Which do you want? If B, I'll add those rows to the taxonomy after you confirm."

  On confirming **B**: write the new row(s) into `UTM Taxonomy.md` (read it, insert the row into the correct table, write it back — `obsidian` CLI or MCP), then continue. The taxonomy is only edited with explicit confirmation.

---

## Step 4 — Construct and self-check the URL

Assemble:
`https://DESTINATION?utm_source=S&utm_medium=M&utm_campaign=C`
Append `&utm_content=…` and/or `&utm_term=…` only if provided.

Self-check against the naming rules (this is a read-and-verify, not code):
- all values lowercase,
- hyphens only (no spaces/underscores/special chars),
- `utm_source` and `utm_medium` are in the vocab,
- campaign names an initiative, not a date,
- add `https://` if the base URL has no protocol.

Fix and note any corrections, then show the user:

> **UTM link (copy-ready)**
> ```
> https://buildmidwestern.com/connect?utm_source=founderpack&utm_medium=podcast&utm_campaign=ep-42&utm_content=spotify
> ```
> | Parameter | Value |
> |---|---|
> | utm_source | founderpack |
> | utm_medium | podcast |
> | utm_campaign | ep-42 |
> | utm_content | spotify |
>
> Confirm and I'll log it, or tell me what to change.

Wait for confirmation (or an explicit "log it") before writing.

---

## Step 5 — Log it to the master list

Get today's date: `date +%Y-%m-%d`. Build the row:

`| <date> | <source> | <medium> | <campaign> | <content> | <term> | <destination-url> | <full-url> | active | <purpose/notes> |`

Leave Content/Term cells blank (a space between the pipes) when unused. Status is always `active` on a new link.

**Append it with read-then-edit — do NOT use `obsidian append`.** Blind append is unreliable for a markdown table: plain append injects a blank line (breaks the table), and `inline` append merges rows onto one line on repeat use. Instead:

1. Read the master list: `Read` the file at `/Users/jk/Documents/Vaults/Main/0_Marketing Hub/4_Performance/Attribution/UTM Master List.md` (or `obsidian read path="0_Marketing Hub/4_Performance/Attribution/UTM Master List.md"`).
2. Find the **last table line** — either the most recent data row, or the separator `|---|...|` if the log is still empty.
3. `Edit` the file: replace that exact last line with itself + a newline + the new row:
   - old: `<last table line>`
   - new: `<last table line>\n<new row>`
4. This puts the new row on its own line every time, regardless of trailing-newline state. The file tools keep a single clean trailing newline. (Obsidian re-indexes filesystem writes, so the note stays searchable.)

Then confirm: "Logged to UTM Master List — [source] / [medium] / [campaign], dated [date]."

---

## Step 6 — Output

Give the user:
1. The final tagged URL in a code block (copy-ready).
2. Confirmation it was logged.
3. If you added a new source in Step 3, a one-line note that the taxonomy now includes it.

---

## Edge cases

- **FounderPack platform variants:** `source=founderpack`. Episodes → `medium=podcast`, `content=spotify|youtube`. Clips → `medium=social-organic`, `content=clips-linkedin|clips-instagram`. Ask which if unstated.
- **Exec LinkedIn:** `source=linkedin`, `medium=social-organic`, `content=exec-firstname-lastname`. Ask which exec if unstated.
- **Paid (LinkedIn Ads / Meta Ads):** `medium=social-paid`; put audience/keyword in `utm_term` if there is one, else leave blank.
- **Multiple links at once:** build and confirm them as a batch, then append each as its own row.
- **Never** edit the taxonomy except to add a confirmed new source (Step 3). Don't reorder or rewrite it.
