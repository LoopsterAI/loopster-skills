---
name: fewer-requests
description: Do the same Loopster work in fewer API requests. Every Loopster MCP tool call is one request against the workspace's per-minute and per-day limits, so this skill plans the calls first, then searches with full pages, imports search results instead of copying them, writes and runs in bulk, waits on the cheap status call, and reads only the rows it needs. Use for any Loopster task that will take more than a few tool calls (searching, loading rows, running columns, waiting for a run, reading results, finding failed rows, fixing cells), near a request limit, or after a 429 "too many requests" answer.
license: MIT
metadata:
  author: Loopster
  version: "0.2.0"
---

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
