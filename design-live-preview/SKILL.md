---
name: design-live-preview
description: Use when JK asks for a localhost view of design work, wants to watch you build, compare design options live, leave comments or feedback on a design, run a feedback round, or open the scratchpad. Applies to print pages, web pages and UI mockups built as HTML by one or more designer agents.
---

# Design Scratchpad

A local viewer. JK watches each option build, pins comments on elements, and clicks Send. You read the comments from disk. Nothing to copy or paste.

Tool: `/Users/jk/Documents/Vaults/Main/0_Marketing GIT/Design Scratchpad/server.mjs`

## Hard rules

- Never read or rebuild the viewer (server.mjs, viewer/*) unless JK asks to change it. Create option folders and read feedback only.
- One designer agent per option. For feedback rounds, resume that same agent with SendMessage. Never spawn a new one for a revision.
- Material redesign of a reviewed option = new folder with a new letter. Do not overwrite.
- Keep the designer brief block below word-for-word the same every session (it caches). Put the project brief after it.

## Folders

The root lives in the project folder, one per round (`<project>/round1/`). A new round is a new root. One subfolder per option under a root: `<letter>-<name>` (`a-report`, `b-editorial`). The letter is the tab and label. Entry file: `index.html`, else the first `*.html`. `--entry <file>` pins a name. `assets/`, `references/`, `renders/`, `node_modules` are not options. Keep letters unique.

- Print: `section.page` frames at US Letter, 816x1056.
- Web or UI: one tall page is fine. No frames means the whole document is one page.

## Start the server

First run `pgrep` (below). If this root is already served, reuse its URL from the log; do not start a second server. Run unsandboxed (fs.watch fails with EMFILE in the sandbox). Start it detached so it outlives the session and the 2-hour background limit:

```bash
mkdir -p "<dir>/.scratchpad" && nohup node "/Users/jk/Documents/Vaults/Main/0_Marketing GIT/Design Scratchpad/server.mjs" --root "<dir>" [--entry f.html] [--pages css] [--width 1440] [--height 900] [--port 5178] > "<dir>/.scratchpad/server.log" 2>&1 &
sleep 1; cat "<dir>/.scratchpad/server.log"
```

The log has the URL: give it to JK with one line: "Press C to comment, then Send. All tab is a canvas: scroll or pinch, Shift+1 fits." Use this per-root log, not `$TMPDIR` (it differs between sandboxed and unsandboxed calls). `.scratchpad/` is not watched, not served and hidden from Obsidian. Loopback only; moves to the next free port if busy. Print defaults to 816x1056. Web with no page frames defaults to 1440 wide (Desktop; JK can switch to Phone 390 or Tablet 768). `--width` and `--height` also resize print page frames.

Status and stop also need unsandboxed Bash (the sandbox cannot list processes):

```bash
pgrep -fl "Design Scratchpad/server.mjs"     # what is running, with each --root
kill <pid>                                   # stop one root's server
pkill -f "Design Scratchpad/server.mjs"      # stop all of them
```

Stop a server only when JK says the round is over. Other roots may be running for other projects.

## Designer brief block (include every time, unchanged)

```
- Write a skeleton of all pages early (empty frames with headings), then fill in.
- Save often. JK watches the viewer live and sees every save.
- Only edit inside your own option folder.
- Set a meaningful <title> (shown as the option name) and optionally <meta name="description"> (shown as the subtitle).
- Keep stable class names or ids on key elements so comment selectors stay meaningful.
- Use relative asset paths, never absolute file:// paths.
- When you get feedback lines: grep the selector or quoted text, patch that region, save. Do not re-read whole files or loop on screenshots. Then run done with the ids you fixed.
```

Give designers the `done` command with the root path filled in (see Mark fixed).

## Feedback loop

1. Arm the wait with `run_in_background: true` (works sandboxed):

```bash
node "/Users/jk/Documents/Vaults/Main/0_Marketing GIT/Design Scratchpad/server.mjs" wait --root "<dir>" --timeout 6600
```

2. `--root` is required (`wait` exits 2 without it). When JK clicks Send, it prints the feedback and exits, which wakes you. A timeout prints `no feedback yet`. Re-arm it after every relay.
3. The last sent round is also in `<root>/.scratchpad/feedback.md`. Read that, never comments.json. Format: header `# Round N · date time`, `root: <abs>`, then one line per comment:
   - `B p2 #7 h2.section-title "element text": body` (pinned to an element)
   - `B all #8: body` (whole option)
   - `* #9: body` (all options)
4. Relay each option's lines verbatim to its designer with SendMessage, batched in one message per option. `*` lines go to every designer.
5. Re-arm `wait`.

## Mark fixed

Designers run this with the ids they fixed. JK sees checkmarks. If JK reopens a done comment it goes back to new and reappears in the next feedback.md, so expect old ids to return.

```bash
node "/Users/jk/Documents/Vaults/Main/0_Marketing GIT/Design Scratchpad/server.mjs" done --root "<dir>" 7 8 9
```

## Render to PDF or PNG (headless Chrome)

Only when JK asks for files. Unsandboxed. Chrome writes the PDF, then hangs: poll for the file, then kill Chrome. Save to `<root>/renders/` (not watched).

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --user-data-dir="$(mktemp -d)" --no-pdf-header-footer --print-to-pdf=out.pdf "http://localhost:5178/a-report/index.html" &
pdftoppm -r 110 -png out.pdf out
```

## Gotchas

- Dotfiles, `.scratchpad/`, `renders/`, `node_modules` and editor temp files never trigger reloads. Root-level file changes reload every option.
- `wait` and `done` work sandboxed. The server start, `pgrep` and `pkill` need unsandboxed.
