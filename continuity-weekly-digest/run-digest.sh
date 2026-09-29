#!/bin/zsh
# Scheduled runner for the continuity-weekly-digest skill.
# Invoked by launchd Friday morning (after the daily meeting catalog). Logs each run to run.log.

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

CLAUDE="$HOME/.local/bin/claude"
VAULT="/Users/jk/Documents/Vaults/Main"
LOG="$HOME/.claude/skills/continuity-weekly-digest/run.log"

echo "" >> "$LOG"
echo "===== $(date '+%Y-%m-%d %H:%M:%S %Z') START =====" >> "$LOG"

cd "$VAULT" || { echo "cd to vault failed" >> "$LOG"; exit 1; }

"$CLAUDE" -p "This is the scheduled automated run. Use the continuity-weekly-digest skill now to assemble this week's marketing continuity digest (the David packet), following that skill's steps exactly — including the sensitivity gate. Print the skill's run summary." \
  --permission-mode acceptEdits >> "$LOG" 2>&1
rc=$?

echo "===== $(date '+%Y-%m-%d %H:%M:%S %Z') END (exit $rc) =====" >> "$LOG"
exit $rc
