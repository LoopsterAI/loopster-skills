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
