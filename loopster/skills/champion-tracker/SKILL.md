---
name: champion-tracker
description: Turn your happiest customers' people into pipeline. Finds customer alumni, people who used your product at a past company and now hold a buying role at an ICP company (free search). Also keeps a champion watchlist that checks every month, at no cost, whether past champions, power users or lost-deal contacts have changed jobs. Flags moves into ICP companies, finds who replaced a champion who left a customer, alerts the owner, and drafts a personal note. Builds the job-change check once as a reusable Function. Use when the user says "track job changes", "champion tracking", "where did our champions go", "have these people moved", "people who used us before", "customer alumni", "warm intros", or "who left our customers".
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

# Champion tracker

## What you get

- **Customer alumni:** a list of people who worked at your customers, now at ICP companies in a buying role. They already know what you do.
- **Champion watchlist:** a Loopster table that re-checks every champion's current employer, plus a monthly schedule (paused until you say yes). Each move is flagged as **joined an ICP company** (outreach) or **left a customer** (a risk: find the replacement).
- **A reusable Function:** `Job change check · Loopster skill`, built from the watchlist's check columns once they work. Any later list, and the scheduled table, calls it instead of rebuilding the columns.
- **For each move:** a short personal draft and an alert to the owner (Slack or CRM), always after a yes.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (ICP, customers list, voice, destinations).

Then check what already exists (house rules, section 2):
- the "Functions" section of `loopster-context.md`, then `list_functions`, for `Job change check · Loopster skill` and `Champion note · Loopster skill`. If the check is there, use it in Play 2, step 2, and don't build the check columns. If the note is there, use it in Play 2, step 7;
- if an id is only in `loopster-context.md`, read it with `get_function`. If it is still a draft, publish it (with a yes, as in "Turn the check into a Function") before you add the `run-function` column. The column doesn't need the Function open to agents;
- `list_tables` with `search` for an existing `Champions · watchlist`.

You need your customer list (company names and domains) and, for the watchlist, your champions:
- name;
- LinkedIn URL (best);
- the company they were at when they championed you.

Champions can come from a CSV, the CRM (closed-won contacts, power users, closed-lost contacts) or an existing Loopster table.

Show the plan in a few lines before you start (house rules, section 4b): the table, the Function you will build after the first run, the monthly schedule (created paused, with its own yes) and the budget. The job-change check itself is free.

## Which surface

| The job | Use |
|---|---|
| Customer alumni, and who replaced a champion | `search_people`, saved as a search table. A search is never a Function step. |
| "Have these people moved?" once, for about 25 people or fewer, no table wanted | `run_function` with `Job change check · Loopster skill` if it exists. If not, `run_capability` with `loopster-data-enrich-person` (free, `maxCostUsd: 0`; confirm in `list_capabilities`) and compare the company in the chat. Build the Function only when the user will repeat the check (Play 2). |
| The watchlist: names, owners, `Alerted on`, the schedule, the Slack alert | A table, with the check as one `run-function` column |
| A live profile check, a Slack alert | Table columns, for those steps only. They can't go in a Function. |
| ICP fit of the movers | `run_function` with a scoring Function if one exists; otherwise an AI column, then turn it into a Function (Play 2, step 4) |
| Turning old work emails into LinkedIn URLs, once | `run_capability` |

## Play 1: Customer alumni (free)

1. Take customer company names from `loopster-context.md` or the user. Batch 10 to 25 names per search.
2. `search_people` with:
   - `pastCompany` set to the customer names, with `mode: "exact"` so "Notion" doesn't also match "Notion Capital";
   - the persona filters (`jobTitle`, `seniority`);
   - the ICP company filters (`companySizeBand`, `companyIndustry`, `companyCountry`), and `country` as well when the people must live in the same region (the `prospect-list` skill explains why);
   - exclusions for the do-not-contact table, by domain with `matches: "company"` (this also leaves out anyone still at a customer, if customers are on it).
3. Re-check each record's current `title`. Filters can match past roles.
4. Show the count and 10 samples, then save as `Customer alumni · <date>` (search table, free) and turn Auto-run off.
5. The angle: they've seen it work. For example: "You used <product> at <old company>. Now that you're at <new company>, would it help to …". Don't claim an outcome they didn't have.

## Play 2: Champion watchlist (free checks, monthly)

1. **Create the table:** blank, `autoplay: false`, titled `Champions · watchlist`. A table is right here: the user wants the rows, owners and alert history in Loopster, and the check runs on a schedule. Columns:
   - `Name`
   - `LinkedIn URL`
   - `Company when champion` (domain)
   - `Owner` (optional)
   - `Source` (closed-won, power user, lost deal)

   Turn on `set_table_create_columns_from_keys`, then insert the champions with those keys, so each key becomes a column (with it off, keys that match no column are dropped). Check `ignoredKeys` is empty. Normalize domains and LinkedIn URLs first.
2. **Add the check.**
   - **The Function exists:** add one `run-function` column that calls `Job change check · Loopster skill`, mapped to `LinkedIn URL` and `Company when champion`. Then add a `Current company domain` column and a `Moved` column that each read its answer. Settings are in `references/watchlist-columns.md`, section "Use the Function in a table".
   - **No Function yet (first build):** add the three free check columns (exact settings in `references/watchlist-columns.md`):
     - `Current profile`: the `loopster-data-enrich-person` template, reading `LinkedIn URL`.
     - `Current company domain`: a Formula that pulls `company_website` out of the profile with a field reference.
     - `Moved`: a Formula that compares it with `Company when champion`, giving `yes`, `no` or `unknown`.

     Once step 3 shows they work, turn them into the Function (section "Turn the check into a Function"), then set up the schedule on the Function's column.
3. **Run once:**
   - **Check columns:** `trigger_rows` on all rows with `columnIds` naming the three columns and `maxCostUsd: 0`.
   - **`run-function` column:** price it from the Function (`get_function` `costEstimate.maxUsdPerRun` × the rows). Use this figure for the quote and the big-spend check. Run 1 row, then 10, then the rest 100 at a time, and read `get_wallet` `consumedUsd` before and after each batch.
4. **Read the movers.** For `Moved = yes`, check the new company against the ICP:
   - free with `loopster-data-enrich-company` on the new domain (read it from the `Current company domain` column);
   - for a scored ICP fit, run it on the movers only. Every step in a Function runs for every champion, so never put an ICP step inside the monthly check.
     - If the "Functions" section of `loopster-context.md` or `list_functions` lists a Function that scores ICP fit, call it with `run_function` on the movers only (up to about 25 inputs; for more, add one `run-function` column that calls that Function to the table and trigger it on the mover `rowIds`). Read its input ids with `get_function` and fill each from the mover's row, because the inputs are usually a title, company, industry and size. Price it first (`costEstimate.maxUsdPerRun` × movers, plus its AI step measured on 10, or 4 × the estimate until measured) and ask. Then run 1, then 10, then the rest 100 at a time, and stop and ask if a batch costs more than 1.5 times its share of the quote.
     - Otherwise score the movers with an AI column. It reads the mover's company profile (the free `loopster-data-enrich-company` result for `Current company domain`) and the ICP context, and returns `{"tier": "A|B|C", "reason": "…"}`. Price it with `estimate_trigger_cost` (an AI column often costs a few times its pre-run estimate, so measure 10 rows before quoting) and ask. Then trigger it on the mover `rowIds` only, with `maxCostUsd` and an `idempotencyKey`. Once the tiers read well, turn the column into a Function with `function-builder`, titled `ICP tier · Loopster skill` (or `ICP tier · movers · Loopster skill` if a Function with the first title already exists), and record its id in `loopster-context.md` straight away. From then on, call it from one `run-function` column.
     - Use `score-prospect` only if the user asks for it. It is a table column that can't go in a Function, and it is priced by use (the template lists $0.0036 as an estimate; measure 10 rows before quoting). Trigger it on the mover `rowIds` with `allowUnpriced: true` and `maxCostUsd`, after a yes, and know the cap does not cover it.

   Real usage depends on your use case and settings, so always check the final cost estimate before you run.
5. **Split the movers:**
   - **Joined an ICP company:** outreach. They go to `contact-finder` (new work email; it reuses the Find work email Function for anyone the free pass misses) and then `outbound-launch`.
   - **Left a customer:** a risk. Find who now holds their role there: `search_people` with `specificCompanies` set to the customer and the persona titles. Tell the user, and alert the account owner only after a yes (step 8).
6. **Freshness:** Loopster Data profiles show `days_since_refresh`. Profiles refresh about every 55 days, so a move can take weeks to appear. For a mover the user cares about, confirm with `enrich-professional-profile`. It's a live lookup at about $0.0015. It can't go in a Function. As a table column, set `execution_mode: "managed"` and trigger it on the mover `rowIds` only. As a capability, it needs the user's own key for the professional-network provider, or Loopster's account saved as that provider's default; ask before setting it.
7. **Write an opener field** for each mover: a `Champion note` column (AI, or written by you) with one sentence about the move. `outbound-launch` reads it as the signal for the first line.
   - If `Champion note · Loopster skill` is in the "Functions" section of `loopster-context.md` or `list_functions`, add one `run-function` column that calls it instead of an AI column.
   - Trigger it on the mover `rowIds` only. Price it first (`estimate_trigger_cost` for a plain AI column; for a `run-function` column, the Function's `maxUsdPerRun` × movers plus its AI step measured on 10) and ask. Run 1 first, then 10. Show the notes and the real cost (`get_wallet` `consumedUsd` before and after), and run the rest only after a yes, 100 `rowIds` at a time. Stop and ask if a batch costs more than 1.5 times its share of the quote.
   - Once the notes read well, turn the column into a Function the same way as the check (next section), named `Champion note · Loopster skill`, with the voice rules from `loopster-context.md` in its prompt. Record its id in `loopster-context.md`, and use one `run-function` column for it from then on.
8. **Alert once:** add a manual `Alerted on` column. After each run:
   - alert only rows where `Moved = yes` and `Alerted on` is blank;
   - then, only for rows whose alert was actually sent after the user's yes, write today's date into `Alerted on` with `update_cells` and copy the new domain (from the `Current company domain` column) into `Company when champion`, so next month compares against where they are now. Leave both untouched for any row you did not alert.

## Turn the check into a Function

The monthly check is the job you will run again on every list, so it belongs in a Function (house rules, section 7). Do this once the check columns have worked on the real watchlist.

1. **Build, record, publish and test it** by following `references/watchlist-columns.md`, section "Build the Function", steps 1 to 6: build it from the table (`create_function` with `fromTable`), write the id in the "Functions" section of `loopster-context.md` straight away, dry-run the publish and ask before the live publish and again before `set_function_agent_access`, then test on 3 checked champions plus one whose profile isn't found.
2. **Swap the table over:** one `run-function` column in place of the three check columns, plus a `Current company domain` column and a `Moved` column that each read the Function's answer (read one cell with `list_rows` first, then use a Formula that parses it, or for a JSON output a field reference whose `path` is `["<output key>", "<field>"]`; `get_function` shows the output keys). While the old columns still exist, give the new ones a different header (for example `Moved (Function)`), and rename them to `Moved` and `Current company domain` with `update_column` once the old ones are deleted. Ask before you delete the old columns, and keep them until the Function has matched the table on every champion you tested.

After that:
- **A list with no table:** `run_function` with the Function, for about 25 people or fewer. For more people, or when the user wants to keep the rows, use a table with one `run-function` column.
- **Any new or scheduled watchlist:** one `run-function` column. Never copy the Function's steps into table columns.

## Keep it running

- Offer a monthly schedule on the check, and ask before you create it (a plan yes does not cover it):
  - `create_schedule` with `cadence: "monthly"`, a `dayOfMonth` (1 to 28), a `time` (required, HH:MM), the user's `timezone` and `cells: "all"` (every champion is re-checked each month, which is what you want here). This is the "price the full re-run" option in house rules, section 9: the check is free, which you prove before you resume. For any paid column, send `cells: "empty"`.
  - the columns to name: the `run-function` column, plus the Formula columns that read its answer (for example `Current company domain` and `Moved`). Schedule only these. If `create_schedule` refuses a Formula column, schedule only the `run-function` column and, after each firing, run the Formula columns with `trigger_rows` (`columnIds` naming them, `force: true`, `maxCostUsd: 0`) before you read `Moved`. If the user says no to building the Function, name the three check columns instead and say that each fix will then have to be made in the table;
  - leave `rerunDependents` off, so the Slack alert column never fires from the schedule;
  - `paused: true`.
- **Prove it is free before you resume.** Don't assume it:
  - `get_function` shows `costEstimate.maxUsdPerRun` 0 and no `unpricedSteps`;
  - `get_wallet` `consumedUsd` is the same before and after a 10-row run (in a shared workspace, other people's runs can add to it, so run it when no one else is running).

  Only then tell the user each firing costs nothing. If any step costs money, price champions × the measured cost per row for each firing, ask, and resume only after a yes.

  Real usage depends on your use case and settings, so always check the final cost estimate before you run.
- **Resume** the schedule only after a yes.
- **Alerts:** add a `slack-send-message` column. A Slack post is a table column and can't go in a Function. Trigger it yourself after each monthly run, naming only the `rowIds` with `Moved = yes` and a blank `Alerted on`. Its text names the person, old and new company, and owner; the channel comes from `loopster-context.md`. Test it on one row in a test channel first. Post for real only with a yes for that month's batch, saying how many people and which channel. A yes for one run is not a yes for the next. Each Slack post is outward-facing.

## Draft the note (rules)

- Short: one sentence for the `Champion note` field. Use 2 to 3 sentences only if the owner will send it as a personal message.
- Personal: congratulate the move and mention your shared history in one clause.
- Ask nothing big. No meeting request in the first note, just an opening.
- Never imply you're monitoring them. "Saw you moved to Acme" is fine; "our system detected" is not.
- Use the voice rules in `loopster-context.md`.

## Show the result

```
Champions · watchlist   (180 champions checked, nothing charged)
  Moved: 14   → joined ICP company 6 · joined non-ICP 5 · unknown 3
  Left a customer: 4 accounts at risk (replacements found for 3)
  Customer alumni found: 92 in buying roles at ICP companies
Function: Job change check · Loopster skill (id saved in loopster-context.md)
Next: contact-finder for 6 movers + 92 alumni → outbound-launch
Schedule: monthly re-check created PAUSED — say "resume" to switch it on
```

Then add the pricing sentence if any paid step ran.

## If something goes wrong

- **Many `unknown`:** the LinkedIn URLs are missing or not in Loopster Data. Get URLs first: run `loopster-data-email-to-linkedin` (free) on their old work emails with `run_capability` (`maxCostUsd: 0`), then write the URLs into `LinkedIn URL` with `update_cells` and re-trigger the check for those rows: `trigger_rows` with their `rowIds`, `columnIds` naming the check columns (the `run-function` column and the Formula columns that read it, or the three first-build columns), `force: true` and `maxCostUsd: 0`. Without `force`, cells that already hold `{"found":false}` keep that answer.
- **False "moved":** the stored company domain differs from the website (for example a parent brand or regional domain). Normalize both, or compare company names as a fallback.
- **The Function's answers differ from the table's:** don't swap yet. Compare one champion at a time (`get_function_run` against the table cells), fix the Function in a new sandbox with `function-builder`, republish after a yes, and test again.
- **Building the Formula columns:** use the field reference once, in `Current company domain` only, and compare plain columns in `Moved` (see `references/watchlist-columns.md`, step 3).
