---
name: outbound-launch
description: Take a finished list from a Loopster table and get it safely into a sequencer campaign (HeyReach, Instantly, Smartlead or Mixmax). Removes do-not-contact, people already in a campaign, and existing connections. Cleans names, checks emails, writes a personal first line per person from their signal, post or company, and has a skeptical-buyer review of the top tier. Shows samples for approval, then pushes into a paused or draft campaign one, then ten, then all, with custom fields mapped, and logs the launch for learning. Use when the user says "send this list to HeyReach", "push to Instantly", "add these to my Smartlead campaign", "launch outreach", "write first lines", or when a play hands off a list for outreach.
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

# Outbound launch

## What you get

The approved people in the user's campaign, with personalization fields filled. You also get:
- a launch report: who was sent, who was held back and why, and what it cost;
- a row in the campaign log of `loopster-context.md`;
- a reusable `First line · Loopster skill` Function, saved once the lines pass review (Step 2), so the next launch writes its lines with one column.

The campaign stays paused or draft. Only the user starts it.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (voice, proof, pains, do-not-contact, destinations, and the "Functions" section). You need:

1. **The list:** a Loopster table (for a CSV or pasted list, create a blank table with `autoplay: false` and `insert_rows` first, named as the house rules describe) with, per person:
   - name;
   - LinkedIn URL (LinkedIn sequencers) or a work email (email sequencers);
   - company;
   - ideally a signal or opener field from the play that built it.
2. **The destination:** the sequencer and campaign. Check `list_connections`, and ask for the campaign id. The campaign must be **paused or draft**; ask the user to confirm. Never push into a live campaign without an explicit "it's live, push anyway". Mixmax sequences may start sending as soon as a recipient is added, so treat Mixmax as live unless the user confirms otherwise.
3. **Campaign variables:** the custom fields the campaign's messages use, so the mapping matches. For HeyReach, variables are single-brace, all caps, for example `{FIRST_LINE}`; the custom field key is `FIRST_LINE`.
4. **Functions to reuse:** look in the "Functions" section of `loopster-context.md`, then `list_functions`, for `First line · Loopster skill` (match any title that starts with `First line`), `Buyer review · Loopster skill` and `Find work email · Loopster skill`. Read each one you find with `get_function`, and tell the user its steps and price. If one is still a draft, publish it first, with its own yes; a `run-function` column runs it once it's published. Open it to agents only if the user also wants `run_function` to reach it, and ask for that separately. Reuse beats rebuilding.
5. **A spend baseline:** read `get_wallet` `consumedUsd` now, for the launch report.

**Where each piece runs** (house rules, section 7). The list stays a table: the user reviews who is held back, and each push names its `rowId`s. The reusable logic lives in Functions, each called by one `run-function` column:
- first lines and the buyer review (Step 2): built as columns the first time, then saved as Functions;
- a missing work email: the `Find work email · Loopster skill` Function.

These stay table columns:
- the pre-flight lookups and the push (sequencer actions can't be Function steps);
- email checks (also not Function steps);
- do-not-contact matching, which reads the user's do-not-contact table and flags rows on the list table;
- name clean-up, a one-line Formula on this list's own name column.

Do-not-contact matching and name clean-up are tidy-up on the list table the user keeps (they review and push from it), not a repeatable job to turn into a Function.

## Step 1: Pre-flight (mostly free)

Add these checks as columns on the list table (settings in `references/preflight-and-push.md`):

1. **Do-not-contact:** read the do-not-contact table (`list_rows`), normalize its domains, emails and LinkedIn URLs the same way as the list, and flag every list row that matches any of them. Show the matches, then leave them out of the push.
2. **Already in a campaign:** `heyreach-get-campaigns-for-lead`, `smartlead-lookup-lead-status-in-campaign` or `instantly-find-lead`.
   - These run on the user's own sequencer account, so nothing is charged to the wallet. Before you add them, call `test_connection` once on that connection (its id is in `list_connections`). If it comes back `rejected`, stop and ask the user to reconnect it in Loopster: a check that errors because the key is bad is not an answer of "not in a campaign". If the provider can't be tested, go on.
   - If the workspace has more than one account for the sequencer (`list_connections`), ask which one owns the campaign, and set `integrationConnectionId` on every column.
   - For HeyReach, an error saying there is no lead record means HeyReach has never seen that person, so they are not in any campaign.
3. **Already connected (HeyReach):** `heyreach-is-connection` needs the sender's `linkedin_account_id`. The user gets it from HeyReach.
   - If the user doesn't have it, skip this check and say so.
   - Connections may need a different message, or no outreach at all.
4. **Name clean-up:** a Formula that strips emojis, titles ("Dr.", "MBA"), "| …" tails and ALL CAPS, giving a proper first name.
5. **Email check** (email sequencers): every email, free or paid, must be checked (`contact-finder` Step 3) before an email sequencer push. Found is not verified.
   - The check stays a table column (or `run_capability` on the emails). A Function finds emails but does not check them, so don't add a check step to it. The check is paid, about $0.0065 an email. Price it with `estimate_trigger_cost` on the rows that have an email, ask, run 1 row, then 10, then 100 `rowId`s at a time with `maxCostUsd` at the agreed amount, and read `get_wallet` `consumedUsd` after each step. Count it in the big-spend total (Step 2, item 3). Real usage depends on your use case and settings, so always check the final cost estimate before you run.
   - **Rows with no email:** use the `Find work email · Loopster skill` Function (see `contact-finder`), called from one `run-function` column on the list table.
     - If the Function doesn't exist yet, build it with the `contact-finder` skill.
     - Map its inputs (`get_function` lists them).
     - Don't set a run condition on this column. The `Work email` Formula below reads it for every row, and a column that reads a skipped column does not run (house rules, section 9). Trigger it with `trigger_rows` on the `rowId`s that have no email and aren't held back by checks 1 to 3, and price those same `rowId`s from the Function: `get_function` `costEstimate.maxUsdPerRun` × the number of rows. Rows you leave alone stay blank. In `update_column`, mark this column optional on the `Work email` Formula (`optionalMentions`), so a blank cell still lets the Formula run and count as no email. On your 1-row test, also check a row you did not trigger: `Work email` must return that row's own email, and the email check must complete on it. If either one skips or fails, stop and tell the user.
     - This column is paid. Price it from the Function: `get_function` `costEstimate.maxUsdPerRun` × the rows. Use this figure for the quote and the big-spend check. Ask (end the message with the pricing sentence), run 1 row, then 10, and read `get_wallet` `consumedUsd` before and after each step. Quote the rest from the real cost of the 10. Count the whole launch, not this column alone: the email finding for every row with no email, the email check, the first lines and the buyer review (Step 2; use 4 times the pre-run estimate for any AI step you have not measured yet). If it is likely over the big-spend limit in house rules section 4c (or the "Ask above" amount in `loopster-context.md`), ask with the 4c wording before the rest, and say plainly that you will control spend with the 1, 10, then 100 steps and wallet reads. Then run the rest 100 `rowId`s at a time. Read `get_wallet` `consumedUsd` after each batch, and stop and ask if a batch costs more than 1.5 times its share of the quote.
     - Don't rebuild the Function's steps as columns.
   - Pull the found email out of the cell (a Formula that parses it, or a field reference with `path`; read the output key with `get_function`). Combine it with the email already on the row in one `Work email` Formula, and point the check column at that. Read the cell on your 1-row test and write the Formula so that both a blank and a `found: false` result count as no email. Only a parsed email address goes into `Work email`. Give the check column a run condition with `update_column`, for example `String(@{<Work email id>}).includes('@')`, so it never runs on a blank, and do not rely on a blank `Work email` to skip it.

Show who's held back and why. The user can release anyone.

## Step 2: First lines

The first time, build the lines as an AI column and tune the prompt on it. When the lines pass review, save the column as a Function (item 7). If a `First line · Loopster skill` Function already exists (Before you start), reuse it (item 2).

1. **Prepare the input.** The line reads one Formula column, `Signal text`, which draws on:
   - the person's signal or opener field (from `signal-outbound` or `champion-tracker`);
   - or their engagement topic (from `engager-leads`);
   - or their recent posts (`professional-person-posts`, $0.006, opt-in);
   - or company facts.

   The inputs come from different plays, and some may be missing on a list. Coalesce them first in `Signal text`, with a fallback of `none`, so the next column never waits on a skipped column (`references/first-line-prompt.md`).
   - `professional-person-posts` can't be a Function step. Fetch the posts in a table column and feed them in through `Signal text`.
2. **Add the First line column.**
   - **No Function yet:** pick the model first (item 6). Then add an AI column, `First line`, on it. It reads `Signal text`, the company, and the voice rules from the context file. The prompt template is in `references/first-line-prompt.md`.
   - **A Function exists:** read its prompt with `get_function` and check that the offer and pain are this campaign's. If they aren't, build a second Function for this campaign (`function-builder`). Edit the existing one only if the user confirms it is only used for this campaign, after asking which tables and schedules call it, and publish after a yes. Then add one `run-function` column (`references/choosing-the-surface.md`), mapping its inputs from `Signal text` and the company column.
     - Put the line in its own `First line` column, because the push maps that column.
     - Run 1 row first (item 3) and read the cell. Then write the `First line` Formula to match what you see (the output key comes from `get_function`).
     - Use a field reference with `path` only for JSON outputs, such as the buyer review's `verdict`.
3. **Price it and ask.**
   - **AI column:** `estimate_trigger_cost` gives only a pre-run estimate, so say the real cost can be several times higher. Run 1 row with `maxCostUsd` and show the line. Then run 10 and show the lines and the real cost from `get_usage`.
   - **`run-function` column:** price it from the Function (`get_function` `costEstimate.maxUsdPerRun` × the rows, plus the AI step measured on 10 rows). Use this figure for the quote and the big-spend check. Run 1 row and show the line. Then run 10, and read `get_wallet` `consumedUsd` before and after.
   - Quote the rest from the real cost of the 10. When you ask, say how you will control the spend.
   - Count the whole job (any email finding, the email check, the first lines and the buyer review), not each batch of 100. If it is likely over $25 (or the "Ask above" amount in `loopster-context.md`), or over 10% of the wallet's `spendableUsd`, it is a big spend: ask with the wording in house rules section 4c. If the Step 1 ask already covered this whole launch at about the same amount, don't ask the same question again.
4. **Skeptical-buyer check, top tier only.** It reads each line as the recipient would. Use the list's tier column, and ask which column and value mean top tier if it isn't obvious. If the list has no tier column, review the 10 test lines only. Trigger it on those `rowId`s only.
   - If `Buyer review · Loopster skill` exists, add one `run-function` column that calls it, with a run condition (`update_column`) that is true only for the top tier (if the list has a tier column). Price it as in item 3 first, then test the condition on rows outside the top tier only: they must skip and cost nothing. The rows that should run are tested by the 1-row and 10-row runs.
   - Otherwise build a second AI column, or do your own review. Item 7 saves the column as a Function.
   - In both cases, flag anything that sounds automated, creepy, flattering, vague or wrong, plus scraping tells such as titles left in names or a company name in the wrong case.
5. **Fix the prompt, not single lines.**
   - **AI column:** rerun the 10 with `force: true` (without it, filled cells are skipped). When the user approves, run the rest with `maxCostUsd`. The cap checks only the pre-run estimate, so read `get_usage` after the 10 and quote the rest from the real cost.
   - **Function:** fix the AI step in a new sandbox, dry-run the publish, and publish after a yes. Callers run the old version until then. Then rerun the 10 with `force: true`. Run the rest 100 `rowId`s at a time, and read `get_wallet` `consumedUsd` after each batch. If a batch costs more than 1.5 times its share of the quote, stop and ask.
6. **Model** (first build only): read the template you want with `get_column_template` rather than listing every AI template. The default `ai` model writes the most specific lines. `ai-openai-gpt-5.4-mini` costs less a line and writes plainer text. Smaller "nano" models cost least and suit simple tasks.

   For a large list, compare them with two AI columns on the same 10 rows of the list table, and let the user choose. This is a one-off, so columns are the right tool. Save the winner as the Function (item 7).
7. **Save it as a Function** once the lines pass review and the user approves them. The next launch then needs one column, and any scheduled or Auto-run table can call it.
   - `create_function` with `fromTable`: the `tableId`, and the `First line` column in `columnIds` and in `outputColumnIds`. Leave `Signal text` in the table, because the columns it reads differ per list; it becomes the Function's input, with the company. Title it `First line · Loopster skill`. If a First line Function for another campaign already exists, title it `First line · <campaign> · Loopster skill` instead. Put the skill name, version and campaign in the description. When you look for one to reuse, match any title that starts with `First line`.
   - Write the `functionId` into the "Functions" section of `loopster-context.md` straight away. Drafts don't show in `list_functions`.
   - Read the new input and output ids with `get_function`, run `publish_function` with `dryRun: true`, and show the contract. Publish only after a yes, and ask again before opening it to agents (`function-builder`).
   - If you built the buyer review as a column, do the same for it, as its own Function, `Buyer review · Loopster skill`. Keep it apart from First line: a Function step runs for every input, and only the top tier should be reviewed and paid for. Next time, call it from a `run-function` column with a run condition (`update_column`) that is true only for the top tier, and test it as in item 4.
   - Leave this launch's `First line` column in place, because the push reads it. The next launch uses one `run-function` column (item 2).

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Step 3: Push (each batch needs a yes)

1. **Add the destination column** (`references/preflight-and-push.md`):
   - **HeyReach:** `heyreach-add-leads-to-campaign`, with `campaign_id`, `first_name`, `last_name`, `profile_url` and `custom_fields` `[{"key": "FIRST_LINE", "value": "@{First line}"}, …]`.
   - **Instantly:** `instantly-add-lead`, with the campaign and custom variables.
   - **Smartlead:** `smartlead-add-lead-to-campaign`, with the campaign and custom fields.
   - **Mixmax:** `mixmax-add-recipient`, with the sequence and variables.

   Each one runs on the user's own account, so nothing is charged to the wallet. Finish the First line and review columns first, and trigger the push column on its own.
2. **One person first.** Pick a held-back test contact the user controls if possible, or the first approved row. Trigger the column on that `rowId`, and have the user open the campaign to check the lead and fields.
3. **Then 10, then the rest.** Each batch needs a yes that states how many people go to which campaign. Read each cell's result; failures carry a message.
4. **Never start the campaign.** Tell the user it's ready to start in the sequencer.

## Step 4: Log it

Append to the campaign log in `loopster-context.md`:
- date;
- play;
- list;
- angle and proof;
- number pushed;
- Functions used or built (title, id, published yes or no).

Report the cost as `get_wallet` `consumedUsd` after the launch minus the baseline you read before you started. It includes Function spend.

Any Function you created in this play goes in the "Functions" section straight away, so the next launch finds it.

When results come in (replies, positive replies, meetings), use the `gtm-context` update mode so the next launch uses what worked.

## Show the result

```
Launch · Signals · hiring · 2026-10-25 → HeyReach "Q4 SDR leaders" (paused)
  Ready: 142 · held back: 31 (do-not-contact 6 · already in campaign 14 · connected 9 · bad name 2)
  First lines: 142 written · top tier reviewed (5 prompt fixes) · cost $X.XX
  Functions: First line · Loopster skill (new, published) · Buyer review · Loopster skill (new, published)
  Pushed: 142 of 142 · errors 0 · campaign still PAUSED: start it in HeyReach when ready
```

End the message with this sentence: Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## If something goes wrong

- **The push cell errors with "campaign not found" or "not active":** check the campaign id, and that the sender account is attached to the campaign.
- **Custom fields empty in the sequencer:** the keys don't match the campaign's variables. Fix the mapping (HeyReach keys are all caps, no braces).
- **Duplicate leads in the campaign:** the pre-flight lookup ran on a different campaign, or before an earlier push finished. Re-run the lookup column.
- **The `run-function` column skips rows:** a mapped input is blank. Map it from `Signal text`, which falls back to `none`.
