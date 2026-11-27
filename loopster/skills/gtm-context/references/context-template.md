# Loopster GTM context

Updated: YYYY-MM-DD · Owner: <name>

## Company and offer
- Company: <name> (<domain>)
- We sell: <one sentence>
- Outcome for the customer: <one sentence>

## ICP
- Industries: <list>
- Company size (employees): <range, e.g. 50-500>
- Regions: <list>
- Must-have traits: <list or "none">
- Deal-breakers: <list>
- Loopster contexts: ICP `<ctx id or "none">`, tiers `<ctx id or "none">`

## Personas
| Role | Titles to search | Seniority | Signs the deal? |
|---|---|---|---|
| <e.g. Sales leader> | VP Sales, Head of Sales | VP, Head | Yes |

## Pains we solve
1. <pain>: noticed when <symptom>
2. <pain>: noticed when <symptom>
3. <pain>: noticed when <symptom>

## Proof
| Customer or result | Number | Best for (persona or industry) | OK to name? |
|---|---|---|---|
| <customer> | <e.g. booked 3x more meetings> | <persona> | yes/no |

## Competitors and alternatives
| They use today | Our one-line difference |
|---|---|
| <tool or "spreadsheets"> | <difference> |

## Voice
- Tone: <e.g. plain, peer-to-peer, no hype>
- Length: <e.g. under 90 words, 3 short paragraphs>
- First names: <yes/no>
- Avoid: <words, e.g. "revolutionary", "synergy", "just checking in">
- Call to action: <e.g. a yes/no question, never a calendar link in email 1>

## Do-not-contact
- Loopster table: `<table id>` "<title>"
- Domain column: `<column id>` · LinkedIn URL column: `<column id>` · Email column: `<column id>`
- Company searches: `{"kind":"list","projectId":"<table id>","columnId":"<domain column id>","matches":"identity"}`
- People searches (everyone at those companies): the same list with `"matches":"company"`
- Searches take at most 3 exclusion lists. Keep do-not-contact in one table, and use its Domain column first, so a slot is left for an "already contacted" list.

## Destinations
- CRM: <HubSpot / Salesforce / Attio / none> · connection `<id>`
- Sequencer: <HeyReach / Instantly / Smartlead / Mixmax / none> · connection `<id>` · default campaign `<id>`
- Slack alerts: connection `<id>` · channel `<channel id>` (<#name>)

## Spending
- Ask above: $25 per job (any job whose realistic cost is higher needs a fresh yes; see house rules, section 4c)
- Monthly budget for agent work: <amount or "none">
- Function runs have no cap. Run 1 input, then 10, then 100 at a time. Compare each batch with its quote, and stop and ask if a batch costs more than 1.5 times its quote.
- Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Functions
The register of every reusable Function in this workspace. Any job that will run again goes in a Function: look here first, then `list_functions`, and reuse one before you build another, and never copy a Function's steps into table columns (house rules, section 7). Record a Function on its own line the moment it is created, because drafts don't show in `list_functions`. Update the line when it is published, opened to agents, edited, measured, called by a table or schedule, or retired.

One line per Function:
`<Title>` · `<functionId>` · published yes/no · open to agents yes/no/unknown · inputs: `<input id>` = <what it takes> · outputs: `<output key>` · list price per run: <from costEstimate, if shown> · measured: <cost per run> on <N> rows · used by: <tables and schedules, or "run_function only">

Starter Functions (the Loopster skills carry recipes for these):
- Find work email · Loopster skill: not built
- Why now · Loopster skill: not built

When a play builds one, it replaces that line with a line in the format above.

Standard Functions plays may create. Each is "not built" until a play builds it; the play then adds its line above:
- Find personal email · Loopster skill (contact-finder)
- Find mobile phone · Loopster skill (contact-finder)
- ICP tier · Loopster skill (prospect-list, engager-leads; champion-tracker and inbound-router reuse a scoring Function if one exists)
- Company check · Loopster skill (prospect-list)
- Find lookalikes · Loopster skill (prospect-list)
- Enrich company · Loopster skill (enrich-list, optional)
- Qualify lead · Loopster skill (inbound-router)
- First line · Loopster skill (outbound-launch)
- Buyer review · Loopster skill (outbound-launch)
- Fill CRM gaps · Loopster skill (crm-manager)
- Job change check · Loopster skill (champion-tracker)
- Current profile · Loopster skill (engager-leads)
- Champion note · Loopster skill (champion-tracker, optional)
- Open roles · Loopster skill (signal-outbound, optional; for a different single signal, such as tech stack, title it with that signal)
- Funding round · Loopster skill (signal-outbound, optional; run it only on accounts whose signal is funding)
- Lead brief · Loopster skill (inbound-router, optional)

How a play adds one: build the steps as table columns and test them, then turn the working columns into a Function (`create_function` with `fromTable`), record its id here, and call it from the table with one `run-function` column. If a play uses another title for the same job, record the title it used. A variant for a different persona, segment or provider is titled `<Job> · <qualifier> · Loopster skill`, for example `Why now · <persona> · Loopster skill`, `ICP tier · <segment> · Loopster skill` or `Find mobile phone · <provider> · Loopster skill`. Record each variant on its own line.

## What's working
- Best angle: <angle> (<positive-reply rate>, <n> sent)
- Best proof: <proof>
- Best signal: <signal>

## Retired angles
- <angle>: <why>, retired YYYY-MM-DD

## Campaign log
| Date | Play | List | Angle / proof | Sent | Replies | Positive | Meetings | What worked |
|---|---|---|---|---|---|---|---|---|
