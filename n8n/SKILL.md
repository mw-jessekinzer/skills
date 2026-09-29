---
name: n8n
description: Work with n8n workflows through the right surface — the n8n MCP server for building and editing workflows (it has node schemas and validation), the REST API via ~/.claude/scripts/n8n.sh for reads, execution history, debugging, and backups. Use whenever the task involves n8n workflows, automations, nodes, credentials, or execution errors. Triggers on "n8n", "my workflow", "the automation", "why did the workflow fail", "build me a workflow", "check the executions", "export the workflow". Do NOT use for Zapier, Make, or other automation platforms.
---

# n8n — which surface to use

> **Plan state as of 2026-09-01: n8n Cloud 14-day trial, so the REST API is OFF.**
> The public API is a paid feature. `n8n.sh` will return 401 or the Settings >
> n8n API page will be missing, and that is expected, not a misconfiguration.
> Until the account upgrades, use MCP for everything and tell JK plainly when a
> task wants an API-only capability. Delete this block once the plan is paid and
> `n8n.sh check` passes.

Two ways into the same instance. They are not interchangeable, and picking
wrong is the main source of broken workflows.

- **MCP server** (`mcp__n8n__*`) — has node type definitions, live dropdown
  resolution, and validation. Use it for anything that writes workflow structure.
- **REST API** (`~/.claude/scripts/n8n.sh`) — plain HTTP, no schema knowledge.
  Fast and reliable for reads and operations. It will happily accept malformed
  node JSON and return 200, so never author through it.

## Routing table

| Task | Surface | Why |
|---|---|---|
| Build a new workflow | MCP | `search_nodes`, `get_node_types`, `validate_workflow`, `create_workflow_from_code` |
| Add or change nodes on an existing workflow | MCP | `update_workflow` does atomic partial updates; the API's PUT overwrites the whole document |
| Figure out how a node is configured | MCP | `get_node_types`, `validate_node_config` |
| Resolve a real Slack channel / Sheet / table ID for a node | MCP | `explore_node_resources` hits the live credential |
| Dry-run before publishing | MCP | `test_workflow` + `prepare_workflow_pin_data` |
| Publish / unpublish | MCP | `publish_workflow` / `unpublish_workflow` |
| Compare two versions | MCP | `get_workflow_versions_diff` |
| "What workflows do I have" | API | `n8n.sh workflows`, one call, compact output |
| "Why did it fail" | API | `n8n.sh errors` pulls the failing node and message directly |
| Execution history, run counts, timing | API | `n8n.sh executions --status error --workflow <id>` |
| Export / back up workflow JSON | API | `n8n.sh export <id> file.json` |
| Restore or bulk-import previously exported JSON | API | `n8n.sh create @file.json` — the JSON was already valid |
| List tags, variables, projects, credentials, users | API | one-liners, no MCP equivalent for most |
| Archive or delete | API | `n8n.sh archive <id> --yes` |

**Default when unsure:** if the task changes what nodes do, use MCP. If it only
reads state or moves whole documents around, use the API.

**Don't cross the streams mid-task.** Reading with the API and writing with MCP
in the same task is fine. Building a workflow with MCP and then patching one node
via `n8n.sh update` is not — the PUT replaces the full document and will drop
whatever MCP just set.

## Setup and credentials

- Base URL and API key live in the macOS Keychain, services `n8n-base-url` and
  `n8n-api-key`. Never put either in a config file or on a command line.
- The API is unavailable on the n8n free trial. Paid or self-hosted only.
  To switch it on after an upgrade: create a key at Settings > n8n API, run
  `security add-generic-password -a "$USER" -s n8n-api-key -U -w` in Terminal,
  then `n8n.sh check`. The base URL is already stored. Delete the trial banner
  at the top of this file once that passes.
- Run `n8n.sh check` first if anything is behaving oddly. It verifies URL, auth,
  and read access in one call.
- `chmod` and Keychain reads under `~/.claude/` need unsandboxed Bash.

## Version floors on the MCP server

If an MCP tool is missing, the instance is too old rather than misconfigured:

| Tool | Needs |
|---|---|
| builder tools, `update_workflow`, `archive_workflow`, `publish_workflow` | 2.12.0 |
| `test_workflow`, `prepare_workflow_pin_data` | 2.15.0 |
| `search_workflow_executions` | 2.20.0 |
| `list_credentials` | 2.21.0 |
| `validate_node_config` | 2.25.1 |
| `get_workflow_best_practices`, `explore_node_resources`, `list_workflow_tags` | 2.27.0 |
| agent tools | 2.34.0 (preview) |
| `get_workflow_versions_diff` | 2.36.0 |

## Known gotchas

- **Empty `search_workflows` is usually scoping, not a broken connection.** n8n
  docs say only workflows explicitly enabled for MCP are reachable. If MCP sees
  nothing but `n8n.sh workflows` lists plenty, enable them in the n8n UI.
- **`n8n.sh workflows` excludes pinned data.** Full workflow JSON is enormous;
  the list view strips it. Use `n8n.sh workflow <id> --raw` when you need it all.
- **`update` republishes by default.** A PUT against an active workflow goes live
  immediately unless you pass `--no-publish`.
- **`delete` is permanent, `archive` is not.** Prefer archive.
- **Export before any destructive change.** `n8n.sh export <id>` costs one call
  and makes every mistake reversible.

## Common recipes

```bash
n8n.sh check                                  # auth + reach
n8n.sh workflows --active true                # what's live right now
n8n.sh workflows --name "lead"                # find by name
n8n.sh errors --limit 5                       # recent failures + error message
n8n.sh errors --workflow 42                   # failures on one workflow
n8n.sh executions --workflow 42 --limit 50    # run history
n8n.sh execution 9981 --data                  # full payload of one run
n8n.sh export 42 backup.json                  # back up before editing
n8n.sh raw GET /insights/summary              # anything not wrapped yet
```
