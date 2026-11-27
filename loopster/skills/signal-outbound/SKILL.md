---
name: signal-outbound
description: Find accounts and people with a reason to buy now, and write the one-line why-now opener for each. Signals cover hiring for roles you sell to, fresh funding, a new sales or revenue leader in seat, a competitor or complementary tool in their stack, and launches, expansion and leadership news. Runs on a target-account list or discovers across the market, ranks by recency and ICP fit, and hands off to contacts and outreach. Use when the user says "who should we reach out to this week", "find companies hiring SDRs", "recently funded", "new VP of Sales", "companies using a certain tool", "trigger-based outbound", "signals", "why now", "refresh the signals", or "watch these accounts every week".
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

# Signal outbound

## What you get

A ranked list of accounts (or people) with an active signal. For each one:
- the signal type and its date;
- the evidence, with its source;
- an ICP fit;
- a one-sentence opener a rep can use as-is.

It's saved as `Signals · <type> · <date>` (a table, or a CSV for a small run), ready for `contact-finder` and `outbound-launch`.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (ICP, personas, pains, voice, do-not-contact). The personas decide which job titles count as a hiring signal. The pains decide which news matters.

Call `get_wallet` and note `consumedUsd` and `spendableUsd`. You need both to size a big spend and to report the real cost.

Then check for a Function that already does the job. Look in the "Functions" section of `loopster-context.md`, then `list_functions`, for "Why now · Loopster skill" (or a one-signal version). Reuse it before you build anything (house rules, section 7).

## Pick the signal

| Signal | Why it works | Source | Cost per account |
|---|---|---|---|
| **New leader in seat** (VP or Head in your buyer function, 0–4 months in role) | New leaders change tools in their first 90 days | `search_people` with `monthsInRole` | free |
| **Hiring for roles you serve** (SDR, AE, RevOps…) | They're investing in the problem now | PredictLeads jobs step (`title_keywords`, `posted_within_days`) | about $0.013 |
| **Fresh funding** (last 90 days) | Budget, plus pressure to grow | PredictLeads news step (`receives_financing`) or financing | about $0.013 / $0.087 |
| **Launch, expansion, new office, key hire** | A new initiative creates new needs | PredictLeads news step | about $0.013 |
| **Competitor or complementary tool in stack** | A ready angle: switch, or integrate | PredictLeads tech stack step | about $0.023 |
| **All of the above, summarized** | One call returns the strongest signal and an opener | The "Why now · Loopster skill" Function (jobs + news + AI) | about $0.03–0.05 |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Recipes with exact settings are in `references/signal-recipes.md`.

## Route 1: New leaders (free, market-wide)

This is a search, so it needs no Function.

1. `search_people` with:
   - `monthsInRole` set to `{min: 0, max: 4}`;
   - `seniority` set to VP, Head or C Suite;
   - `jobTitle` set to the persona titles;
   - the ICP company filters;
   - the do-not-contact exclusions.
2. Re-check each record's current `title` (`seniority` can match a past role). Read `roleStartedAt` as the signal date. Use the title excludes and both location filters in `references/signal-recipes.md` (New leaders). Remove any exclude word that appears in a title you want. For example, "Operations" would drop "VP Revenue Operations".
3. Opener angle: what a new leader in that seat is usually rebuilding, tied to a pain from the context file. Not "congrats", and not a countdown of their first days. For example: "New sales leaders at 100-person SaaS companies usually inherit a CRM full of half-built lists."
4. Save as a search table named `Signals · new <role> leaders · <date>` (free). It starts with Auto-run on, so call `set_table_autoplay` with `false` before you add any column. Then go to `contact-finder`, which checks each email's domain against the person's current company.

## Route 2: Account signals (paid per account)

1. **Get the accounts:**
   - the user's target list or a CRM table;
   - or `prospect-list` route A as a company search (free) for discovery. Exclude the do-not-contact domains with `matches: "identity"`; `company` is for people searches only.

   Start with 25 to 100 accounts, not thousands. Take out the do-not-contact domains before you run, so you do not pay to check them.
2. **Pick the engine:**
   - **Best signal of several, plus an opener (the default):** use "Why now · Loopster skill".
     - Find its id in the "Functions" section of `loopster-context.md`, then `list_functions`. Drafts don't show in `list_functions`, so check the context file first.
     - Before you reuse it, read it with `get_function`. Check its title keywords, its 90-day window and its ICP context against this user's. They are fixed inside the Function. If any differ, build a variant, `Why now · <persona> · Loopster skill`, from `references/why-now.function.md` with the `function-builder` steps.
     - If you build a variant, write its id in the "Functions" section of `loopster-context.md` as soon as `create_function` returns. Ask before `publish_function` and before `set_function_agent_access`: both change what other tables and agents can run. After a yes, update that line with its version and its published and open-to-agents status. If you reuse a published Function, skip this.
   - **One signal type** (for example, only hiring or only tech stack): build it once as a PredictLeads column on a table of the accounts, configured for the personas (`references/signal-recipes.md`; `trigger_rows` takes `maxCostUsd`). If the user will run it again, turn it into a Function (`create_function` with `fromTable`, for example `Open roles · Loopster skill`), write its id in the "Functions" section straight away, and ask before publishing it. After a yes, update that line with its version and status. From then on, run the Function with `run_function` or one `run-function` column. Never copy its steps into another table.
   - **Round details for funded accounts** (amount, investors): run the financing recipe only on the accounts whose signal is funding. See `references/signal-recipes.md`.
3. **Choose where it runs:**
   - **About 25 accounts or fewer, and no table wanted:** `run_function` on the domains, once the Function exists. Inputs are keyed by input id (read it with `get_function`). For the first build of a one-signal engine, use its column on a small table (step 2).
   - **More than about 25 accounts, or the user wants the list in Loopster, or it will run on a schedule:** create a table of the domains (`autoplay: false`) with ONE `run-function` column that calls the Function. Map the Function's `Company domain` input to the domain column. Add columns for Signal, Date, Evidence, Opener and Fit that read the `why_now` output: a Formula that parses the cell and then `why_now`, or a field reference with `path` `["why_now", "signal"]` (and `"date"`, `"evidence"`, `"opener"`, `"fit"`).
4. **Price, ask, test, run.**
   - Price it. For a Function, that is `get_function` `costEstimate.maxUsdPerRun` × the number of accounts, plus the AI step measured on 10 accounts (4 × its estimate until you have measured). The estimate can undercount. For a `run-function` column, price it as the Function itself (the same sum). Use this figure for the quote and the big-spend check. For example, 1,000 accounts at about $0.04 is about $40.
   - Ask, with the pricing sentence below. If it is a big spend (house rules, section 4c: over $25 or the "Ask above" amount in `loopster-context.md`, or over 10% of the wallet's `spendableUsd`), use the wording in section 4c.
   - Run 1 account and show its signal, opener and real cost. Then run 10, and show the hit rate and the real cost (`get_wallet` `consumedUsd` before and after). For a table, run with `trigger_rows`: `rowIds` for the 1, 10 or 100 accounts, `columnIds` naming the `run-function` column and the Signal, Date, Evidence, Opener and Fit columns, and an `idempotencyKey`. Send `maxCostUsd` at the agreed amount for the Formula columns. For the `run-function` column, control its spend with the 1, 10, then 100 steps, the 1.5 times stop, and `get_wallet` `consumedUsd` before and after each batch.
   - Run the rest 100 accounts at a time. `run_function` takes no `maxCostUsd`, so the batches are how you control spend. Read `consumedUsd` after each batch and compare it with the quote. If a batch costs more than 1.5 times its share, stop sending batches and ask again.
   - Send an `idempotencyKey` on each `run_function` and `trigger_rows` call. Check `get_run` before any retry, and retry with the same key.
5. **Keep and rank.**
   - Leave `signal: "none"` and signals older than the window out of the ranked list and the CSV. If they are in a table, do not delete them (step 6). The window is 90 days by default; use the same number in the jobs recipe and the Why-now prompt. A `none` is a complete result, so say "no signal found", not "failed".
   - Rank by fit (high, then medium), then recency.
6. **Save it.**
   - **From `run_function`:** a Function keeps no list to page through. Poll `get_run` with the batch `runId`, then call `get_function_run` for each account with `functionId` and its `rowId` as `runId`, right after the batch finishes. Parse each `why_now` (it is JSON text). Write a CSV in the user's working folder and give the path. If the user asks for it in Loopster after the run (the run is already paid for, so don't run it again), `insert_rows` the kept accounts into a blank table `Signals · <type> · <date>` (`autoplay: false`), with columns Domain, Signal, Date, Evidence, Opener and Fit. If they want it in Loopster from the start, use the table route in step 3.
   - **From a table:** the results are already cells. Read them with `list_rows` and write the CSV. To see only active accounts, filter or sort the table, or use the CSV. Keep the `none` rows: they are paid results, and a scheduled table needs them for the next weekly check. Delete rows only if the user asks, and say first that it is permanent and that re-running costs again.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Write the opener (rules)

- One signal, one sentence, under 25 words. Lead with the fact, not "I saw that…".
- The opener feeds the campaign's `{FIRST_LINE}`. The campaign's own message template carries the pain, proof and call to action, so write the opener to lead into it.
- No flattery stacking ("Congrats on the amazing launch!"). Plain and specific.
- Never invent a detail that isn't in the evidence. If the evidence is thin, say so and use a softer angle.

## Show the result

```
Signals · hiring + news · 2026-10-25   (100 accounts checked, real cost $X.XX)
  Active signals: 37   (hiring 18 · funding 6 · launch 9 · leadership 4)
  Top 5:
   1. acme.com    launch   2026-10-19  v3.1 reporting dashboard (company blog)   fit high
      "Acme v3.1 put a reporting dashboard in front of every finance review — …"
   …
Saved: table "Signals · hiring + news · 2026-10-25" (or the CSV path for a small run)
```

Then end the message with this sentence: Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Offer: `contact-finder` for the decision-makers at the active accounts (persona titles with `specificCompanies`), then `outbound-launch` with each opener as a custom field.

## Make it weekly

Offer a weekly refresh, and ask before you create it:
- Schedules run table columns, not Functions. Keep the accounts in a table with ONE `run-function` column that calls the Function. If the table still holds the one-signal column from the first build, turn it into a Function first (`create_function` with `fromTable`), record its id in the "Functions" section, and swap in one `run-function` column.
- Create the schedule with `create_schedule`:
  - `columns`: the `run-function` column plus the Signal, Date, Evidence, Opener and Fit columns that read it. A scheduled run does not refresh columns that read the ones it runs, and a Formula runs only when named, so without these the openers would stay a week old;
  - leave `rerunDependents` off and name the columns yourself, so nothing else on the table (a contact or sequencer column) fires from the schedule;
  - `cadence: "weekly"`, a `dayOfWeek` (0 is Sunday), a `time` (required, HH:MM) and the user's `timezone`;
  - `paused: true`.
- If `create_schedule` will not take a Formula column, schedule only the `run-function` column. After each firing, and before anyone reads the signals, run the reading columns with `trigger_rows` (`columnIds` naming them, `force: true`, `maxCostUsd: 0`). Tell the user this when you ask.
- For a weekly watch, use `cells: "all"`: every firing re-checks every account and pays for every account again. Say so when you ask. `cells: "empty"` only checks accounts added since the last firing, so it never refreshes the old ones.
- Show the measured cost per run from a manual 10-account run (`get_wallet` `consumedUsd` before and after), not the estimate. Monthly cost is that cost per account × the accounts × about 4.3 firings a month. For example, 100 accounts × $0.04 × 4.3 is about $17 a month, and 150 accounts is about $26.
- Over $25 a month is a big spend and needs its own yes, even though the schedule starts paused. Keep the table small, and check `get_wallet` after the first firing.
- Resume it only after a yes: `update_schedule` with `paused: false`.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

For the free new-leader route, re-run the search each week. Saved searches don't refresh by themselves. Log results in `loopster-context.md` (the `gtm-context` update mode), so the best-converting signal moves up.

## If something goes wrong

- **Every result is "none":** the window is too short, or the accounts are too small to make news. Widen `posted_within_days` or switch to the new-leader route.
- **Off-target hiring hits:** tighten `title_keywords` (for example "sales development representative" rather than "sales").
- **The AI step returns prose instead of JSON:** keep the exact JSON shape in the prompt and the words "JSON only". Parse defensively.
- **A provider is refused for "no account":** PredictLeads runs on Loopster's account when `execution_mode` is `"managed"`. Make sure each step sets it.
- **A Function item looks wrong:** read that item with `get_function_run` and check `failedSteps`, `skipped` and the `why_now` value. For a batch, `list_run_items` shows which inputs failed or were skipped. An item can be complete and still say none; report it as not found.
- **`add_function_step` answers 400 for a step:** that step stays a table column. Only the steps listed in `function-builder` go in a Function.
