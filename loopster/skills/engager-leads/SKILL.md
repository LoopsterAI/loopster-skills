---
name: engager-leads
description: Turn LinkedIn engagement and event attendance into qualified leads. Pulls the people who reacted to or commented on a post (yours, a competitor's, or an influencer's in your space) or a company's recent posts, or takes an event guest list. Removes your own team, competitors and do-not-contact, resolves each person's current title and company, keeps those who fit the ICP, marks repeat engagers as warmer, and hands them to outreach with the topic they engaged with. Use when the user says "people who liked my post", "competitor's post engagers", "who commented on", "LinkedIn engagement leads", "event attendees", "webinar registrants", "who reacted to a competitor's post", or "warm leads".
license: MIT
metadata:
  author: Loopster
  version: "0.1.0"
---

# Engager leads

## What you get

A Loopster table `Engagers · <source> · <date>`, one row per person. For each:
- name, current title and company, and LinkedIn URL;
- which post they engaged with and how (reaction or comment, with the comment text);
- how many tracked posts they engaged with;
- ICP tier (A, B or C).

Ready for `contact-finder`, then `outbound-launch`.

## Before you start

Read `references/house-rules.md` and `loopster-context.md` (ICP, personas, competitors, do-not-contact, your own company domain).

Call `get_wallet` and note `consumedUsd` and `spendableUsd`. You need both, to report the real spend and to size a big spend.

Then look for Functions this play can call: the "Functions" section of `loopster-context.md`, then `list_functions`. You want two:
- one that takes a LinkedIn URL and returns the current title and company (Step 4);
- one that scores a person against the ICP (Step 5).

Run what exists. Build one only when none fits (house rules, section 7).

Where each part runs:
- **The engager list is a table.** The user keeps and filters the rows, it usually passes 25 people, and the post steps below can't go in a Function. Keep the table thin: logic that repeats (resolve, score) goes in a Function called by one `run-function` column. Never copy a Function's steps into table columns.
- **Not Function steps:** company and person posts, post reactions, post comments and live professional profiles (`enrich-professional-profile`). They stay table columns (`execution_mode: "managed"`) or capabilities.

Pick the source:

| Source | Input |
|---|---|
| Specific posts | Post URLs (`https://www.linkedin.com/posts/…`) |
| A company's recent posts | Company LinkedIn URL. Pick the posts with the most engagement. |
| A person's recent posts (founder, influencer, competitor exec) | Person LinkedIn URL |
| An event | The guest list as a CSV (from Luma or the event tool). Start at Step 3. |

## Step 1: Get the posts

- **Company posts:** `professional-company-posts` (company LinkedIn URL). It returns recent posts with `url`, `postedAt`, `reactionsCount`, `commentsCount` and `text`.
- **Person posts:** `professional-person-posts` (profile URL).
- Show the posts by engagement and let the user pick 1 to 10. Topic matters more than volume; a post about the problem you solve beats a holiday post.

These run on the professional-network provider (`professionalNetwork`), so they are table columns or capabilities, never Function steps. Use the two routes in Step 2: the capability (`run_capability`) if the provider is set up, else a scratch table `Engager sources · <date>` (`autoplay: false`) with a `Company URL` or `Profile URL` column and a column for `professional-company-posts` or `professional-person-posts` with `execution_mode: "managed"`. As a capability, it needs the user's own key or Loopster's account saved as that provider's default (ask first). Price the post pull (the `cost` in `list_capabilities`, or `estimate_trigger_cost` for a column, × the number of companies or people), ask with the pricing sentence, and send `maxCostUsd` and an `idempotencyKey`, as in Step 2.

List prices from `list_capabilities` (read the live `cost` before you quote):
- company posts: about $0.04 listed;
- person posts: $0.006 at the default of 50 results (billed per page of 25 results);
- one post's reactions or comments: about $0.04 listed at the default limit of 25 (billed per item returned);
- profiles: $0.0015 per person.

**Volume:** the reactions and comments columns take a `limit` setting (about 25 by default) and bill per item returned, so a higher `limit` pulls more people and costs more. Read the setting with `get_column_template` before raising it. Commenters are the warmest and say the most, so favour posts with comments. Set the expectation up front: 3 posts typically give 50 to 90 people before filtering.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Step 2: Pull the engagers

Pick the route:

- **Capability route, when the provider is already set up.** If the user's own key for the `professionalNetwork` provider is connected, or Loopster's account is already saved as that provider's default (`list_connections`, `list_provider_defaults`), run `professional-post-reactions` and `professional-post-comments` with `run_capability` on the chosen post URLs. No scratch table is needed.
  - Read the inputs and `cost` in `list_capabilities`, and price it (cost × posts).
  - Send `maxCostUsd` and an `idempotencyKey`. Run 1 post first, then the rest.
  - Poll `get_run` until `status` is not `running`, then read each item's `output` with `list_run_items`.
  - Save the items to a CSV as soon as the run finishes: capability results stay readable for a while only.
  - Never change a provider default without asking.
- **Table route, otherwise:**
  1. Create a small table, `Engager sources · <date>` (blank, `autoplay: false`), with a `Post URL` column. Insert the chosen post URLs.
  2. Add two columns, each with `execution_mode: "managed"`:
     - `professional-post-reactions`, reading `Post URL`;
     - `professional-post-comments`, reading `Post URL`.
  3. Price with `estimate_trigger_cost`, ask, then `trigger_rows` with `maxCostUsd` and an `idempotencyKey`, poll `get_run` until it is not `running`, and read the cells with `list_rows`.

Either way, each result holds `items[]`:
- reactions: `reactionType`, plus `person` (name, profile URL, headline);
- comments: the comment text, plus person details.

## Step 3: Build the people table

1. Create `Engagers · <source> · <date>` (blank, `autoplay: false`) with columns:
   - `Name`
   - `LinkedIn URL`
   - `Headline`
   - `Post`
   - `Engagement` (reaction type or "comment")
   - `Comment`
   - `Times engaged`
2. Insert one row per engagement first, from the Step 2 cells or CSV. Merging comes after Step 4, because the same person can appear under different URL forms (member id vs vanity handle).
   - For an event list, map its columns (name, email, company, title).
   - Guest lists usually have emails, not LinkedIn URLs, so add `loopster-data-email-to-linkedin` (free) as a column, then fill the `LinkedIn URL` column with a Formula that returns the URL when the lookup found one and stays empty when it returned `{"found":false}`. Don't rely on an empty cell to stop a later column. Run Step 4 only on rows that have a URL by passing their `rowIds`, or set a `runCondition` on the Step 4 columns with `update_column` that parses the email-to-LinkedIn column and tests `found`.
3. **Remove noise before spending:**
   - your own employees (headline or company names your company);
   - the post author's own employees, when it's a competitor's post (the user can choose to keep them);
   - do-not-contact matches;
   - obvious non-buyers by headline (students, recruiters, "open to work"), unless the user wants them.

## Step 4: Resolve who they are now

Order: free lookup for everyone (the Function, or the columns), live lookup only for the misses, then the `Resolved` columns, then the merge.

Engager profile URLs often use member ids (`/in/ACoAA…`), not vanity handles.

**Reuse first.** If a Function that does this exists (Before you start), use it instead of building columns:
1. Add one `run-function` column calling it, with its LinkedIn URL input mapped (`mode: "column"`) to `LinkedIn URL`. Read the input ids and output keys with `get_function` (column settings: `references/choosing-the-surface.md`, section 4).
2. Price it from the Function: `get_function` `costEstimate.maxUsdPerRun` × the rows. Use this figure for the quote and the big-spend check. Run 1 row, then 10, then the rest (100 at a time for a longer list), and read `get_wallet` `consumedUsd` before and after each batch. Compare each batch's real cost with its quote; if a batch costs more than 1.5 times its share, stop and ask.
3. Read one cell with `list_rows` to see how each output is stored. Then pull the vanity URL, current title and company domain into their own columns, one per output: use a Formula that parses the cell and then parses the output (the cell is a JSON object whose outputs are each JSON text, so two parses; if an output turns out not to be JSON, wrap that second parse in try/catch and fall back to the text), or, for an output that holds JSON, a field reference whose `path` is `["<output key>", "<field>"]`, encoded as in the build route below.

**If none exists, build the columns first:**
1. Add `loopster-data-enrich-person`, reading `LinkedIn URL`. It's free, and resolves some member ids to a profile with vanity URL, current title, company and website.
2. Pull out the vanity URL, current title and company domain with three Formula columns, using a field reference. `@{ref:v1:<data>}`, where `<data>` is the base64url (no `=` padding) of `{"columnId":"<profile column id>","source":"value","path":["company_website"]}`. Use one field reference per Formula.
3. Write each Formula so it always returns a value: set `optionalMentions` on it with `update_column` so an empty field gets through, and return the text `not found` when the field is empty.

**Then, on either route:**
1. For rows where the vanity URL is `not found`, add `enrich-professional-profile` with `execution_mode: "managed"` (a live profile, $0.0015). It can't be a Function step, so it stays a table column. Price it, ask, and run only on those rows (pass their `rowIds`). Pull the same three fields from it with their own Formula columns, each returning `not found` when its field is empty.
2. Add a Formula column `Resolved URL` that returns the free profile's vanity URL, or the live profile's when the first is `not found`. Set `optionalMentions` on it so a blank live-profile cell gets through. Do the same for `Resolved title` and `Resolved company domain`. Read Step 5 and the merge from these three columns.
3. **Now merge:** group rows by `Resolved URL`. Keep one row per person, with `Times engaged` set to the number of different posts they engaged with (a reaction and a comment on one post count once), and the post names and comment text joined into `Post` and `Comment`. Leave rows whose `Resolved URL` is `not found` as separate rows. The merge is table editing and stays in the table.

**After a column build, save it as a Function.** Offer it in one line. Building is free, and publishing needs its own yes (house rules, section 4b):
- Follow `function-builder`, from a working table: `create_function` with `fromTable`, `columnIds` the enrich-person column and its three Formula columns, and `outputColumnIds` the three Formulas (vanity URL, current title, company domain), titled `Current profile · Loopster skill` (check `list_functions` for that title first). Leave the raw profile out of the outputs: it is large. The live-profile column stays in the table.
- Write the new draft's `functionId` into the "Functions" section of `loopster-context.md` straight away.
- Dry-run the publish, show the contract, and ask before publishing and before opening it to agents.
- Then run the Function with `run_function` on 3 rows from the table, including one the free lookup missed. Its steps are free, so there is no price to quote; read `get_wallet` `consumedUsd` before and after to confirm. Compare with the columns' values. A miss should give `not found`.
- This table keeps its columns. Next time use one `run-function` column calling it. On a scheduled or Auto-run table, every firing or inserted row bills the Function (a schedule re-runs every cell unless you send `cells: "empty"`), so price it per month, include it in the big-spend check (house rules, section 4c), and ask before you create the schedule or turn Auto-run on.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## Step 5: Keep the fits

Score against the ICP:
1. **If a scoring Function exists** (Before you start), add one `run-function` column calling it. Map each of its inputs from the matching column (read the input ids with `get_function`; column settings: `references/choosing-the-surface.md`, section 4). If it needs an input this table has no column for, use item 2 instead.
   - Price it and run 1 row, then 10, then the rest (100 at a time for a longer list), as in Step 4. Compare each batch's real cost with its quote; if a batch costs more than 1.5 times its share, stop and ask.
   - Read one cell with `list_rows`, then pull the tier into its own column the same way as in Step 4. Read the output key with `get_function`: it is `tier` for the standard Function. Sort on that column. Say which scale the Function uses.
2. **If none exists, build the column first:** an AI column returning `{"tier": "A|B|C", "reason": "…"}`, reading the ICP context and the `Resolved title` and `Resolved company domain` columns.
   - Price it with `estimate_trigger_cost` (an AI column's real cost can be 3 to 4 times its estimate) and ask with the pricing sentence. Then `trigger_rows` with `maxCostUsd` at the agreed amount and an `idempotencyKey`, on rows whose `Resolved title` is not `not found` (pass their `rowIds`): 1 row, then 10, then the rest.
   - Once it works, save it as a Function the way Step 4 does: `create_function` with `fromTable`, the AI column as the step and as the output, titled `ICP tier · Loopster skill` (check `list_functions` for that title first). Record its id in the "Functions" section of `loopster-context.md` straight after `create_function`, as in Step 4.
3. **`score-prospect`, only when the user asks for it.** It uses the ICP context, is priced by use (measure 10 rows for the real cost) and can't be a Function step, so it stays a table column. Trigger it with `allowUnpriced: true` and `maxCostUsd`, and know the cap doesn't cover it. It returns `Tier 1`, `Tier 2`, `Tier 3` or `Not a fit`; map them to A, B and C with a Formula so the sort works the same way.

Engager lists are small (50 to 90 people), so 1, then 10, then the rest in one batch is enough. For a longer event guest list, run the rest 100 at a time.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

Sort tier A first, then by `Times engaged`. A `Times engaged` of 2 or more is a warm signal; say so.

## Hand off

Go to `contact-finder` for emails (it runs the "Find work email · Loopster skill" Function), or straight to a LinkedIn sequencer (HeyReach needs only the LinkedIn URL and name), then `outbound-launch`.

The angle is the topic, not the click. Good: "Your comment on <author>'s post about forecast accuracy stuck with me: …". Bad: "I saw you liked a post."

## Show the result

Write the sorted rows to a CSV from `list_rows` (house rules, section 10) and give the path.

```
Engagers · Acme pricing post · 2026-10-25   (3 posts, real cost $X.XX)
  Pulled 112 engagements → 87 unique people
  Removed: 24 own team · 6 competitor staff · 3 do-not-contact · 9 non-buyers
  Resolved 45 of 45 (38 free, 7 live profile)
  ICP tier: A 11 · B 14 · C 20 · repeat engagers 6
  Saved: ./engagers-2026-10-25.csv   (and the table "Engagers · Acme pricing post · 2026-10-25")
```

Report the real spend as `get_wallet` `consumedUsd` now, minus the value you noted at the start. It includes Function spend; in a shared workspace, other people's runs can add to it.

Then add the pricing sentence:

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

## If something goes wrong

- **400 "runs on your own professionalNetwork account":** you used the capability. Use a table column with `execution_mode: "managed"`, or ask to save Loopster's account as the default for that provider.
- **400 when you add a post, reaction, comment or professional-profile step to a Function:** those aren't Function steps, and nothing is stored. Use a managed table column or a capability for them, and pass their text into a Function as an input if it needs it.
- **Reading a `run-function` cell:** it holds a JSON object of the Function's outputs, each itself JSON text. Read the output keys with `get_function`, and pull a field with a Formula that parses twice.
- **Fewer reactors than the post shows:** each call returns about 25 reactors. Note the count you got, don't promise the full list, and lean on commenters.
- **Huge cell values:** read only `items[].person` and the comment text, and never paste whole cells.
