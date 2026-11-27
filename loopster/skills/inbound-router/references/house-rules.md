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
