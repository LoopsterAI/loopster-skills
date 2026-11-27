---
name: crm-manager
description: A RevOps assistant for HubSpot, Salesforce or Attio data in Loopster. It audits CRM records (fill rates, duplicates, personal or invalid emails, missing LinkedIn and firmographics, contacts who changed jobs) and gives a health score with the cost to fix each issue. It fills the gaps free first, proposes every change for review, writes back only approved changes (blanks only, by default), revives closed-lost deals that show a new reason to talk, and can keep the CRM fresh on a monthly schedule. The gap fills and the work-email search become reusable Functions, so the next audit reuses them. Use when the user says "clean my CRM", "audit HubSpot", "fill missing fields", "fill CRM gaps", "dedupe contacts", "who in our CRM changed jobs", "enrich our accounts in Salesforce", "revive closed-lost", or "keep our CRM up to date".
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

# CRM manager

## What you get

- **A health report:** fill rate per key field, duplicates, bad or personal emails, job changes and stale records, each with the cost to fix. The audit is free and needs no table.
- **A fix table in Loopster,** made when the user picks fixes, showing current value next to proposed value for every record, so the user approves before anything changes.
- **Write-back** of approved changes only. By default it fills blanks and never overwrites, and tests 1 record, then 10, then all.
- **Reusable Functions:** the free gap fills become a "Fill CRM gaps · Loopster skill" Function after the first run, and the paid email search is the "Find work email · Loopster skill" Function. The job-change check is the "Job change check · Loopster skill" Function that `champion-tracker` builds. The next audit reuses all three. The monthly refresh reuses only the free ones (gap fills and job-change check); the paid email search runs by hand.
- **Optionally:** a closed-lost revival list, and a monthly refresh created paused.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (ICP, destinations).

Then check for Functions to reuse: the "Functions" section of `loopster-context.md`, then `list_functions`. Look for **Fill CRM gaps · Loopster skill**, **Find work email · Loopster skill**, **Job change check · Loopster skill** and **Why now · Loopster skill**. Read each one you find with `get_function`, and tell the user its steps and price.

Then find the records:

| Where the CRM data is | How |
|---|---|
| A Loopster table imported from HubSpot or Salesforce (Loopster → new table → HubSpot or Salesforce import) | `list_tables` with `search: "HubSpot"` or `"Salesforce"`. These tables have a record column, reference columns per property, and a `Record ID`. |
| No import yet | Ask the user to create one in Loopster (it syncs fields and keeps the record id for write-back), or to export a CSV with the record id column. |
| Attio | A CSV with record ids, or the `attio-find-record` column per row. |

Check `list_connections` for the CRM account, and make sure it's the right portal or org. A workspace can have several HubSpot connections, so confirm which one is production and which is a test.

Step 1 makes no table. The working copy is made in Step 3, once the user has picked fixes.

## Step 1: Audit (free, no table)

Read every record from the import table (`references/audit-checks.md` says how, for a large table and a small one) and compute the checks with a local script, without paid calls:

- **Fill rate** per field: email, first and last name, title, company, domain, LinkedIn URL, industry, size, country, phone.
- **Duplicates:**
  - same normalized email;
  - same LinkedIn URL;
  - same first and last name plus company domain;
  - for companies, the same normalized domain.
- **Email quality:** personal domains (gmail and similar), role inboxes (info@, sales@), malformed addresses.
- **Mismatches:** email domain ≠ company domain.

Show a health score (the share of records with all key fields valid) and the top issues with counts.

If the user only wanted a health report, give it in chat and save the issue lists and duplicate groups as CSV files in their working folder (house rules section 10). Create no table.

## Step 2: Price the fixes

Show one table: issue · records · fix · source · runs as · price (estimate).

| Issue | Records | Fix | Source | Runs as | Price |
|---|---|---|---|---|---|
| Missing LinkedIn URL | count | Find from email | `loopster-data-email-to-linkedin` | Fill CRM gaps Function | free |
| Missing title or company (has LinkedIn) | count | Person profile | `loopster-data-enrich-person` | Fill CRM gaps Function | free |
| Missing industry or size or country (has domain) | count | Company profile | `loopster-data-enrich-company` | Fill CRM gaps Function | free |
| Missing work email | count | Find email | **Find work email · Loopster skill** (free Loopster Data step first, then Icypeas, then Findymail) | Function, from a `run-function` column | free first, then paid |
| Unverified emails | count | Check | `zero-bounce-validate-email` | Table column (`execution_mode: "managed"`); `run_capability` only when `list_provider_defaults` shows a ZeroBounce account or the user has their own key (`contact-finder`, Step 3) | $0.0065 per email |
| Changed jobs | count | Compare current company | **Job change check · Loopster skill** (built by `champion-tracker`) | One `run-function` column; if the Function doesn't exist yet, run `champion-tracker` first | free |
| Duplicates | count | Merge list for the user (CRMs merge in their own UI) | none | Local script | free |

- For a Function row, the estimate is a floor, because usage-priced steps add to it. Step 3 measures the real cost on 10 records, and you quote the rest from that.
- Email checks are table columns or capabilities, because a Function cannot hold them. A Function can find emails but cannot verify them.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Ask which fixes to run. In the plan, say what you will create: the working table and, once the free fill columns work, the Fill CRM gaps Function. For gaps the free sources leave, use the paid routes in house rules section 3b. Never fill CRM fields with an AI web research column first; a CRM-wide fill is usually a big spend (section 4c).

## Step 3: Propose changes (no CRM writes yet)

Step 3 goes in this order: working copy, gap fills, job changes, work email and email check (only if picked), then proposed values and review.

**Working copy (skip it for about 25 records or fewer with no write-back: see the next paragraph).** Read the import table's rows (as in `references/audit-checks.md`) and insert them into a working table `CRM health · <CRM> <object> · <YYYY-MM-DD>` (for example `CRM health · HubSpot contacts · 2026-10-25`) (blank, `autoplay: false`) with the record id. Never add columns to the live import table if it has Auto-run on.

To look at a handful of records (up to about 25) with no write-back, and with the Fill CRM gaps Function already built, skip the table. Run the Function with `run_function`, read each result with `get_function_run`, and compare with the CRM values yourself.

**Gap fills (free).**
- **The Fill CRM gaps Function exists:** add ONE `run-function` column. Map its inputs (email, LinkedIn URL, company domain; input ids from `get_function`) to the table's columns. Mark the source columns of its optional inputs (email, LinkedIn URL, company domain) optional with `update_column` and `optionalMentions`, because a record may lack any of them. Don't copy its steps into columns.
- **First build, no Function yet:**
  1. Add one column per free fix from Step 2 (`loopster-data-email-to-linkedin`, `loopster-data-enrich-person`, `loopster-data-enrich-company`), and test them on 10 rows as in "Proposed values and review" below.
  2. Once they work, turn them into a Function with `create_function` and `fromTable` (see the `function-builder` skill). Its inputs are the CRM columns the fixes read (mark the ones a record may lack as optional). Return only outputs that always get a value, for example a Formula with a fallback.
  3. Name it **Fill CRM gaps · Loopster skill**, and record its id in the "Functions" section of `loopster-context.md`.
  4. Publishing it and opening it to agents each need their own yes (house rules section 4b).
  5. This table keeps its first-build columns. From the next audit on, and for any scheduled table, use one `run-function` column instead.

**Job changes (free).**
- **The Job change check Function exists:** add ONE `run-function` column. Map its LinkedIn URL input to the record's LinkedIn URL (the CRM value, or the one the gap fill found; a Formula column can pick whichever has a value). Map its "Company when champion" input to the CRM company domain. Input ids come from `get_function`.
- Run that column on 1 row and read its cell first, to see its shape. Then add a `Moved` column that reads the `moved` output: a Formula that parses the cell (parse twice only if the output is itself JSON text), or a field reference whose `path` starts with `["moved"]`. `get_function` lists the output keys; `list_columns` does not. `Moved` should read `yes`, `no` or `unknown`.
- **No Function yet:** run the `champion-tracker` skill on a small table first so it builds `Job change check · Loopster skill`, or leave job changes out of this audit and say so. Record the id in the "Functions" section of `loopster-context.md`.
- Never copy the Function's steps into columns.

**Work email (paid, only where needed).**
- Add one `run-function` column calling **Find work email · Loopster skill** (id in the context file, or `list_functions`; if it's missing, build it with the `contact-finder` skill). Map First name, Last name, Company domain and LinkedIn URL (optional).
- Check the domain. The `Proposed work email` Formula returns the Function's `work_email` only when its domain equals the CRM company domain, and returns an empty string otherwise (a miss such as `{"found":false}` also counts as empty). List the mismatches as "needs review" in the review summary. Never propose an email at a previous employer's domain (`contact-finder`, "Domain guard").
- Run it only for records that need it. Add a free Formula column `Needs work email` that always returns `yes` or `no`: yes when the CRM email is blank and the record has a name and a company domain. Mark every column the Formula reads optional (`optionalMentions`: CRM email, first name, last name, company domain), so a blank value still lets it run and it always returns `yes` or `no`.
- Do not set a run condition on the work-email column. A column that reads a skipped column does not run (house rules, section 9), and `Proposed work email` reads this column on every row. Trigger it with `trigger_rows` on the `rowId`s where `Needs work email` is `yes`, and always name those `rowId`s. Never trigger this column without `rowIds`. Cells you don't trigger stay blank, and `optionalMentions` lets a blank through. After each batch, re-run `Proposed work email` (and `Write payload`, once it exists) on those rows with `force: true`.
- On the work-email `run-function` column, mark the source column of the Function's optional input (LinkedIn URL) optional with `update_column` and `optionalMentions`.
- Do not run this column yet. Price it, ask and run it in item 3 of "Proposed values and review" (1 row, then 10). Pick the 10 rows from those where `Needs work email` is `yes`, and include records with no LinkedIn URL (they must still run, not skip). If one comes back skipped, fix the optional mentions and re-run only that record: `trigger_rows` with its `rowId` and the work-email column in `columnIds`, and no `force`. Without `force`, a skipped cell runs again and the cells that already hold an answer are kept; `force: true` would bill them again. Then read `Proposed work email` (and `Write payload`, once it exists) on a row you did not trigger: both must complete. If they fail, add a `manual` column `Found work email`, write the parsed emails into it with `update_cells`, and point `Proposed work email` at that column.

**Email check (paid, only if the user picked it).** Add a `zero-bounce-validate-email` table column (`execution_mode: "managed"`) that reads the CRM email. Price it with `estimate_trigger_cost` on the rows that have an email, ask, and run 1 row, then 10, then 100 `rowId`s at a time with `maxCostUsd` at the agreed amount. Read `get_wallet` `consumedUsd` before and after each batch. If the whole job is over $25, use the 4c wording. Keep it out of any schedule. Flag invalid emails in the review summary, and never delete or overwrite the CRM email.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

**Proposed values and review.**
1. Add one `Proposed <field>` Formula per field: it uses the found value only where the CRM value is blank, unless the user chose "overwrite".
   - A `run-function` cell holds a JSON object of the Function's outputs, each itself JSON text. Read a field with a Formula that parses twice, or a field reference with `path` `["<output key>", "<field>"]` (`get_function` lists the output keys; `list_columns` does not).
   - Mark the `run-function` columns optional in each Proposed Formula, and give each a fallback so it always completes.
2. Run the free columns on 10 rows, show current vs proposed, then run the rest. Include records that lack an email, LinkedIn URL or company domain in the 10.
   - First-build columns: use `maxCostUsd: 0`.
   - Each free `run-function` column (Fill CRM gaps, Job change check): check with `get_function` that `costEstimate.maxUsdPerRun` is 0 and the Function lists no `unpricedSteps`. Read `get_wallet` `consumedUsd` before and after the 10 rows; it must not move.
3. Run the work-email column on its own, never in the same trigger as a write-back column:
   - Quote it from its Function: `get_function` `costEstimate.maxUsdPerRun` × the number of `rowId`s where `Needs work email` is yes, plus any usage-priced step measured on 10 rows. Use this figure for the quote and the big-spend check. Control its spend with the 1, 10, then 100 steps, the 1.5 times stop, and `get_wallet` `consumedUsd` before and after each batch (the next bullets).
   - Run 1 row, then 10. Read `get_wallet` `consumedUsd` before and after the 10 (in a shared workspace, other runs can add to it). Show the hit rate and the cost.
   - Quote the rest from that measurement and get a yes. If it is a big spend (section 4c), use the 4c wording.
   - Run the rest in batches of 100. After each batch, compare its real cost with its share of the quote, and stop and ask if it costs more than 1.5 times that.
   - Report the real cost from `get_wallet` `consumedUsd`, which includes the Function.

   Real usage depends on your use case and settings, so always check the final cost estimate before you run.
4. Give the user a review summary: "Industry: fill 412 blanks. Title: fill 96 blanks, 31 differ from the CRM (not changed). Emails: 87 invalid (flagged, not changed). Job changed: 27 contacts."
5. Job changes (the contacts where `Moved` is `yes`) are their own list. Don't overwrite the contact's company; that loses history. Suggest the CRM's own process: mark them, then create a new contact at the new company.

## Step 4: Write back (only with a yes)

1. **Check automations first.** Ask the user whether a CRM workflow or flow fires on these property changes; one could email the contacts. Pause it or exclude these records before writing.
2. **Write-back column:**
   - **HubSpot:**
     - First build a blank-safe `Write payload` Formula that holds only the approved fields with a value, and a `Has payload` flag that the write-back column's run condition reads (`references/writeback.md`).
     - Then add `hubspot-update-object`, with `mode: "update"`, `objectType` (contacts or companies), `recordId: "@{Record ID}"` and `properties: "@{Write payload}"`. Use the CRM's internal property names (for example `industry`, `jobtitle`, `hs_linkedin_url`).
     - Set `integrationConnectionId` to the right HubSpot connection.
     - Never map proposed columns straight into `properties`, because a blank could clear the field.
   - **Salesforce:** `salesforce-upsert-object` with an external id, or `salesforce-update-object` with the record id.
   - **Attio:** `attio-send-record`.

   Settings are in `references/writeback.md`. CRM writes are table columns, so the working table stays.
3. **One record first.** Trigger the write-back column on its own, on 1 row, and have the user check the record in the CRM (nothing else changed). Then 10, then the rest.
4. **Each batch needs its own yes.** Report what was written: record count, fields, and any errors from the cell messages.
5. **Changing the proposal after the user approved it.** A `Proposed` or `Write payload` Formula recomputes at once, so the edit changes what the next batch writes. First try it in a table sandbox (house rules, section 5b): open it with `mode: "explicit"` and the `rowIds` of a few records the user already checked, and show the new payload next to the old one. Publish after a yes, then ask the user to approve the review again before any further write. Never run the write-back column in a sandbox: its rows are real CRM records.

## Closed-lost revival (optional)

1. Get closed-lost deals with their company domain and loss date: an import of deals, or a CSV.
2. For deals lost 3 to 24 months ago, look for a new reason to talk:
   - the champion moved, or a new leader is in seat (`champion-tracker`, or `signal-outbound` route 1);
   - a funding, hiring or launch signal: run **Why now · Loopster skill** on the deal domains (id in the context file, or `list_functions`; if it's missing, build it with the `signal-outbound` skill, which holds the design).
3. Pick the path before you run anything. Up to about 25 deals and no CRM write: no table. Run **Why now · Loopster skill** with `run_function`, read each result with `get_function_run`, and save the ranked list to a CSV. More than about 25 deals, or tasks or a list wanted in the CRM: use the table in item 5, and read the ranking from its cells.
   - Price it first (`costEstimate.maxUsdPerRun` × deals; usage-priced steps add to it) and ask.
   - Run 1 deal, then 10, then the rest, and read `get_wallet` `consumedUsd` before and after each step.
4. Rank by signal strength, and write one sentence per deal: what changed, plus a suggested opener.
5. Offer to create tasks or a list in the CRM, with a yes. That needs a table: the deals, one `run-function` column calling the Why now Function, and a write-back column.
   - Quote the `run-function` column from its Function: `get_function` `costEstimate.maxUsdPerRun` × the rows, plus any usage-priced step measured on 10 rows. Use this figure for the quote and the big-spend check. Control its spend with the steps in the next bullet: 1, 10, then 100 at a time, the 1.5 times stop, and `get_wallet` `consumedUsd` before and after each batch.
   - Run 1 deal, then 10. Quote the whole job from the real cost of the 10. If it is likely over $25, the "Ask above" amount in `loopster-context.md`, or 10% of `spendableUsd`, ask with the wording in house rules section 4c. Then run 100 at a time, read `get_wallet` `consumedUsd` before and after each batch, and stop and ask if a batch costs more than 1.5 times its share of the quote.
   - Write-back follows Step 4, with its own yes.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Keep it clean (optional)

Offer a monthly refresh. A schedule runs table columns only, and it is created paused, so:

- Use a table whose free work sits behind `run-function` columns: one calling **Fill CRM gaps · Loopster skill** and one calling **Job change check · Loopster skill**, plus the Formula columns that read them (for example `Moved`). Don't schedule copied step columns.
- On the first-build table, add the `run-function` columns beside the first-build columns (give them a different header), and schedule only the `run-function` columns and the Formulas that read them.
- Schedule only columns that cost nothing. Prove it first: `get_function` must show `costEstimate.maxUsdPerRun` 0 and no `unpricedSteps`, and `get_wallet` `consumedUsd` must not move on a 10-row run.
- Keep the **Find work email · Loopster skill** column out of the schedule. Its paid steps would charge every month. Run it by hand when the user asks.
- Create the schedule with `paused: true` and `cells: "all"`: every column in it is free, and the job-change check must re-run on every row each month. This is the "price the full re-run" option in house rules, section 9, and it costs $0 only after you prove it (see below). If you ever add a paid column, send `cells: "empty"` or price every firing.
- Name in `columns` (the `create_schedule` parameter; `columnIds` belongs to `trigger_rows`) only the free `run-function` columns and the Formula columns that read them, and leave `rerunDependents` off (its default), so the work-email column and the write-back column never fire from the schedule. After you create it, read `list_schedules` and check it lists exactly those columns.
- A schedule re-runs only the rows the table holds; it does not re-read the CRM. New CRM records appear only when you re-read the import table (`references/audit-checks.md`) and insert them as rows, so tell the user that is a step to repeat before the monthly firing. The free columns then run on the new rows and re-check the old ones.
- Before resuming, run the schedule's columns by hand on 10 rows with `trigger_rows`, and read `get_wallet` `consumedUsd` before and after (it must not move). `get_function` should show `costEstimate.maxUsdPerRun` 0 and no `unpricedSteps`.
- Resume only after a separate yes (house rules sections 4b and 6). After every firing, read `consumedUsd` again. If it moved, pause the schedule and tell the user. Before each firing, if anyone has edited the Fill CRM gaps or Job change check Function, read `get_function` again: if `costEstimate.maxUsdPerRun` is above 0 or `unpricedSteps` appears, pause the schedule and ask. If the monthly cost could be a big spend, use the 4c wording.
- Write-back columns stay manual unless the user explicitly asks for automatic write-back after seeing several clean runs.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Show the result

```
CRM health · HubSpot contacts · 2026-10-25   (8,412 records)
  Health score: 61% → 84% after fixes
  Filled (free): LinkedIn 1,920 · title 640 · industry 2,310 · size 2,288
  Emails checked: 1,104 · invalid 87 (flagged, not deleted)
  Duplicates: 214 groups (list saved for merge in HubSpot)
  Job changes: 312 (list saved → champion-tracker / outbound)
  Functions: Fill CRM gaps · Loopster skill, Find work email · Loopster skill, Job change check · Loopster skill (ids in loopster-context.md)
  Written to HubSpot: 5,158 fields on 3,902 records (blanks only)  · real cost $X.XX
```

Take the real cost from `get_wallet` `consumedUsd` before and after the play, so it includes the Functions. Then add the pricing sentence:

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## If something goes wrong

- **The write-back cell errors with a property name:** the CRM's internal name differs from the label. Ask the user for the internal name (HubSpot property settings), and fix the mapping.
- **Wrong portal:** stop. Check `integrationConnectionId` against `list_connections` before any further batch.
- **The import table has Auto-run on:** don't add columns to it. Work on a copy.
- **A work-email cell is blank:** you did not trigger that row, which is right for a record that already has an email.
- **A Function output reads `{"found":false}`:** that is a miss, not a blank. Parse the text, and leave the CRM field alone.
