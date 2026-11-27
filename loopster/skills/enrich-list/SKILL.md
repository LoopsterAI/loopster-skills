---
name: enrich-list
description: Add data to a list of companies or people (a CSV, a pasted list, a Loopster table or one record), such as industry, headcount, HQ, LinkedIn URLs, job titles, tech stack, funding, open roles, or website summaries, using free Loopster Data first and the cheapest paid source only where needed. Runs once with no table, or as a reusable Function when the same enrichment will run again. Use when the user says "enrich this list", "add industry and size", "fill in the LinkedIn URLs", "find their LinkedIn profiles", "get the latest LinkedIn profile", "what is their current job or title", "what tech do these companies use", "add funding", "add open roles and news", "enrich every new batch of leads", or uploads a CSV and asks for more columns. For emails and phone numbers use contact-finder.
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

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
