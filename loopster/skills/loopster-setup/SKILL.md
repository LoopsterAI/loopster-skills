---
name: loopster-setup
description: Connect Loopster to Claude Code, Codex, Cursor, Claude Desktop or any MCP-capable AI tool, confirm the connection works, and get a first free result in about two minutes. Use when the user says "set up Loopster", "connect Loopster", "install the Loopster MCP", "Loopster isn't working", "sign in to Loopster", or when a Loopster tool is missing or answers 401/403.
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

# Set up Loopster

## What you get

Loopster connected to this AI tool, a quick check of what the workspace holds, and one free result, so the user can start a real play straight away.

## Step 1: Is Loopster already connected?

Call `get_wallet`.

- **It answers:** Loopster is connected. Go to Step 3.
- **The tool does not exist:** the MCP server is not set up. Go to Step 2.
- **401 or 403:** the server is set up but not signed in, or the key is wrong. Go to Step 2 and sign in again, or replace the key.

## Step 2: Connect

Find the tool the user is in, and follow its section in `references/connect-by-tool.md`. In short:

- **Claude Code with the Loopster plugin:** the server comes with the plugin. Run `/mcp`, pick `loopster`, and sign in in the browser.
- **Claude Code without the plugin:** run `claude mcp add --transport http loopster https://app.loopster.ai/api/mcp`, then `/mcp` to sign in.
- **Codex:** add the server to `~/.codex/config.toml`, then run `codex mcp login loopster`.
- **Cursor:** install the Loopster plugin, or add the server in **Settings → MCP**, then sign in.
- **Claude.ai or Claude Desktop:** **Customize → Connectors → Add custom connector**, with the URL `https://app.loopster.ai/api/mcp`.
- **Anything else:** point it at `https://app.loopster.ai/api/mcp` and sign in, or send an API key as `Authorization: Bearer …`.

OAuth sign-in connects the workspace chosen in the browser. To work in another workspace, sign in again and pick it.

**API key instead of sign-in** (servers, CI, tools without a browser): the user creates a key in Loopster under **Settings → Loopster API**. Use the **Editor** role to build and run; **Member** can only read. Never ask the user to paste a key into the chat. Have them put it in an environment variable or the tool's secret settings.

After connecting, some tools need a restart before the new tools appear. Then call `get_wallet` again.

## Step 3: Look around (free)

Run these five calls in parallel, then summarize in a few lines:

| Call | Tell the user |
|---|---|
| `get_wallet` | Plan and `spendableUsd` |
| `list_connections` | Their own connected accounts (CRM, sequencers, Slack), and how many providers Loopster's account covers |
| `list_contexts` | Whether an ICP and tier list exist. If not, suggest adding one in Loopster: plays use it. |
| `list_tables` with `pageSize: 5` | The 5 newest tables. If a `nextCursor` comes back, there are more: say "more than 5" unless the answer gives a total |
| `list_functions` | How many reusable Functions exist, and their titles (for example Find work email · Loopster skill) |

Also read the "Functions" section of `loopster-context.md` (working folder, then `~/.loopster/context.md`) if there is one. `list_functions` shows only published Functions that are open to agents, so call `get_function` on each id in the file that it does not show:

- It answers: report it as a draft, or published but not open to agents.
- It fails: say the file is out of date.

Plays reuse these Functions first, so this is where the user learns what is already built.

Keep it short. For example: "You're on the Unlimited plan, with `<spendableUsd>` to spend. HubSpot, HeyReach and Slack are connected. Your ICP and tier list are set up. You have more than 5 tables and 3 reusable Functions: Find work email, Why now, ICP tier."

## Step 4: First win (free)

Ask for the user's company website, or use the domain of their email if you know it. Then run Loopster Data's free company lookup:

- `run_capability` with `templateId: "loopster-data-enrich-company"`, `inputs: [{"domain": "<their domain>"}]` and `maxCostUsd: 0`.
- Use a capability here, not a Function or a table: it is a one-off connection check, it is free, and there is nothing to keep.
- Poll `get_run`, then read `list_run_items`. Parse `output` as JSON.
- Show name, industry, employee range and location. If `found` is false, say Loopster Data has no record for that domain and try a well-known domain instead.

## Step 5: Offer the next play

If there is no `loopster-context.md` yet, offer `gtm-context` first (about five minutes): every play reads it. Then offer two or three plays that fit what you saw. For example:

- A CRM is connected → `crm-manager` or `inbound-router`.
- A sequencer is connected → `prospect-list` then `outbound-launch`.
- Nothing connected yet → `prospect-list` (free to search) or `enrich-list`.
- No Functions yet and the user will look up emails or phones often → `contact-finder`, which builds the Find work email Function on first use. For any other job they will repeat → `function-builder`. Once a Function exists, plays run it instead of building their own columns.
- Functions already exist → say which ones, and that the plays will run them first.

Anything the user will run again belongs in a Function. A table is only for rows that must live in Loopster, a push to a CRM, sequencer or Slack, a schedule or webhook, more than about 25 results to keep, or a step a Function can't take (`references/house-rules.md`, section 7). The `loopster` skill lists every play.

## If something goes wrong

- **The browser sign-in never opens:** copy the sign-in link the tool prints and open it by hand. In a remote or headless environment, use an API key instead.
- **403 "Invalid API key":** the key is wrong or was revoked. Create a new one under **Settings → Loopster API**.
- **401 with `key_expired`:** the key passed its end date. Create a new one.
- **The wrong workspace's data shows up:** sign in again and pick the right workspace, or use that workspace's key.
- **Tools still missing after connecting:** restart the AI tool, then check its MCP list shows `loopster` as connected.

## Learn more

- Connect Loopster to Claude Code and other AI tools (MCP): https://help.loopster.ai/en/articles/17693712-connect-loopster-to-claude-code-and-other-ai-tools-mcp
- Use, rotate and revoke a Loopster API key: https://help.loopster.ai/en/articles/17684096-create-and-revoke-a-loopster-api-key
