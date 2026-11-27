---
name: prospect-list
description: Build a qualified prospect list from plain English or the saved ICP, as companies, people, or companies and then their decision-makers. Searches Loopster Data for free, shows counts before anything else, leaves out customers and anyone on the do-not-contact list, caps people per company, checks that each person's current title really fits, optionally scores and tiers every row against the ICP, and saves it as a Loopster table ready for contacts and outreach. Also builds lists from lookalikes of best customers and from a named account list. Reuses Functions for the steps you repeat from list to list (company check, ICP tier, lookalikes). Use when the user says "build a list", "find me prospects", "who should we target", "VPs of Sales at…", "companies like our best customers", "people at these accounts", "TAM", "score these prospects" or "tier this list". For people who are new in role (months in seat), use signal-outbound.
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

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
