# Loopster skills

Run real go-to-market plays with Loopster from your AI agent: Claude Code, Claude.ai, Codex, Cursor or any MCP client.

Example session (illustrative numbers):

```
> Find VPs of Sales who started in the last 4 months at 50–500 person US SaaS companies,
  skip our customers, get their work emails, and add them to my HeyReach campaign
  with a first line about their new role.

⏺ signal-outbound  5,650 match · 180 kept (max 2 per company, customers removed)        free
⏺ contact-finder   152 of 180 emails · 131 free from Loopster Data, 21 paid             $0.14
⏺ outbound-launch  12 held back (already in a campaign or connected) · 140 first lines
                   written, top tier reviewed · pushed to "Q4 new leaders" (paused)
Done. The campaign is ready to start in HeyReach.
```

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## What's inside

| Skill | What it gets done |
|---|---|
| `loopster` | Start here: what Loopster can do, which play fits, and the rules every play follows |
| `loopster-setup` | Connect Loopster to your AI tool and get a first free result |
| `gtm-context` | Your ICP, offer, proof, voice, do-not-contact list and destinations, saved once and read by every play |
| `prospect-list` | Companies and decision-makers that fit your ICP, without the customers you already have |
| `contact-finder` | Work emails and phones, free sources first, paid only for the misses |
| `email-check` | A list checked before a send: keep, risky or remove, free checks first, one verifier on the rest |
| `enrich-list` | Firmographics, tech stack, funding, open roles and more for any list, no table needed |
| `fewer-requests` | The same work in fewer API requests: full search pages, bulk writes, one run, cheap waiting |
| `function-builder` | Turn a job you repeat into a one-call tool anyone on the team can run |
| `signal-outbound` | Accounts that are hiring, raising, changing leaders or tools, with a why-now line each |
| `champion-tracker` | Customer alumni in buying roles, and a free monthly check on where your champions went |
| `engager-leads` | People who engaged with LinkedIn posts or attended events, qualified and ready for outreach |
| `inbound-router` | Every form fill enriched, scored and routed to the right rep within minutes |
| `crm-manager` | A CRM audit, gaps filled, duplicates found, job changes flagged and closed-lost revived; approved changes only |
| `outbound-launch` | A finished list into HeyReach, Instantly, Smartlead or Mixmax: checked, personalized and pushed safely |

### Single-step skills

The plays above run a whole job. These do one step, for when that step is all you need. Each names the play to use for the whole job.

| Skill | One step |
|---|---|
| `work-email` | Work emails for a few named people, free first |
| `work-phone` | Phone numbers for a few named people, free first |
| `verify-email` | One verifier over addresses you already have: send, risky, do not send |
| `linkedin-profile` | LinkedIn URLs from an email or name + company, free first |
| `decision-makers` | Buyers and influencers at companies you name, one free search |
| `refresh-contacts` | Who on an old list moved or changed title; changes only on your yes |
| `enrich-accounts` | Industry, size, location and more for a list of companies, free |
| `company-brief` | A short, sourced research brief per company |
| `tech-stack` | Which tools these companies use |
| `headcount-growth` | Who is growing or shrinking, in bands |
| `hiring-signals` | Open roles per company for one team |
| `scrape-website` | The text of given pages into a table |
| `icp-to-filters` | Your ICP in plain words as search filters, with a count |
| `market-size` | Counts by country, size or industry, no list |
| `account-tiers` | Your accounts in tiers 1 to 4, with visible weights |
| `lead-score` | A to D grades from the fields a table already has |
| `buyer-check` | Buyer, influencer or not, per person |
| `account-question` | One yes/no question answered for every company |
| `dedupe-plan` | Duplicates found and a merge plan; nothing deleted |
| `record-audit` | Company records checked against fresh data; changes only on your yes |

## How the plays behave

- **Free first:** Loopster Data and your own connected accounts before anything paid.
- **Price, ask, cap:** every paid step shows its price and runs only after a yes, with a spending cap on table and capability runs. AI steps (whose real cost can come in above the estimate) and Functions run on one record, then ten, then a hundred at a time, with the real cost checked after each batch.
- **One, then ten, then all:** nothing runs at scale before you've seen a result.
- **Nothing leaves Loopster without a yes:** CRM writes, sequencer pushes, Slack posts, schedules and public share links each ask first.
- **Live tables stay safe:** a change to a table that's already running is tried on a few rows in its sandbox first.
- **Your workspace, your Functions:** reusable Functions are built in your workspace, where you can open and edit them.

## Install

You need a Loopster account (https://app.loopster.ai) and one of the tools below.

Fastest way: give your AI agent [`GETTING_STARTED.md`](./GETTING_STARTED.md) (paste its link or contents) and say "set up Loopster for me". It runs what it can and tells you the few steps only you can do, such as signing in. To install by hand:

**Claude Code**

```
claude plugin marketplace add LoopsterAI/loopster-skills
claude plugin install loopster@loopster-skills
```

Or, inside a session: `/plugin marketplace add LoopsterAI/loopster-skills`, then `/plugin install loopster@loopster-skills`. Then run `/mcp` and sign in to Loopster.

**Claude.ai, Claude Desktop and Cowork:** under **Customize → Plugins → Add**, choose **Add marketplace** and enter `https://github.com/LoopsterAI/loopster-skills`, then add **Loopster**. Connect Loopster from the plugin's **Connectors** tab and sign in. One plugin gives you every skill and the connector. On Team and Enterprise plans, an Owner can add it for the whole organization.

**Codex**

```
codex plugin marketplace add LoopsterAI/loopster-skills
```

Install **loopster** from **Plugins**, then run `codex mcp login loopster`.

**Cursor:** install the Loopster plugin, or add `https://app.loopster.ai/api/mcp` under **Settings → MCP** and copy the folders inside `loopster/skills/` (each holds a `SKILL.md`) into `.cursor/skills/`.

**Any other agent:** connect `https://app.loopster.ai/api/mcp` as a remote MCP server, then copy the folders inside `loopster/skills/` into the folder your agent reads skills from (many read `.agents/skills/`). If it can read only one instructions file, use `dist/AGENTS.md` for Loopster work: it holds the rules and every skill, so it is large.

Single skills: each skill is also a zip in `dist/`, for tools that take one skill at a time (on Claude.ai, **Customize → Skills**, with code execution on). The plays call each other by name, so add `loopster`, `loopster-setup` and `gtm-context` first.

## First run

Start a new chat and say "Set up Loopster". The `loopster-setup` skill checks the connection and gets a first free result. Then say "Set up my GTM context" (about five minutes), and ask for what you need, for example "Build a list of VPs of Sales at US fintechs".

## Help

- Loopster Help Center: https://help.loopster.ai
- Problems or ideas: ask your agent to send feedback to Loopster, or contact support from the Help Center.

MIT licensed.
