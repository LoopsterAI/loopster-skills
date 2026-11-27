---
name: contact-finder
description: Find work emails, mobile numbers and personal emails for people you already have (a CSV, a Loopster table, a search result or a pasted list), free Loopster Data first, then paid providers only for the misses, with an email check and a spending limit agreed up front. Reuses the "Find work email" Function (builds it on first use), and builds "Find mobile phone" or "Find personal email" Functions when the lookup will run again. Use when the user says "find emails for", "get phone numbers", "get contact details", "I need verified emails", "find their mobile", "enrich this list with contacts", "find work emails for this list", or when another play needs contacts before outreach.
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

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
