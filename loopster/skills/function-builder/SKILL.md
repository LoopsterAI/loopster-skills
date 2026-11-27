---
name: function-builder
description: Turn a job someone repeats into a reusable Loopster Function, a one-call tool with named inputs, steps (AI, Formula, waterfalls, PredictLeads, Loopster Data and other provider actions) and named outputs, that runs on one record or a list of up to 1,000 with no table, from any AI agent or the API. Designs it, builds it (in a sandbox, or from tested table columns), tests it on samples, publishes it, opens it to agents, and documents how to call it. Also edits, republishes, retires and restores Functions. Also puts a Function into a table as one run-function column, so tables stay thin. Use when the user says "make this reusable", "build a function that…", "I do this every week", "we'll run this again", "turn this into a tool", "edit my Loopster function", or when a play needs a Function that does not exist yet. Any job that will run again belongs in a Function (house rules, section 7).
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

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
