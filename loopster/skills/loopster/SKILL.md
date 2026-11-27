---
name: loopster
description: Start here for anything in Loopster, the go-to-market data and enrichment platform. Explains what the user can get done (prospect lists, verified contacts, buying signals, inbound routing, CRM clean-up, outbound launches), picks the right Loopster play for the request, and holds the rules every Loopster skill follows, including Functions first for any job that will run again. Use when the user mentions Loopster, asks "what can Loopster do", wants leads, contacts, enrichment, signals or outbound and no other Loopster skill clearly fits, wants a job they will run again, or before a first Loopster task in a session.
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

# Loopster: start here

Loopster finds companies and people, enriches them from its own data and dozens of providers, and pushes the results into the tools where work happens: CRMs, sequencers and Slack. From an AI agent, it can also **build** things: reusable Functions (the default for anything that runs again, email waterfalls included), plus tables, schedules and webhooks when work must be seen, pushed or run on its own.

## Before anything else

1. **Connected?** If Loopster tools are missing or answer 401/403, follow the `loopster-setup` skill.
2. **House rules:** read `references/house-rules.md` once per session. In short:
   - read what the workspace already has (tables, contexts, connections, Functions, wallet)
   - **Functions first** (house rules, section 7): any job that will run again goes in a Function, even one step. Reuse one first (the "Functions" section of `loopster-context.md`, then `list_functions`). If none fits, use `function-builder`: build and test the steps as table columns first, then `create_function` with `fromTable`, and record the id. Build a Function directly only from a recipe the pack ships, such as Find work email or Why now. A table is only for rows the user wants in Loopster, more than about 25 results to keep, a push to a CRM, sequencer or Slack, a schedule or webhook, or a step a Function can't take. It calls the Function with one `run-function` column. Never copy a Function's steps into columns. One action, once: `run_capability`.
   - cheapest rung first: free Loopster Data, then the user's accounts, then paid data, then AI, and AI web research ("Loopgent", "Find LinkedIn profile URL", any "(Web Search)" model) last, only for what's left. Asked to research something on company websites (pricing pages, about pages)? Offer website text (`predict-leads-website-subpages`) plus an AI column without web search first, even when the user named the web agent (house rules, section 3b), and measure 3 rows before quoting the rest
   - price, ask, cap, then run. `run_function` takes no `maxCostUsd`, so control a Function's spend with the 1, 10, then 100 steps: compare each batch's real cost with its quote (`get_wallet` `consumedUsd` before and after), and stop and ask if a batch costs over 1.5 times its share
   - a big spend (over $25 or the "Ask above" amount in `loopster-context.md`, over 10% of the wallet, AI web research on more than 25 rows, or a schedule or Auto-run table expected to cost over $25 a month, counting the Functions its `run-function` columns call) always gets its own yes, in every permission mode
   - one record, then ten, then all
   - an explicit yes before anything leaves Loopster

   Every message that gives a cost or a price ends with this sentence: "Real usage depends on your use case and settings, so always check the final cost estimate before you run."
3. **GTM context:** look for `loopster-context.md` in the working folder, then `~/.loopster/context.md`. If neither exists and the request is a play (not a one-off lookup), offer the `gtm-context` skill first. It takes about five minutes, and every play reads it.

## Answer "what can Loopster do?"

Talk about outcomes the user cares about, in their words. Pick three that fit what you know about them, then offer to run one now:

- "Build a list of companies and decision-makers that match your ICP, without the customers you already have."
- "Get verified work emails and mobile numbers for a list, free sources first."
- "Find companies that just raised, started hiring for a role you sell to, or hired a new leader, and draft the why-now message."
- "Track your past champions and tell you, within weeks, when one joins a company that fits your ICP."
- "Turn the people who engaged with a LinkedIn post into qualified leads."
- "Enrich, score and route every inbound lead to the right rep in Slack within minutes."
- "Audit your CRM, fill the gaps, remove duplicates, and flag job changes and closed-lost deals worth reviving."
- "Push an approved list into your HeyReach, Instantly or Smartlead campaign, with personal first lines."

## Pick the play

| The user wants | Skill |
|---|---|
| To connect Loopster or fix the connection | `loopster-setup` |
| To set up their ICP, offer, proof, voice and do-not-contact list | `gtm-context` |
| A list of target companies or people | `prospect-list` |
| Emails or phone numbers for people they already have | `contact-finder` |
| To check or clean a list of emails before a send | `email-check` |
| To add data to a CSV or list (firmographics, LinkedIn, anything) | `enrich-list` |
| A person's LinkedIn URL, latest LinkedIn profile, or current company and title | `enrich-list` (free Loopster Data first; see house rules, section 3b) |
| A job they will run again, or a play needs a Function that doesn't exist yet | `function-builder` (plays call it themselves; look for an existing Function first) |
| Accounts that are raising, hiring, changing leaders or tools, and a reason to reach out now | `signal-outbound` |
| To know when past customers or champions change jobs | `champion-tracker` |
| Leads from LinkedIn post engagers or event guests | `engager-leads` |
| Inbound leads enriched, scored and routed automatically | `inbound-router` |
| A cleaner, fuller CRM, or closed-lost deals to revive | `crm-manager` |
| To send a finished list into a sequencer campaign | `outbound-launch` |

Plays chain. A typical run goes `prospect-list` or `signal-outbound`, then `contact-finder`, then `outbound-launch`. Say which step comes next when one finishes.

Any job that takes more than a few calls also follows the `fewer-requests` skill: every MCP call is one request against the workspace's limits.

If the request fits none of these, choose the Loopster surface with `references/choosing-the-surface.md` (search, then Function, then capability, then table, in that order) and work from `references/tools-map.md`.

## How to work

- **Narrate:** say what you are about to do, then what happened. Use tables and counts, not JSON.
- **Reuse:** keep ids and results from earlier calls instead of fetching them again. Write every Function id you create or find, with its measured cost per run, in the "Functions" section of `loopster-context.md`. If no context file exists yet, use the `gtm-context` skill's "record a Function" mode to create it, so the id is never lost.
- **Quiet identity checks:** don't announce workspace or sign-in checks unless something is wrong.
- **One question at a time** when you need input. Offer a sensible default the user can accept with "yes". If they give a full spec up front, skip the questions.
- **Ask, don't pick:** if the request can be read two ways and the choice changes cost or what gets sent, ask.
- **Keep work findable:** name tables and Functions as `references/house-rules.md` describes, and tell the user where to find them in Loopster.

## Getting help

- Help Center: start at the home page, help.loopster.ai.
- For a product problem, offer to send it to the Loopster team with `send_feedback`, as house rules, section 12 says: ask first, show the message, and never include secrets or personal data.
