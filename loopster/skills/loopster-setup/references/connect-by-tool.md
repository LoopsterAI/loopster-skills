# Connect Loopster, tool by tool

Server URL for every tool: `https://app.loopster.ai/api/mcp`. Sign-in is OAuth by default. An API key, sent as `Authorization: Bearer loopster_sk_…`, works where a browser sign-in is not possible.

## Claude Code

**With the Loopster plugin** (skills and server together):

```
/plugin marketplace add LoopsterAI/loopster-skills
/plugin install loopster@loopster-skills
```

Then run `/mcp`, choose the Loopster server, and sign in in the browser.

**Server only:**

```
claude mcp add --transport http loopster https://app.loopster.ai/api/mcp
```

Then run `/mcp` to sign in. To use a key instead, add `--header "Authorization: Bearer $LOOPSTER_API_KEY"` to the same command, with the key in an environment variable.

## Codex

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.loopster]
url = "https://app.loopster.ai/api/mcp"
```

Then sign in:

```
codex mcp login loopster
```

To use a key instead, add `bearer_token_env_var = "LOOPSTER_API_KEY"` under the same section and set that environment variable.

With the Loopster plugin: `codex plugin marketplace add LoopsterAI/loopster-skills`, then install **loopster** from **Plugins**.

## Cursor

**Plugin:** install **Loopster** from Cursor's plugins once it is listed. It brings the skills and the server.

**Server only:** in **Settings → MCP → Add server**, or in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "loopster": { "url": "https://app.loopster.ai/api/mcp" }
  }
}
```

Then sign in from the MCP settings. For a key, add `"headers": { "Authorization": "Bearer ${env:LOOPSTER_API_KEY}" }`.

Cursor also reads skills from `.cursor/skills/`, `.agents/skills/` and `.claude/skills/`.

## Claude.ai and Claude Desktop

1. Open **Customize → Connectors → Add custom connector**.
2. Enter the name `Loopster` and the URL `https://app.loopster.ai/api/mcp`.
3. Connect, and sign in in the browser.

To add a skill, open **Customize → Skills → Upload a skill** and upload its zip (the skill folder must be at the top level of the zip). Code execution must be on.

## Other MCP clients

Point the client at `https://app.loopster.ai/api/mcp` as a remote HTTP (streamable) server. Use OAuth if the client supports it; otherwise send the key in the `Authorization` header.

## Roles

- **Member:** read only.
- **Editor:** read, write and run. Use this for the plays.
- **Admin:** everything a key can do, including deleting tables.

Keys are created and revoked in Loopster under **Settings → Loopster API**, never through the API.
