# Getting started with Loopster skills

> This file is written for your AI agent. Paste its link or contents and say "set up Loopster for me".
>
> Agent: run the shell commands yourself. For slash commands and settings screens, give the user the exact text to type or the menu path to click, then wait. The user signs in.

## 1. Install the skills and the Loopster connection

Work out which tool you are running in, then:

**Claude Code** (one install gives the skills and the server). In the shell:

```
claude plugin marketplace add LoopsterAI/loopster-skills
claude plugin install loopster@loopster-skills
```

The same steps typed by the user inside a session: `/plugin marketplace add LoopsterAI/loopster-skills`, then `/plugin install loopster@loopster-skills`.

**Codex:**

```
codex plugin marketplace add LoopsterAI/loopster-skills
```

Install **loopster** from **Plugins**. If the plugin's server doesn't appear, add this to `~/.codex/config.toml`:

```toml
[mcp_servers.loopster]
url = "https://app.loopster.ai/api/mcp"
```

**Cursor:**

1. Install the Loopster plugin if it's listed.
2. Otherwise, add the server under **Settings → MCP**:

   ```json
   {"mcpServers": {"loopster": {"url": "https://app.loopster.ai/api/mcp"}}}
   ```

   And copy `loopster/skills/*` into `.cursor/skills/` (or `~/.cursor/skills/`).

**Claude.ai, Claude Desktop or Cowork** (the user clicks):

1. **Customize → Plugins → Add → Add marketplace**, with `https://github.com/LoopsterAI/loopster-skills`, then add **Loopster**.
2. On the plugin's **Connectors** tab, connect Loopster and sign in.

If plugins aren't available, add the connector under **Customize → Connectors → Add custom connector** (`https://app.loopster.ai/api/mcp`), and upload the skill zips from `dist/` under **Customize → Skills**, starting with `loopster.zip`, `loopster-setup.zip` and `gtm-context.zip`.

**Anything else:** connect `https://app.loopster.ai/api/mcp` as a remote HTTP MCP server, and copy the folders inside `loopster/skills/` into the folder the agent reads skills from (often `.agents/skills/`). If it reads only one instructions file, give it `dist/AGENTS.md` for Loopster work.

## 2. Sign in

- **Claude Code:** `/mcp`, choose Loopster, and sign in in the browser.
- **Codex:** `codex mcp login loopster`.
- **Cursor and Claude:** sign in from the MCP or connector settings.

No browser available (servers, CI)? The user creates an API key in Loopster under **Settings → Loopster API** (Editor role) and stores it as a secret. Send it as `Authorization: Bearer …`. Never paste a key into the chat.

## 3. Run the setup skill

Run the `loopster-setup` skill (`/loopster:loopster-setup` in Claude Code). If your tool doesn't list skills right after installing, restart it, or find and read the file yourself:

```
find ~/.claude ~/.codex ~/.cursor ~/.agents -path '*/loopster-setup/SKILL.md' 2>/dev/null | head -1
```

It checks the connection, looks at the workspace, and gets a first free result.

## 4. Next

- Run `gtm-context` once (about five minutes). Every play reads it.
- Then run the `loopster` skill and ask "what can Loopster do for me?". It picks the play that fits.
