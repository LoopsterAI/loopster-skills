# Loopster skills for any AI agent

Connect the Loopster MCP server (https://app.loopster.ai/api/mcp), then follow the skill that matches the job.
Wherever a skill says `references/<file>.md`, that file is in this document: the shared files at the top,
and each skill's own files right after its section. It is large: load it for Loopster work only.

<!-- references/choosing-the-surface.md -->
# Choosing the Loopster surface

Loopster offers five ways to get work done from an agent. Go down this list and pick the first that fits. A table is the exception, not the default.

## 1. Search: new companies or people

`search_people` / `search_companies` over Loopster Data. Free, up to 50 records a page.

- Call `list_search_filters` first. Use only filters it lists as `available`; `indexed: false` filters can be slow.
- Put `exclusions` (a table column of domains, LinkedIn URLs or emails) on the first call. With a `searchId`, send only `cursor`, and leave `limit` unset while paging.
- To keep the results, create a table with `create_table` (`type: "search"`, the `searchId`, a `limit`). This is free. A table made from a search starts with Auto-run on, so call `set_table_autoplay` with `false` before you add any column.

## 2. Function: any job that will run again

A Function takes inputs, runs steps and returns named outputs, with no table. Use one for any job the user will do again, or that another play calls, even if it's a single step (an email waterfall, a company lookup, a score, a first line).

- **Reuse first:** the "Functions" section of `loopster-context.md`, then `list_functions` (it shows only Functions that are published and open to agents; read any other id from the context file with `get_function`).
- **Build one** with the `function-builder` skill, then run it with `run_function` on 1 to 1,000 inputs.
- **Steps a Function can take:** AI, Formula, the email waterfall, and lookups from Loopster Data, PredictLeads, AI Ark, Aviato, Wiza, FullEnrich, BetterContact, Surfe, Reverse Contact, Icypeas and Hunter email finders, and ClearoutPhone.
- **Steps it can't take:** CRM, sequencer and Slack actions; email checks (ZeroBounce, Findymail, Icypeas verify); LinkedIn data from the professional-network provider (live profiles, posts, post engagers, company headcount and open jobs); `score-prospect`. Those stay table columns or capabilities.
- **Cost:** every step runs for every input (the email waterfall stops at its first hit), and `run_function` takes no cap. Run 1, then 10, then 100 at a time (house rules, sections 4 and 5).
- **Results:** read each input's outputs with `get_function_run`. For more than about 25 inputs, put the Function in a table instead (section 4).

## 3. Capability: one action, once

`run_capability` runs one enrichment action on 1 to 1,000 inputs with no table. Check `list_capabilities` for the inputs, `connection` and `cost`.

- Good for: a quick lookup, a test before building anything, or a step no Function can take.
- If the user will want the same action again, build a Function instead.
- Results stay readable for a while only. Save them to a file when the run finishes.

## 4. Table: only when the work must live in Loopster

A table holds rows, and its columns enrich, score and push. Use one only when:
- the user wants to open, filter, share or keep the rows in Loopster;
- you need to keep a Function's results for more than about 25 inputs (a Function keeps no list to page through; a one-off capability run returns up to 1,000 items you read with `list_run_items`, so size alone doesn't need a table);
- the job pushes to a CRM, sequencer or Slack (those actions are columns);
- it runs by itself, through a schedule or an inbound webhook;
- a step can't go in a Function (section 2).

**Keep the table thin.** Put the reusable logic in a Function, and add one `run-function` column that calls it. Never copy a Function's steps into table columns.

The `run-function` column:

```json
{"templateId": "run-function", "header": "Work email",
 "taskConfig": {"runFunction": {
   "functionId": "<id>",
   "inputMappings": [
     {"inputId": "<input id>", "mode": "column", "sourceColumnId": "<column id>"},
     {"inputId": "<input id>", "mode": "static", "staticValue": "<fixed value>"}]}}}
```

- Input ids come from `get_function`. The cell holds a JSON object of the Function's outputs, each itself JSON text. To use one field in another column, use a Formula that parses twice, or a field reference whose `path` is `["<output key>", "<field>"]`.
- Quote it from its Function: `costEstimate.maxUsdPerRun` (from `get_function`) × the rows. Use this figure for the quote and the big-spend check. Control its spend with the 1, 10, then 100 steps: read the real cost (`get_wallet` `consumedUsd` before and after) after each batch, and stop and ask if a batch costs more than 1.5 times its quote.
- The Function must be published; it doesn't need to be open to agents.
- Give the column a plain header with no commas, and refer to columns by id in later calls.
- Keep `autoplay` off while building. A new table starts with Auto-run on, so create a blank or webhook table with `autoplay: false`, and call `set_table_autoplay` with `false` on a search table or a table the user already has.

## 5. Automation: runs without anyone watching

- **Inbound:** a webhook table with Auto-run on. Each posted row runs its columns, including its `run-function` column.
- **Recurring:** a schedule on a table's columns, including a `run-function` column. Name the `run-function` column and the Formula columns that read it in `columns`, and leave `rerunDependents` off, so a push, Slack or write-back column on the same table never fires from the schedule. Create it paused, check it, then resume. A schedule re-runs every cell by default, so send `cells: "empty"` to run only new rows, or price the full re-run for every firing.
- **Schedule or Auto-run?** When the user adds rows in batches ("we add new accounts every week"), offer a paused weekly schedule with `cells: "empty"`. Use Auto-run only when each row must run the moment it arrives, such as an inbound webhook. Either way, ask before creating or switching it on.
- **Notify when done:** an outbound webhook (`run.settled`) for runs you trigger.
- **Changing one later:** on a table with Auto-run on, a webhook, a schedule or paid answers, try the column change in its table sandbox first and publish after a yes (house rules, section 5b). Pause the schedule before you publish.

## Quick decision

| Question | If yes |
|---|---|
| Is it about finding new records? | Search |
| Will the user run this again, on any list, even as one step? | Function (reuse first, else build) |
| Is it one action, once, never repeated? | Capability |
| Must the rows live in Loopster, get pushed, or run on a schedule or webhook? Over about 25 Function results to keep? | Table, with the logic in a Function called by a `run-function` column |
| Does a step need something a Function can't take? | A table column or capability for that step only |

<!-- references/house-rules.md -->
# Loopster house rules

Every Loopster skill follows these rules. Read this file once per session, before the first action that writes, spends or sends.

## 1. Work in the open

- Before each step, tell the user in one sentence what it does and why. After it, tell them the result. Use plain words.
- Show results as a short table, counts and a one-line takeaway. Never paste raw JSON unless asked.
- Call things by the names the user sees in Loopster (table titles, column headers, Function titles), not by ids.
- When a job took more than a few Loopster tool calls, say how many in the final report (the `fewer-requests` skill keeps the count low).

## 2. Read before you buy

Before you search, enrich or build anything, check what the workspace already has:

| Check | Tool | Why |
|---|---|---|
| Tables with a matching name | `list_tables` with `search` | Don't rebuild a list that exists. |
| ICP and tier contexts | `list_contexts` | Use the user's own definitions instead of asking. Use a context in a prompt (`@{ctx:<id>}`) or in `score-prospect` only when its `hasContent` is true: an empty one gives the column nothing. |
| Connected accounts | `list_connections`, `list_provider_defaults` | Prefer accounts the user already pays for. |
| Reusable Functions | The "Functions" section of `loopster-context.md`, then `list_functions` | Run a Function that already does the job (section 7). |
| Wallet | `get_wallet` | Before paid work: know `spendableUsd`, and note `consumedUsd` as the baseline for the real-cost report (section 4, step 5). Skip it when the job is free (search, import, edits, a run priced at zero). |
| Deleted work | `list_trash` | Before you rebuild a table or Function that should exist, look in Trash. Restoring (`restore_from_trash` with the id `list_trash` gives) is free and runs nothing. |

**Test an account before you rely on it.** Before a play checks against, or pushes to, one of the user's own accounts (a sequencer, a CRM, an email checker), call `test_connection` once with its id from `list_connections`. Only a `connected` account can run.
- `ok: false` with `reason: "rejected"`: the key no longer works. Stop and ask the user to reconnect it in Loopster. Never read a failed lookup as "not found" or "not in a campaign".
- `reason: "unverifiable"`: the provider could not answer. Tell the user, and go on only if they agree.
- A refusal that names the providers that can be tested is not a failure: go on.
- Test each account once per play: each test is a call on that account, and a workspace gets 10 a day per provider. Loopster's own accounts (`managed: true`) can't be tested.

Only ask the user what the workspace cannot answer. For a one-off free lookup (one company, one person), skip these checks and just run it.

## 3. Cheapest first: the cost ladder

Climb one rung at a time. Each rung runs only on the records the rungs below did not answer.

| Rung | Route | Typical list price per row |
|---|---|---|
| 1 | **Loopster Data:** `search_people`, `search_companies` and the `loopster-data-*` lookups (`enrich-company`, `enrich-person`, `find-work-email`, `find-personal-email`, `find-phone-number`, `email-to-linkedin`) | free |
| 2 | **The user's own connected accounts** (`list_connections`) | nothing charged to the wallet, when the step runs on their account |
| 3 | **Data providers on Loopster's account,** cheapest first (each skill's routes table) | mostly $0.0015 to $0.05; a few premium ones up to about $0.75 |
| 4 | **AI columns without web search,** for judgement and writing (scoring, summaries, first lines), never for looking up a fact a data route has | listed from about $0.0002 to $0.02; the real cost is often a few times the pre-run estimate |
| 5 | **AI web research, last resort:** `ai-web` ("Loopgent"), `find-linkedin-url` ("Find LinkedIn profile URL") and every model template whose id ends in `-web` (labelled "(Web Search)") | listed from about $0.01 to $1.23, and the real cost can be several times the listed price |

To run on the user's account, name it: its id from `list_connections` as `integrationConnectionId`. With no account named, a step runs on the provider's saved default (`list_provider_defaults`), and when that default is Loopster's account it bills the wallet.

Rules for rung 5:
- **Never start there** for a job in the table in section 3b (LinkedIn URLs, current jobs, emails, phones, firmographics). Run rungs 1 to 4 first, then offer rung 5 only for what's left.
- **Check what a template does.** "Find LinkedIn profile URL" is an AI web agent. Before using a template you haven't used in this session, read its `type`, `label` and `cost` with `get_column_template`. If it's `type: "ai"` and named for a lookup, or its id is `ai-web` or ends in `-web`, it's rung 5.
- **Compare web models.** Web templates list from about $0.012 to $1.23 a row. The cheapest list at about $0.012 to $0.025 a row (`ai-openai-gpt-5-nano-web`, `ai-loopster-default-mini-web`, `ai-openai-gpt-6-luna-web`), while `ai-web` and `find-linkedin-url` list at about $0.18. A "mini" in the name doesn't mean cheap: `ai-openai-gpt-5.4-mini-web` also lists at about $0.18. Check each one's `cost` with `get_column_template`.
- **Measure first.** Run 3 rows on the cheapest web model that might work, and on the one the user asked for if different. Read the real cost with `get_usage`, compare the answers, then quote the rest from what you measured. Three rows are never a big spend: if the user asked for this job, their request covers the test, so run it (with `maxCostUsd`) instead of asking for it; otherwise ask first.
- More than 25 rows of rung 5 is always a big spend (section 4c).

**Inside a Function, every step runs for every input,** except that the email waterfall step stops at its first hit. To keep free-first inside a Function, give the paid step a run condition so it runs only when the free step found nothing (`function-builder` shows how). Or run a free Function first, and a paid one only on the misses.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## 3b. Common jobs: cheapest route first

| Job | Rung 1 (free) | Then, only for the misses |
|---|---|---|
| A person's LinkedIn URL | With an email: `loopster-data-email-to-linkedin`. With name + company: `search_people` with `personName` + `specificCompanies`, batching about 25 names and their companies per call (one call returns at most 50 records: if `nextCursor` comes back, page on with `searchId` and `cursor` until every match is read), then keeping a record only when both name and company match | `surfe-find-profile` ($0.0127), `icypeas-email-to-linkedin` ($0.0325) |
| Latest profile: current company, title, role start date (LinkedIn URL known) | `loopster-data-enrich-person` (profiles refresh about every 55 days) | Live profile, `enrich-professional-profile` ($0.0015; a table column with `execution_mode: "managed"`) |
| Has this person changed jobs? | The `champion-tracker` watchlist (free lookups and formulas) | Live profile for the people who matter |
| Work email | `loopster-data-find-work-email` (check it's on the current company's domain) | The "Find work email" Function: Icypeas ($0.0064), then Findymail ($0.0127) |
| Mobile number | `loopster-data-find-phone-number` | `ai-ark-find-mobile-phone` ($0.013), then pricier providers |
| Company firmographics | `loopster-data-enrich-company` | PredictLeads or AI Ark ($0.0003 to $0.0017) |
| A company's domain from its name | `search_companies` with `name` | none needed |
| Hiring, news or tech stack | none | PredictLeads ($0.0127 to $0.0233 per account) |
| A fact no data route holds ("does their pricing page mention usage pricing?") | none | Website text (`predict-leads-website-subpages`, $0.0017) plus an AI column without web search. It can come back empty for many companies, so test 10 rows first. Rung 5, on the cheapest web model that works, only for what that can't answer. |

For example, current profiles for 2,000 people cost nothing on rung 1, plus at most about $3 for live checks on the misses. An AI web agent on every row lists at $365 or more before its real cost is measured.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## 4. Price, ask, cap, run, report

Never start paid work without a price and a yes.

1. **Price it.**
   - A table run: `estimate_trigger_cost` with the same arguments you will send to `trigger_rows`: the exact `rowIds` and `columnIds`, plus `force: true` for a forced re-run (without it, cells that already hold an answer are left out of the price). Read `maxCostUsd` (a ceiling) and `perColumn`.
   - A capability: the `cost` in `list_capabilities` × the number of inputs.
   - A Function: `costEstimate.maxUsdPerRun` × the number of inputs. That is only a floor when the Function has usage-priced steps (`unpricedSteps`, such as AI steps): add their cost measured on 10 inputs, or 4 × their estimate until you have measured.
   - A `run-function` column (a table column that calls a Function): quote it from its Function, `costEstimate.maxUsdPerRun` (from `get_function`) × the rows, plus any usage-priced step measured on 10 rows. Use this figure for the quote and the big-spend check.
2. **Ask.** Show the number of records, the ceiling, and what it buys. End the message with the pricing sentence below. If it's a big spend, use the wording in section 4c.
3. **Cap.** Send `maxCostUsd` set to the agreed amount on `trigger_rows` and `run_capability`, plus an `idempotencyKey`. On `trigger_rows`, always name the `rowIds` and `columnIds` you priced: with no `rowIds` it runs every row, and with no `columnIds` every column that runs automatically. Then compare `triggeredCount` with the rows you sent (ids under `notInTable` did not start).
   - **Unpriced columns:** `trigger_rows` refuses a run that includes a column with no up-front price (for example `score-prospect`) unless you also send `allowUnpriced: true`. With that flag, those columns are **not** checked against the cap. `estimate_trigger_cost` lists them as unpriced.
   - **AI columns** are priced, but only with a pre-run estimate (`basis: "pre_run_estimate"`), and `maxCostUsd` checks only that estimate. The real cost can come in above it, so until you have measured 10 rows, quote 4 times the estimate.
   - **Functions and `run-function` columns:** `run_function` takes no `maxCostUsd`. Quote a `run-function` column from its Function (step 1). A table can call any published Function, open to agents or not.
   - For all of these, the protection is the one-ten-all ladder (section 5) plus reading the real cost after each step (`get_wallet` `consumedUsd` before and after). Say so when you ask.
   - **Choosing an AI model:** the default template is `ai`; a smaller one is `ai-openai-gpt-5.4-mini`. A smaller model costs less a line and writes plainer text, so for first lines run 10 rows on each and let the user pick. Read each model's `cost` with `get_column_template`.
   - Always run a few rows, read the real cost, then quote the rest.

     Real usage depends on your use case and settings, so always check the final cost estimate before you run.
4. **Run.** Poll until done (see section 9).
5. **Report.** When something paid ran, give the actual spend, not the estimate: `get_wallet` `consumedUsd` before and after the play, which includes Function spend (in a shared workspace, other people's runs can add to it).

Every message that gives a cost or a price ends with this exact sentence:

> Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## 4b. One plan, one yes

Don't ask for a yes at every small step.

1. At the start of a play, show the plan in a few lines:
   - the steps;
   - what will be created (tables, Functions);
   - the total budget.
2. One yes covers every step inside Loopster within that budget.
3. Still ask separately for:
   - a big spend (section 4c), even inside the budget;
   - anything that leaves Loopster (section 6);
   - publishing a Function or opening it to agents;
   - creating or resuming a schedule;
   - deleting rows or a column (`delete_rows`, `delete_column`): neither can be undone, and a column of paid results is money already spent. A deleted table goes to Trash for 30 days;
   - going over the budget.

## 4c. Big spend: always ask, in every mode

A **big spend** is a job whose realistic cost is any of these:
- over **$25**, or the "Ask above" amount in `loopster-context.md` if the user set one;
- over 10% of the wallet's `spendableUsd` (`get_wallet`);
- AI web research (rung 5) on more than 25 rows;
- a schedule or Auto-run table expected to cost over $25 a month, counting the Functions its `run-function` columns call.

Count the whole job, not each batch: splitting 2,000 rows into batches of 100 is still one big spend.

**Realistic cost** is what the user will actually pay, not the cheapest-looking number:
- data providers: list price × rows (providers that charge on result make this a ceiling);
- AI columns: the cost measured on 10 rows, or 4 × the pre-run estimate until you have measured;
- AI web research: the cost measured on 3 rows. Until you have measured, don't ask for the full run: run the 3-row test first (section 3, "Measure first"), then ask with the measured figure. If you can't run it, say the cost isn't measured yet, give 4 × the list price as a rough upper figure, and ask for the test;
- Functions and `run-function` columns: `maxUsdPerRun` × inputs, plus every usage-priced step measured on 10 inputs (4 × its estimate until measured). An AI web step inside a Function is rung 5.

Before a big spend, **stop and ask in the chat**, every time, in this shape:

> This will spend about **$X** from your Loopster wallet: N rows × about $Y a row, using <route>. <The cheaper route, if one exists: "Running <route> first would cost about $Z and answer about P% of rows.">  Proceed?
>
> Real usage depends on your use case and settings, so always check the final cost estimate before you run.

- **More than the wallet holds?** If the realistic cost is above `spendableUsd`, say so plainly in the question, and offer a smaller batch (for example the best-fit rows first).
- **Permission modes don't change this.** Bypass, auto-accept, "don't ask" and similar modes only skip tool-approval prompts. They are not permission to spend the user's money.
- **Only a clear yes to that question counts.** A plan yes (section 4b), an earlier yes, or "go ahead with whatever it takes" said before the question does not cover a big spend.
- **No one to ask?** In a run nobody is watching (`claude -p`, a scheduled agent, CI or another automation), don't start a big spend. Do the free and cheap rungs, then stop and report what's left, the route and the price.
- After the yes, send `maxCostUsd` at the agreed amount where the route takes one (`run_capability` and `trigger_rows`), and follow the one-ten-all ladder (section 5). For `run_function` and `run-function` columns, control the spend with the ladder and the wallet reads after each batch.

## 5. One, then ten, then all

- A paid or outward-facing step runs on **1 record** first. Show the result.
- Then **10**. Show the hit rate and the cost.
- Then the rest, in batches of up to 1,000, with progress updates. Function runs take no cap, so run them 100 at a time: compare each batch's real cost with the quote, and stop and ask if a batch costs more than 1.5 times its share.
- **A batch overshoots while it runs?** Stop it, then ask. For a run from `trigger_rows` or `run_function`, call `cancel_run` with its `runId`. For Auto-run work, turn Auto-run off (`set_table_autoplay` `false`) and call `stop_run` with the `tableId`. Neither is a refund: work already running finishes and is billed. Read `consumedUsd` again before you quote the total.
- Skip the ladder only when the user says so in this conversation, and never for anything that sends a message to a person.

## 5b. Change a live table in its sandbox first

A table sandbox is a copy of a table's columns and up to 50 of its rows. You change and run the copy; the table stays as it is until you publish. Opening one is free.

Use it before you add, change or remove a column on a table that already holds rows when Auto-run is on, rows arrive by webhook, a schedule runs it, it holds answers the user paid for, or it is the user's live inbound, CRM or campaign table. Skip it on a new table you are still building with Auto-run off.

1. `get_table_sandbox`. If one is already open, someone may be using it: ask before you touch it. `canOpen: false` means too few rows: change the table itself, one row first (section 5).
2. `open_table_sandbox` with 5 to 10 rows. Pick them with `rowIds` (`mode: "explicit"`) so they include the awkward cases: a blank input, a personal email, a record with no match.
3. Change and run the copy with the `sandboxTableId` it returns (`create_column`, `update_column`, `delete_column`, `trigger_rows`, `list_rows`). A sandbox run is a real run on its rows: price it and send `maxCostUsd` as usual. While the sandbox is open, the table's own columns can't be changed; rows still arrive.
4. Never run a column that sends outside Loopster (CRM, sequencer, Slack, webhook) in a sandbox: its rows are real people and records.
5. Show the user the results and `changes` from `get_table_sandbox` (the columns publishing would add, change or remove). Publish only after a yes.
6. `publish_table_sandbox` swaps in the sandbox's columns, copies the sandbox rows' results back and spends nothing. To fill the other rows, price and run `trigger_rows` with `columnIds` set to `affectedColumnIds` and `rowIds` that leave out `alreadyRunRowIds`, in batches. On an Auto-run table, new rows run the changed columns from now on, so price a month of rows first (section 4c). Pause a schedule before you publish.
7. Never leave a sandbox open: publish it, or drop it with `exit_table_sandbox`.

## 6. Ask before anything leaves Loopster

These each need their own explicit yes, with exactly what will be sent, where and how many:

- a CRM write (HubSpot, Salesforce, Attio)
- a sequencer push (HeyReach, Instantly, Smartlead, Mixmax)
- a Slack message
- a webhook to n8n, Make or Zapier
- a schedule (create it with `paused: true`, then resume only after a yes)
- publishing a Function or opening it to agents (`publish_function`, `set_function_agent_access`): this changes what other tables and agents run, and who may call it
- a public share link to a table (`create_share_link`): anyone with the URL can read every row without signing in. Offer `expiresInSeconds`, and `revoke_share_link` when it's no longer needed

A yes for one batch is not a yes for the next.

Also ask first, with its own yes even inside an agreed plan, before you change who pays or which account runs:
- switching off keep existing results (`set_table_keep_existing_results` `false`): every later edit would re-run and re-bill answered cells;
- choosing or clearing a provider's default account (`set_provider_default`, `clear_provider_default`): it changes which account every column with no named account uses;
- deleting a saved key (`remove_connection`): only the user can add it back, in the Loopster app.

Never send to real people while testing:
- use a paused campaign, a test channel and a test CRM record;
- use made-up names on a domain the user owns;
- remember that writing a CRM property can enrol a contact in a CRM workflow that emails them. Ask the user to check their CRM automations before the first write.

## 7. Choose the right Loopster surface: Functions first

**If a job will run again, it goes in a Function,** even a one-step job such as an email waterfall, a company lookup, a score or a first line. A Function is built once, any agent or table can reuse it, and a fix happens in one place.

1. **Reuse first.** Look in the "Functions" section of `loopster-context.md`, then `list_functions`. A Function under another title counts if it does the same job. Read its inputs, output keys and `costEstimate` with `get_function`, and map whatever ids it returns. If an input is marked `readsMetadata`, a `run_function` call sends values only, so the output behind it comes back empty and named in `skipped`: call that Function from a `run-function` column instead, and never report the empty output as "not found". If it costs much more per run than the pack's recipe for that job (more providers, extra checks), say so, and offer to build the cheaper recipe.
2. **Build one if none fits,** with the `function-builder` skill, then run it with `run_function`.
3. **Use a table only when you have to,** and even then keep the reusable logic in the Function, called by one `run-function` column. You have to when:
   - the user wants to open, filter, share or keep the rows in Loopster;
   - you need results for more than about 25 inputs: a table holds them in cells, while `run_function` needs one read per input;
   - it pushes to a CRM, sequencer or Slack (those are table columns);
   - it runs by itself, on a schedule or from an inbound webhook;
   - a step can't go in a Function: email checks, LinkedIn data from the professional-network provider (live profiles, posts, post engagers, company headcount and open jobs), `score-prospect`, and CRM, sequencer or Slack actions.
4. **One action, once, never to be repeated:** `run_capability`, with no table and no Function.

| The job | Use |
|---|---|
| New people or companies | `search_people` / `search_companies` |
| Anything that will run again, even one step | A Function (reuse, else build), run with `run_function` |
| The same, when rows must live in Loopster, get pushed, or run on a schedule or webhook | A table with one `run-function` column calling that Function, plus the push or automation columns |
| A step no Function can take | A table column, or `run_capability`, for that step only |
| One action, once | `run_capability` |

Never copy a Function's steps into table columns. Details, including the `run-function` column settings: `references/choosing-the-surface.md`, section 4.

## 8. Name things so people find them later

- Tables: `<Play> · <what> · <YYYY-MM-DD>`, for example `Prospect list · US fintech VPs Sales · 2026-10-25`. A list built from a signal is named for the signal, for example `Signals · new sales leaders · 2026-10-25`.
- Lasting reference tables keep a plain name with no date, for example `Do not contact · <company>` or `Champions · watchlist`.
- Functions: `<Job> · Loopster skill`, for example `Find work email · Loopster skill`. Put the skill name and version in the description.
- Before creating a Function, check `list_functions` for one with that title, and reuse it. Drafts don't appear in `list_functions`, so record every Function id you create in `loopster-context.md` (section "Functions"), and look there first.
- A table the user will open: when the play is done, add a saved view with `create_view` (free; it never runs anything). Name it for what it shows (for example `Ready to push`), filter to those rows, and hide helper columns with `columnVisibility`. Don't call `delete_view` without a yes: it can't be undone.

## 9. Read results the reliable way

- **Table runs:** poll `get_run` with the `runId` until `status` is not `running`, then read the cells with `list_rows`.
- **Rows added with Auto-run on:** read `enrichment` in the `insert_rows` answer. `started`: poll `get_run` with its `runId`. `none`: nothing was meant to run. `not_started`: the rows are in the table but nothing started, so call `trigger_rows` with the `rowsToTrigger` ids and never insert them again. `unknown`: check `get_status` before you trigger anything. For rows posted to a webhook, poll `get_status` for the table. Then read the rows.
- **Capability runs:** poll `get_run`, then `list_run_items`. It gives up to 100 items a page: follow `nextCursor` until none comes back, so a run of 1,000 inputs is read in full. Read each item's `output`, not only its `status`: an item can be `complete` with an output that says nothing was found. Save each batch to a file before you start the next batch of the same action: only that action's newest 1,000 results are kept, and older items read `gone`.
- **Function runs:** `get_function_run` takes both `functionId` and `runId`. For one input, use its `runId` and poll until `status` is not `running` (a run can take minutes). `complete` carries the outputs and a `skipped` list; `failed` names the step in `errors` or `failedSteps`. For a list, poll `get_run` with the batch `runId`, then call `get_function_run` with each item's `rowId` as the `runId`.
  - Inputs are keyed by input id: the id `add_function_input` returned, or the column-style id `create_function` with `fromTable` gave.
  - Outputs come back keyed by output name, as text (an output whose step is shaped as a number comes back as a number). A lookup's output is JSON text such as `{"found":false}`, so parse it; "not found" is not blank.
- **`run-function` cells** hold a JSON object of the Function's outputs, each itself JSON text. To use one field in another column, add a Formula that parses twice, or use a field reference whose `path` is `["<output key>", "<field>"]`. `list_columns` doesn't show the output keys; read them with `get_function`.
- **Schedules** re-run every cell by default (`force` is true), so each firing pays again for every row. Send `cells: "empty"` to run only new rows, or price the full re-run for every firing.
- **After editing a cell** (`update_cells`, `update_row`): the old value is gone, and a paid answer you overwrite must be paid for again. Don't write into a column of paid answers unless the user asks.
  - Auto-run off: nothing re-runs by itself. Re-trigger the columns that read the cell (name them in `columnIds`) with `force: true`, after you price it: without `force`, a cell that already holds an answer keeps it.
  - Auto-run on: the edit re-queues the columns that read the cell, which can spend. With keep existing results on (the default; `get_table` `settings.keepExistingResults`), only their empty, errored or skipped cells run again. Leave it on (section 6).
  - Read every write's answer: `rejected` lists cells that weren't written (a run was still working on them), so send those again when it ends.
- **After changing a column's prompt or Formula,** re-run with `force: true`. Without it, cells that already hold a value are skipped.
- **Spend from Functions,** including `run-function` columns: read it from `get_wallet` `consumedUsd` before and after the run (in a shared workspace, other people's runs can add to it).
- **Loading rows:** `insert_rows` stores only keys that match a column header or id. A row with no matching key is refused; a row with some is stored without the others, which come back in `ignoredKeys`. Before the first insert into a new blank table (it has one `Input` column), turn on `set_table_create_columns_from_keys`, insert, then turn it off again so a later typo doesn't add a column. Or add each column first (`templateId: "manual"`). Check that `ignoredKeys` is empty.
- **Writing plain values** (a note, a date, a status): add a column with `templateId: "manual"`, then write cells with `update_cells`.
- **Very large answers:** `list_search_filters`, `list_capabilities` and `list_column_templates` can each return a very large answer, so read only what you need.
  - When you know the template id, read it with `get_column_template` (both template tools need a `tableId`).
  - Otherwise filter `list_column_templates` with `provider` (for example `hubspot`), which keeps the answer small.
  - If your tool saves a large answer to a file, query only the entries you need from it.
- A cell can be `complete` and empty. Say "not found", not "failed".
- **Blank inputs:** a column whose mentioned input is blank skips that row. `optionalMentions` (on `update_column`) lets a blank value through. Its entries are the text inside the column's own `@{...}` mentions, and each call replaces the whole list, so send every mention that may be blank each time (read `appliedFixes`). A column waits for the columns it reads, so if an upstream column is skipped, this one doesn't run. Keep chains flowing by giving upstream columns inputs that are never blank, for example a Formula that falls back to a placeholder.

## 10. Keep the results

- For more than 20 rows, write a CSV in the user's working folder and give the path. When the user asked for the results in a Loopster table, the table is the result: name it and offer a CSV instead of exporting one unasked.
  - **A whole table, or what one view shows:** `export_table` (free; `format: "csv"` or `"jsonl"`, `viewId` for a view). Poll `get_export` until `status` is `complete`, then download `resultUrl`, following its redirect. The link lasts up to an hour; call `get_export` again for a fresh one. Poll one export rather than starting another (20 an hour).
  - **Part of a table, or when you can't download a file:** page `list_rows` (with `page` and `pageSize`, or with `cursor` when you filter or sort) in the default detailed format, because `concise` shortens long values. A large page can come back short and say so in `warnings`, so on a wide table use a `pageSize` of 100 or less, and check the total against `get_status`.
  - **A run's results:** `list_run_items`, following `nextCursor`.
- A Function keeps no list you can page through. Right after a `run_function` batch, read each input's outputs with `get_function_run` and write the CSV. For more than about 25 inputs, use a table with a `run-function` column instead (section 7).
- If you built a table, keep it so the user can open it in Loopster, unless they ask you to delete it.

## 10b. Load a big file

For a file of more than about 10,000 rows (up to 50 MB), don't send the rows through `insert_rows`.

1. `create_upload_link` with the `tableId` and `format` (`csv`, or `ndjson`). `PUT` the file to `uploadUrl` within two hours and keep the `fileId`.
2. `import_file` with the `fileId`. Send a `mapping` (each file key to a column, or `action: "skip"`), or `createColumnsFromKeys: false`, so stray headers don't add columns. `hasHeaderRow: false` if the first line is data.
3. Poll `get_job` until `status` is `complete` or `failed`, and tell the user how many rows went in: auto-dedupe and the table's row limit can keep some out.

An import is free and starts no enrichment, even with Auto-run on; price and run the columns afterwards (section 4), at most 10,000 `rowIds` per `trigger_rows`. A `fileId` imports once. If you can't `PUT` a file (a chat-only agent), use `insert_rows` in batches of 10,000 rows or fewer, or ask the user to import the file in the Loopster app.

## 11. When something goes wrong

- **400:** read the message, fix the request, and never resend it unchanged.
- **402:** `insufficient_balance`, `workspace_limit` or `daily_cogs_limit`. Stop and tell the user. Nothing was charged on that call. A run bigger than `spendableUsd` instead runs the rows the wallet covers, in order, and refuses the rest, so check which inputs ran. `daily_cogs_limit` is a daily safety limit: topping up doesn't lift it, and it resets at midnight UTC.
- **409:** a state problem. Read the `code`, for example `sandbox_required`, `no_outputs` or an idempotency code.
- **422 `cost_cap_exceeded`:** the cap was below the estimate. Ask before raising it.
- **429:** wait the `Retry-After` seconds, then send it again. On a search, `search_concurrency` means 4 searches are already running (the most a workspace may run): wait about 2 seconds, and never start more than 4 at once.
- **503 `nothing_started`:** nothing ran or was charged. Send the same call again with the same `idempotencyKey`. A 500 `nothing_started_internal` also started nothing, but trying again now will likely fail the same way: tell the user and try later. A 503 on a search: try again shortly with the same filters.
- **413 `too_many_rows`** on `insert_rows`: one call takes at most 25,000 rows. Send batches of 10,000 or fewer.
- Never retry a paid call without the same `idempotencyKey`. `create_schedule` and `create_webhook` take none: after a timeout, check `list_schedules` or `list_webhooks` before you create it again.

## 12. Point to help

When the user may want to read more, link the matching Help Center article. Start from the "API and MCP" collection: https://help.loopster.ai/en/collections/19788062-api-and-mcp.

**Tell Loopster when the product gets in the way.** Offer `send_feedback` when a refusal looks wrong, the docs and a tool's answer don't match, a capability is missing, or the user is unhappy.
- Show the user the exact message and send it only after a yes.
- Say what you tried, what came back and what you expected. Add `type`, the `tableId` if any, and short facts in `context` (the tool, the status code).
- Never include secrets or personal data: no keys, webhook addresses, emails, names, LinkedIn URLs or row values. Collect several points into one message.
- It reaches the Loopster team with the workspace id, opens no ticket, and nothing answers it in this chat. Say so.

<!-- references/tools-map.md -->
# Loopster MCP tools map

The Loopster MCP server is `https://app.loopster.ai/api/mcp`. Each tool matches a REST call on `https://app.loopster.ai/api/v1`. Only the tools the skills use are listed. "Spends" means it can take money from the wallet.

## Workspace and money

| Tool | Does | Spends |
|---|---|---|
| `get_wallet` | Balance; `spendableUsd` decides whether a run starts | No |
| `get_usage` | Spend by table, column or day (`groupBy`, `tableId`, `from` / `to`; the default window is the last 30 days) | No |
| `list_contexts` | ICP, tier and company contexts (ids for `@{ctx:<id>}`) | No |
| `list_connections` | The workspace's own accounts, accounts shared into it from the organization, and Loopster's managed accounts (`managed: true`, no id). Only status `connected` can run | No |
| `test_connection` | Ask the provider whether a connection's key still works (`ok`, or `rejected` / `unverifiable`). The user's own connections only; 10 a day per provider (house rules, section 2) | No |
| `list_provider_defaults` / `set_provider_default` | Which account a provider runs on. `set_provider_default` needs `provider` and one of `account: "loopster"` or `connectionId`. It changes which account later columns use, so ask first (house rules, section 6) | No |
| `clear_provider_default`, `remove_connection` | Remove a provider's default account; delete a saved key. Both change what later runs use, so ask first (house rules, section 6) | No |
| `send_feedback` | Tell the Loopster team about a refusal that looks wrong, a missing capability, a docs mismatch or an unhappy user. Ask the user first; no secrets or personal data (house rules, section 12) | No |

## Search Loopster Data (free)

| Tool | Does |
|---|---|
| `list_search_filters` | Filter ids, kinds, accepted values and `indexed` / `available` flags. Call before searching. |
| `search_people` / `search_companies` | Up to 50 records a page. Returns `searchId` and `nextCursor`. `exclusions` leaves out records already held (a table column of LinkedIn URLs, emails or domains). `perCompanyLimit` caps people per company on each page; across pages, apply the cap yourself. |

To page a search, send `searchId` and `cursor` only, and leave `limit` unset. Put `exclusions` on the first call with the filters, because they cannot be sent with a `searchId`.

`exclusions` hold up to 3 lists:
- `matches: "identity"` leaves out the records themselves (people by LinkedIn URL or email, companies by domain);
- `matches: "company"` (people searches only) leaves out everyone at the listed companies.

## Tables, columns and rows

| Tool | Does | Spends |
|---|---|---|
| `create_table` | Blank, webhook, search (from a `searchId`, free) and import starters | Only paid starters |
| `list_tables`, `get_table`, `rename_table` | Find, read, rename | No |
| `delete_table` | Move to Trash (needs an admin key); restorable for 30 days. Queued work keeps running and billing, so call `stop_run` first | No |
| `list_trash`, `restore_from_trash` | What Trash holds (tables, workbooks, Functions) with each `purgesAt`; restore one by its id. Restoring runs and bills nothing | No |
| `set_table_autoplay` | Auto-run on insert, on or off. A new table starts with it on; a blank or webhook table can be created with `autoplay: false` | Turning it on makes later inserts spend |
| `set_table_keep_existing_results` | Whether an edit leaves answered cells alone. On by default (`get_table` `settings.keepExistingResults`). Off means every later edit on an Auto-run table re-runs and re-bills answered cells, so ask before switching it off (house rules, section 6) | Off: edits spend |
| `set_table_auto_dedupe` | Needs `columnId`, and `enabled: true` to switch on. On insert (and webhook posts), `keep: "oldest"` (the default) skips a new row that matches, and `keep: "newest"` deletes the earlier rows. Editing that cell into a duplicate can delete the edited row. Blank values never match | No |
| `set_table_create_columns_from_keys` | Let inserts (and webhook posts) create a column per new key. Turn it off again once the columns exist | No |
| `create_upload_link`, `import_file`, `get_job` | Load a CSV or JSON-lines file (up to 50 MB): get the link, `PUT` the file within two hours, `import_file` with the `fileId`, poll `get_job`. Free, and starts no enrichment even with Auto-run on. Use it above about 10,000 rows (house rules, section 10b) | No |
| `export_table`, `get_export` | A whole table, or what one view shows, as `csv` or `jsonl`. Poll `get_export`, then download `resultUrl`, following its redirect. 20 exports an hour | No |
| `create_view`, `list_views`, `update_view`, `delete_view` | Saved views: filters, sort and visible columns. Free; they never run anything. `delete_view` can't be undone | No |
| `list_column_templates`, `get_column_template` | Every column type, its inputs, its cost and its settings schema. Both need a `tableId` (any table works) | No |
| `list_columns` | A table's columns with ids, types and settings | No |
| `create_column`, `update_column`, `delete_column` | Build columns, including AI, export and `run-function` columns (a column that calls a Function). `update_column` also takes `optionalMentions`, `dependencies` and `runCondition` (a Formula that decides whether the column runs for a row). `delete_column` can't be undone | No (running spends) |
| `create_columns` | Up to 20 columns in one call, all or nothing; a column can read an earlier one from the same call by name. Not in a table sandbox | No (running spends) |
| `insert_rows`, `list_rows`, `get_row`, `update_cells`, `update_row`, `delete_rows` | Row data. `insert_rows` keeps only keys that match a column (others come back in `ignoredKeys`), takes up to 25,000 rows a call, and answers with `enrichment` and a `runId` when a run started. `list_rows` pages with `page`, up to 500 rows a page (a large page can come back short: read `warnings`); it uses `cursor` only with a filter, sort, `viewId` or `updatedSince`. `delete_rows` can't be undone | With Auto-run on, inserts and cell edits spend |
| `get_table_webhook` | Whether the table has an inbound address, shown as its last four characters only | No |
| `rotate_table_webhook` | Issues a new inbound address and returns the full URL once. Any older address stops working | No |

## Table sandbox

A copy of a table's columns and up to 50 of its rows, to try column changes on before they reach every row (house rules, section 5b).

| Tool | Does | Spends |
|---|---|---|
| `get_table_sandbox` | Whether one is open, its `sandboxTableId`, and `changes` (the columns publishing would add, change or remove). `canOpen: false` means too few rows | No |
| `open_table_sandbox`, `add_table_sandbox_rows` | Copy the columns and 1 to 50 rows in (`mode` `top`, `random`, or `explicit` with `rowIds`) | No |
| `create_column`, `update_column`, `delete_column`, `trigger_rows`, `get_status`, `list_rows`, `get_row` | Called with the `sandboxTableId`, they work on the copy. A sandbox run bills like any run, on its rows only | Running spends |
| `publish_table_sandbox` | Swap in the sandbox's columns and copy its rows' results back. Returns `affectedColumnIds` and `alreadyRunRowIds` for filling the other rows | No |
| `reset_table_sandbox`, `exit_table_sandbox` | Start over with a fresh copy, or close it; both throw away what wasn't published | No |

While a sandbox is open, the table's own columns can't be changed. Rows still arrive.

## Running and reading

| Tool | Does | Spends |
|---|---|---|
| `estimate_trigger_cost` | Dry run of `trigger_rows`, with the same arguments (send `force: true` to price a forced re-run). For a `run-function` column, quote it from `get_function`: `costEstimate.maxUsdPerRun` × the rows | No |
| `trigger_rows` | Run columns on rows. Takes `maxCostUsd` and `idempotencyKey`. Always send `rowIds` and `columnIds`: with no `rowIds` it runs every row, with no `columnIds` every column that runs automatically. At most 10,000 rows a call | Yes |
| `get_run`, `list_run_items`, `list_runs` | Progress and per-item results | No |
| `get_status` | Whole-table progress, including Auto-run work | No |
| `get_waterfall_trace` | Why a waterfall or AI cell holds what it holds | No |
| `cancel_run` | Cancel one run by its `runId` (from `trigger_rows` or `run_function`): removes its work still queued | No |
| `stop_run` | Takes a `tableId`: cancels everything queued and in progress on that table, including Auto-run work. Call it before `delete_table` | No |

Neither is a refund: work already running finishes and is billed, and the answer says how many cells were stopped and how many were already running.

## Capabilities (one action, no table)

| Tool | Does | Spends |
|---|---|---|
| `list_capabilities` | 89 actions, each with inputs, `connection` and `cost` | No |
| `run_capability` | Run one action on 1 to 1,000 inputs, for example `{"templateId": "loopster-data-enrich-company", "inputs": [{"domain": "stripe.com"}], "maxCostUsd": 0, "idempotencyKey": "<key>"}` | Yes, unless free or on your own account |

## Functions (reusable, no table)

| Tool | Does | Spends |
|---|---|---|
| `list_functions` | Functions that are published and open to agents. Drafts don't appear here | No |
| `get_function` | Any Function by id, draft included, with ids for inputs and steps | No |
| `create_function` | Empty draft, or `fromTable` from working columns | No |
| `open_function_sandbox` | Open the editable copy | No |
| `add_function_input`, `update_function_input`, `remove_function_input` | Inputs | No |
| `add_function_step`, `update_function_step`, `delete_function_step` | Steps (AI, Formula, waterfall and provider actions) | No |
| `set_function_outputs` | What the Function returns | No |
| `publish_function` | Dry run first, then live | No |
| `set_function_agent_access` | Let agents list and run it | No |
| `run_function`, `get_function_run` | Run on 1 to 1,000 inputs, keyed by input id; read each input's outputs. No `maxCostUsd` | Yes |
| `delete_function`, `restore_from_trash` | Trash and restore | No |

Steps that can be added to a Function over the API: AI, Formula, the email waterfall, and provider actions from Loopster Data, PredictLeads, AI Ark, Aviato, Wiza, FullEnrich, BetterContact, Reverse Contact, Surfe, Icypeas and Hunter (email finders) and ClearoutPhone. Not Function steps: CRM, sequencer and Slack actions, email checks, LinkedIn data from the professional-network provider (live profiles, posts, post engagers, company headcount and open jobs), and `score-prospect`. Those stay table columns or capabilities.

## Automation

| Tool | Does | Spends |
|---|---|---|
| `create_schedule`, `update_schedule`, `list_schedules`, `delete_schedule` | Run columns on a schedule, including a `run-function` column. `create_schedule` needs a `time`; it re-runs every cell unless you send `cells: "empty"`. Create with `paused: true` | Every firing spends |
| `create_webhook`, `test_webhook`, `list_webhooks`, `list_webhook_deliveries`, `delete_webhook` | Get a signed `run.settled` message when a run finishes | No |

## Sharing

| Tool | Does |
|---|---|
| `create_share_link`, `list_share_links`, `revoke_share_link` | A read-only public link to a table |

<!-- references/data-routes.md -->
# Data routes: which source for which field

Cheapest first. These are list prices on Loopster's managed account, read 2026-10-25; read the live `cost` in `list_capabilities` or `list_column_templates` before quoting.

- **Runs as:** "capability" runs with no table (`run_capability`). "Column template" is a table column template. For a source marked "capability" that you want as a table column, read the template with the same id using `get_column_template` (any table id) to confirm it exists and to see its settings.
- **Function step?** says whether a Function can take it (`add_function_step`). Any job that will run again goes in a Function (house rules, section 7), so check this column before you choose how to run a source.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Companies (key: domain)

| Field | Source | Runs as | Function step? | List price |
|---|---|---|---|---|
| Name, industry, employees, revenue range, HQ, founded, LinkedIn URL (output keys include `found`, `industry`, `employee_count` and `employee_range`; read one row to see the rest) | `loopster-data-enrich-company` | capability | yes | free |
| Extended firmographics, NAICS, funding stage | `predict-leads-enrich-company-extended` | column template | yes | $0.0017 |
| Company profile, parent and subsidiaries | `predict-leads-enrich-company` | column template | yes | $0.0017 |
| Firmographics (second source) | `ai-ark-enrich-company` | capability | yes | $0.0003 |
| Website text (pricing, about, careers) for an AI summary | `predict-leads-website-subpages` | column template | yes | $0.0017 |
| Products and services | `predict-leads-products` | column template | yes | $0.0017 |
| Similar companies | `predict-leads-find-lookalikes` / `ai-ark-find-lookalike-companies` | column template / capability | yes / yes | $0.0017 / $0.013 |
| Open jobs (with title filters and recency) | `predict-leads-find-jobs` | column template | yes | $0.0127 |
| Recent news (funding, launches, hires, expansion) | `predict-leads-find-news` | column template | yes | $0.0127 |
| Tech stack | `predict-leads-find-tech-stack` | column template | yes | $0.0233 |
| Funding rounds and investors | `predict-leads-find-financing` | column template | yes | $0.0871 |
| Web traffic | `aviato-company-web-traffic` | capability | yes | $0.1083 |
| Total funding, financials | `aviato-company-financials` | capability | yes | $0.5121 |
| People count at a company | `ai-ark-count-people` | capability | yes | $0.0026 |
| Headcount by title or location | `professional-company-headcount` | capability* | no | $0.0015 |
| Open jobs (second source) | `professional-company-open-jobs` | capability* | no | $0.0015 |
| Domain from company name | `search_companies` with `name` | search | no | free |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## People (key: LinkedIn URL)

| Field | Source | Runs as | Function step? | List price |
|---|---|---|---|---|
| Title, seniority, company, company website, location, role start date | `loopster-data-enrich-person` | capability | yes | free |
| LinkedIn URL from an email | `loopster-data-email-to-linkedin` | capability | yes | free |
| LinkedIn URL from name + company | `search_people` with `personName` + `specificCompanies` | search | no | free |
| LinkedIn URL (paid, for misses) | `surfe-find-profile` (name + company) | capability | yes | $0.0127 |
| LinkedIn URL (paid, for misses) | `icypeas-email-to-linkedin` (email) | capability | no | $0.0325 |
| Live profile, positions, about, skills | `enrich-professional-profile` | capability* | no | $0.0015 |
| Recent posts (for personalization) | `professional-person-posts` | capability* | no | $0.006 |
| Person enrichment (second source) | `ai-ark-enrich-person` | capability | yes | $0.0013 |
| Personality profile | `ai-ark-personality-profile` | capability | yes | $0.05 |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

\* Runs on the professional-network provider ("professionalNetwork"). **Not a Function step.** For a repeat job, use a managed table column for these (`execution_mode: "managed"`, runs on Loopster's account, no default needed) and a Function for the rest. As a capability it needs the user's own key, or Loopster's account saved as that provider's default (`set_provider_default` with `account: "loopster"`; ask first). Some outputs are large, so in a table use the column template rather than the capability when there are more than about 10 rows.

## AI web research (last resort)

`ai-web` ("Loopgent"), `find-linkedin-url` ("Find LinkedIn profile URL") and the model templates whose id ends in `-web` search the web for every row. They list from about $0.01 to $1.23 a row, and the real cost can be several times that. Use them only for rows and fields no route above answers, after measuring 3 rows and asking (house rules, sections 3 and 4c).

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Contacts (emails and phones)

Use the `contact-finder` skill.

## Notes

- Capabilities that need `connection: required` (for example `theirstack-find-tech-stack` and `hunter-find-email`) run only on the user's own key.
- **These can be Function steps:** Loopster Data lookups, PredictLeads, AI Ark, Aviato, Wiza, FullEnrich, BetterContact, Reverse Contact, Surfe, Icypeas and Hunter email finders, AI steps and Formula steps. That's how to bundle "website text + AI summary" or "jobs + news + AI why-now" into one reusable call.
- **These can't:** the `professional-*` routes and `enrich-professional-profile`, `search_people` and `search_companies`. Keep them as table columns or searches.
- **A bundle Function costs the sum of all its steps on every input,** and AI steps bill by use on top. `costEstimate.maxUsdPerRun` is a floor when the Function has an AI step. Keep expensive steps (for example `aviato-company-financials`, about $0.51 a row) out of a bundle that runs on every row. Put them in a second Function that you run only on the rows that need them, or use `run_capability` for a one-off.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

<!-- references/icp-to-filters.md -->
# ICP to Loopster Data filters

Filter ids, kinds and values come from `list_search_filters`. Always call it first, because the vocabulary is live. Envelopes:

- textList: `{"kind": "textList", "include": ["…"], "exclude": ["…"], "mode": "contains" | "exact"}`
- multiSelect: `{"kind": "multiSelect", "include": ["…"], "exclude": ["…"]}`; values must come from the filter's options
- numberRange: `{"kind": "numberRange", "min": n, "max": n}`
- boolean: `{"kind": "boolean", "value": true}`

## People filters

| ICP words | Filter | Notes |
|---|---|---|
| "VP Sales", "Head of RevOps" | `jobTitle` (textList, `mode: "contains"`) | The most precise persona filter. List 3 to 8 title variants. |
| "leaders", "decision-makers" | `seniority` (C Suite, VP, Head, Director, Manager, …) | Can match a past role: re-check the current title in the results |
| "sales team", "marketing" | `jobTitle` (textList, `mode: "contains"`) | Use title words such as "Sales" or "Marketing", with `seniority`. Send only filters `list_search_filters` lists |
| "in the US", "based in London" | `country`, `personState`, `personCity` | Where the person is |
| "US companies" | `companyCountry`, `companyState`, `companyCity` | Where the company is |
| "fintech", "SaaS" | `companyIndustry` (589 options) | Use several neighbouring industries. Use `companyIndustryGroup` only if `list_search_filters` lists it. |
| "50–200 people" | `companySizeBand` (1-10 … 10001+) | |
| "10 to 50 million in revenue" | `companyRevenueBand` | Values like "$10M - $20M"; read the options |
| "funded", "Series B+" | `companyFundingRounds`, `companyTotalFunding` (numberRange) | A static fact, not a recent event. For recent rounds use `signal-outbound`. |
| "founded after 2018" | `companyFoundedYear` (numberRange) | |
| "new in role" | `monthsInRole` (numberRange, e.g. 0–4) | Powers the new-leader play |
| "used to work at …" | `pastCompany` (textList) | Powers the customer-alumni play |
| "at these accounts" | `specificCompanies` (textList) | Company names or domains |
| "has an email or phone" | `hasEmail`, `hasPhone` (boolean) | Raises contact hit rates later |
| "named person" | `personName` | Pair with `specificCompanies` |

## Company filters

`industry`, `employeeCount`, `sizeBand`, `country`, `state`, `city`, `postalCode`, `revenueBand`, `companyType`, `keywords` (textList over the description), `name`, `hasLiveDomain`, `foundedYear`, `totalFunding`, `fundingRounds`. Use `industryGroup` only if `list_search_filters` lists it.

## Worked example

"VPs and Heads of Sales at 50–500 person US software companies, not our customers, max 2 per company":

```json
{
  "filters": {
    "jobTitle": {"kind": "textList", "include": ["VP Sales", "Vice President of Sales", "Head of Sales", "VP Revenue", "Chief Revenue Officer"],
                 "exclude": ["AVP", "EVP", "Area", "Associate", "Fractional", "Regional", "Development", "Engineering", "Operations", "Enablement"], "mode": "contains"},
    "seniority": {"kind": "multiSelect", "include": ["C Suite", "VP", "Head"]},
    "companySizeBand": {"kind": "multiSelect", "include": ["51-200", "201-500"]},
    "companyCountry": {"kind": "textList", "include": ["US"]},
    "country": {"kind": "textList", "include": ["United States"]},
    "companyIndustry": {"kind": "multiSelect", "include": ["Software Development", "Information Technology"]}
  },
  "exclusions": [{"kind": "list", "projectId": "<do-not-contact table id>", "columnId": "<domain column id>", "matches": "company"}],
  "perCompanyLimit": 2,
  "limit": 25
}
```

Check `companyIndustry` and `companyCountry` values against the live options first: the option list is what the index enforces.

## Unpacking the person record (saved search tables)

A table created from a search holds a JSON `Person record` column; read its column id with `list_columns`. Add one Formula per field you need. The keys are snake_case:

```json
{"templateId": "formula", "header": "Company domain",
 "taskConfig": {"formula": {"expression": "(() => { try { return JSON.parse(@{<Person record id>}).company_domain || '' } catch (e) { return '' } })()"}}}
```

Keys include `company_domain` and `role_started_at`. To see every key, read one row's `Person record` with `get_row` before adding more Formulas. Formulas run only when named: trigger them with `columnIds` and `maxCostUsd: 0`.

## Reading results

- Each record has `fields`:
  - person: `linkedinUrl`, `firstName`, `lastName`, `title`, `seniority`, `function`, `location`
  - company: `companyName`, `companyDomain`, `companySizeBand`, `companyIndustry`
  - `roleStartedAt`
- Results come in the index's own order, not by relevance, so the first page is not a sample. Page through before judging quality.
- `approximateTotal` is the market size for the filters.

<!-- references/routes.md -->
# Contact routes and prices

Prices are Loopster's per-input list prices when the action runs on Loopster's managed account, read from `list_capabilities` on 2026-10-25. Always read the live `cost` before quoting, because prices change. On the user's own connected account (their key), nothing is charged to the Loopster wallet. "On result" means the provider charges only when it finds something.

The **Function step?** column says whether a Function can take that route as a step. A route marked No runs as a capability (`run_capability`) or a table column. Every step in a Function runs for every input, so a mobile or personal-email Function holds one paid provider step; only the email waterfall step stops at its first hit.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Work email

| Order | templateId | Needs | List price | Function step? |
|---|---|---|---|---|
| 1 | `loopster-data-find-work-email` | `linkedin_url` | free | Yes |
| 2 | `icypeas-find-email` | `firstname`, `lastname`, `domainOrCompany` | $0.0064 | Yes |
| 3 | `findymail-find-name` | `name`, `domain` | $0.0127 | Only as a provider inside the email waterfall step |
| 3 | `findymail-find-business-profile` | `linkedin_url` | $0.0127 | No |
| alt | `reverse-contact-find-work-email` | `linkedin_url` or `full_name` + `company_domain` | $0.0195 | Yes |
| alt | `better-contact-find-work-email` | LinkedIn URL or name + company | $0.034 | Yes |
| alt | `surfe-find-work-email` | LinkedIn URL or name + company | $0.034 | Yes |
| alt | `contactout-find-work-email` | `linkedin_url` | $0.039 | No |
| alt | `full-enrich-find-work-email` | LinkedIn URL or name + company | $0.0476 | Yes |
| alt | `wiza-find-work-email` | profile URL or name + company | $0.052 | Yes |
| own key | `hunter-find-email`, `prospeo-email-finder` | name + domain or company | wallet $0 | `hunter-find-email` Yes; `prospeo-email-finder` No |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Mobile phone

| Order | templateId | Needs | List price | Function step? |
|---|---|---|---|---|
| 1 | `loopster-data-find-phone-number` | `linkedin_url` | free | Yes |
| 2 | `ai-ark-find-mobile-phone` | LinkedIn URL, or domain + full name | $0.013 | Yes |
| 3 | `findymail-find-mobile-phone` | `linkedin_url` | $0.0871 | No |
| alt | `wiza-find-mobile-phone` | profile URL or name + company | $0.13 | Yes |
| alt | `contactout-find-mobile-phone` | `linkedin_url` | $0.2783 | No |
| alt | `surfe-find-mobile-phone`, `better-contact-find-mobile-phone` | LinkedIn URL or name + company | $0.3208 | Yes |
| alt | `full-enrich-find-mobile-phone` | LinkedIn URL or name + company | $0.7467 | Yes |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Personal email

| Order | templateId | Needs | List price | Function step? |
|---|---|---|---|---|
| 1 | `loopster-data-find-personal-email` | `linkedin_url` | free | Yes |
| 2 | `full-enrich-find-personal-email` | LinkedIn URL or name + company | $0.0468 | Yes |
| 3 | `surfe-find-personal-email` | LinkedIn URL or name + company | $0.0676 | Yes |
| alt | `aviato-find-personal-email` | `linkedin_url` | $0.0871 | Yes |
| alt | `contactout-find-personal-email` | `linkedin_url` | $0.1296 | No |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Getting a LinkedIn URL first (unlocks the free route)

| templateId | Needs | List price | Function step? |
|---|---|---|---|
| `loopster-data-email-to-linkedin` | `email` | free | Yes |
| `icypeas-email-to-linkedin` | `email` | $0.0325 | No |
| `surfe-find-profile` | name + company | $0.0127 | Yes |

`icypeas-email-to-linkedin` is not a Function step (Icypeas goes in a Function only as its email finder), so keep it a capability (`run_capability`). `surfe-find-profile` can be a Function step.

Or search Loopster Data with `search_people`, using `personName` + `specificCompanies` (free).

Don't use an AI web research column (`find-linkedin-url` "Find LinkedIn profile URL", `ai-web` or any `-web` model) for this until the routes above have run. It lists at about $0.18 a row or more, and is for the few rows they can't answer.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Email checks

As table columns, `zero-bounce-validate-email` and `icypeas-verify-email` run on Loopster's account when their settings include `execution_mode: "managed"`. As capabilities (and `findymail-verify-email` in any form), they run on the user's own key, or on Loopster's account only after it is saved as the provider's default (`list_provider_defaults` shows which). Otherwise `run_capability` answers 400. Ask the user before saving a default.

`zero-bounce-validate-email`, `icypeas-verify-email` and `findymail-verify-email` cannot be Function steps. `clearout-phone-validate-phone` can.

| templateId | Needs | List price | Function step? |
|---|---|---|---|
| `zero-bounce-validate-email` | `email` | $0.0065 | No |
| `findymail-verify-email` | `email` | $0.0043 | No |
| `icypeas-verify-email` | `email` | $0.0043 | No |
| `reoon-verify-email` | `email` | own key | No |
| `clearout-phone-validate-phone` (phone: carrier and line type) | `phone` | $0.0065 | Yes |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## When a paid action is refused for "no account"

Actions marked `connection: optional` run on the user's own key, or on Loopster's account if the workspace saved Loopster as that provider's default. With neither, `run_capability` answers 400 and nothing runs. Ask the user before saving a default (`set_provider_default` with `account: "loopster"`), because it applies to every column created afterwards for that provider.

<!-- references/signal-recipes.md -->
# Signal recipes

`<domain>` is the account's domain: an input id in a Function, or a column id in a table, as `@{…}`. Every PredictLeads step takes `"execution_mode": "managed"` unless the user has their own PredictLeads key.

The `taskConfig` is the same on both surfaces:
- **In a table column:** `domain` is `@{<column id>}`. Use this route for a first build; running it with `trigger_rows` takes `maxCostUsd`.
- **In a Function step** (`add_function_step`): `domain` is `@{<input id>}`. The jobs and news steps are the first two steps of "Why now · Loopster skill" (`why-now.function.md`).
- For tech stack and financing, build the column first. Once it works and the user will run it again, turn it into a Function with `create_function` and `fromTable`, record its id in the "Functions" section of `loopster-context.md`, and run it from then on with `run_function` or one `run-function` column.

## Hiring for roles you serve

Template `predict-leads-find-jobs`. The full `taskConfig`:

```json
{"predictLeadsFindJobs": {"execution_mode": "managed", "domain": "@{<domain>}",
 "title_keywords": ["sales development", "SDR", "BDR", "account executive", "revenue operations"],
 "posted_within_days": 90, "active_only": true, "max_results": 10}}
```

- Build `title_keywords` from the personas the user sells to. Hiring for the team your buyer runs is the signal.
- Read the output as JSON: `count`, plus `items[]` (title, location, posted date, URL). `count: 0` means no matching openings.
- Add `description_keywords` for a tool or skill named in postings (for example a competitor's product name).

## Funding and company news

Template `predict-leads-find-news`. The full `taskConfig`:

```json
{"predictLeadsFindNews": {"execution_mode": "managed", "domain": "@{<domain>}", "max_results": 25}}
```

- Each item has `category`, `summary`, `found_at`, `effective_date`, `amount` and `article.url`.
- Categories include: `receives_financing`, `invests_into`, `launches`, `hires`, `expands_offices_in`, `integrates_with`, `signs_new_client`, `attends_event`, `recognized_as`, `has_revenue`, `identified_as_competitor_of`.
- Keep items whose `effective_date` (or `found_at`) is within the window.

For round details (amount, investors), use template `predict-leads-find-financing`. It costs more than the news step (see the cost guide), so run it only on accounts whose signal is funding.

- Every step in a Function runs for every input, so keep financing out of the Why now Function: it would run on every account.
- First build: add the financing column to the Signals table (or a small table of the flagged domains) and run it on the flagged rows only (`trigger_rows` with those `rowIds`).
- To reuse it, turn that column into a `Funding round · Loopster skill` Function with `create_function` and `fromTable`, and record its id in the "Functions" section as soon as it returns. After a Why now run, pass only the flagged domains to `run_function`. If more than about 25 domains are flagged, call that Function from one `run-function` column in a table instead of `run_function`. Price it as the number of flagged domains × the financing price, and ask with the pricing sentence (over the big-spend limit in house rules 4c needs its own yes). Then run 1, then 10, then 100 at a time. Read `get_wallet` `consumedUsd` after each batch, and stop and ask if a batch costs more than 1.5 times its share of the quote.

## Tech stack (switch or integrate)

Template `predict-leads-find-tech-stack`, key `predictLeadsFindTechStack`. The output lists technologies with detection strength, plus the competing tools found.

- **Switch play:** a competitor's tool is detected. The angle is the one-line difference in `loopster-context.md`.
- **Integrate play:** a tool you integrate with is detected. The angle is "works with the <tool> you already use".

## New leaders (free)

```json
{"filters": {
  "monthsInRole": {"kind": "numberRange", "min": 0, "max": 4},
  "seniority": {"kind": "multiSelect", "include": ["C Suite", "VP", "Head"]},
  "jobTitle": {"kind": "textList", "include": ["VP Sales", "Head of Sales", "Chief Revenue Officer", "VP Revenue Operations"],
               "exclude": ["AVP", "EVP", "Area", "Associate", "Fractional", "Regional", "Development", "Engineering", "Enablement"], "mode": "contains"},
  "companySizeBand": {"kind": "multiSelect", "include": ["51-200", "201-500"]},
  "country": {"kind": "textList", "include": ["United States"]},
  "companyCountry": {"kind": "textList", "include": ["US"]}
}}
```

Signal date: `roleStartedAt`. Re-check the current `title`. `country` is where the person is, `companyCountry` where the company is; send both, or a US company's team abroad slips in.

## Customer alumni (free; see also `champion-tracker`)

`pastCompany` set to your customers' names, plus the persona and ICP filters. These are people who used your product at their last company.

## Cost guide (list prices, managed accounts, 2026-10-25)

| Engine | Per account |
|---|---|
| Jobs only | $0.0127 |
| News only | $0.0127 |
| Tech stack only | $0.0233 |
| Financing | $0.0871 |
| Why-now Function (jobs + news + AI summary) | about $0.03 to $0.05 (AI priced by use) |

`trigger_rows` and `run_capability` take `maxCostUsd`; `run_function` takes none. Price a `run-function` column from its Function (`get_function` `costEstimate.maxUsdPerRun` × the accounts, plus any usage-priced step measured on 10 rows). Read the real cost on 10 domains (`get_wallet` `consumedUsd` before and after) before you quote a big run.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## account-question

Answer one yes/no question about every company in a list (for example which sell into healthcare, which have a free plan, which are building an AI team) in one step: free data first, AI web research only for unclear rows after measuring 3 and a yes. Use when someone asks which of these companies do or have something. For a full research brief, use company-brief.

# Account question

One step: one question, an answer per company. For a full brief, use `company-brief`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **The question** as one line with a yes/no/unknown answer. Agree on it before running.
2. **Free data first:** `loopster-data-enrich-company` (industry, description) answers many questions for free. Mark yes or no where the data is clear.
3. **Cheaper text next:** website text (`predict-leads-website-subpages`, see `references/data-routes.md`) plus an AI column without web search, for the unclear rows, priced and asked.
4. **AI web research last**, on the rows still unclear: run 3 rows with `maxCostUsd` (the request covers that test), read the real cost, then ask for the rest with the measured figure.
5. **Answer** yes, no or unknown per company, each with its source (the data field or a URL).
6. **Report** counts per answer and the cost.

## Does not claim

- More than the sources show: "unknown" is an answer.

## account-tiers

Sort a list of accounts into tiers 1 to 4 against the user's ideal customer profile in one step, from free data first, with visible weights and a reason per tier. Use when someone asks to tier, rank or prioritise these accounts against their ICP. For scoring inbound leads, use lead-score; to find new accounts, use prospect-list.

# Account tiers

One step: tiers for accounts the user already has. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **The ICP** from the user or `loopster-context.md`: the 3 to 5 things that matter (industry, size, location, a tool or signal).
2. **Free data first:** `loopster-data-enrich-company` on every domain (free) for industry, size and location. Paid fields (tech stack, hiring) only if the ICP needs them: price per account and ask (`references/data-routes.md`).
3. **Weights.** Show a small table (criterion · weight · how it's met) before tiering, for example industry match 40, size in range 30, location 20, extra signal 10.
4. **Tier** with a Formula column or one `update_cells`: 1 = 80+, 2 = 60–79, 3 = 40–59, 4 = below 40, plus a one-line reason per account.
5. **Report** counts per tier and the top accounts. Unknown fields lower the score and are named, never guessed.

No AI web research per row without a price and a yes.

## Does not claim

- That a tier predicts a deal: it is the ICP fit on the data found.

## buyer-check

Mark each person in a Loopster table as buyer, influencer or not a buyer for what the user sells, in one step: rules from title and seniority first (free), an AI column only for unclear rows after a price and a yes. Use when someone asks who in this list would buy, who the buyers or influencers are, or to filter out people who wouldn't buy. To find buyers at companies, use decision-makers.

# Buyer check

One step: a label per person already in a table. To find people at companies, use `decision-makers`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **What is sold** and to whom (ask if unclear). Write the buyer titles, the influencer titles, and titles that are never buyers.
2. **Rules first (free):** label from title and seniority with a Formula column or one `update_cells`: **buyer**, **influencer**, **not a buyer**, or **unclear**. Add a persona label (for example "Sales leader") and a confidence (high on an exact title match, medium on seniority alone).
3. **Unclear rows only:** an AI column without web search on title + company. Price it on those rows (measure 10 rows, or 4 × the estimate until measured), ask with the pricing sentence, then run with `maxCostUsd`.
4. **Report** counts per label and a few examples of each.

## Does not claim

- Budget authority: a title is the best signal in the data, not an org chart.

## champion-tracker

Turn your happiest customers' people into pipeline. Finds customer alumni, people who used your product at a past company and now hold a buying role at an ICP company (free search). Also keeps a champion watchlist that checks every month, at no cost, whether past champions, power users or lost-deal contacts have changed jobs. Flags moves into ICP companies, finds who replaced a champion who left a customer, alerts the owner, and drafts a personal note. Builds the job-change check once as a reusable Function. Use when the user says "track job changes", "champion tracking", "where did our champions go", "have these people moved", "people who used us before", "customer alumni", "warm intros", or "who left our customers".

# Champion tracker

## What you get

- **Customer alumni:** a list of people who worked at your customers, now at ICP companies in a buying role. They already know what you do.
- **Champion watchlist:** a Loopster table that re-checks every champion's current employer, plus a monthly schedule (paused until you say yes). Each move is flagged as **joined an ICP company** (outreach) or **left a customer** (a risk: find the replacement).
- **A reusable Function:** `Job change check · Loopster skill`, built from the watchlist's check columns once they work. Any later list, and the scheduled table, calls it instead of rebuilding the columns.
- **For each move:** a short personal draft and an alert to the owner (Slack or CRM), always after a yes.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (ICP, customers list, voice, destinations).

Then check what already exists (house rules, section 2):
- the "Functions" section of `loopster-context.md`, then `list_functions`, for `Job change check · Loopster skill` and `Champion note · Loopster skill`. If the check is there, use it in Play 2, step 2, and don't build the check columns. If the note is there, use it in Play 2, step 7;
- if an id is only in `loopster-context.md`, read it with `get_function`. If it is still a draft, publish it (with a yes, as in "Turn the check into a Function") before you add the `run-function` column. The column doesn't need the Function open to agents;
- `list_tables` with `search` for an existing `Champions · watchlist`.

You need your customer list (company names and domains) and, for the watchlist, your champions:
- name;
- LinkedIn URL (best);
- the company they were at when they championed you.

Champions can come from a CSV, the CRM (closed-won contacts, power users, closed-lost contacts) or an existing Loopster table.

Show the plan in a few lines before you start (house rules, section 4b): the table, the Function you will build after the first run, the monthly schedule (created paused, with its own yes) and the budget. The job-change check itself is free.

## Which surface

| The job | Use |
|---|---|
| Customer alumni, and who replaced a champion | `search_people`, saved as a search table. A search is never a Function step. |
| "Have these people moved?" once, for about 25 people or fewer, no table wanted | `run_function` with `Job change check · Loopster skill` if it exists. If not, `run_capability` with `loopster-data-enrich-person` (free, `maxCostUsd: 0`; confirm in `list_capabilities`) and compare the company in the chat. Build the Function only when the user will repeat the check (Play 2). |
| The watchlist: names, owners, `Alerted on`, the schedule, the Slack alert | A table, with the check as one `run-function` column |
| A live profile check, a Slack alert | Table columns, for those steps only. They can't go in a Function. |
| ICP fit of the movers | `run_function` with a scoring Function if one exists; otherwise an AI column, then turn it into a Function (Play 2, step 4) |
| Turning old work emails into LinkedIn URLs, once | `run_capability` |

## Play 1: Customer alumni (free)

1. Take customer company names from `loopster-context.md` or the user. Batch 10 to 25 names per search.
2. `search_people` with:
   - `pastCompany` set to the customer names, with `mode: "exact"` so "Notion" doesn't also match "Notion Capital";
   - the persona filters (`jobTitle`, `seniority`);
   - the ICP company filters (`companySizeBand`, `companyIndustry`, `companyCountry`), and `country` as well when the people must live in the same region (the `prospect-list` skill explains why);
   - exclusions for the do-not-contact table, by domain with `matches: "company"` (this also leaves out anyone still at a customer, if customers are on it).
3. Re-check each record's current `title`. Filters can match past roles.
4. Show the count and 10 samples, then save as `Customer alumni · <date>` (search table, free) and turn Auto-run off.
5. The angle: they've seen it work. For example: "You used <product> at <old company>. Now that you're at <new company>, would it help to …". Don't claim an outcome they didn't have.

## Play 2: Champion watchlist (free checks, monthly)

1. **Create the table:** blank, `autoplay: false`, titled `Champions · watchlist`. A table is right here: the user wants the rows, owners and alert history in Loopster, and the check runs on a schedule. Columns:
   - `Name`
   - `LinkedIn URL`
   - `Company when champion` (domain)
   - `Owner` (optional)
   - `Source` (closed-won, power user, lost deal)

   Turn on `set_table_create_columns_from_keys`, then insert the champions with those keys, so each key becomes a column (with it off, keys that match no column are dropped). Check `ignoredKeys` is empty. Normalize domains and LinkedIn URLs first.
2. **Add the check.**
   - **The Function exists:** add one `run-function` column that calls `Job change check · Loopster skill`, mapped to `LinkedIn URL` and `Company when champion`. Then add a `Current company domain` column and a `Moved` column that each read its answer. Settings are in `references/watchlist-columns.md`, section "Use the Function in a table".
   - **No Function yet (first build):** add the three free check columns (exact settings in `references/watchlist-columns.md`):
     - `Current profile`: the `loopster-data-enrich-person` template, reading `LinkedIn URL`.
     - `Current company domain`: a Formula that pulls `company_website` out of the profile with a field reference.
     - `Moved`: a Formula that compares it with `Company when champion`, giving `yes`, `no` or `unknown`.

     Once step 3 shows they work, turn them into the Function (section "Turn the check into a Function"), then set up the schedule on the Function's column.
3. **Run once:**
   - **Check columns:** `trigger_rows` on all rows with `columnIds` naming the three columns and `maxCostUsd: 0`.
   - **`run-function` column:** price it from the Function (`get_function` `costEstimate.maxUsdPerRun` × the rows). Use this figure for the quote and the big-spend check. Run 1 row, then 10, then the rest 100 at a time, and read `get_wallet` `consumedUsd` before and after each batch.
4. **Read the movers.** For `Moved = yes`, check the new company against the ICP:
   - free with `loopster-data-enrich-company` on the new domain (read it from the `Current company domain` column);
   - for a scored ICP fit, run it on the movers only. Every step in a Function runs for every champion, so never put an ICP step inside the monthly check.
     - If the "Functions" section of `loopster-context.md` or `list_functions` lists a Function that scores ICP fit, call it with `run_function` on the movers only (up to about 25 inputs; for more, add one `run-function` column that calls that Function to the table and trigger it on the mover `rowIds`). Read its input ids with `get_function` and fill each from the mover's row, because the inputs are usually a title, company, industry and size. Price it first (`costEstimate.maxUsdPerRun` × movers, plus its AI step measured on 10, or 4 × the estimate until measured) and ask. Then run 1, then 10, then the rest 100 at a time, and stop and ask if a batch costs more than 1.5 times its share of the quote.
     - Otherwise score the movers with an AI column. It reads the mover's company profile (the free `loopster-data-enrich-company` result for `Current company domain`) and the ICP context, and returns `{"tier": "A|B|C", "reason": "…"}`. Price it with `estimate_trigger_cost` (an AI column often costs a few times its pre-run estimate, so measure 10 rows before quoting) and ask. Then trigger it on the mover `rowIds` only, with `maxCostUsd` and an `idempotencyKey`. Once the tiers read well, turn the column into a Function with `function-builder`, titled `ICP tier · Loopster skill` (or `ICP tier · movers · Loopster skill` if a Function with the first title already exists), and record its id in `loopster-context.md` straight away. From then on, call it from one `run-function` column.
     - Use `score-prospect` only if the user asks for it. It is a table column that can't go in a Function, and it is priced by use (the template lists $0.0036 as an estimate; measure 10 rows before quoting). Trigger it on the mover `rowIds` with `allowUnpriced: true` and `maxCostUsd`, after a yes, and know the cap does not cover it.

   Real usage depends on your use case and settings, so always check the final cost estimate before you run.
5. **Split the movers:**
   - **Joined an ICP company:** outreach. They go to `contact-finder` (new work email; it reuses the Find work email Function for anyone the free pass misses) and then `outbound-launch`.
   - **Left a customer:** a risk. Find who now holds their role there: `search_people` with `specificCompanies` set to the customer and the persona titles. Tell the user, and alert the account owner only after a yes (step 8).
6. **Freshness:** Loopster Data profiles show `days_since_refresh`. Profiles refresh about every 55 days, so a move can take weeks to appear. For a mover the user cares about, confirm with `enrich-professional-profile`. It's a live lookup at about $0.0015. It can't go in a Function. As a table column, set `execution_mode: "managed"` and trigger it on the mover `rowIds` only. As a capability, it needs the user's own key for the professional-network provider, or Loopster's account saved as that provider's default; ask before setting it.
7. **Write an opener field** for each mover: a `Champion note` column (AI, or written by you) with one sentence about the move. `outbound-launch` reads it as the signal for the first line.
   - If `Champion note · Loopster skill` is in the "Functions" section of `loopster-context.md` or `list_functions`, add one `run-function` column that calls it instead of an AI column.
   - Trigger it on the mover `rowIds` only. Price it first (`estimate_trigger_cost` for a plain AI column; for a `run-function` column, the Function's `maxUsdPerRun` × movers plus its AI step measured on 10) and ask. Run 1 first, then 10. Show the notes and the real cost (`get_wallet` `consumedUsd` before and after), and run the rest only after a yes, 100 `rowIds` at a time. Stop and ask if a batch costs more than 1.5 times its share of the quote.
   - Once the notes read well, turn the column into a Function the same way as the check (next section), named `Champion note · Loopster skill`, with the voice rules from `loopster-context.md` in its prompt. Record its id in `loopster-context.md`, and use one `run-function` column for it from then on.
8. **Alert once:** add a manual `Alerted on` column. After each run:
   - alert only rows where `Moved = yes` and `Alerted on` is blank;
   - then, only for rows whose alert was actually sent after the user's yes, write today's date into `Alerted on` with `update_cells` and copy the new domain (from the `Current company domain` column) into `Company when champion`, so next month compares against where they are now. Leave both untouched for any row you did not alert.

## Turn the check into a Function

The monthly check is the job you will run again on every list, so it belongs in a Function (house rules, section 7). Do this once the check columns have worked on the real watchlist.

1. **Build, record, publish and test it** by following `references/watchlist-columns.md`, section "Build the Function", steps 1 to 6: build it from the table (`create_function` with `fromTable`), write the id in the "Functions" section of `loopster-context.md` straight away, dry-run the publish and ask before the live publish and again before `set_function_agent_access`, then test on 3 checked champions plus one whose profile isn't found.
2. **Swap the table over:** one `run-function` column in place of the three check columns, plus a `Current company domain` column and a `Moved` column that each read the Function's answer (read one cell with `list_rows` first, then use a Formula that parses it, or for a JSON output a field reference whose `path` is `["<output key>", "<field>"]`; `get_function` shows the output keys). While the old columns still exist, give the new ones a different header (for example `Moved (Function)`), and rename them to `Moved` and `Current company domain` with `update_column` once the old ones are deleted. Ask before you delete the old columns, and keep them until the Function has matched the table on every champion you tested.

After that:
- **A list with no table:** `run_function` with the Function, for about 25 people or fewer. For more people, or when the user wants to keep the rows, use a table with one `run-function` column.
- **Any new or scheduled watchlist:** one `run-function` column. Never copy the Function's steps into table columns.

## Keep it running

- Offer a monthly schedule on the check, and ask before you create it (a plan yes does not cover it):
  - `create_schedule` with `cadence: "monthly"`, a `dayOfMonth` (1 to 28), a `time` (required, HH:MM), the user's `timezone` and `cells: "all"` (every champion is re-checked each month, which is what you want here). This is the "price the full re-run" option in house rules, section 9: the check is free, which you prove before you resume. For any paid column, send `cells: "empty"`.
  - the columns to name: the `run-function` column, plus the Formula columns that read its answer (for example `Current company domain` and `Moved`). Schedule only these. If `create_schedule` refuses a Formula column, schedule only the `run-function` column and, after each firing, run the Formula columns with `trigger_rows` (`columnIds` naming them, `force: true`, `maxCostUsd: 0`) before you read `Moved`. If the user says no to building the Function, name the three check columns instead and say that each fix will then have to be made in the table;
  - leave `rerunDependents` off, so the Slack alert column never fires from the schedule;
  - `paused: true`.
- **Prove it is free before you resume.** Don't assume it:
  - `get_function` shows `costEstimate.maxUsdPerRun` 0 and no `unpricedSteps`;
  - `get_wallet` `consumedUsd` is the same before and after a 10-row run (in a shared workspace, other people's runs can add to it, so run it when no one else is running).

  Only then tell the user each firing costs nothing. If any step costs money, price champions × the measured cost per row for each firing, ask, and resume only after a yes.

  Real usage depends on your use case and settings, so always check the final cost estimate before you run.
- **Resume** the schedule only after a yes.
- **Alerts:** add a `slack-send-message` column. A Slack post is a table column and can't go in a Function. Trigger it yourself after each monthly run, naming only the `rowIds` with `Moved = yes` and a blank `Alerted on`. Its text names the person, old and new company, and owner; the channel comes from `loopster-context.md`. Test it on one row in a test channel first. Post for real only with a yes for that month's batch, saying how many people and which channel. A yes for one run is not a yes for the next. Each Slack post is outward-facing.

## Draft the note (rules)

- Short: one sentence for the `Champion note` field. Use 2 to 3 sentences only if the owner will send it as a personal message.
- Personal: congratulate the move and mention your shared history in one clause.
- Ask nothing big. No meeting request in the first note, just an opening.
- Never imply you're monitoring them. "Saw you moved to Acme" is fine; "our system detected" is not.
- Use the voice rules in `loopster-context.md`.

## Show the result

```
Champions · watchlist   (180 champions checked, nothing charged)
  Moved: 14   → joined ICP company 6 · joined non-ICP 5 · unknown 3
  Left a customer: 4 accounts at risk (replacements found for 3)
  Customer alumni found: 92 in buying roles at ICP companies
Function: Job change check · Loopster skill (id saved in loopster-context.md)
Next: contact-finder for 6 movers + 92 alumni → outbound-launch
Schedule: monthly re-check created PAUSED — say "resume" to switch it on
```

Then add the pricing sentence if any paid step ran.

## If something goes wrong

- **Many `unknown`:** the LinkedIn URLs are missing or not in Loopster Data. Get URLs first: run `loopster-data-email-to-linkedin` (free) on their old work emails with `run_capability` (`maxCostUsd: 0`), then write the URLs into `LinkedIn URL` with `update_cells` and re-trigger the check for those rows: `trigger_rows` with their `rowIds`, `columnIds` naming the check columns (the `run-function` column and the Formula columns that read it, or the three first-build columns), `force: true` and `maxCostUsd: 0`. Without `force`, cells that already hold `{"found":false}` keep that answer.
- **False "moved":** the stored company domain differs from the website (for example a parent brand or regional domain). Normalize both, or compare company names as a fallback.
- **The Function's answers differ from the table's:** don't swap yet. Compare one champion at a time (`get_function_run` against the table cells), fix the Function in a new sandbox with `function-builder`, republish after a yes, and test again.
- **Building the Formula columns:** use the field reference once, in `Current company domain` only, and compare plain columns in `Moved` (see `references/watchlist-columns.md`, step 3).

<!-- champion-tracker/references/watchlist-columns.md -->
# Watchlist columns

A champion whose stored company differs from their current one reads `Moved = yes`, and one who hasn't moved reads `no`. Nothing is charged: the lookup and both formulas are free.

**Reuse first.** If `Job change check · Loopster skill` is in the "Functions" section of `loopster-context.md` or in `list_functions`, skip the columns below and go to "Use the Function in a table" or "Use the Function without a table". An id found only in `loopster-context.md` may be a draft: read it with `get_function`, and publish it (with a yes) before you call it from a table. Open it to agents (also with a yes) only before you call it with `run_function`. The columns below are the first build. Once they work on the real watchlist, turn them into that Function ("Build the Function") and call it from one `run-function` column on every later table and on any scheduled table.

Assumed columns from the insert (it creates them when `set_table_create_columns_from_keys` is on): `LinkedIn URL` (id `<liCol>`) and `Company when champion` (id `<oldCol>`). Read the real ids from `list_columns` or from the insert's `columnsCreated`.

## 1. Current profile (free)

`create_column`:

```json
{"templateId": "loopster-data-enrich-person", "header": "Current profile",
 "taskConfig": {"loopsterDataEnrichPerson": {"linkedin_url": "@{<liCol>}"}}}
```

The value holds `company_name`, `company_website`, `title`, `current_role_start_date` and `days_since_refresh`, or `found: false`.

## 2. Current company domain (free)

Build a field reference to `company_website` in the profile column:

1. Take the JSON `{"columnId":"<profileCol>","source":"value","path":["company_website"]}`, exactly, with no spaces.
2. Base64url-encode it and drop the `=` padding. That's `<data>`.

```json
{"templateId": "formula", "header": "Current company domain",
 "taskConfig": {"formula": {"expression": "String(@{ref:v1:<data>} || '').toLowerCase().replace(/^https?:\\/\\//,'').replace(/^www\\./,'').split('/')[0]"}}}
```

## 3. Moved (free)

```json
{"templateId": "formula", "header": "Moved",
 "taskConfig": {"formula": {"expression": "(String(@{<domainCol>}).trim() === '') ? 'unknown' : (String(@{<domainCol>}).trim() === String(@{<oldCol>}).trim().toLowerCase() ? 'no' : 'yes')"}}}
```

Use the field reference from step 2 once, in the `Current company domain` column only. In `Moved`, compare the extracted column.

## Run

Formulas run only when named. Use `trigger_rows` with `columnIds: ["Current profile", "Current company domain", "Moved"]` and `maxCostUsd: 0`.

## Optional alert column

`slack-send-message`:

```json
{"templateId": "slack-send-message", "header": "Alert owner",
 "taskConfig": {"slackSendChannelMessage": {"channel_id": "<channel id>",
   "text": "Champion move: @{<nameCol>} left @{<oldCol>} and is now at @{<domainCol>}. Owner: @{<ownerCol>}"}}}
```

Only trigger it on rows where `Moved = yes`. Pass those `rowIds` explicitly, and get a yes before the first real post. A Slack post is a table column and can't go in a Function.

## Build the Function (once the columns above work)

1. **Check the outputs on a profile that isn't found.** Run the three table columns on one champion whose LinkedIn URL isn't in Loopster Data (add a row for it if the table has none). `Current profile` always gets a value (`{"found":false}`). If `Current company domain` or `Moved` comes back blank or skipped, give those two Formula columns `optionalMentions` with `update_column`, re-run, and check again. Return an output only when it comes back with a value (`unknown` for `Moved`). Otherwise return `Current profile` alone, and keep the two Formula columns in the table, reading its answer.
2. Call `create_function`:
   - `title`: `Job change check · Loopster skill`
   - `description`: `Built by the Loopster champion-tracker skill v0.1.0. Looks up a person's current company from their LinkedIn URL (Loopster Data) and says whether they moved from the company you give: yes, no or unknown. Every step is a free lookup or Formula. Safe to edit in Loopster.`
   - `fromTable`:
     - `tableId`: the `Champions · watchlist` table;
     - `columnIds`: the ids of `Current profile`, `Current company domain` and `Moved` (read them with `list_columns`);
     - `outputColumnIds`: the ids of the outputs that passed step 1 (all three when they did).
3. The columns they read become the inputs: `LinkedIn URL` and `Company when champion`, both required. Read the input ids and output keys from `draft` in the answer and from `get_function`, because they are not the table's column ids. Output keys come from the step names (for example `Moved` becomes `moved`).
4. Write the `functionId` into the "Functions" section of `loopster-context.md` straight away.
5. **Publish with a yes.** Dry-run the publish (`publish_function` with `dryRun: true`), show the contract (inputs, output keys, cost per run) and ask. Then publish, and ask again before `set_function_agent_access`. Once it's published, a table's `run-function` column can run it and spend, even if it isn't open to agents; opening it only lets `run_function` reach it.
6. **Test it** with `run_function` on 3 champions the table has already checked, plus one champion whose profile isn't found (see "Use the Function without a table"). Its steps are free, so there is no price to quote, but read `get_wallet` `consumedUsd` before and after to confirm. Each `moved` (when the Function returns it) must match the table's `Moved`, the unfound champion reads `unknown`, and no output may come back blank. If any differ, fix the Function in a new sandbox with `function-builder`, dry-run, ask, republish, and test again.

Keep the ICP check, the live profile check and the Slack alert out of this Function. Every step in a Function runs for every input, and the live profile check and the Slack alert can't be Function steps.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Use the Function without a table

For about 25 people or fewer, when the user doesn't need the rows kept in Loopster.

```
run_function { functionId, idempotencyKey,
  inputs: [{ "<LinkedIn URL input id>": "https://www.linkedin.com/in/…",
             "<Company when champion input id>": "acme.com" }, …] }
```

1. Key each input by the input id, not by its name.
2. For one input, poll `get_function_run` with its `runId`. For a list, poll `get_run` with the batch `runId` until it is no longer `running`, then call `get_function_run` with `functionId` and each item's `rowId` as the `runId`. That is one call per person.
3. Outputs come back as text keyed by output name. Parse them: a profile that isn't found reads `{"found":false}`, which is a result, not a blank.
4. Show a short table (name, old company, current company, moved). For more than 20 people, write a CSV in the user's folder (house rules, section 10).
5. For more than about 25 people, or when the user wants to keep the rows, use a table (next section).

Run 1 person, then 10, then the rest 100 at a time, and read `get_wallet` `consumedUsd` before and after each batch (house rules, section 5).

## Use the Function in a table

Add one column, mapped to the watchlist's columns. Never copy the Function's steps into columns.

```json
{"templateId": "run-function", "header": "Job change check",
 "taskConfig": {"runFunction": {"functionId": "<id>",
   "inputMappings": [
     {"inputId": "<LinkedIn URL input id>", "mode": "column", "sourceColumnId": "<liCol>"},
     {"inputId": "<Company when champion input id>", "mode": "column", "sourceColumnId": "<oldCol>"}]}}}
```

- The cell holds a JSON object of the Function's outputs, each itself JSON text. Read one cell on 1 row first, then add a `Current company domain` column and a `Moved` column that each read the Function's answer (the `current_company_domain` and `moved` outputs): a field reference whose `path` starts with the output key, or a Formula that parses the cell. If the Function returns only `current_profile` ("Build the Function", step 1), build both columns as in sections 2 and 3 above, with the field reference pointing at the `run-function` column and a `path` of `["current_profile", "company_website"]`. Check on 3 rows that `Moved` reads `yes`, `no` or `unknown`. `Current company domain` is the column the next steps read to find the new company and to update `Company when champion`.
- If the old check columns are still in the table, give the new columns different headers (for example `Moved (Function)` and `Current company domain (Function)`) until the user agrees to delete the old ones. Ask before `delete_column`, then rename the new columns to `Moved` and `Current company domain` with `update_column`.
- Price it from the Function: `get_function` should show `costEstimate.maxUsdPerRun` 0 for these free steps. Run 1 row, then 10, and read `get_wallet` `consumedUsd` before and after.
- Keep `autoplay` off while building.
- Schedule the `run-function` column plus the Formula columns that read it, created paused, with `cells: "all"` and `rerunDependents` off. `cells: "all"` is the "price the full re-run" option in house rules, section 9; it is safe here only because the check is free. Prove that before you resume (see `SKILL.md`, "Keep it running").

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## company-brief

Write a short, sourced research brief on a few companies in one step, with one AI web research run capped and priced first. Use when someone asks for a brief, a summary, research or background on these companies before a call or outreach. For data fields across a list, use enrich-list or enrich-accounts.

# Company brief

One step: a short brief per company from web research. For data fields on a list, use `enrich-accounts` or `enrich-list`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Free facts first:** `loopster-data-enrich-company` for every domain (free). The brief builds on these and doesn't pay to research what is already known.
2. **Cheaper text before the web agent:** website text (`predict-leads-website-subpages`, see `references/data-routes.md`) plus an AI column without web search often answers "what they do, who they sell to". Offer it first.
3. **AI web research** (`ai-web` as a column or capability) when the user wants news or depth. Prompt with fixed keys: `what_they_do`, `who_they_sell_to`, `products`, `size_and_location`, `recent_news` (with dates), `sources` (URLs). Say "unknown" rather than guess.
4. **Cap and measure.** Up to 3 companies: the request covers the run, so run it with `maxCostUsd` and an `idempotencyKey`. More: run 3, read the real cost (`get_usage`), then ask for the rest with the measured figure.
5. **Show** each brief with its sources, and the real cost.

## Does not claim

- That every fact is right: the sources are listed so a person can check.
- Private data (a private company's revenue, internal plans).

## contact-finder

Find work emails, mobile numbers and personal emails for people you already have (a CSV, a Loopster table, a search result or a pasted list), free Loopster Data first, then paid providers only for the misses, with an email check and a spending limit agreed up front. Reuses the "Find work email" Function (builds it on first use), and builds "Find mobile phone" or "Find personal email" Functions when the lookup will run again. Use when the user says "find emails for", "get phone numbers", "get contact details", "I need verified emails", "find their mobile", "enrich this list with contacts", "find work emails for this list", or when another play needs contacts before outreach.

# Contact finder

## What you get

Each person gets their best work email (and mobile or personal email if asked), where it came from, and whether it was checked. You get a hit rate, the real cost, and a CSV, or one new column on the user's table that calls the Function.

## Before you start

Read `references/house-rules.md`. Then:

1. **Find the Functions first.** Look for **Find work email · Loopster skill**, **Find mobile phone · Loopster skill** and **Find personal email · Loopster skill** in the "Functions" section of `loopster-context.md`, then in `list_functions` (it shows only Functions that are published and open to agents; read any other id from the context file with `get_function`). Reuse what exists. Tell the user which ones exist and what a run costs.
2. **What you have per person.** A LinkedIn URL is the best key, because the free route needs it. Otherwise you need first name, last name and company domain.
3. **What they need:** work email (default), mobile, personal email, or more than one.
4. **How many people,** and a spending cap. Suggest one from the price table in `references/routes.md`. `run_function` takes no `maxCostUsd`, so you hold the agreed amount yourself, with the batches in Step 2.
5. **Do-not-contact:** if `loopster-context.md` names a do-not-contact table, drop anyone whose company domain or LinkedIn URL is on it before spending.

## The route (free first)

Each step runs only on the people the step before did not answer.

| Step | Work email | Mobile | Personal email |
|---|---|---|---|
| 1. Free | `loopster-data-find-work-email` (LinkedIn URL) | `loopster-data-find-phone-number` | `loopster-data-find-personal-email` |
| 2. Function, on the misses | **Find work email · Loopster skill**: a waterfall, free Loopster Data first, then Icypeas, then Findymail (name + domain works) | **Find mobile phone · Loopster skill**: one paid provider step | **Find personal email · Loopster skill**: one paid provider step |
| 3. Check | `zero-bounce-validate-email` or `icypeas-verify-email` (required before an email sequencer) | `clearout-phone-validate-phone` | none |

Build the mobile and personal-email Functions in a table first (see "Mobile or personal email on the misses").

For a one-off lookup, or a provider no Function step can take, use `run_capability` instead (see `references/routes.md`).

## Step 1: Free pass

- Run `run_capability` with the free action for every person who has a LinkedIn URL, with `maxCostUsd: 0` and an `idempotencyKey`.
  - Keep this pass a capability, even when the job repeats: the domain check must happen between the free pass and the paid pass, and the Function's waterfall would stop at a stale free email. `maxCostUsd: 0` also guarantees nothing is charged. A scheduled or Auto-run table has no separate free pass: see "When a table is needed", item 5.
  - The paid Function then runs only on the misses.
- Batch up to 1,000 inputs per call.
- Poll `get_run`, then read every page of `list_run_items` (100 items a page; keep calling with `nextCursor` until none comes back). Parse each `output`: `{"found": true, "email": …}` or `{"found": false}`.
- **Check the domain now, not later.** An email whose domain differs from the person's **current** company domain is usually from a previous job, so it counts as a miss.
  - People who changed jobs recently are the most likely to have an email at a previous employer, so always check the domain.
  - Use the current company domain from the list (search records carry `companyDomain`), or from `loopster-data-enrich-person` `company_website`.
- Report: "Free pass: N of M on the current company's domain, at no cost. K more were at a previous employer and go to the paid pass."

## Step 2: Paid pass, only for the misses

1. **Reuse or build the Function.** Use the one you found in "Before you start". If **Find work email · Loopster skill** is not there, build it from `references/find-work-email.function.md` using the `function-builder` steps. Building it costs nothing. Write its id in the "Functions" section of `loopster-context.md`.
   - For everyone in the paid pass, leave the `LinkedIn URL` input **blank**. The free step already ran on it, and running it again returns the same previous-employer email.
   - Apply the domain guard to the Function's results too.
2. **Price it.** Multiply `costEstimate.maxUsdPerRun` by the number of misses.
   - For this Function that is close to a ceiling: it has no AI step, and the providers charge only when they find an email.
   - Show it with the pricing sentence and get a yes.
   - If the total is a big spend (house rules, section 4c), ask in that section's wording, and say how you will control the spend: the 1, 10, then 100 steps, the 1.5 times stop, and the wallet reads.
3. **Run 1, then 10, then 100 at a time** (house rules, section 5).
   - Read `get_wallet` `consumedUsd` before and after each batch. Compare the change with that batch's quote (`maxUsdPerRun` × the inputs in the batch). Stop and ask the user if a batch costs more than 1.5 times its quote.
   - **Up to about 25 people, and the results are for you only:** use `run_function`.
     - Send a list of inputs keyed by the input ids from `get_function`, plus an `idempotencyKey` per batch.
     - Poll `get_run` with the batch `runId` until it is done.
     - Then call `get_function_run` once per person, passing `functionId` and that person's `rowId` as `runId`. Write each answer into the contacts CSV as you read it, next to its input row.
     - The output is `work_email` in the pack's recipe. A Function you reused may name it differently, so read the key with `get_function`. An empty answer, or JSON such as `{"found":false}`, means not found.
     - List anyone skipped or rejected as "not run", not as "not found".
   - **More than about 25 people, or the user wants the rows in Loopster:** use one `run-function` column in a table (see "When a table is needed"). A table holds every result in a cell, while `run_function` needs one read per person.
4. **Mobile or personal email.** See the next section.

### Mobile or personal email on the misses

- **If the user will look these up again,** use **Find mobile phone · Loopster skill** or **Find personal email · Loopster skill**. Reuse it if it exists. Each holds one paid provider step, because every step in a Function runs for every input. Build and test them table first, not straight in a sandbox:
  1. Make a scratch table (`autoplay: false`) with a `LinkedIn URL` column and 3 of the user's real misses. The header must be exactly `LinkedIn URL`, because the Function input takes its name from that column.
  2. Add the provider step as one column, using the step and settings in `references/find-phone-and-personal-email.function.md`. Price it, ask, then run 1 row, then the other 2, and check the answers.
  3. Turn the working column into a Function with `create_function` and `fromTable` (`function-builder`, Step 2, "From a working table"), with that column as both the step and the output. Write its id in the "Functions" section straight away. Read the new input ids with `get_function`.
  4. Dry-run the publish. Ask before the live publish, and ask again before opening it to agents.
  5. Run 3 real samples through the Function and compare them with the table cells (price them first and ask) before any list.
  - Run it the same way as the work-email Function: price it, run 1, then 10, then 100 at a time, read the wallet after each batch, and use a `run-function` column for more than about 25 people.
  - To try a second provider on the misses, build another Function the same way from the reference, with that provider's step, titled `Find mobile phone (<provider>) · Loopster skill`. Record its id in the "Functions" section and run it only on the first one's misses. For a single try, use `run_capability` on the misses.
- **For a one-off, or a provider no Function step can take** (`findymail-find-mobile-phone`, `contactout-*`): run the capability from `references/routes.md` on the misses, with `maxCostUsd` on `run_capability`. Price it as the capability's `cost` × the number of misses.

## Step 3: Check (required before an email sequencer)

- **Before anything goes into an email sequencer** (Instantly, Smartlead, Mixmax), check every email, free ones included. A free email is found, not verified.
- For other uses (CRM fill, research), checking is optional. Label unchecked emails `unverified`.
- Email checks cannot be Function steps, so this is one of the few jobs that needs a table column or a capability.
- **Easiest route, a table column:** `zero-bounce-validate-email` or `icypeas-verify-email` with `execution_mode: "managed"` in its settings runs on Loopster's account with no other setup.
  - Put the emails in a table and add the column. Use the user's table if the people are already in one, or a check-only table named `Contacts · email check · <YYYY-MM-DD>`.
- **As a capability** (`run_capability`, no table), or with `findymail-verify-email` (which has no `execution_mode` setting), the checker runs on the user's own key, or on Loopster's account only once it is saved as that provider's default. Without either, it answers 400.
  - Check `list_provider_defaults` before promising a check.
  - If neither is set up, ask the user whether to save Loopster's account as the default (`set_provider_default` with `provider` and `account: "loopster"`). It applies to every new column for that provider, so it's their call.
  - If they say no, use the table column above, or mark the emails `unverified`.
- Price it as the cost per email × the count, then ask and cap.
- Keep emails the checker marks valid. Mark risky ones as risky. Drop invalid ones.
- **Phone numbers:** `clearout-phone-validate-phone` can be a step in the mobile Function. Give it a run condition so it runs only when a number was found, and feed it the number extracted by a Formula (`references/find-phone-and-personal-email.function.md`; `function-builder`, "Steps that run only sometimes"). For a one-off, run it as a capability on the numbers you found.

## Respect consent

Mobile numbers and personal emails carry stricter rules in many regions (for example the EU and UK). Ask what the user will use them for, and remind them to follow their own policy and local law before calling or texting.

## Domain guard (every step)

An email must match the person's **current** company domain:
- `@example.com` for `example.com` passes;
- a previous employer's domain fails, and goes back as a miss;
- a gmail address in a work-email field fails.

After the last paid step, put any remaining mismatches on a "needs review" list rather than dropping them silently.

## Show the result

```
Contacts: 300 people · work email for 241 (80%)
  Free (Loopster Data):    198
  Paid (waterfall):         43   real cost $X.XX
  Checked: 43 · valid 39 · risky 3 · invalid 1 (dropped)
  Needs review (domain mismatch): 2
Saved: ./contacts-2026-10-25.csv   (or: new columns on "Prospect list · …")
```

Take the real cost from `get_wallet` `consumedUsd` before and after the play. Then add the pricing sentence:

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Offer the next step: `outbound-launch`, or adding the contacts to their CRM through `crm-manager`.

## When a table is needed

Use a table when the user wants the rows in Loopster, when you need results for more than about 25 people, or when the people already live in one. Keep it thin: the logic stays in the Function, and the table gets one `run-function` column that calls it. Never rebuild the waterfall as table columns.

1. **The people.** Use the user's table. For a CSV or a pasted list, create one (`create_table` with `autoplay: false`, then `insert_rows`) named as the house rules describe. Turn on `set_table_create_columns_from_keys` before the insert, or add each column first, so the keys become columns. If the user's own table has Auto-run on (`get_table`), call `set_table_autoplay` with `false` before you add the Function column. If the free pass answered some people on the current company's domain, write those emails into a plain column (`templateId: "manual"`, then `update_cells`), and run the Function column on every other row by `rowIds`, including people whose free email was at a previous employer.
2. **Add the column** with the Function's input ids from `get_function`:

   ```json
   {"templateId": "run-function", "header": "Work email",
    "taskConfig": {"runFunction": {"functionId": "<id>",
      "inputMappings": [
        {"inputId": "<First name id>", "mode": "column", "sourceColumnId": "<column id>"},
        {"inputId": "<Last name id>", "mode": "column", "sourceColumnId": "<column id>"},
        {"inputId": "<Company domain id>", "mode": "column", "sourceColumnId": "<column id>"}]}}}
   ```

   - Leave the optional `LinkedIn URL` input unmapped for the paid pass. Read one row's cell before you run 10.
3. **Price and run.** Price the column from the Function: `get_function` `costEstimate.maxUsdPerRun` × the rows you will run. Use this figure for the quote and the big-spend check. Send `trigger_rows` with `rowIds`, `columnIds` and an `idempotencyKey`. Run 1 row, then 10, then 100 at a time, and read `get_wallet` `consumedUsd` before and after each batch. Stop and ask if a batch costs more than 1.5 times its quote. Keep `autoplay` off while you build.
4. **Read the result.** The cell holds a JSON object of the Function's outputs, each itself JSON text. Read one row's `work_email` value from the 1-row run first. If it is plain text, use it as it is. If it is JSON, use the field name you see there in the Formula or `path`. Pull the email into its own column with a Formula that parses twice, or a field reference whose `path` is `["work_email", "<field>"]`. `get_function` shows the output keys; `list_columns` does not. Then read the rows with `list_rows` and write the CSV.
5. **Scheduled or Auto-run tables:** no free pass runs on new rows, so map the optional `LinkedIn URL` input in that column so the free step answers first, and add a Formula column that flags emails whose domain differs from the company domain as needs review. Price a month of firings (rows per firing × `maxUsdPerRun`, run 10 first), and if that is a big spend (house rules, section 4c), ask in that section's wording. A schedule re-runs every cell unless you send `cells: "empty"`, so send it and only new rows run. Create the schedule paused, and ask before you resume it (house rules, section 6).

## If something goes wrong

- **Very low free hit rate:** most records lack LinkedIn URLs. Offer `loopster-data-email-to-linkedin` (free), or a search that matches name and company, to get URLs first.
- **A paid step is refused for "no account":** the provider needs the user's own key, or Loopster's account saved as its default. Ask before changing a default with `set_provider_default`.
- **Very low paid hit rate (under 30%):** check the domains are real company domains (not `linkedin.com` or a parent brand) and the names are clean. Strip titles, emojis and "Dr.".

## Go further

- `references/routes.md`: every provider, its inputs, its price and whether a Function can take it.
- `references/find-work-email.function.md`: the work-email Function design and how to run it.
- `references/find-phone-and-personal-email.function.md`: the mobile and personal-email Function designs.

<!-- contact-finder/references/find-phone-and-personal-email.function.md -->
# Function designs: Find mobile phone and Find personal email

Build each of these in a table first. Make a scratch table (`autoplay: false`) with a plain `LinkedIn URL` column and the user's 3 sample people. Add the provider step as a column that reads it. Price it and ask first (house rules, section 4), then run 1 row, then the other 2. Next, run `create_function` with `fromTable` (`function-builder`, Step 2), and write the new `functionId` in the "Functions" section of `loopster-context.md` straight away. Then dry-run the publish, and run 3 real samples through the Function before a list.

Every step in a Function runs for every input, so each Function holds one paid provider step. Run the free Loopster Data lookup first as a capability with `maxCostUsd: 0` (SKILL.md, Step 1), then run the Function on the misses only. Prices and the order to try providers are in `routes.md`.

## Find mobile phone · Loopster skill

- Title: `Find mobile phone · Loopster skill`
- Description: `Built by the Loopster contact-finder skill 0.1.0. One paid mobile lookup, for people the free Loopster Data lookup missed. Safe to edit in Loopster.`
- Input: a `LinkedIn URL` column in the scratch table. `fromTable` turns it into the required `LinkedIn URL` Function input, and the input takes the column's header, so the header must be exactly `LinkedIn URL`. If the list has no URLs, get them first (`routes.md`, "Getting a LinkedIn URL first").
- Step: `ai-ark-find-mobile-phone`, header `Mobile phone`, reading the `LinkedIn URL` column as `@{<LinkedIn URL column id>}`.
  - Read the template's settings with `get_column_template` and pass them under `taskConfig`. Set `execution_mode: "managed"` where it is offered, or leave it off if the user has their own key for the provider.
  - Other providers a Function can take: `wiza-find-mobile-phone`, `surfe-find-mobile-phone`, `better-contact-find-mobile-phone`, `full-enrich-find-mobile-phone`. Use one per Function. `findymail-find-mobile-phone` and `contactout-find-mobile-phone` are not Function steps; use `run_capability`.
- Output: return the provider column. Check the output key with `get_function` after `fromTable`. A lookup that finds nothing still returns text such as `{"found":false}`, so read it as JSON.
- Optional check step: `clearout-phone-validate-phone`. Extract the number first with a Formula that parses the mobile step's JSON (or a field reference), and give Clearout that Formula's output. It runs for every input unless it has a run condition, so give it one that runs only when the mobile step found a number. Build it in the same scratch table and set the run condition on its column with `update_column` before `create_function` (`function-builder`, "Steps that run only sometimes"). The condition comes along. Return its output only with that condition in place.

## Find personal email · Loopster skill

- Title: `Find personal email · Loopster skill`
- Description: `Built by the Loopster contact-finder skill 0.1.0. One paid personal-email lookup, for people the free Loopster Data lookup missed. Safe to edit in Loopster.`
- Input: a `LinkedIn URL` column in the scratch table, as above. It becomes the required `LinkedIn URL` Function input. If the list has no LinkedIn URLs, get them first (`routes.md`, "Getting a LinkedIn URL first") and run only the people who now have one.
- Step: `full-enrich-find-personal-email`, header `Personal email`, reading the `LinkedIn URL` column as `@{<LinkedIn URL column id>}`. Settings as above.
  - Other providers a Function can take: `surfe-find-personal-email`, `aviato-find-personal-email`. Use one per Function. `contactout-find-personal-email` is not a Function step; use `run_capability`.
- Output: return the provider column. Check the output key with `get_function` after `fromTable`, and read the answer as JSON.

## Publish and run

1. `create_function` with `fromTable`: `columnIds` is the paid step's column (plus the Formula and Clearout columns if you built them), and `outputColumnIds` is the paid step's column (add the Clearout column only with its run condition in place). Write the new id in the "Functions" section straight away.
2. `publish_function` with `dryRun: true`. Show the contract (inputs, output key, cost per run) and ask before the live publish.
3. After a clear yes, publish live. Ask again before opening it to agents, because it is a separate yes. Then call `set_function_agent_access` with `agentAccess: true`.
4. Run 3 real samples through the published Function and compare them with the table cells (price them first and ask). Then run it as the work-email Function runs: 1, then 10, then 100 at a time, the wallet read after each batch, and a `run-function` column for more than about 25 people.
5. Write the Function's id and its measured cost per run in the "Functions" section of `loopster-context.md`.

Mobile numbers and personal emails carry consent rules in many regions. Ask what the user will use them for before they call or text (SKILL.md, "Respect consent").

<!-- contact-finder/references/find-work-email.function.md -->
# Function design: Find work email · Loopster skill

Build it with the `function-builder` steps; the exact calls are below.

## Title and description

- Title: `Find work email · Loopster skill`
- Description: `Built by the Loopster contact-finder skill 0.1.0. Free Loopster Data first, then Icypeas and Findymail only when it misses. Safe to edit in Loopster.`

## Inputs (add in this order)

| Header | required | Notes |
|---|---|---|
| `First name` | true | |
| `Last name` | true | |
| `Company domain` | true | `example.com` form, no `www` |
| `LinkedIn URL` | false | With it, the free step can answer |

Keep each `input.id` from `add_function_input`; the step below mentions them.

## Step: work-email waterfall

`add_function_step` with `templateId: "waterfall-email"`, `header: "Work email"`, and:

```json
{"waterfallEmail": {
  "providers": [
    {"id": "loopsterDataFindWorkEmail-default", "order": 0, "enabled": true, "taskType": "loopsterDataFindWorkEmail"},
    {"id": "icypeasFindEmail-default", "order": 1, "enabled": true, "taskType": "icypeasFindEmail", "executionMode": "managed"},
    {"id": "findymailFindByName-default", "order": 2, "enabled": true, "taskType": "findymailFindByName", "executionMode": "managed"}
  ],
  "validation": {"enabled": false},
  "inputMapping": {
    "first_name": "@{<First name id>}",
    "last_name": "@{<Last name id>}",
    "domain": "@{<Company domain id>}",
    "linkedin_url": "@{<LinkedIn URL id>}"
  }
}}
```

- If the user has their own key for a provider, drop `executionMode: "managed"` from that step so it runs on their key.
- The answer lists `childColumnsBuilt`: a result column ("Work Email", key `result`) and one column per step.
- `appliedFixes` may say verification was left off because no verifier account is set. That's fine. Keep `validation` off: email checks cannot be Function steps. Check emails separately (SKILL.md, Step 3).
- The answer's `costEstimate.maxUsdPerRun` is the most one run of this Function can cost, because it has no AI step. If you add an AI step, treat the figure as a floor. It is about $0.019 at list prices; the paid steps charge only when they find an email.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Output

`get_function` → `draft.outputs` lists the result column ("Work Email", grouped under "Work email"). Set it as the only output:

`set_function_outputs` with `columnIds: ["<result column id>"]`. The output key becomes `work_email`.

## Publish and open

1. `publish_function` with `dryRun: true`. Expect `wouldPublish: true` and outputs `["work_email"]`.
2. Show the user the contract from the dry run (inputs, output key, cost per run) and ask. Only after a clear yes, publish live. Ask again before opening it to agents: it is a separate yes.
3. `publish_function` (live).
4. After that second yes, `set_function_agent_access` with `agentAccess: true`.

## Run

Run it as SKILL.md, Step 2 says: 1, then 10, then 100 at a time, with the wallet read after each batch and a stop at 1.5 times the quote. Use `run_function` up to about 25 people and one `run-function` column above that (see "When a table is needed"). Function-specific points:

- Inputs are keyed by input id (`get_function` lists them). Leave `LinkedIn URL` out when the free pass has already run on these people.
- `work_email` holds the email when one was found. An empty answer, or JSON such as `{"found":false}`, means not found. Skipped or rejected inputs are "not run".
- In a table, map the three required inputs, and `LinkedIn URL` only when the free pass has not run on those rows.

## crm-manager

A RevOps assistant for HubSpot, Salesforce or Attio data in Loopster. It audits CRM records (fill rates, duplicates, personal or invalid emails, missing LinkedIn and firmographics, contacts who changed jobs) and gives a health score with the cost to fix each issue. It fills the gaps free first, proposes every change for review, writes back only approved changes (blanks only, by default), revives closed-lost deals that show a new reason to talk, and can keep the CRM fresh on a monthly schedule. The gap fills and the work-email search become reusable Functions, so the next audit reuses them. Use when the user says "clean my CRM", "audit HubSpot", "fill missing fields", "fill CRM gaps", "dedupe contacts", "who in our CRM changed jobs", "enrich our accounts in Salesforce", "revive closed-lost", or "keep our CRM up to date".

# CRM manager

## What you get

- **A health report:** fill rate per key field, duplicates, bad or personal emails, job changes and stale records, each with the cost to fix. The audit is free and needs no table.
- **A fix table in Loopster,** made when the user picks fixes, showing current value next to proposed value for every record, so the user approves before anything changes.
- **Write-back** of approved changes only. By default it fills blanks and never overwrites, and tests 1 record, then 10, then all.
- **Reusable Functions:** the free gap fills become a "Fill CRM gaps · Loopster skill" Function after the first run, and the paid email search is the "Find work email · Loopster skill" Function. The job-change check is the "Job change check · Loopster skill" Function that `champion-tracker` builds. The next audit reuses all three. The monthly refresh reuses only the free ones (gap fills and job-change check); the paid email search runs by hand.
- **Optionally:** a closed-lost revival list, and a monthly refresh created paused.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (ICP, destinations).

Then check for Functions to reuse: the "Functions" section of `loopster-context.md`, then `list_functions`. Look for **Fill CRM gaps · Loopster skill**, **Find work email · Loopster skill**, **Job change check · Loopster skill** and **Why now · Loopster skill**. Read each one you find with `get_function`, and tell the user its steps and price.

Then find the records:

| Where the CRM data is | How |
|---|---|
| A Loopster table imported from HubSpot or Salesforce (Loopster → new table → HubSpot or Salesforce import) | `list_tables` with `search: "HubSpot"` or `"Salesforce"`. These tables have a record column, reference columns per property, and a `Record ID`. |
| No import yet | Ask the user to create one in Loopster (it syncs fields and keeps the record id for write-back), or to export a CSV with the record id column. |
| Attio | A CSV with record ids, or the `attio-find-record` column per row. |

Check `list_connections` for the CRM account, and make sure it's the right portal or org. A workspace can have several HubSpot connections, so confirm which one is production and which is a test.

Step 1 makes no table. The working copy is made in Step 3, once the user has picked fixes.

## Step 1: Audit (free, no table)

Read every record from the import table (`references/audit-checks.md` says how, for a large table and a small one) and compute the checks with a local script, without paid calls:

- **Fill rate** per field: email, first and last name, title, company, domain, LinkedIn URL, industry, size, country, phone.
- **Duplicates:**
  - same normalized email;
  - same LinkedIn URL;
  - same first and last name plus company domain;
  - for companies, the same normalized domain.
- **Email quality:** personal domains (gmail and similar), role inboxes (info@, sales@), malformed addresses.
- **Mismatches:** email domain ≠ company domain.

Show a health score (the share of records with all key fields valid) and the top issues with counts.

If the user only wanted a health report, give it in chat and save the issue lists and duplicate groups as CSV files in their working folder (house rules section 10). Create no table.

## Step 2: Price the fixes

Show one table: issue · records · fix · source · runs as · price (estimate).

| Issue | Records | Fix | Source | Runs as | Price |
|---|---|---|---|---|---|
| Missing LinkedIn URL | count | Find from email | `loopster-data-email-to-linkedin` | Fill CRM gaps Function | free |
| Missing title or company (has LinkedIn) | count | Person profile | `loopster-data-enrich-person` | Fill CRM gaps Function | free |
| Missing industry or size or country (has domain) | count | Company profile | `loopster-data-enrich-company` | Fill CRM gaps Function | free |
| Missing work email | count | Find email | **Find work email · Loopster skill** (free Loopster Data step first, then Icypeas, then Findymail) | Function, from a `run-function` column | free first, then paid |
| Unverified emails | count | Check | `zero-bounce-validate-email` | Table column (`execution_mode: "managed"`); `run_capability` only when `list_provider_defaults` shows a ZeroBounce account or the user has their own key (`contact-finder`, Step 3) | $0.0065 per email |
| Changed jobs | count | Compare current company | **Job change check · Loopster skill** (built by `champion-tracker`) | One `run-function` column; if the Function doesn't exist yet, run `champion-tracker` first | free |
| Duplicates | count | Merge list for the user (CRMs merge in their own UI) | none | Local script | free |

- For a Function row, the estimate is a floor, because usage-priced steps add to it. Step 3 measures the real cost on 10 records, and you quote the rest from that.
- Email checks are table columns or capabilities, because a Function cannot hold them. A Function can find emails but cannot verify them.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Ask which fixes to run. In the plan, say what you will create: the working table and, once the free fill columns work, the Fill CRM gaps Function. For gaps the free sources leave, use the paid routes in house rules section 3b. Never fill CRM fields with an AI web research column first; a CRM-wide fill is usually a big spend (section 4c).

## Step 3: Propose changes (no CRM writes yet)

Step 3 goes in this order: working copy, gap fills, job changes, work email and email check (only if picked), then proposed values and review.

**Working copy (skip it for about 25 records or fewer with no write-back: see the next paragraph).** Read the import table's rows (as in `references/audit-checks.md`) and insert them into a working table `CRM health · <CRM> <object> · <YYYY-MM-DD>` (for example `CRM health · HubSpot contacts · 2026-10-25`) (blank, `autoplay: false`) with the record id. Never add columns to the live import table if it has Auto-run on.

To look at a handful of records (up to about 25) with no write-back, and with the Fill CRM gaps Function already built, skip the table. Run the Function with `run_function`, read each result with `get_function_run`, and compare with the CRM values yourself.

**Gap fills (free).**
- **The Fill CRM gaps Function exists:** add ONE `run-function` column. Map its inputs (email, LinkedIn URL, company domain; input ids from `get_function`) to the table's columns. Mark the source columns of its optional inputs (email, LinkedIn URL, company domain) optional with `update_column` and `optionalMentions`, because a record may lack any of them. Don't copy its steps into columns.
- **First build, no Function yet:**
  1. Add one column per free fix from Step 2 (`loopster-data-email-to-linkedin`, `loopster-data-enrich-person`, `loopster-data-enrich-company`), and test them on 10 rows as in "Proposed values and review" below.
  2. Once they work, turn them into a Function with `create_function` and `fromTable` (see the `function-builder` skill). Its inputs are the CRM columns the fixes read (mark the ones a record may lack as optional). Return only outputs that always get a value, for example a Formula with a fallback.
  3. Name it **Fill CRM gaps · Loopster skill**, and record its id in the "Functions" section of `loopster-context.md`.
  4. Publishing it and opening it to agents each need their own yes (house rules section 4b).
  5. This table keeps its first-build columns. From the next audit on, and for any scheduled table, use one `run-function` column instead.

**Job changes (free).**
- **The Job change check Function exists:** add ONE `run-function` column. Map its LinkedIn URL input to the record's LinkedIn URL (the CRM value, or the one the gap fill found; a Formula column can pick whichever has a value). Map its "Company when champion" input to the CRM company domain. Input ids come from `get_function`.
- Run that column on 1 row and read its cell first, to see its shape. Then add a `Moved` column that reads the `moved` output: a Formula that parses the cell (parse twice only if the output is itself JSON text), or a field reference whose `path` starts with `["moved"]`. `get_function` lists the output keys; `list_columns` does not. `Moved` should read `yes`, `no` or `unknown`.
- **No Function yet:** run the `champion-tracker` skill on a small table first so it builds `Job change check · Loopster skill`, or leave job changes out of this audit and say so. Record the id in the "Functions" section of `loopster-context.md`.
- Never copy the Function's steps into columns.

**Work email (paid, only where needed).**
- Add one `run-function` column calling **Find work email · Loopster skill** (id in the context file, or `list_functions`; if it's missing, build it with the `contact-finder` skill). Map First name, Last name, Company domain and LinkedIn URL (optional).
- Check the domain. The `Proposed work email` Formula returns the Function's `work_email` only when its domain equals the CRM company domain, and returns an empty string otherwise (a miss such as `{"found":false}` also counts as empty). List the mismatches as "needs review" in the review summary. Never propose an email at a previous employer's domain (`contact-finder`, "Domain guard").
- Run it only for records that need it. Add a free Formula column `Needs work email` that always returns `yes` or `no`: yes when the CRM email is blank and the record has a name and a company domain. Mark every column the Formula reads optional (`optionalMentions`: CRM email, first name, last name, company domain), so a blank value still lets it run and it always returns `yes` or `no`.
- Do not set a run condition on the work-email column. A column that reads a skipped column does not run (house rules, section 9), and `Proposed work email` reads this column on every row. Trigger it with `trigger_rows` on the `rowId`s where `Needs work email` is `yes`, and always name those `rowId`s. Never trigger this column without `rowIds`. Cells you don't trigger stay blank, and `optionalMentions` lets a blank through. After each batch, re-run `Proposed work email` (and `Write payload`, once it exists) on those rows with `force: true`.
- On the work-email `run-function` column, mark the source column of the Function's optional input (LinkedIn URL) optional with `update_column` and `optionalMentions`.
- Do not run this column yet. Price it, ask and run it in item 3 of "Proposed values and review" (1 row, then 10). Pick the 10 rows from those where `Needs work email` is `yes`, and include records with no LinkedIn URL (they must still run, not skip). If one comes back skipped, fix the optional mentions and re-run only that record: `trigger_rows` with its `rowId` and the work-email column in `columnIds`, and no `force`. Without `force`, a skipped cell runs again and the cells that already hold an answer are kept; `force: true` would bill them again. Then read `Proposed work email` (and `Write payload`, once it exists) on a row you did not trigger: both must complete. If they fail, add a `manual` column `Found work email`, write the parsed emails into it with `update_cells`, and point `Proposed work email` at that column.

**Email check (paid, only if the user picked it).** Add a `zero-bounce-validate-email` table column (`execution_mode: "managed"`) that reads the CRM email. Price it with `estimate_trigger_cost` on the rows that have an email, ask, and run 1 row, then 10, then 100 `rowId`s at a time with `maxCostUsd` at the agreed amount. Read `get_wallet` `consumedUsd` before and after each batch. If the whole job is over $25, use the 4c wording. Keep it out of any schedule. Flag invalid emails in the review summary, and never delete or overwrite the CRM email.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

**Proposed values and review.**
1. Add one `Proposed <field>` Formula per field: it uses the found value only where the CRM value is blank, unless the user chose "overwrite".
   - A `run-function` cell holds a JSON object of the Function's outputs, each itself JSON text. Read a field with a Formula that parses twice, or a field reference with `path` `["<output key>", "<field>"]` (`get_function` lists the output keys; `list_columns` does not).
   - Mark the `run-function` columns optional in each Proposed Formula, and give each a fallback so it always completes.
2. Run the free columns on 10 rows, show current vs proposed, then run the rest. Include records that lack an email, LinkedIn URL or company domain in the 10.
   - First-build columns: use `maxCostUsd: 0`.
   - Each free `run-function` column (Fill CRM gaps, Job change check): check with `get_function` that `costEstimate.maxUsdPerRun` is 0 and the Function lists no `unpricedSteps`. Read `get_wallet` `consumedUsd` before and after the 10 rows; it must not move.
3. Run the work-email column on its own, never in the same trigger as a write-back column:
   - Quote it from its Function: `get_function` `costEstimate.maxUsdPerRun` × the number of `rowId`s where `Needs work email` is yes, plus any usage-priced step measured on 10 rows. Use this figure for the quote and the big-spend check. Control its spend with the 1, 10, then 100 steps, the 1.5 times stop, and `get_wallet` `consumedUsd` before and after each batch (the next bullets).
   - Run 1 row, then 10. Read `get_wallet` `consumedUsd` before and after the 10 (in a shared workspace, other runs can add to it). Show the hit rate and the cost.
   - Quote the rest from that measurement and get a yes. If it is a big spend (section 4c), use the 4c wording.
   - Run the rest in batches of 100. After each batch, compare its real cost with its share of the quote, and stop and ask if it costs more than 1.5 times that.
   - Report the real cost from `get_wallet` `consumedUsd`, which includes the Function.

   Real usage depends on your use case and settings, so always check the final cost estimate before you run.
4. Give the user a review summary: "Industry: fill 412 blanks. Title: fill 96 blanks, 31 differ from the CRM (not changed). Emails: 87 invalid (flagged, not changed). Job changed: 27 contacts."
5. Job changes (the contacts where `Moved` is `yes`) are their own list. Don't overwrite the contact's company; that loses history. Suggest the CRM's own process: mark them, then create a new contact at the new company.

## Step 4: Write back (only with a yes)

1. **Check automations first.** Ask the user whether a CRM workflow or flow fires on these property changes; one could email the contacts. Pause it or exclude these records before writing.
2. **Write-back column:**
   - **HubSpot:**
     - First build a blank-safe `Write payload` Formula that holds only the approved fields with a value, and a `Has payload` flag that the write-back column's run condition reads (`references/writeback.md`).
     - Then add `hubspot-update-object`, with `mode: "update"`, `objectType` (contacts or companies), `recordId: "@{Record ID}"` and `properties: "@{Write payload}"`. Use the CRM's internal property names (for example `industry`, `jobtitle`, `hs_linkedin_url`).
     - Set `integrationConnectionId` to the right HubSpot connection.
     - Never map proposed columns straight into `properties`, because a blank could clear the field.
   - **Salesforce:** `salesforce-upsert-object` with an external id, or `salesforce-update-object` with the record id.
   - **Attio:** `attio-send-record`.

   Settings are in `references/writeback.md`. CRM writes are table columns, so the working table stays.
3. **One record first.** Trigger the write-back column on its own, on 1 row, and have the user check the record in the CRM (nothing else changed). Then 10, then the rest.
4. **Each batch needs its own yes.** Report what was written: record count, fields, and any errors from the cell messages.
5. **Changing the proposal after the user approved it.** A `Proposed` or `Write payload` Formula recomputes at once, so the edit changes what the next batch writes. First try it in a table sandbox (house rules, section 5b): open it with `mode: "explicit"` and the `rowIds` of a few records the user already checked, and show the new payload next to the old one. Publish after a yes, then ask the user to approve the review again before any further write. Never run the write-back column in a sandbox: its rows are real CRM records.

## Closed-lost revival (optional)

1. Get closed-lost deals with their company domain and loss date: an import of deals, or a CSV.
2. For deals lost 3 to 24 months ago, look for a new reason to talk:
   - the champion moved, or a new leader is in seat (`champion-tracker`, or `signal-outbound` route 1);
   - a funding, hiring or launch signal: run **Why now · Loopster skill** on the deal domains (id in the context file, or `list_functions`; if it's missing, build it with the `signal-outbound` skill, which holds the design).
3. Pick the path before you run anything. Up to about 25 deals and no CRM write: no table. Run **Why now · Loopster skill** with `run_function`, read each result with `get_function_run`, and save the ranked list to a CSV. More than about 25 deals, or tasks or a list wanted in the CRM: use the table in item 5, and read the ranking from its cells.
   - Price it first (`costEstimate.maxUsdPerRun` × deals; usage-priced steps add to it) and ask.
   - Run 1 deal, then 10, then the rest, and read `get_wallet` `consumedUsd` before and after each step.
4. Rank by signal strength, and write one sentence per deal: what changed, plus a suggested opener.
5. Offer to create tasks or a list in the CRM, with a yes. That needs a table: the deals, one `run-function` column calling the Why now Function, and a write-back column.
   - Quote the `run-function` column from its Function: `get_function` `costEstimate.maxUsdPerRun` × the rows, plus any usage-priced step measured on 10 rows. Use this figure for the quote and the big-spend check. Control its spend with the steps in the next bullet: 1, 10, then 100 at a time, the 1.5 times stop, and `get_wallet` `consumedUsd` before and after each batch.
   - Run 1 deal, then 10. Quote the whole job from the real cost of the 10. If it is likely over $25, the "Ask above" amount in `loopster-context.md`, or 10% of `spendableUsd`, ask with the wording in house rules section 4c. Then run 100 at a time, read `get_wallet` `consumedUsd` before and after each batch, and stop and ask if a batch costs more than 1.5 times its share of the quote.
   - Write-back follows Step 4, with its own yes.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Keep it clean (optional)

Offer a monthly refresh. A schedule runs table columns only, and it is created paused, so:

- Use a table whose free work sits behind `run-function` columns: one calling **Fill CRM gaps · Loopster skill** and one calling **Job change check · Loopster skill**, plus the Formula columns that read them (for example `Moved`). Don't schedule copied step columns.
- On the first-build table, add the `run-function` columns beside the first-build columns (give them a different header), and schedule only the `run-function` columns and the Formulas that read them.
- Schedule only columns that cost nothing. Prove it first: `get_function` must show `costEstimate.maxUsdPerRun` 0 and no `unpricedSteps`, and `get_wallet` `consumedUsd` must not move on a 10-row run.
- Keep the **Find work email · Loopster skill** column out of the schedule. Its paid steps would charge every month. Run it by hand when the user asks.
- Create the schedule with `paused: true` and `cells: "all"`: every column in it is free, and the job-change check must re-run on every row each month. This is the "price the full re-run" option in house rules, section 9, and it costs $0 only after you prove it (see below). If you ever add a paid column, send `cells: "empty"` or price every firing.
- Name in `columns` (the `create_schedule` parameter; `columnIds` belongs to `trigger_rows`) only the free `run-function` columns and the Formula columns that read them, and leave `rerunDependents` off (its default), so the work-email column and the write-back column never fire from the schedule. After you create it, read `list_schedules` and check it lists exactly those columns.
- A schedule re-runs only the rows the table holds; it does not re-read the CRM. New CRM records appear only when you re-read the import table (`references/audit-checks.md`) and insert them as rows, so tell the user that is a step to repeat before the monthly firing. The free columns then run on the new rows and re-check the old ones.
- Before resuming, run the schedule's columns by hand on 10 rows with `trigger_rows`, and read `get_wallet` `consumedUsd` before and after (it must not move). `get_function` should show `costEstimate.maxUsdPerRun` 0 and no `unpricedSteps`.
- Resume only after a separate yes (house rules sections 4b and 6). After every firing, read `consumedUsd` again. If it moved, pause the schedule and tell the user. Before each firing, if anyone has edited the Fill CRM gaps or Job change check Function, read `get_function` again: if `costEstimate.maxUsdPerRun` is above 0 or `unpricedSteps` appears, pause the schedule and ask. If the monthly cost could be a big spend, use the 4c wording.
- Write-back columns stay manual unless the user explicitly asks for automatic write-back after seeing several clean runs.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Show the result

```
CRM health · HubSpot contacts · 2026-10-25   (8,412 records)
  Health score: 61% → 84% after fixes
  Filled (free): LinkedIn 1,920 · title 640 · industry 2,310 · size 2,288
  Emails checked: 1,104 · invalid 87 (flagged, not deleted)
  Duplicates: 214 groups (list saved for merge in HubSpot)
  Job changes: 312 (list saved → champion-tracker / outbound)
  Functions: Fill CRM gaps · Loopster skill, Find work email · Loopster skill, Job change check · Loopster skill (ids in loopster-context.md)
  Written to HubSpot: 5,158 fields on 3,902 records (blanks only)  · real cost $X.XX
```

Take the real cost from `get_wallet` `consumedUsd` before and after the play, so it includes the Functions. Then add the pricing sentence:

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## If something goes wrong

- **The write-back cell errors with a property name:** the CRM's internal name differs from the label. Ask the user for the internal name (HubSpot property settings), and fix the mapping.
- **Wrong portal:** stop. Check `integrationConnectionId` against `list_connections` before any further batch.
- **The import table has Auto-run on:** don't add columns to it. Work on a copy.
- **A work-email cell is blank:** you did not trigger that row, which is right for a record that already has an email.
- **A Function output reads `{"found":false}`:** that is a miss, not a blank. Parse the text, and leave the CRM field alone.

<!-- crm-manager/references/audit-checks.md -->
# CRM audit checks (free)

Run these on the rows you read from the import table. They make no paid calls and need no table: the audit is a local script on the rows you read.

**Reading the rows:**
- **More than about 500 records:** use `export_table` with `format: "jsonl"`, then poll `get_export` and download `resultUrl` to a local file (free; 20 exports an hour). Each line is one row keyed by column name, with `_row_id`.
- **A small table, or no way to download a file:** use `list_rows` (paged with `page` and `pageSize`; use `cursor` only when you filter or sort). CRM import tables are wide, so use a `pageSize` of 100 or less and ask only for the columns the checks read (`columns`). Read the default detailed format, because `concise` shortens long values.
- A large page can come back with fewer rows than `pageSize`, and the answer says so in `warnings`. If you see that, read the table again from the start with a smaller `pageSize`, or rows are skipped.
- At the end, check that the rows you read match the row total in `get_status`.

**Running the checks:**
- **Over a few hundred records:** write the rows to a local file (the export, or the pages you read) and compute the checks with a short script. Don't do it by reading.
- **No code execution available:** audit a random sample of 500, and say it's a sample.
- The rows you read are a snapshot, and so is the working copy table made later in Step 3. For a monthly refresh, re-read the CRM import table first, so you work on current records.

## Normalize first

- **Email:** trim, lower-case.
- **Domain:**
  - from the website: lower-case, strip `http(s)://`, `www.` and any path;
  - from the email: the part after `@`.
- **LinkedIn URL:** `https://www.linkedin.com/in/<handle>`. Lower-case the handle, and strip query strings and the trailing slash.
- **Names:** trim. Collapse spaces. Drop emojis and titles.

## Checks

| Check | Rule | Severity |
|---|---|---|
| Missing email | empty | high for outbound |
| Personal email | domain in gmail.com, googlemail.com, yahoo.com, outlook.com, hotmail.com, live.com, icloud.com, me.com, aol.com, proton.me, protonmail.com, gmx.com, mail.com | medium |
| Role inbox | local part in info, sales, hello, contact, admin, support, team, marketing, office | medium |
| Malformed email | not `x@y.z` | high |
| Domain mismatch | email domain ≠ company domain (ignore personal emails) | medium: often a job change or an agency |
| Missing LinkedIn URL | empty | medium: blocks the free routes |
| Missing title / company / industry / size / country | empty | low to medium |
| Duplicate contact | same normalized email; or same LinkedIn URL; or same first + last name + company domain | high |
| Duplicate company | same normalized domain | high |

## Health score

The share of records with:
- a valid work email;
- a name;
- a company domain;
- a LinkedIn URL;
- no duplicate.

Report it before and after fixes.

## Duplicate output

Group duplicates, and for each group list the record ids with their last-modified date, if the import has it. Most CRMs merge in their own UI, so give the user the list and the suggested survivor (the most complete or most recent record). Don't delete records through write-back.

<!-- crm-manager/references/writeback.md -->
# Write-back columns

All of these write to the user's CRM on their own connected account (`connection: own_key`; nothing is charged to the Loopster wallet). Every batch needs its own yes. Read the live settings with `get_column_template` before creating a column.

## HubSpot

**Step 1: build a blank-safe payload** with one Formula column, `Write payload`. It holds only the approved fields that have a value:

```js
(() => { const p = {};
  const add = (k, v) => { v = String(v ?? '').trim(); if (v) p[k] = v; };
  add('industry', @{<Proposed industry id>});
  add('jobtitle', @{<Proposed title id>});
  add('hs_linkedin_url', @{<Proposed LinkedIn id>});
  return Object.keys(p).length ? JSON.stringify(p) : ''; })()
```

- Mark every proposed column it reads as optional (`update_column` with `optionalMentions` listing their ids), so a blank proposal doesn't stop the Formula.
- The proposed columns must themselves always complete. Give them a fallback, never a skip.
- When nothing is approved for a row, the payload is blank. Do not rely on a blank value to stop the write. Add a free Formula column `Has payload` that always returns `yes` or `no`: `(() => String(@{<Write payload id>}).trim() ? 'yes' : 'no')()`. Mark `Write payload` optional in `Has payload` (`update_column` with `optionalMentions`), so a blank payload still lets it run. Then set a run condition on the write-back column with `update_column`: `{"enabled": true, "description": "Only when there is something to write", "condition": "(() => String(@{<Has payload id>}).trim() === 'yes')()"}`. Test on a row with nothing approved: the write-back cell must be skipped, and the CRM record must not change. Check the record in the CRM, not just the cell.

**Step 2: the write-back column.** Template `hubspot-update-object`, task `hubspotSendObject`:

```json
{"hubspotSendObject": {
  "mode": "update",
  "objectType": "contacts",
  "recordId": "@{<Record ID column id>}",
  "properties": "@{<Write payload id>}"
}}
```

- `properties` is a string holding a JSON object of HubSpot internal property names to values. Use internal names (HubSpot → Settings → Properties), not labels.
- Never map a proposed column directly into `properties`. A blank value would be sent as `""`, and that can clear the CRM field.
- Set `integrationConnectionId` to the right HubSpot connection; a workspace can hold several portals.
- Related templates:
  - `hubspot-create-object` (create mode, described for companies and deals; contacts are updated, not created, with these columns);
  - `hubspot-find-object` (look a record up);
  - `hubspot-associate-object`;
  - `hubspot-add-to-list`.

## Salesforce

| Template | Use it when |
|---|---|
| `salesforce-upsert-object` | An external id field exists. Updates a match or creates a new record, and is safe to re-run. |
| `salesforce-update-object` | You have the Salesforce record id. |
| `salesforce-find-object` | You need to look a record up first. |
| `salesforce-create-object` | Creating a new record. |

## Attio

| Template | Does |
|---|---|
| `attio-send-record` | Creates or updates a record, matching on a unique attribute |
| `attio-find-record` | Looks a record up |

## Before the first write

Ask the user to check their CRM automations. A property change can enrol contacts in a HubSpot workflow or a Salesforce flow that emails them. If one would fire, pause it or exclude these records first.

## Safe order

1. Proposed-value columns are filled and reviewed.
2. Create the write-back column with Auto-run off and the `Has payload` run condition.
3. `trigger_rows` with **one** `rowId`. Have the user check the record in the CRM, and confirm no other field changed.
4. Then 10, then the rest. Every trigger names `rowIds` explicitly, and `maxCostUsd: 0` is a safe cap for the write-back column.
5. Trigger the write-back column on its own. A `run-function` column is checked by reading the wallet, so run it first and separately (`get_wallet` `consumedUsd` before and after), and never include it in the write-back trigger.
6. Read the cell errors after each batch; they name the property or permission problem.

## decision-makers

Find the people who decide or influence a purchase at companies the user names, in one free step: one people search inside the list of companies, with titles and seniority from what the user sells. Use when someone asks who to contact at these companies, who the buyers or decision makers are at these accounts, or for people at a list of domains. To build a prospect list from a target description (companies and people, exclusions, export), use prospect-list.

# Decision makers

One step: named people at named companies. To build a whole prospect list from a description, use the `prospect-list` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Roles.** From what the user sells, write the buyer roles (who signs) and, if useful, influencers: 2 to 6 job titles plus seniority. Show them before searching. If the product is unclear, ask.
2. **Vocabulary once:** `list_search_filters` (see `references/icp-to-filters.md`).
3. **One search** for all companies: `search_people` with `specificCompanies` (domains match best, up to 1,000), the titles and seniority, `perCompanyLimit` = people per company (default 3). Never one search per company.
4. **Coverage.** Name the companies with nobody found. Try one wider search for those only (more titles, or seniority alone).
5. **Keep the results** the way the user wants: an answer in chat for a few, or a table with `create_table` (`type: "search"`, the `searchId`). Search and import are free.
6. **Report** per company who was found and their title, the companies with nobody, and the roles used. Offer `work-email` next.

## Does not claim

- Budget authority from a title, or that the person still works there (it is not a live check).

## dedupe-plan

Find duplicate contacts or companies in a list or Loopster table and propose a merge plan (which records are the same, which to keep and why), in one free step that deletes nothing. Use when someone asks to find duplicates, dedupe a list or CRM export, or which records are the same. Applying the plan is a separate step the user approves.

# Dedupe plan

One step: a plan, not a change. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Read once:** the file, or the table with one `list_rows` over the key columns.
2. **Normalise** without changing the data: lower-case emails and domains, trim spaces, drop `www.` and trailing slashes, strip common company suffixes (Inc, Ltd, GmbH).
3. **Group** rows that match on email; then name + company; then domain for companies. Give each group a reason (same email, same name and company).
4. **Keeper per group:** the most complete or most recent record, with a one-line why. Show which values the keeper would take from the others.
5. **Show the plan** (group · rows · keeper · reason) and counts. Write it to a new column or a CSV if asked.

Never delete, merge or overwrite anything. Applying the plan is a separate yes, and deletion stays with the user.

## Does not claim

- That two people with the same name are the same person without a second match (email, company).

## email-check

Check a list of email addresses before a send and sort every address into keep, risky or remove, with a reason. Free checks run first (duplicates, malformed addresses, role addresses like info@, disposable domains), then one paid verifier runs only on what is left, priced and agreed first. Nothing is deleted. Use when the user asks to verify emails, check if addresses will bounce, clean or scrub an email list, remove bad or duplicate emails from a CSV, or prepare a list for a campaign. To find emails people don't have yet, use contact-finder.

# Email check

The free checks go first, so the paid verifier sees as few addresses as possible. Every address ends in one group with a reason; nothing is deleted. Read `references/house-rules.md` once per session, and keep the calls few (the `fewer-requests` skill).

## Ask first

1. **Where are the addresses?** A few in chat, a CSV, or an email column in a Loopster table.
2. **Their own verifier account?** If the user has one connected, it runs on their key. Otherwise use one that runs on Loopster's account (step 3).
3. **What happens to the result?** A CSV back, a column in the table, or saved views per group. Default: a column, plus a CSV.

## 1. Load once

- **A few addresses in chat (up to about 25):** no table. Go to step 2.
- **A CSV:** load it into a new table with Auto-run off. Above about 10,000 rows, load the file (house rules, section 10b); below that, one `insert_rows` call.
- **A table:** read the email column once with `list_rows` (`columns` set to it).

## 2. Free checks

On that one read, mark each address:

| Check | Group | Reason |
|---|---|---|
| Not an email address (no single `@`, no dot in the domain, spaces) | remove | malformed |
| Same address as an earlier row, ignoring case and spaces | remove | duplicate (the first one stays) |
| A disposable-mail domain | remove | disposable |
| A role address: info@, sales@, support@, hello@, admin@ and the like | risky | role address |
| A personal domain (gmail.com, outlook.com and the like) when the list is meant to be work emails | risky | personal address |

Say the counts before anything is paid for.

## 3. One verifier on what is left

- **Pick it** from `list_column_templates` with `tab: "enrich"` (the `contact-finder` skill lists the usual email checks). Compare the prices, and whether it needs the user's own key.
- **As a table column** (the usual case): the verifier runs on Loopster's account when its settings carry `execution_mode: "managed"`. As a capability, it needs the user's key or a saved provider default. Never save a default without asking: it applies to every column made afterwards for that provider.
- **Price, ask, run** (house rules, section 4): `estimate_trigger_cost` for the rows that passed step 2 only. After a yes, run 1 row, then 10, then the rest (house rules, section 5), with `trigger_rows` and those `rowIds`. Poll `get_run`.
- **A few addresses in chat:** one `run_capability` with all of them, if the verifier runs that way for this workspace. Otherwise make a small table.

## 4. Sort and write back

| Verifier says | Group |
|---|---|
| Valid, deliverable | keep |
| Catch-all, accept-all, unknown | risky: the server accepts every address, so "valid" proves nothing there |
| Invalid, undeliverable, disposable | remove |
| No answer | risky: say why |

- Write each row's group and reason in one `update_cells` call, into a plain column you create first.
- Offer `export_table` for a CSV, or a saved view per group.
- **Never delete rows or addresses.** Removing them from a list, a CRM or a campaign is the user's step, after a yes.

## Report

Counts per group and reason, how many addresses the verifier checked and what it cost, and where the results are.

## What it does not claim

- That a "keep" address belongs to the person on the row: a verifier checks the mailbox, not its owner.
- Anything certain about catch-all domains.
- That a verdict stays true: mailboxes close, so check again before a later send.
- Consent: whether the list may be emailed is the sender's question.

## engager-leads

Turn LinkedIn engagement and event attendance into qualified leads. Pulls the people who reacted to or commented on a post (yours, a competitor's, or an influencer's in your space) or a company's recent posts, or takes an event guest list. Removes your own team, competitors and do-not-contact, resolves each person's current title and company, keeps those who fit the ICP, marks repeat engagers as warmer, and hands them to outreach with the topic they engaged with. Use when the user says "people who liked my post", "competitor's post engagers", "who commented on", "LinkedIn engagement leads", "event attendees", "webinar registrants", "who reacted to a competitor's post", or "warm leads".

# Engager leads

## What you get

A Loopster table `Engagers · <source> · <date>`, one row per person. For each:
- name, current title and company, and LinkedIn URL;
- which post they engaged with and how (reaction or comment, with the comment text);
- how many tracked posts they engaged with;
- ICP tier (A, B or C).

Ready for `contact-finder`, then `outbound-launch`.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (ICP, personas, competitors, do-not-contact, your own company domain).

Call `get_wallet` and note `consumedUsd` and `spendableUsd`. You need both, to report the real spend and to size a big spend.

Then look for Functions this play can call: the "Functions" section of `loopster-context.md`, then `list_functions`. You want two:
- one that takes a LinkedIn URL and returns the current title and company (Step 4);
- one that scores a person against the ICP (Step 5).

Run what exists. Build one only when none fits (house rules, section 7).

Where each part runs:
- **The engager list is a table.** The user keeps and filters the rows, it usually passes 25 people, and the post steps below can't go in a Function. Keep the table thin: logic that repeats (resolve, score) goes in a Function called by one `run-function` column. Never copy a Function's steps into table columns.
- **Not Function steps:** company and person posts, post reactions, post comments and live professional profiles (`enrich-professional-profile`). They stay table columns (`execution_mode: "managed"`) or capabilities.

Pick the source:

| Source | Input |
|---|---|
| Specific posts | Post URLs (`https://www.linkedin.com/posts/…`) |
| A company's recent posts | Company LinkedIn URL. Pick the posts with the most engagement. |
| A person's recent posts (founder, influencer, competitor exec) | Person LinkedIn URL |
| An event | The guest list as a CSV (from Luma or the event tool). Start at Step 3. |

## Step 1: Get the posts

- **Company posts:** `professional-company-posts` (company LinkedIn URL). It returns recent posts with `url`, `postedAt`, `reactionsCount`, `commentsCount` and `text`.
- **Person posts:** `professional-person-posts` (profile URL).
- Show the posts by engagement and let the user pick 1 to 10. Topic matters more than volume; a post about the problem you solve beats a holiday post.

These run on the professional-network provider (`professionalNetwork`), so they are table columns or capabilities, never Function steps. Use the two routes in Step 2: the capability (`run_capability`) if the provider is set up, else a scratch table `Engager sources · <date>` (`autoplay: false`) with a `Company URL` or `Profile URL` column and a column for `professional-company-posts` or `professional-person-posts` with `execution_mode: "managed"`. As a capability, it needs the user's own key or Loopster's account saved as that provider's default (ask first). Price the post pull (the `cost` in `list_capabilities`, or `estimate_trigger_cost` for a column, × the number of companies or people), ask with the pricing sentence, and send `maxCostUsd` and an `idempotencyKey`, as in Step 2.

List prices from `list_capabilities` (read the live `cost` before you quote):
- company posts: about $0.04 listed;
- person posts: $0.006 at the default of 50 results (billed per page of 25 results);
- one post's reactions or comments: about $0.04 listed at the default limit of 25 (billed per item returned);
- profiles: $0.0015 per person.

**Volume:** the reactions and comments columns take a `limit` setting (about 25 by default) and bill per item returned, so a higher `limit` pulls more people and costs more. Read the setting with `get_column_template` before raising it. Commenters are the warmest and say the most, so favour posts with comments. Set the expectation up front: 3 posts typically give 50 to 90 people before filtering.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Step 2: Pull the engagers

Pick the route:

- **Capability route, when the provider is already set up.** If the user's own key for the `professionalNetwork` provider is connected, or Loopster's account is already saved as that provider's default (`list_connections`, `list_provider_defaults`), run `professional-post-reactions` and `professional-post-comments` with `run_capability` on the chosen post URLs. No scratch table is needed.
  - Read the inputs and `cost` in `list_capabilities`, and price it (cost × posts).
  - Send `maxCostUsd` and an `idempotencyKey`. Run 1 post first, then the rest.
  - Poll `get_run` until `status` is not `running`, then read each item's `output` with `list_run_items`.
  - Save the items to a CSV as soon as the run finishes: capability results stay readable for a while only.
  - Never change a provider default without asking.
- **Table route, otherwise:**
  1. Create a small table, `Engager sources · <date>` (blank, `autoplay: false`), with a `Post URL` column. Insert the chosen post URLs.
  2. Add two columns, each with `execution_mode: "managed"`:
     - `professional-post-reactions`, reading `Post URL`;
     - `professional-post-comments`, reading `Post URL`.
  3. Price with `estimate_trigger_cost`, ask, then `trigger_rows` with `maxCostUsd` and an `idempotencyKey`, poll `get_run` until it is not `running`, and read the cells with `list_rows`.

Either way, each result holds `items[]`:
- reactions: `reactionType`, plus `person` (name, profile URL, headline);
- comments: the comment text, plus person details.

## Step 3: Build the people table

1. Create `Engagers · <source> · <date>` (blank, `autoplay: false`) with columns:
   - `Name`
   - `LinkedIn URL`
   - `Headline`
   - `Post`
   - `Engagement` (reaction type or "comment")
   - `Comment`
   - `Times engaged`
2. Insert one row per engagement first, from the Step 2 cells or CSV. Merging comes after Step 4, because the same person can appear under different URL forms (member id vs vanity handle).
   - For an event list, map its columns (name, email, company, title).
   - Guest lists usually have emails, not LinkedIn URLs, so add `loopster-data-email-to-linkedin` (free) as a column, then fill the `LinkedIn URL` column with a Formula that returns the URL when the lookup found one and stays empty when it returned `{"found":false}`. Don't rely on an empty cell to stop a later column. Run Step 4 only on rows that have a URL by passing their `rowIds`, or set a `runCondition` on the Step 4 columns with `update_column` that parses the email-to-LinkedIn column and tests `found`.
3. **Remove noise before spending:**
   - your own employees (headline or company names your company);
   - the post author's own employees, when it's a competitor's post (the user can choose to keep them);
   - do-not-contact matches;
   - obvious non-buyers by headline (students, recruiters, "open to work"), unless the user wants them.

## Step 4: Resolve who they are now

Order: free lookup for everyone (the Function, or the columns), live lookup only for the misses, then the `Resolved` columns, then the merge.

Engager profile URLs often use member ids (`/in/ACoAA…`), not vanity handles.

**Reuse first.** If a Function that does this exists (Before you start), use it instead of building columns:
1. Add one `run-function` column calling it, with its LinkedIn URL input mapped (`mode: "column"`) to `LinkedIn URL`. Read the input ids and output keys with `get_function` (column settings: `references/choosing-the-surface.md`, section 4).
2. Price it from the Function: `get_function` `costEstimate.maxUsdPerRun` × the rows. Use this figure for the quote and the big-spend check. Run 1 row, then 10, then the rest (100 at a time for a longer list), and read `get_wallet` `consumedUsd` before and after each batch. Compare each batch's real cost with its quote; if a batch costs more than 1.5 times its share, stop and ask.
3. Read one cell with `list_rows` to see how each output is stored. Then pull the vanity URL, current title and company domain into their own columns, one per output: use a Formula that parses the cell and then parses the output (the cell is a JSON object whose outputs are each JSON text, so two parses; if an output turns out not to be JSON, wrap that second parse in try/catch and fall back to the text), or, for an output that holds JSON, a field reference whose `path` is `["<output key>", "<field>"]`, encoded as in the build route below.

**If none exists, build the columns first:**
1. Add `loopster-data-enrich-person`, reading `LinkedIn URL`. It's free, and resolves some member ids to a profile with vanity URL, current title, company and website.
2. Pull out the vanity URL, current title and company domain with three Formula columns, using a field reference. `@{ref:v1:<data>}`, where `<data>` is the base64url (no `=` padding) of `{"columnId":"<profile column id>","source":"value","path":["company_website"]}`. Use one field reference per Formula.
3. Write each Formula so it always returns a value: set `optionalMentions` on it with `update_column` so an empty field gets through, and return the text `not found` when the field is empty.

**Then, on either route:**
1. For rows where the vanity URL is `not found`, add `enrich-professional-profile` with `execution_mode: "managed"` (a live profile, $0.0015). It can't be a Function step, so it stays a table column. Price it, ask, and run only on those rows (pass their `rowIds`). Pull the same three fields from it with their own Formula columns, each returning `not found` when its field is empty.
2. Add a Formula column `Resolved URL` that returns the free profile's vanity URL, or the live profile's when the first is `not found`. Set `optionalMentions` on it so a blank live-profile cell gets through. Do the same for `Resolved title` and `Resolved company domain`. Read Step 5 and the merge from these three columns.
3. **Now merge:** group rows by `Resolved URL`. Keep one row per person, with `Times engaged` set to the number of different posts they engaged with (a reaction and a comment on one post count once), and the post names and comment text joined into `Post` and `Comment`. Leave rows whose `Resolved URL` is `not found` as separate rows. The merge is table editing and stays in the table.

**After a column build, save it as a Function.** Offer it in one line. Building is free, and publishing needs its own yes (house rules, section 4b):
- Follow `function-builder`, from a working table: `create_function` with `fromTable`, `columnIds` the enrich-person column and its three Formula columns, and `outputColumnIds` the three Formulas (vanity URL, current title, company domain), titled `Current profile · Loopster skill` (check `list_functions` for that title first). Leave the raw profile out of the outputs: it is large. The live-profile column stays in the table.
- Write the new draft's `functionId` into the "Functions" section of `loopster-context.md` straight away.
- Dry-run the publish, show the contract, and ask before publishing and before opening it to agents.
- Then run the Function with `run_function` on 3 rows from the table, including one the free lookup missed. Its steps are free, so there is no price to quote; read `get_wallet` `consumedUsd` before and after to confirm. Compare with the columns' values. A miss should give `not found`.
- This table keeps its columns. Next time use one `run-function` column calling it. On a scheduled or Auto-run table, every firing or inserted row bills the Function (a schedule re-runs every cell unless you send `cells: "empty"`), so price it per month, include it in the big-spend check (house rules, section 4c), and ask before you create the schedule or turn Auto-run on.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Step 5: Keep the fits

Score against the ICP:
1. **If a scoring Function exists** (Before you start), add one `run-function` column calling it. Map each of its inputs from the matching column (read the input ids with `get_function`; column settings: `references/choosing-the-surface.md`, section 4). If it needs an input this table has no column for, use item 2 instead.
   - Price it and run 1 row, then 10, then the rest (100 at a time for a longer list), as in Step 4. Compare each batch's real cost with its quote; if a batch costs more than 1.5 times its share, stop and ask.
   - Read one cell with `list_rows`, then pull the tier into its own column the same way as in Step 4. Read the output key with `get_function`: it is `tier` for the standard Function. Sort on that column. Say which scale the Function uses.
2. **If none exists, build the column first:** an AI column returning `{"tier": "A|B|C", "reason": "…"}`, reading the ICP context and the `Resolved title` and `Resolved company domain` columns.
   - Price it with `estimate_trigger_cost` (an AI column's real cost can be 3 to 4 times its estimate) and ask with the pricing sentence. Then `trigger_rows` with `maxCostUsd` at the agreed amount and an `idempotencyKey`, on rows whose `Resolved title` is not `not found` (pass their `rowIds`): 1 row, then 10, then the rest.
   - Once it works, save it as a Function the way Step 4 does: `create_function` with `fromTable`, the AI column as the step and as the output, titled `ICP tier · Loopster skill` (check `list_functions` for that title first). Record its id in the "Functions" section of `loopster-context.md` straight after `create_function`, as in Step 4.
3. **`score-prospect`, only when the user asks for it.** It uses the ICP context, is priced by use (measure 10 rows for the real cost) and can't be a Function step, so it stays a table column. Trigger it with `allowUnpriced: true` and `maxCostUsd`, and know the cap doesn't cover it. It returns `Tier 1`, `Tier 2`, `Tier 3` or `Not a fit`; map them to A, B and C with a Formula so the sort works the same way.

Engager lists are small (50 to 90 people), so 1, then 10, then the rest in one batch is enough. For a longer event guest list, run the rest 100 at a time.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Sort tier A first, then by `Times engaged`. A `Times engaged` of 2 or more is a warm signal; say so.

## Hand off

Go to `contact-finder` for emails (it runs the "Find work email · Loopster skill" Function), or straight to a LinkedIn sequencer (HeyReach needs only the LinkedIn URL and name), then `outbound-launch`.

The angle is the topic, not the click. Good: "Your comment on <author>'s post about forecast accuracy stuck with me: …". Bad: "I saw you liked a post."

## Show the result

Write the sorted rows to a CSV from `list_rows` (house rules, section 10) and give the path.

```
Engagers · Acme pricing post · 2026-10-25   (3 posts, real cost $X.XX)
  Pulled 112 engagements → 87 unique people
  Removed: 24 own team · 6 competitor staff · 3 do-not-contact · 9 non-buyers
  Resolved 45 of 45 (38 free, 7 live profile)
  ICP tier: A 11 · B 14 · C 20 · repeat engagers 6
  Saved: ./engagers-2026-10-25.csv   (and the table "Engagers · Acme pricing post · 2026-10-25")
```

Report the real spend as `get_wallet` `consumedUsd` now, minus the value you noted at the start. It includes Function spend; in a shared workspace, other people's runs can add to it.

Then add the pricing sentence:

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## If something goes wrong

- **400 "runs on your own professionalNetwork account":** you used the capability. Use a table column with `execution_mode: "managed"`, or ask to save Loopster's account as the default for that provider.
- **400 when you add a post, reaction, comment or professional-profile step to a Function:** those aren't Function steps, and nothing is stored. Use a managed table column or a capability for them, and pass their text into a Function as an input if it needs it.
- **Reading a `run-function` cell:** it holds a JSON object of the Function's outputs, each itself JSON text. Read the output keys with `get_function`, and pull a field with a Formula that parses twice.
- **Fewer reactors than the post shows:** each call returns about 25 reactors. Note the count you got, don't promise the full list, and lean on commenters.
- **Huge cell values:** read only `items[].person` and the comment text, and never paste whole cells.

## enrich-accounts

Fill in company fields (industry, employee count and range, revenue range, location, founded year, LinkedIn page) for a list of companies in one step, from the free Loopster Data company lookup. Use when someone asks to add industry, size or location to these domains or companies, quickly and for free. For paid fields (tech stack, open roles, funding, news), people, or a mix, use enrich-list.

# Enrich accounts

One step: the free company lookup over a list of companies. For paid fields, people or a mix, use the `enrich-list` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Keys.** Domains match best (not `linkedin.com`, a parent group or a link shortener). Names without domains: find the domain with `search_companies` (`name`, free) and confirm on location or size.
2. **One call:** `loopster-data-enrich-company` with all domains (`run_capability`, up to 1,000 inputs, `maxCostUsd: 0`), or one column on the user's table run with `trigger_rows`. Never one call per domain.
3. **Keep the fields asked for:** name, industry, employee count and range, revenue range, HQ, founded year, LinkedIn URL (`references/data-routes.md`).
4. **Report** the fill rate per field and the domains not found. Save a CSV next to the original, or the columns in the table.
5. Fields this lookup doesn't have (tech stack, jobs, news, funding): say so and offer `enrich-list`, which prices them.

## Does not claim

- That a field is current: say the source.
- A value for a company not found: leave it empty, never guess.

## enrich-list

Add data to a list of companies or people (a CSV, a pasted list, a Loopster table or one record), such as industry, headcount, HQ, LinkedIn URLs, job titles, tech stack, funding, open roles, or website summaries, using free Loopster Data first and the cheapest paid source only where needed. Runs once with no table, or as a reusable Function when the same enrichment will run again. Use when the user says "enrich this list", "add industry and size", "fill in the LinkedIn URLs", "find their LinkedIn profiles", "get the latest LinkedIn profile", "what is their current job or title", "what tech do these companies use", "add funding", "add open roles and news", "enrich every new batch of leads", or uploads a CSV and asks for more columns. For emails and phone numbers use contact-finder.

# Enrich a list

## What you get

The user's list back, with the new fields added, a fill rate for each field, and the real cost. It comes as a CSV, or as new columns if the list lives in a Loopster table. If the job will run again, it also comes with a reusable Function, so the next list is one call.

## Before you start

Read `references/house-rules.md`. Then:

1. **Find the keys in the list:**
   - for companies, a domain or website, else the company name;
   - for people, a LinkedIn URL, else an email, else name + company.

   Clean them first:
   - domains to `example.com` (no `www`, no path);
   - LinkedIn URLs to `https://www.linkedin.com/in/<handle>`;
   - trim spaces and drop empty rows.
2. **Ask which fields they want.** Offer the common set from `references/data-routes.md` as a default.
3. **Ask how many rows.** Assume the job will run again if they say weekly, monthly, "every new batch" or "new leads", or if another play uses the same fields. Ask only when it is unclear.
4. **Look for a Function that already returns the fields:** the "Functions" section of `loopster-context.md`, then `list_functions`. Reuse it instead of building a copy (house rules, section 7).

## Pick the surface

Any job that will run again goes in a Function. Rows 1 and 2 say how the work runs: take the one that fits. Rows 3 and 4 then say where the rows live and what a Function can't take. Check both and apply each one that fits. A repeating job with 300 rows is row 2 for the logic and row 3 for the rows.

| Situation | Surface |
|---|---|
| One action per field, once, never repeated (up to 1,000 rows a call) | `run_capability` per field, no table. |
| They will run it again (weekly, every new batch, or another play uses the same fields) | A Function: reuse one that returns the fields, else build it (see "If you run a Function"). `run_function` for up to about 25 inputs. For more than that, also use row 3. |
| The user wants the rows in Loopster (to open, filter, share or keep), you need to keep results for more than about 25 inputs, it pushes to a CRM, sequencer or Slack, or it runs on a schedule | A table: a blank table with `autoplay: false`, `insert_rows`, then **one `run-function` column** for the Function's logic. For a one-off, template columns from `references/data-routes.md` are fine. A one-off field with several steps (look up, then AI summary) is template columns in a table. Never copy a Function's steps into columns. |
| A field uses a professional-network provider source (live profile, headcount, open jobs second source, posts) | A table column with `execution_mode: "managed"` for that field only, next to the `run-function` column. A capability needs the user's own key or Loopster's account saved as that provider's default. |

Size alone is not a reason for a table when one capability does the job: it takes up to 1,000 inputs a call. A Function keeps no list you can page through, so more than about 25 inputs to keep means a table.

**A big file** (more than about 10,000 rows, up to 50 MB): load it into the table with `create_upload_link` and `import_file`, not `insert_rows` (house rules, section 10b). The import is free and starts no enrichment. Then price and run the enrichment in batches of `rowIds` (house rules, sections 4 and 5).

## Steps

1. **Free pass.**
   - Run the free Loopster Data action for every row that has the key: `loopster-data-enrich-company` (domain) or `loopster-data-enrich-person` (LinkedIn URL). As a capability, use `maxCostUsd: 0`.
   - One call returns many fields at once. For companies: name, industry, employee count and range, revenue range, location, founded year, LinkedIn URL. For people: current title, seniority, company, company website, location, role start date.
   - If the job repeats, these lookups are the first steps of the Function (see "If you run a Function").
   - Report the hit rate.
2. **Map what's still missing.** For each field the user wants, count the rows that are still empty after the free pass. Pick the source from `references/data-routes.md`, cheapest first. Never reach for an AI web research column (`ai-web` "Loopgent", `find-linkedin-url`, any `-web` model) while a data route is left untried (house rules, section 3).
3. **Price it.**
   - Show a small table: field · rows still empty · source · price per row · total.
   - A capability's total is list price × rows, a ceiling.
   - A Function's total is `costEstimate.maxUsdPerRun` × inputs. Every paid step in it runs for every input, and AI steps are priced by use, so call that figure a floor when the Function has an AI step. Add the AI cost measured on 10 inputs, or 4 × its estimate until you have measured.
   - A table's columns: `estimate_trigger_cost` with the exact `rowIds` and `columnIds`. Quote a `run-function` column from its Function: `costEstimate.maxUsdPerRun` (from `get_function`) × the rows, plus any usage-priced step measured on 10 rows. Use this figure for the quote and the big-spend check.
   - An AI web research column (the user named one, or it is the only route left): say it is an AI web agent. If its price is per use (an estimate, not a fixed price per row), don't quote it from the estimate: run it on 3 rows first with `maxCostUsd`, without asking (the user's request covers the test), read the real cost with `get_usage`, and quote the rest from that. A fixed price per row is exact: quote it as it is, and offer the 3-row test only to judge the answers.
   - Ask which fields are worth it. If the total is a big spend (house rules, section 4c), ask in that exact shape, whatever permission mode the tool is in.
   - End with the pricing sentence.
4. **Test, then run.** Run the chosen sources on 1 row, then 10. Show the values and the hit rate, so the user can judge quality before paying for the rest. Then run the rest the way the surface allows:
   - **Capability:** `maxCostUsd` and an `idempotencyKey`, in batches of up to 1,000.
   - **Function:** `run_function` takes no `maxCostUsd`. Send an `idempotencyKey`, run 100 at a time, and read `get_wallet` `consumedUsd` before and after each batch. Compare it with the quote, and stop and ask if a batch costs more than 1.5 times its share.
   - **`run-function` column:** price it from the Function (`get_function` `costEstimate.maxUsdPerRun` × the rows). Use this figure for the quote and the big-spend check. Run 1 row, 10 rows, then 100 rows at a time, reading `get_wallet` `consumedUsd` before and after each. Stop and ask if a batch costs more than 1.5 times its quote.
   - **Template columns** (provider, professional-network and AI columns): `trigger_rows` with `maxCostUsd` and an `idempotencyKey`. For AI columns the cap checks only the pre-run estimate, so read the real cost after the first 10 rows.
   - A big spend needs its own yes first, on every surface.
5. **Merge.**
   - Keep the user's original columns and order, and add the new fields on the right.
   - Leave a cell empty when nothing was found; never invent a value.
   - Keep a `source` note per field if the user asks where values came from.
6. **Save.**
   - **Capability run:** the CSV next to the original (`<name>-enriched-<date>.csv`).
   - **Function run:** write each `get_function_run` answer into the CSV as you read it, matched to its input row by the item `index` in the `run_function` answer. Save the file when the last one is in. Don't rely on reading the run again later.
   - **Table:** confirm the new columns, and for more than 20 rows write the CSV from `list_rows`.

## If you run a Function

**Reuse first.** Read `get_function` for its input ids and output keys, then run it.
- Work emails: `Find work email · Loopster skill` (the `contact-finder` skill runs it). For mobile numbers and personal emails, hand off to the `contact-finder` skill.
- Open roles and recent news from a company domain, as the strongest recent signal plus a one-line opener: `Why now · Loopster skill`. It takes the company domain, and its output `why_now` is JSON text. Use it when the user wants a reason to reach out, not raw lists of roles or news. Read it with `get_function` first. Its title keywords, 90-day window and ICP context are fixed inside it, so if they don't fit this user, build a variant with the `function-builder` skill (see `signal-outbound`).

**Run it.**
- Up to about 25 inputs: `run_function` with inputs keyed by input id. For a list, poll `get_run` with the batch `runId`, then call `get_function_run` for each item, using its `rowId`.
- More than that, or whenever the rows must live in Loopster: a table with one `run-function` column (settings in `references/choosing-the-surface.md`).
- A Function can be refreshed on a schedule through a table's `run-function` column. Create the schedule paused, send `cells: "empty"` to run only new rows (or price every firing), and resume only after a yes. A schedule expected to cost over the big-spend limit a month is a big spend (house rules, section 4c).

**Build one if none fits.** The first build uses steps you have already tested as table columns:
1. Put the first rows in a table (the user's own, or a scratch one) with `autoplay: false`. Add each source from `references/data-routes.md` as a column, free first. For a source marked "capability", read the template with the same id using `get_column_template` (any table id) to confirm it exists and to see its settings. Run 1 row, then 10, as in step 4.
2. Once the values are right, turn the working columns into a Function with the `function-builder` skill: `create_function` with `fromTable`. Name it `<Job> · Loopster skill`, for example `Enrich company · Loopster skill`.
3. Record its id in the "Functions" section of `loopster-context.md`, and tell the user its name and where to find it.
4. If the rows live in a table, add one `run-function` column and run it only on rows the old columns have not filled yet, so nothing is bought twice. Delete the old columns only after the user agrees and the results are saved to a CSV. From then on, reuse the Function.

Publishing it and opening it to agents each need a yes (house rules, sections 4b and 6).

**What goes in it.** Loopster Data lookups, PredictLeads, AI Ark, Aviato, Wiza, FullEnrich, BetterContact, Reverse Contact, AI steps and Formula steps. The "Function step?" column in `references/data-routes.md` shows each source. Professional-network provider sources, email checks and CRM, sequencer and Slack actions stay table columns next to the `run-function` column. Return only outputs that always get a value or are skipped by a run condition, and return a summary rather than a large raw result.

**Free first.** Every step in a Function runs for every input. To keep the paid steps for the misses:
- give a paid step a run condition, so it runs only when the free step found nothing: set it with `update_column` on the table column, test it on a few rows, then `create_function` with `fromTable` (`function-builder` shows how); or
- keep the free steps in one Function, and put the paid steps in a second one that you run only on the misses.

If the job will run again, keep the free steps in their own free Function, which costs nothing because every step in it is free. Use a capability with `maxCostUsd: 0` only for a one-off free pass.

## LinkedIn profiles and current jobs

The most common request, and the easiest to overpay for. Follow this order:

1. **No LinkedIn URL yet:**
   - with an email, run `loopster-data-email-to-linkedin` (free);
   - with name + company, run `search_people` with `personName` and `specificCompanies` (free). Batch about 25 names and their companies per call. Accept a match only when the company matches too, and flag people with two profiles at the same company, or with only an initial for a surname.
2. **Latest profile** (current company, title, role start date): `loopster-data-enrich-person` on the URL (free). Its profiles refresh about every 55 days.
3. **Paid steps only for the rows steps 1 and 2 missed.** Price them on those rows and offer them first:
   - URL still missing: `surfe-find-profile` ($0.0127) or `icypeas-email-to-linkedin` ($0.0325);
   - no profile from step 2: live profile, `enrich-professional-profile` ($0.0015) as a table column with `execution_mode: "managed"`.

   "Latest" in the request is not a reason to re-check rows step 2 answered. Offer a live check of those rows only if the user asks for today's data, as a separate option after the misses, with its own price.
4. **AI web research only for what's left.** Tell the user how many rows that is. Then run it on 3 of those rows yourself, with `maxCostUsd`: the user asked for this job, so their request covers the test (house rules, section 3, "Measure first"). Read the real cost with `get_usage`, and only then ask for the rest, quoting the measured figure in the big-spend shape (section 4c).

For 2,000 people, steps 1 to 3 cost nothing if the free steps answer every row. If every row misses, the ceiling is about $28 by name + company (Surfe plus a live profile) and about $68 by email (Icypeas plus a live profile).

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

**If this will run again:**
- Steps 1 and 2 are free Loopster Data lookups (`loopster-data-email-to-linkedin`, `loopster-data-enrich-person`), so they go in a Function. Reuse one first, else build it as above.
- Step 3's live profile is a professional-network provider source, which a Function can't take. Keep it as a managed table column next to the `run-function` column.
- `search_people` for name + company is a search. Keep it a search, and pass its results to the Function or the table.

## Show the result

```
Enriched 480 companies
  Field          Filled   Source
  Industry       451 94%  Loopster Data (free)
  Employees      447 93%  Loopster Data (free)
  Tech stack     398 83%  PredictLeads   $X.XX
  Open roles     212 44%  PredictLeads   $X.XX
Real cost: $X.XX   Saved: ./accounts-enriched-2026-10-25.csv
```

Take the real cost from `get_wallet` `consumedUsd` before and after the play, which includes Function spend. Then add the pricing sentence:

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Suggest a next step: `prospect-list` to find people at these companies, `signal-outbound` to find which ones to contact now, or `crm-manager` to write the fields into the CRM. If you built or reused a Function, name it and say that the next list runs with one call.

If the user said the list grows ("we add new accounts every week"), end by offering a paused weekly schedule on the `run-function` column with `cells: "empty"`, so only new rows run. Don't suggest Auto-run for rows added in batches; it's for rows that must run the moment they arrive, such as an inbound webhook. Ask before creating the schedule, and again before resuming it.

## Reading results

- A capability item's `output` is JSON text. Parse it; `{"found": false}` means no record.
- A Function's answers come from `get_function_run`, one call per input. Its output values are text (an output whose step is shaped as a number is a JSON number): parse the JSON ones, and say "not found" for blank or `{"found": false}` outputs.
- A `run-function` cell holds a JSON object of the Function's outputs, each itself JSON text. Pull a field out with a Formula that parses twice, or a field reference with `path: ["<output key>", "<field>"]`. `get_function` lists the output keys.
- Some outputs are large (company posts, full profiles, news). Keep only the fields the user asked for; never paste the whole output.
- When a value conflicts between sources, prefer the newer one (`last_updated`, `scrapedAt`) and say so.

## If something goes wrong

- **Many companies not found:** check the domains are the company's own (not `linkedin.com`, a parent group, or a link shortener). For names without domains, find the domain first by searching Loopster Data (`search_companies` with `name`, free), and confirm the match on location or size before using it.
- **A paid source is refused for "no account":** it needs the user's key, or Loopster's account saved as that provider's default. Ask before `set_provider_default`.
- **The CSV has odd encoding or merged headers:** clean it first and confirm the column mapping with the user before running anything paid.
- **A Function call is refused:** read the status and message, then see "If something goes wrong" in the `function-builder` skill.

## fewer-requests

Do the same Loopster work in fewer API requests. Every Loopster MCP tool call is one request against the workspace's per-minute and per-day limits, so this skill plans the calls first, then searches with full pages, imports search results instead of copying them, writes and runs in bulk, waits on the cheap status call, and reads only the rows it needs. Use for any Loopster task that will take more than a few tool calls (searching, loading rows, running columns, waiting for a run, reading results, finding failed rows, fixing cells), near a request limit, or after a 429 "too many requests" answer.

# Fewer requests

Every Loopster MCP tool call is **one API request**, the same as the REST call behind it. Requests count against the workspace's limits per minute and per day, which depend on the plan:

| Plan | Per minute | Per day | Calls that can start paid work, per minute |
|---|---|---|---|
| Launch | 500 | 5,000 | 60 |
| Scale, trial | 2,000 | 30,000 | 240 |
| Unlimited | 5,000 | 150,000 | 600 |

The calls that can start paid work are `trigger_rows`, `update_cells`, `update_row`, `run_function`, `run_capability`, `create_table` from a paid starter, and `insert_rows` on an Auto-run table.

The goal is **the same result in fewer calls**. Never trade a correct result, or a step the house rules require (price, ask, one then ten then all), for a saved request. Read `references/house-rules.md` once per session.

## Before you start: count the calls

Write the plan as a list of calls and count them. For every loop in it ("for each row…", "until it's done…"), ask whether one call can do the whole loop. The rules below are the usual answers.

## 1. Search with full pages, and import instead of copying

- **Ask for the page you need,** up to `limit: 50`. Leave `limit` out and the first page is 25 and every later page only 10, so a crawl takes up to five times the calls.
- **Next page:** send `searchId` and `cursor`, not the filters again.
- **Only need the count?** Read `approximateTotal` from the first page (prospect-list, step 2). Never page through to count.
- **Results into a table:** `create_table` with `type: "search"` and the `searchId` imports the whole result in one call, free. Don't page the search and `insert_rows` the pages.
- **Many named people or companies:** one `search_people` with `specificCompanies` (up to 1,000 values) and `perCompanyLimit`, not one search per company. For names, batch about 25 names and their companies per call (house rules, section 3b).

Bad: 20 `search_people` calls with no `limit` to collect 200 people, then 4 `insert_rows` calls.
Good: 1 `search_people` with `limit: 50` to see the first page and get the `searchId`, then 1 `create_table` with `type: "search"`.

A later page refused with 422 (the search took too long) is fixed with a smaller `limit`. That costs calls, so go down only as far as needed.

## 2. Write in bulk

- **Rows:** `insert_rows` takes up to 25,000 rows a call; send batches of 10,000 or fewer. Above about 10,000 rows, load a file instead (house rules, section 10b): one link, one upload, one `import_file`.
- **Cells:** one `update_cells` call for many rows, not one `update_row` per row.
- **Columns:** one `create_columns` call for several columns, not `create_column` for each.

Bad: 300 `update_row` calls to fix one wrong value in 300 rows.
Good: 1 `update_cells` call with the 300 row and column pairs.

## 3. Run in one call

- **Table columns:** one `trigger_rows` runs up to 10,000 rows. Send every `rowId` that needs the run, and the `columnIds`, in one call (tools map: never leave them out). Price it first with `estimate_trigger_cost`, which is one call for the whole run.
- **No table:** `run_function` and `run_capability` take up to 1,000 inputs in one call and return one `runId`.
- **Rejected rows:** if a trigger reports `rejected` rows, call again for those rows only. `deduplicated` and `waiting` rows need nothing.
- **Don't edit cells only to make Auto-run start them,** and never trigger row by row.

The one-then-ten-then-all rule (house rules, section 5) still applies. That's three or four runs for the whole job, not one per row.

Bad: 2,000 `trigger_rows` calls, one per row.
Good: 1 `estimate_trigger_cost`, then runs on 1 row, 10 rows and the rest: 4 calls in all.

## 4. Wait on the cheap call

- **Poll `get_run`** with the `runId`, every 10 seconds or more. Its answer is cached for 5 seconds, so polling faster returns the same answer and spends requests.
- **Not counted against the daily limit** (they still count per minute): `get_run`, `list_run_items`, `get_job`, `get_export`, `get_wallet`, `get_usage`.
- **Counted against the daily limit:** `get_status`, `list_rows`, `get_row`. Use `get_status` for the whole table's picture once, not as the loop you wait in.
- **Long runs from an integration:** a webhook on `run.settled` replaces polling altogether.

Bad: `get_status` every 2 seconds for 5 minutes: 150 calls, all against the daily limit.
Good: `get_run` every 15 seconds: about 20 calls, none against the daily limit.

## 5. Read only what you need

- **Pages:** `list_rows` takes `pageSize` up to 500 (default 50). On a wide table, keep it at 100 or less: a large page can come back short and say so in `warnings` (house rules, section 9).
- **Columns:** ask only for the `columns` you need.
- **Let the server filter** with `filter` (for example `isEmpty` on a column), instead of reading every row and filtering yourself. Filters on Formula columns can give wrong counts, so filter on the column the Formula reads instead.
- **Failures of a run:** `list_run_items` lists each item's state, 100 a page. Then `get_row` only for the failed rows whose error you need.
- **Second look at a table:** `updatedSince` reads only the rows changed since a time.
- **A whole table:** `export_table` is one export and one download, not dozens of pages (house rules, section 10).

Bad: read a 5,000-row table at 50 a page (100 calls) to find the 12 rows that failed.
Good: 1 `list_run_items` call for the run, then `get_row` on those 12.

## 6. Keep what you were given

Keep and reuse what earlier calls returned: table and column ids, a `searchId`, the `rowIds` an insert returned, a run's `runId`, a Function's id and inputs. Ask again only when the data can have changed since. The big catalogs (`list_search_filters`, `list_capabilities`, `list_column_templates`) are large answers: read each once per session.

- **Wallet only around paid work.** `get_wallet` before and after is for measuring real spend. A free job (search, import, cell edits, a run priced at zero) needs neither read.
- **Check a result with counts, not by reading it back.** The answer of the write call, or one `get_status` (row and cell counts), confirms it. Don't page or export a table you just wrote only to look at it.
- **One trigger per run.** `trigger_rows` answers with a `runId`: poll that. Don't send the same trigger again unless the answer said `rejected` rows or 503 `nothing_started`.

Bad: after inserting 200 rows, `list_rows` at 50 a page (4 calls) to find their ids and check they landed, then `list_columns` again before the run.
Good: take the `rowIds` and the count from the `insert_rows` answer and the column ids from the call that created them, then `trigger_rows` with both: no extra reads.

## 7. After a failure: wait or fix, never repeat blindly

- **429:** wait the `Retry-After` seconds before the next call, and longer on repeats. `X-RateLimit-Scope` says which limit ran out. Quick retries only collect more 429s.
- **400 or 422:** the same request fails the same way. Change it; never resend it unchanged (house rules, section 11).
- **401, or an invalid key:** a retry won't fix it. Stop and follow `loopster-setup`.
- **503 `nothing_started` on `trigger_rows`:** nothing ran. One retry after a few seconds is right.

Bad: a 429 answered with the same call again at once, five times: five more requests, five more 429s.
Good: wait the `Retry-After` seconds, then send the call once.

## Report

Your final message always ends with this line, as its very last line (after any list of changed files), also when you stop to ask a question:

Loopster tool calls: <N>

N is the number of Loopster MCP tool calls you made in this task, counted from your own calls (not an estimate). If the task came near a limit, say which one in the line before it.

## function-builder

Turn a job someone repeats into a reusable Loopster Function, a one-call tool with named inputs, steps (AI, Formula, waterfalls, PredictLeads, Loopster Data and other provider actions) and named outputs, that runs on one record or a list of up to 1,000 with no table, from any AI agent or the API. Designs it, builds it (in a sandbox, or from tested table columns), tests it on samples, publishes it, opens it to agents, and documents how to call it. Also edits, republishes, retires and restores Functions. Also puts a Function into a table as one run-function column, so tables stay thin. Use when the user says "make this reusable", "build a function that…", "I do this every week", "we'll run this again", "turn this into a tool", "edit my Loopster function", or when a play needs a Function that does not exist yet. Any job that will run again belongs in a Function (house rules, section 7).

# Function builder

## What you get

A published Function in the user's workspace, for example "Why now · Loopster skill" or "ICP tier · Loopster skill":
- It is tested on real samples.
- It is open to agents.
- It comes with a short note on how to call it.

Anyone on the team can run it from Loopster, an AI agent or the API.

## Before you start

Read `references/house-rules.md`. Then look for a Function that already does the job: the "Functions" section of `loopster-context.md` (with `get_function` on each id, drafts included), then `list_functions` (published and open to agents only). Offer to reuse or edit it instead of building a duplicate.

## Step 1: Design it with the user (no calls yet)

Write the design out and get a yes:

- **Title and description:** use `<Job> · Loopster skill` when a play builds it, or the user's own name. Put the purpose, the skill and version, and "safe to edit in Loopster" in the description.
- **Inputs:** the fewest that do the job, each with a header and required true or false. Use keys people already have (domain, LinkedIn URL, name + domain).
- **Steps:** each one with its template and what it reads. Steps read inputs and earlier steps by mentioning their id as `@{id}`. AI prompts can embed workspace contexts as `@{ctx:<id>}`. Recipes are in `references/step-recipes.md`.
- **Every step runs for every input.** Only the email waterfall step stops at its first hit. If a paid step should run only when a free step found nothing, give it a run condition (below), or make two Functions and run the paid one only on the misses.
- **Outputs:** only what the caller needs, and only steps that always produce a value or are skipped by a run condition. Large raw outputs (news lists, full profiles) make every run's answer huge; return an AI summary or a Formula extract instead.
- **Cost per run:** the sum of every step that runs. AI steps are priced by use.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Steps that can be added over the API:
- AI columns, Formula and `waterfallEmail`;
- provider actions from Loopster Data, PredictLeads, AI Ark, Aviato, Wiza, FullEnrich, BetterContact, Reverse Contact, Surfe, Icypeas and Hunter (email finders) and ClearoutPhone.

Not Function steps (the API refuses them by name, and nothing is stored): CRM, sequencer and Slack actions; email checks (ZeroBounce, Findymail, Icypeas verify); LinkedIn steps from the professional-network provider (live profiles, posts, post reactions and comments, company headcount, open jobs); `score-prospect` (use an AI step that returns a tier and a reason instead). Keep those as table columns next to a `run-function` column (Step 5).

**Steps that run only sometimes.** Run conditions are set on table columns, so a Function with one is always built table first (Step 2). To run a step only when an earlier one found nothing:
1. build those steps as columns in a scratch table (`autoplay: false`);
2. set the condition with `update_column` and `runCondition`, for example `{"enabled": true, "description": "Only when no phone was found", "condition": "(() => { let r = @{<phone column id>}; try { r = JSON.parse(r); } catch (e) { r = null; } return !(r && r.found && r.phone); })()"}`;
3. read one real cell of the earlier column and use its field names in the condition, not the ones in the example. Then test on a row that found a value and a row that found nothing: the first must show the step skipped (a skipped cell says the condition wasn't met), and the second must run;
4. `create_function` with `fromTable`. The condition comes along.

A lookup that finds nothing still returns text such as `{"found":false}`, so a condition must parse it, not test for blank. Use a run condition for this, not a Formula that returns blank to stop the next step.

## Step 2: Build it

**Pick the route first.**

- **Table first.** Use this for every design except the pack's own recipes (Find work email, Why now), and for any step that needs a run condition. Build the steps as columns in a scratch table (`autoplay: false`), or use the columns a play already tested. Building is free, but testing the columns costs money: price the test rows and ask (house rules, section 4), run 1 row, then 10, and check the answers. Then `create_function` with `fromTable` (see "From a working table instead" below), write its `functionId` into the "Functions" section of `loopster-context.md` straight away, and go to Step 3. Run it with `run_function`. Add one `run-function` column only when a table is needed (Step 5). Tell the user the scratch table is still in Loopster, and keep it unless they ask to delete it.
- **Direct build** only for a recipe the pack ships (Find work email in the `contact-finder` skill, Why now in the `signal-outbound` skill) that has no run condition. Follow `references/function-lifecycle.md`. In short:

  1. `create_function`, with the title and description, to make a draft. Write its `functionId` into the "Functions" section of `loopster-context.md` straight away; drafts can't be found by title later.
  2. `open_function_sandbox`.
  3. `add_function_input` for each input. Always send `required`, and keep each returned `input.id`.
  4. `add_function_step` for each step, in order, with the ids filled in. Read `warnings` and `appliedFixes` in each answer. For example, a waterfall may leave verification off, or an AI step with no prompt cannot run.
  5. `get_function`: read `draft.outputs` to see which columns can be returned. A waterfall offers its result column there.
  6. `set_function_outputs` with the full list of output column ids.

**From a working table instead:** if the steps already work as table columns, use `create_function` with `fromTable` (`tableId`, `columnIds`, and `outputColumnIds` for what to return). This is the route for every design except the pack's own recipes, for steps with run conditions, and for column chains a play has already tested. The columns become steps, the columns they read become inputs (`optionalInputColumnIds` for ones a run may leave out), and outputs are the `outputColumnIds` you pass. If you pass none, the Function returns every step's result (large raw outputs included), so always pass the list. Read the new ids and `draft.outputs` with `get_function`, because they are not the table's ids. Use `set_function_outputs` so only columns that always get a value, or are skipped by a run condition, are returned. Then, in the play's table, add one `run-function` column (Step 5) and run it only on rows that have no result yet, so nothing is bought twice. Delete the old columns only after the user agrees and the results are saved to a CSV.

## Step 3: Test before it's live

- `publish_function` with `dryRun: true`. Expect `wouldPublish: true`. `contract.outputs` shows the output keys, which come from the step names (for example "Why now" becomes `why_now`).
- If it is refused with `no_outputs`, set outputs and try again.
- Other refusals:
  - `step_columns_missing`: open a sandbox, which builds the missing step columns, then publish.
  - `waterfall_running`: wait, then publish again.
  - `column_limit`: the workspace's column limit is reached.
  - `live_body_changed`: the Function was edited in Loopster after the sandbox opened. Tell the user what the error says would be lost. Send `discardLiveEdits: true` only if they say to discard those edits.
  - `sandbox_changed`: send the same call again.
  - `nothing_to_publish`: there is no change to publish.
- Show the user the contract the dry run returned (inputs, output keys, cost per run), and ask before the live publish. Publishing and opening to agents change what others can run, so each needs its own yes (house rules, sections 4b and 6).
- After a yes, publish. Ask again before opening it to agents (`set_function_agent_access`). Then run it on **1 real sample** the user picks, show the outputs, then on 2 more.
  - Price the samples first (`costEstimate.maxUsdPerRun` × 3) and ask, with the pricing sentence.
  - Read each sample's outputs with `get_function_run`, and read `get_wallet` `consumedUsd` before and after each run.
- Show the outputs and ask whether they're right. Fix prompts or settings in a new sandbox, then republish. Callers keep the old version until you publish again.

## Step 4: Hand it over

Give the user a short "how to call it" note, and update this Function's line in the "Functions" section of `loopster-context.md` (published, open to agents, inputs, outputs, cost per run). If there is no context file, give the user the note and the id:

```
Why now · Loopster skill   (id: <functionId>)
Input:  Company domain  → key <inputId>
Output: why_now = {"signal","date","evidence","opener","fit"}
Cost:   up to $0.03 a company + AI by use
Agent:  run_function { functionId, inputs: [{ "<inputId>": "acme.com" }] }
API:    POST /v1/functions/<functionId>/runs  {"inputs": [{"<inputId>": "acme.com"}]}
```

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Step 5: Use it from a table (only when a table is needed)

When the results must live in a table (the user wants the rows in Loopster, more than about 25 inputs, a push, a schedule or a webhook), call the Function from one `run-function` column. Don't copy its steps into columns.

```json
{"templateId": "run-function", "header": "Work email",
 "taskConfig": {"runFunction": {"functionId": "<id>",
   "inputMappings": [{"inputId": "<input id>", "mode": "column", "sourceColumnId": "<column id>"}]}}}
```

- Map every required input, with `mode: "column"` (from a table column) or `mode: "static"` with a `staticValue`. Input ids come from `get_function`.
- The cell holds a JSON object of the outputs, each itself JSON text. Pull one field into its own column with a Formula that parses twice, or with a field reference whose `path` is `["<output key>", "<field>"]`. `list_columns` doesn't list the output keys; `get_function` does.
- Quote it as the Function's `costEstimate.maxUsdPerRun` × the rows, plus any usage-priced step measured on 10 rows. Use this figure for the quote and the big-spend check. If the Function is free, say so and go on. Otherwise, unless the plan's budget already covers it (house rules, section 4b), show the rows and the ceiling and ask for a yes, ending with the pricing sentence. Run 1 row, then 10, then 100 rows at a time (`trigger_rows` with `rowIds`). Read `get_wallet` `consumedUsd` before and after each batch. Stop and ask if a batch costs more than 1.5 times its share of the quote. Keep `autoplay` off while you build.
- If the whole job is a big spend (house rules, section 4c), ask in that section's wording instead, in every permission mode, before the first paid run.
- A schedule re-runs every cell unless you send `cells: "empty"`, so send it and only new rows run. Create it with `paused: true`. Price a month of firings (rows per firing × the Function's cost per run, measured on 10 rows). Resume it only after a yes, and if that is a big spend, ask in section 4c's wording. An Auto-run table spends on every new row, so price a month of new rows the same way before you turn Auto-run on.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Editing later

1. `open_function_sandbox`. It copies recent rows in to test on, and `seededRows` says how many.
2. Change what you need in the sandbox, one call each:
   - a step: `update_function_step` (its answer shows the new `costEstimate.maxUsdPerRun` and any `unpricedSteps`; read `appliedFixes`) or `delete_function_step`. Only steps the API can add can be updated; a refusal names the step, so keep that part as a table column;
   - an input: `add_function_input`, `update_function_input` (name, description, required) or `remove_function_input`;
   - outputs: after you delete a step that was an output, or want another, send the whole list again with `set_function_outputs`;
   - a step's output key comes from its name, and callers read it by key. Don't rename a step that is an output unless the user agrees, and check the new keys in the dry run's `contract.outputs`. Renaming an input is safe, because callers send inputs by id. Removing an input, or making one required, can break callers (item 4).
3. Dry-run the publish, show what changes, and ask before publishing. Ask the user which tables and agents call the Function, because a publish changes what they run, including every `run-function` column that calls it. Until then, callers run the published version, and their runs say `hasUnpublishedChanges: true`.
   - If the edit adds a paid step or an AI step, every caller's next run costs more. Say so in the ask. For each schedule or Auto-run table the user names (check `list_schedules` and `get_table`), price one firing as rows × the dry run's cost per run, plus 4 × the estimate for any AI step, because a new step can't be measured until it is live. If the monthly total is a big spend (house rules, section 4c), use that section's wording and wait for its own yes.
   - Offer to pause those schedules (`update_schedule` with `paused: true`) and turn off Auto-run (`set_table_autoplay`) before you publish. After publishing, run 1 input, then 10, read `get_wallet` `consumedUsd` before and after, and resume only after a yes (house rules, section 6).

   Real usage depends on your use case and settings, so always check the final cost estimate before you run.
4. A new required input breaks every existing caller that doesn't send it. Add new inputs as not required unless every caller will send them.

## Retiring

`delete_function` moves it to Trash for 30 days. It stops every table and agent that calls it until it is restored: a table's runs fail and agents get 404. Ask the user which tables and agents use it, and get a clear yes before you delete. The answer's `usedBy.tables` says how many tables called it. Find it with `list_trash` (it shows when it will be purged), then restore it with `restore_from_trash` using that id.

## If something goes wrong

- **403 on run:** the Function is not open to agents. Ask the user, then call `set_function_agent_access` (house rules, section 6).
- **409 "never been published":** dry-run the publish, show the contract, and publish only after a yes.
- **400 "Missing required inputs":** inputs must be keyed by input id, not by name.
- **A step is refused by name:** it is not one the API can add yet. Use a table column instead, or build that part in Loopster.
- **An AI step's output is empty:** check that its mentions point at real step or input ids. A required mention whose value is blank stops the step from running.

<!-- function-builder/references/function-lifecycle.md -->
# Function lifecycle: calls and answers

Read these answers after each call.

| Call | Key fields | Answer to read |
|---|---|---|
| `create_function` | `title`, `description` (or `fromTable`) | `function.id`; `published: false`, `agentAccess: false` |
| `open_function_sandbox` | `functionId` | `sandbox.opened: true`, `seededRows` |
| `add_function_input` | `header`, `required` (always send it), `description` | `input.id` (a UUID); stored `header` |
| `add_function_step` | `templateId`, `header`, and `taskConfig` or `aiConfig` | `column.id`, `dependencies`, `costEstimate.maxUsdPerRun`, `warnings`, `appliedFixes`, `childColumnsBuilt` (waterfalls) |
| `get_function` | `functionId` | `draft.inputs`, `draft.steps`, `draft.outputs[].columnId` (what can be returned) |
| `set_function_outputs` | `columnIds` (the whole list) | `draft.outputs[].selected` |
| `publish_function` | `dryRun: true` first | `wouldPublish`, `contract.outputs` (keys), `refusal` |
| `publish_function` | live | `published: true`; the sandbox closes |
| `set_function_agent_access` | `agentAccess: true` | `agentAccess: true` (can be set before publishing, but it can't run until published) |
| `run_function` | `inputs`: one object, or a list of up to 1,000, keyed by **input id**; `idempotencyKey` | one input: `runId`; a list: `runId` for the batch and `items[]` with `index` and `rowId`, plus `rejected[]` |
| `get_function_run` | `functionId` and `runId` (a single run's `runId`, or a batch item's `rowId`) | `status`, `outputs` (text, or a JSON number for a number-shaped step), `skipped`, `hasUnpublishedChanges` |
| `get_run` / `list_run_items` | the batch `runId` | counts and per-item state (no outputs) |
| `delete_function` | `functionId` | `inTrash: true`, `usedBy.tables`; later runs answer 404 |

## Refusals to expect

- `run_function` on a Function not open to agents: 403 "This function is not enabled for agent access."
- `run_function` open to agents but never published: 409 "This function has never been published…"
- A value keyed by the input's name instead of its id: 400 "Missing required inputs: <id>".
- `publish_function` with no outputs: 409 `no_outputs`.
- Changing inputs, steps or outputs with no sandbox open: 409 `sandbox_required` (publishing closes the sandbox).

## Notes

- The output key is made from the step's name: "Why now" → `why_now`, "Work Email" → `work_email`.
- Output values come back as text, except an output whose step is shaped as a number, which is a JSON number when it holds one. Parse JSON outputs yourself.
- A `fromTable` Function keeps working after its source table goes to Trash.
- Waterfall steps get a result column plus one column per step (`childColumnsBuilt`). Return the result column.

<!-- function-builder/references/step-recipes.md -->
# Step recipes

`<inputId>` and `<stepId>` stand for the ids returned when you add inputs and steps. Mentions keep the braces: `@{<inputId>}`.

## Formula: clean or derive a value (free)

```json
{"templateId": "formula", "header": "Clean domain",
 "taskConfig": {"formula": {"expression": "String(@{<inputId>}).trim().toLowerCase().replace(/^https?:\\/\\//,'').replace(/^www\\./,'').split('/')[0]"}}}
```

The expression is JavaScript, and `@{id}` stands for the value. A later step can read this one with `@{<stepId>}`.

**Reading one field of a JSON result** (for example `company_website` from a person lookup): use a field reference, `@{ref:v1:<data>}`. `<data>` is the base64url encoding, with no `=` padding, of `{"columnId":"<step or column id>","source":"value","path":["company_website"]}`, with exactly those keys in that order and no spaces. Extract the field into its own Formula step or column, then compare it in the next one. Use one field reference per Formula expression. A plain column mention can be used more than once.

## AI: judge, summarize or write, using the workspace ICP

```json
{"templateId": "ai", "header": "ICP fit",
 "aiConfig": {"prompt": "Our ideal customer profile:\n@{ctx:<icpContextId>}\n\nCompany data (JSON):\n@{<stepId>}\n\nAnswer with JSON only: {\"fit\": \"high|medium|low\", \"reason\": \"one sentence\"}"}}
```

- Get context ids from `list_contexts`.
- Ask for JSON only, and give the exact shape, so callers can parse the result.
- AI steps are priced by use (`unpricedSteps: 1`), so the Function's quote is only a floor. Until you have run 10 inputs, quote 4 × the step's estimate. After a yes, run the Function on 1 input, then 10, and read `get_wallet` `consumedUsd` before and after each run, then quote from what you measured.
- Every mention is required by default. A blank value stops the step from running. PredictLeads list results come back as JSON even when empty, so they do not block.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## PredictLeads signal steps

All of these take `domain` and `execution_mode: "managed"` (Loopster's account) unless the user has their own PredictLeads key.

| templateId | taskConfig key | Useful settings | List price |
|---|---|---|---|
| `predict-leads-find-jobs` | `predictLeadsFindJobs` | `title_keywords` (list), `description_keywords`, `posted_within_days`, `active_only`, `max_results` | $0.0127 |
| `predict-leads-find-news` | `predictLeadsFindNews` | `categories`, `max_results` | $0.0127 |
| `predict-leads-find-financing` | `predictLeadsFindFinancing` | | $0.0871 |
| `predict-leads-find-tech-stack` | `predictLeadsFindTechStack` | | $0.0233 |
| `predict-leads-find-lookalikes` | `predictLeadsFindLookalikes` | | $0.0017 |
| `predict-leads-website-subpages` | `predictLeadsWebsiteSubpages` | | $0.0017 |

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Example:

```json
{"templateId": "predict-leads-find-jobs", "header": "Open sales roles",
 "taskConfig": {"predictLeadsFindJobs": {"execution_mode": "managed", "domain": "@{<inputId>}",
   "title_keywords": ["sales development", "SDR", "account executive"], "posted_within_days": 90, "active_only": true, "max_results": 10}}}
```

## Work-email waterfall

Add four inputs first: `First name`, `Last name` and `Company domain` (all required), and `LinkedIn URL` (not required; with it, the free step can answer). Then add one step:

```json
{"templateId": "waterfall-email", "header": "Work email",
 "taskConfig": {"waterfallEmail": {
   "providers": [
     {"id": "loopsterDataFindWorkEmail-default", "order": 0, "enabled": true, "taskType": "loopsterDataFindWorkEmail"},
     {"id": "icypeasFindEmail-default", "order": 1, "enabled": true, "taskType": "icypeasFindEmail", "executionMode": "managed"},
     {"id": "findymailFindByName-default", "order": 2, "enabled": true, "taskType": "findymailFindByName", "executionMode": "managed"}],
   "validation": {"enabled": false},
   "inputMapping": {"first_name": "@{<first name input id>}", "last_name": "@{<last name input id>}",
     "domain": "@{<domain input id>}", "linkedin_url": "@{<LinkedIn URL input id>}"}}}}
```

- Providers run in order, free Loopster Data first, and the waterfall stops at its first hit.
- Map only the inputs the Function has. Leave `linkedin_url` out when there is no LinkedIn input.
- Leave `executionMode` off a provider if the user has their own key for it.
- The answer lists `childColumnsBuilt`. Return the result column ("Work Email", output key `work_email`), not the per-provider columns.
- `appliedFixes` may say verification was left off. That is expected, because email checks can't be Function steps.
- After a yes, test any other provider mix on 1 input, then 10, before you rely on it.

## Provider actions

Any API-addable task works as a step. Read its settings with `get_column_template` (on any table id) and pass them under `taskConfig.<taskType>`. For the step to run on Loopster's account, set `execution_mode: "managed"` where the schema offers it, or `executionMode` on waterfall steps.

## gtm-context

Set up the go-to-market context every Loopster play reads, in about five minutes. It covers what you sell, your ICP and buyer personas, pains, proof, voice, competitors, the do-not-contact list, and where results should go (CRM, sequencer, Slack), saved as loopster-context.md, plus a Loopster do-not-contact table used to exclude records from every search and a register of the reusable Functions in the workspace. Also logs campaign results so later plays get sharper. Use when the user says "set up my ICP", "here's what we sell", "update our messaging", "add these to do-not-contact", "log campaign results", "what Functions do we have", "record this Function", or when a Loopster play starts and no loopster-context.md exists.

# GTM context

## What you get

- **`loopster-context.md`:** one file every Loopster play reads, so nobody re-explains the business each time.
- **A do-not-contact table in Loopster:** customers, open deals, competitors and anyone who asked not to be contacted. Searches use it as an exclusion list, and plays check it before pushing anyone.
- **A Functions register** inside the same file: the reusable Functions the workspace already has, with their ids, inputs, outputs and costs. Every play reads it first and reuses a Function before it builds one. No play copies a Function's steps into table columns (house rules, section 7).
- **A campaign log** inside the same file, which plays update after each run.

The template is in `references/context-template.md`. To choose between a Function, a table and a capability, see `references/choosing-the-surface.md`.

## Where the file lives

1. Look for `loopster-context.md` in the working folder.
2. If it's not there, look for `~/.loopster/context.md` (one context for all projects).
3. If neither exists, create it in the working folder, unless the user wants it global.
4. If this tool keeps no files between chats (for example Claude.ai), show the user the file's text at the end of the session and ask them to save it and paste it back at the start of the next chat. Never assume the file is there.

If a file exists, show a three-line summary and ask whether to update it or start over. If they start over, keep the "Functions" section and the "Campaign log" exactly as they are, and rewrite only the other sections. Either way, check the "Functions" section against `list_functions` (Step 1) and add any Function it is missing.

## Before you start

Read `references/house-rules.md` once per session (sections 4 and 7 matter most here).

## Step 1: Start from what Loopster already knows (free)

- `list_contexts`: note the ids of the ICP and tier contexts, if any. AI steps can read them as `@{ctx:<id>}`. The API returns titles only, not the text, so still capture a plain-English ICP in the file.
- Functions register:
  1. `list_functions`: write each Function's title and id on its own line in the "Functions" section, with "open to agents yes". It shows only published Functions that are open to agents.
  2. Ask whether the user has drafts, or published Functions not yet open to agents. Read each id they give with `get_function` and write its line too.
  3. Read the ones a play would reuse (emails, phones, scoring, signals, first lines, CRM fills) with `get_function`, and add each one's input ids, output keys and `costEstimate` if shown.
  4. If there are none, write "none yet".
- Ask for the company website, as one question with a default: the domain of the user's work email or of the connected accounts if you can see one, else say they can reply "skip" and you'll go on from the ICP in their message. Run `run_capability` with `loopster-data-enrich-company` (free, `maxCostUsd: 0`) for name, industry, size and location. This is one action, once, so a capability is the right surface: no table and no Function.
- Do-not-contact table: if `list_tables` with `search: "Do not contact"` finds none, create it now (Step 3, items 1 to 3), before the questions. It is free and needs no answers; loading rows into it waits for Step 3, item 4.
- If you can read web pages yourself, read the homepage, pricing and customers pages. Draft a one-paragraph offer summary and a first ICP guess from them. Show the draft rather than asking from scratch.

## Step 2: Fill the gaps, one question at a time

Ask only what Step 1 and the user's own message did not answer. **One question per message:** ask it, offer your best guess as the default the user can accept with "yes", and wait for the answer before the next. Never send the questions below as a list. If nobody can answer (an unattended run), ask only the first open question and stop there. If the user skips a question, write "not provided" in the file and move on; plays fall back to safe defaults.

1. **Offer:** what you sell, in one sentence, and the outcome a customer gets.
2. **ICP:**
   - industries
   - company size (employees)
   - regions
   - must-have traits, such as "uses Salesforce" or "B2B" (optional)
   - deal-breakers
3. **Personas:** 1 to 3 buyer roles (titles and seniority), and who signs.
4. **Pains:** the top 3 problems you solve, each with how the buyer notices it.
5. **Proof:** 2 to 5 customers or results that can be named, with numbers where possible, and which persona or industry each one is strongest for.
6. **Competitors and alternatives:** what buyers use today instead, and the one-line difference.
7. **Voice:**
   - tone
   - maximum length
   - words to avoid
   - first-name or formal
   - the call to action you prefer (question, short meeting, resource)
8. **Destinations:** check `list_connections` first, then confirm where results go:
   - the CRM (which connected account)
   - the sequencer and campaign
   - the Slack channel for alerts

## Step 3: Build the do-not-contact table (free)

This stays a table: searches take exclusions as a table column, and people edit its rows by hand. It holds no repeated logic, so there is nothing to put in a Function.

1. Look for an existing table first: `list_tables` with `search: "Do not contact"`.
2. If there's none, create a blank table with `autoplay: false`, titled `Do not contact · <company name>`. Reference tables keep a plain name with no date. A new blank table already has one `Input` column; you can ignore it.
3. Add four columns, `Domain`, `LinkedIn URL`, `Email` and `Reason`, either way:
   - turn on `set_table_create_columns_from_keys` and insert rows with those keys;
   - or create them with `templateId: "manual"`.

   Read the column ids with `list_columns`; columns created from keys may use the key itself as the id.
4. Ask what to load:
   - current customers
   - open opportunities
   - competitors
   - partners
   - people who opted out

   Accept a CSV, a pasted list, or an existing Loopster table. Insert the rows; normalize domains to `example.com` form first.
5. Record the table id and its column ids in the context file. Plays exclude with:

   `{"kind": "list", "projectId": "<table id>", "columnId": "<Domain column id>", "matches": "identity"}`

   For people searches, use `"matches": "company"` on the Domain column to leave out everyone at those companies.

## Step 4: Write the file

- Fill `references/context-template.md` and save it. Include the Functions you found in Step 1 and the Spending lines (how Function runs are batched).
- Write each Function you found as a line in the template's format, with its real id. A Function that doesn't exist yet stays "not built". Never leave a `<...>` placeholder in the file; the one-line format guide in the "Functions" section is the only exception.
- Show the user a short summary.
- Ask them to correct anything wrong. A wrong ICP costs more later than a question now.

## Update mode: log a campaign

When a play finishes, or the user reports results ("40 sent, 6 replies, 3 positive"), append a row to **Campaign log**:

- date
- play
- list
- angle and proof used
- how many were sent
- replies
- positive replies
- meetings
- one line on what worked

Then update **What's working**:

- An angle with a positive-reply rate above the others after 100 or more sends: move it up.
- One with none after 200 sends: move it to **Retired angles**.

Never delete history.

## Update mode: record a Function

If there is no `loopster-context.md` yet, create it from `references/context-template.md` with only the "Functions" section filled and every other section marked "not provided". Do not start the interview; tell the user they can complete the file later with this skill.

The "Functions" section is the one place every play records Function ids. Update it whenever a play or the `function-builder` skill:
- creates a Function (write the id straight away, even for a draft; drafts don't show in `list_functions`);
- publishes it, opens it to agents, edits it or retires it;
- measures its cost per run (`get_wallet` `consumedUsd` before and after, divided by the inputs you ran);
- adds a table whose `run-function` column calls it, or a schedule on that table.

Keep one line per Function, in the format in the template. A retired Function stays on its line, marked "retired YYYY-MM-DD", so nobody rebuilds it by mistake. When you quote a run, read the Function's cost from its line and price it as house rules section 4 says.

When a play has built a repeating job as table columns and they worked on the first build, the play turns them into a Function (`create_function` with `fromTable`) and records its id here. From then on, that play, and any scheduled or Auto-run table, calls the Function with one `run-function` column instead of copying its steps into columns.

Columns that use a step Functions refuse (CRM, sequencer and Slack actions, email checks, live LinkedIn profiles and posts, score-prospect) stay table columns; convert only the rest. Creating the draft is free; publishing it and opening it to agents each need the user's own yes (house rules, sections 4b and 6).

## If something goes wrong

- **A recorded Function can't be found:** it may have been deleted. Call `list_trash`: if it is there, it can be restored until its `purgesAt`. Tell the user, mark its line "not found", and ask whether to restore it (`restore_from_trash`) or build a new one with `function-builder`.
- **The website lookup finds nothing:** ask for the details instead. Loopster Data does not hold every company.
- **The user does not know their ICP:** start from their best 5 to 10 customers. Run `loopster-data-enrich-company` on their domains (free) and propose the common traits.
- **The do-not-contact table already exists with other columns:** reuse it, and record which column holds domains.

<!-- gtm-context/references/context-template.md -->
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

## headcount-growth

Measure how fast companies are growing or shrinking by headcount, in one step: one priced headcount source, growth bands, and companies without data reported as no data. Use when someone asks which accounts are growing fastest, who is hiring the most, or for headcount trends on a list. For hiring signals turned into outreach, use signal-outbound.

# Headcount growth

One step: headcount and its growth per company. For outreach on top of it, use the `signal-outbound` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Free headcount now:** `loopster-data-enrich-company` gives the current employee count (free). Growth over time needs a paid source.
2. **Growth source:** the professional-network company headcount route (see `references/data-routes.md`), as a table column with `execution_mode: "managed"`. Read the live `cost`.
3. **Ask before the first paid row.** This source is not AI web research, so the request doesn't cover a test: show the price for 3 rows and for all companies, and ask with the pricing sentence.
4. **On a yes, 3 rows first** to see which periods the growth comes in. If they have no growth data, stop, say the source has none for these companies, and offer a proxy (open roles per 100 staff, `hiring-signals`). Otherwise 10, then the rest.
5. **Bands** (default: below −5% shrinking, −5% to +5% flat, +5% to +20% growing, above +20% fast-growing). Write them into one column with one `update_cells`.
6. **Report** counts per band, the fastest growers, the companies with no growth data (as "no data", never "flat"), and the cost.

## Does not claim

- Why a company grew or shrank.
- Growth the source doesn't report.

## hiring-signals

See which companies are hiring for a given team right now, in one step: job postings filtered by title keywords and a recent window, priced per company and agreed first, ranked by open roles. Use when someone asks which of these accounts are hiring engineers, SDRs or another team, or for open roles at a list of companies. To turn hiring into outreach with openers, use signal-outbound.

# Hiring signals

One step: open roles per company for one team. For outreach with openers, use the `signal-outbound` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **The team** as title keywords (for engineers: "software engineer", "backend", "frontend", "data engineer"…) and a window (default: posted in the last 90 days, active only). Show them.
2. **Job postings:** `predict-leads-find-jobs` with `title_keywords`, `posted_within_days` and `active_only` (see `references/signal-recipes.md`, "Hiring for roles you serve"), as a table column or capability with `execution_mode: "managed"`.
3. **Price per company** (live `cost`), ask with the pricing sentence. Run 1, then 10, then the rest, `maxCostUsd` and `idempotencyKey`.
4. **Rank** by matching open roles (`count`). Companies with none: say so.
5. **Report** the ranked counts, companies not matched, and the cost. Openers or messages only if asked (`signal-outbound`).

## Does not claim

- That a posted role is really open: postings stay up after a hire.
- A trend from one run.

## icp-to-filters

Turn an ideal customer profile written in plain words into Loopster search filters that run, and give one count, in one free step. Use when someone asks to turn this ICP into filters, what filters to use, or how to search for their target companies or people. To build the list itself (people, exclusions, export), use prospect-list; for a market count by slices, use market-size.

# ICP to filters

One step: plain words to filters, plus one count. To build the list, use the `prospect-list` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Vocabulary once:** `list_search_filters`. Values must come from its options.
2. **Map each part** of the ICP to a filter with `references/icp-to-filters.md`: industries (several neighbouring ones), size band, location of the company or the person, titles and seniority for people.
3. **Name the gaps:** parts with no filter (for example "selling to finance teams") stay out of the filters. Say so, and say how they could be checked later (an AI question on the results, `account-question`).
4. **One count:** `search_companies` or `search_people` with the filters and a small `limit`, and read the total. Search is free.
5. **Show** the filters as JSON and a plain table (ICP words · filter · values), the count, and the gaps.

No import and no table unless the user asks: that is `prospect-list`.

## Does not claim

- That the count is the whole market: it is Loopster's coverage.

## inbound-router

Build an inbound lead router in Loopster. Every form fill, signup or demo request posted to a webhook is enriched within minutes (free sources first), checked for personal emails, scored against the ICP, given an owner, and pushed where it should go. That can be a Slack alert with a short brief and a drafted reply, the CRM (update, or create after a test), or a sequencer campaign for the rest. The repeated qualify logic lives in a reusable Function that the webhook table calls from one column. Built step by step, tested with a made-up lead, and switched on only after a yes. Use when the user says "route inbound leads", "speed to lead", "enrich form fills", "qualify demo requests", "qualify inbound leads", "alert sales in Slack when a good lead signs up", or "send signups to HubSpot".

# Inbound router

## What you get

A Loopster webhook table, `Inbound · <source> · router`, that runs by itself within minutes of each form fill.

1. Your form, website or tool posts each lead to its address.
2. Each lead is enriched, scored, assigned and pushed automatically.

You also get:
- a Function, `Qualify lead · Loopster skill`, built from the working columns once the test passes and you agree (or an existing one reused), that holds the enrich-and-score logic, so the next form reuses it;
- a result summary (the block under "Show the result") with the address, Function, cost per lead, routes and test result;
- a test lead run end to end before it goes live.

## What lives where

Repeated logic goes in a Function. A table is here for what a Function can't do, and for the `Tier` and `Route to` rules you will tune (house rules, section 7).

- **In the Function:** the steps every lead repeats: the domain, the personal-email check, the company profile, the LinkedIn lookup and the ICP fit. A fix happens in one place, and other forms can call it.
- **Only a table can do:** the webhook address, Auto-run on each posted lead, the double-submit guard, and the Slack, CRM and sequencer columns. They send outside Loopster, so each needs its own yes (house rules, section 6).
- **Kept in the table for now:**
  - `Tier` and `Route to`: routing rules for this form. A Formula edit is free, while a Function edit needs a republish.
  - `Brief` starts as a table AI column. It runs for every lead, so once it reads well on the made-up leads, turn it into its own Function titled `Lead brief · Loopster skill` in step 7 with `create_function` `fromTable` (`Tier` and the columns it reads become inputs), record its id in the "Functions" section of `loopster-context.md`, and call it from one `run-function` column that `Alert` reads through a pulled-out column. If the user declines, keep the column.
- `score-prospect` can't be a Function step. The ICP fit uses an AI step that returns a tier and a reason.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (ICP, destinations, voice).

Then look for a Function that already qualifies leads: the "Functions" section of `loopster-context.md`, then `list_functions`.
- If `Qualify lead · Loopster skill` exists (or a Function whose inputs and output keys match it in `get_function`), read it with `get_function` and tell the user its inputs, steps and price. Reuse it: the table calls it from one `run-function` column (Build it, step 7), and you skip items 1 to 5 of step 5. If it is still a draft, publish it and open it to agents first, each with its own yes.
- If a scoring Function fits instead, such as `ICP tier · Loopster skill` (or an `ICP tier · <qualifier> · Loopster skill` variant), read it with `get_function` and tell the user its inputs, steps and price. Keep items 1 to 4 of step 5 as columns, and call it from one `run-function` column in place of item 5 (Build it, step 7).
- If none fits, you build it in step 7, after the columns work.
- Always take a Function's output keys from `get_function`, not from this skill.

Settle five things, one question at a time, with defaults:

1. **Source and fields:** what the form sends. At minimum an email; ideally name, company, website, title and message. Ask for a sample payload.
2. **What makes a good lead:** use the ICP context. Default tiers: **A** is ICP fit at a work email, **B** is partial fit, **C** is no fit or a personal email.
3. **Owners:** round robin, by region, by company size, or one inbox. Default: one Slack channel for A and B.
4. **Destinations:**
   - Slack channel per tier;
   - CRM (HubSpot, Salesforce, Attio): update existing contacts, or create new ones after a test;
   - sequencer for C (nurture).

   Check `list_connections`.
5. **Cost per lead you accept.** Enrichment is free. The ICP fit and the AI brief are priced by use.
   - Read the AI fit and the brief together on 10 made-up leads (`get_wallet` `consumedUsd` before and after), then quote that total. Until you have measured 10, use 4 × the pre-run estimate (house rules, section 4c).

   Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Then show the plan in a few lines (house rules, section 4b): the steps, what you will create (the webhook table and the `Qualify lead · Loopster skill` Function, and the `Lead brief · Loopster skill` Function if you build it) and a test budget in dollars for the made-up leads. End that message with the pricing sentence. One yes covers every test run inside that budget. Publishing a Function, opening it to agents, the real destinations, switching Auto-run on and any big spend each still need their own yes.

## Build it (Auto-run OFF while building)

Use exact settings from `references/router-columns.md`.

1. **Table:** `create_table` with `type: "webhook"`, `autoplay: false` and the title. Turn on `set_table_create_columns_from_keys`. Once the sample post in step 3 has made the input columns, turn it off again (`set_table_create_columns_from_keys` with `false`), so a typo or a renamed field in a later post does not add a column.
2. **Address:** on the new table, call `rotate_table_webhook`. It returns the full address once; `get_table_webhook` later shows only its last four characters.
   - On an existing table, rotating issues a new address and the old one stops working. Ask first if a form already posts to it.
   - The address contains a secret, and anyone with it can add rows. Show it to the user once and tell them to store it like a password.
   - Never paste it into a public place, a ticket or a shared doc.
3. **Post one sample payload now,** so the input columns exist before you build on them.
   - Use a made-up lead: an obviously fake name, and an email on a domain the user owns, so no real outside person is involved. Send every field the form sends, because a field missing from this post gets no column once the setting is off.
   - POST it to the address with `curl` (or the user's form tool), which tests the real address; `insert_rows` would bypass it.
   - Auto-run is off, so nothing runs yet.
   - `list_columns` now shows the input columns. On a webhook table their ids equal the field names (`Email`, `Name`, …).
4. **Deduplicate:** `set_table_auto_dedupe` with `columnId` `Email`, `enabled: true` and `keep: "oldest"`, so a double submit is not added and does not run or charge twice. Read `settings.autoDedupe` in `get_table` to confirm. Do not edit the `Email` cell of a kept row to a value another row already has: that deletes the edited row. A blank email never matches, so the valid-address gate in step 8 still matters.
5. **Columns, in order.** Build items 1 to 5 as table columns first. They are the steps that step 7 turns into the Function. If you are reusing a Function, follow "Before you start" for the items it replaces.
   1. `Domain`: a Formula that takes the email domain, with a placeholder for personal emails so the next lookup never skips (`references/router-columns.md`).
   2. `Personal email`: a Formula; `yes` for gmail.com, outlook.com and similar.
   3. `Company profile`: `loopster-data-enrich-company` on `Domain` (free).
   4. `LinkedIn lookup`: `loopster-data-email-to-linkedin` on the email (free). It adds the profile link to the brief and the CRM record.
   5. `ICP fit`: an AI column returning `{"tier","reason"}` with the ICP context (`references/router-columns.md`, section 5). Use an AI column, because it can move into the Function and `score-prospect` can't. Don't give it a run condition yet: `Tier` reads this column, and a column that reads a skipped column does not run (house rules, section 9). You add the condition in step 7, inside the Function.
   6. `Tier`: a Formula combining fit and personal email (`references/router-columns.md`, section 6). A personal email caps the tier at C. Set `optionalMentions` for `ICP fit` on `Tier`. If `ICP fit` is `none`, empty or can't be read, the Formula gives `review`, so no lead is dropped. After step 7, this relies on the `icp_fit` pull-out returning `none` (`references/router-columns.md`, section 10).
   7. `Route to`: a Formula giving the Slack channel id: the hot channel for A and B, and the review channel for `review`. It is never blank: the review channel is the fallback, and the `Alert` run condition keeps C leads out of Slack (section 7). For owners by region or size, map those fields to channels in the same Formula. True round robin needs a counter, so use one channel per team instead.
   8. `Brief`: an AI column that writes 3 lines (who, company facts, why they matter), plus a 2-sentence reply draft in the house voice. Give it a run condition so it runs only for A, B and `review`: C leads are never alerted, so they don't need a brief (section 8). Set `optionalMentions` for `ICP fit` on `Brief` too.
   9. Destination columns:
       - `Alert`: `slack-send-message`, with `channel_id` set to `@{Route to}` and text set to `@{Brief}`. Give it a run condition for A, B and `review` only (section 9);
       - `CRM`: for Salesforce, `salesforce-upsert-object`. For HubSpot, `hubspot-find-object` looks the contact up by email, then `hubspot-update-object` updates the found record. This only updates contacts that already exist, so a new lead is not added. Say that to the user. To add new contacts, test `hubspot-create-object` with `objectType: "contacts"` on the made-up lead in a test portal first;
       - `Nurture` (optional, for C): a sequencer column with a run condition for tier C only (section 9). A lead that never asked to be contacted shouldn't go straight to a sequence. Prefer a CRM list, or hand C leads to `outbound-launch` with its pre-flight checks.
6. **Test end to end on the made-up leads.**
   - While testing, `Route to` must point at a **test** channel, the CRM column at a **test** record or sandbox, and any sequencer at a **paused** test campaign.
   - Post 3 to 5 made-up leads, each with its own email on the user's domain: a work email at an ICP-sized company, a gmail address, one with a blank `Message` and one with a blank `Name`.
   - Check the price fits the test budget, then trigger the columns on one row first, with `maxCostUsd`.
   - Read the row. Check every column, and fix prompts or formulas until the brief, tier and route are right. While they are still columns, an edit is cheap: re-run the column with `force: true`.
   - Check the gmail lead: `Tier` reads C and `Brief` is skipped.
   - Read a first cost per lead: `get_wallet` `consumedUsd` before and after these leads. A quote needs 10 leads: step 7 measures `Qualify` and `Brief` on 10 (if you keep the columns, run 10 made-up leads through them).
7. **Turn the qualify columns into a Function.** Do this before Auto-run, because every lead and every later form repeats this logic (house rules, section 7). Follow `references/router-columns.md`, section 10. It covers building `Qualify lead · Loopster skill`, reusing an existing Function, the one `Qualify` column, the cost checks, later edits and the `Brief` Function.
   - Publishing a Function and opening it to agents each need their own yes. If the user declines to publish, keep the five columns (the AI fit then runs for personal emails too) and say that the next form will repeat them. If they publish but decline agent access, the `Qualify` column still runs it; only `run_function` is affected.
   - The `icp_fit` pull-out returns `none` when the Function gave nothing, so `Tier`, `Brief` and `Alert` still run. Test the gmail lead and the `review` path as in section 10.
   - Delete the five columns only after `Tier` and `Route to` give the same answers through `Qualify`, and only after the user says yes. Until then, name only `Qualify` in triggers, so one trigger can't pay twice for the same work.
8. **Switch on.**
   - **Work out the monthly cost.** Ask how many leads a month the form gets. Monthly cost is leads × the cost per lead (`Qualify` plus `Brief`) measured on those 10 leads. Until you have measured 10, use 4 × the pre-run estimate (house rules, section 4c). An Auto-run table keeps spending on every new lead, so say this when you ask. Spend is read from `get_wallet` `consumedUsd` (see "Watch it").
   - If that is over $25 a month (or the "Ask above" amount in `loopster-context.md`), or over 10% of `spendableUsd`, it is a big spend (house rules, section 4c). Ask separately, in the 4c wording, and wait for a clear yes.

     Real usage depends on your use case and settings, so always check the final cost estimate before you run.
   - **Add a free gate.** Set a run condition on the `Qualify` column so a blank, malformed or obvious test address is skipped (`references/router-columns.md`, section 11). Keep `Email` mapped to the `Email` column.
     - Join the same address check, with `&&`, to the run conditions on `Brief`, `Alert` and `Nurture`, and set it alone on `CRM lookup` (HubSpot) and `CRM`, so a junk post can't reach a paid or sending step (a Slack post, a CRM record, a sequence). The exact conditions are in `references/router-columns.md`, section 11.
     - If you kept the columns instead of a Function, there is no `Qualify` column: set the check on `ICP fit` instead, and name `ICP fit` in place of `Qualify` in the `columnIds` below.
     - Then call `trigger_rows` with `columnIds: ["Qualify", "Brief", "Alert"]`, plus `CRM lookup`, `CRM` and `Nurture` if you built them, on a row that holds a malformed address (Auto-run is still off, so posting alone proves nothing). Check each cell says the condition wasn't met and `get_wallet` `consumedUsd` did not move.
   - **Check the sending columns.** Auto-run for columns that send outside Loopster is switched on in the Loopster app, not through the API. Read `list_columns` for `manualTriggerOnly` on `Alert`, `CRM` and `Nurture`. If any shows `manualTriggerOnly: true`, ask the user to switch Auto-run on for those columns in the app.
   - Switch `Route to` and the destinations to the real targets.
   - Show the full flow, the cost per lead, the monthly cost and every place a lead gets sent. Read `get_table` first: `settings.keepExistingResults` should be `true` (the default). If it shows `false`, tell the user and ask before switching it on with `set_table_keep_existing_results`: with it off, every later edit to a lead re-runs and re-bills answered cells (house rules, section 6). With a yes to the flow, run `set_table_autoplay` with `true`. From now on, each posted lead runs the columns that have Auto-run on, and each paid one costs money, so keep the address private.
   - After the first real lead, read it with `get_row` and check that `Alert` ran.

## Watch it

- New leads don't appear as runs. Watch progress with `get_status` for the table, and read the latest rows with `list_rows` and `updatedSince`.
- A `Qualify` cell that failed or came back empty: read it with `get_row`. Then run the same lead through `run_function` and read the answer with `get_function_run`.
- Week one: review 10 routed leads with the user and tune the tier rules (free Formulas). Also list rows whose `Qualify` cell failed or is empty.
- Try each rule change in a table sandbox first (house rules, section 5b):
  - get the `rowIds` of the reviewed leads from `list_rows`, then call `open_table_sandbox` with `mode: "explicit"` and those `rowIds`;
  - edit `Tier` or `Route to` in the sandbox, run only those columns on the sandbox rows, and show the user the new tier and route next to the old ones;
  - after a yes, publish with `publish_table_sandbox`, or discard with `exit_table_sandbox`, and don't leave it open (while one is open, the table's own columns can't be changed);
  - never trigger `Alert`, `CRM` or `Nurture` in the sandbox: its rows are real leads, and those columns send outside Loopster.
- Spend: `get_wallet` `consumedUsd` at the start and end of a day or a week, divided by the leads in that time. It includes the Function (in a shared workspace, other people's runs can add to it). If a day costs more than 1.5 times its share of the monthly quote, turn Auto-run off with `set_table_autoplay` `false`, call `stop_run` with the table's id to release leads still queued (work already running finishes and is billed), and tell the user.

## Show the result

```
Inbound · Demo form · router   (LIVE)
  Address: https://app.loopster.ai/api/v1/webhooks/loopster_whk_…  (store as a secret)
  Function: Qualify lead · Loopster skill (published; id in loopster-context.md)
  Per lead: free enrichment + AI fit and brief ≈ $<measured> (measured with get_wallet consumedUsd on 10 made-up leads)
  Routes: A/B → #inbound-hot (with brief + reply draft) · review → #inbound-review · all → HubSpot (update existing contacts)
  Test lead: passed (tier A, alert posted to #test-inbound)
```

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Connect the form

- **Most form tools** can POST JSON to a URL: Typeform, Tally, HubSpot forms (through a workflow webhook), Webflow, Framer, Zapier, n8n and Make. Send `{"Email": "...", "Name": "...", "Company": "...", "Website": "...", "Message": "..."}`.
- One lead per request, or an array of leads.
- The address answers right away; enrichment runs after.

## If something goes wrong

- **Columns didn't run on a new lead:** check that Auto-run is on (`get_table`).
- **The `Qualify` cell failed or is empty:** read it with `get_row`, then run the same lead with `run_function` and read it with `get_function_run`. Check that the Function is still published, that `Email` is not blank, and that the input ids in the column match `get_function`.
- **The table runs an old version after a Function edit:** publish the Function again (ask first), then follow "Later edits" in `references/router-columns.md`, section 10.
- **The Slack step shows "skipped":** expected for C leads (the `Alert` run condition is not met). For A or B, check the channel id.
- **Lots of tier C from personal emails:** expected for B2C-style signups. Consider asking for a work email on the form.
- **The CRM step creates duplicates:** switch to update (find the record first with `hubspot-find-object`) or to Salesforce upsert with an external id.

<!-- inbound-router/references/router-columns.md -->
# Router columns

Build sections 1 to 9 as table columns, and try each one on made-up leads before you rely on it. The brief (section 8), the AI fit (section 5) and the Function version (section 10) are priced by use: read their real cost together, with `get_wallet` `consumedUsd` before and after 10 made-up leads. Everything else in sections 1 to 9 is free.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

How the sections fit together:
- Sections 1 to 5 are the qualify logic. Build them as table columns first. Section 10 turns them into the Function `Qualify lead · Loopster skill`.
- Sections 6, 7 and 9 (Tier, Route to, destinations) stay table columns. Section 8 (Brief) starts as a table column; section 10, last bullet, turns it into the Function `Lead brief · Loopster skill`.
- Section 11 is a free gate for Auto-run.

On a webhook table with "create columns from keys" on, the first payload creates the input columns. Their ids equal the field names (`Email`, `Name`, `Company`, `Website`, `Message`). Read the real ids with `list_columns`.

**Optional inputs:**
- A form field that can be blank (Name, Message, Website) must be listed in `optionalMentions` (`update_column`), or the column skips that row.
- `optionalMentions` covers a blank **value**. It does not cover an upstream column that was **skipped**: a column reading a skipped column does not run.
- So keep every enrichment in the chain running: give it an input that is never blank. The Domain formula below uses a placeholder for personal emails instead of a blank.
- In the Function, an input that can be blank is not required (`optionalInputColumnIds` when you build it from the table). Test the Function with a blank Name, a blank Message and a gmail lead.
- If `Qualify` is skipped for a blank `Name` or `Message`, map that input from a Formula column that returns `(none)` when the field is blank (house rules, section 9).

**Run conditions:**
- To stop a paid or sending column on some rows, set a run condition with `update_column` and `runCondition`: `{"enabled": true, "description": "...", "condition": "<formula over the row>"}`. The column runs a row only when the condition is true.
- Write the whole `condition` each time you update it. If a column needs two checks, join them with `&&`.
- A run condition on a table column comes along when you build a Function with `fromTable`.
- `estimate_trigger_cost` does not evaluate run conditions, so its figure is a ceiling.

## 1. Domain (free)

A company domain from the email. Personal email providers get the placeholder `personal-email.invalid`, which matches no company, so the lookup answers `found: false` instead of skipping.

```json
{"templateId": "formula", "header": "Domain",
 "taskConfig": {"formula": {"expression": "(() => { const d = String(@{Email}).trim().toLowerCase().split('@').pop(); return ['gmail.com','googlemail.com','yahoo.com','outlook.com','hotmail.com','live.com','icloud.com','me.com','aol.com','proton.me','protonmail.com','gmx.com','mail.com'].includes(d) ? 'personal-email.invalid' : d; })()"}}}
```

Always send the placeholder, never the raw personal domain, to the company lookup.

## 2. Personal email (free)

```json
{"templateId": "formula", "header": "Personal email",
 "taskConfig": {"formula": {"expression": "['gmail.com','googlemail.com','yahoo.com','outlook.com','hotmail.com','live.com','icloud.com','me.com','aol.com','proton.me','protonmail.com','gmx.com','mail.com'].includes(String(@{Email}).trim().toLowerCase().split('@').pop()) ? 'yes' : 'no'"}}}
```

## 3. Company profile (free)

```json
{"templateId": "loopster-data-enrich-company", "header": "Company profile",
 "taskConfig": {"loopsterDataEnrichCompany": {"domain": "@{<Domain id>}"}}}
```

## 4. LinkedIn lookup and optional person (free)

```json
{"templateId": "loopster-data-email-to-linkedin", "header": "LinkedIn lookup",
 "taskConfig": {"loopsterDataEmailToLinkedin": {"email": "@{Email}"}}}
```

Optional: if the brief should carry the person's title and company, add two columns after `LinkedIn lookup`.

1. `LinkedIn URL`: a Formula that reads the URL out of the `LinkedIn lookup` cell and returns `not found` when there is none, so the next column never gets a blank. Read one `LinkedIn lookup` cell first to see the url field name. Use one field reference in the expression: `String(@{ref:v1:<data>} || 'not found')`. `<data>` is the base64url (no `=` padding) of `{"columnId":"<LinkedIn lookup column id>","source":"value","path":["<url field name seen in the cell>"]}`, with those keys in that order and no spaces. Set `optionalMentions` on this Formula.
2. `Person profile`: `loopster-data-enrich-person` with `linkedin_url` set to `@{<LinkedIn URL id>}` (a plain column mention, not a field reference).

Test both on the gmail lead, where nothing is found. `Person profile` must come back `{"found":false}`, not skipped. If it is skipped, leave it out of the brief.

After section 10 deletes the original columns, point the field reference at the `Qualify · linkedin lookup` column instead.

## 5. ICP fit with an AI column (the version that moves into the Function)

An AI column that returns a tier and a reason. It can become a Function step; read its real cost together with the brief on 10 made-up leads (`get_wallet` `consumedUsd` before and after).

```json
{"templateId": "ai", "header": "ICP fit",
 "aiConfig": {"prompt": "You score an inbound lead against our ideal customer profile.\nOur ideal customer profile:\n@{ctx:<ICP context id>}\nLead name: @{Name}\nLead email: @{Email}\nPersonal email: @{<Personal email id>}\nCompany profile (JSON from our database, may be empty or say found false): @{<Company profile id>}\nTheir message: @{Message}\nTier A means a clear ICP fit. Tier B means a partial fit. Tier C means no fit or not enough data. A personal email is never above tier C.\nAnswer with JSON only: {\"tier\": \"A|B|C\", \"reason\": \"one sentence\"}\nNever invent facts that are not in the data above."}}
```

Then call `update_column` with `optionalMentions: ["Name", "Message", "<Company profile id>"]`.

A personal-email lead always ends at tier C, so the paid step has nothing to add for it. Don't give the column a run condition yet: `Tier` reads this column, and a column that reads a skipped column does not run (house rules, section 9). In step 7, just before `create_function` (section 10), set this run condition. It comes along into the Function, where the table reads the `Qualify` cell, which always completes:

```json
{"runCondition": {"enabled": true, "description": "Only for work emails",
 "condition": "String(@{<Personal email id>}) !== 'yes'"}}
```

- An `ai` step is `{"templateId": "ai", "aiConfig": {"prompt": "..."}}`, with each mention in braces and required unless the column has `optionalMentions`.
- The cell holds JSON text such as `{"tier":"A","reason":"..."}`. The Tier formula in section 6 reads it, and answers C for a personal email without reading the fit.
- Test it on a work-email lead, a gmail lead, a lead with a blank Name and a lead with a blank Message before you rely on it.
- Read the cost per lead again after you add the condition.

## 6. Tier (free)

Reads the `tier` field of the AI answer. A personal email still caps the tier at C. If the fit is `none`, empty or can't be read, the tier is `review`, so the lead is routed to a person instead of dropped. After section 10 this holds only because the `icp_fit` pull-out returns `none`, never blank.

```json
{"templateId": "formula", "header": "Tier",
 "taskConfig": {"formula": {"expression": "(() => { let f = @{<ICP fit id>}; try { f = JSON.parse(f); } catch (e) { f = null; } if (String(@{<Personal email id>}) === 'yes') return 'C'; return f && ['A', 'B', 'C'].includes(f.tier) ? f.tier : 'review'; })()"}}}
```

`none` can't be parsed, so the lead reads as `review`, unless it is a personal email, which gives C.

Then call `update_column` on `Tier` with `optionalMentions: ["<ICP fit id>"]`. A blank fit would otherwise skip `Tier` itself, so it would never read `review`, and `Route to`, `Brief` and `Alert` would skip too. After section 10, `<ICP fit id>` is the pull-out Formula column, which returns `none` for a skipped or empty fit, so it is never blank.

Tier and Route to stay table Formulas on purpose: they are the rules you tune in week one, and a Formula edit is free.

## 7. Route to (free)

```json
{"templateId": "formula", "header": "Route to",
 "taskConfig": {"formula": {"expression": "({'A': '<hot channel id>', 'B': '<hot channel id>'})[String(@{<Tier id>})] || '<review channel id>'"}}}
```

`Route to` is never blank. A and B go to the hot channel; `review`, and anything else, goes to the review channel. The `Alert` run condition (section 9) keeps C leads out of Slack. For several channels or owners, map the tier, region or size to channel ids in the expression.

## 8. Brief (AI, priced by use)

Prompt: see the configuration below. Then call `update_column` with `optionalMentions: ["Name", "Message", "<Company profile id>", "<ICP fit id>"]`. The fit can be blank on the `review` path, and a blank mention would skip `Brief`, then `Alert`. `Brief` reads `ICP fit: none` for a review lead and still runs. Test that path as in section 10.

The Brief starts as a table AI column; section 10, last bullet, turns it into a Function. After section 10, its `Company profile` and `ICP fit` lines read the columns that pull those fields out of the `Qualify` cell. Read the cost again with the AI fit.

Give it a run condition so it runs only for the leads that get an alert:

```json
{"runCondition": {"enabled": true, "description": "Only for A, B and review",
 "condition": "['A', 'B', 'review'].includes(String(@{<Tier id>}))"}}
```

Read the cost per lead again after you add the condition.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

```
You write a Slack alert for a sales rep about a new inbound lead.
Our ideal customer profile:
@{ctx:<ICP context id>}
Lead name: @{Name}
Lead email: @{Email}
Company profile (JSON from our database, may be empty or say found false): @{<Company profile id>}
ICP fit: @{<ICP fit id>}
Tier: @{<Tier id>}
Their message: @{Message}
Write plain text, no markdown headers, exactly this layout:
Line 1: Name, title if known, company and one fact (size or industry).
Line 2: Why they matter or not, in one sentence tied to our ICP.
Line 3: Suggested next step for the rep.
Then a blank line and 'Reply draft:' followed by a 2-sentence reply to the lead, friendly and specific to their message, no hype, no calendar link.
Never invent facts that are not in the data above. If the company profile is empty, say the company is unknown.
```

## 9. Destinations (each sends for real)

| Column | Template | Key settings |
|---|---|---|
| Alert | `slack-send-message` | `slackSendChannelMessage`: `channel_id: "@{<Route to id>}"`, `text: "@{<Brief id>}"`; run condition for A, B and `review` (below) |
| CRM lookup | `hubspot-find-object` | finds the contact by email; read its settings with `get_column_template` |
| CRM | `hubspot-update-object` | updates existing contacts only, so a new lead is not added. `hubspotSendObject`: `mode: "update"`, `objectType: "contacts"`, `recordId` from the lookup, `properties` (a JSON string of HubSpot internal property names; build it blank-safe with one Formula column that includes only the fields that have a value, so a blank never clears a CRM field; never map a column straight into `properties`); `integrationConnectionId` |
| CRM (Salesforce) | `salesforce-upsert-object` | matches on an external id field, so it creates or updates |
| Nurture | `heyreach-add-leads-to-campaign` / `instantly-add-lead` / `smartlead-add-lead-to-campaign` | campaign id (a constant) plus custom fields; run condition for tier C only (below) |

Gate the two tier-based sends with run conditions (`update_column`, `runCondition`):

```json
{"runCondition": {"enabled": true, "description": "Alert A, B and review leads",
 "condition": "['A', 'B', 'review'].includes(String(@{<Tier id>}))"}}
```

```json
{"runCondition": {"enabled": true, "description": "Nurture C leads only",
 "condition": "String(@{<Tier id>}) === 'C'"}}
```

The first goes on `Alert`, the second on `Nurture`. Section 11 adds the address check to `Alert`, `Nurture` and the CRM columns before Auto-run.

Test each one on the made-up lead in a test channel or test record before switching Auto-run on.

## 10. Qualify lead as a Function (after the test passes)

**Reusing a Function.**
- If `Qualify lead · Loopster skill` exists, skip the build: add its `run-function` column below and check the input ids and output keys with `get_function`. Price it before any run (see Cost below), run 1 made-up lead, then the rest.
- If a scoring Function fits instead, add its `run-function` column in place of `ICP fit`. Map its inputs from the columns you have (for example the fields of `Company profile`). Pull its output into a column with a Formula that parses twice and falls back to a placeholder, and change the `Tier` Formula to read its tier values. Price it, run 1 made-up lead, then the rest, and check the tier and route.
- Don't give that column the personal-email run condition: the pull-out Formula and `Tier` read it, and a column that reads a skipped column does not run (house rules, section 9). A gmail lead then pays for the scoring step unless the Function skips personal emails itself, so tell the user.

Turn sections 1 to 5 into one Function, so every lead and every future form shares the same logic. Each check below must pass before you wire the table. If one fails, keep the five columns, tell the user which check failed, and do not delete them.

Build it with `function-builder` (Step 2, "From a working table"):
- Before `create_function`, set the personal-email run condition on `ICP fit` (section 5). It comes along into the Function.
- `create_function` with the title `Qualify lead · Loopster skill`, a description that names the skill and version (`inbound-router 0.1.0`) and says "safe to edit in Loopster", and `fromTable`:
  - `columnIds`: `Domain`, `Personal email`, `Company profile`, `LinkedIn lookup`, `ICP fit`;
  - `outputColumnIds`: `Personal email`, `Company profile`, `LinkedIn lookup`, `ICP fit`;
  - `optionalInputColumnIds`: `Name`, `Message`.
- Write the `functionId` into the "Functions" section of `loopster-context.md` straight away.
- Read the new input ids and output keys with `get_function`. The output keys come from the step names: `personal_email`, `company_profile`, `linkedin_lookup`, `icp_fit`.
- Dry-run the publish and show the contract. Publish and open it to agents only after a separate yes for each.
- Price the test first: `costEstimate.maxUsdPerRun` × the number of leads, plus the AI step cost you measured on the made-up leads. `run_function` takes no `maxCostUsd`. Say the price against the test budget, ending with the pricing sentence, and ask again only if it goes over. Send `inputs` keyed by the input ids from `get_function`, one object per lead, with an `idempotencyKey`.
- Test it with `run_function` on a work-email lead, a gmail lead, a lead with a blank Name and a lead with a blank Message, and read each answer with `get_function_run`.

Then call it from the table with one column. Map every required input, and the optional `Name` and `Message` too.

```json
{"templateId": "run-function", "header": "Qualify",
 "taskConfig": {"runFunction": {"functionId": "<Qualify lead function id>",
   "inputMappings": [
     {"inputId": "<Email input id>", "mode": "column", "sourceColumnId": "Email"},
     {"inputId": "<Name input id>", "mode": "column", "sourceColumnId": "Name"},
     {"inputId": "<Message input id>", "mode": "column", "sourceColumnId": "Message"}]}}}
```

The cell holds a JSON object of the outputs, each itself JSON text. Pull each field you need into its own column with a Formula that parses twice (or a field reference whose `path` is `["<output key>", "<field>"]`). Repeat this Formula with `personal_email`, `company_profile` and, if used, `linkedin_lookup`. Use the `icp_fit` version below for the fit:

```json
{"templateId": "formula", "header": "Qualify · personal email",
 "taskConfig": {"formula": {"expression": "(() => { let c = @{<Qualify id>}; try { c = JSON.parse(c); } catch (e) { c = {}; } let v = c ? c['personal_email'] : ''; try { v = JSON.parse(v); } catch (e) {} return v === undefined || v === null ? '' : (typeof v === 'object' ? JSON.stringify(v) : String(v)); })()"}}}
```

For `icp_fit` only, return `none` instead of a blank when the Function gave no value (it is skipped for personal emails):

```json
{"templateId": "formula", "header": "Qualify · icp fit",
 "taskConfig": {"formula": {"expression": "(() => { let c = @{<Qualify id>}; try { c = JSON.parse(c); } catch (e) { c = {}; } let v = c ? c['icp_fit'] : ''; try { v = JSON.parse(v); } catch (e) {} return v === undefined || v === null || v === '' ? 'none' : (typeof v === 'object' ? JSON.stringify(v) : String(v)); })()"}}}
```

- `icp_fit` comes out as `none` when the Function skipped or gave nothing, so `Tier`, `Brief` and `Alert` still run. A blank cell would skip them, and `optionalMentions` does not help when the column before it was skipped.
- Check each new column against what the original column held on the same made-up lead.
- Point `Tier`, `Route to` and `Brief` at the new columns, and set `optionalMentions` on `Tier` and `Brief`. Each call replaces the whole list, so send the full list: for `Tier`, the new `icp fit` column id; for `Brief`, `Name`, `Message`, the company-profile pull-out id and the new `icp fit` column id. Run the made-up leads again and check the tier and route match the first test.
- Test the gmail and `review` paths:
  - (a) On the gmail lead, check that the `icp fit` pull-out reads `none`, `Tier` reads C and `Brief` is skipped.
  - (b) For `review`, take one made-up work-email lead (Auto-run off) and write `none` into its `icp fit` pull-out cell with `update_cells`. Point `Route to` at a test channel and get a yes first, because `Alert` sends. Price the re-run, since `Brief` is paid. Then call `trigger_rows` with that row's id, `columnIds: ["Tier", "Route to", "Brief", "Alert"]` and `force: true`. Check that `Tier` reads `review`, `Brief` has text and `Alert` posts to the test channel. If you kept the columns, do the same on the `ICP fit` cell.
- Ask the user, and only after a yes delete the five original columns. Until then, name only `Qualify` in triggers, so one trigger can't pay twice for the same work.
- **Cost.** The cost per lead is `Qualify` plus `Brief`, never `Qualify` alone.
  - Price `Qualify` from the Function: `get_function` `costEstimate.maxUsdPerRun` × the leads, plus its AI step measured on the made-up leads. Use `estimate_trigger_cost` for `Brief` while it is still an AI column. Say the price against the test budget, ending with the pricing sentence, and ask again only if it goes over.
  - Control the spend of a `run-function` column such as `Qualify` with the 1, 10, 100 steps, the 1.5 times stop, and `get_wallet` `consumedUsd` before and after.
  - Name `Qualify`, its pull-out columns, `Tier` and `Brief` in `columnIds`, so `Brief` really runs. Run 1 made-up work-email lead that should land in tier A or B, then 10 (post more made-up leads, each with its own email, if you need them).
  - Make the 10 a mix of tiers A, B and C that matches the form: a gmail lead skips both paid steps, and a tier C work-email lead skips `Brief`. If you don't know the mix, use mostly work-email leads that land in A or B, so the figure is a ceiling.
  - Read `get_wallet` `consumedUsd` before and after each batch. The cost per lead you quote in step 8 is the 10-lead total ÷ 10.
- **Later edits.** To change a prompt later, edit it in the Function's sandbox, dry-run, ask, republish, then run 3 to 5 made-up leads with `run_function` (priced and asked first) and read them with `get_function_run`. Re-run `Qualify` with `force: true` on the made-up test rows only. For other rows, price it first from the Function: `get_function` `costEstimate.maxUsdPerRun` × the exact `rowIds`, plus its AI step measured on the made-up leads, ask with the pricing sentence, and re-run only the rows the user names.
- **Brief as a Function.** Once the Brief reads well on the made-up leads, turn it into its own Function titled `Lead brief · Loopster skill` the same way: `create_function` with `fromTable` on the `Brief` column. `Tier` and the other columns it reads become its inputs. Record its id in the "Functions" section of `loopster-context.md`, and call it from one `run-function` column. `Alert` reads the brief through a pulled-out column (the same two-step Formula as above). Publishing it and opening it to agents each need their own yes. If the user declines, keep the column.

## 11. Valid lead gate (a run condition, free, before Auto-run)

Set a run condition on the `Qualify` column so a blank, malformed or obvious test address is skipped and a junk post spends nothing. Keep the `Email` input mapped to the `Email` column.

Call `update_column` on `Qualify` with:

```json
{"runCondition": {"enabled": true, "description": "Only for a valid, non-test email",
 "condition": "(() => { const e = String(@{Email}).trim().toLowerCase(); return /^[^@\\s]+@[^@\\s]+\\.[^@\\s]{2,}$/.test(e) && !['example.com', 'test.com'].includes(e.split('@').pop()); })()"}}
```

`Brief` and `Alert` already carry a tier condition. Write the address check and the tier check together in one `condition`, joined with `&&`, so a junk post can't reach a paid or sending step through `review`. For `Brief` (use the same for `Alert`):

```json
{"runCondition": {"enabled": true, "description": "Only for a valid email, and A, B or review",
 "condition": "(() => { const e = String(@{Email}).trim().toLowerCase(); return /^[^@\\s]+@[^@\\s]+\\.[^@\\s]{2,}$/.test(e) && !['example.com', 'test.com'].includes(e.split('@').pop()) && ['A', 'B', 'review'].includes(String(@{<Tier id>})); })()"}}
```

Do the same on `Nurture`, joining the address check to its tier C check. `CRM lookup` (HubSpot) and `CRM` have no tier check, so set the address check alone on them. Then a junk post can't reach a Slack post, a CRM record or a sequence.

If you kept the columns instead of a Function, there is no `Qualify` column: set the same address check on `ICP fit` instead, and name `ICP fit` in place of `Qualify` in the `columnIds` below.

Before Auto-run, post a malformed address to the test table. Auto-run is still off, so posting alone proves nothing: call `trigger_rows` with `columnIds: ["Qualify", "Brief", "Alert"]`, plus `CRM lookup`, `CRM` and `Nurture` if you built them, on that row. Check each cell says the condition wasn't met and `get_wallet` `consumedUsd` did not move.

## lead-score

Score and grade leads already in a Loopster table (A to D) in one step, from the fields they have, with the weights shown and the grade written into one column. Use when someone asks to score, grade or rank these leads or the rows in a table. For inbound routing (enrich, score and alert as leads arrive), use inbound-router.

# Lead score

One step: a grade per row from what the table already holds. For live inbound routing, use the `inbound-router` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Read the columns once** (`get_table`), and one page of rows to see the values.
2. **Rules from the fields present:** seniority, title words, company size, industry, location. Show the weights (for example seniority 35, title match 30, size 20, industry 15) and the grade bands (A 80+, B 60–79, C 40–59, D below 40) before writing.
3. **Write one column:** a Formula column over existing columns (free), or the grades with one `update_cells`.
4. **Missing fields** lower the score and are named. Offer free enrichment (`loopster-data-enrich-person`, `loopster-data-enrich-company`) to fill them; paid enrichment only if asked, priced first.
5. **Report** counts per grade and the top rows.

## Does not claim

- That a grade predicts a reply: it ranks the data you have.

## linkedin-profile

Find the LinkedIn profile URL of people the user names, in one step: free routes first (Loopster Data from an email, the people search from name and company), paid lookups only for the misses. Use when someone asks for LinkedIn URLs or profiles of these people, or to fill a LinkedIn column. For full profiles, current titles and company data on a list, use enrich-list.

# LinkedIn profile

One step: the profile URL. For current title, company and other fields on a whole list, use `enrich-list`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Split the people** by what they have: an email, or name + company (domain best), or neither (say how many).
2. **With an email:** `loopster-data-email-to-linkedin` on all of them in one call (free, `maxCostUsd: 0`).
3. **With name + company:** `search_people` with `personName` and `specificCompanies`, about 25 people per call (free). Accept a match only when the company matches too. Two profiles at the same company, or only an initial for a surname: mark it **ambiguous**, don't pick one.
4. **Misses only, priced first:** `surfe-find-profile` (name + company) or `icypeas-email-to-linkedin` (email) from `references/routes.md`. Show the price and ask.
5. Never use an AI web research column (`find-linkedin-url`, `ai-web`) before these routes. It is for the few rows they can't answer, after measuring 3 rows and asking.
6. **Report** found, not found and ambiguous, and the cost (zero when only free routes ran).

## Does not claim

- That the profile is current: the person may have moved since.
- A match on the name alone.

## loopster

Start here for anything in Loopster, the go-to-market data and enrichment platform. Explains what the user can get done (prospect lists, verified contacts, buying signals, inbound routing, CRM clean-up, outbound launches), picks the right Loopster play for the request, and holds the rules every Loopster skill follows, including Functions first for any job that will run again. Use when the user mentions Loopster, asks "what can Loopster do", wants leads, contacts, enrichment, signals or outbound and no other Loopster skill clearly fits, wants a job they will run again, or before a first Loopster task in a session.

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

## loopster-setup

Connect Loopster to Claude Code, Codex, Cursor, Claude Desktop or any MCP-capable AI tool, confirm the connection works, and get a first free result in about two minutes. Use when the user says "set up Loopster", "connect Loopster", "install the Loopster MCP", "Loopster isn't working", "sign in to Loopster", or when a Loopster tool is missing or answers 401/403.

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

<!-- loopster-setup/references/connect-by-tool.md -->
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

## market-size

Size a market in one free step: how many companies or people match a profile, broken down by slices such as country, size or industry, with count-only searches. Use when someone asks how many companies match, how big the market is, or for counts by country, size or industry. To build the list itself, use prospect-list.

# Market size

One step: counts, no list. To build the list, use the `prospect-list` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Filters** from the description (`list_search_filters` once, `references/icp-to-filters.md`).
2. **Count only:** one `search_companies` (or `search_people`) per slice with a small `limit`, reading the total. Searches are free. At most one call per slice; for many slices, say how many calls it takes first.
3. **Table:** slice · count, plus the total. Check the slices add up to the total; say why if not (overlap, unknown values).
4. **Say what the count is:** companies in Loopster's data that match, not the whole market.

No import and no table unless the user asks.

## Does not claim

- Revenue or spend per company: these are counts.

## outbound-launch

Take a finished list from a Loopster table and get it safely into a sequencer campaign (HeyReach, Instantly, Smartlead or Mixmax). Removes do-not-contact, people already in a campaign, and existing connections. Cleans names, checks emails, writes a personal first line per person from their signal, post or company, and has a skeptical-buyer review of the top tier. Shows samples for approval, then pushes into a paused or draft campaign one, then ten, then all, with custom fields mapped, and logs the launch for learning. Use when the user says "send this list to HeyReach", "push to Instantly", "add these to my Smartlead campaign", "launch outreach", "write first lines", or when a play hands off a list for outreach.

# Outbound launch

## What you get

The approved people in the user's campaign, with personalization fields filled. You also get:
- a launch report: who was sent, who was held back and why, and what it cost;
- a row in the campaign log of `loopster-context.md`;
- a reusable `First line · Loopster skill` Function, saved once the lines pass review (Step 2), so the next launch writes its lines with one column.

The campaign stays paused or draft. Only the user starts it.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (voice, proof, pains, do-not-contact, destinations, and the "Functions" section). You need:

1. **The list:** a Loopster table (for a CSV or pasted list, create a blank table with `autoplay: false` and `insert_rows` first, named as the house rules describe) with, per person:
   - name;
   - LinkedIn URL (LinkedIn sequencers) or a work email (email sequencers);
   - company;
   - ideally a signal or opener field from the play that built it.
2. **The destination:** the sequencer and campaign. Check `list_connections`, and ask for the campaign id. The campaign must be **paused or draft**; ask the user to confirm. Never push into a live campaign without an explicit "it's live, push anyway". Mixmax sequences may start sending as soon as a recipient is added, so treat Mixmax as live unless the user confirms otherwise.
3. **Campaign variables:** the custom fields the campaign's messages use, so the mapping matches. For HeyReach, variables are single-brace, all caps, for example `{FIRST_LINE}`; the custom field key is `FIRST_LINE`.
4. **Functions to reuse:** look in the "Functions" section of `loopster-context.md`, then `list_functions`, for `First line · Loopster skill` (match any title that starts with `First line`), `Buyer review · Loopster skill` and `Find work email · Loopster skill`. Read each one you find with `get_function`, and tell the user its steps and price. If one is still a draft, publish it first, with its own yes; a `run-function` column runs it once it's published. Open it to agents only if the user also wants `run_function` to reach it, and ask for that separately. Reuse beats rebuilding.
5. **A spend baseline:** read `get_wallet` `consumedUsd` now, for the launch report.

**Where each piece runs** (house rules, section 7). The list stays a table: the user reviews who is held back, and each push names its `rowId`s. The reusable logic lives in Functions, each called by one `run-function` column:
- first lines and the buyer review (Step 2): built as columns the first time, then saved as Functions;
- a missing work email: the `Find work email · Loopster skill` Function.

These stay table columns:
- the pre-flight lookups and the push (sequencer actions can't be Function steps);
- email checks (also not Function steps);
- do-not-contact matching, which reads the user's do-not-contact table and flags rows on the list table;
- name clean-up, a one-line Formula on this list's own name column.

Do-not-contact matching and name clean-up are tidy-up on the list table the user keeps (they review and push from it), not a repeatable job to turn into a Function.

## Step 1: Pre-flight (mostly free)

Add these checks as columns on the list table (settings in `references/preflight-and-push.md`):

1. **Do-not-contact:** read the do-not-contact table (`list_rows`), normalize its domains, emails and LinkedIn URLs the same way as the list, and flag every list row that matches any of them. Show the matches, then leave them out of the push.
2. **Already in a campaign:** `heyreach-get-campaigns-for-lead`, `smartlead-lookup-lead-status-in-campaign` or `instantly-find-lead`.
   - These run on the user's own sequencer account, so nothing is charged to the wallet. Before you add them, call `test_connection` once on that connection (its id is in `list_connections`). If it comes back `rejected`, stop and ask the user to reconnect it in Loopster: a check that errors because the key is bad is not an answer of "not in a campaign". If the provider can't be tested, go on.
   - If the workspace has more than one account for the sequencer (`list_connections`), ask which one owns the campaign, and set `integrationConnectionId` on every column.
   - For HeyReach, an error saying there is no lead record means HeyReach has never seen that person, so they are not in any campaign.
3. **Already connected (HeyReach):** `heyreach-is-connection` needs the sender's `linkedin_account_id`. The user gets it from HeyReach.
   - If the user doesn't have it, skip this check and say so.
   - Connections may need a different message, or no outreach at all.
4. **Name clean-up:** a Formula that strips emojis, titles ("Dr.", "MBA"), "| …" tails and ALL CAPS, giving a proper first name.
5. **Email check** (email sequencers): every email, free or paid, must be checked (`contact-finder` Step 3) before an email sequencer push. Found is not verified.
   - The check stays a table column (or `run_capability` on the emails). A Function finds emails but does not check them, so don't add a check step to it. The check is paid, about $0.0065 an email. Price it with `estimate_trigger_cost` on the rows that have an email, ask, run 1 row, then 10, then 100 `rowId`s at a time with `maxCostUsd` at the agreed amount, and read `get_wallet` `consumedUsd` after each step. Count it in the big-spend total (Step 2, item 3). Real usage depends on your use case and settings, so always check the final cost estimate before you run.
   - **Rows with no email:** use the `Find work email · Loopster skill` Function (see `contact-finder`), called from one `run-function` column on the list table.
     - If the Function doesn't exist yet, build it with the `contact-finder` skill.
     - Map its inputs (`get_function` lists them).
     - Don't set a run condition on this column. The `Work email` Formula below reads it for every row, and a column that reads a skipped column does not run (house rules, section 9). Trigger it with `trigger_rows` on the `rowId`s that have no email and aren't held back by checks 1 to 3, and price those same `rowId`s from the Function: `get_function` `costEstimate.maxUsdPerRun` × the number of rows. Rows you leave alone stay blank. In `update_column`, mark this column optional on the `Work email` Formula (`optionalMentions`), so a blank cell still lets the Formula run and count as no email. On your 1-row test, also check a row you did not trigger: `Work email` must return that row's own email, and the email check must complete on it. If either one skips or fails, stop and tell the user.
     - This column is paid. Price it from the Function: `get_function` `costEstimate.maxUsdPerRun` × the rows. Use this figure for the quote and the big-spend check. Ask (end the message with the pricing sentence), run 1 row, then 10, and read `get_wallet` `consumedUsd` before and after each step. Quote the rest from the real cost of the 10. Count the whole launch, not this column alone: the email finding for every row with no email, the email check, the first lines and the buyer review (Step 2; use 4 times the pre-run estimate for any AI step you have not measured yet). If it is likely over the big-spend limit in house rules section 4c (or the "Ask above" amount in `loopster-context.md`), ask with the 4c wording before the rest, and say plainly that you will control spend with the 1, 10, then 100 steps and wallet reads. Then run the rest 100 `rowId`s at a time. Read `get_wallet` `consumedUsd` after each batch, and stop and ask if a batch costs more than 1.5 times its share of the quote.
     - Don't rebuild the Function's steps as columns.
   - Pull the found email out of the cell (a Formula that parses it, or a field reference with `path`; read the output key with `get_function`). Combine it with the email already on the row in one `Work email` Formula, and point the check column at that. Read the cell on your 1-row test and write the Formula so that both a blank and a `found: false` result count as no email. Only a parsed email address goes into `Work email`. Give the check column a run condition with `update_column`, for example `String(@{<Work email id>}).includes('@')`, so it never runs on a blank, and do not rely on a blank `Work email` to skip it.

Show who's held back and why. The user can release anyone.

## Step 2: First lines

The first time, build the lines as an AI column and tune the prompt on it. When the lines pass review, save the column as a Function (item 7). If a `First line · Loopster skill` Function already exists (Before you start), reuse it (item 2).

1. **Prepare the input.** The line reads one Formula column, `Signal text`, which draws on:
   - the person's signal or opener field (from `signal-outbound` or `champion-tracker`);
   - or their engagement topic (from `engager-leads`);
   - or their recent posts (`professional-person-posts`, $0.006, opt-in);
   - or company facts.

   The inputs come from different plays, and some may be missing on a list. Coalesce them first in `Signal text`, with a fallback of `none`, so the next column never waits on a skipped column (`references/first-line-prompt.md`).
   - `professional-person-posts` can't be a Function step. Fetch the posts in a table column and feed them in through `Signal text`.
2. **Add the First line column.**
   - **No Function yet:** pick the model first (item 6). Then add an AI column, `First line`, on it. It reads `Signal text`, the company, and the voice rules from the context file. The prompt template is in `references/first-line-prompt.md`.
   - **A Function exists:** read its prompt with `get_function` and check that the offer and pain are this campaign's. If they aren't, build a second Function for this campaign (`function-builder`). Edit the existing one only if the user confirms it is only used for this campaign, after asking which tables and schedules call it, and publish after a yes. Then add one `run-function` column (`references/choosing-the-surface.md`), mapping its inputs from `Signal text` and the company column.
     - Put the line in its own `First line` column, because the push maps that column.
     - Run 1 row first (item 3) and read the cell. Then write the `First line` Formula to match what you see (the output key comes from `get_function`).
     - Use a field reference with `path` only for JSON outputs, such as the buyer review's `verdict`.
3. **Price it and ask.**
   - **AI column:** `estimate_trigger_cost` gives only a pre-run estimate, so say the real cost can be several times higher. Run 1 row with `maxCostUsd` and show the line. Then run 10 and show the lines and the real cost from `get_usage`.
   - **`run-function` column:** price it from the Function (`get_function` `costEstimate.maxUsdPerRun` × the rows, plus the AI step measured on 10 rows). Use this figure for the quote and the big-spend check. Run 1 row and show the line. Then run 10, and read `get_wallet` `consumedUsd` before and after.
   - Quote the rest from the real cost of the 10. When you ask, say how you will control the spend.
   - Count the whole job (any email finding, the email check, the first lines and the buyer review), not each batch of 100. If it is likely over $25 (or the "Ask above" amount in `loopster-context.md`), or over 10% of the wallet's `spendableUsd`, it is a big spend: ask with the wording in house rules section 4c. If the Step 1 ask already covered this whole launch at about the same amount, don't ask the same question again.
4. **Skeptical-buyer check, top tier only.** It reads each line as the recipient would. Use the list's tier column, and ask which column and value mean top tier if it isn't obvious. If the list has no tier column, review the 10 test lines only. Trigger it on those `rowId`s only.
   - If `Buyer review · Loopster skill` exists, add one `run-function` column that calls it, with a run condition (`update_column`) that is true only for the top tier (if the list has a tier column). Price it as in item 3 first, then test the condition on rows outside the top tier only: they must skip and cost nothing. The rows that should run are tested by the 1-row and 10-row runs.
   - Otherwise build a second AI column, or do your own review. Item 7 saves the column as a Function.
   - In both cases, flag anything that sounds automated, creepy, flattering, vague or wrong, plus scraping tells such as titles left in names or a company name in the wrong case.
5. **Fix the prompt, not single lines.**
   - **AI column:** rerun the 10 with `force: true` (without it, filled cells are skipped). When the user approves, run the rest with `maxCostUsd`. The cap checks only the pre-run estimate, so read `get_usage` after the 10 and quote the rest from the real cost.
   - **Function:** fix the AI step in a new sandbox, dry-run the publish, and publish after a yes. Callers run the old version until then. Then rerun the 10 with `force: true`. Run the rest 100 `rowId`s at a time, and read `get_wallet` `consumedUsd` after each batch. If a batch costs more than 1.5 times its share of the quote, stop and ask.
6. **Model** (first build only): read the template you want with `get_column_template` rather than listing every AI template. The default `ai` model writes the most specific lines. `ai-openai-gpt-5.4-mini` costs less a line and writes plainer text. Smaller "nano" models cost least and suit simple tasks.

   For a large list, compare them with two AI columns on the same 10 rows of the list table, and let the user choose. This is a one-off, so columns are the right tool. Save the winner as the Function (item 7).
7. **Save it as a Function** once the lines pass review and the user approves them. The next launch then needs one column, and any scheduled or Auto-run table can call it.
   - `create_function` with `fromTable`: the `tableId`, and the `First line` column in `columnIds` and in `outputColumnIds`. Leave `Signal text` in the table, because the columns it reads differ per list; it becomes the Function's input, with the company. Title it `First line · Loopster skill`. If a First line Function for another campaign already exists, title it `First line · <campaign> · Loopster skill` instead. Put the skill name, version and campaign in the description. When you look for one to reuse, match any title that starts with `First line`.
   - Write the `functionId` into the "Functions" section of `loopster-context.md` straight away. Drafts don't show in `list_functions`.
   - Read the new input and output ids with `get_function`, run `publish_function` with `dryRun: true`, and show the contract. Publish only after a yes, and ask again before opening it to agents (`function-builder`).
   - If you built the buyer review as a column, do the same for it, as its own Function, `Buyer review · Loopster skill`. Keep it apart from First line: a Function step runs for every input, and only the top tier should be reviewed and paid for. Next time, call it from a `run-function` column with a run condition (`update_column`) that is true only for the top tier, and test it as in item 4.
   - Leave this launch's `First line` column in place, because the push reads it. The next launch uses one `run-function` column (item 2).

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Step 3: Push (each batch needs a yes)

1. **Add the destination column** (`references/preflight-and-push.md`):
   - **HeyReach:** `heyreach-add-leads-to-campaign`, with `campaign_id`, `first_name`, `last_name`, `profile_url` and `custom_fields` `[{"key": "FIRST_LINE", "value": "@{First line}"}, …]`.
   - **Instantly:** `instantly-add-lead`, with the campaign and custom variables.
   - **Smartlead:** `smartlead-add-lead-to-campaign`, with the campaign and custom fields.
   - **Mixmax:** `mixmax-add-recipient`, with the sequence and variables.

   Each one runs on the user's own account, so nothing is charged to the wallet. Finish the First line and review columns first, and trigger the push column on its own.
2. **One person first.** Pick a held-back test contact the user controls if possible, or the first approved row. Trigger the column on that `rowId`, and have the user open the campaign to check the lead and fields.
3. **Then 10, then the rest.** Each batch needs a yes that states how many people go to which campaign. Read each cell's result; failures carry a message.
4. **Never start the campaign.** Tell the user it's ready to start in the sequencer.

## Step 4: Log it

Append to the campaign log in `loopster-context.md`:
- date;
- play;
- list;
- angle and proof;
- number pushed;
- Functions used or built (title, id, published yes or no).

Report the cost as `get_wallet` `consumedUsd` after the launch minus the baseline you read before you started. It includes Function spend.

Any Function you created in this play goes in the "Functions" section straight away, so the next launch finds it.

When results come in (replies, positive replies, meetings), use the `gtm-context` update mode so the next launch uses what worked.

## Show the result

```
Launch · Signals · hiring · 2026-10-25 → HeyReach "Q4 SDR leaders" (paused)
  Ready: 142 · held back: 31 (do-not-contact 6 · already in campaign 14 · connected 9 · bad name 2)
  First lines: 142 written · top tier reviewed (5 prompt fixes) · cost $X.XX
  Functions: First line · Loopster skill (new, published) · Buyer review · Loopster skill (new, published)
  Pushed: 142 of 142 · errors 0 · campaign still PAUSED: start it in HeyReach when ready
```

End the message with this sentence: Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## If something goes wrong

- **The push cell errors with "campaign not found" or "not active":** check the campaign id, and that the sender account is attached to the campaign.
- **Custom fields empty in the sequencer:** the keys don't match the campaign's variables. Fix the mapping (HeyReach keys are all caps, no braces).
- **Duplicate leads in the campaign:** the pre-flight lookup ran on a different campaign, or before an earlier push finished. Re-run the lookup column.
- **The `run-function` column skips rows:** a mapped input is blank. Map it from `Signal text`, which falls back to `none`.

<!-- outbound-launch/references/first-line-prompt.md -->
# First-line prompt (AI column)

The first line fills the campaign's `{FIRST_LINE}`. The campaign's message template carries the pain, proof and call to action, so the line only has to earn the second sentence.

## Before the prompt: one input column

Lists come from different plays, and some columns may be missing or skipped. Build one Formula column, `Signal text`, that combines whatever exists, with a fallback, and point the prompt at that one column. For example:

```js
(() => { const pick = (...v) => v.map(x => String(x ?? '').trim()).find(x => x && x !== 'none');
  return pick(@{<Opener id>}, @{<Engagement topic id>}, @{<Company summary id>}) || 'none'; })()
```

List each of those mentions in `optionalMentions` (`update_column`). If a column doesn't exist on this list, leave it out of the Formula.

## The prompt

Don't pass the person's name. Models tend to greet with it even when told not to. Fill the `<…>` from `loopster-context.md`.

```
You write the first line of a cold message to a <title> at @{<Company id>}.
What we know (may be "none"): @{<Signal text id>}
What we help with: <one-line offer from context>. The problem they likely feel: <pain from context>.

Write ONE sentence, 12 to 22 words, that connects the most specific fact above to a consequence for someone in their seat.
Rules:
- Do not restate their job title or start date.
- Do not start with "Stepping into", "Starting as", "Taking over", "Congrats", "I saw", "I noticed", "Hope".
- No greeting, no name, no year, no exclamation marks, no hype words (<avoid list>).
- Plain, peer-to-peer, specific. If the fact is "none", write about the problem, not about them.
Return only the sentence.
```

## Good and bad (for calibration)

- **Bad:** "Stepping into the role of VP of Sales at Acme in August means selling analytics software for finance teams." It restates the title and date, is templated, and says nothing they don't know.
- **Better:** "Selling analytics software to finance teams usually means a long list of budget owners nobody has mapped yet." A fact, then a consequence, in their world.
- **Better:** "Hedge-fund buyers rarely take a first call without a peer reference, which makes the first 50 accounts the hard part." Specific to a fund-tech seller.

## Review before scale

1. **Sameness check:** read the 10 test lines together. If 3 or more share an opening or structure, change the prompt (add the opener to the banned list) and rerun with `force: true`. If the lines come from a Function, change its AI step in a new sandbox, publish after a yes, then rerun with `force: true`.
2. **Skeptical-buyer check** (top tier only, so trigger it on the top-tier `rowId`s only): a second AI column, or your own review:

```
You are a <title> at @{<Company id>}. You get 40 cold messages a week. Read this opening line:
"@{<First line id>}"
Reply with JSON only: {"verdict": "keep|fix", "why": "one short reason"}.
Mark fix if it sounds automated or templated, flatters, guesses, gets a fact wrong, restates their title, shows a scraping tell (odd capitalisation, a company suffix like "Inc."), or could have been sent to anyone.
```

If more than 1 in 10 come back `fix`, change the prompt and rerun. Don't hand-edit single lines.

## As a Function

When both checks pass and the user approves the lines, save the column as a Function (`SKILL.md`, Step 2, items 2 and 7). Run both checks again on the first 10 lines of the next list, even though the prompt is proven.

<!-- outbound-launch/references/preflight-and-push.md -->
# Pre-flight and push columns

Every sequencer column runs on the user's own connected account (`connection: own_key`), so nothing is charged to the Loopster wallet. Set `integrationConnectionId` to the right account from `list_connections`, because a workspace can have several. Read each template's live settings with `get_column_template` before creating the column.

Sequencer actions are table columns, never Function steps. Keep the pre-flight lookups and the push here, and let a `run-function` column (First line, Find work email) feed them.

## Pre-flight lookups (read-only on the user's account)

| Check | Template | Reads |
|---|---|---|
| Already in a HeyReach campaign | `heyreach-get-campaigns-for-lead` | LinkedIn URL (or email or HeyReach id) |
| Already a LinkedIn connection | `heyreach-is-connection` | LinkedIn URL |
| Lead status in a Smartlead campaign | `smartlead-lookup-lead-status-in-campaign` | email |
| Lead exists in Instantly | `instantly-find-lead` | email |

## Name clean-up (free Formula)

```js
(() => { let n = String(@{<First name id>} || '').trim();
  n = n.replace(/\p{Extended_Pictographic}/gu, '').replace(/\b(dr|mr|mrs|ms|prof)\.?\s+/i, '').split(/[|,(]/)[0].trim();
  if (n === n.toUpperCase()) n = n.charAt(0) + n.slice(1).toLowerCase();
  return n; })()
```

## HeyReach: add to campaign

Template `heyreach-add-leads-to-campaign`, task `heyreachSendLeadToCampaign`:

```json
{"heyreachSendLeadToCampaign": {
  "campaign_id": "<campaign id>",
  "first_name": "@{<Clean first name id>}",
  "last_name": "@{<Last name id>}",
  "profile_url": "@{<LinkedIn URL id>}",
  "custom_fields": [
    {"key": "FIRST_LINE", "value": "@{<First line id>}"},
    {"key": "COMPANY", "value": "@{<Company id>}"}
  ]
}}
```

- `linkedin_account_id` is optional; it pins a sender.
- Custom field keys must match the campaign's variables. In HeyReach messages, the variable `{FIRST_LINE}` is fed by key `FIRST_LINE`.
- Related templates:
  - `heyreach-add-leads-to-list` adds to a list instead of a campaign;
  - `heyreach-stop-lead-in-campaign` removes a lead;
  - `heyreach-add-tags` tags leads.

## Instantly, Smartlead, Mixmax

| Destination | Template |
|---|---|
| Instantly | `instantly-add-lead` (add to a campaign with custom variables), or `instantly-update-lead-email` (create or update by email) |
| Smartlead | `smartlead-add-lead-to-campaign` (with custom fields) |
| Mixmax | `mixmax-add-recipient` (add to a sequence with variables) |

Read their settings schema with `get_column_template` and map variables the same way.

## Pushing safely

1. Create the push column with `autoplay` off on the table.
2. `trigger_rows` with **one** `rowId` and the push column in `columnIds`. Read the cell: success, or an error message. Have the user confirm in the sequencer.
3. Then 10 `rowIds`, then the rest, each after a yes. Nothing is charged to the wallet, so `maxCostUsd: 0` is a safe cap.
4. Run the First line column (an AI column or a `run-function` column) first, and on its own. Put only the push column in a trigger that uses `maxCostUsd: 0`.
5. Never trigger the push column without naming `rowIds`.

## prospect-list

Build a qualified prospect list from plain English or the saved ICP, as companies, people, or companies and then their decision-makers. Searches Loopster Data for free, shows counts before anything else, leaves out customers and anyone on the do-not-contact list, caps people per company, checks that each person's current title really fits, optionally scores and tiers every row against the ICP, and saves it as a Loopster table ready for contacts and outreach. Also builds lists from lookalikes of best customers and from a named account list. Reuses Functions for the steps you repeat from list to list (company check, ICP tier, lookalikes). Use when the user says "build a list", "find me prospects", "who should we target", "VPs of Sales at…", "companies like our best customers", "people at these accounts", "TAM", "score these prospects" or "tier this list". For people who are new in role (months in seat), use signal-outbound.

# Prospect list

## What you get

A Loopster table named `Prospect list · <segment> · <date>` holding the people (or companies) that match. It leaves out customers and the do-not-contact list, and has at most N people per company. It can also have a tier (A, B or C) with a one-line reason per row.

You also get the market size behind it: how many match in total, so the user knows if the list is a niche or a TAM.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` if it exists (ICP, personas, do-not-contact table, Functions). Ask only for what's missing.

If the plan has a paid step, call `get_wallet` and note `consumedUsd` and `spendableUsd`. You need both later, to report the real spend and to size a big spend. A search saved as a table is free: skip the wallet for that.

Then look for a Function that already does a step below (company check, ICP tier, lookalikes): the "Functions" section of `loopster-context.md`, then `list_functions`. If one fits, run it, or call it from one `run-function` column, instead of building columns.

## Where the work lives

- **Searching** is `search_people` and `search_companies`. It is free and not a Function step.
- **The list** is a table, because the user wants to open, filter and keep the rows, and a list is usually more than about 25 rows. If the user only wants a quick look at up to about 25 names, show them in the chat and skip the table.
- **Steps you would run again** (company check, ICP tier, lookalikes, work emails, a why-now angle) belong in a Function. The table calls it with one `run-function` column. Never copy a Function's steps into table columns.
- **Steps that can't go in a Function** stay table columns: `score-prospect`, and CRM, sequencer and Slack actions.
- **On a first list,** build the column steps below. Once they work, turn them into a Function (see "Make the repeat steps reusable") so the next list reuses them.

## Pick the route

| The user has | Route |
|---|---|
| An ICP or persona in words | A. Search |
| 5 to 20 best customers | B. Lookalikes, then C for people |
| A named list of target accounts | C. Accounts, then people |
| "Everyone we could ever sell to" | A with counts only (TAM view), then a slice |

## A. Search (free)

1. **Map the ICP to filters.**
   - Call `list_search_filters` for `people` (or `companies`) and use `references/icp-to-filters.md`.
   - For people, combine:
     - persona: `jobTitle`, `seniority`
     - company: `companyIndustry`, `companySizeBand`, `companyRevenueBand`, `companyCountry`, `companyFundingRounds`
     - location: `country`
   - **Titles:** `jobTitle` with `mode: "contains"` also matches look-alikes. Add an `exclude` list in the same envelope: AVP, EVP, Area, Associate, Fractional, Regional, Development, Engineering, Operations, Enablement, Channel, EMEA/APAC. Remove any word that appears in a title the user wants (for example Operations for "VP Revenue Operations", or for a RevOps persona), because an exclude with `mode: "contains"` drops every title that contains it.
   - **"US companies" vs "people in the US":** `companyCountry` is the company's country; `country` is the person's. For US-based buyers at US companies, send both.
   - **"Software":** use several neighbouring `companyIndustry` values (6 to 8 is normal); one value misses most of the market.
2. **Count first, with the guards on.** Run the search with `limit: 50` (the most a page takes; leave it out and later pages hold only 10, see the `fewer-requests` skill), the exclusions from step 4 (if the user has a do-not-contact table, customers or a contacted list) and the `perCompanyLimit` from step 5, all on this first call. They can't be added to a `searchId` later, and the table in step 6 keeps whatever the saved `searchId`'s call carried. Read `approximateTotal`. It is the market size for the filters and does not change with exclusions. Show the count:
   - Over 10,000: suggest narrowing (size band, region, seniority).
   - Under 50: suggest widening (more titles, more industries).
3. **Check fit.**
   - The `seniority` filter can match a past role, so read each record's current `title`.
   - Results come in index order (ascending by record id), not by relevance, so the first page is not a sample of the match set. Read the first page, then page on with `searchId`, the cursor and `limit: 50` for a page or two before you judge fit. Never page through a search to copy it into a table: step 6 imports the whole result in one free call.
   - If more than 1 in 5 is off-persona, tighten with `jobTitle` and `mode: "contains"`, plus a few precise titles.
   - A page can hold fewer records than `limit`, or none. Page on with the cursor before judging fit.
4. **Exclusions** (send them on the step 2 call; they can't be sent with a `searchId`; up to 3 lists):
   - **People searches:** the do-not-contact table's Domain column with `matches: "company"` leaves out everyone at those companies. Add a table of people already contacted, by LinkedIn URL, with `matches: "identity"`.
   - **Company searches:** the Domain column with `matches: "identity"`. `company` is for people searches only.
   - Read `applied.exclusions` in the answer to confirm they were applied.
5. **One person per company?** Set `perCompanyLimit` (2 to 3 is typical for outbound) on the step 2 call too. On a search page it applies to that page only. When you save the search as a table (step 6), the import applies it across the whole import, and the answer reports `perCompany`.
6. **Save the list.**
   - Use the `searchId` from the call that carried the exclusions and cap. If you change a filter, run the search again with the same exclusions and cap, and save the new `searchId`.
   - `create_table` with `type: "search"`, the `searchId`, a `limit` and the title. This is free.
   - A table made from a search starts with Auto-run on, so call `set_table_autoplay` with `false` before adding any column.
   - The table has name, title, company and LinkedIn columns, plus a JSON `Person record` column. Unpack what you need (company domain, role start, seniority) with Formula columns; see `references/icp-to-filters.md`, "Unpacking the person record". The JSON keys are snake_case (`company_domain`, `role_started_at`).
   - For a hand-curated list (merged searches, filtered samples), create a blank table with `autoplay: false` and use `insert_rows`.
7. **Quality check on the saved table:**
   - A large search keeps filling in the background, so wait until the table's row total in `get_status` stops growing before you count; that total is the row count, so don't read the rows back or export the table just to count them. For the per-company cap, trust the import's `perCompany` report; only when it is missing, count with one `list_rows` that reads just the domain column (`pageSize` 500). Remove extras over the cap with `delete_rows` only after you tell the user how many rows go and that it cannot be undone (house rules, section 6), and keep a CSV of the rows first.
   - **Is it the right company?** If a company check Function exists, read it with `get_function` first. If `costEstimate.maxUsdPerRun` is above 0 or it lists `unpricedSteps`, price it and ask, and run 1 row, then 10, then the rest 100 at a time. Then add one `run-function` column that calls it. Otherwise add `loopster-data-enrich-company` on the domain as a column (free). Compare its name and industry with the row, and drop or flag any row where the domain's company is not the company the person works at.
   - Spot-check that no do-not-contact domain made it in, and spot-check 10 titles: one `list_rows` call with `pageSize: 10` and only the title and domain columns.
   - Report what you removed.

## B. Lookalikes of best customers

1. Get 5 to 20 customer domains from the user, the context file, or a CRM table.
2. Run `loopster-data-enrich-company` on them with `run_capability` (free, `maxCostUsd: 0`, no table) to find the shared traits (industry, size, region). Propose those as filters for route A.
3. For named lookalikes, go cheapest first, and run each step only on the domains the step before found nothing for (a miss is text such as `{"found":false}`, not a blank cell, so read each item's `output`):
   - **Reuse first:** if the "Functions" section or `list_functions` has a lookalike Function, run it with `run_function` on the customer domains.
   - **Otherwise:** `predict-leads-find-lookalikes` ($0.0017 each). If `list_capabilities` lists it, run it with `run_capability`. If not, add it as a column on a small table of the customer domains.
   - **Then:** `ai-ark-find-lookalike-companies` as a capability ($0.013 each), only for the domains that got no result. Read each item's `output`, not only its `status`.
   - **Price it and ask first:**
     - A capability or a column: the `cost` × the number of domains. Send `maxCostUsd` and an `idempotencyKey`.
     - A Function: `costEstimate.maxUsdPerRun` × the number of domains, plus any usage-priced step measured on 10 domains. Send an `idempotencyKey`. `run_function` takes no `maxCostUsd`, so run 1, then 10, then the rest 100 at a time. Compare each batch's real cost with its quote, and stop and ask if a batch costs more than 1.5 times its share.
   - **Read a Function's results:** poll `get_run` with the batch `runId`. Right after the batch, call `get_function_run` for each domain (its `rowId` as the `runId`) and parse each output. A miss comes back as text such as `{"found":false}`, not blank.
   - **Keep the results:** save the lookalike domains in a company table the user keeps.
4. Remove existing customers and do-not-contact domains. Then find people at the lookalikes with route C.
5. If the user will run lookalikes again, turn the working step into a Function (see "Make the repeat steps reusable").

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## C. Accounts, then people

- `search_people` with `specificCompanies` (company names or domains), the persona filters, `perCompanyLimit` and the exclusions from route A, step 4. Then continue with route A, steps 3 to 7.
- Accounts with no match in Loopster Data: list them for the user. Don't guess people.

## Qualify and tier (optional, recommended for more than 200 rows)

Add one column to the table.

**Reuse first.** Look in the "Functions" section of `loopster-context.md`, then `list_functions`, for a Function that returns a tier from a title, company, industry and size (for example `ICP tier · Loopster skill`).
- Before you reuse it, read it with `get_function` and check the ICP inside it (the `@{ctx:<id>}` or prompt text) is this list's ICP. If it differs, build a variant `ICP tier · <segment> · Loopster skill` (see "Make the repeat steps reusable") instead of reusing it.
- If it fits, add one `run-function` column that calls it. Map each input id (from `get_function`) to the row's title, company, industry and size columns.
- Pull the tier into its own column with a field reference whose `path` is `["<output key>", "<field>"]`, or with a Formula that parses twice. Read the output keys with `get_function`.

**Otherwise, on the first list, use an AI column** that reads the row and returns `{"tier": "A|B|C", "reason": "…"}` against the ICP.
- Put the ICP from `loopster-context.md` in the prompt, or embed the ICP context with `@{ctx:<id>}` (the id comes from `list_contexts`).
- Price each run with `estimate_trigger_cost` (exact `rowIds` and `columnIds`), ask, and send `maxCostUsd` and an `idempotencyKey` on `trigger_rows`. The cap checks only the pre-run estimate.
- To compare models, add one AI column per model (the default `ai` and `ai-openai-gpt-5.4-mini`). Run 1 row, then 10, on each. Show both sets of tiers and reasons with the real cost from `get_usage`, let the user pick, and delete the other column.

**`score-prospect`: only if the user asks for that template.** It can't go inside a Function, so it stays a table column.
- Set `taskConfig.scoreProspect.contextId` to the ICP id and `tierCount: 3`. Point `prospectData` at the row's title, company, industry and size columns.
- It returns only the tier: `Tier 1`, `Tier 2`, `Tier 3` or `Not a fit`, with no reason. Add a Formula that maps it to A, B, C (for example `({'Tier 1': 'A', 'Tier 2': 'B', 'Tier 3': 'C'})[String(@{<ICP fit id>})] || 'out'`).
- It is priced by use. The template lists an estimate, so measure 10 rows for the real cost. The dry run lists it as unpriced, so trigger with `allowUnpriced: true` and a `maxCostUsd`, and remember the cap does not cover it.

**A `run-function` column:** quote it from its Function: `costEstimate.maxUsdPerRun` (from `get_function`) × the rows, plus any usage-priced step measured on 10 rows. Use this figure for the quote and the big-spend check. Control its spend with the 1, 10, then 100 steps, the 1.5 times stop, and `get_wallet` `consumedUsd` before and after each batch.

**Count the whole list.** Multiply the rows by the cost measured on the 10 rows (4 × the estimate until you have measured).
- Over $25 (or the "Ask above" amount in `loopster-context.md`), or over 10% of the wallet's `spendableUsd`: stop and ask in the big-spend shape (house rules, section 4c), even inside an agreed plan.
- Offer a smaller batch first, for example the rows at the best-fit titles and companies.
- After the yes, run the rest in batches. For a Function, use 100 at a time, compare each batch with its quote, and stop and ask if a batch costs more than 1.5 times its share.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Make the repeat steps reusable

The company check, the ICP tier and the lookalike step run again on every new list. On the first list, build them as the columns above. Once they have run and the user is happy with the results, turn each one into a Function so the next list calls it instead of rebuilding it. Follow `function-builder` for the build, test and publish steps.

1. `create_function` with `fromTable`: the `tableId`, the `columnIds` of that step, and `outputColumnIds` for what to return. The columns the step reads become its inputs. Return only outputs that always get a value, or are skipped by a run condition.
   - **Company check:** add a Formula column that extracts only the company name, industry and size band, and return that instead of the full profile. Write the Formula so it always returns a value: set `optionalMentions` with `update_column` and return `not found` when the profile has no name. Test it on one domain Loopster Data does not know before you create the Function.
   - **Blank inputs:** pass `optionalInputColumnIds` for inputs a row may leave blank.
   - **A step that ran as a capability** (`run_capability`) has no columns to convert. Add the same template as a column on a small scratch table (`autoplay: false`), test it on 10 domains, then `create_function` with `fromTable`. Use `function-builder` Step 2 (`add_function_step`) only when no column template exists, and test the Function on 3 samples before you use it.
   - **A paid step that must run only when an earlier one found nothing** (for example `ai-ark-find-lookalike-companies` after `predict-leads-find-lookalikes`): every step in a Function runs for every input, so use one of two routes.
     - Build both steps as columns in a scratch table (`autoplay: false`), set `runCondition` with `update_column`, test, then `create_function` with `fromTable`.
     - Or make two Functions, and run the second only on the misses of the first.
2. Title it `<Job> · Loopster skill`, for example `ICP tier · Loopster skill`, `Company check · Loopster skill` or `Find lookalikes · Loopster skill`. Put this skill's name and version in the description.
3. Write the Function id into the "Functions" section of `loopster-context.md` straight away.
4. Read the new input ids and output keys with `get_function` (they are not the table's ids). Dry-run `publish_function` and show the user the contract. Ask before publishing and before opening it to agents.
5. On the next list, add one `run-function` column that calls it. On a scheduled or Auto-run table, every firing or inserted row bills the Function: price it per month, include it in the big-spend check (house rules, section 4c), and ask before you create the schedule or turn Auto-run on. The column settings are in `references/choosing-the-surface.md`. Don't rebuild the steps as columns.

## Show the result

```
Prospect list · US fintech sales leaders · 2026-10-25
  Market: ~5,650 match · list: 400 people at 210 companies (max 2 per company)
  Left out: 38 customers, 12 do-not-contact, 21 already contacted
  Tiers: A 62 · B 211 · C 127
  Reusable: "ICP tier · Loopster skill" (id saved in loopster-context.md)
  CSV: ./prospect-list-2026-10-25.csv
  Open in Loopster: table "Prospect list · …"
```

Write the rows to a CSV from `list_rows` (house rules, section 10) and give the path.

Report the real spend: `get_wallet` `consumedUsd` now, minus the value you noted at the start. It includes Function spend (in a shared workspace, other people's runs can add to it).

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Then offer the next step:
- `contact-finder` tries free Loopster Data first, then runs the "Find work email · Loopster skill" Function on the misses, tier A and B first (one, then ten, then 100 at a time, reading `get_wallet` `consumedUsd` after each batch), then `outbound-launch`.
- For a "why now" angle, `signal-outbound` runs the "Why now · Loopster skill" Function on the companies: `run_function` for up to about 25, or a `run-function` column on a table of the company domains, one row per company, because this table has several people per company and a column runs once per row.

## If something goes wrong

- **422 "could not answer in time":** the filter combination is too heavy. Drop the least important filter, or use `limit: 10`. It's not an error in the query.
- **400 naming a filter value:** that value isn't in the index. Pick one from `list_search_filters` options.
- **400 `filter_removed`:** a filter you sent no longer exists. Drop it and use `jobTitle` and `seniority`.
- **Paging is refused:** retry the same cursor with a smaller `limit` before changing anything else. A refusal that persists at a small limit means you've reached the end.
- **Too many off-persona rows:** use `jobTitle` with exact titles, and set `seniority` explicitly.
- **A Function call is refused:** for `run_function`, it may not be published or not open to agents. A table's `run-function` column only needs the Function published. Follow the troubleshooting list in `function-builder`, and ask before changing who can run it.

## record-audit

Audit company records (from a CRM export or a Loopster table) against fresh data in one step: the free Loopster Data company lookup, a flag per mismatch with the fresh value, and no change without a yes. Use when someone asks to check, audit or validate company names, industries, sizes or locations on a list. For people records, use refresh-contacts; for a whole CRM audit with write-back, use crm-manager.

# Record audit

One step: compare company records with fresh data, once. For people, use `refresh-contacts`; for a CRM audit with write-back, use the `crm-manager` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Fields to check:** the ones the team relies on (name, industry, employee range, country). Agree on them.
2. **Free lookup:** `loopster-data-enrich-company` on every domain in one call (free, `maxCostUsd: 0`; see `references/data-routes.md`).
3. **Compare** per field: **match**, **differs** (with the fresh value), **no data**. Normalise first (case, suffixes like Inc or Ltd), so "Stripe, Inc." and "Stripe" match.
4. **Show** mismatches as record · field · on record · fresh value, and counts per field.
5. **Apply only on a yes**: write fresh values with one `update_cells` after the user agrees. Never overwrite on your own.

## Does not claim

- That the fresh value is right and the record wrong: it shows they differ, and the source.

## refresh-contacts

Check whether the people on an old contact list still work where the list says, in one step: the free Loopster Data person lookup first, a verdict per person (same, title changed, moved, unknown), and no change written without a yes. Use when someone asks to refresh, re-check or update an old contact list or CRM export, or whether these people are still at their companies. To watch past champions over time, use champion-tracker.

# Refresh contacts

One step: compare the list with fresh data, once. To keep watching people over time, use `champion-tracker`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Load once.** A file goes into a new table with Auto-run off (`insert_rows`), or read the user's table once.
2. **LinkedIn URLs first** for people who lack one: `loopster-data-email-to-linkedin` or `search_people` (`personName` + `specificCompanies`), both free.
3. **Free lookup:** `loopster-data-enrich-person` on every URL (free, `maxCostUsd: 0`). Its profiles refresh about every 55 days.
4. **Verdict per person**: **same**, **title changed**, **moved** (new company), **unknown** (no lookup). Write it into one manual column with one `update_cells`.
5. **Paid live profile** (`enrich-professional-profile`, see `references/routes.md`) only for the unknowns, or if the user asks for today's data. Price it and ask first.
6. **Apply only on a yes.** Show the changes as a list; write new titles or companies with one `update_cells` after the user agrees. Never overwrite the user's columns on your own.
7. **Report** counts per verdict and the cost. Offer `work-email` for the movers.

## Does not claim

- A move the profile doesn't show yet: profiles lag.
- That "same" is confirmed by the person: it means the lookup agrees.

## scrape-website

Pull the content of web pages into a Loopster table in one step, with the Scrape Website template, priced first. Use when someone asks to scrape, pull or copy the text of these pages or URLs into a table. To research a company across the web (news, products, who they sell to), use company-brief.

# Scrape website

One step: the text of given pages. For research across the web, use `company-brief`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **The URLs.** Full page URLs (a pricing page, a careers page). For a company's own subpages by domain, `predict-leads-website-subpages` is an alternative (see `references/data-routes.md`).
2. **Table:** the user's, or a blank one with Auto-run off and one `insert_rows` of the URLs.
3. **Column:** find the Scrape Website template with `list_column_templates` and read its `cost`. Not an AI web agent: a plain page fetch is enough for a known URL.
4. **Price** (pages · price · total), ask with the pricing sentence, then `trigger_rows` with the `rowIds`, `maxCostUsd` and an `idempotencyKey`. More than 10 pages: 1, then 10, then the rest.
5. **Named fields** (for example plan names and prices): an AI column without web search over the scraped text, priced the same way.
6. **Report** pages scraped, pages that failed and why, and the cost.

## Does not claim

- Content a page loads after sign-in or behind a script the fetch can't run.

## signal-outbound

Find accounts and people with a reason to buy now, and write the one-line why-now opener for each. Signals cover hiring for roles you sell to, fresh funding, a new sales or revenue leader in seat, a competitor or complementary tool in their stack, and launches, expansion and leadership news. Runs on a target-account list or discovers across the market, ranks by recency and ICP fit, and hands off to contacts and outreach. Use when the user says "who should we reach out to this week", "find companies hiring SDRs", "recently funded", "new VP of Sales", "companies using a certain tool", "trigger-based outbound", "signals", "why now", "refresh the signals", or "watch these accounts every week".

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

<!-- signal-outbound/references/why-now.function.md -->
# Function design: Why now · Loopster skill

Example results for two accounts:
- **An account with a recent launch:** the signal is `launch`, with its date and an opener.
- **An account with only old news:** the signal is `none`. The Function declines to invent a reason.

Typical cost is about $0.03 to $0.05 per domain at list prices, with the AI step priced by use. Measure 10 domains before you quote a big run.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Reuse or build

Look for this Function first: the "Functions" section of `loopster-context.md`, then `list_functions`. The persona keywords, the 90-day window and the ICP context are fixed inside its steps and prompt, so read it with `get_function` and compare them with the current user's. If they match, reuse it. If they differ, build a variant named `Why now · <persona> · Loopster skill` from this design.

## Title and description

- Title: `Why now · Loopster skill`
- Description: `Built by the Loopster signal-outbound skill v0.1. Open roles + recent news from PredictLeads, read by AI against your ICP. Returns the strongest buying signal and a one-line opener. Safe to edit in Loopster.`
- End the description with the settings this build uses, so a later reader can compare them: `Hiring keywords: <title_keywords>. Window: 90 days. ICP context: <icpContextId or "pasted ICP">.`

## Input

| Header | required |
|---|---|
| `Company domain` | true |

## Steps (in order)

1. **Open roles:** `predict-leads-find-jobs`, header `Open roles`. Use the hiring recipe in `signal-recipes.md`, with `title_keywords` built from the user's personas and `domain: "@{<inputId>}"`.
2. **Recent news:** `predict-leads-find-news`, header `Recent news`, with `{"execution_mode": "managed", "domain": "@{<inputId>}"}`.
3. **Why now:** template `ai`, header `Why now`, with the prompt below. Replace the ids. `<icpContextId>` comes from `list_contexts`. If there is no ICP context, paste the ICP from `loopster-context.md` into the prompt instead.

```
You help a sales team decide why to contact a company now.

Our ideal customer profile:
@{ctx:<icpContextId>}

Company domain: @{<inputId>}

Open roles posted in the last 90 days (JSON, may be empty):
@{<openRolesStepId>}

Recent company news (JSON, may be empty):
@{<newsStepId>}

Pick the single strongest, most recent buying signal that relates to our ICP. Signals that count: hiring for roles we help, funding, expansion, leadership change, product launch, acquisition, partnership. Ignore anything older than 90 days.

Answer with JSON only, no prose, in exactly this shape:
{"signal": "hiring|funding|expansion|leadership|launch|acquisition|partnership|none", "date": "YYYY-MM-DD or empty", "evidence": "one short factual phrase with the source detail", "opener": "one plain sentence a rep could open an email with, referencing the evidence, no hype, under 25 words; empty if signal is none", "fit": "high|medium|low"}
```

## Output

Return **only** the `Why now` step (`set_function_outputs` with that step id). The raw news JSON is often 20 KB or more per company. Output key: `why_now`; parse it as JSON.

## Record, publish and run

1. **Record it first.** As soon as `create_function` returns, write the Function's id in the "Functions" section of `loopster-context.md`, so the next run (or a restarted build) finds it.
2. **Ask before publishing.** Publishing, and opening the Function to agents, change what other tables and agents can run. Get a separate yes for each (house rules, sections 4b and 6).
3. After a yes: dry-run the publish, publish, then `set_function_agent_access` with `true`. Then update the "Functions" line with its version and its published and open-to-agents status.
4. **Run it.** Price it, ask, then run 1 domain, then 10, then the rest 100 at a time, as in `SKILL.md` Route 2, step 4. `run_function` takes no `maxCostUsd`, so read `get_wallet` `consumedUsd` before and after each batch, and stop and ask if a batch costs more than 1.5 times its share. For up to about 25 domains, use `run_function`. Poll `get_run` with the batch `runId`, then read each `why_now` with `get_function_run`, using `functionId` and each item's `rowId` as `runId`. For more than about 25 domains, or when the user wants the rows in Loopster, call it from one `run-function` column in a table and read the `why_now` field with a field reference whose `path` is `["why_now", "<field>"]`.

## tech-stack

Find which tools these companies use (CRM, marketing, data, cloud) in one step: tech-stack data first, AI web research only for what it can't answer, priced and agreed first. Use when someone asks whether these companies use HubSpot, Salesforce or another tool, or what their tech stack is. To turn a tool signal into outreach (switch or integrate plays with openers), use signal-outbound.

# Tech stack

One step: tools per company. For outreach built on it (switch or integrate plays), use the `signal-outbound` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Which tools?** "Everything" or named tools. Named tools are cheaper to check and clearer to report.
2. **Data route first:** `predict-leads-find-tech-stack` (see `references/signal-recipes.md`, "Tech stack", and `references/data-routes.md`). The user's own TheirStack key, if connected (`list_connections`), runs on their account.
3. **Price per company** from the live `cost`: companies · price · total. Ask with the pricing sentence. Then 1, then 10, then the rest, with `maxCostUsd` and an `idempotencyKey`.
4. **AI web research** only for companies the data route didn't cover, after measuring 3 rows and asking.
5. **Answer per company and tool:** yes, no or unknown, with the detection strength or source.
6. **Report** how many use each tool, the unknowns, and the cost.

## Does not claim

- That a tool is still in use: detections and job posts can be old.
- Tools with no public trace (internal systems).

## verify-email

Run one email verifier over addresses the user already has and sort them into send, risky and do not send, in one step, priced and agreed first. Use when someone asks to verify these addresses, check whether these emails are valid, or add a verification column to a table. To clean a whole list before a campaign (duplicates, role and disposable addresses, then verification), use email-check.

# Verify email

One step: one verifier over addresses that are already clean. To clean a list first (duplicates, malformed, role and disposable addresses), use `email-check`. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Steps

1. **Drop what needs no check:** exact duplicates and text that is not an email address. Say how many.
2. **Choose the verifier** from `references/routes.md` ("Email checks"): the user's own connected account if they have one (`list_connections`), otherwise one that runs on Loopster's account. As a capability it may need a provider default; ask before `set_provider_default`.
3. **Price one call for all addresses** (a capability takes up to 1,000 inputs; a table column runs on the rows you name). Show addresses · verifier · price · total, and ask with the pricing sentence.
4. **Run once on a yes**, `maxCostUsd` and an `idempotencyKey`. Never one call per address.
5. **Sort** into **send** (valid), **risky** (catch-all, unknown, role address) and **do not send** (invalid, disposable), with counts.

## Does not claim

- That a valid result on a catch-all domain proves anything: such a server accepts every address.
- That the mailbox belongs to the intended person, or that the verdict stays true later.

## work-email

Find the work email of a few named people, or of the people in one table column, in one step: the free Loopster Data lookup first, then one paid finder only for the people it missed, priced and agreed first. Use when someone asks for the work email of these people, an email for this LinkedIn profile, or to fill an email column once. For a repeat job (every week, new people keep coming) or emails plus phones for a whole list, use contact-finder.

# Work email

One step: work emails for the people the user names, now. For a job that repeats or covers emails and phones together, use the `contact-finder` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Inputs

- Per person: a **LinkedIn URL** (best), or **name + company domain**.
- A few people in chat, a CSV, or a column in a Loopster table.

## Steps

1. **Free pass.** Run `loopster-data-find-work-email` (needs `linkedin_url`) on every person in one call: `run_capability` with all inputs and `maxCostUsd: 0`, or a column in the user's table. People with only name + domain and no URL: find the URL first with `search_people` (`personName` + `specificCompanies`, free).
2. **Count the misses.** Found, not found, and no input. Stop here if every person was found.
3. **Price the misses only.** Take the next route from `references/routes.md` ("Work email"), cheapest first, and read its live `cost`. Show: people left · route · price per person · total. Ask, with the pricing sentence.
4. **Run on a yes**, on the misses only, with `maxCostUsd` and an `idempotencyKey`. More than 10 people: 1, then 10, then the rest (house rules, section 5).
5. **Report** found free, found paid, not found, and the real cost (`get_usage`).

No Function and no new table for a one-off: those are for jobs that repeat (`contact-finder`).

## Does not claim

- That an address on a catch-all domain will deliver. Offer `verify-email` for those.
- That "not found" means the person has no work email: only that no route had it.

## work-phone

Find mobile or direct phone numbers for a few named people in one step: the free Loopster Data lookup first, then one paid finder only for the misses, priced and agreed first. Use when someone asks for phone numbers, mobiles or a direct line for these people or LinkedIn profiles. For emails and phones for a whole list, or a job that repeats, use contact-finder.

# Work phone

One step: phone numbers for the people the user names, now. For emails and phones together, or a repeat job, use the `contact-finder` workflow. Read `references/house-rules.md` once per session (price, ask, cap; 1 row, then 10, then all; nothing leaves Loopster without a yes), and keep the calls few (the `fewer-requests` skill).

## Inputs

- Per person: a **LinkedIn URL**. Every phone route needs it (some also take domain + full name).
- People with only an email: get the URL first with `loopster-data-email-to-linkedin` (free).

## Steps

1. **Free pass.** `loopster-data-find-phone-number` on every person in one call (`run_capability`, `maxCostUsd: 0`, or a table column).
2. **Count the misses.** Found, not found, no LinkedIn URL.
3. **Price the misses only** from `references/routes.md` ("Mobile phone"), cheapest first, live `cost`. Phone routes cost far more than email routes: show people left · route · price · total, and ask with the pricing sentence. A big spend (house rules, section 4c) needs that exact question, in any mode.
4. **Run on a yes**, on the misses only, `maxCostUsd` and `idempotencyKey`; 1, then 10, then the rest.
5. **Line type** (mobile or landline) only if asked: `clearout-phone-validate-phone`, priced separately.
6. **Report** found free, found paid, not found, real cost.

## Does not claim

- That a number is a mobile, unless a line check said so.
- That the person answers it: it is a provider's record, not a confirmed direct line.
