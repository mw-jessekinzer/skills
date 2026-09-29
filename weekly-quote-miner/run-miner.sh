#!/bin/zsh
# Scheduled runner for the weekly-quote-miner skill.
# Invoked by launchd Friday 9:15am. Logs each run to run.log.

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

CLAUDE="$HOME/.local/bin/claude"
LOG="$HOME/.claude/skills/weekly-quote-miner/run.log"

echo "" >> "$LOG"
echo "===== $(date '+%Y-%m-%d %H:%M:%S %Z') START =====" >> "$LOG"

cd "$HOME" || exit 1

"$CLAUDE" -p "This is the scheduled automated run. Use the weekly-quote-miner skill now: mine the past week's Airspeed call transcripts for client quotes and post the digest to #client-quotes, following that skill's steps exactly. Print the skill's run summary." \
  --allowedTools "ToolSearch,Agent,Bash(date:*),mcp__airspeed__list_calls,mcp__airspeed__get_call_info,mcp__plugin_slack_slack__slack_send_message" \
  >> "$LOG" 2>&1
rc=$?

echo "===== $(date '+%Y-%m-%d %H:%M:%S %Z') END (exit $rc) =====" >> "$LOG"
exit $rc
