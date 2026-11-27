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
