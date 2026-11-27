---
name: inbound-router
description: Build an inbound lead router in Loopster. Every form fill, signup or demo request posted to a webhook is enriched within minutes (free sources first), checked for personal emails, scored against the ICP, given an owner, and pushed where it should go. That can be a Slack alert with a short brief and a drafted reply, the CRM (update, or create after a test), or a sequencer campaign for the rest. The repeated qualify logic lives in a reusable Function that the webhook table calls from one column. Built step by step, tested with a made-up lead, and switched on only after a yes. Use when the user says "route inbound leads", "speed to lead", "enrich form fills", "qualify demo requests", "qualify inbound leads", "alert sales in Slack when a good lead signs up", or "send signups to HubSpot".
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

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
