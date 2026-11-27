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
