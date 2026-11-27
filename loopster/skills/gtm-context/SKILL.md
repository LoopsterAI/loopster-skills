---
name: gtm-context
description: Set up the go-to-market context every Loopster play reads, in about five minutes. It covers what you sell, your ICP and buyer personas, pains, proof, voice, competitors, the do-not-contact list, and where results should go (CRM, sequencer, Slack), saved as loopster-context.md, plus a Loopster do-not-contact table used to exclude records from every search and a register of the reusable Functions in the workspace. Also logs campaign results so later plays get sharper. Use when the user says "set up my ICP", "here's what we sell", "update our messaging", "add these to do-not-contact", "log campaign results", "what Functions do we have", "record this Function", or when a Loopster play starts and no loopster-context.md exists.
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

# GTM context

## What you get

- **`loopster-context.md`:** one file every Loopster play reads, so nobody re-explains the business each time.
- **A do-not-contact table in Loopster:** customers, open deals, competitors and anyone who asked not to be contacted. Searches use it as an exclusion list, and plays check it before pushing anyone.
- **A Functions register** inside the same file: the reusable Functions the workspace already has, with their ids, inputs, outputs and costs. Every play reads it first and reuses a Function before it builds one. No play copies a Function's steps into table columns (house rules, section 7).
- **A campaign log** inside the same file, which plays update after each run.

The template is in `references/context-template.md`. To choose between a Function, a table and a capability, see `references/choosing-the-surface.md`.

## Where the file lives

1. Look for `loopster-context.md` in the working folder.
2. If it's not there, look for `~/.loopster/context.md` (one context for all projects).
3. If neither exists, create it in the working folder, unless the user wants it global.
4. If this tool keeps no files between chats (for example Claude.ai), show the user the file's text at the end of the session and ask them to save it and paste it back at the start of the next chat. Never assume the file is there.

If a file exists, show a three-line summary and ask whether to update it or start over. If they start over, keep the "Functions" section and the "Campaign log" exactly as they are, and rewrite only the other sections. Either way, check the "Functions" section against `list_functions` (Step 1) and add any Function it is missing.

## Before you start

Read `references/house-rules.md` once per session (sections 4 and 7 matter most here).

## Step 1: Start from what Loopster already knows (free)

- `list_contexts`: note the ids of the ICP and tier contexts, if any. AI steps can read them as `@{ctx:<id>}`. The API returns titles only, not the text, so still capture a plain-English ICP in the file.
- Functions register:
  1. `list_functions`: write each Function's title and id on its own line in the "Functions" section, with "open to agents yes". It shows only published Functions that are open to agents.
  2. Ask whether the user has drafts, or published Functions not yet open to agents. Read each id they give with `get_function` and write its line too.
  3. Read the ones a play would reuse (emails, phones, scoring, signals, first lines, CRM fills) with `get_function`, and add each one's input ids, output keys and `costEstimate` if shown.
  4. If there are none, write "none yet".
- Ask for the company website, as one question with a default: the domain of the user's work email or of the connected accounts if you can see one, else say they can reply "skip" and you'll go on from the ICP in their message. Run `run_capability` with `loopster-data-enrich-company` (free, `maxCostUsd: 0`) for name, industry, size and location. This is one action, once, so a capability is the right surface: no table and no Function.
- Do-not-contact table: if `list_tables` with `search: "Do not contact"` finds none, create it now (Step 3, items 1 to 3), before the questions. It is free and needs no answers; loading rows into it waits for Step 3, item 4.
- If you can read web pages yourself, read the homepage, pricing and customers pages. Draft a one-paragraph offer summary and a first ICP guess from them. Show the draft rather than asking from scratch.

## Step 2: Fill the gaps, one question at a time

Ask only what Step 1 and the user's own message did not answer. **One question per message:** ask it, offer your best guess as the default the user can accept with "yes", and wait for the answer before the next. Never send the questions below as a list. If nobody can answer (an unattended run), ask only the first open question and stop there. If the user skips a question, write "not provided" in the file and move on; plays fall back to safe defaults.

1. **Offer:** what you sell, in one sentence, and the outcome a customer gets.
2. **ICP:**
   - industries
   - company size (employees)
   - regions
   - must-have traits, such as "uses Salesforce" or "B2B" (optional)
   - deal-breakers
3. **Personas:** 1 to 3 buyer roles (titles and seniority), and who signs.
4. **Pains:** the top 3 problems you solve, each with how the buyer notices it.
5. **Proof:** 2 to 5 customers or results that can be named, with numbers where possible, and which persona or industry each one is strongest for.
6. **Competitors and alternatives:** what buyers use today instead, and the one-line difference.
7. **Voice:**
   - tone
   - maximum length
   - words to avoid
   - first-name or formal
   - the call to action you prefer (question, short meeting, resource)
8. **Destinations:** check `list_connections` first, then confirm where results go:
   - the CRM (which connected account)
   - the sequencer and campaign
   - the Slack channel for alerts

## Step 3: Build the do-not-contact table (free)

This stays a table: searches take exclusions as a table column, and people edit its rows by hand. It holds no repeated logic, so there is nothing to put in a Function.

1. Look for an existing table first: `list_tables` with `search: "Do not contact"`.
2. If there's none, create a blank table with `autoplay: false`, titled `Do not contact · <company name>`. Reference tables keep a plain name with no date. A new blank table already has one `Input` column; you can ignore it.
3. Add four columns, `Domain`, `LinkedIn URL`, `Email` and `Reason`, either way:
   - turn on `set_table_create_columns_from_keys` and insert rows with those keys;
   - or create them with `templateId: "manual"`.

   Read the column ids with `list_columns`; columns created from keys may use the key itself as the id.
4. Ask what to load:
   - current customers
   - open opportunities
   - competitors
   - partners
   - people who opted out

   Accept a CSV, a pasted list, or an existing Loopster table. Insert the rows; normalize domains to `example.com` form first.
5. Record the table id and its column ids in the context file. Plays exclude with:

   `{"kind": "list", "projectId": "<table id>", "columnId": "<Domain column id>", "matches": "identity"}`

   For people searches, use `"matches": "company"` on the Domain column to leave out everyone at those companies.

## Step 4: Write the file

- Fill `references/context-template.md` and save it. Include the Functions you found in Step 1 and the Spending lines (how Function runs are batched).
- Write each Function you found as a line in the template's format, with its real id. A Function that doesn't exist yet stays "not built". Never leave a `<...>` placeholder in the file; the one-line format guide in the "Functions" section is the only exception.
- Show the user a short summary.
- Ask them to correct anything wrong. A wrong ICP costs more later than a question now.

## Update mode: log a campaign

When a play finishes, or the user reports results ("40 sent, 6 replies, 3 positive"), append a row to **Campaign log**:

- date
- play
- list
- angle and proof used
- how many were sent
- replies
- positive replies
- meetings
- one line on what worked

Then update **What's working**:

- An angle with a positive-reply rate above the others after 100 or more sends: move it up.
- One with none after 200 sends: move it to **Retired angles**.

Never delete history.

## Update mode: record a Function

If there is no `loopster-context.md` yet, create it from `references/context-template.md` with only the "Functions" section filled and every other section marked "not provided". Do not start the interview; tell the user they can complete the file later with this skill.

The "Functions" section is the one place every play records Function ids. Update it whenever a play or the `function-builder` skill:
- creates a Function (write the id straight away, even for a draft; drafts don't show in `list_functions`);
- publishes it, opens it to agents, edits it or retires it;
- measures its cost per run (`get_wallet` `consumedUsd` before and after, divided by the inputs you ran);
- adds a table whose `run-function` column calls it, or a schedule on that table.

Keep one line per Function, in the format in the template. A retired Function stays on its line, marked "retired YYYY-MM-DD", so nobody rebuilds it by mistake. When you quote a run, read the Function's cost from its line and price it as house rules section 4 says.

When a play has built a repeating job as table columns and they worked on the first build, the play turns them into a Function (`create_function` with `fromTable`) and records its id here. From then on, that play, and any scheduled or Auto-run table, calls the Function with one `run-function` column instead of copying its steps into columns.

Columns that use a step Functions refuse (CRM, sequencer and Slack actions, email checks, live LinkedIn profiles and posts, score-prospect) stay table columns; convert only the rest. Creating the draft is free; publishing it and opening it to agents each need the user's own yes (house rules, sections 4b and 6).

## If something goes wrong

- **A recorded Function can't be found:** it may have been deleted. Call `list_trash`: if it is there, it can be restored until its `purgesAt`. Tell the user, mark its line "not found", and ask whether to restore it (`restore_from_trash`) or build a new one with `function-builder`.
- **The website lookup finds nothing:** ask for the details instead. Loopster Data does not hold every company.
- **The user does not know their ICP:** start from their best 5 to 10 customers. Run `loopster-data-enrich-company` on their domains (free) and propose the common traits.
- **The do-not-contact table already exists with other columns:** reuse it, and record which column holds domains.
