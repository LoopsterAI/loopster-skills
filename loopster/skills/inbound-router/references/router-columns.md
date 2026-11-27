# Router columns

Build sections 1 to 9 as table columns, and try each one on made-up leads before you rely on it. The brief (section 8), the AI fit (section 5) and the Function version (section 10) are priced by use: read their real cost together, with `get_wallet` `consumedUsd` before and after 10 made-up leads. Everything else in sections 1 to 9 is free.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

How the sections fit together:
- Sections 1 to 5 are the qualify logic. Build them as table columns first. Section 10 turns them into the Function `Qualify lead · Loopster skill`.
- Sections 6, 7 and 9 (Tier, Route to, destinations) stay table columns. Section 8 (Brief) starts as a table column; section 10, last bullet, turns it into the Function `Lead brief · Loopster skill`.
- Section 11 is a free gate for Auto-run.

On a webhook table with "create columns from keys" on, the first payload creates the input columns. Their ids equal the field names (`Email`, `Name`, `Company`, `Website`, `Message`). Read the real ids with `list_columns`.

**Optional inputs:**
- A form field that can be blank (Name, Message, Website) must be listed in `optionalMentions` (`update_column`), or the column skips that row.
- `optionalMentions` covers a blank **value**. It does not cover an upstream column that was **skipped**: a column reading a skipped column does not run.
- So keep every enrichment in the chain running: give it an input that is never blank. The Domain formula below uses a placeholder for personal emails instead of a blank.
- In the Function, an input that can be blank is not required (`optionalInputColumnIds` when you build it from the table). Test the Function with a blank Name, a blank Message and a gmail lead.
- If `Qualify` is skipped for a blank `Name` or `Message`, map that input from a Formula column that returns `(none)` when the field is blank (house rules, section 9).

**Run conditions:**
- To stop a paid or sending column on some rows, set a run condition with `update_column` and `runCondition`: `{"enabled": true, "description": "...", "condition": "<formula over the row>"}`. The column runs a row only when the condition is true.
- Write the whole `condition` each time you update it. If a column needs two checks, join them with `&&`.
- A run condition on a table column comes along when you build a Function with `fromTable`.
- `estimate_trigger_cost` does not evaluate run conditions, so its figure is a ceiling.

## 1. Domain (free)

A company domain from the email. Personal email providers get the placeholder `personal-email.invalid`, which matches no company, so the lookup answers `found: false` instead of skipping.

```json
{"templateId": "formula", "header": "Domain",
 "taskConfig": {"formula": {"expression": "(() => { const d = String(@{Email}).trim().toLowerCase().split('@').pop(); return ['gmail.com','googlemail.com','yahoo.com','outlook.com','hotmail.com','live.com','icloud.com','me.com','aol.com','proton.me','protonmail.com','gmx.com','mail.com'].includes(d) ? 'personal-email.invalid' : d; })()"}}}
```

Always send the placeholder, never the raw personal domain, to the company lookup.

## 2. Personal email (free)

```json
{"templateId": "formula", "header": "Personal email",
 "taskConfig": {"formula": {"expression": "['gmail.com','googlemail.com','yahoo.com','outlook.com','hotmail.com','live.com','icloud.com','me.com','aol.com','proton.me','protonmail.com','gmx.com','mail.com'].includes(String(@{Email}).trim().toLowerCase().split('@').pop()) ? 'yes' : 'no'"}}}
```

## 3. Company profile (free)

```json
{"templateId": "loopster-data-enrich-company", "header": "Company profile",
 "taskConfig": {"loopsterDataEnrichCompany": {"domain": "@{<Domain id>}"}}}
```

## 4. LinkedIn lookup and optional person (free)

```json
{"templateId": "loopster-data-email-to-linkedin", "header": "LinkedIn lookup",
 "taskConfig": {"loopsterDataEmailToLinkedin": {"email": "@{Email}"}}}
```

Optional: if the brief should carry the person's title and company, add two columns after `LinkedIn lookup`.

1. `LinkedIn URL`: a Formula that reads the URL out of the `LinkedIn lookup` cell and returns `not found` when there is none, so the next column never gets a blank. Read one `LinkedIn lookup` cell first to see the url field name. Use one field reference in the expression: `String(@{ref:v1:<data>} || 'not found')`. `<data>` is the base64url (no `=` padding) of `{"columnId":"<LinkedIn lookup column id>","source":"value","path":["<url field name seen in the cell>"]}`, with those keys in that order and no spaces. Set `optionalMentions` on this Formula.
2. `Person profile`: `loopster-data-enrich-person` with `linkedin_url` set to `@{<LinkedIn URL id>}` (a plain column mention, not a field reference).

Test both on the gmail lead, where nothing is found. `Person profile` must come back `{"found":false}`, not skipped. If it is skipped, leave it out of the brief.

After section 10 deletes the original columns, point the field reference at the `Qualify · linkedin lookup` column instead.

## 5. ICP fit with an AI column (the version that moves into the Function)

An AI column that returns a tier and a reason. It can become a Function step; read its real cost together with the brief on 10 made-up leads (`get_wallet` `consumedUsd` before and after).

```json
{"templateId": "ai", "header": "ICP fit",
 "aiConfig": {"prompt": "You score an inbound lead against our ideal customer profile.\nOur ideal customer profile:\n@{ctx:<ICP context id>}\nLead name: @{Name}\nLead email: @{Email}\nPersonal email: @{<Personal email id>}\nCompany profile (JSON from our database, may be empty or say found false): @{<Company profile id>}\nTheir message: @{Message}\nTier A means a clear ICP fit. Tier B means a partial fit. Tier C means no fit or not enough data. A personal email is never above tier C.\nAnswer with JSON only: {\"tier\": \"A|B|C\", \"reason\": \"one sentence\"}\nNever invent facts that are not in the data above."}}
```

Then call `update_column` with `optionalMentions: ["Name", "Message", "<Company profile id>"]`.

A personal-email lead always ends at tier C, so the paid step has nothing to add for it. Don't give the column a run condition yet: `Tier` reads this column, and a column that reads a skipped column does not run (house rules, section 9). In step 7, just before `create_function` (section 10), set this run condition. It comes along into the Function, where the table reads the `Qualify` cell, which always completes:

```json
{"runCondition": {"enabled": true, "description": "Only for work emails",
 "condition": "String(@{<Personal email id>}) !== 'yes'"}}
```

- An `ai` step is `{"templateId": "ai", "aiConfig": {"prompt": "..."}}`, with each mention in braces and required unless the column has `optionalMentions`.
- The cell holds JSON text such as `{"tier":"A","reason":"..."}`. The Tier formula in section 6 reads it, and answers C for a personal email without reading the fit.
- Test it on a work-email lead, a gmail lead, a lead with a blank Name and a lead with a blank Message before you rely on it.
- Read the cost per lead again after you add the condition.

## 6. Tier (free)

Reads the `tier` field of the AI answer. A personal email still caps the tier at C. If the fit is `none`, empty or can't be read, the tier is `review`, so the lead is routed to a person instead of dropped. After section 10 this holds only because the `icp_fit` pull-out returns `none`, never blank.

```json
{"templateId": "formula", "header": "Tier",
 "taskConfig": {"formula": {"expression": "(() => { let f = @{<ICP fit id>}; try { f = JSON.parse(f); } catch (e) { f = null; } if (String(@{<Personal email id>}) === 'yes') return 'C'; return f && ['A', 'B', 'C'].includes(f.tier) ? f.tier : 'review'; })()"}}}
```

`none` can't be parsed, so the lead reads as `review`, unless it is a personal email, which gives C.

Then call `update_column` on `Tier` with `optionalMentions: ["<ICP fit id>"]`. A blank fit would otherwise skip `Tier` itself, so it would never read `review`, and `Route to`, `Brief` and `Alert` would skip too. After section 10, `<ICP fit id>` is the pull-out Formula column, which returns `none` for a skipped or empty fit, so it is never blank.

Tier and Route to stay table Formulas on purpose: they are the rules you tune in week one, and a Formula edit is free.

## 7. Route to (free)

```json
{"templateId": "formula", "header": "Route to",
 "taskConfig": {"formula": {"expression": "({'A': '<hot channel id>', 'B': '<hot channel id>'})[String(@{<Tier id>})] || '<review channel id>'"}}}
```

`Route to` is never blank. A and B go to the hot channel; `review`, and anything else, goes to the review channel. The `Alert` run condition (section 9) keeps C leads out of Slack. For several channels or owners, map the tier, region or size to channel ids in the expression.

## 8. Brief (AI, priced by use)

Prompt: see the configuration below. Then call `update_column` with `optionalMentions: ["Name", "Message", "<Company profile id>", "<ICP fit id>"]`. The fit can be blank on the `review` path, and a blank mention would skip `Brief`, then `Alert`. `Brief` reads `ICP fit: none` for a review lead and still runs. Test that path as in section 10.

The Brief starts as a table AI column; section 10, last bullet, turns it into a Function. After section 10, its `Company profile` and `ICP fit` lines read the columns that pull those fields out of the `Qualify` cell. Read the cost again with the AI fit.

Give it a run condition so it runs only for the leads that get an alert:

```json
{"runCondition": {"enabled": true, "description": "Only for A, B and review",
 "condition": "['A', 'B', 'review'].includes(String(@{<Tier id>}))"}}
```

Read the cost per lead again after you add the condition.

Real usage depends on your use case and settings, so always check the final cost estimate before you run.

```
You write a Slack alert for a sales rep about a new inbound lead.
Our ideal customer profile:
@{ctx:<ICP context id>}
Lead name: @{Name}
Lead email: @{Email}
Company profile (JSON from our database, may be empty or say found false): @{<Company profile id>}
ICP fit: @{<ICP fit id>}
Tier: @{<Tier id>}
Their message: @{Message}
Write plain text, no markdown headers, exactly this layout:
Line 1: Name, title if known, company and one fact (size or industry).
Line 2: Why they matter or not, in one sentence tied to our ICP.
Line 3: Suggested next step for the rep.
Then a blank line and 'Reply draft:' followed by a 2-sentence reply to the lead, friendly and specific to their message, no hype, no calendar link.
Never invent facts that are not in the data above. If the company profile is empty, say the company is unknown.
```

## 9. Destinations (each sends for real)

| Column | Template | Key settings |
|---|---|---|
| Alert | `slack-send-message` | `slackSendChannelMessage`: `channel_id: "@{<Route to id>}"`, `text: "@{<Brief id>}"`; run condition for A, B and `review` (below) |
| CRM lookup | `hubspot-find-object` | finds the contact by email; read its settings with `get_column_template` |
| CRM | `hubspot-update-object` | updates existing contacts only, so a new lead is not added. `hubspotSendObject`: `mode: "update"`, `objectType: "contacts"`, `recordId` from the lookup, `properties` (a JSON string of HubSpot internal property names; build it blank-safe with one Formula column that includes only the fields that have a value, so a blank never clears a CRM field; never map a column straight into `properties`); `integrationConnectionId` |
| CRM (Salesforce) | `salesforce-upsert-object` | matches on an external id field, so it creates or updates |
| Nurture | `heyreach-add-leads-to-campaign` / `instantly-add-lead` / `smartlead-add-lead-to-campaign` | campaign id (a constant) plus custom fields; run condition for tier C only (below) |

Gate the two tier-based sends with run conditions (`update_column`, `runCondition`):

```json
{"runCondition": {"enabled": true, "description": "Alert A, B and review leads",
 "condition": "['A', 'B', 'review'].includes(String(@{<Tier id>}))"}}
```

```json
{"runCondition": {"enabled": true, "description": "Nurture C leads only",
 "condition": "String(@{<Tier id>}) === 'C'"}}
```

The first goes on `Alert`, the second on `Nurture`. Section 11 adds the address check to `Alert`, `Nurture` and the CRM columns before Auto-run.

Test each one on the made-up lead in a test channel or test record before switching Auto-run on.

## 10. Qualify lead as a Function (after the test passes)

**Reusing a Function.**
- If `Qualify lead · Loopster skill` exists, skip the build: add its `run-function` column below and check the input ids and output keys with `get_function`. Price it before any run (see Cost below), run 1 made-up lead, then the rest.
- If a scoring Function fits instead, add its `run-function` column in place of `ICP fit`. Map its inputs from the columns you have (for example the fields of `Company profile`). Pull its output into a column with a Formula that parses twice and falls back to a placeholder, and change the `Tier` Formula to read its tier values. Price it, run 1 made-up lead, then the rest, and check the tier and route.
- Don't give that column the personal-email run condition: the pull-out Formula and `Tier` read it, and a column that reads a skipped column does not run (house rules, section 9). A gmail lead then pays for the scoring step unless the Function skips personal emails itself, so tell the user.

Turn sections 1 to 5 into one Function, so every lead and every future form shares the same logic. Each check below must pass before you wire the table. If one fails, keep the five columns, tell the user which check failed, and do not delete them.

Build it with `function-builder` (Step 2, "From a working table"):
- Before `create_function`, set the personal-email run condition on `ICP fit` (section 5). It comes along into the Function.
- `create_function` with the title `Qualify lead · Loopster skill`, a description that names the skill and version (`inbound-router 0.1.0`) and says "safe to edit in Loopster", and `fromTable`:
  - `columnIds`: `Domain`, `Personal email`, `Company profile`, `LinkedIn lookup`, `ICP fit`;
  - `outputColumnIds`: `Personal email`, `Company profile`, `LinkedIn lookup`, `ICP fit`;
  - `optionalInputColumnIds`: `Name`, `Message`.
- Write the `functionId` into the "Functions" section of `loopster-context.md` straight away.
- Read the new input ids and output keys with `get_function`. The output keys come from the step names: `personal_email`, `company_profile`, `linkedin_lookup`, `icp_fit`.
- Dry-run the publish and show the contract. Publish and open it to agents only after a separate yes for each.
- Price the test first: `costEstimate.maxUsdPerRun` × the number of leads, plus the AI step cost you measured on the made-up leads. `run_function` takes no `maxCostUsd`. Say the price against the test budget, ending with the pricing sentence, and ask again only if it goes over. Send `inputs` keyed by the input ids from `get_function`, one object per lead, with an `idempotencyKey`.
- Test it with `run_function` on a work-email lead, a gmail lead, a lead with a blank Name and a lead with a blank Message, and read each answer with `get_function_run`.

Then call it from the table with one column. Map every required input, and the optional `Name` and `Message` too.

```json
{"templateId": "run-function", "header": "Qualify",
 "taskConfig": {"runFunction": {"functionId": "<Qualify lead function id>",
   "inputMappings": [
     {"inputId": "<Email input id>", "mode": "column", "sourceColumnId": "Email"},
     {"inputId": "<Name input id>", "mode": "column", "sourceColumnId": "Name"},
     {"inputId": "<Message input id>", "mode": "column", "sourceColumnId": "Message"}]}}}
```

The cell holds a JSON object of the outputs, each itself JSON text. Pull each field you need into its own column with a Formula that parses twice (or a field reference whose `path` is `["<output key>", "<field>"]`). Repeat this Formula with `personal_email`, `company_profile` and, if used, `linkedin_lookup`. Use the `icp_fit` version below for the fit:

```json
{"templateId": "formula", "header": "Qualify · personal email",
 "taskConfig": {"formula": {"expression": "(() => { let c = @{<Qualify id>}; try { c = JSON.parse(c); } catch (e) { c = {}; } let v = c ? c['personal_email'] : ''; try { v = JSON.parse(v); } catch (e) {} return v === undefined || v === null ? '' : (typeof v === 'object' ? JSON.stringify(v) : String(v)); })()"}}}
```

For `icp_fit` only, return `none` instead of a blank when the Function gave no value (it is skipped for personal emails):

```json
{"templateId": "formula", "header": "Qualify · icp fit",
 "taskConfig": {"formula": {"expression": "(() => { let c = @{<Qualify id>}; try { c = JSON.parse(c); } catch (e) { c = {}; } let v = c ? c['icp_fit'] : ''; try { v = JSON.parse(v); } catch (e) {} return v === undefined || v === null || v === '' ? 'none' : (typeof v === 'object' ? JSON.stringify(v) : String(v)); })()"}}}
```

- `icp_fit` comes out as `none` when the Function skipped or gave nothing, so `Tier`, `Brief` and `Alert` still run. A blank cell would skip them, and `optionalMentions` does not help when the column before it was skipped.
- Check each new column against what the original column held on the same made-up lead.
- Point `Tier`, `Route to` and `Brief` at the new columns, and set `optionalMentions` on `Tier` and `Brief`. Each call replaces the whole list, so send the full list: for `Tier`, the new `icp fit` column id; for `Brief`, `Name`, `Message`, the company-profile pull-out id and the new `icp fit` column id. Run the made-up leads again and check the tier and route match the first test.
- Test the gmail and `review` paths:
  - (a) On the gmail lead, check that the `icp fit` pull-out reads `none`, `Tier` reads C and `Brief` is skipped.
  - (b) For `review`, take one made-up work-email lead (Auto-run off) and write `none` into its `icp fit` pull-out cell with `update_cells`. Point `Route to` at a test channel and get a yes first, because `Alert` sends. Price the re-run, since `Brief` is paid. Then call `trigger_rows` with that row's id, `columnIds: ["Tier", "Route to", "Brief", "Alert"]` and `force: true`. Check that `Tier` reads `review`, `Brief` has text and `Alert` posts to the test channel. If you kept the columns, do the same on the `ICP fit` cell.
- Ask the user, and only after a yes delete the five original columns. Until then, name only `Qualify` in triggers, so one trigger can't pay twice for the same work.
- **Cost.** The cost per lead is `Qualify` plus `Brief`, never `Qualify` alone.
  - Price `Qualify` from the Function: `get_function` `costEstimate.maxUsdPerRun` × the leads, plus its AI step measured on the made-up leads. Use `estimate_trigger_cost` for `Brief` while it is still an AI column. Say the price against the test budget, ending with the pricing sentence, and ask again only if it goes over.
  - Control the spend of a `run-function` column such as `Qualify` with the 1, 10, 100 steps, the 1.5 times stop, and `get_wallet` `consumedUsd` before and after.
  - Name `Qualify`, its pull-out columns, `Tier` and `Brief` in `columnIds`, so `Brief` really runs. Run 1 made-up work-email lead that should land in tier A or B, then 10 (post more made-up leads, each with its own email, if you need them).
  - Make the 10 a mix of tiers A, B and C that matches the form: a gmail lead skips both paid steps, and a tier C work-email lead skips `Brief`. If you don't know the mix, use mostly work-email leads that land in A or B, so the figure is a ceiling.
  - Read `get_wallet` `consumedUsd` before and after each batch. The cost per lead you quote in step 8 is the 10-lead total ÷ 10.
- **Later edits.** To change a prompt later, edit it in the Function's sandbox, dry-run, ask, republish, then run 3 to 5 made-up leads with `run_function` (priced and asked first) and read them with `get_function_run`. Re-run `Qualify` with `force: true` on the made-up test rows only. For other rows, price it first from the Function: `get_function` `costEstimate.maxUsdPerRun` × the exact `rowIds`, plus its AI step measured on the made-up leads, ask with the pricing sentence, and re-run only the rows the user names.
- **Brief as a Function.** Once the Brief reads well on the made-up leads, turn it into its own Function titled `Lead brief · Loopster skill` the same way: `create_function` with `fromTable` on the `Brief` column. `Tier` and the other columns it reads become its inputs. Record its id in the "Functions" section of `loopster-context.md`, and call it from one `run-function` column. `Alert` reads the brief through a pulled-out column (the same two-step Formula as above). Publishing it and opening it to agents each need their own yes. If the user declines, keep the column.

## 11. Valid lead gate (a run condition, free, before Auto-run)

Set a run condition on the `Qualify` column so a blank, malformed or obvious test address is skipped and a junk post spends nothing. Keep the `Email` input mapped to the `Email` column.

Call `update_column` on `Qualify` with:

```json
{"runCondition": {"enabled": true, "description": "Only for a valid, non-test email",
 "condition": "(() => { const e = String(@{Email}).trim().toLowerCase(); return /^[^@\\s]+@[^@\\s]+\\.[^@\\s]{2,}$/.test(e) && !['example.com', 'test.com'].includes(e.split('@').pop()); })()"}}
```

`Brief` and `Alert` already carry a tier condition. Write the address check and the tier check together in one `condition`, joined with `&&`, so a junk post can't reach a paid or sending step through `review`. For `Brief` (use the same for `Alert`):

```json
{"runCondition": {"enabled": true, "description": "Only for a valid email, and A, B or review",
 "condition": "(() => { const e = String(@{Email}).trim().toLowerCase(); return /^[^@\\s]+@[^@\\s]+\\.[^@\\s]{2,}$/.test(e) && !['example.com', 'test.com'].includes(e.split('@').pop()) && ['A', 'B', 'review'].includes(String(@{<Tier id>})); })()"}}
```

Do the same on `Nurture`, joining the address check to its tier C check. `CRM lookup` (HubSpot) and `CRM` have no tier check, so set the address check alone on them. Then a junk post can't reach a Slack post, a CRM record or a sequence.

If you kept the columns instead of a Function, there is no `Qualify` column: set the same address check on `ICP fit` instead, and name `ICP fit` in place of `Qualify` in the `columnIds` below.

Before Auto-run, post a malformed address to the test table. Auto-run is still off, so posting alone proves nothing: call `trigger_rows` with `columnIds: ["Qualify", "Brief", "Alert"]`, plus `CRM lookup`, `CRM` and `Nurture` if you built them, on that row. Check each cell says the condition wasn't met and `get_wallet` `consumedUsd` did not move.
